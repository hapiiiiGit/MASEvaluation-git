import cv2
import threading
import time
from typing import Optional
import numpy as np


class CameraHandler:
    """
    Manages live camera feeds using OpenCV or GStreamer.
    Supports initialization, starting, reading frames, and stopping the feed.
    """

    def __init__(self, source: str):
        """
        Initialize the CameraHandler.

        Args:
            source (str): Camera source (device index, file path, or GStreamer pipeline string).
        """
        self.source = source
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.error = None

    def start(self) -> None:
        """
        Start the camera feed and begin reading frames in a background thread.
        """
        if self.running:
            return
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera source: {self.source}")
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self) -> None:
        """
        Internal method to continuously read frames from the camera.
        """
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.error = "Failed to read frame from camera."
                    time.sleep(0.01)
                    continue
                with self.lock:
                    self.frame = frame
            except Exception as e:
                self.error = str(e)
                time.sleep(0.01)

    def read_frame(self) -> Optional[np.ndarray]:
        """
        Retrieve the latest frame from the camera.

        Returns:
            np.ndarray or None: The latest frame, or None if not available.
        """
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            else:
                return None

    def stop(self) -> None:
        """
        Stop the camera feed and release resources.
        """
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
            self.thread = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.frame = None

    def __del__(self):
        """
        Ensure resources are released when the object is deleted.
        """
        self.stop()