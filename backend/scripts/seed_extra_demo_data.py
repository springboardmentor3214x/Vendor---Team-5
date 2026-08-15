"""Add rich, idempotent demo records without changing the main seed dataset.

Run from the backend directory after ``python seed_data.py``:
    python scripts/seed_extra_demo_data.py

All accounts created by this script use the password ``Demo@123``.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.activity_log import ActivityLog
from app.models.communication import Communication
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant
from app.models.invoice import Invoice
from app.models.message import Message, RelatedEntityType
from app.models.notification import Notification
from app.models.order_tracking import OrderTracking
from app.models.performance import PerformanceRecord
from app.models.procurement_recommendation import ProcurementRecommendation
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import PerformanceTrend, VendorReliability
from app.models.vendor_reliability_score import VendorReliabilityScore
from app.models.role import Role
from app.models.user import User
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.models.vendor_contact import VendorContact
from app.models.vendor_ranking import VendorRanking


PASSWORD = "Demo@123"
NOW = datetime.utcnow()


def get_or_create_user(db, *, email: str, full_name: str, role: str, company_name: str | None = None) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        company_name=company_name,
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_vendor(db, config: dict, category: VendorCategory) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.email == config["email"]).first()
    if not vendor:
        vendor = db.query(Vendor).filter(Vendor.company_name == config["company_name"]).first()
    if not vendor:
        vendor = Vendor(
            company_name=config["company_name"],
            category_id=category.id,
            contact_person_name=config["contact_person_name"],
            designation=config["designation"],
            email=config["email"],
            phone_number=config["phone_number"],
            city=config["city"],
            state=config["state"],
            country="India",
            vendor_status="Active",
            approval_status="Approved",
            reliability_score=config["reliability_score"],
            gst_number=config["gst_number"],
            pan_number=config["pan_number"],
            payment_terms="Net 30",
        )
        db.add(vendor)
        db.flush()
    else:
        # Keep each demo portal account linked to its real vendor record.
        vendor.email = config["email"]
        vendor.vendor_status = "Active"
        vendor.approval_status = "Approved"
        vendor.reliability_score = config["reliability_score"]

    contact = db.query(VendorContact).filter(
        VendorContact.vendor_id == vendor.id,
        VendorContact.email == config["email"],
    ).first()
    if not contact:
        db.add(VendorContact(
            vendor_id=vendor.id,
            contact_person_name=config["contact_person_name"],
            designation=config["designation"],
            email=config["email"],
            phone_number=config["phone_number"],
            is_primary=True,
        ))
    return vendor


def get_or_create_request(db, *, number: str, title: str, vendor: Vendor, requester: User, project: str, budget: float) -> ProcurementRequest:
    request = db.query(ProcurementRequest).filter(ProcurementRequest.request_number == number).first()
    if request:
        return request
    request = ProcurementRequest(
        request_number=number,
        title=title,
        department="Operations",
        project_name=project,
        item_description=f"Procurement requirement for {project}",
        product_name=title,
        product_category="Operational Supplies",
        quantity=25,
        unit_of_measurement="Units",
        estimated_budget=budget,
        required_delivery_date=NOW + timedelta(days=14),
        priority="High",
        business_justification=f"Demo procurement activity for {project}",
        requested_by=requester.id,
        approval_status="Approved",
        approved_by=requester.id,
        approved_date=NOW - timedelta(days=12),
        vendor_id=vendor.id,
    )
    db.add(request)
    db.flush()
    return request


def get_or_create_po(db, *, number: str, request: ProcurementRequest, vendor: Vendor, manager: User, project: str, score: float, delayed: bool) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == number).first()
    if not po:
        po = PurchaseOrder(
            procurement_request_id=request.id,
            vendor_id=vendor.id,
            po_number=number,
            quantity=25,
            unit_price=4000.0,
            total_cost=100000.0,
            tax_details=18000.0,
            shipping_address="VendorIQ Demo Operations Centre, India",
            expected_delivery_date=NOW - timedelta(days=10),
            actual_delivery_date=NOW - timedelta(days=(4 if delayed else 11)),
            payment_terms="Net 30",
            po_status="Delivered",
            created_by=manager.id,
            approved_by=manager.id,
            assigned_procurement_manager_id=manager.id,
            project_name=project,
            po_date=NOW - timedelta(days=20),
        )
        db.add(po)
        db.flush()
    tracking = db.query(OrderTracking).filter(OrderTracking.purchase_order_id == po.id).first()
    if not tracking:
        db.add(OrderTracking(
            purchase_order_id=po.id,
            dispatch_date=NOW - timedelta(days=15),
            expected_delivery_date=NOW - timedelta(days=10),
            actual_delivery_date=po.actual_delivery_date,
            delivery_status="Delayed" if delayed else "Completed",
            delay_days=6 if delayed else 0,
            remarks="Demo delayed delivery" if delayed else "Demo delivery completed on time",
        ))
    invoice_number = number.replace("PO", "INV")
    invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    if not invoice:
        db.add(Invoice(
            purchase_order_id=po.id,
            invoice_number=invoice_number,
            invoice_amount=100000.0,
            tax_amount=18000.0,
            total_amount=118000.0,
            invoice_date=NOW - timedelta(days=9),
            due_date=NOW + timedelta(days=21),
            paid_date=NOW - timedelta(days=2),
            payment_status="Paid",
        ))
    return po


def seed_reliability(db, *, vendor: Vendor, rank: int, score: float, risk: str, project: str) -> None:
    factors = {
        "delivery_score": max(score - 2, 0),
        "quality_score": max(score - 4, 0),
        "communication_score": min(score + 2, 100),
        "compliance_score": max(score - 1, 0),
        "issue_resolution_score": max(score - 5, 0),
        "procurement_history_score": max(score - 3, 0),
    }
    reliability = db.query(VendorReliability).filter(VendorReliability.vendor_id == vendor.id).first()
    if not reliability:
        reliability = VendorReliability(vendor_id=vendor.id)
        db.add(reliability)
    for field, value in factors.items():
        setattr(reliability, field, value)
    reliability.reliability_score = score
    reliability.risk_level = risk
    reliability.recommendation = f"{project}: {'Preferred for new orders' if risk == 'Low' else 'Use with enhanced review controls'}"

    # The compact dashboard reads this legacy summary table. Seed it alongside
    # the current reliability model so chart data stays real rather than blank.
    dashboard_score = db.query(VendorReliabilityScore).filter(VendorReliabilityScore.vendor_id == vendor.id).first()
    if not dashboard_score:
        dashboard_score = VendorReliabilityScore(vendor_id=vendor.id)
        db.add(dashboard_score)
    dashboard_score.reliability_score = score
    dashboard_score.delivery_factor = factors["delivery_score"]
    dashboard_score.quality_factor = factors["quality_score"]
    dashboard_score.communication_factor = factors["communication_score"]
    dashboard_score.compliance_factor = factors["compliance_score"]
    dashboard_score.purchase_history_factor = factors["procurement_history_score"]
    dashboard_score.issue_resolution_factor = factors["issue_resolution_score"]
    dashboard_score.risk_level = f"{risk} Risk"

    performance = db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == vendor.id).first()
    if not performance:
        performance = PerformanceRecord(vendor_id=vendor.id)
        db.add(performance)
    performance.total_completed_orders = 3
    performance.on_time_delivery_rate = factors["delivery_score"]
    performance.delayed_delivery_count = 0 if risk == "Low" else 2
    performance.average_quality_score = factors["quality_score"] / 20
    performance.average_response_time = 45 if risk == "Low" else 210
    performance.average_communication_score = factors["communication_score"]
    performance.average_service_rating_score = factors["issue_resolution_score"] / 20
    performance.overall_performance_score = score
    performance.performance_status = "Excellent" if score >= 85 else "Good" if score >= 65 else "Needs Improvement"
    performance.notes = f"Seeded performance trail for {project}."

    ranking = db.query(VendorRanking).filter(VendorRanking.vendor_id == vendor.id).first()
    if not ranking:
        ranking = VendorRanking(vendor_id=vendor.id)
        db.add(ranking)
    ranking.overall_performance_score = score
    ranking.delivery_score = factors["delivery_score"]
    ranking.quality_score = factors["quality_score"]
    ranking.communication_score = factors["communication_score"]
    ranking.service_rating_score = factors["issue_resolution_score"]
    ranking.rank_position = rank

    recommendation = db.query(ProcurementRecommendation).filter(ProcurementRecommendation.vendor_id == vendor.id).first()
    if not recommendation:
        recommendation = ProcurementRecommendation(vendor_id=vendor.id, category_id=vendor.category_id)
        db.add(recommendation)
    recommendation.recommendation_score = score
    recommendation.recommendation_status = "Recommended" if risk == "Low" else "Caution"
    recommendation.reason = reliability.recommendation

    for months_ago, delta in ((2, -4), (1, -2), (0, 0)):
        month_date = NOW - timedelta(days=30 * months_ago)
        trend = db.query(PerformanceTrend).filter(
            PerformanceTrend.vendor_id == vendor.id,
            PerformanceTrend.year == month_date.year,
            PerformanceTrend.month == month_date.month,
        ).first()
        if not trend:
            trend = PerformanceTrend(vendor_id=vendor.id, year=month_date.year, month=month_date.month)
            db.add(trend)
        trend.reliability_score = score + delta
        trend.delivery_score = factors["delivery_score"] + delta
        trend.quality_score = factors["quality_score"] + delta
        trend.communication_score = factors["communication_score"] + delta
        trend.compliance_score = factors["compliance_score"] + delta
        trend.issue_resolution_score = factors["issue_resolution_score"] + delta
        trend.procurement_history_score = factors["procurement_history_score"] + delta


def add_notification(db, *, user: User, vendor: Vendor, po: PurchaseOrder, title: str, message: str, priority: str) -> None:
    existing = db.query(Notification).filter(Notification.user_id == user.id, Notification.title == title).first()
    if not existing:
        db.add(Notification(
            user_id=user.id,
            vendor_id=vendor.id,
            purchase_order_id=po.id,
            title=title,
            message=message,
            type="DELIVERY_DELAY" if priority == "HIGH" else "PROCUREMENT_ALERT",
            notification_type="DELIVERY_DELAY" if priority == "HIGH" else "PROCUREMENT_ALERT",
            related_module="Procurement",
            related_record_id=po.id,
            priority=priority,
            is_read=False,
            link=f"/procurement/purchase-orders/{po.id}",
        ))


def main() -> None:
    db = SessionLocal()
    try:
        # Roles must exist after the normal seed. This still works if an operator runs it first.
        for role_name in ("Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor", "Finance Officer", "Auditor", "Department User"):
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name, description=f"{role_name} role"))
        db.flush()

        users = {
            "aarav": get_or_create_user(db, email="aarav.sharma@vendoriq.com", full_name="Aarav Sharma", role="Procurement Manager", company_name="Bharat Procurement Services"),
            "kavya": get_or_create_user(db, email="kavya.verma@vendoriq.com", full_name="Kavya Verma", role="Vendor", company_name="Verma Industrial Supplies"),
            "rohan": get_or_create_user(db, email="rohan.singh@vendoriq.com", full_name="Rohan Singh", role="Vendor", company_name="Singh Logistics India"),
            "ananya": get_or_create_user(db, email="ananya.iyer@vendoriq.com", full_name="Ananya Iyer", role="Finance Officer", company_name="VendorIQ Finance"),
            "vivek": get_or_create_user(db, email="vivek.gupta@vendoriq.com", full_name="Vivek Gupta", role="Supply Chain Manager", company_name="Bharat Supply Chain"),
            "meera": get_or_create_user(db, email="meera.nair@vendoriq.com", full_name="Meera Nair", role="Auditor", company_name="Nair Audit Partners"),
            "aditya": get_or_create_user(db, email="aditya.joshi@vendoriq.com", full_name="Aditya Joshi", role="Department User", company_name="Operations Department"),
        }
        db.flush()

        categories = {category.name: category for category in db.query(VendorCategory).all()}
        for name in ("Equipment Vendors", "IT Vendors", "Logistics Partners", "Service Providers"):
            if name not in categories:
                category = VendorCategory(name=name, description=f"Demo {name}", is_active=True)
                db.add(category)
                db.flush()
                categories[name] = category

        vendor_configs = [
            {"email": "kavya.verma@vendoriq.com", "company_name": "Verma Industrial Supplies", "contact_person_name": "Kavya Verma", "designation": "Director", "phone_number": "9876501001", "city": "Jaipur", "state": "Rajasthan", "gst_number": "08AABCV1001A1Z1", "pan_number": "AABCV1001A", "reliability_score": 91.0, "category": "Equipment Vendors", "rank": 2, "risk": "Low", "project": "Factory Automation", "delayed": False},
            {"email": "rohan.singh@vendoriq.com", "company_name": "Singh Logistics India", "contact_person_name": "Rohan Singh", "designation": "Operations Head", "phone_number": "9876501002", "city": "Delhi", "state": "Delhi", "gst_number": "07AABCS1002A1Z2", "pan_number": "AABCS1002B", "reliability_score": 74.0, "category": "Logistics Partners", "rank": 3, "risk": "Medium", "project": "North India Distribution", "delayed": True},
            {"email": "neelam.traders@vendoriq.in", "company_name": "Neelam Office Solutions", "contact_person_name": "Neelam Kapoor", "designation": "Business Owner", "phone_number": "9876501003", "city": "Chandigarh", "state": "Punjab", "gst_number": "03AABCN1003A1Z3", "pan_number": "AABCN1003C", "reliability_score": 82.0, "category": "Service Providers", "rank": 4, "risk": "Medium", "project": "Greenfield Site", "delayed": False},
            {"email": "rajat.tech@vendoriq.in", "company_name": "Rajat Digital Systems", "contact_person_name": "Rajat Malhotra", "designation": "Managing Partner", "phone_number": "9876501004", "city": "Pune", "state": "Maharashtra", "gst_number": "27AABCR1004A1Z4", "pan_number": "AABCR1004D", "reliability_score": 63.0, "category": "IT Vendors", "rank": 5, "risk": "High", "project": "ERP Modernization", "delayed": True},
        ]

        vendors: list[tuple[Vendor, dict]] = []
        for config in vendor_configs:
            vendor = get_or_create_vendor(db, config, categories[config["category"]])
            vendors.append((vendor, config))
        db.flush()

        # Also link the standard vendor login created by the base seed script.
        standard_vendor_user = db.query(User).filter(User.email == "vendor.contact@samplesupplies.com").first()
        sample_vendor = db.query(Vendor).filter(Vendor.company_name == "Sample Supplies Pvt Ltd").first()
        if standard_vendor_user and sample_vendor:
            sample_vendor.email = standard_vendor_user.email

        for index, (vendor, config) in enumerate(vendors, start=1):
            request = get_or_create_request(
                db,
                number=f"REQ-DEMO-{index:03}",
                title=f"{config['project']} procurement package",
                vendor=vendor,
                requester=users["aditya"],
                project=config["project"],
                budget=100000.0,
            )
            po = get_or_create_po(
                db,
                number=f"PO-DEMO-{index:03}",
                request=request,
                vendor=vendor,
                manager=users["aarav"],
                project=config["project"],
                score=config["reliability_score"],
                delayed=config["delayed"],
            )
            seed_reliability(db, vendor=vendor, rank=config["rank"], score=config["reliability_score"], risk=config["risk"], project=config["project"])
            add_notification(
                db,
                user=users["aarav"],
                vendor=vendor,
                po=po,
                title=f"{config['company_name']} purchase order update",
                message=f"{po.po_number} is {'delayed and needs attention' if config['delayed'] else 'completed and ready for performance review'}.",
                priority="HIGH" if config["delayed"] else "MEDIUM",
            )

        first_vendor, first_config = vendors[0]
        first_po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == "PO-DEMO-001").first()
        if first_po:
            messages = [
                (users["aarav"], users["kavya"], "Kavya ji, please confirm final installation dates for the Factory Automation equipment."),
                (users["kavya"], users["aarav"], "Aarav ji, installation team is confirmed. We will complete delivery before Friday."),
                (users["vivek"], users["aarav"], "Please upload the acceptance report after installation so the performance cycle can close."),
            ]
            for sender, receiver, content in messages:
                exists = db.query(Message).filter(Message.sender_id == sender.id, Message.receiver_id == receiver.id, Message.content == content).first()
                if not exists:
                    db.add(Message(sender_id=sender.id, receiver_id=receiver.id, content=content, related_entity_type=RelatedEntityType.PURCHASE_ORDER, related_entity_id=first_po.id, is_read=False))

            discussion = db.query(Discussion).filter(Discussion.title == "Factory Automation delivery coordination").first()
            if not discussion:
                discussion = Discussion(title="Factory Automation delivery coordination", created_by_id=users["aarav"].id, vendor_id=first_vendor.id, purchase_order_id=first_po.id, status="OPEN")
                db.add(discussion)
                db.flush()
                for participant in (users["aarav"], users["kavya"], users["vivek"], users["ananya"]):
                    db.add(DiscussionParticipant(discussion_id=discussion.id, user_id=participant.id))

            exists = db.query(Communication).filter(Communication.subject == "Factory Automation delivery schedule").first()
            if not exists:
                db.add(Communication(sender_id=users["aarav"].id, vendor_id=first_vendor.id, procurement_request_id=first_po.procurement_request_id, subject="Factory Automation delivery schedule", message="Please share the final dispatch and commissioning plan."))

            if not db.query(ActivityLog).filter(ActivityLog.action == "DEMO_PROCUREMENT_CREATED").first():
                db.add(ActivityLog(user_id=users["aarav"].id, module="Procurement", action="DEMO_PROCUREMENT_CREATED", description="Created additional full-flow demo procurement records.", related_entity_type="PurchaseOrder", related_entity_id=first_po.id))

        db.commit()
        print("Extra demo data is ready.")
        print("Created/verified 7 Indian-named accounts and 4 additional active approved vendors.")
        print("Added linked requests, delivered POs, invoices, reliability scores, trends, messages, notifications, and discussion data.")
        print(f"All new accounts use password: {PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
