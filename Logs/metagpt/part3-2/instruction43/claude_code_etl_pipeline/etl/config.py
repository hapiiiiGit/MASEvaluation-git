from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
import yaml
import os


class Config(BaseModel):
    db_uri: str = Field(..., description="QuestDB connection URI")
    retry_policy: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_attempts": 3,
            "backoff_seconds": 2,
            "max_backoff_seconds": 30,
            "jitter": True
        },
        description="Retry policy for pipeline operations"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    @classmethod
    def load(cls, path: str) -> "Config":
        """
        Load configuration from a YAML or JSON file.

        Args:
            path (str): Path to the configuration file.

        Returns:
            Config: Loaded configuration object.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValidationError: If the config is invalid.
            ValueError: If the file format is unsupported.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.endswith(".yaml") or path.endswith(".yml"):
                raw = yaml.safe_load(f)
            elif path.endswith(".json"):
                import json
                raw = json.load(f)
            else:
                raise ValueError("Unsupported config file format. Use .yaml, .yml, or .json")

        try:
            return cls(**raw)
        except ValidationError as ve:
            raise ve

    def dict(self) -> Dict[str, Any]:
        """
        Return the config as a dictionary.
        """
        return super().dict()


# Example usage:
# config = Config.load("config.yaml")