import psutil
import threading
import time
from typing import List, Dict, Any

from session_manager import AppiumSession
from logger import Logger

class Monitor:
    """
    Collects resource metrics, reports status of Appium sessions, and logs events in real time.
    """

    def __init__(self, sessions: List[AppiumSession], interval: float = 5.0):
        """
        Initialize Monitor with a list of AppiumSession objects and monitoring interval (seconds).
        """
        self.sessions = sessions
        self.interval = interval
        self.logger = Logger()
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._metrics: Dict[str, Any] = {}

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect system resource metrics (CPU, memory, etc.).
        Returns a dictionary of metrics.
        """
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "net_io": psutil.net_io_counters()._asdict(),
            "active_sessions": len(self.sessions),
            "session_statuses": {s.session_id: s.status for s in self.sessions}
        }
        self._metrics = metrics
        self.logger.log(f"Collected system metrics: {metrics}", "DEBUG")
        return metrics

    def report_status(self) -> None:
        """
        Report the status of all Appium sessions and system metrics.
        """
        self.logger.log("Reporting Appium session statuses:", "INFO")
        for session in self.sessions:
            self.logger.log(
                f"Session {session.session_id}: Device={session.device.device_id}, Status={session.status}",
                "INFO"
            )
        self.logger.log(f"System Metrics: {self._metrics}", "INFO")

    def log_event(self, event: str) -> None:
        """
        Log a custom event.
        """
        self.logger.log(f"Monitor Event: {event}", "INFO")

    def start_monitoring(self) -> None:
        """
        Start real-time monitoring in a background thread.
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.log("Monitor is already running.", "WARNING")
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.log("Started real-time monitoring thread.", "INFO")

    def stop_monitoring(self) -> None:
        """
        Stop the real-time monitoring thread.
        """
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join()
            self.logger.log("Stopped real-time monitoring thread.", "INFO")

    def _monitor_loop(self) -> None:
        """
        Internal loop for periodic monitoring.
        """
        while not self._stop_event.is_set():
            try:
                self.collect_metrics()
                self.report_status()
            except Exception as e:
                self.logger.log_error(e)
            time.sleep(self.interval)