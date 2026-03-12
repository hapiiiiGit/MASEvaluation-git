import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.models.ad_metric import AdMetric
from backend.models.contact import Contact
from backend.models.deal import Deal
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Environment variables for tokens (in production, use secure storage)
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

# Facebook API endpoints
FACEBOOK_AD_INSIGHTS_URL = "https://graph.facebook.com/v18.0/act_{ad_account_id}/insights"

# HubSpot API endpoints
HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_DEALS_URL = "https://api.hubapi.com/crm/v3/objects/deals"

def fetch_facebook_ad_metrics(
    ad_account_id: str,
    access_token: str,
    since: str,
    until: str
) -> List[AdMetric]:
    """
    Fetch ad metrics from Facebook Marketing API for a given account and date range.
    """
    params = {
        "level": "ad",
        "fields": "ad_id,campaign_id,date_start,clicks,impressions,spend,actions",
        "time_range": {"since": since, "until": until},
        "access_token": access_token
    }
    url = FACEBOOK_AD_INSIGHTS_URL.format(ad_account_id=ad_account_id)
    response = requests.get(url, params=params)
    if response.status_code != 200:
        logger.error(f"Failed to fetch Facebook ad metrics: {response.text}")
        raise Exception("Failed to fetch Facebook ad metrics")
    data = response.json().get("data", [])
    metrics = []
    for item in data:
        conversions = 0
        if "actions" in item:
            for action in item["actions"]:
                if action.get("action_type") == "offsite_conversion":
                    conversions += int(action.get("value", 0))
        metric = AdMetric(
            id=None,
            campaign_id=item.get("campaign_id"),
            ad_id=item.get("ad_id"),
            date=datetime.strptime(item.get("date_start"), "%Y-%m-%d").date(),
            clicks=int(item.get("clicks", 0)),
            impressions=int(item.get("impressions", 0)),
            spend=float(item.get("spend", 0.0)),
            conversions=conversions
        )
        metrics.append(metric)
    logger.info(f"Fetched {len(metrics)} ad metrics from Facebook.")
    return metrics

def map_metrics_to_contacts(metrics: List[AdMetric]) -> List[Contact]:
    """
    Map ad metrics to HubSpot contacts.
    For demo: match ad_id to facebook_id in contacts (in production, use a real mapping).
    """
    contacts = []
    for metric in metrics:
        # Fetch or create contact in HubSpot by facebook_id (ad_id as proxy)
        contact = get_or_create_hubspot_contact(metric.ad_id)
        contact.update_from_metric(metric)
        contacts.append(contact)
    logger.info(f"Mapped {len(contacts)} ad metrics to contacts.")
    return contacts

def map_metrics_to_deals(metrics: List[AdMetric]) -> List[Deal]:
    """
    Map ad metrics to HubSpot deals.
    For demo: create/update a deal for each contact.
    """
    deals = []
    for metric in metrics:
        contact = get_or_create_hubspot_contact(metric.ad_id)
        deal = get_or_create_hubspot_deal(contact.id)
        deal.update_from_metric(metric)
        deals.append(deal)
    logger.info(f"Mapped {len(deals)} ad metrics to deals.")
    return deals

def get_or_create_hubspot_contact(facebook_id: str) -> Contact:
    """
    Get or create a HubSpot contact by facebook_id (ad_id as proxy).
    """
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
    params = {"limit": 1, "properties": "email,firstname,facebook_id"}
    search_url = f"{HUBSPOT_CONTACTS_URL}/search"
    search_body = {
        "filterGroups": [
            {
                "filters": [
                    {"propertyName": "facebook_id", "operator": "EQ", "value": facebook_id}
                ]
            }
        ],
        "properties": ["email", "firstname", "facebook_id"]
    }
    response = requests.post(search_url, headers=headers, json=search_body)
    if response.status_code == 200 and response.json().get("results"):
        contact_data = response.json()["results"][0]
        contact = Contact.from_hubspot(contact_data)
        logger.info(f"Found existing HubSpot contact for facebook_id={facebook_id}")
    else:
        # Create a new contact
        create_body = {
            "properties": {
                "email": f"{facebook_id}@example.com",
                "firstname": f"FB User {facebook_id}",
                "facebook_id": facebook_id
            }
        }
        response = requests.post(HUBSPOT_CONTACTS_URL, headers=headers, json=create_body)
        if response.status_code != 201:
            logger.error(f"Failed to create HubSpot contact: {response.text}")
            raise Exception("Failed to create HubSpot contact")
        contact = Contact.from_hubspot(response.json())
        logger.info(f"Created new HubSpot contact for facebook_id={facebook_id}")
    return contact

