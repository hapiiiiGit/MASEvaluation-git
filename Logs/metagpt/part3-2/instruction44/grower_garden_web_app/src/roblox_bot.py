import os
import requests
from src.models import User, Item, Transaction

class RobloxBot:
    """
    Handles automatic item delivery to users via Roblox bot.
    """

    def __init__(self):
        # Example: Endpoint for bot API, or credentials if using RPA
        self.bot_api_url = os.getenv('ROBLOX_BOT_API_URL', 'https://api.example-roblox-bot.com/deliver')
        self.bot_api_key = os.getenv('ROBLOX_BOT_API_KEY', '')

    def deliver_item(self, user: User, item: Item) -> str:
        """
        Delivers the specified item to the user's Roblox account.
        Returns a delivery proof URL (e.g., screenshot or confirmation link).
        """
        payload = {
            "roblox_username": user.roblox_username,
            "asset_id": item.roblox_asset_id,
            "private_server_info": user.private_server_info,
            "api_key": self.bot_api_key
        }
        try:
            response = requests.post(self.bot_api_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Expecting bot to return a delivery proof URL
            delivery_proof_url = data.get("delivery_proof_url", "")
            return delivery_proof_url
        except Exception as e:
            # Log error, return empty string as proof
            return ""

    def get_delivery_proof(self, transaction: Transaction) -> str:
        """
        Returns the delivery proof URL for a given transaction.
        """
        return transaction.delivery_proof_url or ""