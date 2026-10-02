import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    transaction_ref = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class PaymentWebhookEvent(Base):
    __tablename__ = "payment_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(PaymentStatus), nullable=False)
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)