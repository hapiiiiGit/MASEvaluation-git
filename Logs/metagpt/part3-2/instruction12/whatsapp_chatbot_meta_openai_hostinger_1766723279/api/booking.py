from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, constr
from datetime import datetime

from db.database import get_db
from db.models import Booking, BookingStatus, Customer

router = APIRouter(prefix="/booking", tags=["Booking"])

class BookingCreateRequest(BaseModel):
    customer_id: int
    service_type: constr(min_length=1, max_length=64)

class BookingResponse(BaseModel):
    id: int
    customer_id: int
    service_type: str
    status: BookingStatus
    created_at: datetime

    class Config:
        orm_mode = True

class BookingUpdateStatusRequest(BaseModel):
    status: BookingStatus

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(request: BookingCreateRequest, db: Session = Depends(get_db)):
    # Ensure customer exists
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    booking = Booking(
        customer_id=request.customer_id,
        service_type=request.service_type,
        status=BookingStatus.PENDING
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return booking

@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    request: BookingUpdateStatusRequest,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    booking.status = request.status
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    db: Session = Depends(get_db)
):
    query = db.query(Booking)
    if customer_id is not None:
        query = query.filter(Booking.customer_id == customer_id)
    if status is not None:
        query = query.filter(Booking.status == status)
    bookings = query.order_by(Booking.created_at.desc()).all()
    return bookings