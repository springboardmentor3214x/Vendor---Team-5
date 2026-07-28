from fastapi import APIRouter


router = APIRouter(prefix="/procurement", tags=["Procurement"])

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

from app.services.reliability_service import recalculate_vendor_reliability
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
)

router = APIRouter(tags=["Procurement"])


VALID_PO_STATUSES = {"Draft", "Issued", "Delivered", "Cancelled", "Completed"}
VALID_DELIVERY_STATUSES = {"Awaiting Shipment", "In Transit", "Delivered", "Delayed", "Completed"}
VALID_PAYMENT_STATUSES = {"Pending", "Verified", "Approved", "Paid", "Rejected"}


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
def create_request(payload: ProcurementRequestCreate, db: Session = Depends(get_db)):
    if payload.required_delivery_date < date.today():
        raise HTTPException(status_code=400, detail="Required delivery date cannot be in the past")

    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    count = db.query(ProcurementRequest).count() + 1
    request_data = payload.model_dump(exclude={"request_number"})
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


@router.get("/procurement-requests", response_model=list[ProcurementRequestOut])
def list_requests(
    department: str | None = None,
    approval_status: str | None = None,
    priority: str | None = None,
    requested_by: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProcurementRequest)

    if department:
        query = query.filter(ProcurementRequest.department == department)
    if approval_status:
        query = query.filter(ProcurementRequest.approval_status == approval_status)
    if priority:
        query = query.filter(ProcurementRequest.priority == priority)
    if requested_by:
        query = query.filter(ProcurementRequest.requested_by == requested_by)

    return query.order_by(ProcurementRequest.created_at.desc()).all()


@router.get("/procurement-requests/{request_id}", response_model=ProcurementRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/procurement-requests/{request_id}", response_model=ProcurementRequestOut)
def update_request(request_id: int, payload: ProcurementRequestUpdate, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

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
def delete_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be deleted")

    db.delete(request)
    db.commit()
    return {"message": "Procurement request deleted successfully"}


@router.patch("/procurement-requests/{request_id}/approve", response_model=ProcurementRequestOut)
def approve_request(request_id: int, payload: ProcurementApprovalAction, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    try:
        request.approval_status = approve_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    request.approved_by = payload.approved_by
    request.approved_date = datetime.utcnow()
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, payload.approved_by, "Approved", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, payload.approved_by, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/reject", response_model=ProcurementRequestOut)
def reject_request(request_id: int, payload: ProcurementApprovalAction, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    try:
        request.approval_status = reject_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    request.approved_by = payload.approved_by
    request.approved_date = datetime.utcnow()
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, payload.approved_by, "Rejected", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, payload.approved_by, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/send-back", response_model=ProcurementRequestOut)
def send_back_request(request_id: int, payload: ProcurementApprovalAction, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    if not can_send_back_procurement_request(old_status):
        raise HTTPException(status_code=400, detail="Only pending or approved requests can be sent back")

    request.approval_status = "Sent Back"
    request.approval_remarks = payload.remarks

    log_approval_action(db, request_id, payload.approved_by, "Sent Back", payload.remarks)
    log_status_change(db, request_id, old_status, request.approval_status, payload.approved_by, payload.remarks)

    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/cancel", response_model=ProcurementRequestOut)
def cancel_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.approval_status
    try:
        request.approval_status = cancel_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_status_change(db, request_id, old_status, request.approval_status, None, "Cancelled")
    db.commit()
    db.refresh(request)
    return request


@router.get("/procurement-requests/{request_id}/status-history")
def get_status_history(request_id: int, db: Session = Depends(get_db)):
    history = (
        db.query(ProcurementStatusHistory)
        .filter(ProcurementStatusHistory.procurement_request_id == request_id)
        .order_by(ProcurementStatusHistory.changed_at.desc())
        .all()
    )
    return history


# ---------------- Vendor Assignment ----------------

@router.get("/procurement-requests/{request_id}/approved-vendors", response_model=list[ApprovedVendorOut])
def get_approved_vendors_for_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    query = db.query(Vendor).filter(Vendor.approval_status == "Approved", Vendor.vendor_status == "Active")

    if request.product_category and hasattr(Vendor, "category_id"):
        pass

    return query.order_by(Vendor.reliability_score.desc()).all()


@router.patch("/procurement-requests/{request_id}/assign-vendor", response_model=ProcurementRequestOut)
def assign_vendor(request_id: int, payload: VendorAssignmentAction, db: Session = Depends(get_db)):
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
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
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
        created_by=payload.created_by,
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


@router.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def list_purchase_orders(
    vendor_id: int | None = None,
    po_status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(PurchaseOrder)
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    if po_status:
        query = query.filter(PurchaseOrder.po_status == po_status)
    return query.order_by(PurchaseOrder.created_at.desc()).all()


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.patch("/purchase-orders/{po_id}/status", response_model=PurchaseOrderOut)
def update_purchase_order_status(po_id: int, payload: PurchaseOrderStatusUpdate, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    if payload.po_status not in VALID_PO_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid purchase order status")

    po.po_status = payload.po_status
    if payload.approved_by:
        po.approved_by = payload.approved_by

    db.commit()
    db.refresh(po)
    try:
        recalculate_vendor_reliability(po.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {po.vendor_id}: {e}")
    return po


@router.patch("/purchase-orders/{po_id}/issue", response_model=PurchaseOrderOut)
def issue_purchase_order(po_id: int, db: Session = Depends(get_db)):
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
    return po


@router.patch("/purchase-orders/{po_id}/deliver", response_model=PurchaseOrderOut)
def deliver_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
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
    try:
        recalculate_vendor_reliability(po.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {po.vendor_id}: {e}")
    return po


@router.patch("/purchase-orders/{po_id}/cancel", response_model=PurchaseOrderOut)
def cancel_purchase_order_route(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    try:
        po.po_status = cancel_purchase_order(po.po_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(po)
    try:
        recalculate_vendor_reliability(po.vendor_id, db)
    except Exception as e:
        print(f"Error recalculating reliability for vendor {po.vendor_id}: {e}")
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

@router.get("/")
def procurement_placeholder():
    return {
        "message": "Procurement API placeholder",
        "status": "ready",
    }
