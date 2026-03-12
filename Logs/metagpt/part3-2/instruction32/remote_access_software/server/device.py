import logging
from typing import Dict, Optional

class Device:
    """
    Represents a device in the remote access system.
    Handles device registration, status, and authorization logic.
    """
    def __init__(self, device_id: str, platform: str, authorized: bool = False):
        self.device_id = device_id
        self.platform = platform
        self.authorized = authorized
        self.online = False
        self.logger = logging.getLogger(f"Device-{device_id}")

    def authorize(self, user_id: str) -> bool:
        """
        Authorize the device for the given user.
        In a real system, this would check user permissions, device trust, etc.
        """
        # For demonstration, we simply authorize the device.
        self.authorized = True
        self.logger.info(f"Device {self.device_id} authorized for user {user_id}")
        return self.authorized

    def deauthorize(self):
        """
        Deauthorize the device.
        """
        self.authorized = False
        self.logger.info(f"Device {self.device_id} deauthorized.")

    def set_online(self, online: bool):
        """
        Set the device online/offline status.
        """
        self.online = online
        status = "online" if online else "offline"
        self.logger.info(f"Device {self.device_id} set to {status}.")

    def is_online(self) -> bool:
        """
        Returns whether the device is online.
        """
        return self.online

    def get_status(self) -> str:
        """
        Returns the status of the device.
        """
        status = "online" if self.online else "offline"
        auth = "authorized" if self.authorized else "unauthorized"
        return f"{status}, {auth}"

    def get_desktop_stream(self):
        """
        Simulate desktop streaming.
        In production, this would capture and encode the desktop screen.
        Here, we yield dummy frames.
        """
        for i in range(10):  # Simulate 10 frames
            yield f"FRAME {i}\n".encode()

class DeviceManager:
    """
    Manages all devices in the remote access system.
    Handles device registration, lookup, and status.
    """
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.logger = logging.getLogger("DeviceManager")

    def register_device(self, device_id: str, platform: str) -> Device:
        """
        Register a new device or return existing.
        """
        if device_id in self.devices:
            device = self.devices[device_id]
            self.logger.info(f"Device {device_id} already registered.")
        else:
            device = Device(device_id, platform)
            self.devices[device_id] = device
            self.logger.info(f"Device {device_id} registered with platform {platform}.")
        return device

    def get_device(self, device_id: str) -> Optional[Device]:
        """
        Get a device by its ID.
        """
        return self.devices.get(device_id)

    def get_or_create_device(self, device_id: str, platform: str = "unknown") -> Device:
        """
        Get an existing device or create a new one if not found.
        """
        device = self.get_device(device_id)
        if device is None:
            device = self.register_device(device_id, platform)
        return device

    def set_device_online(self, device_id: str, online: bool):
        """
        Set the online status of a device.
        """
        device = self.get_device(device_id)
        if device:
            device.set_online(online)
        else:
            self.logger.warning(f"Device {device_id} not found to set online status.")

    def authorize_device(self, device_id: str, user_id: str) -> bool:
        """
        Authorize a device for a user.
        """
        device = self.get_device(device_id)
        if device:
            return device.authorize(user_id)
        else:
            self.logger.warning(f"Device {device_id} not found for authorization.")
            return False

    def deauthorize_device(self, device_id: str):
        """
        Deauthorize a device.
        """
        device = self.get_device(device_id)
        if device:
            device.deauthorize()
        else:
            self.logger.warning(f"Device {device_id} not found for deauthorization.")

    def get_all_devices(self) -> Dict[str, Device]:
        """
        Returns all registered devices.
        """
        return self.devices