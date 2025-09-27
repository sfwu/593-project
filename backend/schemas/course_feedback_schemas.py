from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseFeedbackCreate(BaseModel):
    course_id: int
    rating: int
    feedback: Optional[str] = ""

class CourseFeedbackResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    rating: int
    feedback: str
    created_at: datetime

    class Config:
        from_attributes = True
