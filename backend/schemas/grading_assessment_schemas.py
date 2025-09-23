"""
Pydantic schemas for Grading and Assessment API request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum

# Enums
class AssignmentType(str, Enum):
    HOMEWORK = "homework"
    PROJECT = "project"
    LAB = "lab"
    QUIZ = "quiz"
    PRESENTATION = "presentation"
    ESSAY = "essay"
    RESEARCH = "research"
    OTHER = "other"

class ExamType(str, Enum):
    MIDTERM = "midterm"
    FINAL = "final"
    QUIZ = "quiz"
    POP_QUIZ = "pop_quiz"
    PRACTICAL = "practical"
    ORAL = "oral"
    WRITTEN = "written"
    ONLINE = "online"

class GradeStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LATE = "late"
    EXEMPT = "exempt"
    INCOMPLETE = "incomplete"
    MISSING = "missing"

class SubmissionStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    LATE = "late"
    GRADED = "graded"
    RETURNED = "returned"

# Assignment Schemas
class AssignmentBase(BaseModel):
    course_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assignment_type: AssignmentType
    instructions: Optional[str] = None
    requirements: Optional[str] = None
    total_points: float = Field(..., gt=0)
    weight_percentage: float = Field(..., ge=0, le=100)
    rubric: Optional[str] = None
    due_date: datetime
    late_submission_deadline: Optional[datetime] = None
    late_penalty_percentage: float = Field(0, ge=0, le=100)
    allow_late_submissions: bool = True
    max_attempts: int = Field(1, ge=1)
    submission_format: Optional[str] = None
    file_size_limit: Optional[int] = Field(None, gt=0)

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assignment_type: Optional[AssignmentType] = None
    instructions: Optional[str] = None
    requirements: Optional[str] = None
    total_points: Optional[float] = Field(None, gt=0)
    weight_percentage: Optional[float] = Field(None, ge=0, le=100)
    rubric: Optional[str] = None
    due_date: Optional[datetime] = None
    late_submission_deadline: Optional[datetime] = None
    late_penalty_percentage: Optional[float] = Field(None, ge=0, le=100)
    allow_late_submissions: Optional[bool] = None
    max_attempts: Optional[int] = Field(None, ge=1)
    submission_format: Optional[str] = None
    file_size_limit: Optional[int] = Field(None, gt=0)
    is_published: Optional[bool] = None

class AssignmentResponse(AssignmentBase):
    id: int
    professor_id: int
    assigned_date: datetime
    is_published: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    course: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None
    submission_count: Optional[int] = None
    
    class Config:
        from_attributes = True

# Assignment Submission Schemas
class AssignmentSubmissionBase(BaseModel):
    assignment_id: int
    submission_content: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None

class AssignmentSubmissionCreate(AssignmentSubmissionBase):
    pass

class AssignmentSubmissionUpdate(BaseModel):
    submission_content: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    professor_feedback: Optional[str] = None

class AssignmentSubmissionResponse(AssignmentSubmissionBase):
    id: int
    student_id: int
    file_path: Optional[str] = None
    submission_status: SubmissionStatus
    submitted_at: datetime
    is_late: bool
    late_hours: float
    attempt_number: int
    professor_feedback: Optional[str] = None
    feedback_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assignment: Optional[Dict[str, Any]] = None
    student: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Exam Schemas
class ExamBase(BaseModel):
    course_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    exam_type: ExamType
    instructions: Optional[str] = None
    total_points: float = Field(..., gt=0)
    weight_percentage: float = Field(..., ge=0, le=100)
    passing_grade: float = Field(60.0, ge=0, le=100)
    exam_date: date
    start_time: time
    end_time: time
    duration_minutes: Optional[int] = Field(None, gt=0)
    location: Optional[str] = None
    is_online: bool = False
    online_platform: Optional[str] = None
    online_link: Optional[str] = None
    proctoring_required: bool = False
    proctoring_software: Optional[str] = None
    allowed_materials: Optional[str] = None
    restricted_materials: Optional[str] = None
    registration_required: bool = False
    registration_deadline: Optional[datetime] = None

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    exam_type: Optional[ExamType] = None
    instructions: Optional[str] = None
    total_points: Optional[float] = Field(None, gt=0)
    weight_percentage: Optional[float] = Field(None, ge=0, le=100)
    passing_grade: Optional[float] = Field(None, ge=0, le=100)
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    location: Optional[str] = None
    is_online: Optional[bool] = None
    online_platform: Optional[str] = None
    online_link: Optional[str] = None
    proctoring_required: Optional[bool] = None
    proctoring_software: Optional[str] = None
    allowed_materials: Optional[str] = None
    restricted_materials: Optional[str] = None
    registration_required: Optional[bool] = None
    registration_deadline: Optional[datetime] = None
    is_published: Optional[bool] = None

class ExamResponse(ExamBase):
    id: int
    professor_id: int
    is_published: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    course: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None
    registered_students: Optional[int] = None
    
    class Config:
        from_attributes = True

# Exam Session Schemas
class ExamSessionBase(BaseModel):
    exam_id: int
    student_id: int
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    attended: bool = False
    late_arrival_minutes: int = 0
    early_departure_minutes: int = 0
    technical_issues: Optional[str] = None
    issues_resolved: bool = False

class ExamSessionCreate(ExamSessionBase):
    pass

class ExamSessionUpdate(BaseModel):
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    attended: Optional[bool] = None
    late_arrival_minutes: Optional[int] = None
    early_departure_minutes: Optional[int] = None
    technical_issues: Optional[str] = None
    issues_resolved: Optional[bool] = None

class ExamSessionResponse(ExamSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    exam: Optional[Dict[str, Any]] = None
    student: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Grade Schemas
class GradeBase(BaseModel):
    student_id: int
    course_id: int
    assignment_id: Optional[int] = None
    exam_id: Optional[int] = None
    points_earned: float = Field(..., ge=0)
    points_possible: float = Field(..., gt=0)
    percentage: float = Field(..., ge=0, le=100)
    letter_grade: Optional[str] = None
    grade_status: GradeStatus = GradeStatus.DRAFT
    is_late: bool = False
    late_penalty_applied: float = 0.0
    extra_credit: float = 0.0
    curve_adjustment: float = 0.0
    professor_comments: Optional[str] = None
    rubric_scores: Optional[str] = None
    detailed_feedback: Optional[str] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    points_earned: Optional[float] = Field(None, ge=0)
    points_possible: Optional[float] = Field(None, gt=0)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    letter_grade: Optional[str] = None
    grade_status: Optional[GradeStatus] = None
    is_late: Optional[bool] = None
    late_penalty_applied: Optional[float] = None
    extra_credit: Optional[float] = None
    curve_adjustment: Optional[float] = None
    professor_comments: Optional[str] = None
    rubric_scores: Optional[str] = None
    detailed_feedback: Optional[str] = None
    is_modified: Optional[bool] = None
    modification_reason: Optional[str] = None

class GradeResponse(GradeBase):
    id: int
    professor_id: int
    graded_date: datetime
    published_date: Optional[datetime] = None
    is_modified: bool
    modification_reason: Optional[str] = None
    modification_date: Optional[datetime] = None
    modified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None
    course: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None
    assignment: Optional[Dict[str, Any]] = None
    exam: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Gradebook Schemas
class GradebookBase(BaseModel):
    course_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    semester: str = Field(..., min_length=1, max_length=20)
    year: int = Field(..., ge=2000, le=3000)
    grading_scheme: Optional[str] = None
    letter_grade_scale: Optional[str] = None
    pass_fail_threshold: float = Field(60.0, ge=0, le=100)
    drop_lowest_assignments: int = Field(0, ge=0)
    drop_lowest_exams: int = Field(0, ge=0)
    curve_enabled: bool = False
    curve_percentage: float = Field(0.0, ge=0, le=50)
    assignment_weight: float = Field(40.0, ge=0, le=100)
    exam_weight: float = Field(50.0, ge=0, le=100)
    participation_weight: float = Field(10.0, ge=0, le=100)
    allow_student_view: bool = True

class GradebookCreate(GradebookBase):
    pass

class GradebookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    semester: Optional[str] = Field(None, min_length=1, max_length=20)
    year: Optional[int] = Field(None, ge=2000, le=3000)
    grading_scheme: Optional[str] = None
    letter_grade_scale: Optional[str] = None
    pass_fail_threshold: Optional[float] = Field(None, ge=0, le=100)
    drop_lowest_assignments: Optional[int] = Field(None, ge=0)
    drop_lowest_exams: Optional[int] = Field(None, ge=0)
    curve_enabled: Optional[bool] = None
    curve_percentage: Optional[float] = Field(None, ge=0, le=50)
    assignment_weight: Optional[float] = Field(None, ge=0, le=100)
    exam_weight: Optional[float] = Field(None, ge=0, le=100)
    participation_weight: Optional[float] = Field(None, ge=0, le=100)
    allow_student_view: Optional[bool] = None
    is_published: Optional[bool] = None

class GradebookResponse(GradebookBase):
    id: int
    professor_id: int
    is_published: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    course: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None
    total_students: Optional[int] = None
    
    class Config:
        from_attributes = True

# Gradebook Entry Schemas
class GradebookEntryBase(BaseModel):
    gradebook_id: int
    student_id: int
    total_points_earned: float = 0.0
    total_points_possible: float = 0.0
    overall_percentage: float = 0.0
    final_letter_grade: Optional[str] = None
    assignment_average: float = 0.0
    exam_average: float = 0.0
    participation_average: float = 0.0
    assignments_completed: int = 0
    assignments_total: int = 0
    exams_completed: int = 0
    exams_total: int = 0
    is_passing: bool = True
    is_at_risk: bool = False
    needs_attention: bool = False

class GradebookEntryCreate(GradebookEntryBase):
    pass

class GradebookEntryUpdate(BaseModel):
    total_points_earned: Optional[float] = None
    total_points_possible: Optional[float] = None
    overall_percentage: Optional[float] = None
    final_letter_grade: Optional[str] = None
    assignment_average: Optional[float] = None
    exam_average: Optional[float] = None
    participation_average: Optional[float] = None
    assignments_completed: Optional[int] = None
    assignments_total: Optional[int] = None
    exams_completed: Optional[int] = None
    exams_total: Optional[int] = None
    is_passing: Optional[bool] = None
    is_at_risk: Optional[bool] = None
    needs_attention: Optional[bool] = None

class GradebookEntryResponse(GradebookEntryBase):
    id: int
    last_calculated: datetime
    created_at: datetime
    updated_at: datetime
    gradebook: Optional[Dict[str, Any]] = None
    student: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Grade Statistics Schemas
class GradeStatisticsBase(BaseModel):
    course_id: int
    gradebook_id: Optional[int] = None
    total_students: int = 0
    students_passing: int = 0
    students_failing: int = 0
    average_grade: float = 0.0
    median_grade: float = 0.0
    highest_grade: float = 0.0
    lowest_grade: float = 0.0
    standard_deviation: float = 0.0
    a_grades: int = 0
    b_grades: int = 0
    c_grades: int = 0
    d_grades: int = 0
    f_grades: int = 0
    assignment_average: float = 0.0
    exam_average: float = 0.0
    participation_average: float = 0.0

class GradeStatisticsCreate(GradeStatisticsBase):
    pass

class GradeStatisticsResponse(GradeStatisticsBase):
    id: int
    calculated_at: datetime
    created_at: datetime
    course: Optional[Dict[str, Any]] = None
    gradebook: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Grade Modification Schemas
class GradeModificationBase(BaseModel):
    grade_id: int
    old_points: float
    new_points: float
    old_percentage: float
    new_percentage: float
    old_letter_grade: Optional[str] = None
    new_letter_grade: Optional[str] = None
    reason: str = Field(..., min_length=1)
    is_approved: bool = False

class GradeModificationCreate(GradeModificationBase):
    pass

class GradeModificationUpdate(BaseModel):
    reason: Optional[str] = Field(None, min_length=1)
    is_approved: Optional[bool] = None

class GradeModificationResponse(GradeModificationBase):
    id: int
    professor_id: int
    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None
    modified_at: datetime
    created_at: datetime
    grade: Optional[Dict[str, Any]] = None
    professor: Optional[Dict[str, Any]] = None
    approver: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Bulk Operations Schemas
class BulkGradeCreate(BaseModel):
    course_id: int
    assignment_id: Optional[int] = None
    exam_id: Optional[int] = None
    grades: List[Dict[str, Any]] = Field(..., min_items=1)  # List of {student_id, points_earned, comments}

class BulkAssignmentCreate(BaseModel):
    course_id: int
    assignment_template: AssignmentCreate
    due_dates: List[datetime] = Field(..., min_items=1)
    titles: List[str] = Field(..., min_items=1)

# Dashboard and Analytics Schemas
class GradingDashboardSummary(BaseModel):
    professor_id: int
    total_courses: int
    total_assignments: int
    total_exams: int
    pending_grades: int
    overdue_assignments: int
    upcoming_exams: int
    students_at_risk: int
    average_course_grade: float

class CourseGradingSummary(BaseModel):
    course_id: int
    course_name: str
    total_assignments: int
    total_exams: int
    total_students: int
    average_grade: float
    completion_rate: float
    students_passing: int
    students_failing: int

class GradeDistributionReport(BaseModel):
    course_id: int
    course_name: str
    total_students: int
    grade_distribution: Dict[str, int]
    statistics: GradeStatisticsResponse
    grade_trends: List[Dict[str, Any]]

class AssignmentAnalytics(BaseModel):
    assignment_id: int
    assignment_title: str
    total_submissions: int
    submission_rate: float
    average_grade: float
    grade_distribution: Dict[str, int]
    late_submissions: int
    completion_time_stats: Dict[str, float]

class ExamAnalytics(BaseModel):
    exam_id: int
    exam_title: str
    total_registered: int
    attendance_rate: float
    average_grade: float
    grade_distribution: Dict[str, int]
    time_analysis: Dict[str, Any]
    difficulty_analysis: Dict[str, Any]

# Search and Filter Schemas
class AssignmentFilters(BaseModel):
    course_id: Optional[int] = None
    assignment_type: Optional[AssignmentType] = None
    is_published: Optional[bool] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    total_points_min: Optional[float] = None
    total_points_max: Optional[float] = None

class ExamFilters(BaseModel):
    course_id: Optional[int] = None
    exam_type: Optional[ExamType] = None
    is_published: Optional[bool] = None
    exam_date_from: Optional[date] = None
    exam_date_to: Optional[date] = None
    is_online: Optional[bool] = None

class GradeFilters(BaseModel):
    course_id: Optional[int] = None
    student_id: Optional[int] = None
    assignment_id: Optional[int] = None
    exam_id: Optional[int] = None
    grade_status: Optional[GradeStatus] = None
    grade_date_from: Optional[datetime] = None
    grade_date_to: Optional[datetime] = None
    points_min: Optional[float] = None
    points_max: Optional[float] = None

# Validation helpers
class GradingValidator:
    @staticmethod
    def validate_grade_percentage(percentage: float) -> float:
        """Validate grade percentage"""
        if not 0.0 <= percentage <= 100.0:
            raise ValueError("Grade percentage must be between 0.0 and 100.0")
        return percentage
    
    @staticmethod
    def validate_points(points: float) -> float:
        """Validate points"""
        if points < 0:
            raise ValueError("Points cannot be negative")
        return points
    
    @staticmethod
    def validate_weight_percentage(weight: float) -> float:
        """Validate weight percentage"""
        if not 0.0 <= weight <= 100.0:
            raise ValueError("Weight percentage must be between 0.0 and 100.0")
        return weight
    
    @staticmethod
    def validate_exam_times(start_time: time, end_time: time) -> tuple:
        """Validate exam start and end times"""
        if start_time >= end_time:
            raise ValueError("Exam start time must be before end time")
        return start_time, end_time
    
    @staticmethod
    def validate_due_date(due_date: datetime) -> datetime:
        """Validate due date is in the future"""
        if due_date <= datetime.now():
            raise ValueError("Due date must be in the future")
        return due_date
    
    @staticmethod
    def calculate_letter_grade(percentage: float, grade_scale: Optional[Dict[str, float]] = None) -> str:
        """Calculate letter grade from percentage"""
        if grade_scale is None:
            # Default grade scale
            grade_scale = {
                "A+": 97, "A": 93, "A-": 90,
                "B+": 87, "B": 83, "B-": 80,
                "C+": 77, "C": 73, "C-": 70,
                "D+": 67, "D": 63, "D-": 60,
                "F": 0
            }
        
        for grade, threshold in grade_scale.items():
            if percentage >= threshold:
                return grade
        
        return "F"
    
    @staticmethod
    def validate_gradebook_weights(assignment_weight: float, exam_weight: float, participation_weight: float) -> tuple:
        """Validate that gradebook weights sum to 100%"""
        total_weight = assignment_weight + exam_weight + participation_weight
        if abs(total_weight - 100.0) > 0.01:  # Allow small floating point differences
            raise ValueError("Gradebook weights must sum to 100%")
        return assignment_weight, exam_weight, participation_weight
