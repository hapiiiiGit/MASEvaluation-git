import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from api.whatsapp import router as whatsapp_router
from api.customer import router as customer_router
from api.booking import router as booking_router
from api.notification import router as notification_router
from api.admin import router as admin_router

# Import dashboard FastAPI app
import sys
import pathlib

# Ensure dashboard module is importable
dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")
if dashboard_path not in sys.path:
    sys.path.append(dashboard_path)

from dashboard.app import app as dashboard_app

# Database initialization
from db.database import init_db

# Initialize database tables
init_db()

app = FastAPI(
    title="WhatsApp Chatbot with Meta Cloud API & OpenAI ChatGPT",
    description="A production-ready WhatsApp chatbot with customer registration, booking, admin dashboard, notifications, and AI integration.",
    version="1.0.0"
)

# CORS settings (adjust origins as needed for production)
origins = [
    "*",  # Allow all for development; restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(whatsapp_router)
app.include_router(customer_router)
app.include_router(booking_router)
app.include_router(notification_router)
app.include_router(admin_router)

# Mount the dashboard FastAPI app at /dashboard
app.mount("/dashboard", dashboard_app)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to the WhatsApp Chatbot API. See /docs for API documentation."
    }

# If running directly, use uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)