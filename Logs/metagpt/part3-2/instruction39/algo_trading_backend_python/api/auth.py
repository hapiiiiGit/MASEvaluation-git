from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from schemas import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    APIKeyResponse,
    SessionStatusResponse,
    ErrorResponse,
)
from utils.security import get_db, verify_password, create_access_token
from services.auth_service import (
    login_user,
    logout_user,
    generate_api_key_for_user,
)
from services.session_service import (
    get_session_status,
)
from utils.error_handlers import handle_auth_error

router = APIRouter()

@router.post("/login", response_model=LoginResponse, responses={401: {"model": ErrorResponse}})
def login(request: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """
    User login endpoint. Authenticates user and returns session token.
    """
    try:
        login_result = login_user(db, request.username, request.password)
        return login_result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_auth_error(e)

@router.post("/logout", response_model=LogoutResponse, responses={401: {"model": ErrorResponse}})
def logout(request: LogoutRequest, db: Session = Depends(get_db)) -> Any:
    """
    User logout endpoint. Terminates session and logs out from mStock.
    """
    try:
        result = logout_user(db, request.session_token)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_auth_error(e)

@router.get("/session", response_model=SessionStatusResponse, responses={401: {"model": ErrorResponse}})
def session_status(token: str, db: Session = Depends(get_db)) -> Any:
    """
    Session status endpoint. Validates session token and returns status.
    """
    try:
        status_result = get_session_status(db, token)
        return status_result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_auth_error(e)

@router.post("/apikey", response_model=APIKeyResponse, responses={401: {"model": ErrorResponse}})
def generate_api_key(user_id: int, db: Session = Depends(get_db)) -> Any:
    """
    API key generation endpoint. Generates a new API key for the user.
    """
    try:
        api_key_result = generate_api_key_for_user(db, user_id)
        return api_key_result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_auth_error(e)