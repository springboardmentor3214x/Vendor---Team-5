import os
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user, normalize_user_role
from app.models.invoice import Invoice
from app.models.order_tracking import OrderTracking
from app.models.procurement_approval import ProcurementApproval
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_status_history import ProcurementStatusHistory
from app.models.purchase_order import PurchaseOrder
from app.models.procurement_request_document import ProcurementRequestDocument
from app.models.invoice_document import InvoiceDocument
from app.models.user import User
from app.models.vendor import Vendor

from app.schemas.procurement import (
    ProcurementRequestCreate,
    ProcurementRequestUpdate,
    ProcurementRequestOut,
    ProcurementApprovalAction,
    VendorAssignmentAction,
    PurchaseOrderCreate,
    PurchaseOrderOut,
    PurchaseOrderStatusUpdate,
    OrderTrackingOut,
    OrderTrackingUpdate,
    InvoiceCreate,
    InvoiceOut,
    InvoiceVerifyAction,
    PaymentStatusUpdate,
    ApprovedVendorOut,
)
from app.schemas.document_lifecycle import LifecycleDocumentOut

from app.api.reliability_refresh import refresh_after_procurement_update
from app.api.file_storage import store_document_upload
from app.services import procurement_document_service
from app.services.procurement_service import (
    approve_procurement_request,
    reject_procurement_request,
    cancel_procurement_request,
    can_send_back_procurement_request,
    can_edit_sent_back_request,
    resubmit_procurement_request,
    generate_procurement_request_number,
    can_assign_vendor_to_request,
)
from app.services.purchase_order_service import (
    generate_purchase_order_number,
    calculate_total_cost,
    can_create_purchase_order,
    issue_purchase_order as issue_purchase_order_action,
    mark_purchase_order_delivered,
    cancel_purchase_order,
    is_delivery_delayed,
    can_complete_procurement,
    render_purchase_order_pdf,
)

router = APIRouter(prefix="/procurement", tags=["Procurement"])


VALID_PO_STATUSES = {"Draft", "Issued", "Delivered", "Cancelled", "Completed"}
VALID_DELIVERY_STATUSES = {"Awaiting Shipment", "In Transit", "Delivered", "Delayed", "Completed"}
VALID_PAYMENT_STATUSES = {"Pending", "Verified", "Approved", "Paid", "Rejected"}

ADMINISTRATOR = "Administrator"
PROCUREMENT_MANAGER = "Procurement Manager"
SUPPLY_CHAIN_MANAGER = "Supply Chain Manager"
DEPARTMENT_USER = "Department User"
VENDOR_ROLE = "Vendor"
FINANCE_OFFICER = "Finance Officer"


def _require_procurement_role(current_user: User, *allowed_roles: str) -> str:
    """Enforce the action-level workflow role, after router-level JWT access."""
    role = normalize_user_role(current_user)
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this procurement action")
    return role


def _vendor_id_for_user(db: Session, current_user: User) -> int:
    vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No vendor record is linked to this user")
    return vendor.id


def _require_vendor_purchase_order_access(db: Session, purchase_order: PurchaseOrder, current_user: User) -> None:
    if normalize_user_role(current_user) == VENDOR_ROLE and purchase_order.vendor_id != _vendor_id_for_user(db, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this purchase order")


def _require_request_owner(request: ProcurementRequest, current_user: User) -> None:
    if normalize_user_role(current_user) == DEPARTMENT_USER and request.requested_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this procurement request")


def _document_response(document: ProcurementRequestDocument | InvoiceDocument) -> dict:
    """Keep lifecycle-document output consistent across request and invoice APIs."""
    return {
        "id": document.id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "content_type": document.content_type,
        "uploaded_by": document.uploaded_by,
        "uploaded_at": document.uploaded_at,
        "version": document.version or 1,
        "is_current": bool(document.is_current),
        "replaced_document_id": document.replaced_document_id,
        "replaced_at": document.replaced_at,
        "replaced_by": document.replaced_by,
    }


def _request_document_access(
    db: Session, request_id: int, current_user: User, *, write: bool
) -> ProcurementRequest:
    role = _require_procurement_role(
        current_user,
        ADMINISTRATOR,
        PROCUREMENT_MANAGER,
        SUPPLY_CHAIN_MANAGER,
        DEPARTMENT_USER,
    )
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Procurement request not found")
    _require_request_owner(request, current_user)
    if write and role not in {ADMINISTRATOR, PROCUREMENT_MANAGER, DEPARTMENT_USER}:
        raise HTTPException(status_code=403, detail="You do not have permission to modify request documents")
    return request


def _invoice_document_access(
    db: Session, invoice_id: int, current_user: User, *, write: bool
) -> Invoice:
    role = _require_procurement_role(
        current_user,
        ADMINISTRATOR,
        PROCUREMENT_MANAGER,
        FINANCE_OFFICER,
        VENDOR_ROLE,
    )
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, purchase_order, current_user)
    if write and role not in {ADMINISTRATOR, FINANCE_OFFICER, VENDOR_ROLE}:
        raise HTTPException(status_code=403, detail="You do not have permission to modify invoice documents")
    return invoice


