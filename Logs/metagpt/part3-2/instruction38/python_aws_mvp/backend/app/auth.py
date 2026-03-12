from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timedelta

from .models import User
from .config import get_settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT settings
settings = get_settings()
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# In-memory user store for MVP (replace with DB in production)
fake_users_db: Dict[str, User] = {}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str) -> Optional[UserInDB]:
    user = fake_users_db.get(email)
    if user:
        return UserInDB(**user.dict(), hashed_password=user.hashed_password)
    return None

def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = get_user(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# AuthManager class as per system design
class AuthManager:
    @staticmethod
    def login(email: str, password: str) -> dict:
        user = authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.user_id})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def register(email: str, password: str) -> dict:
        if email in fake_users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user_id = f"user_{len(fake_users_db)+1}"
        hashed_password = get_password_hash(password)
        user = UserInDB(
            user_id=user_id,
            email=email,
            roles=["user"],
            hashed_password=hashed_password
        )
        fake_users_db[email] = user
        access_token = create_access_token(data={"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def verify_token(token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return False
            return True
        except JWTError:
            return False

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Find user by user_id
    for user in fake_users_db.values():
        if user.user_id == user_id:
            return user
    raise credentials_exception

# FastAPI router for authentication
auth_router = APIRouter()

@auth_router.post("/login", response_model=Token, summary="Login and get JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return AuthManager.login(form_data.username, form_data.password)

class RegisterRequest(BaseModel):
    email: str
    password: str

@auth_router.post("/register", response_model=Token, summary="Register new user")
async def register(request: RegisterRequest):
    return AuthManager.register(request.email, request.password)

@auth_router.get("/me", response_model=User, summary="Get current user info")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

def get_auth_router():
    return auth_router