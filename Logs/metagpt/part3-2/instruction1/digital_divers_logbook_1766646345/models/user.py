import os
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'logbook.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=True)  # For local auth
    oauth_provider = Column(String(32), nullable=True)  # e.g., 'google', 'dropbox'
    oauth_id = Column(String(128), nullable=True)       # Provider user id
    is_active = Column(Boolean, default=True)
    is_instructor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_instructor": self.is_instructor,
            "oauth_provider": self.oauth_provider,
            "oauth_id": self.oauth_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class UserModel:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def create_user(self, username: str, email: str, password_hash: Optional[str] = None,
                   oauth_provider: Optional[str] = None, oauth_id: Optional[str] = None,
                   is_instructor: bool = False) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_instructor=is_instructor
        )
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def get_user_by_oauth(self, provider: str, oauth_id: str) -> Optional[User]:
        return self.session.query(User).filter_by(oauth_provider=provider, oauth_id=oauth_id).first()

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.session.commit()
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True

    def authenticate_local(self, username_or_email: str, password_hash: str) -> Optional[User]:
        user = self.session.query(User).filter(
            ((User.username == username_or_email) | (User.email == username_or_email)),
            User.password_hash == password_hash,
            User.is_active == True
        ).first()
        return user

    def authenticate_oauth(self, provider: str, oauth_id: str) -> Optional[User]:
        user = self.get_user_by_oauth(provider, oauth_id)
        if user and user.is_active:
            return user
        return None

    def list_users(self) -> list:
        return self.session.query(User).all()

    def close(self):
        self.session.close()