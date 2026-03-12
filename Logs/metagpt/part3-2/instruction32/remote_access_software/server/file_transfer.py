import logging
from typing import Optional, Dict, Any
import os

from server.security import SecurityManager

class FileTransferManager:
    """
    Manages secure file transfer between client and server.
    Uses AES-256 encryption for all file data in transit.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, security_manager: Optional[SecurityManager] = None):
        self.logger = logging.getLogger("FileTransferManager")
        self.config = config or {}
        self.security_manager = security_manager or SecurityManager()
        self.upload_dir = self.config.get("upload_dir", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def handle_transfer(self, session_id: str, user_id: str, device_id: str, file_info: str, reader, writer):
        """
        Handles file transfer from client to server.
        file_info: expected format "filename:size"
        """
        try:
            filename, size_str = file_info.split(":")
            size = int(size_str)
            safe_filename = f"{session_id}_{user_id}_{device_id}_{os.path.basename(filename)}"
            file_path = os.path.join(self.upload_dir, safe_filename)
            self.logger.info(f"Receiving file '{filename}' ({size} bytes) for session {session_id}")

            # Receive encrypted file data
            received = 0
            encrypted_data = b""
            while received < size:
                chunk = await reader.read(min(4096, size - received))
                if not chunk:
                    break
                encrypted_data += chunk
                received += len(chunk)

            # Decrypt file data
            file_data = self.security_manager.decrypt(encrypted_data)
            if file_data is None:
                self.logger.error("Failed to decrypt file data.")
                writer.write(b"ERR Decryption failed\n")
                await writer.drain()
                return False

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_data)
            self.logger.info(f"File '{filename}' saved to '{file_path}'.")

            writer.write(b"OK File received\n")
            await writer.drain()
            return True
        except Exception as e:
            self.logger.error(f"File transfer error: {e}")
            writer.write(b"ERR File transfer failed\n")
            await writer.drain()
            return False

    async def send_file(self, file_path: str, writer):
        """
        Sends a file to the client securely.
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                writer.write(b"ERR File not found\n")
                await writer.drain()
                return False

            with open(file_path, "rb") as f:
                file_data = f.read()

            encrypted_data = self.security_manager.encrypt(file_data)
            writer.write(encrypted_data)
            await writer.drain()
            self.logger.info(f"File '{file_path}' sent to client.")
            return True
        except Exception as e:
            self.logger.error(f"Error sending file: {e}")
            writer.write(b"ERR File send failed\n")
            await writer.drain()
            return False