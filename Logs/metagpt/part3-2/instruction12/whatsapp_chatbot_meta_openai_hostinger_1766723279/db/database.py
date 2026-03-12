from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
from .models import Base
import os

from fastapi import Depends
from typing import Generator

def get_database_url():
    # Prefer environment variable DATABASE_URL, fallback to .env or default
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")

DATABASE_URL = get_database_url()

# For production, use NullPool for SQLite, otherwise default pool
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=NullPool
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator:
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()