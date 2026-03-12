from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    user_id: str
    email: EmailStr
    roles: List[str]

class FileUpload(BaseModel):
    file_id: str
    user_id: str
    filename: str
    status: str  # e.g., "pending", "uploaded", "failed"