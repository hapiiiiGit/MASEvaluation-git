from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.logger import setup_logger
from utils.error_handlers import register_error_handlers

from api.auth import router as auth_router
from api.funds import router as funds_router

import logging

# Initialize logger
setup_logger()

app = FastAPI(
    title="Algo Trading Backend (mStock Type A User APIs)",
    description="Backend for user authentication, session management, fund details, and API key management.",
    version="1.0.0"
)

# CORS settings (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to trusted domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(funds_router, prefix="/api/funds", tags=["funds"])

# Register error handlers
register_error_handlers(app)

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    return {"message": "Welcome to the Algo Trading Backend powered by mStock Type A User APIs."}

# Run with: uvicorn main:app --reload