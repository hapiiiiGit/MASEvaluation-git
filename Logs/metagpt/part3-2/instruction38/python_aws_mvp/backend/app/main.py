from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    get_auth_router,
    get_storage_router,
    get_billing_router,
    get_observability_router,
)
from .config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="python_aws_mvp API",
    description="Backend API for python_aws_mvp MVP. Provides authentication, S3 presigned uploads, Stripe metered billing, and observability.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(get_auth_router(), prefix="/auth", tags=["Authentication"])
app.include_router(get_storage_router(), prefix="/storage", tags=["Storage"])
app.include_router(get_billing_router(), prefix="/billing", tags=["Billing"])
app.include_router(get_observability_router(), prefix="/observability", tags=["Observability"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Entry point for running with uvicorn
def run():
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )

if __name__ == "__main__":
    run()