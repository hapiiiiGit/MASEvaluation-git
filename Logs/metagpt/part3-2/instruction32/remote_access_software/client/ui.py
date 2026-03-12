import sys
import logging
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer

from client.connection import RemoteAccessClientConnection

class DeviceListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []

    def update_devices(self, devices: List[Dict[str, Any]]):
        self.clear()
        self.devices = devices
        for device in devices:
            status = "Online" if device.get("online") else "Offline"
            auth = "Authorized" if device.get("authorized") else "Unauthorized"
            item = QListWidgetItem(
                f"{device.get('device_id')} ({device.get('platform')}) - {status}, {auth}"
            )
            if not device.get("online"):
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.addItem(item)

    def get_selected_device(self) -> Optional[Dict[str, Any]]:
        selected = self.currentRow()
        if 0 <= selected < len(self.devices):
            return self.devices[selected]
        return None

class SessionWindow(QDialog):
    def __init__(self, session_id: str, client_conn: RemoteAccessClientConnection, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.client_conn = client_conn
        self.setWindowTitle(f"Remote Session - {session_id}")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.running = True
        self.start_stream()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Session Active")
        self.desktop_view = QLabel("Remote desktop stream will appear here.")
        self.desktop_view.setStyleSheet("background-color: #222; color: #fff; padding: 20px;")
        self.file_transfer_btn = QPushButton("Send File")
        self.file_transfer_btn.clicked.connect(self.send_file)
        self.end_btn = QPushButton("End Session")
        self.end_btn.clicked.connect(self.end_session)
        layout.addWidget(self.status_label)
        layout.addWidget(self.desktop_view)
        layout.addWidget(self.file_transfer_btn)
        layout.addWidget(self.end_btn)
        self.setLayout(layout)

    def start_stream(self):
        # Simulate remote desktop streaming with a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stream)
        self.timer.start(1000)  # 1 FPS for demo

    def update_stream(self):
        if not self.running:
            return
        frame = self.client_conn.get_next_desktop_frame(self.session_id)
        if frame:
            self.desktop_view.setText(frame)
        else:
            self.desktop_view.setText("Waiting for remote desktop stream...")

    def send_file(self):
        file_path, ok = QInputDialog.getText(self, "Send File", "Enter file path to send:")
        if ok and file_path:
            result = self.client_conn.send_file(self.session_id, file_path)
            if result:
                QMessageBox.information(self, "File Transfer", "File sent successfully.")
            else:
                QMessageBox.warning(self, "File Transfer", "File transfer failed.")

    def end_session(self):
        self.running = False
        self.timer.stop()
        self.client_conn.end_session(self.session_id)
        self.status_label.setText("Session Ended")
        self.accept()

class RemoteAccessClientUI(QWidget):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger("RemoteAccessClientUI")
        self.setWindowTitle("Remote Access Client")
        self.setMinimumSize(800, 600)
        self.client_conn = RemoteAccessClientConnection(config)
        self.init_ui()
        self.refresh_devices()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(5000)  # Refresh device list every 5 seconds

    def init_ui(self):
        main_layout = QVBoxLayout()
        header = QLabel("Remote Access Dashboard")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(header)

        # Device list and controls
        device_layout = QHBoxLayout()
        self.device_list = DeviceListWidget()
        device_layout.addWidget(self.device_list)

        controls_layout = QVBoxLayout()
        self.quick_connect_btn = QPushButton("Quick Connect")
        self.quick_connect_btn.clicked.connect(self.quick_connect)
        self.refresh_btn = QPushButton("Refresh Devices")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        self.session_status = QLabel("No active session.")
        self.security_status = QLabel("Security: Disconnected")
        controls_layout.addWidget(self.quick_connect_btn)
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addWidget(self.session_status)
        controls_layout.addWidget(self.security_status)
        controls_layout.addStretch()
        device_layout.addLayout(controls_layout)

        main_layout.addLayout(device_layout)

        # Recent sessions
        self.recent_sessions_label = QLabel("Recent Sessions:")
        self.recent_sessions_list = QListWidget()
        main_layout.addWidget(self.recent_sessions_label)
        main_layout.addWidget(self.recent_sessions_list)

        # Settings
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        main_layout.addWidget(self.settings_btn)

        self.setLayout(main_layout)

    def refresh_devices(self):
        devices = self.client_conn.get_device_list()
        self.device_list.update_devices(devices)
        self.security_status.setText(
            f"Security: {'Connected' if self.client_conn.is_authenticated() else 'Disconnected'}"
        )

    def quick_connect(self):
        device = self.device_list.get_selected_device()
        if not device:
            QMessageBox.warning(self, "Quick Connect", "Please select an online device to connect.")
            return
        if not device.get("authorized"):
            QMessageBox.warning(self, "Quick Connect", "Device is not authorized for your account.")
            return
        session_id = self.client_conn.start_session(device["device_id"])
        if session_id:
            self.session_status.setText(f"Active session: {session_id}")
            self.recent_sessions_list.addItem(f"{device['device_id']} ({session_id})")
            session_window = SessionWindow(session_id, self.client_conn, self)
            session_window.exec_()
            self.session_status.setText("No active session.")
        else:
            QMessageBox.critical(self, "Quick Connect", "Failed to start remote session.")

    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog not implemented in this demo.")

    def run(self):
        self.show()

# For direct execution (for development/testing)
if __name__ == "__main__":
    import json
    import os

    logging.basicConfig(level=logging.INFO)
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "r") as f:
        config = json.load(f)
    app = QApplication(sys.argv)
    ui = RemoteAccessClientUI(config)
    ui.run()
    sys.exit(app.exec_())