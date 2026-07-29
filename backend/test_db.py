from app.core.database import Base, engine
from app.models.vendor import Vendor
from app.models.vendor_document import VendorDocument
from app.models.contract import Contract
from app.models.procurement import ProcurementOrder
from app.models.performance import PerformanceRecord
from app.models.user import User
from app.models.role import Role

print("Dropping old tables...")
Base.metadata.drop_all(bind=engine)
print("Creating updated tables...")
Base.metadata.create_all(bind=engine)
print("All tables recreated successfully in vendoriq database!")