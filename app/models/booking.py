import enum
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id", ondelete="RESTRICT"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("diagnostic_tests.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_time = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)