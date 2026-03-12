import logging
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
import requests

class Notifier:
    """
    Notifier class for sending notifications via email, SMS, and push.
    Includes send_email, send_sms, and send_push methods as per system design.
    """

    def __init__(self, notification_settings: Dict[str, Any]):
        self.logger = logging.getLogger("Notifier")
        self.email_settings = notification_settings.get("email", {})
        self.sms_settings = notification_settings.get("sms", {})
        self.push_settings = notification_settings.get("push", {})

    def send_email(self, msg: str, subject: str = "Trading Bot Notification", to: Optional[str] = None):
        """
        Send an email notification.
        :param msg: Message body
        :param subject: Email subject
        :param to: Recipient email address (optional, uses default if not provided)
        """
        smtp_server = self.email_settings.get("smtp_server")
        smtp_port = self.email_settings.get("smtp_port", 587)
        smtp_user = self.email_settings.get("smtp_user")
        smtp_password = self.email_settings.get("smtp_password")
        from_addr = self.email_settings.get("from_addr")
        to_addr = to or self.email_settings.get("to_addr")

        if not all([smtp_server, smtp_user, smtp_password, from_addr, to_addr]):
            self.logger.error("Email settings are incomplete.")
            return

        try:
            message = MIMEText(msg)
            message["Subject"] = subject
            message["From"] = from_addr
            message["To"] = to_addr

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_addr, [to_addr], message.as_string())
            self.logger.info(f"Email sent to {to_addr}: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")

    def send_sms(self, msg: str, to: Optional[str] = None):
        """
        Send an SMS notification.
        :param msg: Message body
        :param to: Recipient phone number (optional, uses default if not provided)
        """
        sms_api_url = self.sms_settings.get("api_url")
        sms_api_key = self.sms_settings.get("api_key")
        sender_id = self.sms_settings.get("sender_id")
        to_number = to or self.sms_settings.get("to_number")

        if not all([sms_api_url, sms_api_key, sender_id, to_number]):
            self.logger.error("SMS settings are incomplete.")
            return

        payload = {
            "api_key": sms_api_key,
            "sender": sender_id,
            "to": to_number,
            "message": msg
        }

        try:
            response = requests.post(sms_api_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"SMS sent to {to_number}: {msg}")
            else:
                self.logger.error(f"Failed to send SMS: {response.text}")
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")

    def send_push(self, msg: str, title: str = "Trading Bot Alert"):
        """
        Send a push notification.
        :param msg: Message body
        :param title: Notification title
        """
        push_api_url = self.push_settings.get("api_url")
        push_api_key = self.push_settings.get("api_key")
        device_id = self.push_settings.get("device_id")

        if not all([push_api_url, push_api_key, device_id]):
            self.logger.error("Push notification settings are incomplete.")
            return

        payload = {
            "api_key": push_api_key,
            "device_id": device_id,
            "title": title,
            "message": msg
        }

        try:
            response = requests.post(push_api_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Push notification sent: {title} - {msg}")
            else:
                self.logger.error(f"Failed to send push notification: {response.text}")
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {e}")