import os
import yaml
import json
from typing import Any, Dict, Optional


class Config:
    """
    Configuration handler for the ISR drone object detection and tracking system.
    Loads configuration from a YAML or JSON file and provides access methods for other modules.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Config object.

        Args:
            config_path (str, optional): Path to the configuration file.
        """
        self._config: Dict[str, Any] = {}
        if config_path:
            self.load(config_path)

    def load(self, path: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML or JSON file.

        Args:
            path (str): Path to the configuration file.

        Returns:
            dict: Loaded configuration dictionary.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        ext = os.path.splitext(path)[1].lower()
        with open(path, 'r') as f:
            if ext in ['.yaml', '.yml']:
                self._config = yaml.safe_load(f)
            elif ext == '.json':
                self._config = json.load(f)
            else:
                raise ValueError("Unsupported config file format. Use .yaml, .yml, or .json.")
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key (str): Configuration key (supports dot notation for nested keys).
            default (Any, optional): Default value if key is not found.

        Returns:
            Any: Configuration value.
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def as_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary.

        Returns:
            dict: Configuration dictionary.
        """
        return self._config

    def __getitem__(self, key: str) -> Any:
        """
        Allow dict-like access to configuration values.

        Args:
            key (str): Configuration key.

        Returns:
            Any: Configuration value.
        """
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the configuration.

        Args:
            key (str): Configuration key.

        Returns:
            bool: True if key exists, False otherwise.
        """
        return self.get(key) is not None