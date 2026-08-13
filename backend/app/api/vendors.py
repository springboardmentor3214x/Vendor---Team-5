import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role, require_roles
from app.core.database import get_db
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.models.vendor_approval_history import VendorApprovalHistory
from app.models.vendor_document import VendorDocument
from app.models.vendor_contact import VendorContact
from app.models.user import User
from app.models.performance import PerformanceRecord
from app.models.reliability import VendorReliability, PerformanceTrend
from app.models.notification import Notification
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.contract import Contract
from app.models.certification import Certification
from app.models.compliance_record import ComplianceRecord
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.service_rating import ServiceRating
from app.models.communication import Communication
from app.models.communication_file import CommunicationFile
from app.models.discussion import Discussion
from app.models.procurement_recommendation import ProcurementRecommendation
from app.schemas.vendor import (
    VendorApprovalAction,
    VendorApprovalHistoryResponse,
    VendorCategoryResponse,
    VendorCreate,
    VendorDocumentResponse,
    VendorUpdate,
)
from app.services.notification_service import create_vendor_approval_notification


router = APIRouter(prefix="/vendors", tags=["Vendors"])
VENDOR_DOCUMENTS_DIRECTORY = Path(__file__).resolve().parents[2] / "uploads" / "vendor_documents"

# Upload policy is intentionally kept at the API boundary so the same contract
# is enforced before local storage or service-layer persistence is reached.
ALLOWED_DOCUMENT_EXTENSIONS = frozenset({"pdf", "xlsx", "xls", "docx", "doc", "png", "jpg", "jpeg", "zip"})
MAX_DOCUMENT_UPLOAD_BYTES = int(os.getenv("VENDOR_DOCUMENT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))


def _validate_vendor_document_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A document file is required")
    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported document file type")


def _vendor_for_authenticated_user(db: Session, current_user: User) -> Vendor | None:
    """Resolve the Vendor record that belongs to a vendor-role account.

    The current schema links a user account to a vendor through the shared email
    address.  Keep that lookup in one place so all record-level checks use the
    same rule until a direct user_id foreign key is introduced.
    """
    return db.query(Vendor).filter(Vendor.email == current_user.email).first()


def _require_vendor_record_access(db: Session, vendor_id: int, current_user: User) -> None:
    """Prevent vendor accounts from reading or changing another vendor's data."""
    if normalize_user_role(current_user) != "Vendor":
        return

    own_vendor = _vendor_for_authenticated_user(db, current_user)
    if not own_vendor or own_vendor.id != vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this vendor record")


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


def _vendor_or_404(db: Session, vendor_id: int) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


def _ensure_vendor_can_be_deleted(db: Session, vendor: Vendor) -> None:
    """Refuse deletion when business records would be orphaned or hidden.

    This is intentionally conservative.  Administrators can delete a vendor
    only before it has collected contacts, workflow, contract, performance,
    communication, or notification history.  It protects data without
    changing database relationships or relying on a cascade policy.
    """
    related_models = (
        ("vendor contacts", VendorContact),
        ("vendor documents", VendorDocument),
        ("approval history", VendorApprovalHistory),
        ("procurement requests", ProcurementRequest),
        ("purchase orders", PurchaseOrder),
        ("contracts", Contract),
        ("certifications", Certification),
        ("compliance records", ComplianceRecord),
        ("delivery performance records", DeliveryPerformance),
        ("quality evaluations", ProductQualityEvaluation),
        ("communication performance records", CommunicationLog),
        ("service ratings", ServiceRating),
        ("performance summaries", PerformanceRecord),
        ("reliability summaries", VendorReliability),
        ("reliability trends", PerformanceTrend),
        ("procurement recommendations", ProcurementRecommendation),
        ("communications", Communication),
        ("communication files", CommunicationFile),
        ("discussions", Discussion),
        ("notifications", Notification),
    )
    for label, model in related_models:
        if db.query(model).filter(model.vendor_id == vendor.id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vendor cannot be deleted because related {label} exist.",
            )

    if db.query(User).filter(User.email == vendor.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor cannot be deleted while a linked user account exists.",
        )


def _document_response(document: VendorDocument) -> dict:
    return {
        "id": document.id,
        "vendorId": document.vendor_id,
        "documentType": document.document_type,
        "fileName": document.file_name,
        "contentType": document.content_type,
        "uploadedBy": document.uploaded_by,
        "uploadedAt": document.uploaded_at,
        "downloadUrl": f"/vendors/{document.vendor_id}/documents/{document.id}/download",
    }


@router.get("/categories", response_model=list[VendorCategoryResponse], dependencies=[Depends(get_current_user)])
def list_vendor_categories(db: Session = Depends(get_db)):
    return db.query(VendorCategory).order_by(VendorCategory.name).all()


@router.get("/", dependencies=[Depends(get_current_user)])
def list_vendors(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    approval_status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if normalize_user_role(current_user) == "Vendor":
        own_vendor = _vendor_for_authenticated_user(db, current_user)
        return [own_vendor] if own_vendor else []

    query = db.query(Vendor)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Vendor.company_name.ilike(term))
            | (Vendor.contact_person_name.ilike(term))
            | (Vendor.email.ilike(term))
        )
    if category and category.strip():
        query = query.join(VendorCategory).filter(VendorCategory.name == category.strip())
    if status and status.strip():
        query = query.filter(Vendor.vendor_status == status.strip())
    if approval_status and approval_status.strip():
        query = query.filter(Vendor.approval_status == approval_status.strip())
    return query.order_by(Vendor.company_name.asc()).all()


@router.get("/{vendor_id}", dependencies=[Depends(get_current_user)])
def get_vendor(vendor_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_vendor_record_access(db, vendor_id, current_user)
    return _vendor_or_404(db, vendor_id)


@router.get("/{vendor_id}/documents", response_model=list[VendorDocumentResponse], dependencies=[Depends(get_current_user)])
def list_vendor_documents(vendor_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_vendor_record_access(db, vendor_id, current_user)
    _vendor_or_404(db, vendor_id)
    documents = (
        db.query(VendorDocument)
        .filter(VendorDocument.vendor_id == vendor_id)
        .order_by(VendorDocument.uploaded_at.desc(), VendorDocument.id.desc())
        .all()
    )
    return [_document_response(document) for document in documents]


@router.post("/{vendor_id}/documents", response_model=VendorDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_vendor_document(
    vendor_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Store a vendor document and its metadata using the DB contract from Milestone 1."""
    _require_vendor_record_access(db, vendor_id, current_user)
    _vendor_or_404(db, vendor_id)
    _validate_vendor_document_upload(file)
    if not document_type.strip():
        raise HTTPException(status_code=400, detail="Document type is required")

    VENDOR_DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    stored_path = VENDOR_DOCUMENTS_DIRECTORY / f"{uuid4().hex}_{safe_name}"
    try:
        bytes_written = 0
        with stored_path.open("wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > MAX_DOCUMENT_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Document file exceeds the 10 MB upload limit")
                output_file.write(chunk)
    except HTTPException:
        stored_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to store vendor document") from exc
    finally:
        await file.close()

    document = VendorDocument(
        vendor_id=vendor_id,
        document_type=document_type.strip(),
        file_name=safe_name,
        file_path=str(stored_path),
        content_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return _document_response(document)


@router.get("/{vendor_id}/documents/{document_id}/download", dependencies=[Depends(get_current_user)])
def download_vendor_document(
    document_id: int,
    vendor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_vendor_record_access(db, vendor_id, current_user)
    document = (
        db.query(VendorDocument)
        .filter(VendorDocument.id == document_id, VendorDocument.vendor_id == vendor_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Vendor document not found")
    stored_path = Path(document.file_path)
    if not stored_path.is_file():
        raise HTTPException(status_code=404, detail="Vendor document file is unavailable")
    return FileResponse(
        path=stored_path,
        media_type=document.content_type or "application/octet-stream",
        filename=document.file_name,
    )


@router.get("/{vendor_id}/approval-history", response_model=list[VendorApprovalHistoryResponse], dependencies=[Depends(get_current_user)])
def list_vendor_approval_history(
    vendor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_vendor_record_access(db, vendor_id, current_user)
    _vendor_or_404(db, vendor_id)
    return (
        db.query(VendorApprovalHistory)
        .filter(VendorApprovalHistory.vendor_id == vendor_id)
        .order_by(VendorApprovalHistory.action_date.desc(), VendorApprovalHistory.id.desc())
        .all()
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("Administrator", "Procurement Manager", "Vendor"))],
)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    vendor_data = payload.model_dump(by_alias=False, exclude_unset=True)
    _resolve_category(db, vendor_data, required=True)

    # vendor_category has been removed above: Vendor has only category_id.
    vendor = Vendor(**vendor_data)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.put(
    "/{vendor_id}",
    dependencies=[Depends(require_roles("Administrator", "Procurement Manager"))],
)
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


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("Administrator"))],
)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Delete only a vendor with no related operational or identity records."""
    vendor = _vendor_or_404(db, vendor_id)
    _ensure_vendor_can_be_deleted(db, vendor)
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}


@router.patch("/{vendor_id}/approve")
def approve_vendor(
    vendor_id: int,
    payload: VendorApprovalAction,
    current_user: User = Depends(require_roles("Administrator", "Procurement Manager")),
    db: Session = Depends(get_db),
):
    """Approve a pending vendor using the existing Vendor status fields."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending vendors can be approved")

    vendor.approval_status = "Approved"
    vendor.vendor_status = "Active"
    db.add(
        VendorApprovalHistory(
            vendor_id=vendor.id,
            action="Approved",
            remarks=payload.remarks,
            acted_by=current_user.id,
        )
    )
    # Create the projections consumed by Performance, Reliability, and
    # Notifications in the same transaction as the approval.
    if not db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == vendor.id).first():
        db.add(PerformanceRecord(vendor_id=vendor.id, performance_status="Not Evaluated", notes="Created when vendor was approved."))
    if not db.query(VendorReliability).filter(VendorReliability.vendor_id == vendor.id).first():
        db.add(VendorReliability(vendor_id=vendor.id, risk_level="Medium", recommendation="Awaiting performance evaluation."))
    # Recipient targeting, deduplication, and optional delivery channels are
    # centralized in the Module 9 service helper.
    create_vendor_approval_notification(db, vendor.id, approved=True)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.patch("/{vendor_id}/reject")
def reject_vendor(
    vendor_id: int,
    payload: VendorApprovalAction,
    current_user: User = Depends(require_roles("Administrator", "Procurement Manager")),
    db: Session = Depends(get_db),
):
    """Reject a pending vendor using the existing Vendor status fields."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending vendors can be rejected")

    vendor.approval_status = "Rejected"
    vendor.vendor_status = "Rejected"
    db.add(
        VendorApprovalHistory(
            vendor_id=vendor.id,
            action="Rejected",
            remarks=payload.remarks,
            acted_by=current_user.id,
        )
    )
    # Keep rejection notification rules consistent with the approval path.
    create_vendor_approval_notification(db, vendor.id, approved=False)
    db.commit()
    db.refresh(vendor)
    return vendor
