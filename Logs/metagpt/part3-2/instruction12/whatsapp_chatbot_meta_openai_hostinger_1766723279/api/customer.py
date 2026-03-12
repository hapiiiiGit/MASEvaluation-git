from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, constr

from db.database import get_db
from db.models import Customer

router = APIRouter(prefix="/customer", tags=["Customer"])

class CustomerRegisterRequest(BaseModel):
    name: constr(min_length=1, max_length=128)
    phone: constr(min_length=6, max_length=32)
    email: Optional[EmailStr] = None
    whatsapp_id: constr(min_length=1, max_length=64)

class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    whatsapp_id: str

    class Config:
        orm_mode = True

class CustomerUpdateRequest(BaseModel):
    name: Optional[constr(min_length=1, max_length=128)] = None
    email: Optional[EmailStr] = None

@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def register_customer(request: CustomerRegisterRequest, db: Session = Depends(get_db)):
    # Check if customer already exists by phone or whatsapp_id
    existing = db.query(Customer).filter(
        (Customer.phone == request.phone) | (Customer.whatsapp_id == request.whatsapp_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this phone or WhatsApp ID already exists."
        )
    customer = Customer(
        name=request.name,
        phone=request.phone,
        email=request.email,
        whatsapp_id=request.whatsapp_id
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/by_phone/{phone}", response_model=CustomerResponse)
def get_customer_by_phone(phone: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.phone == phone).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer

@router.get("/by_whatsapp/{whatsapp_id}", response_model=CustomerResponse)
def get_customer_by_whatsapp(whatsapp_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.whatsapp_id == whatsapp_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    if request.name is not None:
        customer.name = request.name
    if request.email is not None:
        customer.email = request.email
    db.commit()
    db.refresh(customer)
    return customer