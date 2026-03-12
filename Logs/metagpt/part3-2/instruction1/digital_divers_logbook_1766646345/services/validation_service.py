import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.signature import SignatureModel
from models.logbook import Logbook
from models.user import UserModel

class ValidationService:
    """
    Handles digital signing, instructor approval, validation status management, and audit trails
    for logbook entries. Integrates with signature and logbook models.
    """

    def __init__(self, config):
        self.config = config
        self.signature_model = SignatureModel()
        self.logbook = Logbook(config)
        self.user_model = UserModel()

    def sign_entry(self, signature_pad, entry_id: Optional[int] = None, signer_user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Capture signature from signature_pad, save it, and associate with the logbook entry.
        Returns the signature record as dict.
        """
        if entry_id is None:
            entry_id = getattr(signature_pad, 'entry_id', None)
        if signer_user_id is None:
            signer_user_id = self.config.get_current_user_id()
        if not entry_id or not signer_user_id:
            return None

        # Save signature image to file
        signature_img = signature_pad.get_signature()  # Should return PIL Image or bytes
        signature_dir = os.path.join(os.path.dirname(__file__), '..', 'signatures')
        os.makedirs(signature_dir, exist_ok=True)
        signature_path = os.path.join(signature_dir, f'signature_{entry_id}_{signer_user_id}_{int(datetime.utcnow().timestamp())}.png')
        if hasattr(signature_img, 'save'):
            signature_img.save(signature_path)
        elif isinstance(signature_img, bytes):
            with open(signature_path, 'wb') as f:
                f.write(signature_img)
        else:
            # If it's a file path, just use it
            signature_path = signature_img

        # Add signature record
        signature = self.signature_model.add_signature(
            dive_entry_id=entry_id,
            signer_user_id=signer_user_id,
            signature_path=signature_path,
            signature_type='digital',
            validation_status='Validated'
        )

        # Update logbook entry validation status
        self.logbook.update_entry(entry_id, signature_path=signature_path, validation_status='Validated')

        return signature.to_dict()

    def get_status(self, entry_id: Optional[int]) -> str:
        """
        Returns the validation status for a given logbook entry.
        """
        if not entry_id:
            return "Pending"
        entry = self.logbook.get_entry(entry_id)
        if entry:
            return entry.validation_status
        return "Pending"

    def approve_entry(self, entry_id: int, instructor_user_id: int) -> bool:
        """
        Instructor approves the logbook entry. Updates validation status and audit trail.
        """
        entry = self.logbook.get_entry(entry_id)
        if not entry:
            return False
        self.logbook.update_entry(entry_id, validation_status='Validated')
        # Add audit trail via signature
        self.signature_model.add_signature(
            dive_entry_id=entry_id,
            signer_user_id=instructor_user_id,
            signature_path='',
            signature_type='digital',
            validation_status='Validated'
        )
        return True

    def reject_entry(self, entry_id: int, instructor_user_id: int, reason: str = "") -> bool:
        """
        Instructor rejects the logbook entry. Updates validation status and audit trail.
        """
        entry = self.logbook.get_entry(entry_id)
        if not entry:
            return False
        self.logbook.update_entry(entry_id, validation_status='Rejected')
        # Add audit trail via signature
        self.signature_model.add_signature(
            dive_entry_id=entry_id,
            signer_user_id=instructor_user_id,
            signature_path='',
            signature_type='digital',
            validation_status='Rejected'
        )
        # Optionally, log the reason somewhere (not in schema)
        return True

    def get_audit_trail(self, entry_id: int) -> List[Dict[str, Any]]:
        """
        Returns a list of signature/audit records for the given entry.
        """
        signatures = self.signature_model.list_signatures_for_entry(entry_id)
        return [sig.to_dict() for sig in signatures]

    def close(self):
        self.signature_model.close()
        self.logbook.close()
        self.user_model.close()