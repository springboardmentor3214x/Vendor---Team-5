from app.core.database import SessionLocal
from app.models.role import Role
from app.models.vendor import Vendor
from app.models.user import User
from datetime import datetime

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

# Seed one sample vendor
sample_vendor = db.query(Vendor).filter(Vendor.email == "sample.vendor@example.com").first()
if not sample_vendor:
    sample_vendor = Vendor(
        company_name="Sample Supplies Pvt Ltd",
        vendor_category="Raw Material Suppliers",
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

db.close()
print("Seeding complete.")