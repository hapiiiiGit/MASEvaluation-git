from donors.models import Donor
from django.utils import timezone
from datetime import timedelta

def get_report_data(report_type, params):
    """
    Generate report data based on report_type and parameters.
    Supports: donation, activity, inventory, custom.
    Returns a dictionary suitable for storing in Report.data.
    """
    if report_type == 'donation':
        # Example: Count donors by blood type and recent donations
        blood_type = params.get('blood_type')
        days = int(params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        donors_qs = Donor.objects.filter(is_active=True)
        if blood_type:
            donors_qs = donors_qs.filter(blood_type=blood_type)
        recent_donors = donors_qs.filter(last_donation__gte=since_date)
        data = {
            "report_type": "Donation",
            "blood_type": blood_type if blood_type else "All",
            "since_date": since_date.strftime('%Y-%m-%d'),
            "total_donors": donors_qs.count(),
            "recent_donors": recent_donors.count(),
            "donors": [
                {
                    "id": donor.id,
                    "name": donor.name,
                    "blood_type": donor.blood_type,
                    "location": donor.location,
                    "last_donation": donor.last_donation.strftime('%Y-%m-%d %H:%M') if donor.last_donation else None,
                }
                for donor in recent_donors
            ]
        }
        return data

    elif report_type == 'activity':
        # Example: Donor activity in a given period
        days = int(params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        donors = Donor.objects.filter(is_active=True, last_donation__gte=since_date)
        data = {
            "report_type": "Donor Activity",
            "since_date": since_date.strftime('%Y-%m-%d'),
            "active_donors": donors.count(),
            "donors": [
                {
                    "id": donor.id,
                    "name": donor.name,
                    "blood_type": donor.blood_type,
                    "location": donor.location,
                    "last_donation": donor.last_donation.strftime('%Y-%m-%d %H:%M') if donor.last_donation else None,
                }
                for donor in donors
            ]
        }
        return data

    elif report_type == 'inventory':
        # Example: Inventory by blood type
        blood_types = [bt[0] for bt in Donor.BLOOD_TYPE_CHOICES]
        inventory = {}
        for bt in blood_types:
            count = Donor.objects.filter(blood_type=bt, is_active=True).count()
            inventory[bt] = count
        data = {
            "report_type": "Inventory",
            "inventory": inventory,
            "total_donors": Donor.objects.filter(is_active=True).count(),
        }
        return data

    elif report_type == 'custom':
        # Custom report: echo params and donor count
        donors = Donor.objects.filter(is_active=True)
        data = {
            "report_type": "Custom",
            "params": params,
            "total_donors": donors.count(),
        }
        return data

    else:
        # Unknown report type
        return {
            "error": "Unknown report type",
            "params": params
        }