import json
import os
from typing import Dict, Any

class Config:
    """
    Configuration management for quiz automation.
    Supports loading/saving config from JSON file and retrieving hotkey setting.
    """

    DEFAULT_CONFIG = {
        "hotkey": "cmd+shift+o",  # Default hotkey for triggering automation
        "ocr_lang": "eng",        # Default OCR language
        "region": None            # Default screenshot region (None = full screen)
    }

    @staticmethod
    def load_config(path: str) -> Dict[str, Any]:
        """
        Loads configuration from a JSON file.
        If the file does not exist, returns the default config.
        Args:
            path: Path to the config file.
        Returns:
            Config dictionary.
        """
        if not os.path.exists(path):
            print(f"[INFO] Config file not found at {path}. Using default config.")
            return Config.DEFAULT_CONFIG.copy()
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Ensure all default keys are present
            for key, value in Config.DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            print(f"[OK] Loaded config from {path}.")
            return config
        except Exception as e:
            print(f"[ERROR] Failed to load config from {path}: {e}. Using default config.")
            return Config.DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(config: Dict[str, Any], path: str) -> None:
        """
        Saves configuration to a JSON file.
        Args:
            config: Config dictionary.
            path: Path to the config file.
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(f"[OK] Config saved to {path}.")
        except Exception as e:
            print(f"[ERROR] Failed to save config to {path}: {e}")

    @staticmethod
    def get_hotkey(config: Dict[str, Any]) -> str:
        """
        Retrieves the hotkey setting from the config.
        Args:
            config: Config dictionary.
        Returns:
            Hotkey string.
        """
        return config.get("hotkey", Config.DEFAULT_CONFIG["hotkey"])

    @staticmethod
    def get_ocr_lang(config: Dict[str, Any]) -> str:
        """
        Retrieves the OCR language setting from the config.
        Args:
            config: Config dictionary.
        Returns:
            OCR language string.
        """
        return config.get("ocr_lang", Config.DEFAULT_CONFIG["ocr_lang"])

    @staticmethod
    def get_region(config: Dict[str, Any]):
        """
        Retrieves the screenshot region from the config.
        Args:
            config: Config dictionary.
        Returns:
            Region tuple or None.
        """
        return config.get("region", Config.DEFAULT_CONFIG["region"])


if __name__ == "__main__":
    # Example usage
    config_path = "config.json"
    config = Config.load_config(config_path)
    print("Current hotkey:", Config.get_hotkey(config))
    print("Current OCR language:", Config.get_ocr_lang(config))
    print("Current region:", Config.get_region(config))
    # Save config (demonstration)
    Config.save_config(config, config_path)