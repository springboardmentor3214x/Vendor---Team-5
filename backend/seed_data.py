from app.core.database import SessionLocal
from app.models.role import Role
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.models.vendor_contact import VendorContact
from app.models.vendor_document import VendorDocument
from app.models.vendor_approval_history import VendorApprovalHistory
from app.models.user import User
from app.models.procurement_request import ProcurementRequest
from app.models.procurement_approval import ProcurementApproval
from app.models.procurement_status_history import ProcurementStatusHistory
from app.models.purchase_order import PurchaseOrder
from app.models.order_tracking import OrderTracking
from app.models.invoice import Invoice
from app.models.communication import Communication
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.service_rating import ServiceRating
from app.models.vendor_ranking import VendorRanking
from app.models.performance import PerformanceRecord
from app.models.password_reset_token import PasswordResetToken
from app.models.reliability import VendorReliability, PerformanceTrend
from app.models.procurement_recommendation import ProcurementRecommendation
from app.models.contract import Contract
from app.models.contract_renewal import ContractRenewal
from app.models.contract_document import ContractDocument
from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.notification import Notification
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant
from app.models.communication_file import CommunicationFile
from app.models.activity_log import ActivityLog
from app.models.message import Message, RelatedEntityType
from datetime import datetime, timedelta


def seed_database():
    db = SessionLocal()

    # 1. Seed Roles
    roles = [
        "Administrator",
        "Procurement Manager",
        "Supply Chain Manager",
        "Vendor",
        "Finance Officer",
        "Auditor",
        "Department User",
    ]

    for role_name in roles:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name, description=f"{role_name} role"))

    db.commit()
    print(f"Seeded {len(roles)} roles.")

    # 2. Seed Demo User Accounts
    user_configs = [
        {"email": "admin@vendoriq.com", "full_name": "Admin User", "role": "Administrator"},
        {"email": "pm.manager@vendoriq.com", "full_name": "Priya Sharma", "role": "Procurement Manager"},
        {"email": "scm.manager@vendoriq.com", "full_name": "Vikram Sethi", "role": "Supply Chain Manager"},
        {"email": "finance.officer@vendoriq.com", "full_name": "Suresh Menon", "role": "Finance Officer"},
        {"email": "auditor@vendoriq.com", "full_name": "Neha Agarwal", "role": "Auditor"},
        {"email": "dept.user@vendoriq.com", "full_name": "Anish Patel", "role": "Department User"},
        {
            "email": "vendor.contact@samplesupplies.com",
            "full_name": "Ravi Kumar",
            "role": "Vendor",
            "company_name": "Sample Supplies Pvt Ltd"
        },
    ]

    users_map = {}
    for cfg in user_configs:
        user = db.query(User).filter(User.email == cfg["email"]).first()
        if not user:
            user = User(
                full_name=cfg["full_name"],
                email=cfg["email"],
                hashed_password="placeholder_hash",
                role=cfg["role"],
                company_name=cfg.get("company_name"),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        users_map[cfg["email"]] = user

    print(f"Seeded/Verified {len(users_map)} user demo accounts.")

    admin_user = users_map["admin@vendoriq.com"]
    pm_user = users_map["pm.manager@vendoriq.com"]
    dept_user = users_map["dept.user@vendoriq.com"]
    vendor_user = users_map["vendor.contact@samplesupplies.com"]

    # 3. Seed Vendor Categories
    categories = [
        "Raw Material Suppliers",
        "Equipment Vendors",
        "IT Vendors",
        "Service Providers",
        "Logistics Partners",
        "Maintenance Vendors",
    ]

    cat_map = {}
    for cat_name in categories:
        cat = db.query(VendorCategory).filter(VendorCategory.name == cat_name).first()
        if not cat:
            cat = VendorCategory(name=cat_name, description=f"{cat_name} category", is_active=True)
            db.add(cat)
            db.commit()
            db.refresh(cat)
        cat_map[cat_name] = cat

    print(f"Seeded {len(categories)} vendor categories.")

    # 4. Seed 3 Vendors across Approved, Pending, Rejected Statuses
    vendor_configs = [
        {
            "email": "sample.vendor@example.com",
            "company_name": "Sample Supplies Pvt Ltd",
            "category": "Raw Material Suppliers",
            "contact_person_name": "Ravi Kumar",
            "designation": "Sales Manager",
            "phone_number": "9876543210",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "vendor_status": "Active",
            "approval_status": "Approved",
            "reliability_score": 4.5,
        },
        {
            "email": "sales@acmetech.com",
            "company_name": "Acme Tech Solutions",
            "category": "IT Vendors",
            "contact_person_name": "Sunil Verma",
            "designation": "Key Account Executive",
            "phone_number": "9811223344",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "vendor_status": "Pending",
            "approval_status": "Pending",
            "reliability_score": 3.5,
        },
        {
            "email": "contact@globallogistics.com",
            "company_name": "Global Logistics Inc",
            "category": "Logistics Partners",
            "contact_person_name": "Rajesh Mehta",
            "designation": "Operations Director",
            "phone_number": "9766554433",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "vendor_status": "Inactive",
            "approval_status": "Rejected",
            "reliability_score": 2.1,
        },
    ]

    vendor_map = {}
    for vcfg in vendor_configs:
        vendor = db.query(Vendor).filter(Vendor.email == vcfg["email"]).first()
        cat_obj = cat_map[vcfg["category"]]
        if not vendor:
            vendor = Vendor(
                company_name=vcfg["company_name"],
                category_id=cat_obj.id,
                contact_person_name=vcfg["contact_person_name"],
                designation=vcfg["designation"],
                email=vcfg["email"],
                phone_number=vcfg["phone_number"],
                city=vcfg["city"],
                state=vcfg["state"],
                country=vcfg["country"],
                vendor_status=vcfg["vendor_status"],
                approval_status=vcfg["approval_status"],
                reliability_score=vcfg["reliability_score"],
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
        vendor_map[vcfg["email"]] = vendor

    print(f"Seeded {len(vendor_map)} vendors.")

    vendor1 = vendor_map["sample.vendor@example.com"]
    vendor2 = vendor_map["sales@acmetech.com"]
    vendor3 = vendor_map["contact@globallogistics.com"]

    # 5. Seed Vendor Contacts
    contacts_data = [
        {
            "vendor_id": vendor1.id,
            "contact_person_name": "Priya Sharma",
            "designation": "Accounts Manager",
            "email": "priya.sharma@samplesupplies.com",
            "phone_number": "9123456780",
            "is_primary": False,
        },
        {
            "vendor_id": vendor2.id,
            "contact_person_name": "Amit Shah",
            "designation": "Technical Lead",
            "email": "amit@acmetech.com",
            "phone_number": "9811223355",
            "is_primary": True,
        },
        {
            "vendor_id": vendor3.id,
            "contact_person_name": "Karan Joshi",
            "designation": "Dispatch Officer",
            "email": "karan@globallogistics.com",
            "phone_number": "9766554444",
            "is_primary": True,
        },
    ]

    for cdata in contacts_data:
        ext = db.query(VendorContact).filter(
            VendorContact.vendor_id == cdata["vendor_id"],
            VendorContact.email == cdata["email"]
        ).first()
        if not ext:
            db.add(VendorContact(**cdata))
    db.commit()
    print("Seeded vendor contacts.")

    # 6. Seed Vendor Documents
    docs_data = [
        {
            "vendor_id": vendor1.id,
            "document_type": "GST Certificate",
            "file_name": "gst_cert_sample.pdf",
            "file_path": "uploads/vendors/gst_cert_sample.pdf",
            "content_type": "application/pdf",
            "uploaded_by": admin_user.id
        },
        {
            "vendor_id": vendor1.id,
            "document_type": "PAN Card",
            "file_name": "pan_card_sample.pdf",
            "file_path": "uploads/vendors/pan_card_sample.pdf",
            "content_type": "application/pdf",
            "uploaded_by": admin_user.id
        },
        {
            "vendor_id": vendor1.id,
            "document_type": "ISO Certificate",
            "file_name": "iso9001_sample.pdf",
            "file_path": "uploads/vendors/iso9001_sample.pdf",
            "content_type": "application/pdf",
            "uploaded_by": admin_user.id
        },
        {
            "vendor_id": vendor2.id,
            "document_type": "Company Registration Certificate",
            "file_name": "reg_cert_acme.pdf",
            "file_path": "uploads/vendors/reg_cert_acme.pdf",
            "content_type": "application/pdf",
            "uploaded_by": admin_user.id
        },
        {
            "vendor_id": vendor3.id,
            "document_type": "Other Supporting Document",
            "file_name": "financials_global.pdf",
            "file_path": "uploads/vendors/financials_global.pdf",
            "content_type": "application/pdf",
            "uploaded_by": admin_user.id
        },
    ]

    for ddata in docs_data:
        ext = db.query(VendorDocument).filter(
            VendorDocument.vendor_id == ddata["vendor_id"],
            VendorDocument.file_name == ddata["file_name"]
        ).first()
        if not ext:
            db.add(VendorDocument(**ddata))
    db.commit()
    print("Seeded vendor documents.")

    # 7. Seed Vendor Approval History
    approval_histories = [
        {
            "vendor_id": vendor1.id,
            "acted_by": admin_user.id,
            "action": "Approve",
            "remarks": "Vendor credentials and GSTIN verified successfully.",
            "action_date": datetime.utcnow() - timedelta(days=25)
        },
        {
            "vendor_id": vendor2.id,
            "acted_by": admin_user.id,
            "action": "Pending",
            "remarks": "Application under preliminary compliance review.",
            "action_date": datetime.utcnow() - timedelta(days=5)
        },
        {
            "vendor_id": vendor3.id,
            "acted_by": admin_user.id,
            "action": "Reject",
            "remarks": "Failed safety audit and incomplete tax filings.",
            "action_date": datetime.utcnow() - timedelta(days=15)
        },
    ]

    for ah in approval_histories:
        ext = db.query(VendorApprovalHistory).filter(
            VendorApprovalHistory.vendor_id == ah["vendor_id"],
            VendorApprovalHistory.action == ah["action"]
        ).first()
        if not ext:
            db.add(VendorApprovalHistory(**ah))
    db.commit()
    print("Seeded vendor approval history.")

    # 8. Seed Password Reset Token
    ext_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == "sample_reset_token_xyz123").first()
    if not ext_token:
        token = PasswordResetToken(
            user_id=admin_user.id,
            token="sample_reset_token_xyz123",
            expires_at=datetime.utcnow() + timedelta(hours=24),
            is_used=False
        )
        db.add(token)
        db.commit()

    # 9. Seed Procurement Requests (Covering Pending, Approved, Sent Back, Rejected, Cancelled)
    requests_data = [
        {
            "request_number": "REQ-2026-001",
            "title": "Monthly Steel Procurement",
            "department": "Production",
            "project_name": "Alpha Expansion",
            "item_description": "Steel rods - 500 units",
            "product_name": "Grade 50 Steel Rods",
            "product_category": "Raw Materials",
            "quantity": 500,
            "unit_of_measurement": "Units",
            "estimated_budget": 125000.0,
            "required_delivery_date": datetime.utcnow() - timedelta(days=5),
            "priority": "High",
            "business_justification": "Necessary for Q3 factory production schedule.",
            "additional_remarks": "Urgent requirement.",
            "requested_by": dept_user.id,
            "request_date": datetime.utcnow() - timedelta(days=20),
            "approval_status": "Approved",
            "approved_by": admin_user.id,
            "approved_date": datetime.utcnow() - timedelta(days=18),
            "vendor_id": vendor1.id,
        },
        {
            "request_number": "REQ-2026-002",
            "title": "IT Workstation Upgrades",
            "department": "IT",
            "project_name": "Factory Automation",
            "item_description": "High-performance laptops - 15 units",
            "product_name": "Workstation Laptops Pro",
            "product_category": "IT Equipment",
            "quantity": 15,
            "unit_of_measurement": "Units",
            "estimated_budget": 300000.0,
            "required_delivery_date": datetime.utcnow() + timedelta(days=15),
            "priority": "Medium",
            "business_justification": "Software upgrades for automation engineers.",
            "additional_remarks": "Standard specs.",
            "requested_by": dept_user.id,
            "request_date": datetime.utcnow() - timedelta(days=10),
            "approval_status": "Pending",
            "approved_by": None,
            "approved_date": None,
            "vendor_id": vendor2.id,
        },
        {
            "request_number": "REQ-2026-003",
            "title": "Office Ergonomic Chairs",
            "department": "HR",
            "project_name": "Greenfield Site",
            "item_description": "Ergonomic desk chairs - 40 units",
            "product_name": "ErgoChair Pro",
            "product_category": "Furniture",
            "quantity": 40,
            "unit_of_measurement": "Units",
            "estimated_budget": 80000.0,
            "required_delivery_date": datetime.utcnow() + timedelta(days=20),
            "priority": "Low",
            "business_justification": "Ergonomic seating compliance.",
            "additional_remarks": "Needs budget re-check.",
            "requested_by": dept_user.id,
            "request_date": datetime.utcnow() - timedelta(days=8),
            "approval_status": "Sent Back",
            "approval_remarks": "Please provide updated vendor quote.",
            "approved_by": pm_user.id,
            "approved_date": datetime.utcnow() - timedelta(days=7),
            "vendor_id": vendor1.id,
        },
        {
            "request_number": "REQ-2026-004",
            "title": "Logistics Express Fleet",
            "department": "Logistics",
            "project_name": "Q3 Logistics Overhaul",
            "item_description": "Container transport services - 5 trips",
            "product_name": "Freight Services",
            "product_category": "Logistics",
            "quantity": 5,
            "unit_of_measurement": "Trips",
            "estimated_budget": 50000.0,
            "required_delivery_date": datetime.utcnow() - timedelta(days=2),
            "priority": "High",
            "business_justification": "Inter-state raw material movement.",
            "additional_remarks": "Vendor rejected due to audit failure.",
            "requested_by": dept_user.id,
            "request_date": datetime.utcnow() - timedelta(days=14),
            "approval_status": "Rejected",
            "approval_remarks": "Selected vendor is inactive due to audit failure.",
            "approved_by": admin_user.id,
            "approved_date": datetime.utcnow() - timedelta(days=12),
            "vendor_id": vendor3.id,
        },
        {
            "request_number": "REQ-2026-005",
            "title": "Marketing Print Media",
            "department": "Marketing",
            "project_name": "Alpha Expansion",
            "item_description": "Brochures and banners",
            "product_name": "Print Material",
            "product_category": "Services",
            "quantity": 1000,
            "unit_of_measurement": "Copies",
            "estimated_budget": 15000.0,
            "required_delivery_date": datetime.utcnow() - timedelta(days=1),
            "priority": "Low",
            "business_justification": "Product launch event marketing.",
            "additional_remarks": "Event postponed.",
            "requested_by": dept_user.id,
            "request_date": datetime.utcnow() - timedelta(days=16),
            "approval_status": "Cancelled",
            "approval_remarks": "Cancelled by department lead.",
            "approved_by": pm_user.id,
            "approved_date": datetime.utcnow() - timedelta(days=15),
            "vendor_id": vendor1.id,
        },
    ]

    req_map = {}
    for rdata in requests_data:
        req = db.query(ProcurementRequest).filter(ProcurementRequest.request_number == rdata["request_number"]).first()
        if not req:
            req = ProcurementRequest(**rdata)
            db.add(req)
            db.commit()
            db.refresh(req)
        req_map[rdata["request_number"]] = req

    print(f"Seeded {len(req_map)} procurement requests.")

    # 10. Seed Procurement Status History & Approvals
    for req_num, req in req_map.items():
        ext_psh = db.query(ProcurementStatusHistory).filter(
            ProcurementStatusHistory.procurement_request_id == req.id
        ).first()
        if not ext_psh:
            db.add(ProcurementStatusHistory(
                procurement_request_id=req.id,
                old_status=None,
                new_status="Pending",
                changed_by=dept_user.id,
                remarks="Request submitted",
                changed_at=req.request_date
            ))
            if req.approval_status != "Pending":
                db.add(ProcurementStatusHistory(
                    procurement_request_id=req.id,
                    old_status="Pending",
                    new_status=req.approval_status,
                    changed_by=req.approved_by or admin_user.id,
                    remarks=req.approval_remarks or f"Status updated to {req.approval_status}",
                    changed_at=req.approved_date or datetime.utcnow()
                ))

        ext_pa = db.query(ProcurementApproval).filter(
            ProcurementApproval.procurement_request_id == req.id
        ).first()
        if not ext_pa and req.approval_status in ["Approved", "Rejected"]:
            db.add(ProcurementApproval(
                procurement_request_id=req.id,
                approved_by=req.approved_by or admin_user.id,
                status=req.approval_status,
                remarks=req.approval_remarks or "Decision recorded",
                approved_at=req.approved_date or datetime.utcnow()
            ))

    db.commit()
    print("Seeded procurement status history and approvals.")

    # 11. Seed Contracts (Active, Expiring Soon, Expired, Renewed)
    contracts_data = [
        {
            "contract_number": "CON-2026-001",
            "contract_title": "Steel Supply Master Agreement",
            "vendor_id": vendor1.id,
            "procurement_request_id": req_map["REQ-2026-001"].id,
            "contract_type": "Supply",
            "procurement_category": "Raw Materials",
            "start_date": datetime.utcnow() - timedelta(days=120),
            "end_date": datetime.utcnow() + timedelta(days=240),
            "contract_value": 150000.0,
            "payment_terms": "Net 30",
            "sla": "Deliver within 7 days of PO",
            "warranty_details": "1-year product warranty",
            "responsible_manager": "Priya Sharma",
            "responsible_manager_id": pm_user.id,
            "status": "Active",
            "compliance_verified": True,
        },
        {
            "contract_number": "CON-2026-002",
            "contract_title": "IT Equipment Maintenance Contract",
            "vendor_id": vendor2.id,
            "procurement_request_id": req_map["REQ-2026-002"].id,
            "contract_type": "Service",
            "procurement_category": "IT Equipment",
            "start_date": datetime.utcnow() - timedelta(days=350),
            "end_date": datetime.utcnow() + timedelta(days=15),  # Expiring soon
            "contract_value": 85000.0,
            "payment_terms": "Net 15",
            "sla": "24-hour response time for IT faults",
            "warranty_details": "6-month service guarantee",
            "responsible_manager": "Vikram Sethi",
            "responsible_manager_id": users_map["scm.manager@vendoriq.com"].id,
            "status": "Active",
            "compliance_verified": True,
        },
        {
            "contract_number": "CON-2026-003",
            "contract_title": "Legacy Freight Delivery SLA",
            "vendor_id": vendor3.id,
            "procurement_request_id": req_map["REQ-2026-004"].id,
            "contract_type": "Logistics",
            "procurement_category": "Logistics",
            "start_date": datetime.utcnow() - timedelta(days=400),
            "end_date": datetime.utcnow() - timedelta(days=10),  # Expired
            "contract_value": 60000.0,
            "payment_terms": "Net 30",
            "sla": "On-time cargo arrival",
            "warranty_details": "Standard freight insurance",
            "responsible_manager": "Admin User",
            "responsible_manager_id": admin_user.id,
            "status": "Expired",
            "compliance_verified": False,
        },
        {
            "contract_number": "CON-2026-004",
            "contract_title": "Raw Materials Framework Contract",
            "vendor_id": vendor1.id,
            "procurement_request_id": req_map["REQ-2026-001"].id,
            "contract_type": "Supply",
            "procurement_category": "Raw Materials",
            "start_date": datetime.utcnow() - timedelta(days=500),
            "end_date": datetime.utcnow() + timedelta(days=365),
            "contract_value": 185000.0,
            "payment_terms": "Net 30",
            "sla": "Guaranteed inventory reservation",
            "warranty_details": "Full lifetime replacement guarantee",
            "responsible_manager": "Priya Sharma",
            "responsible_manager_id": pm_user.id,
            "status": "Renewed",
            "compliance_verified": True,
        },
    ]

    contract_map = {}
    for cdata in contracts_data:
        cobj = db.query(Contract).filter(Contract.contract_number == cdata["contract_number"]).first()
        if not cobj:
            cobj = Contract(**cdata)
            db.add(cobj)
            db.commit()
            db.refresh(cobj)
        contract_map[cdata["contract_number"]] = cobj

    print(f"Seeded {len(contract_map)} contracts.")

    # 12. Seed Contract Renewal using fixed schema fields
    contract_for_renewal = contract_map["CON-2026-004"]
    ext_renewal = db.query(ContractRenewal).filter(ContractRenewal.contract_id == contract_for_renewal.id).first()
    if not ext_renewal:
        renewal = ContractRenewal(
            contract_id=contract_for_renewal.id,
            previous_end_date=datetime.utcnow() - timedelta(days=30),
            new_end_date=datetime.utcnow() + timedelta(days=365),
            renewal_date=datetime.utcnow() - timedelta(days=30),
            renewed_by=admin_user.id,
            renewal_notes="Annual renewal agreed with 5% volume discount.",
            remarks="Contract extended successfully with updated volume terms.",
            revised_contract_value=185000.0,
            renewal_value=185000.0,
        )
        db.add(renewal)
        db.commit()
        print("Seeded 1 contract renewal.")

    # 13. Seed Contract Document
    ext_cd = db.query(ContractDocument).filter(ContractDocument.contract_id == contract_map["CON-2026-001"].id).first()
    if not ext_cd:
        cd = ContractDocument(
            contract_id=contract_map["CON-2026-001"].id,
            document_type="Signed Agreement",
            file_name="steel_master_agreement_signed.pdf",
            file_path="uploads/contracts/steel_master_agreement_signed.pdf"
        )
        db.add(cd)
        db.commit()
        print("Seeded contract document.")

    # 14. Seed Purchase Orders & Order Tracking (Draft, Issued/In Transit, Delivered, Delayed, Completed, Cancelled)
    po_configs = [
        {
            "procurement_request_id": req_map["REQ-2026-001"].id,
            "vendor_id": vendor1.id,
            "contract_id": contract_map["CON-2026-001"].id,
            "po_number": "PO-2026-001",
            "quantity": 500,
            "unit_price": 250.0,
            "total_cost": 125000.0,
            "tax_details": 18.0,
            "shipping_address": "Factory Warehouse Gate 2, Hyderabad",
            "expected_delivery_date": datetime.utcnow() - timedelta(days=10),
            "actual_delivery_date": datetime.utcnow() - timedelta(days=9),
            "payment_terms": "Net 30",
            "po_status": "Delivered",
            "created_by": admin_user.id,
            "approved_by": admin_user.id,
            "assigned_procurement_manager_id": pm_user.id,
            "project_name": "Alpha Expansion",
            "po_date": datetime.utcnow() - timedelta(days=17),
            "tracking": {
                "dispatch_date": datetime.utcnow() - timedelta(days=12),
                "delivery_status": "Completed",
                "delay_days": 0,
                "remarks": "Delivered intact."
            }
        },
        {
            "procurement_request_id": req_map["REQ-2026-002"].id,
            "vendor_id": vendor2.id,
            "contract_id": contract_map["CON-2026-002"].id,
            "po_number": "PO-2026-002",
            "quantity": 15,
            "unit_price": 20000.0,
            "total_cost": 300000.0,
            "tax_details": 18.0,
            "shipping_address": "IT Support Desk, Bengaluru",
            "expected_delivery_date": datetime.utcnow() + timedelta(days=5),
            "actual_delivery_date": None,
            "payment_terms": "Net 15",
            "po_status": "Issued",
            "created_by": pm_user.id,
            "approved_by": admin_user.id,
            "assigned_procurement_manager_id": pm_user.id,
            "project_name": "Factory Automation",
            "po_date": datetime.utcnow() - timedelta(days=3),
            "tracking": {
                "dispatch_date": datetime.utcnow() - timedelta(days=1),
                "delivery_status": "In Transit",
                "delay_days": 0,
                "remarks": "Shipped via Express Courier."
            }
        },
        {
            "procurement_request_id": req_map["REQ-2026-003"].id,
            "vendor_id": vendor1.id,
            "contract_id": contract_map["CON-2026-004"].id,
            "po_number": "PO-2026-003",
            "quantity": 40,
            "unit_price": 2000.0,
            "total_cost": 80000.0,
            "tax_details": 12.0,
            "shipping_address": "Greenfield Office, Pune",
            "expected_delivery_date": datetime.utcnow() + timedelta(days=15),
            "actual_delivery_date": None,
            "payment_terms": "Net 30",
            "po_status": "Draft",
            "created_by": pm_user.id,
            "approved_by": None,
            "assigned_procurement_manager_id": users_map["scm.manager@vendoriq.com"].id,
            "project_name": "Greenfield Site",
            "po_date": datetime.utcnow() - timedelta(days=1),
            "tracking": {
                "dispatch_date": None,
                "delivery_status": "Awaiting Shipment",
                "delay_days": 0,
                "remarks": "Draft order created."
            }
        },
        {
            "procurement_request_id": req_map["REQ-2026-004"].id,
            "vendor_id": vendor3.id,
            "contract_id": contract_map["CON-2026-003"].id,
            "po_number": "PO-2026-004",
            "quantity": 5,
            "unit_price": 10000.0,
            "total_cost": 50000.0,
            "tax_details": 18.0,
            "shipping_address": "Logistics Hub, Mumbai",
            "expected_delivery_date": datetime.utcnow() - timedelta(days=5),
            "actual_delivery_date": None,
            "payment_terms": "Net 30",
            "po_status": "Cancelled",
            "created_by": admin_user.id,
            "approved_by": admin_user.id,
            "assigned_procurement_manager_id": pm_user.id,
            "project_name": "Q3 Logistics Overhaul",
            "po_date": datetime.utcnow() - timedelta(days=10),
            "tracking": {
                "dispatch_date": None,
                "delivery_status": "Cancelled",
                "delay_days": 0,
                "remarks": "Order cancelled due to vendor rejection."
            }
        },
        {
            "procurement_request_id": req_map["REQ-2026-005"].id,
            "vendor_id": vendor1.id,
            "contract_id": contract_map["CON-2026-001"].id,
            "po_number": "PO-2026-005",
            "quantity": 100,
            "unit_price": 150.0,
            "total_cost": 15000.0,
            "tax_details": 18.0,
            "shipping_address": "Marketing Store, Hyderabad",
            "expected_delivery_date": datetime.utcnow() - timedelta(days=12),
            "actual_delivery_date": datetime.utcnow() - timedelta(days=8),
            "payment_terms": "Net 30",
            "po_status": "Delivered",
            "created_by": pm_user.id,
            "approved_by": admin_user.id,
            "assigned_procurement_manager_id": pm_user.id,
            "project_name": "Alpha Expansion",
            "po_date": datetime.utcnow() - timedelta(days=20),
            "tracking": {
                "dispatch_date": datetime.utcnow() - timedelta(days=15),
                "delivery_status": "Delayed",
                "delay_days": 4,
                "remarks": "Delivered 4 days after expected date due to weather."
            }
        },
    ]

    po_map = {}
    for pcfg in po_configs:
        tr_info = pcfg.pop("tracking")
        po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == pcfg["po_number"]).first()
        if not po:
            po = PurchaseOrder(**pcfg)
            db.add(po)
            db.commit()
            db.refresh(po)
        po_map[pcfg["po_number"]] = po

        ext_ot = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po.id).first()
        if not ext_ot:
            ot = OrderTracking(
                purchase_order_id=po.id,
                dispatch_date=tr_info["dispatch_date"],
                expected_delivery_date=po.expected_delivery_date or datetime.utcnow(),
                actual_delivery_date=po.actual_delivery_date,
                delivery_status=tr_info["delivery_status"],
                delay_days=tr_info["delay_days"],
                remarks=tr_info["remarks"]
            )
            db.add(ot)
            db.commit()

    print(f"Seeded {len(po_map)} purchase orders and tracking records.")

    # 15. Seed Invoices (Pending, Verified, Approved, Paid, Rejected)
    invoices_data = [
        {
            "purchase_order_id": po_map["PO-2026-001"].id,
            "invoice_number": "INV-2026-001",
            "invoice_amount": 125000.0,
            "tax_amount": 22500.0,
            "total_amount": 147500.0,
            "supporting_document_url": "https://example.com/invoices/INV-2026-001.pdf",
            "invoice_date": datetime.utcnow() - timedelta(days=9),
            "due_date": datetime.utcnow() + timedelta(days=21),
            "paid_date": None,
            "payment_status": "Verified",
        },
        {
            "purchase_order_id": po_map["PO-2026-001"].id,
            "invoice_number": "INV-2026-002",
            "invoice_amount": 15000.0,
            "tax_amount": 2700.0,
            "total_amount": 17700.0,
            "supporting_document_url": "https://example.com/invoices/INV-2026-002.pdf",
            "invoice_date": datetime.utcnow() - timedelta(days=25),
            "due_date": datetime.utcnow() - timedelta(days=5),
            "paid_date": datetime.utcnow() - timedelta(days=4),
            "payment_status": "Paid",
        },
        {
            "purchase_order_id": po_map["PO-2026-002"].id,
            "invoice_number": "INV-2026-003",
            "invoice_amount": 300000.0,
            "tax_amount": 54000.0,
            "total_amount": 354000.0,
            "supporting_document_url": "https://example.com/invoices/INV-2026-003.pdf",
            "invoice_date": datetime.utcnow() - timedelta(days=2),
            "due_date": datetime.utcnow() + timedelta(days=28),
            "paid_date": None,
            "payment_status": "Pending",
        },
        {
            "purchase_order_id": po_map["PO-2026-002"].id,
            "invoice_number": "INV-2026-004",
            "invoice_amount": 50000.0,
            "tax_amount": 9000.0,
            "total_amount": 59000.0,
            "supporting_document_url": "https://example.com/invoices/INV-2026-004.pdf",
            "invoice_date": datetime.utcnow() - timedelta(days=4),
            "due_date": datetime.utcnow() + timedelta(days=26),
            "paid_date": None,
            "payment_status": "Approved",
        },
        {
            "purchase_order_id": po_map["PO-2026-004"].id,
            "invoice_number": "INV-2026-005",
            "invoice_amount": 50000.0,
            "tax_amount": 9000.0,
            "total_amount": 59000.0,
            "supporting_document_url": "https://example.com/invoices/INV-2026-005.pdf",
            "invoice_date": datetime.utcnow() - timedelta(days=7),
            "due_date": datetime.utcnow() + timedelta(days=23),
            "paid_date": None,
            "payment_status": "Rejected",
        },
    ]

    for inv in invoices_data:
        ext = db.query(Invoice).filter(Invoice.invoice_number == inv["invoice_number"]).first()
        if not ext:
            db.add(Invoice(**inv))
    db.commit()
    print(f"Seeded {len(invoices_data)} invoices.")

    # 16. Seed Delivery Performance, Quality, Communication Logs & Service Ratings
    po1 = po_map["PO-2026-001"]
    ext_dp = db.query(DeliveryPerformance).filter(DeliveryPerformance.purchase_order_id == po1.id).first()
    if not ext_dp:
        db.add(DeliveryPerformance(
            purchase_order_id=po1.id,
            vendor_id=vendor1.id,
            expected_delivery_date=po1.expected_delivery_date,
            actual_delivery_date=po1.actual_delivery_date,
            delay_days=0,
            delivery_status="Early Delivery",
            remarks="Delivered 1 day early, no issues."
        ))

    ext_pqe = db.query(ProductQualityEvaluation).filter(ProductQualityEvaluation.purchase_order_id == po1.id).first()
    if not ext_pqe:
        db.add(ProductQualityEvaluation(
            purchase_order_id=po1.id,
            vendor_id=vendor1.id,
            inspection_date=datetime.utcnow() - timedelta(days=9),
            material_quality=4.5,
            packaging_quality=4.0,
            quantity_accuracy=5.0,
            specification_compliance=4.5,
            product_defects=1,
            overall_quality_rating=4.5,
            inspector_remarks="Minor packaging wear, otherwise excellent quality."
        ))

    ext_cl = db.query(CommunicationLog).filter(CommunicationLog.purchase_order_id == po1.id).first()
    if not ext_cl:
        sent = datetime.utcnow() - timedelta(days=15)
        db.add(CommunicationLog(
            purchase_order_id=po1.id,
            vendor_id=vendor1.id,
            message_sent_time=sent,
            vendor_response_time=sent + timedelta(hours=1, minutes=30),
            response_duration_minutes=90,
            communication_status="Responded",
            remarks="Vendor confirmed delivery schedule promptly."
        ))

    ext_sr = db.query(ServiceRating).filter(ServiceRating.purchase_order_id == po1.id).first()
    if not ext_sr:
        db.add(ServiceRating(
            purchase_order_id=po1.id,
            vendor_id=vendor1.id,
            professionalism=4.5,
            customer_support=4.0,
            documentation_quality=4.5,
            flexibility=4.0,
            communication_effectiveness=4.5,
            issue_resolution=4.0,
            overall_service_rating=4.3,
            comments="Reliable vendor, good communication throughout."
        ))

    db.commit()

    # 17. Seed Performance Records, Reliability, Trends, Rankings & Recommendations for 3 Vendors
    vendor_reliability_configs = [
        {
            "vendor_id": vendor1.id,
            "overall_performance_score": 88.5,
            "delivery_score": 95.0,
            "quality_score": 90.0,
            "communication_score": 100.0,
            "compliance_score": 100.0,
            "issue_resolution_score": 80.0,
            "procurement_history_score": 92.0,
            "service_rating_score": 86.0,
            "reliability_score": 93.5,
            "risk_level": "Low",
            "recommendation": "Recommended vendor for procurement",
            "rank_position": 1,
            "performance_status": "Excellent",
        },
        {
            "vendor_id": vendor2.id,
            "overall_performance_score": 72.0,
            "delivery_score": 75.0,
            "quality_score": 70.0,
            "communication_score": 80.0,
            "compliance_score": 85.0,
            "issue_resolution_score": 65.0,
            "procurement_history_score": 70.0,
            "service_rating_score": 70.0,
            "reliability_score": 72.0,
            "risk_level": "Medium",
            "recommendation": "Conditional approval with periodic auditing",
            "rank_position": 2,
            "performance_status": "Good",
        },
        {
            "vendor_id": vendor3.id,
            "overall_performance_score": 45.0,
            "delivery_score": 40.0,
            "quality_score": 50.0,
            "communication_score": 50.0,
            "compliance_score": 40.0,
            "issue_resolution_score": 30.0,
            "procurement_history_score": 40.0,
            "service_rating_score": 40.0,
            "reliability_score": 45.0,
            "risk_level": "High",
            "recommendation": "Not recommended due to quality and delivery delays",
            "rank_position": 3,
            "performance_status": "Poor",
        },
    ]

    for vrc in vendor_reliability_configs:
        vid = vrc["vendor_id"]

        ext_pr = db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == vid).first()
        if not ext_pr:
            db.add(PerformanceRecord(
                vendor_id=vid,
                total_completed_orders=1 if vid == vendor1.id else 0,
                on_time_delivery_rate=vrc["delivery_score"],
                delayed_delivery_count=0 if vid == vendor1.id else 1,
                average_quality_score=vrc["quality_score"] / 20.0,
                average_response_time=90.0 if vid == vendor1.id else 240.0,
                average_communication_score=vrc["communication_score"],
                average_service_rating_score=vrc["service_rating_score"] / 20.0,
                overall_performance_score=vrc["overall_performance_score"],
                performance_status=vrc["performance_status"],
                notes=f"Evaluation cycle completed with status: {vrc['performance_status']}."
            ))

        ext_vr = db.query(VendorRanking).filter(VendorRanking.vendor_id == vid).first()
        if not ext_vr:
            db.add(VendorRanking(
                vendor_id=vid,
                overall_performance_score=vrc["overall_performance_score"],
                delivery_score=vrc["delivery_score"],
                quality_score=vrc["quality_score"],
                communication_score=vrc["communication_score"],
                service_rating_score=vrc["service_rating_score"],
                rank_position=vrc["rank_position"]
            ))

        ext_rel = db.query(VendorReliability).filter(VendorReliability.vendor_id == vid).first()
        if not ext_rel:
            db.add(VendorReliability(
                vendor_id=vid,
                delivery_score=vrc["delivery_score"],
                quality_score=vrc["quality_score"],
                communication_score=vrc["communication_score"],
                compliance_score=vrc["compliance_score"],
                issue_resolution_score=vrc["issue_resolution_score"],
                procurement_history_score=vrc["procurement_history_score"],
                reliability_score=vrc["reliability_score"],
                risk_level=vrc["risk_level"],
                recommendation=vrc["recommendation"]
            ))

        ext_rec = db.query(ProcurementRecommendation).filter(ProcurementRecommendation.vendor_id == vid).first()
        if not ext_rec:
            db.add(ProcurementRecommendation(
                vendor_id=vid,
                category_id=db.query(Vendor).get(vid).category_id,
                recommendation_score=vrc["reliability_score"],
                recommendation_status="Recommended" if vrc["risk_level"] == "Low" else ("Caution" if vrc["risk_level"] == "Medium" else "Not Recommended"),
                reason=vrc["recommendation"]
            ))

        # Seed monthly trend rows for each vendor
        for m_offset in [2, 1, 0]:
            month_val = (datetime.utcnow().month - m_offset - 1) % 12 + 1
            year_val = datetime.utcnow().year if datetime.utcnow().month - m_offset > 0 else datetime.utcnow().year - 1
            ext_trend = db.query(PerformanceTrend).filter(
                PerformanceTrend.vendor_id == vid,
                PerformanceTrend.year == year_val,
                PerformanceTrend.month == month_val
            ).first()
            if not ext_trend:
                score_mod = -1.5 * m_offset
                db.add(PerformanceTrend(
                    vendor_id=vid,
                    year=year_val,
                    month=month_val,
                    reliability_score=vrc["reliability_score"] + score_mod,
                    delivery_score=vrc["delivery_score"] + score_mod,
                    quality_score=vrc["quality_score"] + score_mod,
                    communication_score=vrc["communication_score"],
                    compliance_score=vrc["compliance_score"],
                    issue_resolution_score=vrc["issue_resolution_score"] + score_mod,
                    procurement_history_score=vrc["procurement_history_score"] + score_mod
                ))

    db.commit()
    print("Seeded performance, reliability, trends, rankings, and recommendations.")

    # 18. Seed Certifications & Compliance Records
    certs_data = [
        {
            "vendor_id": vendor1.id,
            "certification_name": "ISO 9001:2015 Quality Management System",
            "certificate_number": "ISO9001-83921",
            "issuing_authority": "TUV SUD",
            "issue_date": datetime.utcnow() - timedelta(days=365),
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "document_url": "uploads/iso_9001_certificate.pdf"
        },
        {
            "vendor_id": vendor2.id,
            "certification_name": "ISO 27001 Information Security",
            "certificate_number": "ISO27001-11029",
            "issuing_authority": "BSI Group",
            "issue_date": datetime.utcnow() - timedelta(days=200),
            "expiry_date": datetime.utcnow() + timedelta(days=165),
            "document_url": "uploads/iso_27001_certificate.pdf"
        },
        {
            "vendor_id": vendor3.id,
            "certification_name": "Safety Operations Compliance",
            "certificate_number": "SOC-99211",
            "issuing_authority": "Bureau Veritas",
            "issue_date": datetime.utcnow() - timedelta(days=400),
            "expiry_date": datetime.utcnow() - timedelta(days=35),  # Expired
            "document_url": "uploads/safety_compliance_cert.pdf"
        },
    ]

    for cert in certs_data:
        ext = db.query(Certification).filter(Certification.certificate_number == cert["certificate_number"]).first()
        if not ext:
            db.add(Certification(**cert))

    compliance_data = [
        {
            "vendor_id": vendor1.id,
            "compliance_type": "GST Registration",
            "status": "Compliant",
            "verification_date": datetime.utcnow() - timedelta(days=10),
            "verified_by": admin_user.id,
            "remarks": "GST status active and verified against GST portal."
        },
        {
            "vendor_id": vendor2.id,
            "compliance_type": "Tax Compliance",
            "status": "Under Review",
            "verification_date": datetime.utcnow() - timedelta(days=5),
            "verified_by": admin_user.id,
            "remarks": "Awaiting latest tax clearance document."
        },
        {
            "vendor_id": vendor3.id,
            "compliance_type": "Safety Audit",
            "status": "Non-Compliant",
            "verification_date": datetime.utcnow() - timedelta(days=15),
            "verified_by": admin_user.id,
            "remarks": "Failed safety clearance audit."
        },
    ]

    for comp in compliance_data:
        ext = db.query(ComplianceRecord).filter(
            ComplianceRecord.vendor_id == comp["vendor_id"],
            ComplianceRecord.compliance_type == comp["compliance_type"]
        ).first()
        if not ext:
            db.add(ComplianceRecord(**comp))

    db.commit()
    print("Seeded certifications and compliance records.")

    # 19. Seed Notifications (Read & Unread)
    scm_user = users_map["scm.manager@vendoriq.com"]
    notifications_data = [
        {
            "user_id": admin_user.id,
            "vendor_id": vendor2.id,
            "title": "New Vendor Application Pending",
            "message": "Acme Tech Solutions has submitted a new vendor registration application for IT Vendors.",
            "notification_type": "VENDOR_APPROVAL",
            "type": "VENDOR_APPROVAL",
            "related_module": "Vendor",
            "related_record_id": vendor2.id,
            "priority": "HIGH",
            "is_read": False,
        },
        {
            "user_id": pm_user.id,
            "purchase_order_id": po_map["PO-2026-002"].id,
            "title": "Purchase Order Dispatched",
            "message": "Purchase Order PO-2026-002 has been shipped by Acme Tech Solutions.",
            "notification_type": "PROCUREMENT_ALERT",
            "type": "PROCUREMENT_ALERT",
            "related_module": "Procurement",
            "related_record_id": po_map["PO-2026-002"].id,
            "priority": "MEDIUM",
            "is_read": True,
            "read_at": datetime.utcnow() - timedelta(hours=1)
        },
        {
            "user_id": scm_user.id,
            "contract_id": contract_map["CON-2026-002"].id,
            "title": "Contract Expiring Soon",
            "message": "Contract CON-2026-002 (IT Equipment Maintenance) expires in 15 days.",
            "notification_type": "CONTRACT_EXPIRY",
            "type": "CONTRACT_EXPIRY",
            "related_module": "Contracts",
            "related_record_id": contract_map["CON-2026-002"].id,
            "priority": "HIGH",
            "is_read": False,
        },
        {
            "user_id": vendor_user.id,
            "purchase_order_id": po_map["PO-2026-001"].id,
            "title": "Invoice Payment Verified",
            "message": "Invoice INV-2026-001 has been successfully verified by Finance.",
            "notification_type": "INVOICE_UPDATE",
            "type": "INVOICE_UPDATE",
            "related_module": "Finance",
            "related_record_id": po_map["PO-2026-001"].id,
            "priority": "MEDIUM",
            "is_read": True,
            "read_at": datetime.utcnow() - timedelta(hours=5)
        },
    ]

    for ndata in notifications_data:
        ext = db.query(Notification).filter(
            Notification.user_id == ndata["user_id"],
            Notification.title == ndata["title"]
        ).first()
        if not ext:
            db.add(Notification(**ndata))

    db.commit()
    print("Seeded notifications.")

    # 20. Seed Communications & Direct Messages
    ext_comm = db.query(Communication).filter(Communication.subject == "PO-2026-001 Delivery Confirmation").first()
    if not ext_comm:
        comm = Communication(
            sender_id=admin_user.id,
            vendor_id=vendor1.id,
            procurement_request_id=req_map["REQ-2026-001"].id,
            subject="PO-2026-001 Delivery Confirmation",
            message="Please confirm delivery schedule for PO-2026-001.",
            created_at=datetime.utcnow() - timedelta(days=11),
        )
        db.add(comm)
        db.commit()

    ext_msgs = db.query(Message).first()
    if not ext_msgs:
        demo_messages = [
            Message(
                sender_id=admin_user.id,
                receiver_id=pm_user.id,
                content="Hi Priya, please review the budget allocation for procurement request REQ-2026-001.",
                related_entity_type=RelatedEntityType.PROCUREMENT_REQUEST,
                related_entity_id=req_map["REQ-2026-001"].id,
                is_read=True,
                created_at=datetime.utcnow() - timedelta(hours=12),
                read_at=datetime.utcnow() - timedelta(hours=11),
            ),
            Message(
                sender_id=pm_user.id,
                receiver_id=vendor_user.id,
                content="Hello Ravi, could you confirm the expected dispatch timeline for Purchase Order PO-2026-001?",
                related_entity_type=RelatedEntityType.PURCHASE_ORDER,
                related_entity_id=po_map["PO-2026-001"].id,
                is_read=True,
                created_at=datetime.utcnow() - timedelta(hours=8),
                read_at=datetime.utcnow() - timedelta(hours=7),
            ),
            Message(
                sender_id=vendor_user.id,
                receiver_id=pm_user.id,
                content="Hi Priya, the batch for PO-2026-001 has been dispatched and quality compliance certificate is attached.",
                related_entity_type=RelatedEntityType.PURCHASE_ORDER,
                related_entity_id=po_map["PO-2026-001"].id,
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=4),
                read_at=None,
            ),
            Message(
                sender_id=admin_user.id,
                receiver_id=vendor_user.id,
                content="Ravi, please submit the renewed ISO certification documents for contract CON-2026-001 before month-end.",
                related_entity_type=RelatedEntityType.CONTRACT,
                related_entity_id=contract_map["CON-2026-001"].id,
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=2),
                read_at=None,
            ),
        ]
        for msg in demo_messages:
            db.add(msg)
        db.commit()

    print("Seeded communications and direct messages.")

    # 21. Seed Modules 7-9 Data: Discussions, Discussion Participants, Communication Files & Activity Logs
    ext_disc = db.query(Discussion).filter(Discussion.title == "Q3 Raw Material Pricing & Volume Discount Negotiation").first()
    if not ext_disc:
        disc = Discussion(
            title="Q3 Raw Material Pricing & Volume Discount Negotiation",
            created_by_id=pm_user.id,
            vendor_id=vendor1.id,
            procurement_request_id=req_map["REQ-2026-001"].id,
            purchase_order_id=po_map["PO-2026-001"].id,
            contract_id=contract_map["CON-2026-001"].id,
            status="OPEN",
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add(disc)
        db.commit()
        db.refresh(disc)

        # Add participants
        for p_user in [pm_user, admin_user, vendor_user]:
            db.add(DiscussionParticipant(
                discussion_id=disc.id,
                user_id=p_user.id,
                joined_at=datetime.utcnow() - timedelta(days=3)
            ))

        # Add Communication File Attachment
        db.add(CommunicationFile(
            filename="q3_pricing_breakdown.pdf",
            file_path="uploads/discussions/q3_pricing_breakdown.pdf",
            file_type="application/pdf",
            file_size=245000,
            uploaded_by_id=pm_user.id,
            discussion_id=disc.id,
            vendor_id=vendor1.id,
            procurement_request_id=req_map["REQ-2026-001"].id,
            purchase_order_id=po_map["PO-2026-001"].id,
            contract_id=contract_map["CON-2026-001"].id
        ))
        db.commit()

    print("Seeded discussions, participants, and communication files.")

    # Seed Activity Logs
    activities = [
        {
            "user_id": admin_user.id,
            "module": "Vendor",
            "action": "VENDOR_APPROVED",
            "description": "Approved vendor application for Sample Supplies Pvt Ltd.",
            "related_entity_type": "Vendor",
            "related_entity_id": vendor1.id,
            "ip_address": "127.0.0.1"
        },
        {
            "user_id": pm_user.id,
            "module": "Procurement",
            "action": "PO_CREATED",
            "description": "Issued Purchase Order PO-2026-001 for Steel Procurement.",
            "related_entity_type": "PurchaseOrder",
            "related_entity_id": po_map["PO-2026-001"].id,
            "ip_address": "127.0.0.1"
        },
        {
            "user_id": admin_user.id,
            "module": "Contracts",
            "action": "CONTRACT_RENEWED",
            "description": "Executed annual renewal for Contract CON-2026-004.",
            "related_entity_type": "Contract",
            "related_entity_id": contract_map["CON-2026-004"].id,
            "ip_address": "127.0.0.1"
        },
        {
            "user_id": pm_user.id,
            "module": "Communication",
            "action": "DISCUSSION_CREATED",
            "description": "Opened discussion thread for Q3 Raw Material Pricing Negotiation.",
            "related_entity_type": "Discussion",
            "related_entity_id": 1,
            "ip_address": "127.0.0.1"
        },
    ]

    for act in activities:
        ext_act = db.query(ActivityLog).filter(
            ActivityLog.module == act["module"],
            ActivityLog.action == act["action"],
            ActivityLog.description == act["description"]
        ).first()
        if not ext_act:
            db.add(ActivityLog(**act))

    db.commit()
    print("Seeded activity logs.")

    db.close()
    print("Seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
