import logging
import traceback
from datetime import datetime

class Logger:
    """
    Provides robust logging and error reporting throughout the system.
    Supports logging messages at different levels and logging exceptions.
    """

    def __init__(self, log_file: str = "appium_automation.log"):
        """
        Initialize the logger with a file handler and console output.
        """
        self.logger = logging.getLogger("AppiumAutomationLogger")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if multiple Logger instances are created
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def log(self, msg: str, level: str = "INFO") -> None:
        """
        Log a message at the specified level.
        Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        level = level.upper()
        if level == "DEBUG":
            self.logger.debug(msg)
        elif level == "INFO":
            self.logger.info(msg)
        elif level == "WARNING":
            self.logger.warning(msg)
        elif level == "ERROR":
            self.logger.error(msg)
        elif level == "CRITICAL":
            self.logger.critical(msg)
        else:
            self.logger.info(msg)

    def log_error(self, error: Exception) -> None:
        """
        Log an exception with traceback at ERROR level.
        """
        error_msg = f"Exception occurred: {str(error)}\n{traceback.format_exc()}"
        self.logger.error(error_msg)

    def log_event(self, event: str, level: str = "INFO") -> None:
        """
        Log a custom event message.
        """
        self.log(f"Event: {event}", level)