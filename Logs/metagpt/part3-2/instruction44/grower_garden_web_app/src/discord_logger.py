import os
import requests
from src.models import Transaction

class DiscordLogger:
    """
    Logs transactions and delivery proofs to a Discord channel using webhooks.
    """

    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')

    def log_transaction(self, transaction: Transaction):
        """
        Sends a transaction log message to the Discord channel.
        """
        if not self.webhook_url:
            return  # Webhook not configured

        embed = {
            "title": "New Transaction",
            "color": 3066993,  # Green
            "fields": [
                {"name": "User ID", "value": str(transaction.user_id), "inline": True},
                {"name": "Item ID", "value": str(transaction.item_id), "inline": True},
                {"name": "Amount", "value": f"${transaction.amount:.2f}", "inline": True},
                {"name": "Status", "value": transaction.status, "inline": True},
                {"name": "Payment Provider", "value": transaction.payment_provider, "inline": True},
                {"name": "Created At", "value": transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
            ]
        }

        payload = {
            "username": "Grower Garden Bot",
            "embeds": [embed]
        }

        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception:
            pass  # Optionally log error elsewhere

    def log_delivery_proof(self, transaction: Transaction, proof_url: str):
        """
        Sends a delivery proof log message to the Discord channel.
        """
        if not self.webhook_url:
            return  # Webhook not configured

        embed = {
            "title": "Delivery Proof",
            "color": 3447003,  # Blue
            "fields": [
                {"name": "User ID", "value": str(transaction.user_id), "inline": True},
                {"name": "Item ID", "value": str(transaction.item_id), "inline": True},
                {"name": "Transaction ID", "value": str(transaction.id), "inline": True},
                {"name": "Delivery Proof URL", "value": proof_url or "N/A", "inline": False}
            ]
        }

        payload = {
            "username": "Grower Garden Bot",
            "embeds": [embed]
        }

        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception:
            pass  # Optionally log error elsewhere