def get_or_create_hubspot_deal(contact_id: int) -> Deal:
    """
    Get or create a HubSpot deal for a contact.
    """
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
    params = {"limit": 1, "properties": "amount,stage,contact_id"}
    search_url = f"{HUBSPOT_DEALS_URL}/search"
    search_body = {
        "filterGroups": [
            {
                "filters": [
                    {"propertyName": "contact_id", "operator": "EQ", "value": str(contact_id)}
                ]
            }
        ],
        "properties": ["amount", "stage", "contact_id"]
    }
    response = requests.post(search_url, headers=headers, json=search_body)
    if response.status_code == 200 and response.json().get("results"):
        deal_data = response.json()["results"][0]
        deal = Deal.from_hubspot(deal_data)
        logger.info(f"Found existing HubSpot deal for contact_id={contact_id}")
    else:
        # Create a new deal
        create_body = {
            "properties": {
                "amount": 0,
                "stage": "appointmentscheduled",
                "contact_id": str(contact_id)
            }
        }
        response = requests.post(HUBSPOT_DEALS_URL, headers=headers, json=create_body)
        if response.status_code != 201:
            logger.error(f"Failed to create HubSpot deal: {response.text}")
            raise Exception("Failed to create HubSpot deal")
        deal = Deal.from_hubspot(response.json())
        logger.info(f"Created new HubSpot deal for contact_id={contact_id}")
    return deal

def update_hubspot_contact(contact: Contact):
    """
    Update a HubSpot contact with new metric data.
    """
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
    update_url = f"{HUBSPOT_CONTACTS_URL}/{contact.id}"
    update_body = {"properties": contact.to_hubspot()}
    response = requests.patch(update_url, headers=headers, json=update_body)
    if response.status_code not in (200, 204):
        logger.error(f"Failed to update HubSpot contact: {response.text}")
        raise Exception("Failed to update HubSpot contact")
    logger.info(f"Updated HubSpot contact id={contact.id}")

def update_hubspot_deal(deal: Deal):
    """
    Update a HubSpot deal with new metric data.
    """
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
    update_url = f"{HUBSPOT_DEALS_URL}/{deal.id}"
    update_body = {"properties": deal.to_hubspot()}
    response = requests.patch(update_url, headers=headers, json=update_body)
    if response.status_code not in (200, 204):
        logger.error(f"Failed to update HubSpot deal: {response.text}")
        raise Exception("Failed to update HubSpot deal")
    logger.info(f"Updated HubSpot deal id={deal.id}")

def run_mapping_sync() -> Dict[str, Any]:
    """
    Main entry point for the sync routine.
    Fetches Facebook ad metrics, maps to contacts and deals, updates HubSpot.
    Returns a summary dict.
    """
    ad_account_id = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
    if not ad_account_id or not FACEBOOK_ACCESS_TOKEN or not HUBSPOT_ACCESS_TOKEN:
        logger.error("Missing required credentials for sync.")
        raise Exception("Missing required credentials for sync.")

    # Sync last 1 day (can be parameterized)
    today = datetime.utcnow().date()
    since = (today - timedelta(days=1)).isoformat()
    until = today.isoformat()

    metrics = fetch_facebook_ad_metrics(ad_account_id, FACEBOOK_ACCESS_TOKEN, since, until)
    contacts = map_metrics_to_contacts(metrics)
    deals = map_metrics_to_deals(metrics)

    # Update contacts and deals in HubSpot
    for contact in contacts:
        update_hubspot_contact(contact)
    for deal in deals:
        update_hubspot_deal(deal)

    summary = {
        "metrics_synced": len(metrics),
        "contacts_updated": len(contacts),
        "deals_updated": len(deals),
        "since": since,
        "until": until
    }
    logger.info(f"Sync summary: {summary}")
    return summary