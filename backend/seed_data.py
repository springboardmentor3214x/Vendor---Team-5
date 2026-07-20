from app.core.database import SessionLocal
from app.models.role import Role
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.models.vendor_contact import VendorContact
from app.models.user import User
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.communication import Communication
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.service_rating import ServiceRating
from app.models.vendor_ranking import VendorRanking
from app.models.performance import PerformanceRecord
from datetime import datetime, timedelta

db = SessionLocal()

# Seed roles
roles = [
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Vendor",
    "Finance Officer",
    "Auditor",
]

for role_name in roles:
    existing = db.query(Role).filter(Role.name == role_name).first()
    if not existing:
        db.add(Role(name=role_name, description=f"{role_name} role"))

db.commit()
print(f"Seeded {len(roles)} roles.")

# Seed vendor categories
categories = [
    "Raw Material Suppliers",
    "Equipment Vendors",
    "IT Vendors",
    "Service Providers",
    "Logistics Partners",
    "Maintenance Vendors",
]

for cat_name in categories:
    existing = db.query(VendorCategory).filter(VendorCategory.name == cat_name).first()
    if not existing:
        db.add(VendorCategory(name=cat_name, description=f"{cat_name} category", is_active=True))

db.commit()
print(f"Seeded {len(categories)} vendor categories.")

# Seed one sample vendor
raw_material_category = db.query(VendorCategory).filter(VendorCategory.name == "Raw Material Suppliers").first()

sample_vendor = db.query(Vendor).filter(Vendor.email == "sample.vendor@example.com").first()
if not sample_vendor:
    sample_vendor = Vendor(
        company_name="Sample Supplies Pvt Ltd",
        category_id=raw_material_category.id,
        contact_person_name="Ravi Kumar",
        designation="Sales Manager",
        email="sample.vendor@example.com",
        phone_number="9876543210",
        city="Hyderabad",
        state="Telangana",
        country="India",
        vendor_status="Active",
        approval_status="Approved",
        reliability_score=4.2,
    )
    db.add(sample_vendor)
    db.commit()
    print("Seeded 1 sample vendor.")
else:
    print("Sample vendor already exists.")

# Seed one sample admin user
sample_user = db.query(User).filter(User.email == "admin@vendoriq.com").first()
if not sample_user:
    sample_user = User(
        full_name="Admin User",
        email="admin@vendoriq.com",
        hashed_password="placeholder_hash",
        role="Administrator",
        is_active=True,
    )
    db.add(sample_user)
    db.commit()
    print("Seeded 1 sample admin user.")
else:
    print("Sample user already exists.")

# Seed one additional vendor contact
existing_contact = db.query(VendorContact).filter(VendorContact.vendor_id == sample_vendor.id).first()
if not existing_contact:
    contact = VendorContact(
        vendor_id=sample_vendor.id,
        contact_person_name="Priya Sharma",
        designation="Accounts Manager",
        email="priya.sharma@samplesupplies.com",
        phone_number="9123456780",
        is_primary=False,
    )
    db.add(contact)
    db.commit()
    print("Seeded 1 vendor contact.")
else:
    print("Vendor contact already exists.")

# Seed one procurement request
existing_request = db.query(ProcurementRequest).filter(ProcurementRequest.request_number == "REQ-2026-001").first()
if not existing_request:
    procurement_request = ProcurementRequest(
        request_number="REQ-2026-001",
        department="Production",
        item_description="Steel rods - 500 units",
        quantity=500,
        requested_by=sample_user.id,
        request_date=datetime.utcnow() - timedelta(days=20),
        approval_status="Approved",
        approved_by=sample_user.id,
        approved_date=datetime.utcnow() - timedelta(days=18),
    )
    db.add(procurement_request)
    db.commit()
    print("Seeded 1 procurement request.")
else:
    procurement_request = existing_request
    print("Procurement request already exists.")

# Seed one purchase order
existing_po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == "PO-2026-001").first()
if not existing_po:
    purchase_order = PurchaseOrder(
        procurement_request_id=procurement_request.id,
        vendor_id=sample_vendor.id,
        po_number="PO-2026-001",
        quantity=500,
        unit_price=250.0,
        total_cost=125000.0,
        expected_delivery_date=datetime.utcnow() - timedelta(days=10),
        actual_delivery_date=datetime.utcnow() - timedelta(days=9),
        payment_terms="Net 30",
        po_status="Delivered",
    )
    db.add(purchase_order)
    db.commit()
    print("Seeded 1 purchase order.")
else:
    purchase_order = existing_po
    print("Purchase order already exists.")

# Seed one invoice
existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == "INV-2026-001").first()
if not existing_invoice:
    invoice = Invoice(
        purchase_order_id=purchase_order.id,
        invoice_number="INV-2026-001",
        invoice_amount=125000.0,
        invoice_date=datetime.utcnow() - timedelta(days=9),
        due_date=datetime.utcnow() + timedelta(days=21),
        payment_status="Pending",
    )
    db.add(invoice)
    db.commit()
    print("Seeded 1 invoice.")
