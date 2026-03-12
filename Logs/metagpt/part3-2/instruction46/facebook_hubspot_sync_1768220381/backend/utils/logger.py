import logging
import sys
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured logger instance for the given module name.
    Ensures consistent formatting and log level across backend modules.
    """
    logger = logging.getLogger(name if name else "facebook_hubspot_sync")
    if not logger.hasHandlers():
        # Set log level (can be configured via environment variable if needed)
        logger.setLevel(logging.INFO)

        # Create console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(ch)
        logger.propagate = False

    return logger