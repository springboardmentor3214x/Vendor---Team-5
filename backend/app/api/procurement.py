from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.schemas.procurement import (
    ProcurementRequestCreate,
    ProcurementRequestOut,
    PurchaseOrderCreate,
    PurchaseOrderOut,
)
from app.services.procurement_service import (
    approve_procurement_request,
    reject_procurement_request,
    cancel_procurement_request,
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


def purchase_order_response(po: PurchaseOrder):
    return {
        "id": po.id,
        "procurement_request_id": po.procurement_request_id,
        "vendor_id": po.vendor_id,
        "contract_id": po.contract_id,
        "quantity": po.quantity,
        "unit_price": po.unit_price,
        "expected_delivery_date": po.expected_delivery_date,
        "actual_delivery_date": po.actual_delivery_date,
        "po_number": po.po_number,
        "total_cost": po.total_cost,
        "payment_terms": po.payment_terms,
        "po_status": po.po_status,
        "created_at": po.created_at,
        "updated_at": po.updated_at,
    }


# ---------------- Procurement Requests ----------------


@router.post("/procurement-requests", response_model=ProcurementRequestOut)
def create_request(payload: ProcurementRequestCreate, db: Session = Depends(get_db)):
    count = db.query(ProcurementRequest).count() + 1
    request = ProcurementRequest(
        **payload.model_dump(),
        request_number=generate_procurement_request_number(count)
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/procurement-requests", response_model=list[ProcurementRequestOut])
def list_requests(db: Session = Depends(get_db)):
    return db.query(ProcurementRequest).all()


@router.get("/procurement-requests/{request_id}", response_model=ProcurementRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/procurement-requests/{request_id}/approve", response_model=ProcurementRequestOut)
def approve_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    try:
        request.approval_status = approve_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/reject", response_model=ProcurementRequestOut)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    try:
        request.approval_status = reject_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(request)
    return request


@router.patch("/procurement-requests/{request_id}/cancel", response_model=ProcurementRequestOut)
def cancel_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(ProcurementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    try:
        request.approval_status = cancel_procurement_request(request.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(request)
    return request


# ---------------- Purchase Orders ----------------


@router.post("/purchase-orders", response_model=PurchaseOrderOut)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    request = db.query(ProcurementRequest).filter(
        ProcurementRequest.id == payload.procurement_request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Procurement request not found")

    if not can_assign_vendor_to_request(request.approval_status):
        raise HTTPException(status_code=400, detail="Vendor can only be assigned to approved requests")

    if not can_create_purchase_order(request.approval_status, payload.vendor_id is not None):
        raise HTTPException(status_code=400, detail="Cannot create purchase order for this request")

    po = PurchaseOrder(
        procurement_request_id=payload.procurement_request_id,
        vendor_id=payload.vendor_id,
        contract_id=payload.contract_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_cost=calculate_total_cost(payload.quantity, payload.unit_price),
        po_number=generate_purchase_order_number(db.query(PurchaseOrder).count() + 1),
        expected_delivery_date=payload.expected_delivery_date,
        payment_terms=payload.payment_terms,
        po_status="Draft",
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return purchase_order_response(po)


@router.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def list_purchase_orders(db: Session = Depends(get_db)):
    return [purchase_order_response(po) for po in db.query(PurchaseOrder).all()]


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return purchase_order_response(po)


@router.patch("/purchase-orders/{po_id}/issue", response_model=PurchaseOrderOut)
def issue_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    try:
        po.po_status = issue_purchase_order_action(po.po_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(po)
    return purchase_order_response(po)


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
    db.commit()
    db.refresh(po)
    return purchase_order_response(po)


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
    return purchase_order_response(po)


@router.get("/purchase-orders/{po_id}/completion-check")
def check_completion(po_id: int, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    delivery_delayed = is_delivery_delayed(po.expected_delivery_date, po.actual_delivery_date)
    invoice_verified = False
    is_complete = can_complete_procurement(po.po_status, invoice_verified)
    return {
        "po_id": po_id,
        "is_complete": is_complete,
        "delivery_delayed": delivery_delayed,
        "invoice_verified": invoice_verified,
        "po_status": po.po_status,
    }