import yaml
import os
from typing import List, Optional

class DeviceConfig:
    def __init__(self, device_id: str, platform_version: str, model: str, appium_url: str):
        self.device_id = device_id
        self.platform_version = platform_version
        self.model = model
        self.appium_url = appium_url

    def __repr__(self):
        return (f"DeviceConfig(device_id={self.device_id}, platform_version={self.platform_version}, "
                f"model={self.model}, appium_url={self.appium_url})")

class Config:
    def __init__(self, devices: List[DeviceConfig], test_scripts: List[str], max_concurrent_sessions: int):
        self.devices = devices
        self.test_scripts = test_scripts
        self.max_concurrent_sessions = max_concurrent_sessions

    @staticmethod
    def load(path: str) -> 'Config':
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)

        # Validate and parse devices
        devices = []
        devices_data = config_data.get('devices', [])
        if not isinstance(devices_data, list):
            raise ValueError("Config 'devices' must be a list.")

        for device in devices_data:
            required_keys = ['device_id', 'platform_version', 'model', 'appium_url']
            for key in required_keys:
                if key not in device:
                    raise ValueError(f"Device config missing required key: {key}")
            devices.append(DeviceConfig(
                device_id=device['device_id'],
                platform_version=device['platform_version'],
                model=device['model'],
                appium_url=device['appium_url']
            ))

        # Validate and parse test scripts
        test_scripts = config_data.get('test_scripts', [])
        if not isinstance(test_scripts, list):
            raise ValueError("Config 'test_scripts' must be a list.")

        # Parse max_concurrent_sessions
        max_concurrent_sessions = config_data.get('max_concurrent_sessions', 1)
        if not isinstance(max_concurrent_sessions, int) or max_concurrent_sessions < 1:
            raise ValueError("Config 'max_concurrent_sessions' must be a positive integer.")

        return Config(
            devices=devices,
            test_scripts=test_scripts,
            max_concurrent_sessions=max_concurrent_sessions
        )