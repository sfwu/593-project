"""
Pydantic schemas for Academic Record API request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class GradeStatus(str, Enum):
    PENDING = "pending"
    GRADED = "graded"
    INCOMPLETE = "incomplete"
    WITHDRAWN = "withdrawn"

class TranscriptStatus(str, Enum):
    DRAFT = "draft"
    OFFICIAL = "official"
    ARCHIVED = "archived"

# Academic Record Schemas
class AcademicRecordBase(BaseModel):
    course_id: int
    semester: str
    year: int
    letter_grade: Optional[str] = None
    numeric_grade: Optional[float] = None
    percentage_grade: Optional[float] = None
    credits_earned: int = 0
    credits_attempted: int = 0
    status: GradeStatus = GradeStatus.PENDING
    professor_notes: Optional[str] = None
    student_notes: Optional[str] = None

class AcademicRecordCreate(AcademicRecordBase):
    pass

class AcademicRecordUpdate(BaseModel):
    letter_grade: Optional[str] = None
    numeric_grade: Optional[float] = None
    percentage_grade: Optional[float] = None
    credits_earned: Optional[int] = None
    credits_attempted: Optional[int] = None
    status: Optional[GradeStatus] = None
    professor_notes: Optional[str] = None
    student_notes: Optional[str] = None

class AcademicRecordResponse(AcademicRecordBase):
    id: int
    student_id: int
    grade_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    course: Optional[Dict[str, Any]] = None  # Course details
    
    class Config:
        from_attributes = True

# Transcript Schemas
class TranscriptBase(BaseModel):
    transcript_type: str = "official"
    status: TranscriptStatus = TranscriptStatus.DRAFT

class TranscriptCreate(TranscriptBase):
    pass

class TranscriptUpdate(BaseModel):
    status: Optional[TranscriptStatus] = None
    file_path: Optional[str] = None
    file_hash: Optional[str] = None

class TranscriptResponse(TranscriptBase):
    id: int
    student_id: int
    generated_date: datetime
    requested_date: datetime
    total_credits_earned: int
    total_credits_attempted: int
    cumulative_gpa: float
    major_gpa: float
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Academic Progress Schemas
class AcademicProgressBase(BaseModel):
    degree_program: str
    major: str
    concentration: Optional[str] = None
    catalog_year: int
    total_credits_required: int = 120
    major_credits_required: int = 60
    general_education_credits_required: int = 30
    elective_credits_required: int = 30

class AcademicProgressCreate(AcademicProgressBase):
    pass

class AcademicProgressUpdate(BaseModel):
    degree_program: Optional[str] = None
    major: Optional[str] = None
    concentration: Optional[str] = None
    total_credits_required: Optional[int] = None
    major_credits_required: Optional[int] = None
    general_education_credits_required: Optional[int] = None
    elective_credits_required: Optional[int] = None
    expected_graduation_date: Optional[datetime] = None

class AcademicProgressResponse(AcademicProgressBase):
    id: int
    student_id: int
    total_credits_earned: int
    major_credits_earned: int
    general_education_credits_earned: int
    elective_credits_earned: int
    cumulative_gpa: float
    major_gpa: float
    semester_gpa: float
    is_on_track: bool
    expected_graduation_date: Optional[datetime] = None
    actual_graduation_date: Optional[datetime] = None
    completed_requirements: Optional[str] = None
    remaining_requirements: Optional[str] = None
    warnings: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Semester GPA Schemas
class SemesterGPABase(BaseModel):
    semester: str
    year: int
    semester_gpa: float = 0.0
    credits_earned: int = 0
    credits_attempted: int = 0
    quality_points: float = 0.0
    courses_completed: int = 0
    courses_attempted: int = 0

class SemesterGPACreate(SemesterGPABase):
    pass

class SemesterGPAUpdate(BaseModel):
    semester_gpa: Optional[float] = None
    credits_earned: Optional[int] = None
    credits_attempted: Optional[int] = None
    quality_points: Optional[float] = None
    courses_completed: Optional[int] = None
    courses_attempted: Optional[int] = None

class SemesterGPAResponse(SemesterGPABase):
    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# GPA Calculation Schemas
class GPACalculationResponse(BaseModel):
    cumulative_gpa: float
    major_gpa: float
    semester_gpa: float
    total_credits_earned: int
    total_credits_attempted: int
    total_quality_points: float
    semester_breakdown: List[SemesterGPAResponse]
    grade_distribution: Dict[str, int]  # A: 5, B+: 3, etc.

# Transcript Generation Schemas
class TranscriptGenerationRequest(BaseModel):
    transcript_type: str = "official"
    include_incomplete: bool = False
    include_withdrawn: bool = False

class TranscriptGenerationResponse(BaseModel):
    transcript_id: int
    status: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    generated_at: datetime

# Academic Progress Summary Schemas
class AcademicProgressSummary(BaseModel):
    student_id: int
    degree_program: str
    major: str
    catalog_year: int
    total_credits_earned: int
    total_credits_required: int
    credits_remaining: int
    completion_percentage: float
    cumulative_gpa: float
    major_gpa: float
    is_on_track: bool
    expected_graduation_date: Optional[datetime] = None
    requirements_status: Dict[str, Any]

# Grade Summary Schemas
class GradeSummary(BaseModel):
    course_code: str
    course_title: str
    semester: str
    year: int
    credits: int
    letter_grade: str
    numeric_grade: float
    percentage_grade: Optional[float] = None
    status: GradeStatus
    grade_date: Optional[datetime] = None

class StudentGradeHistory(BaseModel):
    student_id: int
    total_courses: int
    courses_completed: int
    courses_incomplete: int
    courses_withdrawn: int
    cumulative_gpa: float
    major_gpa: float
    grade_summary: List[GradeSummary]
    semester_breakdown: List[SemesterGPAResponse]

# Validation helpers
class GradeValidator:
    @staticmethod
    def validate_letter_grade(letter_grade: str) -> str:
        """Validate letter grade format"""
        valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP', 'I', 'W']
        if letter_grade not in valid_grades:
            raise ValueError(f"Invalid letter grade: {letter_grade}")
        return letter_grade
    
    @staticmethod
    def validate_numeric_grade(numeric_grade: float) -> float:
        """Validate numeric grade range"""
        if not 0.0 <= numeric_grade <= 4.0:
            raise ValueError("Numeric grade must be between 0.0 and 4.0")
        return numeric_grade
    
    @staticmethod
    def validate_percentage_grade(percentage_grade: float) -> float:
        """Validate percentage grade range"""
        if not 0.0 <= percentage_grade <= 100.0:
            raise ValueError("Percentage grade must be between 0.0 and 100.0")
        return percentage_grade

