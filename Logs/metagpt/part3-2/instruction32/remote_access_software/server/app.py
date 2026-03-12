import asyncio
import logging
from typing import Dict, Any

from server.auth import AuthProvider
from server.session import SessionManager
from server.device import DeviceManager
from server.audit import AuditLogger
from server.security import SecurityManager

class RemoteAccessServer:
    """
    Main server class for the remote access software.
    Handles authentication, device authorization, session management, and secure communication.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("RemoteAccessServer")
        self.host = config.get("server_host", "0.0.0.0")
        self.port = config.get("server_port", 8888)
        self.auth_provider = AuthProvider(config.get("auth", {}))
        self.device_manager = DeviceManager()
        self.session_manager = SessionManager()
        self.audit_logger = AuditLogger(config.get("audit", {}))
        self.security_manager = SecurityManager(config.get("security", {}))
        self.server = None
        self.running = False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peername = writer.get_extra_info('peername')
        self.logger.info(f"Incoming connection from {peername}")

        try:
            # Step 1: Authenticate client
            data = await reader.readline()
            auth_request = data.decode().strip()
            if not auth_request.startswith("AUTH "):
                self.logger.warning(f"Malformed auth request from {peername}")
                writer.write(b"ERR Malformed auth request\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            token = auth_request[5:]
            user_id = await self.auth_provider.authenticate_oauth(token)
            if not user_id:
                self.logger.warning(f"Authentication failed for {peername}")
                writer.write(b"ERR Authentication failed\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            # Step 2: Device authorization
            writer.write(b"OK Authenticated\n")
            await writer.drain()
            data = await reader.readline()
            device_request = data.decode().strip()
            if not device_request.startswith("DEVICE "):
                self.logger.warning(f"Malformed device request from {peername}")
                writer.write(b"ERR Malformed device request\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            device_id = device_request[7:]
            device = self.device_manager.get_or_create_device(device_id)
            if not device.authorize(user_id):
                self.logger.warning(f"Device authorization failed for {user_id} on {device_id}")
                writer.write(b"ERR Device authorization failed\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            writer.write(b"OK Device authorized\n")
            await writer.drain()

            # Step 3: Session management
            session = self.session_manager.create_session(user_id, device_id)
            self.audit_logger.log_event("session_start", user_id, device_id)
            writer.write(f"OK Session {session.session_id} started\n".encode())
            await writer.drain()

            # Step 4: Main session loop (handle commands)
            while True:
                data = await reader.readline()
                if not data:
                    break
                command = data.decode().strip()
                if command == "END":
                    self.logger.info(f"Session {session.session_id} ended by client")
                    self.audit_logger.log_event("session_end", user_id, device_id)
                    break
                elif command.startswith("TRANSFER "):
                    # Handle file transfer (details in file_transfer.py)
                    file_info = command[9:]
                    await session.handle_file_transfer(file_info, reader, writer)
                elif command == "STREAM":
                    # Handle remote desktop streaming (details in remote_desktop.py)
                    await session.handle_stream_desktop(reader, writer)
                else:
                    writer.write(b"ERR Unknown command\n")
                    await writer.drain()

            # Clean up session
            self.session_manager.end_session(session.session_id)
            writer.write(b"OK Session ended\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            self.logger.error(f"Exception in client handler: {e}")
            writer.write(b"ERR Internal server error\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    def start(self):
        self.logger.info(f"Starting RemoteAccessServer on {self.host}:{self.port}")
        self.running = True
        asyncio.run(self._run_server())

    async def _run_server(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        addr = self.server.sockets[0].getsockname()
        self.logger.info(f"Server listening on {addr}")

        async with self.server:
            await self.server.serve_forever()

    def stop(self):
        self.logger.info("Stopping RemoteAccessServer...")
        self.running = False
        # Proper shutdown logic can be added here if needed

# For direct execution (optional)
if __name__ == "__main__":
    import json
    import sys
    import os

    logging.basicConfig(level=logging.INFO)
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "r") as f:
        config = json.load(f)
    server = RemoteAccessServer(config)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()