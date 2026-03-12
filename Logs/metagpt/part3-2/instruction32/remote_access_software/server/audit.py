import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogger:
    """
    Implements audit logging for the remote access server.
    Records session events, file transfers, and security-related actions for compliance and monitoring.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.log_dir = self.config.get("log_dir", "audit_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, self._get_log_filename())
        self.logger = logging.getLogger("AuditLogger")
        self.logger.setLevel(logging.INFO)
        self._setup_file_handler()

    def _get_log_filename(self) -> str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return f"audit_{date_str}.log"

    def _setup_file_handler(self):
        # Avoid adding multiple handlers if re-instantiated
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(self.log_file)
                   for h in self.logger.handlers):
            file_handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_event(self, event_type: str, user_id: str, device_id: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log an audit event.
        :param event_type: Type of event (e.g., session_start, session_end, file_transfer, authentication, etc.)
        :param user_id: ID of the user involved
        :param device_id: ID of the device involved
        :param extra: Optional dictionary with additional event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "user_id": user_id,
            "device_id": device_id,
        }
        if extra:
            event.update(extra)
        # Write to file as JSON for structured logs
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
            self.logger.info(f"Audit event logged: {event_type} (user={user_id}, device={device_id})")
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")

    def rotate_log(self):
        """
        Rotates the audit log file (e.g., at midnight or on demand).
        """
        self.log_file = os.path.join(self.log_dir, self._get_log_filename())
        self._setup_file_handler()
        self.logger.info("Audit log rotated.")

    def get_events(self, since: Optional[datetime] = None) -> list:
        """
        Retrieve audit events, optionally filtering by timestamp.
        :param since: Only return events after this UTC datetime.
        :return: List of event dicts.
        """
        events = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        if since:
                            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", ""))
                            if event_time < since:
                                continue
                        events.append(event)
                    except Exception:
                        continue
        except FileNotFoundError:
            self.logger.warning("Audit log file not found when retrieving events.")
        except Exception as e:
            self.logger.error(f"Error reading audit log: {e}")
        return events