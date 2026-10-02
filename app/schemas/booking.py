from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    centre_id: int
    test_id: int
    appointment_time: datetime

class BookingResponse(BaseModel):
    id: int
    user_id: int
    centre_id: int
    test_id: int
    appointment_time: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)