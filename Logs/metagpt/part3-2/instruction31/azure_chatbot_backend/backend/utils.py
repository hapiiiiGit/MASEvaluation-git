import logging
from typing import Optional

# Configure logging for the backend
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("azure_chatbot_backend")

def validate_user_message(message: Optional[str]) -> str:
    """
    Validates the user message input.
    Returns the stripped message if valid, raises ValueError otherwise.
    """
    if message is None:
        raise ValueError("Message cannot be None.")
    message = message.strip()
    if not message:
        raise ValueError("Message cannot be empty.")
    return message

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Logs an error with optional context.
    """
    if context:
        logger.error(f"{context}: {str(error)}")
    else:
        logger.error(str(error))

def log_info(info: str, context: Optional[str] = None) -> None:
    """
    Logs an info message with optional context.
    """
    if context:
        logger.info(f"{context}: {info}")
    else:
        logger.info(info)