else:
    print("Invoice already exists.")

# Seed one communication (general)
existing_comm = db.query(Communication).filter(Communication.subject == "PO-2026-001 Delivery Confirmation").first()
if not existing_comm:
    comm = Communication(
        sender_id=sample_user.id,
        vendor_id=sample_vendor.id,
        procurement_request_id=procurement_request.id,
        subject="PO-2026-001 Delivery Confirmation",
        message="Please confirm delivery schedule for PO-2026-001.",
        created_at=datetime.utcnow() - timedelta(days=11),
    )
    db.add(comm)
    db.commit()
    print("Seeded 1 communication.")
else:
    print("Communication already exists.")

# Seed delivery performance
existing_dp = db.query(DeliveryPerformance).filter(DeliveryPerformance.purchase_order_id == purchase_order.id).first()
if not existing_dp:
    dp = DeliveryPerformance(
        purchase_order_id=purchase_order.id,
        vendor_id=sample_vendor.id,
        expected_delivery_date=purchase_order.expected_delivery_date,
        actual_delivery_date=purchase_order.actual_delivery_date,
        delay_days=0,
        delivery_status="Early Delivery",
        remarks="Delivered 1 day early, no issues.",
    )
    db.add(dp)
    db.commit()
    print("Seeded 1 delivery performance record.")
else:
    print("Delivery performance record already exists.")

# Seed product quality evaluation
existing_pqe = db.query(ProductQualityEvaluation).filter(ProductQualityEvaluation.purchase_order_id == purchase_order.id).first()
if not existing_pqe:
    pqe = ProductQualityEvaluation(
        purchase_order_id=purchase_order.id,
        vendor_id=sample_vendor.id,
        inspection_date=datetime.utcnow() - timedelta(days=9),
        material_quality=4.5,
        packaging_quality=4.0,
        quantity_accuracy=5.0,
        specification_compliance=4.5,
        product_defects=1,
        overall_quality_rating=4.5,
        inspector_remarks="Minor packaging wear, otherwise excellent quality.",
    )
    db.add(pqe)
    db.commit()
    print("Seeded 1 product quality evaluation.")
else:
    print("Product quality evaluation already exists.")

# Seed communication log
existing_cl = db.query(CommunicationLog).filter(CommunicationLog.purchase_order_id == purchase_order.id).first()
if not existing_cl:
    sent = datetime.utcnow() - timedelta(days=15)
    responded = sent + timedelta(hours=1, minutes=30)
    cl = CommunicationLog(
        purchase_order_id=purchase_order.id,
        vendor_id=sample_vendor.id,
        message_sent_time=sent,
        vendor_response_time=responded,
        response_duration_minutes=90,
        communication_status="Responded",
        remarks="Vendor confirmed delivery schedule promptly.",
    )
    db.add(cl)
    db.commit()
    print("Seeded 1 communication log.")
else:
    print("Communication log already exists.")

# Seed service rating
existing_sr = db.query(ServiceRating).filter(ServiceRating.purchase_order_id == purchase_order.id).first()
if not existing_sr:
    sr = ServiceRating(
        purchase_order_id=purchase_order.id,
        vendor_id=sample_vendor.id,
        professionalism=4.5,
        customer_support=4.0,
        documentation_quality=4.5,
        flexibility=4.0,
        communication_effectiveness=4.5,
        issue_resolution=4.0,
        overall_service_rating=4.3,
        comments="Reliable vendor, good communication throughout.",
    )
    db.add(sr)
    db.commit()
    print("Seeded 1 service rating.")
else:
    print("Service rating already exists.")

# Seed vendor ranking (computed summary — one row per vendor)
existing_vr = db.query(VendorRanking).filter(VendorRanking.vendor_id == sample_vendor.id).first()
if not existing_vr:
    vr = VendorRanking(
        vendor_id=sample_vendor.id,
        overall_performance_score=88.5,
        delivery_score=95.0,
        quality_score=90.0,
        communication_score=100.0,
        service_rating_score=86.0,
        rank_position=1,
    )
    db.add(vr)
    db.commit()
    print("Seeded 1 vendor ranking.")
else:
    print("Vendor ranking already exists.")

# Seed performance record (summary — one row per vendor)
existing_pr = db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == sample_vendor.id).first()
if not existing_pr:
    pr = PerformanceRecord(
        vendor_id=sample_vendor.id,
        total_completed_orders=1,
        on_time_delivery_rate=100.0,
        delayed_delivery_count=0,
        average_quality_score=4.5,
        average_response_time=90.0,
        average_service_rating_score=4.3,
        overall_performance_score=88.5,
        performance_status="Excellent",
        evaluation_date=datetime.utcnow(),
        notes="Strong first evaluation cycle.",
    )
    db.add(pr)
    db.commit()
    print("Seeded 1 performance record.")
else:
    print("Performance record already exists.")

db.close()
print("Seeding complete.")