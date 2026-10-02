from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    booking_id: int
    # We allow the client to simulate different outcomes for testing
    simulate_status: PaymentStatus = PaymentStatus.SUCCESS

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    status: PaymentStatus
    transaction_ref: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WebhookPayload(BaseModel):
    event_id: str
    transaction_ref: str
    status: PaymentStatus

class WebhookResponse(BaseModel):
    event_id: str
    status: str
    message: str