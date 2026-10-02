import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus, PaymentWebhookEvent
from app.schemas.payment import PaymentCreate, PaymentResponse, WebhookPayload, WebhookResponse
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments & Webhooks"])

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def simulate_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch booking and lock it for update to prevent race conditions
    booking = db.query(Booking).with_for_update().filter(Booking.id == payment_in.booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking.")
    if booking.status == BookingStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail="Booking is already confirmed and paid.")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot pay for a cancelled booking.")

    # 2. Simulate Payment Creation
    transaction_ref = f"pay_{uuid.uuid4().hex[:16]}"
    new_payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=payment_in.simulate_status,
        transaction_ref=transaction_ref
    )
    db.add(new_payment)
    
    # 3. Synchronously update booking based on simulated outcome
    if new_payment.status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    elif new_payment.status == PaymentStatus.FAILED:
        booking.status = BookingStatus.FAILED
        
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.post("/webhook/", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
def payment_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    # 1. IDEMPOTENCY CHECK: Have we seen this exact event_id before?
    existing_event = db.query(PaymentWebhookEvent).filter(PaymentWebhookEvent.event_id == payload.event_id).first()
    if existing_event:
        # Return success immediately without touching the booking again
        return WebhookResponse(
            event_id=payload.event_id, 
            status="PROCESSED", 
            message="Idempotent replay: Event already processed."
        )

    # 2. Fetch Payment and related Booking (locked for safety)
    payment = db.query(Payment).with_for_update().filter(Payment.transaction_ref == payload.transaction_ref).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction reference not found.")

    booking = db.query(Booking).with_for_update().filter(Booking.id == payment.booking_id).first()

    # 3. State transition logic
    payment.status = payload.status
    if booking.status != BookingStatus.CANCELLED:
        if payload.status == PaymentStatus.SUCCESS:
            booking.status = BookingStatus.CONFIRMED
        elif payload.status == PaymentStatus.FAILED:
            booking.status = BookingStatus.FAILED

    # 4. Record the webhook event to prevent future duplicates
    webhook_event = PaymentWebhookEvent(
        event_id=payload.event_id,
        payment_id=payment.id,
        status=payload.status,
        payload=payload.model_dump(mode="json")
    )
    db.add(webhook_event)
    
    # 5. Commit everything atomically
    try:
        db.commit()
    except IntegrityError:
        # Fallback if a duplicate event_id was inserted at the exact same millisecond
        db.rollback()
        return WebhookResponse(
            event_id=payload.event_id, 
            status="PROCESSED", 
            message="Event already processed simultaneously."
        )

    return WebhookResponse(event_id=payload.event_id, status="PROCESSED", message="Webhook processed successfully.")