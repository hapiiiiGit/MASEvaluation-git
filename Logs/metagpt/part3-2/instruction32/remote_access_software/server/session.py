import logging
import uuid
from typing import Dict, Optional

from server.device import DeviceManager
from server.file_transfer import FileTransferManager
from server.audit import AuditLogger

class Session:
    """
    Represents a remote access session between a user and a device.
    Handles file transfer and remote desktop streaming.
    """
    def __init__(self, session_id: str, user_id: str, device_id: str,
                 device_manager: DeviceManager,
                 file_transfer_manager: FileTransferManager,
                 audit_logger: AuditLogger):
        self.session_id = session_id
        self.user_id = user_id
        self.device_id = device_id
        self.device_manager = device_manager
        self.file_transfer_manager = file_transfer_manager
        self.audit_logger = audit_logger
        self.active = False
        self.logger = logging.getLogger(f"Session-{session_id}")

    def start(self):
        self.active = True
        self.logger.info(f"Session {self.session_id} started for user {self.user_id} on device {self.device_id}")
        self.audit_logger.log_event("session_start", self.user_id, self.device_id)

    def end(self):
        self.active = False
        self.logger.info(f"Session {self.session_id} ended for user {self.user_id} on device {self.device_id}")
        self.audit_logger.log_event("session_end", self.user_id, self.device_id)

    def transfer_file(self, file_info: str, reader, writer):
        """
        Handles file transfer during the session.
        file_info: metadata about the file (e.g., filename, size)
        """
        self.logger.info(f"Initiating file transfer: {file_info}")
        result = self.file_transfer_manager.handle_transfer(self.session_id, self.user_id, self.device_id, file_info, reader, writer)
        if result:
            self.logger.info(f"File transfer successful: {file_info}")
            self.audit_logger.log_event("file_transfer", self.user_id, self.device_id, extra={"file_info": file_info})
        else:
            self.logger.warning(f"File transfer failed: {file_info}")
        return result

    def stream_desktop(self, reader, writer):
        """
        Handles remote desktop streaming during the session.
        """
        self.logger.info(f"Starting remote desktop stream for session {self.session_id}")
        device = self.device_manager.get_device(self.device_id)
        if not device or not device.is_online():
            self.logger.warning(f"Device {self.device_id} is not online for streaming.")
            writer.write(b"ERR Device not online\n")
            return False
        # Simulate streaming: In production, integrate with platform-specific screen capture and encoding.
        try:
            for frame in device.get_desktop_stream():
                writer.write(frame)
            self.logger.info(f"Remote desktop stream ended for session {self.session_id}")
            self.audit_logger.log_event("desktop_stream", self.user_id, self.device_id)
            return True
        except Exception as e:
            self.logger.error(f"Error during desktop streaming: {e}")
            writer.write(b"ERR Streaming failed\n")
            return False

    def get_status(self) -> str:
        return "active" if self.active else "inactive"

class SessionManager:
    """
    Manages all active sessions.
    """
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.logger = logging.getLogger("SessionManager")
        # These should be set by the server on initialization
        self.device_manager: Optional[DeviceManager] = None
        self.file_transfer_manager: Optional[FileTransferManager] = None
        self.audit_logger: Optional[AuditLogger] = None

    def set_dependencies(self, device_manager: DeviceManager, file_transfer_manager: FileTransferManager, audit_logger: AuditLogger):
        self.device_manager = device_manager
        self.file_transfer_manager = file_transfer_manager
        self.audit_logger = audit_logger

    def create_session(self, user_id: str, device_id: str) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            session_id,
            user_id,
            device_id,
            self.device_manager,
            self.file_transfer_manager,
            self.audit_logger
        )
        session.start()
        self.sessions[session_id] = session
        self.logger.info(f"Session {session_id} created for user {user_id} on device {device_id}")
        return session

    def end_session(self, session_id: str):
        session = self.sessions.get(session_id)
        if session:
            session.end()
            del self.sessions[session_id]
            self.logger.info(f"Session {session_id} ended and removed from active sessions.")

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)