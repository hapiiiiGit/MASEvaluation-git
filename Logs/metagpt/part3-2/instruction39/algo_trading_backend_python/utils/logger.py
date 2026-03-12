from loguru import logger
import sys
import os

def setup_logger():
    """
    Set up the centralized logger for the backend application using loguru.
    Logs are output to both stdout and a rotating file.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    # Remove default handlers to avoid duplicate logs
    logger.remove()
    # Console handler
    logger.add(sys.stdout, level=log_level, format=log_format, enqueue=True, backtrace=True, diagnose=True)
    # Rotating file handler
    logger.add(
        "logs/algo_trading_backend.log",
        rotation="10 MB",
        retention="10 days",
        level=log_level,
        format=log_format,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

# Expose logger for import in other modules
__all__ = ["logger", "setup_logger"]