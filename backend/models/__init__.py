"""
Models package - Import all models here for database initialization
"""
from .user import User, UserRole
from .student import Student
from .professor import Professor
from .course import Course, student_course_association
from .academic_record import AcademicRecord, Transcript, AcademicProgress, SemesterGPA, GradeStatus, TranscriptStatus
from .student_information import (
    Attendance, AttendanceSummary, Message, MessageRecipient, StudentDirectory,
    StudentPerformance, CommunicationLog, AttendanceStatus, MessageStatus,
    MessageType, MessagePriority
)
from .grading_assessment import (
    Assignment, AssignmentSubmission, Exam, ExamSession, Grade, Gradebook,
    GradebookEntry, GradeStatistics, GradeModification, AssignmentType,
    ExamType, GradeStatus, SubmissionStatus
)

__all__ = [
    "User", "UserRole", "Student", "Professor", "Course", "student_course_association",
    "AcademicRecord", "Transcript", "AcademicProgress", "SemesterGPA", "GradeStatus", "TranscriptStatus",
    "Attendance", "AttendanceSummary", "Message", "MessageRecipient", "StudentDirectory",
    "StudentPerformance", "CommunicationLog", "AttendanceStatus", "MessageStatus",
    "MessageType", "MessagePriority",
    "Assignment", "AssignmentSubmission", "Exam", "ExamSession", "Grade", "Gradebook",
    "GradebookEntry", "GradeStatistics", "GradeModification", "AssignmentType",
    "ExamType", "GradeStatus", "SubmissionStatus"
]
