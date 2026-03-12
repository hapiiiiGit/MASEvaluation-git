import os
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'logbook.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    dive_entry_id = Column(Integer, ForeignKey('dive_entries.id'), nullable=False)
    file_path = Column(String(256), nullable=False)
    thumbnail_path = Column(String(256), nullable=True)
    uploaded_to_cloud = Column(String(64), nullable=True)  # e.g., 'gdrive', 'dropbox', 's3'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to DiveEntry (optional, for ORM navigation)
    dive_entry = relationship("DiveEntry", backref="photos")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dive_entry_id": self.dive_entry_id,
            "file_path": self.file_path,
            "thumbnail_path": self.thumbnail_path,
            "uploaded_to_cloud": self.uploaded_to_cloud,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class PhotoModel:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def add_photo(self, dive_entry_id: int, file_path: str, thumbnail_path: Optional[str] = None,
                  uploaded_to_cloud: Optional[str] = None) -> Photo:
        photo = Photo(
            dive_entry_id=dive_entry_id,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            uploaded_to_cloud=uploaded_to_cloud
        )
        self.session.add(photo)
        self.session.commit()
        return photo

    def get_photo(self, photo_id: int) -> Optional[Photo]:
        return self.session.query(Photo).filter_by(id=photo_id).first()

    def list_photos_for_entry(self, dive_entry_id: int) -> list:
        return self.session.query(Photo).filter_by(dive_entry_id=dive_entry_id).all()

    def update_photo(self, photo_id: int, **kwargs) -> Optional[Photo]:
        photo = self.get_photo(photo_id)
        if not photo:
            return None
        for key, value in kwargs.items():
            if hasattr(photo, key):
                setattr(photo, key, value)
        self.session.commit()
        return photo

    def delete_photo(self, photo_id: int) -> bool:
        photo = self.get_photo(photo_id)
        if not photo:
            return False
        self.session.delete(photo)
        self.session.commit()
        return True

    def close(self):
        self.session.close()