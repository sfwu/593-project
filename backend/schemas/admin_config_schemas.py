from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TermConfigCreate(BaseModel):
    semester: str
    year: int

class TermConfigResponse(BaseModel):
    id: int
    semester: str
    year: int
    created_at: datetime
    class Config:
        from_attributes = True

class GradingPolicyCreate(BaseModel):
    scale_name: str
    details: str  # JSON string or text

class GradingPolicyResponse(BaseModel):
    id: int
    scale_name: str
    details: str
    created_at: datetime
    class Config:
        from_attributes = True
