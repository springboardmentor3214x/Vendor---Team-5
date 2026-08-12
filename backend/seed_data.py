from app.core.database import SessionLocal
from app.models.role import Role
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
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
from app.models.password_reset_token import PasswordResetToken
from app.models.vendor_approval_history import VendorApprovalHistory
from app.models.procurement_approval import ProcurementApproval
from app.models.order_tracking import OrderTracking
from app.models.procurement_status_history import ProcurementStatusHistory
from app.models.reliability import VendorReliability, PerformanceTrend, ProcurementRecommendation
from app.models.contract import Contract
from app.models.contract_renewal import ContractRenewal
from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.message import Message, RelatedEntityType
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
        hashed_password="placeholder_hash",  # Pranjali/auth team will replace with real bcrypt hash
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

# Seed one password reset token
existing_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == "sample_reset_token_xyz123").first()
if not existing_token:
    token = PasswordResetToken(
        user_id=sample_user.id,
        token="sample_reset_token_xyz123",
        expires_at=datetime.utcnow() + timedelta(hours=24),
        is_used=False
    )
    db.add(token)
    db.commit()
    print("Seeded 1 password reset token.")
else:
    print("Password reset token already exists.")

# Seed one vendor approval history record
existing_vah = db.query(VendorApprovalHistory).filter(VendorApprovalHistory.vendor_id == sample_vendor.id).first()
if not existing_vah:
    vah = VendorApprovalHistory(
        vendor_id=sample_vendor.id,
        acted_by=sample_user.id,
        action="Approve",
        remarks="Vendor credentials and GSTIN verified successfully.",
        action_date=datetime.utcnow() - timedelta(days=25)
    )
    db.add(vah)
    db.commit()
    print("Seeded 1 vendor approval history record.")
else:
    print("Vendor approval history already exists.")

# Seed one procurement request
existing_request = db.query(ProcurementRequest).filter(ProcurementRequest.request_number == "REQ-2026-001").first()
if not existing_request:
    procurement_request = ProcurementRequest(
        request_number="REQ-2026-001",
        title="Monthly Steel Procurement",
        department="Production",
        project_name="Alpha Expansion",
        item_description="Steel rods - 500 units",
        product_name="Grade 50 Steel Rods",
        product_category="Raw Materials",
        quantity=500,
        unit_of_measurement="Units",
        estimated_budget=125000.0,
        required_delivery_date=datetime.utcnow() - timedelta(days=5),
        priority="High",
        business_justification="Necessary for Q3 factory production schedule.",
        additional_remarks="Urgent requirement.",
        requested_by=sample_user.id,
        request_date=datetime.utcnow() - timedelta(days=20),
        approval_status="Approved",
        approved_by=sample_user.id,
        approved_date=datetime.utcnow() - timedelta(days=18),
        vendor_id=sample_vendor.id,
    )
    db.add(procurement_request)
    db.commit()
    print("Seeded 1 procurement request.")
else:
    procurement_request = existing_request
    print("Procurement request already exists.")

# Seed one procurement status history
existing_psh = db.query(ProcurementStatusHistory).filter(ProcurementStatusHistory.procurement_request_id == procurement_request.id).first()
if not existing_psh:
    psh1 = ProcurementStatusHistory(
        procurement_request_id=procurement_request.id,
        old_status=None,
        new_status="Pending",
        changed_by=sample_user.id,
        remarks="Draft submitted",
        changed_at=datetime.utcnow() - timedelta(days=20)
    )
    psh2 = ProcurementStatusHistory(
        procurement_request_id=procurement_request.id,
        old_status="Pending",
        new_status="Approved",
        changed_by=sample_user.id,
        remarks="Request approved by manager",
        changed_at=datetime.utcnow() - timedelta(days=18)
    )
    db.add(psh1)
    db.add(psh2)
    db.commit()
    print("Seeded 2 procurement status history records.")
else:
    print("Procurement status history already exists.")

# Seed one procurement approval
existing_pa = db.query(ProcurementApproval).filter(ProcurementApproval.procurement_request_id == procurement_request.id).first()
if not existing_pa:
    pa = ProcurementApproval(
        procurement_request_id=procurement_request.id,
        approved_by=sample_user.id,
        status="Approved",
        remarks="Budget approved, vendor assignment permitted.",
        approved_at=datetime.utcnow() - timedelta(days=18)
    )
    db.add(pa)
    db.commit()
    print("Seeded 1 procurement approval record.")
else:
    print("Procurement approval record already exists.")

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
        tax_details=18.0,
        shipping_address="Factory Warehouse Gate 2, Hyderabad",
        expected_delivery_date=datetime.utcnow() - timedelta(days=10),
        actual_delivery_date=datetime.utcnow() - timedelta(days=9),
        payment_terms="Net 30",
        po_status="Delivered",
        created_by=sample_user.id,
        approved_by=sample_user.id,
        assigned_procurement_manager_id=sample_user.id,
        project_name="Alpha Expansion",
        po_date=datetime.utcnow() - timedelta(days=17)
    )
    db.add(purchase_order)
    db.commit()
    print("Seeded 1 purchase order.")
