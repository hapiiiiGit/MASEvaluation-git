from typing import List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator, ValidationError


class ConversationRecord(BaseModel):
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    timestamp: datetime = Field(..., description="Timestamp of the conversation event")
    user_id: str = Field(..., description="User identifier")
    messages: List[str] = Field(..., description="List of message strings in the conversation")

    @validator('conversation_id')
    def conversation_id_must_not_be_empty(cls, v):
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("conversation_id must be a non-empty string")
        return v

    @validator('timestamp')
    def timestamp_must_be_datetime(cls, v):
        if not isinstance(v, datetime):
            raise ValueError("timestamp must be a datetime object")
        return v

    @validator('user_id')
    def user_id_must_not_be_empty(cls, v):
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("user_id must be a non-empty string")
        return v

    @validator('messages')
    def messages_must_be_non_empty_list(cls, v):
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("messages must be a non-empty list of strings")
        for msg in v:
            if not isinstance(msg, str) or msg.strip() == "":
                raise ValueError("Each message must be a non-empty string")
        return v

    def validate(self) -> bool:
        """
        Validates the ConversationRecord instance.
        Returns True if valid, raises ValidationError otherwise.
        """
        try:
            self.__class__.validate(self)
            return True
        except ValidationError as e:
            raise e

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationRecord":
        """
        Create a ConversationRecord from a dictionary, handling timestamp parsing.
        """
        if "timestamp" in data and not isinstance(data["timestamp"], datetime):
            # Try to parse timestamp from string
            try:
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            except Exception:
                raise ValueError("timestamp must be a datetime or ISO format string")
        return cls(**data)