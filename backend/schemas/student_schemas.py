"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"

# Authentication schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: UserRole
    user_id: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# Base User schemas
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Student schemas
class StudentBase(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    major: Optional[str] = None
    year_level: Optional[str] = None

class StudentCreate(StudentBase):
    email: EmailStr
    password: str = Field(..., min_length=6)
    date_of_birth: Optional[datetime] = None

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    major: Optional[str] = None
    year_level: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    enrollment_date: datetime
    graduation_date: Optional[datetime] = None
    gpa: Optional[str] = None
    
    class Config:
        from_attributes = True

# Professor schemas
class ProfessorBase(BaseModel):
    professor_id: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    office_location: Optional[str] = None
    office_hours: Optional[str] = None
    department: str
    title: Optional[str] = None
    specialization: Optional[str] = None

class ProfessorCreate(ProfessorBase):
    email: EmailStr
    password: str = Field(..., min_length=6)

class ProfessorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    office_location: Optional[str] = None
    office_hours: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    specialization: Optional[str] = None

class ProfessorResponse(ProfessorBase):
    id: int
    
    class Config:
        from_attributes = True

# Course schemas
class CourseBase(BaseModel):
    course_code: str
    title: str
    description: Optional[str] = None
    credits: int = 3
    department: str
    semester: str
    year: int
    max_enrollment: int = 30
    prerequisites: Optional[str] = None
    schedule: Optional[str] = None
    syllabus: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    max_enrollment: Optional[int] = None
    prerequisites: Optional[str] = None
    schedule: Optional[str] = None
    syllabus: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    professor_id: int
    is_active: bool
    created_at: datetime
    enrolled_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class CourseWithProfessor(CourseResponse):
    professor: ProfessorResponse

class CourseWithStudents(CourseResponse):
    enrolled_students: List[StudentResponse]

# Enrollment schemas
class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentResponse(BaseModel):
    student_id: int
    course_id: int
    enrollment_date: datetime
    status: str
    course: CourseResponse