else:
    purchase_order = existing_po
    print("Purchase order already exists.")

# Seed one order tracking record
existing_ot = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == purchase_order.id).first()
if not existing_ot:
    ot = OrderTracking(
        purchase_order_id=purchase_order.id,
        dispatch_date=datetime.utcnow() - timedelta(days=12),
        expected_delivery_date=purchase_order.expected_delivery_date,
        actual_delivery_date=purchase_order.actual_delivery_date,
        delivery_status="Completed",
        delay_days=0,
        remarks="Delivered intact."
    )
    db.add(ot)
    db.commit()
    print("Seeded 1 order tracking record.")
else:
    print("Order tracking record already exists.")

# Seed one invoice
existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == "INV-2026-001").first()
if not existing_invoice:
    invoice = Invoice(
        purchase_order_id=purchase_order.id,
        invoice_number="INV-2026-001",
        invoice_amount=125000.0,
        tax_amount=22500.0,
        total_amount=147500.0,
        supporting_document_url="https://example.com/invoices/INV-2026-001.pdf",
        invoice_date=datetime.utcnow() - timedelta(days=9),
        due_date=datetime.utcnow() + timedelta(days=21),
        payment_status="Verified",
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
        notes="Strong first evaluation cycle.",
    )
    db.add(pr)
    db.commit()
    print("Seeded 1 performance record.")
else:
    print("Performance record already exists.")

# Seed reliability details
existing_rel = db.query(VendorReliability).filter(VendorReliability.vendor_id == sample_vendor.id).first()
if not existing_rel:
    rel = VendorReliability(
        vendor_id=sample_vendor.id,
        delivery_score=95.0,
        quality_score=90.0,
        communication_score=100.0,
        compliance_score=100.0,
        issue_resolution_score=80.0,
        reliability_score=93.5,
        risk_level="Low",
        recommendation="Recommended vendor for procurement",
    )
    db.add(rel)
    db.commit()
    print("Seeded reliability details.")

# Seed monthly trend data for past few months
for m_offset in [2, 1, 0]:
    month_val = (datetime.utcnow().month - m_offset - 1) % 12 + 1
    year_val = datetime.utcnow().year if datetime.utcnow().month - m_offset > 0 else datetime.utcnow().year - 1
    existing_trend = db.query(PerformanceTrend).filter(
        PerformanceTrend.vendor_id == sample_vendor.id,
        PerformanceTrend.year == year_val,
        PerformanceTrend.month == month_val
    ).first()
    if not existing_trend:
        # Vary scores slightly to make trends look realistic
        score_modifier = -2.0 * m_offset
        trend = PerformanceTrend(
            vendor_id=sample_vendor.id,
            year=year_val,
            month=month_val,
            reliability_score=93.5 + score_modifier,
            delivery_score=95.0 + score_modifier,
            quality_score=90.0 + score_modifier,
            communication_score=100.0,
            compliance_score=100.0,
            issue_resolution_score=80.0 + score_modifier
        )
        db.add(trend)
db.commit()
print("Seeded monthly performance trend data.")

# Seed procurement recommendation
existing_rec = db.query(ProcurementRecommendation).filter(ProcurementRecommendation.vendor_id == sample_vendor.id).first()
if not existing_rec:
    rec = ProcurementRecommendation(
        vendor_id=sample_vendor.id,
        reliability_score=93.5,
        risk_level="Low",
        recommendation_status="Recommended",
        reason="Vendor shows high delivery rate, strong product quality, and verified compliance.",
    )
    db.add(rec)
    db.commit()
    print("Seeded procurement recommendation.")

# Seed contract
existing_contract = db.query(Contract).filter(Contract.contract_number == "CON-2026-001").first()
if not existing_contract:
    contract = Contract(
        contract_number="CON-2026-001",
        contract_title="Steel Supply Master Agreement",
        vendor_id=sample_vendor.id,
        contract_type="Supply",
        procurement_category="Raw Materials",
        start_date=datetime.utcnow() - timedelta(days=120),
        end_date=datetime.utcnow() + timedelta(days=240),
        contract_value=150000.0,
        payment_terms="Net 30",
        sla="Deliver within 7 days of PO",
        warranty_details="1-year product warranty",
        responsible_manager="John Doe",
        status="Active",
        compliance_verified=True,
    )
    db.add(contract)
    db.commit()
    print("Seeded 1 sample contract.")
else:
    print("Sample contract already exists.")

