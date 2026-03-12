import logging
from typing import Dict, Any, List, Optional
import threading
import time

class Monitor:
    """
    Monitor class for logging trades, sending alerts, and reporting status.
    Includes log_trade, alert, and get_status methods as per system design.
    """

    def __init__(self):
        self.logger = logging.getLogger("Monitor")
        self._trade_log: List[Dict[str, Any]] = []
        self._alerts: List[Dict[str, Any]] = []
        self._status: Dict[str, Any] = {
            "running": True,
            "last_trade": None,
            "last_alert": None,
            "start_time": time.time(),
            "trade_count": 0,
            "alert_count": 0,
        }
        self._lock = threading.Lock()

    def log_trade(self, trade: Dict[str, Any]):
        """
        Log a trade event.
        :param trade: Trade information dictionary.
        """
        with self._lock:
            self._trade_log.append(trade)
            self._status["last_trade"] = trade
            self._status["trade_count"] += 1
        self.logger.info(f"Trade logged: {trade}")

    def alert(self, event: str):
        """
        Log an alert event.
        :param event: Alert message string.
        """
        alert_info = {
            "timestamp": time.time(),
            "event": event
        }
        with self._lock:
            self._alerts.append(alert_info)
            self._status["last_alert"] = alert_info
            self._status["alert_count"] += 1
        self.logger.warning(f"ALERT: {event}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status.
        :return: Status dictionary.
        """
        with self._lock:
            status_copy = self._status.copy()
            status_copy["uptime_sec"] = time.time() - self._status["start_time"]
        return status_copy

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all trade logs.
        :return: List of trade log dictionaries.
        """
        with self._lock:
            return list(self._trade_log)

    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all alert logs.
        :return: List of alert log dictionaries.
        """
        with self._lock:
            return list(self._alerts)