def log_status_change(db: Session, request_id: int, old_status: str, new_status: str, changed_by: int | None, remarks: str | None = None):
    history = ProcurementStatusHistory(
        procurement_request_id=request_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        remarks=remarks,
        changed_at=datetime.utcnow(),
    )
    db.add(history)


def log_approval_action(db: Session, request_id: int, approved_by: int | None, action: str, remarks: str | None = None):
    approval = ProcurementApproval(
        procurement_request_id=request_id,
        approved_by=approved_by,
        status=action,
        remarks=remarks,
        approved_at=datetime.utcnow(),
    )
    db.add(approval)


# ---------------- Procurement Requests ----------------

@router.post("/procurement-requests", response_model=ProcurementRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: ProcurementRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, DEPARTMENT_USER)
    if payload.required_delivery_date < date.today():
        raise HTTPException(status_code=400, detail="Required delivery date cannot be in the past")

    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    count = db.query(ProcurementRequest).count() + 1
    request_data = payload.model_dump(exclude={"request_number"})
    # Request ownership is derived from the authenticated actor, never a
    # client-supplied requestedBy value.
    request_data["requested_by"] = current_user.id
    request = ProcurementRequest(
        **request_data,
        request_number=generate_procurement_request_number(count),
        approval_status="Pending",
        request_date=datetime.utcnow(),
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    log_status_change(db, request.id, None, "Pending", request.requested_by, "Request created")
    db.commit()

    return request


@router.get("/procurement-requests", response_model=list[ProcurementRequestOut], dependencies=[Depends(get_current_user)])
def list_requests(
    department: str | None = None,
    approval_status: str | None = None,
    priority: str | None = None,
    requested_by: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, DEPARTMENT_USER)
    query = db.query(ProcurementRequest)

    if role == DEPARTMENT_USER:
        query = query.filter(ProcurementRequest.requested_by == current_user.id)

    if department:
        query = query.filter(ProcurementRequest.department == department)
    if approval_status:
        query = query.filter(ProcurementRequest.approval_status == approval_status)
    if priority:
        query = query.filter(ProcurementRequest.priority == priority)
    if requested_by:
        if role == DEPARTMENT_USER and requested_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own procurement requests")
        query = query.filter(ProcurementRequest.requested_by == requested_by)

    return query.order_by(ProcurementRequest.created_at.desc()).all()


@router.get("/procurement-requests/{request_id}", response_model=ProcurementRequestOut, dependencies=[Depends(get_current_user)])
def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, DEPARTMENT_USER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    _require_request_owner(request, current_user)
    return request


@router.get(
    "/procurement-requests/{request_id}/documents",
    response_model=list[LifecycleDocumentOut],
)
def list_request_documents(
    request_id: int,
    include_replaced: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current request supporting documents, with optional version history."""
    _request_document_access(db, request_id, current_user, write=False)
    documents = procurement_document_service.list_procurement_request_documents(
        db, request_id, include_replaced=include_replaced
    )
    return [_document_response(document) for document in documents]


@router.post(
    "/procurement-requests/{request_id}/documents",
    response_model=LifecycleDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_request_document(
    request_id: int,
    document_type: str = Form("Supporting Document"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload supporting evidence for a procurement request."""
    _request_document_access(db, request_id, current_user, write=True)
    if not document_type.strip():
        raise HTTPException(status_code=400, detail="Document type is required")
    upload = await store_document_upload(file, area="procurement_request_documents")
    document = procurement_document_service.create_procurement_request_document(
        db,
        request_id=request_id,
        document_type=document_type.strip(),
        file_name=upload.file_name,
        file_path=upload.file_path,
        file_size=upload.file_size,
        content_type=upload.content_type,
        uploaded_by=current_user.id,
    )
    return _document_response(document)


@router.get("/procurement-requests/{request_id}/documents/{document_id}/download")
def download_request_document(
    request_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _request_document_access(db, request_id, current_user, write=False)
    document = procurement_document_service.get_procurement_request_document(db, document_id)
    if not document or document.request_id != request_id:
        raise HTTPException(status_code=404, detail="Request document not found")
    if not document.file_path or not os.path.isfile(document.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on disk")
    return FileResponse(document.file_path, filename=document.file_name, media_type=document.content_type)


@router.post(
    "/procurement-requests/{request_id}/documents/{document_id}/replace",
    response_model=LifecycleDocumentOut,
)
async def replace_request_document(
    request_id: int,
    document_id: int,
    document_type: str = Form("Supporting Document"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _request_document_access(db, request_id, current_user, write=True)
    existing = procurement_document_service.get_procurement_request_document(db, document_id)
    if not existing or existing.request_id != request_id:
        raise HTTPException(status_code=404, detail="Request document not found")
    upload = await store_document_upload(file, area="procurement_request_documents")
    try:
        replacement = procurement_document_service.replace_procurement_request_document(
            db,
            document_id,
            file_name=upload.file_name,
            file_path=upload.file_path,
            file_size=upload.file_size,
            content_type=upload.content_type,
            document_type=document_type.strip() or None,
            uploaded_by=current_user.id,
        )
    except ValueError as error:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not replacement:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Request document not found")
    return _document_response(replacement)


@router.patch("/procurement-requests/{request_id}", response_model=ProcurementRequestOut)
def update_request(
    request_id: int,
    payload: ProcurementRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, DEPARTMENT_USER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    _require_request_owner(request, current_user)
    if not can_edit_sent_back_request(request.approval_status):
        raise HTTPException(status_code=400, detail="Only sent-back requests can be edited and resubmitted")

    old_status = request.approval_status
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    request.approval_status = resubmit_procurement_request(old_status)
    log_status_change(
        db,
        request.id,
        old_status,
        request.approval_status,
        request.requested_by,
        "Request edited and resubmitted",
    )

    db.commit()
    db.refresh(request)
    return request


@router.delete("/procurement-requests/{request_id}")
def delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, DEPARTMENT_USER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    _require_request_owner(request, current_user)
    if request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be deleted")

    db.delete(request)
    db.commit()
    return {"message": "Procurement request deleted successfully"}


@router.patch("/procurement-requests/{request_id}/approve", response_model=ProcurementRequestOut)
def approve_request(
    request_id: int,
    payload: ProcurementApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    try:
        request.approval_status = approve_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    request.approved_by = current_user.id
    request.approved_date = datetime.utcnow()
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, current_user.id, "Approved", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, current_user.id, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/reject", response_model=ProcurementRequestOut)
def reject_request(
    request_id: int,
    payload: ProcurementApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    try:
        request.approval_status = reject_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    request.approved_by = current_user.id
    request.approved_date = datetime.utcnow()
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, current_user.id, "Rejected", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, current_user.id, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/send-back", response_model=ProcurementRequestOut)
def send_back_request(
    request_id: int,
    payload: ProcurementApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    if not can_send_back_procurement_request(old_status):
        raise HTTPException(status_code=400, detail="Only pending or approved requests can be sent back")

    request.approval_status = "Sent Back"
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, current_user.id, "Sent Back", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, current_user.id, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/cancel", response_model=ProcurementRequestOut)
def cancel_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, DEPARTMENT_USER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    _require_request_owner(request, current_user)
    old_status = request.approval_status
    try:
        request.approval_status = cancel_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_status_change(db, request_id, old_status, request.approval_status, current_user.id, "Cancelled")
    db.commit()
    db.refresh(request)
    return request


@router.get("/procurement-requests/{request_id}/status-history", dependencies=[Depends(get_current_user)])
def get_status_history(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, DEPARTMENT_USER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    _require_request_owner(request, current_user)
    history = (
        db.query(ProcurementStatusHistory)
        .filter(ProcurementStatusHistory.procurement_request_id == request_id)
        .order_by(ProcurementStatusHistory.changed_at.desc())
        .all()
    )
    return history


# ---------------- Vendor Assignment ----------------

@router.get("/procurement-requests/{request_id}/approved-vendors", response_model=list[ApprovedVendorOut], dependencies=[Depends(get_current_user)])
def get_approved_vendors_for_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    query = db.query(Vendor).filter(Vendor.approval_status == "Approved", Vendor.vendor_status == "Active")

    if request.product_category and hasattr(Vendor, "category_id"):
        pass

    return query.order_by(Vendor.reliability_score.desc()).all()


@router.patch("/procurement-requests/{request_id}/assign-vendor", response_model=ProcurementRequestOut)
def assign_vendor(
    request_id: int,
    payload: VendorAssignmentAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if not can_assign_vendor_to_request(request.approval_status):
        raise HTTPException(status_code=400, detail="Vendor can only be assigned to approved requests")

    vendor = db.query(Vendor).filter(Vendor.id == payload.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if vendor.approval_status != "Approved":
        raise HTTPException(status_code=400, detail="Only approved vendors can be assigned")

    request.vendor_id = payload.vendor_id
    db.commit()
    db.refresh(request)
    return request


# ---------------- Purchase Orders ----------------

@router.post("/purchase-orders", response_model=PurchaseOrderOut, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    payload: PurchaseOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    request = db.query(ProcurementRequest).filter(
        ProcurementRequest.id == payload.procurement_request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Procurement request not found")

    if not request.vendor_id:
        raise HTTPException(status_code=400, detail="Assign a vendor to this request before creating a purchase order")

    if not can_create_purchase_order(request.approval_status, request.vendor_id is not None):
        raise HTTPException(status_code=400, detail="Cannot create purchase order for this request")

    if request.vendor_id:
        from app.models.reliability import VendorReliability
        from app.utils.constants import RISK_HIGH
        rel = db.query(VendorReliability).filter(VendorReliability.vendor_id == request.vendor_id).first()
        if rel and rel.risk_level == RISK_HIGH:
            raise HTTPException(
                status_code=400,
                detail="Warning: This vendor is classified as High Risk. Additional approval is required before proceeding."
            )

    existing_po = db.query(PurchaseOrder).filter(
        PurchaseOrder.procurement_request_id == payload.procurement_request_id
    ).first()
    if existing_po:
        raise HTTPException(status_code=400, detail="Purchase order already exists for this request")

    po = PurchaseOrder(
        procurement_request_id=payload.procurement_request_id,
        vendor_id=request.vendor_id,
        contract_id=payload.contract_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_cost=calculate_total_cost(payload.quantity, payload.unit_price),
        tax_details=payload.tax_details or 0.0,
        shipping_address=payload.shipping_address,
        po_number=generate_purchase_order_number(db.query(PurchaseOrder).count() + 1),
        expected_delivery_date=payload.expected_delivery_date,
        payment_terms=payload.payment_terms,
        po_status="Draft",
        created_by=current_user.id,
        assigned_procurement_manager_id=payload.assigned_procurement_manager_id or (
            current_user.id if normalize_user_role(current_user) == PROCUREMENT_MANAGER else None
        ),
        project_name=payload.project_name or request.project_name,
        po_date=datetime.utcnow(),
    )
    db.add(po)
    db.commit()
    db.refresh(po)

    tracking = OrderTracking(
        purchase_order_id=po.id,
        expected_delivery_date=payload.expected_delivery_date,
        delivery_status="Awaiting Shipment",
        delay_days=0,
    )
    db.add(tracking)
    db.commit()

    return po


@router.get("/purchase-orders", response_model=list[PurchaseOrderOut], dependencies=[Depends(get_current_user)])
def list_purchase_orders(
    vendor_id: int | None = None,
    po_status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, VENDOR_ROLE)
    query = db.query(PurchaseOrder)
    if role == VENDOR_ROLE:
        own_vendor_id = _vendor_id_for_user(db, current_user)
        if vendor_id is not None and vendor_id != own_vendor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own purchase orders")
        query = query.filter(PurchaseOrder.vendor_id == own_vendor_id)
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    if po_status:
        query = query.filter(PurchaseOrder.po_status == po_status)
    return query.order_by(PurchaseOrder.created_at.desc()).all()


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut, dependencies=[Depends(get_current_user)])
def get_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, VENDOR_ROLE)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, po, current_user)
    return po


@router.get("/purchase-orders/{po_id}/print")
def print_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a print-ready PDF rendered from the persisted PO, request, and vendor."""
    _require_procurement_role(
        current_user,
        ADMINISTRATOR,
        PROCUREMENT_MANAGER,
        SUPPLY_CHAIN_MANAGER,
        VENDOR_ROLE,
    )
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, purchase_order, current_user)
    request = (
        db.query(ProcurementRequest)
        .filter(ProcurementRequest.id == purchase_order.procurement_request_id)
        .first()
    )
    vendor = db.query(Vendor).filter(Vendor.id == purchase_order.vendor_id).first()
    if not request or not vendor:
        raise HTTPException(
            status_code=409,
            detail="Purchase order is missing its procurement request or vendor reference",
        )
    pdf = render_purchase_order_pdf(purchase_order, request, vendor)
    safe_number = (purchase_order.po_number or f"purchase-order-{po_id}").replace("/", "-")
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_number}.pdf"'},
    )


@router.patch("/purchase-orders/{po_id}/status", response_model=PurchaseOrderOut)
def update_purchase_order_status(
    po_id: int,
    payload: PurchaseOrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    if payload.po_status not in VALID_PO_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid purchase order status")

    po.po_status = payload.po_status
    if payload.approved_by or payload.po_status in {"Issued", "Delivered", "Completed"}:
        po.approved_by = current_user.id

    db.commit()
    db.refresh(po)
    refresh_after_procurement_update(po.vendor_id, db)
    return po


@router.patch("/purchase-orders/{po_id}/issue", response_model=PurchaseOrderOut)
def issue_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    try:
        po.po_status = issue_purchase_order_action(po.po_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tracking = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po_id).first()
    if tracking:
        tracking.dispatch_date = datetime.utcnow()
        tracking.delivery_status = "In Transit"

    db.commit()
    db.refresh(po)
    refresh_after_procurement_update(po.vendor_id, db)
    return po


@router.patch("/purchase-orders/{po_id}/deliver", response_model=PurchaseOrderOut)
def deliver_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, VENDOR_ROLE)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, po, current_user)
    try:
        po.po_status = mark_purchase_order_delivered(po.po_status)
        if po.actual_delivery_date is None:
            po.actual_delivery_date = datetime.utcnow()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tracking = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po_id).first()
    if tracking:
        tracking.actual_delivery_date = po.actual_delivery_date
        delayed = is_delivery_delayed(po.expected_delivery_date, po.actual_delivery_date)
        tracking.delivery_status = "Delayed" if delayed else "Delivered"
        if delayed and po.expected_delivery_date and po.actual_delivery_date:
            tracking.delay_days = (po.actual_delivery_date.date() - po.expected_delivery_date.date()).days
        else:
            tracking.delay_days = 0

    db.commit()
    db.refresh(po)
    refresh_after_procurement_update(po.vendor_id, db)
    return po


@router.patch("/purchase-orders/{po_id}/cancel", response_model=PurchaseOrderOut)
def cancel_purchase_order_route(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    try:
        po.po_status = cancel_purchase_order(po.po_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(po)
    refresh_after_procurement_update(po.vendor_id, db)
    return po


def _completion_check(po_id: int, db: Session, *, apply_completion: bool):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    delivery_delayed = is_delivery_delayed(po.expected_delivery_date, po.actual_delivery_date)

    latest_invoice = (
        db.query(Invoice)
        .filter(Invoice.purchase_order_id == po_id)
        .order_by(Invoice.id.desc())
        .first()
    )
    invoice_status = latest_invoice.payment_status if latest_invoice is not None else ""
    invoice_verified = invoice_status in {"Verified", "Approved", "Paid"}

    is_complete = can_complete_procurement(po.po_status, invoice_status)

    if apply_completion and is_complete and po.po_status != "Completed":
        po.po_status = "Completed"
        db.commit()
        db.refresh(po)
        refresh_after_procurement_update(po.vendor_id, db)
    return {
        "po_id": po_id,
        "is_complete": is_complete,
        "delivery_delayed": delivery_delayed,
        "invoice_verified": invoice_verified,
        "po_status": po.po_status,
    }


@router.get("/purchase-orders/{po_id}/completion-check", dependencies=[Depends(get_current_user)])
def preview_completion(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return completion eligibility without changing the purchase order."""
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, VENDOR_ROLE)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, po, current_user)
    return _completion_check(po_id, db, apply_completion=False)


@router.post("/purchase-orders/{po_id}/completion-check")
def complete_if_eligible(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply the supported completion transition after an explicit user action."""
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER)
    return _completion_check(po_id, db, apply_completion=True)


@router.get("/order-tracking/{po_id}", response_model=OrderTrackingOut, dependencies=[Depends(get_current_user)])
def get_order_tracking(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, SUPPLY_CHAIN_MANAGER, VENDOR_ROLE)
    tracking = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Order tracking record not found")
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, purchase_order, current_user)
    return tracking


@router.patch("/order-tracking/{po_id}", response_model=OrderTrackingOut)
def update_order_tracking(
    po_id: int,
    payload: OrderTrackingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, VENDOR_ROLE)
    tracking = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Order tracking record not found")
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, purchase_order, current_user)
    if payload.delivery_status and payload.delivery_status not in VALID_DELIVERY_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid delivery status")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tracking, field, value)
    if tracking.expected_delivery_date and tracking.actual_delivery_date:
        if tracking.actual_delivery_date.date() > tracking.expected_delivery_date.date():
            tracking.delay_days = (tracking.actual_delivery_date.date() - tracking.expected_delivery_date.date()).days
            if tracking.delivery_status not in {"Delivered", "Completed"}:
                tracking.delivery_status = "Delayed"
    db.commit()
    db.refresh(tracking)
    refresh_after_procurement_update(purchase_order.vendor_id, db)
    return tracking


@router.post("/invoices", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def upload_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, VENDOR_ROLE)
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == payload.purchase_order_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, po, current_user)
    invoice = Invoice(
        purchase_order_id=payload.purchase_order_id,
        invoice_number=payload.invoice_number,
        invoice_amount=payload.invoice_amount,
        tax_amount=payload.tax_amount or 0.0,
        total_amount=payload.invoice_amount + (payload.tax_amount or 0.0),
        supporting_document_url=payload.supporting_document_url,
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        payment_status="Pending",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices", response_model=list[InvoiceOut], dependencies=[Depends(get_current_user)])
def list_invoices(
    purchase_order_id: int | None = None,
    payment_status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, FINANCE_OFFICER, VENDOR_ROLE)
    query = db.query(Invoice)
    if role == VENDOR_ROLE:
        own_vendor_id = _vendor_id_for_user(db, current_user)
        po_ids = [row.id for row in db.query(PurchaseOrder).filter(PurchaseOrder.vendor_id == own_vendor_id).all()]
        query = query.filter(Invoice.purchase_order_id.in_(po_ids))
    if purchase_order_id:
        query = query.filter(Invoice.purchase_order_id == purchase_order_id)
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    return query.order_by(Invoice.invoice_date.desc()).all()


@router.get("/invoices/{invoice_id}/documents", response_model=list[LifecycleDocumentOut])
def list_invoice_documents(
    invoice_id: int,
    include_replaced: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _invoice_document_access(db, invoice_id, current_user, write=False)
    documents = procurement_document_service.list_invoice_documents(
        db, invoice_id, include_replaced=include_replaced
    )
    return [_document_response(document) for document in documents]


@router.post(
    "/invoices/{invoice_id}/documents",
    response_model=LifecycleDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_invoice_document(
    invoice_id: int,
    document_type: str = Form("Invoice Document"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a real invoice supporting document and keep the legacy URL synced."""
    _invoice_document_access(db, invoice_id, current_user, write=True)
    if not document_type.strip():
        raise HTTPException(status_code=400, detail="Document type is required")
    upload = await store_document_upload(file, area="invoice_documents")
    document = procurement_document_service.create_invoice_document(
        db,
        invoice_id=invoice_id,
        document_type=document_type.strip(),
        file_name=upload.file_name,
        file_path=upload.file_path,
        file_size=upload.file_size,
        content_type=upload.content_type,
        uploaded_by=current_user.id,
    )
    return _document_response(document)


@router.get("/invoices/{invoice_id}/documents/{document_id}/download")
def download_invoice_document(
    invoice_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _invoice_document_access(db, invoice_id, current_user, write=False)
    document = procurement_document_service.get_invoice_document(db, document_id)
    if not document or document.invoice_id != invoice_id:
        raise HTTPException(status_code=404, detail="Invoice document not found")
    if not document.file_path or not os.path.isfile(document.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on disk")
    return FileResponse(document.file_path, filename=document.file_name, media_type=document.content_type)


@router.post("/invoices/{invoice_id}/documents/{document_id}/replace", response_model=LifecycleDocumentOut)
async def replace_invoice_document(
    invoice_id: int,
    document_id: int,
    document_type: str = Form("Invoice Document"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _invoice_document_access(db, invoice_id, current_user, write=True)
    existing = procurement_document_service.get_invoice_document(db, document_id)
    if not existing or existing.invoice_id != invoice_id:
        raise HTTPException(status_code=404, detail="Invoice document not found")
    upload = await store_document_upload(file, area="invoice_documents")
    try:
        replacement = procurement_document_service.replace_invoice_document(
            db,
            document_id,
            file_name=upload.file_name,
            file_path=upload.file_path,
            file_size=upload.file_size,
            content_type=upload.content_type,
            document_type=document_type.strip() or None,
            uploaded_by=current_user.id,
        )
    except ValueError as error:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not replacement:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Invoice document not found")
    return _document_response(replacement)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut, dependencies=[Depends(get_current_user)])
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, PROCUREMENT_MANAGER, FINANCE_OFFICER, VENDOR_ROLE)
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    _require_vendor_purchase_order_access(db, purchase_order, current_user)
    return invoice


@router.patch("/invoices/{invoice_id}/verify", response_model=InvoiceOut)
def verify_invoice(
    invoice_id: int,
    payload: InvoiceVerifyAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, FINANCE_OFFICER)
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.payment_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending invoices can be verified")
    invoice.payment_status = "Verified"
    db.commit()
    db.refresh(invoice)
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()
    if purchase_order:
        refresh_after_procurement_update(purchase_order.vendor_id, db)
    return invoice


@router.patch("/invoices/{invoice_id}/reject", response_model=InvoiceOut)
def reject_invoice(
    invoice_id: int,
    payload: InvoiceVerifyAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, FINANCE_OFFICER)
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.payment_status not in {"Pending", "Verified"}:
        raise HTTPException(status_code=400, detail="Only pending or verified invoices can be rejected")
    invoice.payment_status = "Rejected"
    db.commit()
    db.refresh(invoice)
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()
    if purchase_order:
        refresh_after_procurement_update(purchase_order.vendor_id, db)
    return invoice


@router.patch("/invoices/{invoice_id}/payment-status", response_model=InvoiceOut)
def update_payment_status(
    invoice_id: int,
    payload: PaymentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_procurement_role(current_user, ADMINISTRATOR, FINANCE_OFFICER)
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    allowed_transitions = {"Verified": {"Approved", "Rejected"}, "Approved": {"Paid"}}
    if payload.payment_status not in allowed_transitions.get(invoice.payment_status, set()):
        raise HTTPException(status_code=400, detail=f"Invoice cannot move from {invoice.payment_status} to {payload.payment_status}")
    invoice.payment_status = payload.payment_status
    if payload.payment_status == "Paid":
        invoice.paid_date = datetime.utcnow()
    db.commit()
    db.refresh(invoice)
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()
    if purchase_order:
        refresh_after_procurement_update(purchase_order.vendor_id, db)
    return invoice
