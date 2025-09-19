"""
Student Information Service - Business logic layer for student information management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from repositories.student_information_repository import StudentInformationRepository
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceSummaryResponse,
    MessageCreate, MessageUpdate, MessageResponse, MessageRecipientResponse,
    StudentDirectoryCreate, StudentDirectoryUpdate, StudentDirectoryResponse,
    StudentPerformanceCreate, StudentPerformanceUpdate, StudentPerformanceResponse,
    CommunicationLogCreate, CommunicationLogResponse, BulkAttendanceCreate, BulkMessageCreate,
    StudentSearchFilters, AttendanceFilters, MessageFilters, StudentDashboardSummary,
    ProfessorDashboardSummary, AttendanceReport, MessageReport
)
from models.student_information import Attendance, Message, StudentPerformance, AttendanceStatus, MessageStatus, MessageType, MessagePriority
from models.student import Student
from models.course import Course
from models.professor import Professor
from datetime import datetime, timedelta
import json

class StudentInformationService:
    """Service layer for student information business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = StudentInformationRepository(db)
    
    # Attendance Management Operations
    def create_attendance(self, attendance_data: AttendanceCreate, professor_id: int) -> AttendanceResponse:
        """Create a new attendance record with validation"""
        # Validate attendance data
        self._validate_attendance_data(attendance_data)
        
        # Create the attendance record
        attendance = self.repository.create_attendance(attendance_data, professor_id)
        
        # Log the communication
        self._log_attendance_communication(professor_id, attendance.student_id, attendance.course_id, attendance)
        
        return AttendanceResponse.from_orm(attendance)
    
    def get_attendance_records(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[AttendanceStatus] = None
    ) -> List[AttendanceResponse]:
        """Get attendance records with optional filtering"""
        records = self.repository.get_attendance_records(
            course_id, student_id, professor_id, date_from, date_to, status
        )
        return [AttendanceResponse.from_orm(record) for record in records]
    
    def update_attendance(self, attendance_id: int, attendance_data: AttendanceUpdate, professor_id: int) -> Optional[AttendanceResponse]:
        """Update an attendance record"""
        attendance = self.repository.update_attendance(attendance_id, attendance_data)
        if not attendance:
            return None
        
        # Log the communication
        self._log_attendance_communication(professor_id, attendance.student_id, attendance.course_id, attendance, "updated")
        
        return AttendanceResponse.from_orm(attendance)
    
    def create_bulk_attendance(self, bulk_data: BulkAttendanceCreate, professor_id: int) -> List[AttendanceResponse]:
        """Create multiple attendance records at once"""
        # Validate bulk attendance data
        self._validate_bulk_attendance_data(bulk_data)
        
        # Create attendance records
        attendance_records = self.repository.create_bulk_attendance(bulk_data, professor_id)
        
        # Log communications for each record
        for attendance in attendance_records:
            self._log_attendance_communication(professor_id, attendance.student_id, attendance.course_id, attendance)
        
        return [AttendanceResponse.from_orm(record) for record in attendance_records]
    
    def get_attendance_summary(self, student_id: int, course_id: int) -> Optional[AttendanceSummaryResponse]:
        """Get attendance summary for a student in a course"""
        summary = self.repository.get_attendance_summary(student_id, course_id)
        if not summary:
            return None
        
        return AttendanceSummaryResponse.from_orm(summary)
    
    def get_course_attendance_report(self, course_id: int) -> AttendanceReport:
        """Generate comprehensive attendance report for a course"""
        # Get course information
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError("Course not found")
        
        # Get attendance summaries for all students
        summaries = self.repository.get_course_attendance_summaries(course_id)
        
        # Calculate overall statistics
        total_students = len(summaries)
        if total_students > 0:
            overall_attendance_percentage = sum([s.attendance_percentage for s in summaries]) / total_students
        else:
            overall_attendance_percentage = 0.0
        
        # Identify students at risk (attendance < 70%)
        students_at_risk = [
            {
                "student_id": s.student_id,
                "student_name": f"{s.student.first_name} {s.student.last_name}" if s.student else "Unknown",
                "attendance_percentage": s.attendance_percentage,
                "total_absences": s.absent_count
            }
            for s in summaries if s.attendance_percentage < 70.0
        ]
        
        return AttendanceReport(
            course_id=course_id,
            course_name=course.title,
            semester=course.semester,
            year=course.year,
            total_sessions=summaries[0].total_sessions if summaries else 0,
            attendance_summary=[AttendanceSummaryResponse.from_orm(s) for s in summaries],
            overall_attendance_percentage=round(overall_attendance_percentage, 2),
            students_at_risk=students_at_risk
        )
    
    # Message Management Operations
    def create_message(self, message_data: MessageCreate, sender_id: int) -> MessageResponse:
        """Create a new message"""
        # Validate message data
        self._validate_message_data(message_data)
        
        # Create the message
        message = self.repository.create_message(message_data, sender_id)
        
        # Create recipients if specified
        if message_data.recipient_ids:
            self.repository.create_message_recipients(message.id, message_data.recipient_ids)
        
        return MessageResponse.from_orm(message)
    
    def send_message(self, message_id: int, sender_id: int) -> Optional[MessageResponse]:
        """Send a message"""
        # Verify message belongs to sender
        message = self.repository.get_message_by_id(message_id)
        if not message or message.sender_id != sender_id:
            return None
        
        # Send the message
        sent_message = self.repository.send_message(message_id)
        if not sent_message:
            return None
        
        # Log communication for each recipient
        recipients = self.repository.get_message_recipients(message_id)
        for recipient in recipients:
            self._log_message_communication(sender_id, recipient.student_id, message.course_id, message)
        
        return MessageResponse.from_orm(sent_message)
    
    def get_messages(
        self,
        sender_id: Optional[int] = None,
        course_id: Optional[int] = None,
        message_type: Optional[MessageType] = None,
        status: Optional[MessageStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[MessageResponse]:
        """Get messages with optional filtering"""
        messages = self.repository.get_messages(
            sender_id, course_id, message_type, status, date_from, date_to
        )
        return [MessageResponse.from_orm(message) for message in messages]
    
    def update_message(self, message_id: int, message_data: MessageUpdate, sender_id: int) -> Optional[MessageResponse]:
        """Update a message (only if it's a draft)"""
        message = self.repository.get_message_by_id(message_id)
        if not message or message.sender_id != sender_id or message.status != MessageStatus.DRAFT:
            return None
        
        updated_message = self.repository.update_message(message_id, message_data)
        if not updated_message:
            return None
        
        return MessageResponse.from_orm(updated_message)
    
    def get_message_recipients(self, message_id: int) -> List[MessageRecipientResponse]:
        """Get all recipients for a message"""
        recipients = self.repository.get_message_recipients(message_id)
        return [MessageRecipientResponse.from_orm(recipient) for recipient in recipients]
    
    def mark_message_as_read(self, message_id: int, student_id: int) -> Optional[MessageRecipientResponse]:
        """Mark a message as read by a student"""
        # Find the recipient record
        recipients = self.repository.get_message_recipients(message_id)
        recipient = next((r for r in recipients if r.student_id == student_id), None)
        
        if not recipient:
            return None
        
        # Update status
        from schemas.student_information_schemas import MessageRecipientUpdate
        updated_recipient = self.repository.update_message_recipient(
            recipient.id,
            MessageRecipientUpdate(status=MessageStatus.READ, read_at=datetime.utcnow())
        )
        
        return MessageRecipientResponse.from_orm(updated_recipient) if updated_recipient else None
    
    def get_message_report(self, professor_id: int, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> MessageReport:
        """Generate message report for a professor"""
        messages = self.repository.get_messages(sender_id=professor_id, date_from=date_from, date_to=date_to)
        
        # Calculate statistics
        total_messages = len(messages)
        messages_by_type = {}
        messages_by_priority = {}
        delivery_stats = {"sent": 0, "delivered": 0, "read": 0}
        
        for message in messages:
            # Count by type
            msg_type = message.message_type.value
            messages_by_type[msg_type] = messages_by_type.get(msg_type, 0) + 1
            
            # Count by priority
            priority = message.priority.value
            messages_by_priority[priority] = messages_by_priority.get(priority, 0) + 1
            
            # Count delivery stats
            if message.status == MessageStatus.SENT:
                delivery_stats["sent"] += 1
            elif message.status == MessageStatus.DELIVERED:
                delivery_stats["delivered"] += 1
            elif message.status == MessageStatus.READ:
                delivery_stats["read"] += 1
        
        # Get recent messages (last 10)
        recent_messages = [MessageResponse.from_orm(msg) for msg in messages[:10]]
        
        return MessageReport(
            total_messages_sent=total_messages,
            messages_by_type=messages_by_type,
            messages_by_priority=messages_by_priority,
            delivery_stats=delivery_stats,
            recent_messages=recent_messages
        )
    
    # Student Directory Operations
    def get_student_directory(
        self,
        name: Optional[str] = None,
        major: Optional[str] = None,
        year_level: Optional[str] = None,
        enrollment_status: Optional[str] = None,
        gpa_min: Optional[float] = None,
        gpa_max: Optional[float] = None,
        is_at_risk: Optional[bool] = None
    ) -> List[StudentDirectoryResponse]:
        """Get student directory with optional filtering"""
        directory_entries = self.repository.get_student_directory(
            name, major, year_level, enrollment_status, gpa_min, gpa_max, is_at_risk
        )
        return [StudentDirectoryResponse.from_orm(entry) for entry in directory_entries]
    
    def get_student_directory_entry(self, student_id: int) -> Optional[StudentDirectoryResponse]:
        """Get specific student directory entry"""
        entry = self.repository.get_student_directory_entry(student_id)
        if not entry:
            return None
        
        return StudentDirectoryResponse.from_orm(entry)
    
    def update_student_directory_entry(self, student_id: int, directory_data: StudentDirectoryUpdate) -> Optional[StudentDirectoryResponse]:
        """Update student directory entry"""
        entry = self.repository.update_student_directory_entry(student_id, directory_data)
        if not entry:
            return None
        
        return StudentDirectoryResponse.from_orm(entry)
    
    # Student Performance Operations
    def get_student_performance(self, student_id: int, course_id: int) -> Optional[StudentPerformanceResponse]:
        """Get student performance for a specific course"""
        performance = self.repository.get_student_performance(student_id, course_id)
        if not performance:
            return None
        
        return StudentPerformanceResponse.from_orm(performance)
    
    def get_course_student_performance(self, course_id: int) -> List[StudentPerformanceResponse]:
        """Get performance records for all students in a course"""
        performances = self.repository.get_course_student_performance(course_id)
        return [StudentPerformanceResponse.from_orm(perf) for perf in performances]
    
    def update_student_performance(self, performance_id: int, performance_data: StudentPerformanceUpdate, professor_id: int) -> Optional[StudentPerformanceResponse]:
        """Update student performance record"""
        performance = self.repository.update_student_performance(performance_id, performance_data)
        if not performance:
            return None
        
        # Log the communication
        self._log_performance_communication(professor_id, performance.student_id, performance.course_id, performance)
        
        return StudentPerformanceResponse.from_orm(performance)
    
    def get_students_at_risk(self, course_id: Optional[int] = None) -> List[StudentPerformanceResponse]:
        """Get students at academic risk"""
        at_risk_students = self.repository.get_students_at_risk(course_id)
        return [StudentPerformanceResponse.from_orm(student) for student in at_risk_students]
    
    def assess_student_risk(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """Assess if a student is at academic risk"""
        # Get performance record
        performance = self.repository.get_student_performance(student_id, course_id)
        if not performance:
            return {"is_at_risk": False, "risk_factors": [], "recommendations": []}
        
        # Get attendance summary
        attendance_summary = self.repository.get_attendance_summary(student_id, course_id)
        
        risk_factors = []
        recommendations = []
        
        # Check attendance
        if attendance_summary and attendance_summary.attendance_percentage < 70.0:
            risk_factors.append("Low attendance")
            recommendations.append("Schedule meeting to discuss attendance issues")
        
        # Check grades
        if performance.current_grade and performance.current_grade < 60.0:
            risk_factors.append("Low academic performance")
            recommendations.append("Provide additional academic support")
        
        # Check participation
        if performance.participation_score < 50.0:
            risk_factors.append("Low participation")
            recommendations.append("Encourage more active participation in class")
        
        # Check assignment performance
        if performance.assignment_average < 60.0:
            risk_factors.append("Poor assignment performance")
            recommendations.append("Review assignment requirements and provide feedback")
        
        is_at_risk = len(risk_factors) > 0
        
        # Update performance record if risk status changed
        if performance.is_at_risk != is_at_risk:
            from schemas.student_information_schemas import StudentPerformanceUpdate
            self.repository.update_student_performance(
                performance.id,
                StudentPerformanceUpdate(
                    is_at_risk=is_at_risk,
                    risk_factors=json.dumps(risk_factors),
                    improvement_areas=json.dumps(recommendations)
                )
            )
        
        return {
            "is_at_risk": is_at_risk,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "attendance_percentage": attendance_summary.attendance_percentage if attendance_summary else 0.0,
            "current_grade": performance.current_grade,
            "participation_score": performance.participation_score
        }
    
    # Dashboard Operations
    def get_professor_dashboard_summary(self, professor_id: int) -> ProfessorDashboardSummary:
        """Get professor dashboard summary"""
        summary_data = self.repository.get_professor_dashboard_summary(professor_id)
        
        return ProfessorDashboardSummary(
            professor_id=professor_id,
            total_students=summary_data["total_students"],
            total_courses=summary_data["total_courses"],
            pending_messages=summary_data["pending_messages"],
            students_at_risk=summary_data["students_at_risk"],
            attendance_alerts=summary_data["attendance_alerts"],
            recent_communications=summary_data["recent_communications"]
        )
    
    def get_student_dashboard_summary(self, student_id: int) -> StudentDashboardSummary:
        """Get student dashboard summary"""
        summary_data = self.repository.get_student_dashboard_summary(student_id)
        
        return StudentDashboardSummary(
            student_id=summary_data["student_id"],
            student_name=summary_data["student_name"],
            student_email=summary_data["student_email"],
            courses_enrolled=summary_data["courses_enrolled"],
            total_attendance_percentage=summary_data["total_attendance_percentage"],
            average_grade=summary_data["average_grade"],
            unread_messages=summary_data["unread_messages"],
            upcoming_assignments=summary_data["upcoming_assignments"],
            is_at_risk=summary_data["is_at_risk"],
            last_contact_date=summary_data["last_contact_date"]
        )
    
    # Communication Log Operations
    def get_communication_logs(
        self,
        professor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None,
        communication_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[CommunicationLogResponse]:
        """Get communication logs with optional filtering"""
        logs = self.repository.get_communication_logs(
            professor_id, student_id, course_id, communication_type, date_from, date_to
        )
        return [CommunicationLogResponse.from_orm(log) for log in logs]
    
    def create_communication_log(self, log_data: CommunicationLogCreate) -> CommunicationLogResponse:
        """Create a communication log entry"""
        log = self.repository.create_communication_log(log_data)
        return CommunicationLogResponse.from_orm(log)
    
    # Private helper methods
    def _validate_attendance_data(self, attendance_data: AttendanceCreate) -> None:
        """Validate attendance data"""
        if attendance_data.late_minutes < 0:
            raise ValueError("Late minutes cannot be negative")
        
        if attendance_data.session_duration and attendance_data.session_duration < 0:
            raise ValueError("Session duration cannot be negative")
    
    def _validate_bulk_attendance_data(self, bulk_data: BulkAttendanceCreate) -> None:
        """Validate bulk attendance data"""
        if not bulk_data.attendance_records:
            raise ValueError("Attendance records cannot be empty")
        
        for record in bulk_data.attendance_records:
            if "student_id" not in record or "status" not in record:
                raise ValueError("Each attendance record must have student_id and status")
            
            if record.get("late_minutes", 0) < 0:
                raise ValueError("Late minutes cannot be negative")
    
    def _validate_message_data(self, message_data: MessageCreate) -> None:
        """Validate message data"""
        if message_data.is_broadcast and not message_data.recipient_ids:
            raise ValueError("Broadcast messages must have recipient IDs")
        
        if message_data.scheduled_at and message_data.scheduled_at < datetime.utcnow():
            raise ValueError("Scheduled time cannot be in the past")
    
    def _log_attendance_communication(self, professor_id: int, student_id: int, course_id: int, attendance: Attendance, action: str = "recorded") -> None:
        """Log attendance-related communication"""
        log_data = CommunicationLogCreate(
            professor_id=professor_id,
            student_id=student_id,
            course_id=course_id,
            communication_type="attendance",
            subject=f"Attendance {action}",
            content=f"Attendance {action} for {attendance.attendance_date.strftime('%Y-%m-%d')} - Status: {attendance.status.value}",
            direction="sent"
        )
        self.repository.create_communication_log(log_data)
    
    def _log_message_communication(self, professor_id: int, student_id: int, course_id: Optional[int], message: Message) -> None:
        """Log message communication"""
        log_data = CommunicationLogCreate(
            professor_id=professor_id,
            student_id=student_id,
            course_id=course_id,
            communication_type="message",
            subject=message.subject,
            content=message.content[:200] + "..." if len(message.content) > 200 else message.content,
            direction="sent"
        )
        self.repository.create_communication_log(log_data)
    
    def _log_performance_communication(self, professor_id: int, student_id: int, course_id: int, performance: StudentPerformance) -> None:
        """Log performance-related communication"""
        log_data = CommunicationLogCreate(
            professor_id=professor_id,
            student_id=student_id,
            course_id=course_id,
            communication_type="performance",
            subject="Performance Update",
            content=f"Performance record updated - Grade: {performance.current_grade}, At Risk: {performance.is_at_risk}",
            direction="sent"
        )
        self.repository.create_communication_log(log_data)
