import logging
import json
import threading
from typing import Any, Dict, List, Optional


class Logger:
    """
    Logger class for structured logging of events, errors, and system status.
    Logs are written to a file in JSON format.
    """

    def __init__(self, log_path: str):
        """
        Initialize the Logger.

        Args:
            log_path (str): Path to the log file.
        """
        self._log_path = log_path
        self._lock = threading.RLock()
        self._setup_logger()

    def _setup_logger(self):
        """
        Set up the Python logging module for structured logging.
        """
        self._logger = logging.getLogger("AI_Submarine_Detection_Logger")
        self._logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if re-initialized
        if not self._logger.handlers:
            file_handler = logging.FileHandler(self._log_path)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

    def log_event(self, event: Dict[str, Any]) -> None:
        """
        Log a structured event.

        Args:
            event (dict): Event data to log.
        """
        with self._lock:
            log_entry = {
                "type": "event",
                "data": event
            }
            self._logger.info(json.dumps(log_entry))

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with optional context.

        Args:
            error (Exception): The exception to log.
            context (dict, optional): Additional context information.
        """
        with self._lock:
            log_entry = {
                "type": "error",
                "error": {
                    "message": str(error),
                    "type": type(error).__name__
                },
                "context": context if context else {}
            }
            self._logger.error(json.dumps(log_entry))

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieve all logs from the log file.

        Returns:
            list: List of log entries as dictionaries.
        """
        logs = []
        with self._lock:
            try:
                with open(self._log_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                # Skip malformed log lines
                                continue
            except FileNotFoundError:
                # No logs yet
                pass
        return logs