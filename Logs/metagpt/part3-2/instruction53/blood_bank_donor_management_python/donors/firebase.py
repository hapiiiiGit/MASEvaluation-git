import firebase_admin
from firebase_admin import credentials, db
from django.conf import settings
from .models import Donor
from datetime import datetime

class FirebaseService:
    def __init__(self):
        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.FIREBASE_DATABASE_URL
            })
        self.ref = db.reference('donors')

    def _dict_to_donor(self, donor_id, data):
        """
        Convert Firebase dict to Donor instance (not saved to DB).
        """
        return Donor(
            id=donor_id,
            name=data.get('name', ''),
            blood_type=data.get('blood_type', ''),
            location=data.get('location', ''),
            contact_info=data.get('contact_info', ''),
            last_donation=self._parse_datetime(data.get('last_donation')),
            is_active=data.get('is_active', True)
        )

    def _donor_to_dict(self, donor):
        """
        Convert Donor instance to dict for Firebase.
        """
        return {
            'name': donor.name,
            'blood_type': donor.blood_type,
            'location': donor.location,
            'contact_info': donor.contact_info,
            'last_donation': donor.last_donation.isoformat() if donor.last_donation else '',
            'is_active': donor.is_active
        }

    def _parse_datetime(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def get_donors(self):
        """
        Returns a list of Donor instances from Firebase.
        """
        donors_data = self.ref.get()
        donors = []
        if donors_data:
            for donor_id, data in donors_data.items():
                donors.append(self._dict_to_donor(donor_id, data))
        return donors

    def get_donor(self, donor_id):
        """
        Returns a single Donor instance by donor_id from Firebase.
        """
        data = self.ref.child(donor_id).get()
        if data:
            return self._dict_to_donor(donor_id, data)
        return None

    def add_donor(self, donor):
        """
        Adds a new donor to Firebase.
        """
        donor_dict = self._donor_to_dict(donor)
        self.ref.child(donor.id).set(donor_dict)

    def update_donor(self, donor):
        """
        Updates an existing donor in Firebase.
        """
        donor_dict = self._donor_to_dict(donor)
        self.ref.child(donor.id).update(donor_dict)

    def delete_donor(self, donor_id):
        """
        Deletes a donor from Firebase.
        """
        self.ref.child(donor_id).delete()