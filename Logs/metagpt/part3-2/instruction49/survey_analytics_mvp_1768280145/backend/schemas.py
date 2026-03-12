from datetime import datetime
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, EmailStr, Field
import enum

# Enums matching models.py
class UserRole(str, enum.Enum):
    admin = "admin"
    creator = "creator"
    analyst = "analyst"
    user = "user"

class QuestionType(str, enum.Enum):
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    text = "text"
    rating = "rating"
    number = "number"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.user

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Survey Schemas
class QuestionBase(BaseModel):
    text: str
    type: QuestionType
    options: Optional[List[str]] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[QuestionType] = None
    options: Optional[List[str]] = None

class QuestionResponse(QuestionBase):
    id: int
    survey_id: int

    class Config:
        orm_mode = True

class SurveyBase(BaseModel):
    title: str
    description: Optional[str] = None

class SurveyCreate(SurveyBase):
    questions: List[QuestionCreate]

class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuestionUpdate]] = None

class SurveyResponse(SurveyBase):
    id: int
    created_by: int
    created_at: datetime
    questions: List[QuestionResponse]

    class Config:
        orm_mode = True

# Response Schemas
class ResponseBase(BaseModel):
    answers: Dict[int, Union[str, int, float]]

class ResponseCreate(ResponseBase):
    pass

class ResponseResponse(ResponseBase):
    id: int
    survey_id: int
    user_id: Optional[int] = None
    submitted_at: datetime

    class Config:
        orm_mode = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

# Analytics Schemas
class RadarChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Union[str, List[float]]]]

class HeatmapData(BaseModel):
    x_labels: List[str]
    y_labels: List[str]
    data: List[List[float]]

# Report Schemas
class PDFReportResponse(BaseModel):
    filename: str
    content: bytes

class CSVReportResponse(BaseModel):
    filename: str
    content: bytes