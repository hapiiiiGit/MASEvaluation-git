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

class Signature(Base):
    __tablename__ = 'signatures'

    id = Column(Integer, primary_key=True)
    dive_entry_id = Column(Integer, ForeignKey('dive_entries.id'), nullable=False)
    signer_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    signature_path = Column(String(256), nullable=False)  # Path to signature image or file
    signature_type = Column(String(32), nullable=False, default='digital')  # 'digital' or 'handwritten'
    signed_at = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String(32), default='Pending')  # 'Pending', 'Validated', 'Rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships for ORM navigation
    dive_entry = relationship("DiveEntry", backref="signatures")
    signer_user = relationship("User", backref="signatures")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dive_entry_id": self.dive_entry_id,
            "signer_user_id": self.signer_user_id,
            "signature_path": self.signature_path,
            "signature_type": self.signature_type,
            "signed_at": self.signed_at.isoformat(),
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class SignatureModel:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def add_signature(self, dive_entry_id: int, signer_user_id: int, signature_path: str,
                      signature_type: str = 'digital', validation_status: str = 'Pending') -> Signature:
        signature = Signature(
            dive_entry_id=dive_entry_id,
            signer_user_id=signer_user_id,
            signature_path=signature_path,
            signature_type=signature_type,
            validation_status=validation_status
        )
        self.session.add(signature)
        self.session.commit()
        return signature

    def get_signature(self, signature_id: int) -> Optional[Signature]:
        return self.session.query(Signature).filter_by(id=signature_id).first()

    def list_signatures_for_entry(self, dive_entry_id: int) -> list:
        return self.session.query(Signature).filter_by(dive_entry_id=dive_entry_id).all()

    def update_signature(self, signature_id: int, **kwargs) -> Optional[Signature]:
        signature = self.get_signature(signature_id)
        if not signature:
            return None
        for key, value in kwargs.items():
            if hasattr(signature, key):
                setattr(signature, key, value)
        self.session.commit()
        return signature

    def delete_signature(self, signature_id: int) -> bool:
        signature = self.get_signature(signature_id)
        if not signature:
            return False
        self.session.delete(signature)
        self.session.commit()
        return True

    def close(self):
        self.session.close()