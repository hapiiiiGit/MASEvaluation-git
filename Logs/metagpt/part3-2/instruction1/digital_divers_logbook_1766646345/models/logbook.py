import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'logbook.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class DiveEntry(Base):
    __tablename__ = 'dive_entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(128), nullable=False)
    depth = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)
    buddy = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    photo_path = Column(String(256), nullable=True)
    signature_path = Column(String(256), nullable=True)
    validation_status = Column(String(32), default='Pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "location": self.location,
            "depth": self.depth,
            "duration": self.duration,
            "buddy": self.buddy,
            "notes": self.notes,
            "photo_path": self.photo_path,
            "signature_path": self.signature_path,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class Logbook:
    def __init__(self, config):
        self.config = config
        Base.metadata.create_all(engine)
        self.session = Session()

    def add_entry(self, user_id: int, date: str, location: str, depth: float, duration: int,
                  buddy: Optional[str], notes: Optional[str], photo_path: Optional[str],
                  signature_path: Optional[str], validation_status: str = 'Pending') -> DiveEntry:
        entry = DiveEntry(
            user_id=user_id,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            location=location,
            depth=depth,
            duration=duration,
            buddy=buddy,
            notes=notes,
            photo_path=photo_path,
            signature_path=signature_path,
            validation_status=validation_status
        )
        self.session.add(entry)
        self.session.commit()
        return entry

    def get_entry(self, entry_id: int) -> Optional[DiveEntry]:
        return self.session.query(DiveEntry).filter_by(id=entry_id).first()

    def update_entry(self, entry_id: int, **kwargs) -> Optional[DiveEntry]:
        entry = self.get_entry(entry_id)
        if not entry:
            return None
        for key, value in kwargs.items():
            if hasattr(entry, key):
                if key == 'date' and isinstance(value, str):
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                setattr(entry, key, value)
        self.session.commit()
        return entry

    def delete_entry(self, entry_id: int) -> bool:
        entry = self.get_entry(entry_id)
        if not entry:
            return False
        self.session.delete(entry)
        self.session.commit()
        return True

    def list_entries(self, user_id: int) -> List[DiveEntry]:
        return self.session.query(DiveEntry).filter_by(user_id=user_id).order_by(DiveEntry.date.desc()).all()

    def get_total_dives(self, user_id: Optional[int] = None) -> int:
        query = self.session.query(DiveEntry)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.count()

    def get_recent_location(self, user_id: Optional[int] = None) -> str:
        query = self.session.query(DiveEntry)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        entry = query.order_by(DiveEntry.date.desc()).first()
        return entry.location if entry else ""

    def save_entry(self, entry_id: Optional[int], date: str, location: str, depth: str, duration: str,
                   buddy: str, notes: str, photo_path: str, signature_path: str) -> DiveEntry:
        # Used by UI to save or update an entry
        user_id = self.config.get_current_user_id()
        depth_val = float(depth) if depth else 0.0
        duration_val = int(duration) if duration else 0
        if entry_id:
            entry = self.update_entry(
                entry_id,
                date=date,
                location=location,
                depth=depth_val,
                duration=duration_val,
                buddy=buddy,
                notes=notes,
                photo_path=photo_path,
                signature_path=signature_path
            )
        else:
            entry = self.add_entry(
                user_id=user_id,
                date=date,
                location=location,
                depth=depth_val,
                duration=duration_val,
                buddy=buddy,
                notes=notes,
                photo_path=photo_path,
                signature_path=signature_path
            )
        return entry

    def get_recent_activity(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        entries = self.session.query(DiveEntry).filter_by(user_id=user_id).order_by(DiveEntry.date.desc()).limit(limit).all()
        return [entry.to_dict() for entry in entries]

    def close(self):
        self.session.close()