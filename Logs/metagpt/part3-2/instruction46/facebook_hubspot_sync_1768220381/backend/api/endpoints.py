from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from datetime import date

from backend.models.ad_metric import AdMetric
from backend.models.contact import Contact
from backend.models.deal import Deal
from backend.sync.scheduler import run_sync, get_sync_status, adjust_interval
from backend.sync.mapping import (
    fetch_facebook_ad_metrics,
    map_metrics_to_contacts,
    map_metrics_to_deals,
)
from backend.utils.logger import get_logger

import os

router = APIRouter()
logger = get_logger(__name__)

# Environment variables for tokens and ad account
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
FACEBOOK_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")

@router.get("/metrics", response_model=List[Dict[str, Any]])
async def get_metrics(
    since: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    until: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign_id"),
    ad_id: Optional[str] = Query(None, description="Filter by ad_id"),
):
    """
    Get Facebook ad metrics, optionally filtered by date range, campaign_id, or ad_id.
    """
    if not FACEBOOK_AD_ACCOUNT_ID or not FACEBOOK_ACCESS_TOKEN:
        logger.error("Missing Facebook credentials for metrics endpoint.")
        raise HTTPException(status_code=500, detail="Facebook credentials not configured.")

    # Default to last 7 days if not provided
    today = date.today()
    since_str = (since or (today.replace(day=max(1, today.day - 7)))).isoformat()
    until_str = (until or today).isoformat()

    metrics = fetch_facebook_ad_metrics(
        ad_account_id=FACEBOOK_AD_ACCOUNT_ID,
        access_token=FACEBOOK_ACCESS_TOKEN,
        since=since_str,
        until=until_str,
    )

    # Filter by campaign_id/ad_id if provided
    if campaign_id:
        metrics = [m for m in metrics if m.campaign_id == campaign_id]
    if ad_id:
        metrics = [m for m in metrics if m.ad_id == ad_id]

    # Return as dicts for frontend
    return [
        {
            "campaign_id": m.campaign_id,
            "ad_id": m.ad_id,
            "date": m.date.isoformat() if m.date else None,
            "clicks": m.clicks,
            "impressions": m.impressions,
            "spend": m.spend,
            "conversions": m.conversions,
        }
        for m in metrics
    ]

@router.get("/contacts", response_model=List[Dict[str, Any]])
async def get_contacts(
    facebook_id: Optional[str] = Query(None, description="Filter by Facebook ID"),
    email: Optional[str] = Query(None, description="Filter by email"),
):
    """
    Get HubSpot contacts, optionally filtered by facebook_id or email.
    """
    # For demo, fetch metrics and map to contacts
    if not FACEBOOK_AD_ACCOUNT_ID or not FACEBOOK_ACCESS_TOKEN:
        logger.error("Missing Facebook credentials for contacts endpoint.")
        raise HTTPException(status_code=500, detail="Facebook credentials not configured.")

    today = date.today()
    since_str = (today.replace(day=max(1, today.day - 7))).isoformat()
    until_str = today.isoformat()

    metrics = fetch_facebook_ad_metrics(
        ad_account_id=FACEBOOK_AD_ACCOUNT_ID,
        access_token=FACEBOOK_ACCESS_TOKEN,
        since=since_str,
        until=until_str,
    )
    contacts = map_metrics_to_contacts(metrics)

    # Filter contacts
    if facebook_id:
        contacts = [c for c in contacts if c.facebook_id == facebook_id]
    if email:
        contacts = [c for c in contacts if c.email == email]

    return [
        {
            "id": c.id,
            "email": c.email,
            "name": c.name,
            "facebook_id": c.facebook_id,
        }
        for c in contacts
    ]

@router.get("/deals", response_model=List[Dict[str, Any]])
async def get_deals(
    contact_id: Optional[int] = Query(None, description="Filter by contact_id"),
    stage: Optional[str] = Query(None, description="Filter by deal stage"),
):
    """
    Get HubSpot deals, optionally filtered by contact_id or stage.
    """
    # For demo, fetch metrics and map to deals
    if not FACEBOOK_AD_ACCOUNT_ID or not FACEBOOK_ACCESS_TOKEN:
        logger.error("Missing Facebook credentials for deals endpoint.")
        raise HTTPException(status_code=500, detail="Facebook credentials not configured.")

    today = date.today()
    since_str = (today.replace(day=max(1, today.day - 7))).isoformat()
    until_str = today.isoformat()

    metrics = fetch_facebook_ad_metrics(
        ad_account_id=FACEBOOK_AD_ACCOUNT_ID,
        access_token=FACEBOOK_ACCESS_TOKEN,
        since=since_str,
        until=until_str,
    )
    deals = map_metrics_to_deals(metrics)

    # Filter deals
    if contact_id is not None:
        deals = [d for d in deals if d.contact_id == contact_id]
    if stage:
        deals = [d for d in deals if d.stage == stage]

    return [
        {
            "id": d.id,
            "contact_id": d.contact_id,
            "amount": d.amount,
            "stage": d.stage,
        }
        for d in deals
    ]

@router.post("/sync/manual")
async def trigger_manual_sync():
    """
    Manually trigger the Facebook-HubSpot sync routine.
    """
    try:
        run_sync()
        return {"status": "success", "message": "Manual sync triggered."}
    except Exception as e:
        logger.error(f"Manual sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Manual sync failed.")

@router.get("/sync/status")
async def get_sync_status_endpoint():
    """
    Get the current status of the sync scheduler.
    """
    status = get_sync_status()
    return status

@router.post("/sync/interval")
async def set_sync_interval(interval_seconds: int):
    """
    Adjust the sync interval for the scheduled sync job.
    """
    if interval_seconds < 60:
        raise HTTPException(status_code=400, detail="Interval must be at least 60 seconds.")
    adjust_interval(interval_seconds)
    return {"status": "success", "interval_seconds": interval_seconds}