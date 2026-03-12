import os
import json
from typing import Any, Optional, Dict
from datetime import datetime

class Config:
    """
    Configuration management utility for the Digital Diver's Logbook app.
    Handles app settings, user/session info, cloud credentials, export paths, and runtime options.
    Provides get/set methods and persistent storage.
    """

    CONFIG_FILENAME = "diverlogbook_config.json"

    def __init__(self, config_dir: Optional[str] = None):
        # Determine config directory (platform-agnostic)
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".digital_divers_logbook")
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except Exception:
                self._config = {}
        else:
            self._config = {}

    def _save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self._save()

    # User/session management
    def get_current_user_id(self) -> Optional[int]:
        return self._config.get("current_user_id")

    def set_current_user_id(self, user_id: Optional[int]):
        if user_id is not None:
            self._config["current_user_id"] = user_id
        else:
            self._config.pop("current_user_id", None)
        self._save()

    # Cloud credentials
    def set_cloud_credential(self, provider: str, key: str, value: Any):
        if "cloud_credentials" not in self._config:
            self._config["cloud_credentials"] = {}
        if provider not in self._config["cloud_credentials"]:
            self._config["cloud_credentials"][provider] = {}
        self._config["cloud_credentials"][provider][key] = value
        self._save()

    def get_cloud_credential(self, provider: str, key: str, default: Any = None) -> Any:
        return self._config.get("cloud_credentials", {}).get(provider, {}).get(key, default)

    # Export directory
    def get_export_dir(self) -> str:
        export_dir = self._config.get("export_dir")
        if not export_dir:
            export_dir = os.path.join(self.config_dir, "exports")
            os.makedirs(export_dir, exist_ok=True)
            self._config["export_dir"] = export_dir
            self._save()
        return export_dir

    def set_export_dir(self, path: str):
        self._config["export_dir"] = path
        os.makedirs(path, exist_ok=True)
        self._save()

    # Tesseract OCR path
    def set_tesseract_cmd(self, path: str):
        self._config["tesseract_cmd"] = path
        self._save()

    def get_tesseract_cmd(self) -> Optional[str]:
        return self._config.get("tesseract_cmd")

    # Encryption settings
    def set_encryption_passphrase(self, passphrase: str):
        self._config["encryption_passphrase"] = passphrase
        self._save()

    def get_encryption_passphrase(self) -> str:
        return self._config.get("encryption_passphrase", "diverlogbook_default_passphrase")

    def set_encryption_salt(self, salt: str):
        self._config["encryption_salt"] = salt
        self._save()

    def get_encryption_salt(self) -> str:
        return self._config.get("encryption_salt", "diverlogbook_salt")

    # Password salt
    def set_password_salt(self, salt: str):
        self._config["password_salt"] = salt
        self._save()

    def get_password_salt(self) -> str:
        return self._config.get("password_salt", "diverlogbook")

    # AWS S3 settings
    def set_aws_credentials(self, access_key_id: str, secret_access_key: str, region: str = "us-east-1"):
        self._config["aws_access_key_id"] = access_key_id
        self._config["aws_secret_access_key"] = secret_access_key
        self._config["aws_region"] = region
        self._save()

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    # Utility
    def get_now_str(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # For testing and reset
    def reset(self):
        self._config = {}
        self._save()