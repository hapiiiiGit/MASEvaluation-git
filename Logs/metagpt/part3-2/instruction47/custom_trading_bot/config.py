import json
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError, root_validator
from cryptography.fernet import Fernet

class BotConfig(BaseModel):
    api_key: str = Field(..., description="CoinDCX API key")
    api_secret: str = Field(..., description="CoinDCX API secret")
    strategy_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for trend-following strategy")
    risk_params: Dict[str, Any] = Field(default_factory=dict, description="Risk management parameters")
    assets: List[str] = Field(default_factory=list, description="List of trading symbols")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Notification preferences")

    @classmethod
    def load(cls, path: str, encryption_key: str = None) -> "BotConfig":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "rb") as f:
            data = f.read()
        if encryption_key:
            fernet = Fernet(encryption_key)
            data = fernet.decrypt(data)
        else:
            data = data.decode("utf-8")
        try:
            config_dict = json.loads(data)
            return cls.parse_obj(config_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid config file: {e}")

    def save(self, path: str, encryption_key: str = None):
        config_dict = self.dict()
        data = json.dumps(config_dict, indent=2)
        if encryption_key:
            fernet = Fernet(encryption_key)
            data = fernet.encrypt(data.encode("utf-8"))
            with open(path, "wb") as f:
                f.write(data)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)

    @staticmethod
    def generate_encryption_key() -> str:
        return Fernet.generate_key().decode("utf-8")

    @root_validator(pre=True)
    def check_required_fields(cls, values):
        required_fields = ["api_key", "api_secret", "strategy_params", "risk_params", "assets", "notification_settings"]
        for field in required_fields:
            if field not in values or values[field] is None:
                raise ValueError(f"Missing required config field: {field}")
        return values