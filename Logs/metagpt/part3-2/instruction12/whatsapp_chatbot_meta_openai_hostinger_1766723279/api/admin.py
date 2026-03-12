from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from typing import Optional
import os

from db.database import get_db
from db.models import Admin
from utils.auth import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminCreateRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=128)

class AdminLoginRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=128)

class AdminResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/create", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_admin(request: AdminCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == request.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this username already exists."
        )
    password_hash = get_password_hash(request.password)
    admin = Admin(username=request.username, password_hash=password_hash)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/login", response_model=TokenResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )
    # Generate JWT token
    access_token = create_access_token(data={"sub": admin.username, "admin_id": admin.id})
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=AdminResponse)
def get_admin_me(current_admin: Admin = Depends(lambda: get_current_admin())):
    return current_admin

# Dependency to get current admin from JWT token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        admin_id: int = payload.get("admin_id")
        if username is None or admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.username == username).first()
    if admin is None:
        raise credentials_exception
    return admin