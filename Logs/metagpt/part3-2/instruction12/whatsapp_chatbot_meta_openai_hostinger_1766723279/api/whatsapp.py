import os
import requests
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

# MetaAPI class for WhatsApp messaging integration
class MetaAPI:
    def __init__(self, token: str, phone_number_id: str, api_version: str = "v18.0"):
        self.token = token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_whatsapp_message(self, to: str, text: str) -> bool:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    def receive_webhook(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse the incoming webhook from Meta and extract message info.
        Returns a dict with sender, message, and message_id if valid, else None.
        """
        try:
            entry = request_data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None
            message = messages[0]
            sender = message["from"]
            message_id = message["id"]
            text = message.get("text", {}).get("body", "")
            return {
                "sender": sender,
                "message": text,
                "message_id": message_id,
                "raw": message
            }
        except Exception as e:
            print(f"Error parsing webhook: {e}")
            return None

# FastAPI router for WhatsApp webhook
router = APIRouter()

# Load Meta API credentials from environment variables or .env
META_TOKEN = os.getenv("META_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
META_API_VERSION = os.getenv("META_API_VERSION", "v18.0")

meta_api = MetaAPI(token=META_TOKEN, phone_number_id=META_PHONE_NUMBER_ID, api_version=META_API_VERSION)

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Endpoint to receive WhatsApp webhook events from Meta.
    """
    try:
        data = await request.json()
        parsed = meta_api.receive_webhook(data)
        if parsed:
            # Here you would typically enqueue the message for processing,
            # or call your bot's message handler.
            # For now, just acknowledge receipt.
            print(f"Received WhatsApp message: {parsed}")
        return JSONResponse(content={"status": "received"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

@router.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(
    hub_mode: str = "", hub_challenge: str = "", hub_verify_token: str = ""
):
    """
    Verification endpoint for WhatsApp webhook setup.
    """
    VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "my_verify_token")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return JSONResponse(content=hub_challenge, status_code=status.HTTP_200_OK)
    return JSONResponse(content="Verification failed", status_code=status.HTTP_403_FORBIDDEN)