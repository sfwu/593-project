"""
Pydantic schemas for Student Information Management API request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    TARDY = "tardy"

class MessageStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"

class MessageType(str, Enum):
    ANNOUNCEMENT = "announcement"
    REMINDER = "reminder"
    ASSIGNMENT = "assignment"
    GRADE = "grade"
    GENERAL = "general"
    URGENT = "urgent"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    course_id: int
    attendance_date: datetime
    status: AttendanceStatus
    notes: Optional[str] = None
    late_minutes: int = 0
    session_topic: Optional[str] = None
    session_duration: Optional[int] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    late_minutes: Optional[int] = None
    session_topic: Optional[str] = None
    session_duration: Optional[int] = None

class AttendanceResponse(AttendanceBase):
    id: int
    recorded_at: datetime
    recorded_by: int
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None  # Student details
    course: Optional[Dict[str, Any]] = None  # Course details
    
    class Config:
        from_attributes = True

# Attendance Summary Schemas
class AttendanceSummaryBase(BaseModel):
    student_id: int
    course_id: int
    semester: str
    year: int
    total_sessions: int = 0
    present_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    excused_count: int = 0
    tardy_count: int = 0
    attendance_percentage: float = 0.0
    total_late_minutes: int = 0

class AttendanceSummaryCreate(AttendanceSummaryBase):
    pass

class AttendanceSummaryUpdate(BaseModel):
    total_sessions: Optional[int] = None
    present_count: Optional[int] = None
    absent_count: Optional[int] = None
    late_count: Optional[int] = None
    excused_count: Optional[int] = None
    tardy_count: Optional[int] = None
    attendance_percentage: Optional[float] = None
    total_late_minutes: Optional[int] = None

class AttendanceSummaryResponse(AttendanceSummaryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None
    course: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    course_id: Optional[int] = None
    subject: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.NORMAL
    is_broadcast: bool = False
    scheduled_at: Optional[datetime] = None

class MessageCreate(MessageBase):
    recipient_ids: Optional[List[int]] = None  # For individual messages
    send_to_all_students: bool = False  # For broadcast messages

class MessageUpdate(BaseModel):
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    scheduled_at: Optional[datetime] = None

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    status: MessageStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    sender: Optional[Dict[str, Any]] = None
    course: Optional[Dict[str, Any]] = None
    recipients: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True

# Message Recipient Schemas
class MessageRecipientBase(BaseModel):
    message_id: int
    student_id: int
    status: MessageStatus = MessageStatus.SENT

class MessageRecipientCreate(MessageRecipientBase):
    pass

class MessageRecipientUpdate(BaseModel):
    status: Optional[MessageStatus] = None
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class MessageRecipientResponse(MessageRecipientBase):
    id: int
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Student Directory Schemas
class StudentDirectoryBase(BaseModel):
    student_id: int
    email: str
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    address: Optional[str] = None
    major: Optional[str] = None
    year_level: Optional[str] = None
    gpa: Optional[float] = None
    enrollment_status: str = "active"
    advisor_id: Optional[int] = None
    notes: Optional[str] = None
    show_contact_info: bool = True
    show_academic_info: bool = True

class StudentDirectoryCreate(StudentDirectoryBase):
    pass

class StudentDirectoryUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    address: Optional[str] = None
    major: Optional[str] = None
    year_level: Optional[str] = None
    gpa: Optional[float] = None
    enrollment_status: Optional[str] = None
    advisor_id: Optional[int] = None
    notes: Optional[str] = None
    show_contact_info: Optional[bool] = None
    show_academic_info: Optional[bool] = None

class StudentDirectoryResponse(StudentDirectoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None
    advisor: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Student Performance Schemas
class StudentPerformanceBase(BaseModel):
    student_id: int
    course_id: int
    current_grade: Optional[float] = None
    participation_score: float = 0.0
    attendance_score: float = 0.0
    assignment_average: float = 0.0
    exam_average: float = 0.0
    is_at_risk: bool = False
    risk_factors: Optional[str] = None
    improvement_areas: Optional[str] = None
    professor_notes: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

class StudentPerformanceCreate(StudentPerformanceBase):
    pass

class StudentPerformanceUpdate(BaseModel):
    current_grade: Optional[float] = None
    participation_score: Optional[float] = None
    attendance_score: Optional[float] = None
    assignment_average: Optional[float] = None
    exam_average: Optional[float] = None
    is_at_risk: Optional[bool] = None
    risk_factors: Optional[str] = None
    improvement_areas: Optional[str] = None
    professor_notes: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

class StudentPerformanceResponse(StudentPerformanceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    student: Optional[Dict[str, Any]] = None
    course: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Communication Log Schemas
class CommunicationLogBase(BaseModel):
    professor_id: int
    student_id: int
    course_id: Optional[int] = None
    communication_type: str = Field(..., min_length=1, max_length=50)
    subject: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    direction: str = Field(..., pattern="^(sent|received)$")
    requires_follow_up: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None

class CommunicationLogCreate(CommunicationLogBase):
    pass

class CommunicationLogUpdate(BaseModel):
    communication_type: Optional[str] = Field(None, min_length=1, max_length=50)
    subject: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    direction: Optional[str] = Field(None, pattern="^(sent|received)$")
    requires_follow_up: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None

class CommunicationLogResponse(CommunicationLogBase):
    id: int
    communication_date: datetime
    created_at: datetime
    professor: Optional[Dict[str, Any]] = None
    student: Optional[Dict[str, Any]] = None
    course: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Bulk Operations Schemas
class BulkAttendanceCreate(BaseModel):
    course_id: int
    attendance_date: datetime
    session_topic: Optional[str] = None
    session_duration: Optional[int] = None
    attendance_records: List[Dict[str, Any]]  # List of {student_id, status, notes, late_minutes}

class BulkMessageCreate(BaseModel):
    course_id: Optional[int] = None
    subject: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.NORMAL
    recipient_ids: List[int] = Field(..., min_items=1)
    scheduled_at: Optional[datetime] = None

# Dashboard and Summary Schemas
class StudentDashboardSummary(BaseModel):
    student_id: int
    student_name: str
    student_email: str
    courses_enrolled: int
    total_attendance_percentage: float
    average_grade: Optional[float] = None
    unread_messages: int
    upcoming_assignments: int
    is_at_risk: bool
    last_contact_date: Optional[datetime] = None

class ProfessorDashboardSummary(BaseModel):
    professor_id: int
    total_students: int
    total_courses: int
    pending_messages: int
    students_at_risk: int
    attendance_alerts: int
    recent_communications: int

class AttendanceReport(BaseModel):
    course_id: int
    course_name: str
    semester: str
    year: int
    total_sessions: int
    attendance_summary: List[AttendanceSummaryResponse]
    overall_attendance_percentage: float
    students_at_risk: List[Dict[str, Any]]

class MessageReport(BaseModel):
    total_messages_sent: int
    messages_by_type: Dict[str, int]
    messages_by_priority: Dict[str, int]
    delivery_stats: Dict[str, int]
    recent_messages: List[MessageResponse]

# Search and Filter Schemas
class StudentSearchFilters(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    year_level: Optional[str] = None
    enrollment_status: Optional[str] = None
    gpa_min: Optional[float] = None
    gpa_max: Optional[float] = None
    is_at_risk: Optional[bool] = None

class AttendanceFilters(BaseModel):
    course_id: Optional[int] = None
    student_id: Optional[int] = None
    status: Optional[AttendanceStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    semester: Optional[str] = None
    year: Optional[int] = None

class MessageFilters(BaseModel):
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    status: Optional[MessageStatus] = None
    course_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_broadcast: Optional[bool] = None

# Validation helpers
class StudentInformationValidator:
    @staticmethod
    def validate_attendance_percentage(percentage: float) -> float:
        """Validate attendance percentage"""
        if not 0.0 <= percentage <= 100.0:
            raise ValueError("Attendance percentage must be between 0.0 and 100.0")
        return percentage
    
    @staticmethod
    def validate_grade(grade: float) -> float:
        """Validate grade"""
        if not 0.0 <= grade <= 100.0:
            raise ValueError("Grade must be between 0.0 and 100.0")
        return grade
    
    @staticmethod
    def validate_late_minutes(minutes: int) -> int:
        """Validate late minutes"""
        if minutes < 0:
            raise ValueError("Late minutes cannot be negative")
        return minutes
