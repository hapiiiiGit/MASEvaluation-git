from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from models import User, APIKey, Session as UserSession
from schemas import LoginResponse, LogoutResponse, APIKeyResponse, UserRead
from utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    get_password_hash,
    generate_api_key,
)
from services.session_service import create_session, terminate_session
from services.mstock_client import mstock_login, mstock_logout
from utils.logger import logger

SESSION_EXPIRE_MINUTES = 60  # Session expiry time

def login_user(db: Session, username: str, password: str) -> LoginResponse:
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        logger.warning(f"Login failed: User '{username}' not found or inactive.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Login failed: Incorrect password for user '{username}'.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    # Authenticate with mStock Type A User API
    mstock_resp = mstock_login(username, password)
    if not mstock_resp.get("success"):
        logger.error(f"mStock login failed for user '{username}': {mstock_resp.get('error')}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="mStock authentication failed.")

    # Create session
    session = create_session(db, user.id)
    logger.info(f"User '{username}' logged in successfully. Session token: {session.token}")

    user_data = UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    return LoginResponse(
        session_token=session.token,
        expires_at=session.expires_at,
        user=user_data,
    )

def logout_user(db: Session, session_token: str) -> LogoutResponse:
    # Find session
    session = db.query(UserSession).filter(UserSession.token == session_token, UserSession.is_active == True).first()
    if not session:
        logger.warning(f"Logout failed: Invalid or expired session token '{session_token}'.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token.")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        logger.error(f"Logout failed: User for session token '{session_token}' not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found for session.")

    # Logout from mStock
    mstock_resp = mstock_logout(session_token)
    if not mstock_resp.get("success"):
        logger.error(f"mStock logout failed for user '{user.username}': {mstock_resp.get('error')}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="mStock logout failed.")

    # Terminate session
    terminate_session(db, session_token)
    logger.info(f"User '{user.username}' logged out successfully. Session token terminated.")

    return LogoutResponse(success=True, message="Logout successful.")

def generate_api_key_for_user(db: Session, user_id: int) -> APIKeyResponse:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        logger.warning(f"API key generation failed: User ID '{user_id}' not found or inactive.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Generate new API key
    new_key = generate_api_key()
    api_key = APIKey(
        user_id=user.id,
        key=new_key,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    logger.info(f"API key generated for user '{user.username}': {api_key.key}")

    return APIKeyResponse(api_key=api_key.key)