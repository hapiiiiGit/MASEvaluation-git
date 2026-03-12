import os
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Notification channel configuration (extend as needed)
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
NOTIFY_SLACK_WEBHOOK = os.getenv("NOTIFY_SLACK_WEBHOOK")

def notify_error(msg: str):
    """
    Notify about an error event.
    Currently logs the error; can be extended to send email or Slack notifications.
    """
    logger.error(f"[NOTIFY_ERROR] {msg}")
    # Example: send to Slack if webhook is configured
    if NOTIFY_SLACK_WEBHOOK:
        try:
            import requests
            requests.post(NOTIFY_SLACK_WEBHOOK, json={"text": f"ERROR: {msg}"})
        except Exception as e:
            logger.error(f"Failed to send Slack error notification: {e}")
    # Example: send email (placeholder, extend with SMTP/email service)
    if NOTIFY_EMAIL:
        try:
            # Implement email sending logic here if needed
            pass
        except Exception as e:
            logger.error(f"Failed to send email error notification: {e}")

def notify_success(msg: str):
    """
    Notify about a successful event.
    Currently logs the success; can be extended to send email or Slack notifications.
    """
    logger.info(f"[NOTIFY_SUCCESS] {msg}")
    # Example: send to Slack if webhook is configured
    if NOTIFY_SLACK_WEBHOOK:
        try:
            import requests
            requests.post(NOTIFY_SLACK_WEBHOOK, json={"text": f"SUCCESS: {msg}"})
        except Exception as e:
            logger.error(f"Failed to send Slack success notification: {e}")
    # Example: send email (placeholder, extend with SMTP/email service)
    if NOTIFY_EMAIL:
        try:
            # Implement email sending logic here if needed
            pass
        except Exception as e:
            logger.error(f"Failed to send email success notification: {e}")