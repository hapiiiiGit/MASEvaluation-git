import os
import json

class Config:
    """
    Handles configuration management for the application, including storage type, storage path, and GPT-4 API key.
    Provides:
        - get_storage_type()
        - get_storage_path()
        - get_gpt4_api_key()
    """

    DEFAULT_CONFIG_PATH = "config.json"
    DEFAULT_STORAGE_TYPE = "sqlite"
    DEFAULT_STORAGE_PATH = "storage.db"
    DEFAULT_GPT4_API_KEY = ""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config = self._load_config()

    def _load_config(self):
        # If config file does not exist, create with defaults
        if not os.path.exists(self.config_path):
            config = {
                "storage_type": self.DEFAULT_STORAGE_TYPE,
                "storage_path": self.DEFAULT_STORAGE_PATH,
                "gpt4_api_key": self.DEFAULT_GPT4_API_KEY
            }
            self._save_config(config)
            return config
        else:
            with open(self.config_path, "r") as f:
                try:
                    config = json.load(f)
                except Exception:
                    config = {
                        "storage_type": self.DEFAULT_STORAGE_TYPE,
                        "storage_path": self.DEFAULT_STORAGE_PATH,
                        "gpt4_api_key": self.DEFAULT_GPT4_API_KEY
                    }
            # Ensure all keys exist
            for key, default in [
                ("storage_type", self.DEFAULT_STORAGE_TYPE),
                ("storage_path", self.DEFAULT_STORAGE_PATH),
                ("gpt4_api_key", self.DEFAULT_GPT4_API_KEY)
            ]:
                if key not in config:
                    config[key] = default
            return config

    def _save_config(self, config):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_storage_type(self) -> str:
        """
        Returns the configured storage type ('sqlite' or 'json').
        """
        return self._config.get("storage_type", self.DEFAULT_STORAGE_TYPE).lower()

    def get_storage_path(self) -> str:
        """
        Returns the configured storage path.
        """
        return self._config.get("storage_path", self.DEFAULT_STORAGE_PATH)

    def get_gpt4_api_key(self) -> str:
        """
        Returns the configured GPT-4 API key.
        """
        return self._config.get("gpt4_api_key", self.DEFAULT_GPT4_API_KEY)

    def set_storage_type(self, storage_type: str):
        """
        Sets and saves the storage type.
        """
        self._config["storage_type"] = storage_type.lower()
        self._save_config(self._config)

    def set_storage_path(self, storage_path: str):
        """
        Sets and saves the storage path.
        """
        self._config["storage_path"] = storage_path
        self._save_config(self._config)

    def set_gpt4_api_key(self, api_key: str):
        """
        Sets and saves the GPT-4 API key.
        """
        self._config["gpt4_api_key"] = api_key
        self._save_config(self._config)