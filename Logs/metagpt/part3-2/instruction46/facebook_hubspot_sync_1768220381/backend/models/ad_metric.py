from datetime import date
from typing import Optional, Dict, Any, List

class AdMetric:
    def __init__(
        self,
        id: Optional[int],
        campaign_id: str,
        ad_id: str,
        date: date,
        clicks: int,
        impressions: int,
        spend: float,
        conversions: int
    ):
        self.id = id
        self.campaign_id = campaign_id
        self.ad_id = ad_id
        self.date = date
        self.clicks = clicks
        self.impressions = impressions
        self.spend = spend
        self.conversions = conversions

    @classmethod
    def from_facebook(cls, data: Dict[str, Any]) -> "AdMetric":
        """
        Create an AdMetric instance from Facebook API response data.
        """
        # Parse conversions from actions list if present
        conversions = 0
        actions = data.get("actions", [])
        for action in actions:
            if action.get("action_type") == "offsite_conversion":
                try:
                    conversions += int(action.get("value", 0))
                except (ValueError, TypeError):
                    conversions += 0

        # Parse date
        date_str = data.get("date_start")
        metric_date = None
        if date_str:
            try:
                metric_date = date.fromisoformat(date_str)
            except Exception:
                metric_date = None

        return cls(
            id=None,  # ID is assigned by DB if needed
            campaign_id=data.get("campaign_id", ""),
            ad_id=data.get("ad_id", ""),
            date=metric_date,
            clicks=int(data.get("clicks", 0)),
            impressions=int(data.get("impressions", 0)),
            spend=float(data.get("spend", 0.0)),
            conversions=conversions
        )

    @classmethod
    def list_from_facebook(cls, data_list: List[Dict[str, Any]]) -> List["AdMetric"]:
        """
        Create a list of AdMetric instances from a list of Facebook API response data.
        """
        return [cls.from_facebook(data) for data in data_list]