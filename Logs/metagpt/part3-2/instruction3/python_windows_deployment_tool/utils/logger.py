import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def get_logger(log_file="deployment.log", log_level="INFO"):
    """
    Configures and returns a logger with both file and console handlers.
    Supports log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    Log messages are formatted for troubleshooting.
    """
    logger = logging.getLogger("PythonWindowsDeploymentTool")
    if getattr(logger, "_is_configured", False):
        return logger  # Prevent duplicate handlers

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Log format
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger._is_configured = True
    return logger