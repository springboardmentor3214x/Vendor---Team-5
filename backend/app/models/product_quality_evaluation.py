from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ProductQualityEvaluation(Base):
    __tablename__ = "product_quality_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    inspection_date = Column(DateTime, default=datetime.utcnow)

    material_quality = Column(Float, nullable=True)        # 1-5 rating
    packaging_quality = Column(Float, nullable=True)       # 1-5 rating
    quantity_accuracy = Column(Float, nullable=True)       # 1-5 rating
    specification_compliance = Column(Float, nullable=True)  # 1-5 rating
    product_defects = Column(Integer, nullable=True)       # count of defects

    overall_quality_rating = Column(Float, nullable=True)  # 1-5 stars

    inspector_remarks = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)