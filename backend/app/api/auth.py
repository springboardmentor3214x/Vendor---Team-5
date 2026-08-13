from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    PasswordChangeRequest,
    ResetPasswordConfirm,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

ALLOWED_ROLES = {
    "Administrator", "Procurement Manager", "Supply Chain Manager",
    "Vendor", "Finance Officer", "Auditor", "Department User",
}


def normalize_user_role(current_user: User) -> str | None:
    """Return a role name for either string-backed or relationship-backed users."""
    role = getattr(current_user, "role", None)
    return getattr(role, "name", role)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return user


def require_roles(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if normalize_user_role(current_user) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user
    return role_checker


# Mirrors the Angular route guards so API access cannot be bypassed by calling
# an endpoint directly.  More-specific paths are matched before module defaults.
FRONTEND_ROLE_POLICIES: dict[str, tuple[str, ...]] = {
    "/dashboard/procurement": ("Administrator", "Procurement Manager", "Supply Chain Manager"),
    "/dashboard/vendor": ("Vendor",),
    "/dashboard/admin": ("Administrator",),
    "/dashboard/cost-analysis": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"),
    "/dashboard/charts": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"),
    "/dashboard": ALLOWED_ROLES,
    # Endpoint-level checks in procurement.py enforce the finer workflow rules.
    # This module-level policy only controls authenticated entry to the router.
    "/procurement/invoices": ("Administrator", "Procurement Manager", "Finance Officer", "Vendor"),
    "/procurement/purchase-orders": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor"),
    "/procurement/order-tracking": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor"),
    "/procurement": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Department User"),
    "/performance": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"),
    "/reliability": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"),
    "/reports": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"),
    # Contract endpoints scope Vendor reads to their own vendor record in
    # contracts.py; mutation remains manager-only below.
    "/contracts": ("Administrator", "Procurement Manager", "Vendor", "Auditor", "Finance Officer"),
    "/compliance": ("Administrator", "Procurement Manager", "Auditor"),
    "/certifications": ("Administrator", "Procurement Manager", "Auditor"),
    "/documents": ("Administrator", "Procurement Manager", "Auditor"),
    # Notification reads are always scoped to the authenticated user in
    # notifications.py, so every supported role may access their own inbox.
    "/notifications": ALLOWED_ROLES,
    "/messages": ALLOWED_ROLES,
    "/vendors": ("Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor"),
}


def require_frontend_route_access(request: Request, current_user: User = Depends(get_current_user)) -> User:
    path = request.url.path.rstrip("/") or "/"
    allowed_roles = next((roles for prefix, roles in FRONTEND_ROLE_POLICIES.items() if path == prefix or path.startswith(prefix + "/")), None)
    if allowed_roles and normalize_user_role(current_user) not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this module")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        manager_only_modules = ("/performance", "/reliability", "/contracts", "/compliance", "/certifications", "/documents")
        if path.startswith(manager_only_modules) and normalize_user_role(current_user) not in {"Administrator", "Procurement Manager"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to modify this module")
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role selected")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and confirm password do not match")

    new_user = User(
        full_name=user.full_name,
        employee_id=user.employee_id,
        company_name=user.company_name,
        email=user.email,
        mobile_number=user.mobile_number,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    password_valid = False
    if db_user:
        try:
            password_valid = verify_password(user.password, db_user.hashed_password)
        except (TypeError, ValueError):
            # Legacy/imported records can contain an invalid password hash.
            # Authentication must fail safely instead of exposing a 500 error.
            password_valid = False

    if not db_user or not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if hasattr(db_user, "is_active") and not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role,
            "user_id": getattr(db_user, "id", None),
            "full_name": getattr(db_user, "full_name", None),
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role,
        # The Angular application has one protected, role-aware /dashboard
        # route.  Returning only registered frontend routes avoids successful
        # logins pointing callers at obsolete role-specific paths.
        "redirect_to": "/dashboard",
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.mobile_number is not None:
        current_user.mobile_number = payload.mobile_number
    if payload.company_name is not None:
        current_user.company_name = payload.company_name
    if hasattr(current_user, "profile_picture") and payload.profile_picture is not None:
        current_user.profile_picture = payload.profile_picture
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return {"message": "If the email is registered, a password reset link/token has been generated"}
    reset_token = create_access_token(
        data={"sub": user.email, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=30),
    )
    if hasattr(user, "reset_token"):
        user.reset_token = reset_token
    if hasattr(user, "reset_token_expiry"):
        user.reset_token_expiry = None
    db.commit()
    return {"message": "Password reset token generated successfully", "reset_token": reset_token}


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordConfirm, db: Session = Depends(get_db)):
    error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and confirm password do not match")
    try:
        decoded = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        if not decoded.get("sub") or decoded.get("purpose") != "password_reset":
            raise error
    except JWTError:
        raise error
    user = db.query(User).filter(User.email == decoded["sub"]).first()
    if not user:
        raise error
    user.hashed_password = get_password_hash(payload.new_password)
    if hasattr(user, "reset_token"):
        user.reset_token = None
    if hasattr(user, "reset_token_expiry"):
        user.reset_token_expiry = None
    db.commit()
    return {"message": "Password updated successfully"}


@router.post("/change-password", response_model=MessageResponse)
def change_password(payload: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and confirm password do not match")
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
