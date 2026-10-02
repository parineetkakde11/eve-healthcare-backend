from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.diagnostic import DiagnosticCentre, DiagnosticTest
from app.schemas.booking import BookingCreate, BookingResponse
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Ensure the appointment is in the future
    if booking_in.appointment_time.astimezone(timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Appointment time must be in the future.")

    # 2. Check if the centre exists
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == booking_in.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Diagnostic centre not found.")

    # 3. Check if the test exists AND is offered at the centre
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == booking_in.test_id).first()
    if not test or test not in centre.tests:
        raise HTTPException(status_code=400, detail="Test not found or not offered at this centre.")

    # 4. Create the booking securely
    new_booking = Booking(
        user_id=current_user.id,
        centre_id=centre.id,
        test_id=test.id,
        appointment_time=booking_in.appointment_time,
        amount=test.price,  # Server-calculated amount!
        status=BookingStatus.PENDING # Starts as PENDING
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=List[BookingResponse])
def get_bookings(
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only return bookings that belong to the logged-in user
    return db.query(Booking).filter(Booking.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    
    # Security: Prevent viewing other users' bookings
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking.")
        
    return booking

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking.")
        
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a booking that is {booking.status.value}.")
        
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking