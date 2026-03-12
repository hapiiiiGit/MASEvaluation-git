import threading
import time
import traceback
from typing import Dict, Optional
from appium import webdriver

from config import DeviceConfig
from logger import Logger

class AppiumSession:
    """
    Represents an Appium session for a specific Android device.
    """
    def __init__(self, session_id: str, device: DeviceConfig):
        self.session_id = session_id
        self.device = device
        self.driver: Optional[webdriver.Remote] = None
        self.status = "INITIALIZED"
        self._lock = threading.Lock()

    def start(self):
        """
        Start the Appium session by initializing the Appium driver.
        """
        desired_caps = {
            "platformName": "Android",
            "platformVersion": self.device.platform_version,
            "deviceName": self.device.model,
            "udid": self.device.device_id,
            "automationName": "UiAutomator2",
            # Add more capabilities as needed
        }
        try:
            self.driver = webdriver.Remote(self.device.appium_url, desired_caps)
            self.status = "RUNNING"
        except Exception as e:
            self.status = "FAILED"
            raise e

    def stop(self):
        """
        Stop the Appium session and quit the driver.
        """
        with self._lock:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
            self.status = "STOPPED"

    def restart(self):
        """
        Restart the Appium session.
        """
        self.stop()
        time.sleep(2)  # Small delay before restart
        self.start()

class SessionManager:
    """
    Manages Appium sessions for multiple Android devices.
    """
    def __init__(self):
        self.sessions: Dict[str, AppiumSession] = {}
        self._lock = threading.Lock()
        self.logger = Logger()

    def start_session(self, device: DeviceConfig) -> AppiumSession:
        """
        Start a new Appium session for the given device.
        """
        session_id = f"{device.device_id}-{int(time.time()*1000)}"
        session = AppiumSession(session_id, device)
        try:
            session.start()
            with self._lock:
                self.sessions[session_id] = session
            self.logger.log(f"Session {session_id} started for device {device.device_id}", "INFO")
            return session
        except Exception as e:
            self.logger.log_error(e)
            self.handle_failure(session_id, e)
            raise e

    def stop_session(self, session_id: str) -> None:
        """
        Stop the Appium session with the given session_id.
        """
        with self._lock:
            session = self.sessions.get(session_id)
        if session:
            try:
                session.stop()
                self.logger.log(f"Session {session_id} stopped.", "INFO")
            except Exception as e:
                self.logger.log_error(e)
            with self._lock:
                del self.sessions[session_id]

    def restart_session(self, session_id: str) -> Optional[AppiumSession]:
        """
        Restart the Appium session with the given session_id.
        """
        with self._lock:
            session = self.sessions.get(session_id)
        if session:
            try:
                session.restart()
                self.logger.log(f"Session {session_id} restarted.", "INFO")
                return session
            except Exception as e:
                self.logger.log_error(e)
                self.handle_failure(session_id, e)
        return None

    def handle_failure(self, session_id: str, error: Exception) -> None:
        """
        Handle session failure, log error, and attempt recovery if possible.
        """
        self.logger.log(f"Handling failure for session {session_id}: {str(error)}", "ERROR")
        self.logger.log_error(error)
        # Attempt to restart session if it exists
        with self._lock:
            session = self.sessions.get(session_id)
        if session and session.status != "STOPPED":
            try:
                session.restart()
                self.logger.log(f"Session {session_id} recovered after failure.", "INFO")
            except Exception as e:
                self.logger.log(f"Session {session_id} could not be recovered: {str(e)}", "ERROR")
                session.stop()
                with self._lock:
                    del self.sessions[session_id]