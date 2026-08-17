from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ServiceRating(Base):
    __tablename__ = "service_ratings"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    professionalism = Column(Float, nullable=True)
    customer_support = Column(Float, nullable=True)
    documentation_quality = Column(Float, nullable=True)
    flexibility = Column(Float, nullable=True)
    communication_effectiveness = Column(Float, nullable=True)
    issue_resolution = Column(Float, nullable=True)

    overall_service_rating = Column(Float, nullable=True)
    comments = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)