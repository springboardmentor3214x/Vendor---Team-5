from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.schemas.vendor import VendorCategoryResponse, VendorCreate, VendorUpdate


router = APIRouter(prefix="/vendors", tags=["Vendors"])


def _category_or_400(db: Session, category_id: int) -> VendorCategory:
    category = db.query(VendorCategory).filter(VendorCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid vendor category")
    return category


def _resolve_category(db: Session, vendor_data: dict, *, required: bool) -> None:
    """Replace the API-only category label with Vendor.category_id."""
    vendor_category = vendor_data.pop("vendor_category", None)
    category_id = vendor_data.get("category_id")

    if category_id is not None:
        _category_or_400(db, category_id)
    elif vendor_category:
        category = db.query(VendorCategory).filter(VendorCategory.name == vendor_category).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid vendor category")
        vendor_data["category_id"] = category.id
    elif required:
        raise HTTPException(status_code=400, detail="Vendor category is required")


@router.get("/categories", response_model=list[VendorCategoryResponse])
def list_vendor_categories(db: Session = Depends(get_db)):
    return db.query(VendorCategory).order_by(VendorCategory.name).all()


@router.get("/")
def list_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    vendor_data = payload.model_dump(by_alias=False, exclude_unset=True)
    _resolve_category(db, vendor_data, required=True)

    # vendor_category has been removed above: Vendor has only category_id.
    vendor = Vendor(**vendor_data)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.put("/{vendor_id}")
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor_data = payload.model_dump(by_alias=False, exclude_unset=True)
    _resolve_category(db, vendor_data, required=False)
    for field, value in vendor_data.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)
    return vendor
