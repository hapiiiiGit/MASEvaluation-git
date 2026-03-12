from fastapi import FastAPI, Request, Form, Depends, status, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional

import os

from db.database import get_db
from db.models import Admin, Booking, BookingStatus, Notification, NotificationStatus, NotificationChannel, Customer
from utils.auth import verify_password, get_password_hash

# Path setup for templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("DASHBOARD_SECRET_KEY", "dashboardsecret"))

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Optionally mount static files if you have CSS/JS
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Helper functions ---

def get_admin_from_session(request: Request, db: Session) -> Optional[Admin]:
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return None
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    return admin

def require_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    admin = get_admin_from_session(request, db)
    if not admin:
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": "/dashboard/login"})
    return admin

# --- Routes ---

@app.get("/dashboard/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/dashboard/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["admin_id"] = admin.id
    return RedirectResponse(url="/dashboard/bookings", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard/bookings", response_class=HTMLResponse)
def bookings_list(
    request: Request,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    admin = get_admin_from_session(request, db)
    if not admin:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)
    query = db.query(Booking).join(Customer)
    if status_filter:
        try:
            status_enum = BookingStatus(status_filter)
            query = query.filter(Booking.status == status_enum)
        except ValueError:
            pass
    bookings = query.order_by(Booking.created_at.desc()).all()
    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "admin": admin,
        "bookings": bookings,
        "BookingStatus": BookingStatus,
        "Customer": Customer,
        "status_filter": status_filter or ""
    })

@app.get("/dashboard/bookings/{booking_id}", response_class=HTMLResponse)
def booking_detail(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    admin = get_admin_from_session(request, db)
    if not admin:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return HTMLResponse("Booking not found", status_code=404)
    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
    return templates.TemplateResponse("bookings.html", {
        "request": request,
        "admin": admin,
        "bookings": [booking],
        "BookingStatus": BookingStatus,
        "Customer": Customer,
        "customer": customer,
        "detail_view": True
    })

@app.post("/dashboard/bookings/{booking_id}/status")
def update_booking_status(
    request: Request,
    booking_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = get_admin_from_session(request, db)
    if not admin:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return HTMLResponse("Booking not found", status_code=404)
    try:
        booking.status = BookingStatus(status)
        db.commit()
    except Exception:
        db.rollback()
        return HTMLResponse("Invalid status", status_code=400)
    return RedirectResponse(url="/dashboard/bookings", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard/notifications", response_class=HTMLResponse)
def notifications_list(
    request: Request,
    db: Session = Depends(get_db)
):
    admin = get_admin_from_session(request, db)
    if not admin:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(100).all()
    customers = {c.id: c for c in db.query(Customer).all()}
    return templates.TemplateResponse("notifications.html", {
        "request": request,
        "admin": admin,
        "notifications": notifications,
        "NotificationStatus": NotificationStatus,
        "NotificationChannel": NotificationChannel,
        "customers": customers
    })

@app.post("/dashboard/notifications/send")
def send_notification(
    request: Request,
    recipient_id: int = Form(...),
    channel: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = get_admin_from_session(request, db)
    if not admin:
        return RedirectResponse(url="/dashboard/login", status_code=status.HTTP_302_FOUND)
    customer = db.query(Customer).filter(Customer.id == recipient_id).first()
    if not customer:
        return HTMLResponse("Customer not found", status_code=404)
    notif_channel = NotificationChannel(channel)
    notif_status = NotificationStatus.PENDING
    # For demo, mark as SENT (integration handled by API)
    notif_status = NotificationStatus.SENT
    notification = Notification(
        recipient_id=recipient_id,
        channel=notif_channel,
        message=message,
        status=notif_status
    )
    db.add(notification)
    db.commit()
    return RedirectResponse(url="/dashboard/notifications", status_code=status.HTTP_302_FOUND)