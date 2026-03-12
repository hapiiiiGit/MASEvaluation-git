from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.survey import router as survey_router
from backend.api.response import router as response_router
from backend.api.analytics import router as analytics_router
from backend.api.report import router as report_router
from backend.api.auth import router as auth_router

from backend.database import engine, Base
from backend.config import settings

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Survey Analytics MVP",
    description="MVP web application for survey capture, analytics, and reporting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(survey_router, prefix="/api/survey", tags=["Survey"])
app.include_router(response_router, prefix="/api/survey", tags=["Response"])
app.include_router(analytics_router, prefix="/api/survey", tags=["Analytics"])
app.include_router(report_router, prefix="/api/survey", tags=["Report"])

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}