from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    total_completed_orders = Column(Integer, default=0)
    on_time_delivery_rate = Column(Float, default=0.0)
    delayed_delivery_count = Column(Integer, default=0)
    average_quality_score = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)  # in minutes, per Sonali's function
    average_service_rating_score = Column(Float, default=0.0)
    overall_performance_score = Column(Float, default=0.0)
    performance_status = Column(String(50), default="Not Evaluated", index=True)
    # Suggested values: Excellent, Good, Average, Poor, Not Evaluated

    evaluation_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)