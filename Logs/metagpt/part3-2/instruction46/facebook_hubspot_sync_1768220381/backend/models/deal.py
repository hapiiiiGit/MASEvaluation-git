from typing import Optional, Dict, Any

from backend.models.ad_metric import AdMetric

class Deal:
    def __init__(
        self,
        id: Optional[int],
        contact_id: Optional[int],
        amount: float,
        stage: str
    ):
        self.id = id
        self.contact_id = contact_id
        self.amount = amount
        self.stage = stage

    def update_from_metric(self, metric: AdMetric):
        """
        Update deal fields based on ad metric.
        For demonstration, we update amount based on spend and conversions.
        """
        # Example: add spend and conversion value to amount
        self.amount += metric.spend + (metric.conversions * 10)  # Assume $10 per conversion

        # Optionally, update stage based on conversions
        if metric.conversions > 0:
            self.stage = "qualifiedtobuy"

    @classmethod
    def from_hubspot(cls, data: Dict[str, Any]):
        """
        Create a Deal instance from HubSpot API response.
        """
        properties = data.get("properties", {})
        return cls(
            id=int(data.get("id")) if data.get("id") is not None else None,
            contact_id=int(properties.get("contact_id")) if properties.get("contact_id") is not None else None,
            amount=float(properties.get("amount", 0.0)),
            stage=properties.get("stage", "")
        )

    def to_hubspot(self) -> Dict[str, Any]:
        """
        Convert Deal instance to HubSpot API format for update/create.
        """
        return {
            "amount": self.amount,
            "stage": self.stage,
            "contact_id": str(self.contact_id) if self.contact_id is not None else None
        }