# Seed certification
existing_cert = db.query(Certification).filter(Certification.certificate_number == "ISO9001-83921").first()
if not existing_cert:
    cert = Certification(
        vendor_id=sample_vendor.id,
        certification_name="ISO 9001:2015 Quality Management System",
        certificate_number="ISO9001-83921",
        issuing_authority="TUV SUD",
        issue_date=datetime.utcnow() - timedelta(days=365),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        document_url="uploads/iso_9001_certificate.pdf"
    )
    db.add(cert)
    db.commit()
    print("Seeded 1 sample certification.")
else:
    print("Sample certification already exists.")

# Seed compliance record
existing_compliance = db.query(ComplianceRecord).filter(
    ComplianceRecord.vendor_id == sample_vendor.id,
    ComplianceRecord.compliance_type == "GST Registration"
).first()
if not existing_compliance:
    admin_user = db.query(User).filter(User.email == "admin@vendoriq.com").first()
    compliance = ComplianceRecord(
        vendor_id=sample_vendor.id,
        compliance_type="GST Registration",
        status="Compliant",
        verification_date=datetime.utcnow() - timedelta(days=10),
        verified_by=admin_user.id if admin_user else None,
        remarks="GST status active and verified against GST portal."
    )
    db.add(compliance)
    db.commit()
    print("Seeded 1 sample compliance record.")
else:
    print("Sample compliance record already exists.")

# Seed demo users for direct messaging
pm_user = db.query(User).filter(User.email == "pm.manager@vendoriq.com").first()
if not pm_user:
    pm_user = User(
        full_name="Priya Sharma",
        email="pm.manager@vendoriq.com",
        hashed_password="placeholder_hash",
        role="Procurement Manager",
        is_active=True,
    )
    db.add(pm_user)
    db.commit()

vendor_user = db.query(User).filter(User.email == "vendor.contact@samplesupplies.com").first()
if not vendor_user:
    vendor_user = User(
        full_name="Ravi Kumar",
        email="vendor.contact@samplesupplies.com",
        hashed_password="placeholder_hash",
        role="Vendor",
        company_name="Sample Supplies Pvt Ltd",
        is_active=True,
    )
    db.add(vendor_user)
    db.commit()

admin_user = db.query(User).filter(User.email == "admin@vendoriq.com").first()

# Seed sample direct messages for demo conversations
existing_messages = db.query(Message).first()
if not existing_messages:
    demo_messages = [
        Message(
            sender_id=admin_user.id,
            receiver_id=pm_user.id,
            content="Hi Priya, please review the budget allocation for procurement request REQ-2026-001.",
            related_entity_type=RelatedEntityType.PROCUREMENT_REQUEST,
            related_entity_id=procurement_request.id,
            is_read=True,
            created_at=datetime.utcnow() - timedelta(hours=12),
            read_at=datetime.utcnow() - timedelta(hours=11),
        ),
        Message(
            sender_id=pm_user.id,
            receiver_id=vendor_user.id,
            content="Hello Ravi, could you confirm the expected dispatch timeline for Purchase Order PO-2026-001?",
            related_entity_type=RelatedEntityType.PURCHASE_ORDER,
            related_entity_id=purchase_order.id,
            is_read=True,
            created_at=datetime.utcnow() - timedelta(hours=8),
            read_at=datetime.utcnow() - timedelta(hours=7),
        ),
        Message(
            sender_id=vendor_user.id,
            receiver_id=pm_user.id,
            content="Hi Priya, the batch for PO-2026-001 has been dispatched and quality compliance certificate is attached.",
            related_entity_type=RelatedEntityType.PURCHASE_ORDER,
            related_entity_id=purchase_order.id,
            is_read=False,
            created_at=datetime.utcnow() - timedelta(hours=4),
            read_at=None,
        ),
        Message(
            sender_id=admin_user.id,
            receiver_id=vendor_user.id,
            content="Ravi, please submit the renewed ISO certification documents for contract CON-2026-001 before month-end.",
            related_entity_type=RelatedEntityType.CONTRACT,
            related_entity_id=contract.id,
            is_read=False,
            created_at=datetime.utcnow() - timedelta(hours=2),
            read_at=None,
        ),
        Message(
            sender_id=vendor_user.id,
            receiver_id=admin_user.id,
            content="Understood. We will upload the verified certificates by tomorrow.",
            related_entity_type=RelatedEntityType.VENDOR,
            related_entity_id=sample_vendor.id,
            is_read=False,
            created_at=datetime.utcnow() - timedelta(minutes=30),
            read_at=None,
        ),
        Message(
            sender_id=pm_user.id,
            receiver_id=admin_user.id,
            content="Hi Admin, all pending vendor evaluations for Module 7 are up to date.",
            related_entity_type=RelatedEntityType.NONE,
            related_entity_id=None,
            is_read=False,
            created_at=datetime.utcnow() - timedelta(minutes=10),
            read_at=None,
        ),
    ]
    for msg in demo_messages:
        db.add(msg)
    db.commit()
    print(f"Seeded {len(demo_messages)} sample direct messages.")
else:
    print("Sample messages already exist.")

db.close()
print("Seeding complete.")

