from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr, EmailStr
from typing import Optional
import os

from db.database import get_db
from db.models import Notification, NotificationChannel, NotificationStatus, Customer
from api.whatsapp import MetaAPI
from utils.email import EmailSender

router = APIRouter(prefix="/notification", tags=["Notification"])

# Load Meta API credentials from environment variables or .env
META_TOKEN = os.getenv("META_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
META_API_VERSION = os.getenv("META_API_VERSION", "v18.0")
meta_api = MetaAPI(token=META_TOKEN, phone_number_id=META_PHONE_NUMBER_ID, api_version=META_API_VERSION)

# Load Email SMTP config from environment variables or .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
email_sender = EmailSender({
    "host": SMTP_HOST,
    "port": SMTP_PORT,
    "username": SMTP_USER,
    "password": SMTP_PASS
})

class WhatsAppNotificationRequest(BaseModel):
    recipient_id: int
    message: constr(min_length=1, max_length=2048)

class EmailNotificationRequest(BaseModel):
    recipient_id: int
    subject: constr(min_length=1, max_length=256)
    body: constr(min_length=1, max_length=4096)

class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    channel: NotificationChannel
    message: str
    status: NotificationStatus

    class Config:
        orm_mode = True

@router.post("/whatsapp", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_whatsapp_notification(request: WhatsAppNotificationRequest, db: Session = Depends(get_db)):
    # Get recipient customer
    customer = db.query(Customer).filter(Customer.id == request.recipient_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient customer not found.")

    # Send WhatsApp message via MetaAPI
    success = meta_api.send_whatsapp_message(to=customer.whatsapp_id, text=request.message)
    notif_status = NotificationStatus.SENT if success else NotificationStatus.FAILED

    # Store notification in DB
    notification = Notification(
        recipient_id=customer.id,
        channel=NotificationChannel.WHATSAPP,
        message=request.message,
        status=notif_status
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

@router.post("/email", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_email_notification(request: EmailNotificationRequest, db: Session = Depends(get_db)):
    # Get recipient customer
    customer = db.query(Customer).filter(Customer.id == request.recipient_id).first()
    if not customer or not customer.email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient customer with email not found.")

    # Send email via EmailSender
    success = email_sender.send_email(
        to=customer.email,
        subject=request.subject,
        body=request.body
    )
    notif_status = NotificationStatus.SENT if success else NotificationStatus.FAILED

    # Store notification in DB
    notification = Notification(
        recipient_id=customer.id,
        channel=NotificationChannel.EMAIL,
        message=request.body,
        status=notif_status
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

@router.get("/customer/{customer_id}", response_model=list[NotificationResponse])
def list_notifications_for_customer(customer_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.recipient_id == customer_id).order_by(Notification.created_at.desc()).all()
    return notifications