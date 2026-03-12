import threading
from typing import Any, Optional


class CommunicationRelay:
    """
    CommunicationRelay module for switching between acoustic and RF links
    based on signal quality and operational context. Provides methods to
    switch links, send data, and get current status.
    """

    def __init__(self, config: Any):
        """
        Initialize the CommunicationRelay.

        Args:
            config (Any): Configuration object (should support get()).
        """
        self._lock = threading.RLock()
        self.config = config
        self.link_type = "acoustic"  # Default link
        self.last_signal_quality = None
        self.status = "initialized"
        self.acoustic_threshold = self.config.get("acoustic_signal_threshold", 0.6)
        self.rf_threshold = self.config.get("rf_signal_threshold", 0.8)
        self.min_switch_interval = self.config.get("min_switch_interval", 2.0)  # seconds
        self._last_switch_time = 0.0

    def switch_link(self, signal_quality: float) -> str:
        """
        Switch between acoustic and RF links based on signal quality.

        Args:
            signal_quality (float): Current signal quality metric (0.0 - 1.0).

        Returns:
            str: The selected link type ("acoustic" or "rf").
        """
        import time
        with self._lock:
            now = time.time()
            # Prevent rapid switching
            if now - self._last_switch_time < self.min_switch_interval:
                return self.link_type

            prev_link = self.link_type
            self.last_signal_quality = signal_quality

            # Decision logic: prefer RF if quality is high, else acoustic
            if signal_quality >= self.rf_threshold:
                self.link_type = "rf"
            elif signal_quality >= self.acoustic_threshold:
                self.link_type = "acoustic"
            else:
                # If both are poor, default to acoustic for robustness
                self.link_type = "acoustic"

            if self.link_type != prev_link:
                self.status = f"Switched from {prev_link} to {self.link_type} at {now:.2f}"
                self._last_switch_time = now
            else:
                self.status = f"No switch. Link remains {self.link_type}."

            return self.link_type

    def send_data(self, data: bytes, link_type: Optional[str] = None) -> bool:
        """
        Simulate sending data over the selected link.

        Args:
            data (bytes): Data to send.
            link_type (str, optional): Link type to use ("acoustic" or "rf").
                If None, use the currently selected link.

        Returns:
            bool: True if data was "sent" successfully, False otherwise.
        """
        import time
        with self._lock:
            link = link_type if link_type else self.link_type
            # Simulate latency and reliability
            if link == "rf":
                latency = self.config.get("rf_latency", 0.1)
                reliability = self.config.get("rf_reliability", 0.98)
            else:
                latency = self.config.get("acoustic_latency", 0.5)
                reliability = self.config.get("acoustic_reliability", 0.90)

            time.sleep(latency)  # Simulate transmission delay

            import random
            success = random.random() < reliability
            if success:
                self.status = f"Data sent over {link} link (latency={latency}s)."
            else:
                self.status = f"Data send failed over {link} link (latency={latency}s)."
            return success

    def get_status(self) -> str:
        """
        Get the current status of the communication relay.

        Returns:
            str: Status string.
        """
        with self._lock:
            return self.status