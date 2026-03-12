import logging
from typing import Any
from datetime import datetime
from .utils import OpenAIClient  # For type hints if needed

def setup_logger(log_file: str = "chatbot_backend.log") -> logging.Logger:
    """
    Sets up and returns a logger for the backend.
    Logs to both console and a file.
    """
    logger = logging.getLogger("chatbot_backend")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Avoid duplicate logs
    logger.propagate = False

    return logger

def log_request(logger: logging.Logger, request: Any) -> None:
    """
    Logs the incoming chat request.
    """
    logger.info(f"Received request: user_id={getattr(request, 'user_id', None)}, message={getattr(request, 'message', None)}")

def log_response(logger: logging.Logger, response: Any) -> None:
    """
    Logs the outgoing chat response.
    """
    logger.info(f"Sent response: response={getattr(response, 'response', None)}, timestamp={getattr(response, 'timestamp', None)}")