"""
Student Information Repository - Data access layer for student information management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from models.student_information import (
    Attendance, AttendanceSummary, Message, MessageRecipient, StudentDirectory,
    StudentPerformance, CommunicationLog, AttendanceStatus, MessageStatus,
    MessageType, MessagePriority
)
from models.student import Student
from models.course import Course
from models.professor import Professor
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, AttendanceSummaryCreate, AttendanceSummaryUpdate,
    MessageCreate, MessageUpdate, MessageRecipientCreate, MessageRecipientUpdate,
    StudentDirectoryCreate, StudentDirectoryUpdate, StudentPerformanceCreate, StudentPerformanceUpdate,
    CommunicationLogCreate, CommunicationLogUpdate, BulkAttendanceCreate, BulkMessageCreate,
    StudentSearchFilters, AttendanceFilters, MessageFilters
)
from datetime import datetime, timedelta
import json

class StudentInformationRepository:
    """Repository for student information data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Attendance Operations
    def create_attendance(self, attendance_data: AttendanceCreate, professor_id: int) -> Attendance:
        """Create a new attendance record"""
        attendance = Attendance(
            **attendance_data.dict(),
            recorded_by=professor_id
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        
        # Update attendance summary
        self._update_attendance_summary(attendance.student_id, attendance.course_id, attendance.attendance_date)
        
        return attendance
    
    def get_attendance_by_id(self, attendance_id: int) -> Optional[Attendance]:
        """Get attendance record by ID"""
        return self.db.query(Attendance).options(
            joinedload(Attendance.student),
            joinedload(Attendance.course),
            joinedload(Attendance.professor)
        ).filter(Attendance.id == attendance_id).first()
    
    def get_attendance_records(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[AttendanceStatus] = None
    ) -> List[Attendance]:
        """Get attendance records with optional filters"""
        query = self.db.query(Attendance).options(
            joinedload(Attendance.student),
            joinedload(Attendance.course),
            joinedload(Attendance.professor)
        )
        
        if course_id:
            query = query.filter(Attendance.course_id == course_id)
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        if professor_id:
            query = query.filter(Attendance.recorded_by == professor_id)
        if date_from:
            query = query.filter(Attendance.attendance_date >= date_from)
        if date_to:
            query = query.filter(Attendance.attendance_date <= date_to)
        if status:
            query = query.filter(Attendance.status == status)
        
        return query.order_by(desc(Attendance.attendance_date)).all()
    
    def update_attendance(self, attendance_id: int, attendance_data: AttendanceUpdate) -> Optional[Attendance]:
        """Update an attendance record"""
        attendance = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance:
            return None
        
        for field, value in attendance_data.dict(exclude_unset=True).items():
            setattr(attendance, field, value)
        
        attendance.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(attendance)
        
        # Update attendance summary
        self._update_attendance_summary(attendance.student_id, attendance.course_id, attendance.attendance_date)
        
        return attendance
    
    def delete_attendance(self, attendance_id: int) -> bool:
        """Delete an attendance record"""
        attendance = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance:
            return False
        
        self.db.delete(attendance)
        self.db.commit()
        
        # Update attendance summary
        self._update_attendance_summary(attendance.student_id, attendance.course_id, attendance.attendance_date)
        
        return True
    
    def create_bulk_attendance(self, bulk_data: BulkAttendanceCreate, professor_id: int) -> List[Attendance]:
        """Create multiple attendance records at once"""
        attendance_records = []
        
        for record_data in bulk_data.attendance_records:
            attendance = Attendance(
                student_id=record_data["student_id"],
                course_id=bulk_data.course_id,
                attendance_date=bulk_data.attendance_date,
                status=record_data["status"],
                notes=record_data.get("notes"),
                late_minutes=record_data.get("late_minutes", 0),
                session_topic=bulk_data.session_topic,
                session_duration=bulk_data.session_duration,
                recorded_by=professor_id
            )
            attendance_records.append(attendance)
            self.db.add(attendance)
        
        self.db.commit()
        
        # Update attendance summaries for all students
        for attendance in attendance_records:
            self.db.refresh(attendance)
            self._update_attendance_summary(attendance.student_id, attendance.course_id, attendance.attendance_date)
        
        return attendance_records
    
    # Attendance Summary Operations
    def get_attendance_summary(
        self,
        student_id: int,
        course_id: int,
        semester: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[AttendanceSummary]:
        """Get attendance summary for a student in a course"""
        query = self.db.query(AttendanceSummary).filter(
            and_(
                AttendanceSummary.student_id == student_id,
                AttendanceSummary.course_id == course_id
            )
        )
        
        if semester:
            query = query.filter(AttendanceSummary.semester == semester)
        if year:
            query = query.filter(AttendanceSummary.year == year)
        
        return query.first()
    
    def get_course_attendance_summaries(self, course_id: int) -> List[AttendanceSummary]:
        """Get attendance summaries for all students in a course"""
        return self.db.query(AttendanceSummary).options(
            joinedload(AttendanceSummary.student),
            joinedload(AttendanceSummary.course)
        ).filter(AttendanceSummary.course_id == course_id).all()
    
    def _update_attendance_summary(self, student_id: int, course_id: int, attendance_date: datetime):
        """Update attendance summary for a student"""
        # Get course info to determine semester/year
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return
        
        semester = course.semester
        year = course.year
        
        # Get or create attendance summary
        summary = self.db.query(AttendanceSummary).filter(
            and_(
                AttendanceSummary.student_id == student_id,
                AttendanceSummary.course_id == course_id,
                AttendanceSummary.semester == semester,
                AttendanceSummary.year == year
            )
        ).first()
        
        if not summary:
            summary = AttendanceSummary(
                student_id=student_id,
                course_id=course_id,
                semester=semester,
                year=year
            )
            self.db.add(summary)
        
        # Recalculate statistics
        attendance_records = self.db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.course_id == course_id,
                Attendance.attendance_date >= datetime(year, 1, 1),
                Attendance.attendance_date < datetime(year + 1, 1, 1)
            )
        ).all()
        
        summary.total_sessions = len(attendance_records)
        summary.present_count = len([r for r in attendance_records if r.status == AttendanceStatus.PRESENT])
        summary.absent_count = len([r for r in attendance_records if r.status == AttendanceStatus.ABSENT])
        summary.late_count = len([r for r in attendance_records if r.status == AttendanceStatus.LATE])
        summary.excused_count = len([r for r in attendance_records if r.status == AttendanceStatus.EXCUSED])
        summary.tardy_count = len([r for r in attendance_records if r.status == AttendanceStatus.TARDY])
        summary.total_late_minutes = sum([r.late_minutes for r in attendance_records])
        
        # Calculate attendance percentage
        if summary.total_sessions > 0:
            present_or_excused = summary.present_count + summary.excused_count
            summary.attendance_percentage = (present_or_excused / summary.total_sessions) * 100
        else:
            summary.attendance_percentage = 0.0
        
        summary.updated_at = datetime.utcnow()
        self.db.commit()
    
    # Message Operations
    def create_message(self, message_data: MessageCreate, sender_id: int) -> Message:
        """Create a new message"""
        message = Message(
            sender_id=sender_id,
            course_id=message_data.course_id,
            subject=message_data.subject,
            content=message_data.content,
            message_type=message_data.message_type,
            priority=message_data.priority,
            is_broadcast=message_data.is_broadcast,
            scheduled_at=message_data.scheduled_at,
            status=MessageStatus.DRAFT
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        return self.db.query(Message).options(
            joinedload(Message.sender),
            joinedload(Message.course),
            joinedload(Message.recipients).joinedload(MessageRecipient.student)
        ).filter(Message.id == message_id).first()
    
    def get_messages(
        self,
        sender_id: Optional[int] = None,
        course_id: Optional[int] = None,
        message_type: Optional[MessageType] = None,
        status: Optional[MessageStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages with optional filters"""
        query = self.db.query(Message).options(
            joinedload(Message.sender),
            joinedload(Message.course),
            joinedload(Message.recipients).joinedload(MessageRecipient.student)
        )
        
        if sender_id:
            query = query.filter(Message.sender_id == sender_id)
        if course_id:
            query = query.filter(Message.course_id == course_id)
        if message_type:
            query = query.filter(Message.message_type == message_type)
        if status:
            query = query.filter(Message.status == status)
        if date_from:
            query = query.filter(Message.created_at >= date_from)
        if date_to:
            query = query.filter(Message.created_at <= date_to)
        
        return query.order_by(desc(Message.created_at)).all()
    
    def update_message(self, message_id: int, message_data: MessageUpdate) -> Optional[Message]:
        """Update a message"""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return None
        
        for field, value in message_data.dict(exclude_unset=True).items():
            setattr(message, field, value)
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def send_message(self, message_id: int) -> Optional[Message]:
        """Send a message (change status to sent)"""
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return None
        
        message.status = MessageStatus.SENT
        message.sent_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    # Message Recipient Operations
    def create_message_recipients(self, message_id: int, recipient_ids: List[int]) -> List[MessageRecipient]:
        """Create message recipients"""
        recipients = []
        
        for student_id in recipient_ids:
            recipient = MessageRecipient(
                message_id=message_id,
                student_id=student_id,
                status=MessageStatus.SENT
            )
            recipients.append(recipient)
            self.db.add(recipient)
        
        self.db.commit()
        
        for recipient in recipients:
            self.db.refresh(recipient)
        
        return recipients
    
    def get_message_recipients(self, message_id: int) -> List[MessageRecipient]:
        """Get all recipients for a message"""
        return self.db.query(MessageRecipient).options(
            joinedload(MessageRecipient.student)
        ).filter(MessageRecipient.message_id == message_id).all()
    
    def update_message_recipient(self, recipient_id: int, recipient_data: MessageRecipientUpdate) -> Optional[MessageRecipient]:
        """Update message recipient status"""
        recipient = self.db.query(MessageRecipient).filter(MessageRecipient.id == recipient_id).first()
        if not recipient:
            return None
        
        for field, value in recipient_data.dict(exclude_unset=True).items():
            setattr(recipient, field, value)
        
        recipient.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(recipient)
        return recipient
    
    # Student Directory Operations
    def create_student_directory_entry(self, directory_data: StudentDirectoryCreate) -> StudentDirectory:
        """Create a student directory entry"""
        directory = StudentDirectory(**directory_data.dict())
        self.db.add(directory)
        self.db.commit()
        self.db.refresh(directory)
        return directory
    
    def get_student_directory_entry(self, student_id: int) -> Optional[StudentDirectory]:
        """Get student directory entry by student ID"""
        return self.db.query(StudentDirectory).options(
            joinedload(StudentDirectory.student),
            joinedload(StudentDirectory.advisor)
        ).filter(StudentDirectory.student_id == student_id).first()
    
    def get_student_directory(
        self,
        name: Optional[str] = None,
        major: Optional[str] = None,
        year_level: Optional[str] = None,
        enrollment_status: Optional[str] = None,
        gpa_min: Optional[float] = None,
        gpa_max: Optional[float] = None,
        is_at_risk: Optional[bool] = None
    ) -> List[StudentDirectory]:
        """Get student directory with optional filters"""
        query = self.db.query(StudentDirectory).options(
            joinedload(StudentDirectory.student),
            joinedload(StudentDirectory.advisor)
        )
        
        if name:
            query = query.join(Student).filter(
                or_(
                    Student.first_name.ilike(f"%{name}%"),
                    Student.last_name.ilike(f"%{name}%")
                )
            )
        if major:
            query = query.filter(StudentDirectory.major.ilike(f"%{major}%"))
        if year_level:
            query = query.filter(StudentDirectory.year_level == year_level)
        if enrollment_status:
            query = query.filter(StudentDirectory.enrollment_status == enrollment_status)
        if gpa_min is not None:
            query = query.filter(StudentDirectory.gpa >= gpa_min)
        if gpa_max is not None:
            query = query.filter(StudentDirectory.gpa <= gpa_max)
        if is_at_risk is not None:
            # This would need to be joined with StudentPerformance table
            pass
        
        return query.order_by(Student.last_name, Student.first_name).all()
    
    def update_student_directory_entry(self, student_id: int, directory_data: StudentDirectoryUpdate) -> Optional[StudentDirectory]:
        """Update student directory entry"""
        directory = self.db.query(StudentDirectory).filter(StudentDirectory.student_id == student_id).first()
        if not directory:
            return None
        
        for field, value in directory_data.dict(exclude_unset=True).items():
            setattr(directory, field, value)
        
        directory.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(directory)
        return directory
    
    # Student Performance Operations
    def create_student_performance(self, performance_data: StudentPerformanceCreate) -> StudentPerformance:
        """Create student performance record"""
        performance = StudentPerformance(**performance_data.dict())
        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)
        return performance
    
    def get_student_performance(self, student_id: int, course_id: int) -> Optional[StudentPerformance]:
        """Get student performance for a specific course"""
        return self.db.query(StudentPerformance).options(
            joinedload(StudentPerformance.student),
            joinedload(StudentPerformance.course)
        ).filter(
            and_(
                StudentPerformance.student_id == student_id,
                StudentPerformance.course_id == course_id
            )
        ).first()
    
    def get_course_student_performance(self, course_id: int) -> List[StudentPerformance]:
        """Get performance records for all students in a course"""
        return self.db.query(StudentPerformance).options(
            joinedload(StudentPerformance.student),
            joinedload(StudentPerformance.course)
        ).filter(StudentPerformance.course_id == course_id).all()
    
    def update_student_performance(self, performance_id: int, performance_data: StudentPerformanceUpdate) -> Optional[StudentPerformance]:
        """Update student performance record"""
        performance = self.db.query(StudentPerformance).filter(StudentPerformance.id == performance_id).first()
        if not performance:
            return None
        
        for field, value in performance_data.dict(exclude_unset=True).items():
            setattr(performance, field, value)
        
        performance.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(performance)
        return performance
    
    def get_students_at_risk(self, course_id: Optional[int] = None) -> List[StudentPerformance]:
        """Get students at academic risk"""
        query = self.db.query(StudentPerformance).options(
            joinedload(StudentPerformance.student),
            joinedload(StudentPerformance.course)
        ).filter(StudentPerformance.is_at_risk == True)
        
        if course_id:
            query = query.filter(StudentPerformance.course_id == course_id)
        
        return query.all()
    
    # Communication Log Operations
    def create_communication_log(self, log_data: CommunicationLogCreate) -> CommunicationLog:
        """Create communication log entry"""
        log = CommunicationLog(**log_data.dict())
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_communication_logs(
        self,
        professor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        course_id: Optional[int] = None,
        communication_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[CommunicationLog]:
        """Get communication logs with optional filters"""
        query = self.db.query(CommunicationLog).options(
            joinedload(CommunicationLog.professor),
            joinedload(CommunicationLog.student),
            joinedload(CommunicationLog.course)
        )
        
        if professor_id:
            query = query.filter(CommunicationLog.professor_id == professor_id)
        if student_id:
            query = query.filter(CommunicationLog.student_id == student_id)
        if course_id:
            query = query.filter(CommunicationLog.course_id == course_id)
        if communication_type:
            query = query.filter(CommunicationLog.communication_type == communication_type)
        if date_from:
            query = query.filter(CommunicationLog.communication_date >= date_from)
        if date_to:
            query = query.filter(CommunicationLog.communication_date <= date_to)
        
        return query.order_by(desc(CommunicationLog.communication_date)).all()
    
    # Dashboard and Analytics Operations
    def get_professor_dashboard_summary(self, professor_id: int) -> Dict[str, Any]:
        """Get professor dashboard summary"""
        # Get total students across all courses
        total_students = self.db.query(Student).join(
            StudentDirectory, Student.id == StudentDirectory.student_id
        ).count()
        
        # Get total courses
        total_courses = self.db.query(Course).filter(Course.professor_id == professor_id).count()
        
        # Get pending messages
        pending_messages = self.db.query(Message).filter(
            and_(
                Message.sender_id == professor_id,
                Message.status == MessageStatus.DRAFT
            )
        ).count()
        
        # Get students at risk
        students_at_risk = self.db.query(StudentPerformance).filter(
            StudentPerformance.is_at_risk == True
        ).count()
        
        # Get attendance alerts (students with low attendance)
        attendance_alerts = self.db.query(AttendanceSummary).filter(
            AttendanceSummary.attendance_percentage < 70.0
        ).count()
        
        # Get recent communications
        recent_communications = self.db.query(CommunicationLog).filter(
            and_(
                CommunicationLog.professor_id == professor_id,
                CommunicationLog.communication_date >= datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "pending_messages": pending_messages,
            "students_at_risk": students_at_risk,
            "attendance_alerts": attendance_alerts,
            "recent_communications": recent_communications
        }
    
    def get_student_dashboard_summary(self, student_id: int) -> Dict[str, Any]:
        """Get student dashboard summary"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {}
        
        # Get courses enrolled
        courses_enrolled = self.db.query(Course).join(
            Course.enrolled_students
        ).filter(Student.id == student_id).count()
        
        # Get average attendance percentage
        attendance_summaries = self.db.query(AttendanceSummary).filter(
            AttendanceSummary.student_id == student_id
        ).all()
        
        total_attendance_percentage = 0.0
        if attendance_summaries:
            total_attendance_percentage = sum([s.attendance_percentage for s in attendance_summaries]) / len(attendance_summaries)
        
        # Get unread messages
        unread_messages = self.db.query(MessageRecipient).filter(
            and_(
                MessageRecipient.student_id == student_id,
                MessageRecipient.status != MessageStatus.READ
            )
        ).count()
        
        # Get performance records
        performance_records = self.db.query(StudentPerformance).filter(
            StudentPerformance.student_id == student_id
        ).all()
        
        is_at_risk = any([p.is_at_risk for p in performance_records])
        average_grade = None
        if performance_records:
            grades = [p.current_grade for p in performance_records if p.current_grade is not None]
            if grades:
                average_grade = sum(grades) / len(grades)
        
        # Get last contact date
        last_contact = self.db.query(CommunicationLog).filter(
            CommunicationLog.student_id == student_id
        ).order_by(desc(CommunicationLog.communication_date)).first()
        
        last_contact_date = last_contact.communication_date if last_contact else None
        
        return {
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "student_email": student.user.email if student.user else "",
            "courses_enrolled": courses_enrolled,
            "total_attendance_percentage": round(total_attendance_percentage, 2),
            "average_grade": round(average_grade, 2) if average_grade else None,
            "unread_messages": unread_messages,
            "upcoming_assignments": 0,  # Would need assignment system
            "is_at_risk": is_at_risk,
            "last_contact_date": last_contact_date
        }
