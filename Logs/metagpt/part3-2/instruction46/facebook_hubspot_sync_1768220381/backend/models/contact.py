from datetime import date
from typing import Optional, Dict, Any

from backend.models.ad_metric import AdMetric

class Contact:
    def __init__(
        self,
        id: Optional[int],
        email: str,
        name: str,
        facebook_id: str
    ):
        self.id = id
        self.email = email
        self.name = name
        self.facebook_id = facebook_id

    def update_from_metric(self, metric: AdMetric):
        """
        Update contact fields based on ad metric.
        For demonstration, we could update the name or add custom fields.
        """
        # Example: append campaign info to name
        if metric.campaign_id:
            self.name = f"{self.name} (Campaign {metric.campaign_id})"

    @classmethod
    def from_hubspot(cls, data: Dict[str, Any]):
        """
        Create a Contact instance from HubSpot API response.
        """
        properties = data.get("properties", {})
        return cls(
            id=int(data.get("id")) if data.get("id") is not None else None,
            email=properties.get("email", ""),
            name=properties.get("firstname", ""),
            facebook_id=properties.get("facebook_id", "")
        )

    def to_hubspot(self) -> Dict[str, Any]:
        """
        Convert Contact instance to HubSpot API format for update/create.
        """
        return {
            "email": self.email,
            "firstname": self.name,
            "facebook_id": self.facebook_id
        }