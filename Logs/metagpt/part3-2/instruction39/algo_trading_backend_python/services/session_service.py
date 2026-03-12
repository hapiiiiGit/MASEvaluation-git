from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import Session as UserSession, User
from schemas import SessionRead, SessionStatusResponse
from utils.security import create_access_token, decode_access_token
from utils.logger import logger

SESSION_EXPIRE_MINUTES = 60  # Session expiry time in minutes

def create_session(db: Session, user_id: int) -> UserSession:
    """
    Create a new session for the user, generate a JWT token, and store it in the database.
    """
    expires_at = datetime.utcnow() + timedelta(minutes=SESSION_EXPIRE_MINUTES)
    token = create_access_token(data={"user_id": user_id}, expires_delta=timedelta(minutes=SESSION_EXPIRE_MINUTES))

    # Deactivate any previous active sessions for this user
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).update({UserSession.is_active: False})

    session = UserSession(
        user_id=user_id,
        token=token,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Session created for user_id={user_id}, session_id={session.id}")
    return session

def validate_session(db: Session, token: str) -> bool:
    """
    Validate the session token. Returns True if valid and active, False otherwise.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            logger.warning("Session validation failed: user_id missing in token payload.")
            return False
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        if session:
            logger.info(f"Session token validated for user_id={user_id}")
            return True
        logger.warning(f"Session validation failed: No active session for token.")
        return False
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return False

def get_session_status(db: Session, token: str) -> SessionStatusResponse:
    """
    Return the status of the session token.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            logger.warning("Session status: user_id missing in token payload.")
            return SessionStatusResponse(is_active=False)
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).first()
        if session and session.expires_at > datetime.utcnow():
            return SessionStatusResponse(is_active=True, expires_at=session.expires_at)
        return SessionStatusResponse(is_active=False)
    except Exception as e:
        logger.error(f"Session status error: {e}")
        return SessionStatusResponse(is_active=False)

def terminate_session(db: Session, token: str) -> bool:
    """
    Terminate (deactivate) the session associated with the given token.
    """
    session = db.query(UserSession).filter(
        UserSession.token == token,
        UserSession.is_active == True
    ).first()
    if not session:
        logger.warning(f"Terminate session failed: No active session for token.")
        return False
    session.is_active = False
    db.commit()
    logger.info(f"Session terminated: session_id={session.id}, user_id={session.user_id}")
    return True