import json
import threading
from typing import Any, Optional


class Config:
    """
    Config class for loading and managing configuration parameters from a JSON file.
    Thread-safe get and set methods for configuration values.
    """

    def __init__(self, config_file: str):
        """
        Initialize Config object and load configuration from the specified JSON file.

        Args:
            config_file (str): Path to the JSON configuration file.
        """
        self._config_file = config_file
        self._lock = threading.RLock()
        self._config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> dict:
        """
        Load configuration from a JSON file.

        Args:
            config_file (str): Path to the JSON configuration file.

        Returns:
            dict: Configuration dictionary.
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config file '{config_file}': {e}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get the value for a configuration key.

        Args:
            key (str): Configuration key.
            default (Any, optional): Default value if key is not found.

        Returns:
            Any: Value for the key, or default if not found.
        """
        with self._lock:
            return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set the value for a configuration key.

        Args:
            key (str): Configuration key.
            value (Any): Value to set.
        """
        with self._lock:
            self._config[key] = value
            self._save_config()

    def _save_config(self) -> None:
        """
        Save the current configuration to the JSON file.
        """
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to save config file '{self._config_file}': {e}")

    def reload(self) -> None:
        """
        Reload configuration from the JSON file.
        """
        with self._lock:
            self._config = self._load_config(self._config_file)