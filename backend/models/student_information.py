"""
Student Information Management models for attendance, messaging, and directory
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    TARDY = "tardy"

class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"

class MessageType(str, enum.Enum):
    ANNOUNCEMENT = "announcement"
    REMINDER = "reminder"
    ASSIGNMENT = "assignment"
    GRADE = "grade"
    GENERAL = "general"
    URGENT = "urgent"

class MessagePriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Attendance(Base):
    """Attendance tracking model"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Attendance details
    attendance_date = Column(DateTime, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    notes = Column(Text)  # Professor notes about attendance
    late_minutes = Column(Integer, default=0)  # Minutes late if status is late/tardy
    
    # Session information
    session_topic = Column(String(200))  # What was covered in class
    session_duration = Column(Integer)  # Duration in minutes
    
    # Timestamps
    recorded_at = Column(DateTime, default=func.now())
    recorded_by = Column(Integer, ForeignKey("professors.id"), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="attendance_records")
    course = relationship("Course", backref="attendance_records")
    professor = relationship("Professor", backref="attendance_records")

class AttendanceSummary(Base):
    """Attendance summary for students per course"""
    __tablename__ = "attendance_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Attendance statistics
    total_sessions = Column(Integer, default=0)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    excused_count = Column(Integer, default=0)
    tardy_count = Column(Integer, default=0)
    
    # Calculated fields
    attendance_percentage = Column(Float, default=0.0)
    total_late_minutes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="attendance_summaries")
    course = relationship("Course", backref="attendance_summaries")

class Message(Base):
    """Message model for professor-student communication"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)  # Optional for course-specific messages
    
    # Message content
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.GENERAL)
    priority = Column(Enum(MessagePriority), default=MessagePriority.NORMAL)
    
    # Message status
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT)
    is_broadcast = Column(Boolean, default=False)  # True if sent to multiple students
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    sent_at = Column(DateTime)
    scheduled_at = Column(DateTime)  # For scheduled messages
    
    # Relationships
    sender = relationship("Professor", backref="sent_messages")
    course = relationship("Course", backref="messages")
    recipients = relationship("MessageRecipient", back_populates="message")

class MessageRecipient(Base):
    """Message recipients (students who receive messages)"""
    __tablename__ = "message_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Delivery status
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    read_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="recipients")
    student = relationship("Student", backref="received_messages")

class StudentDirectory(Base):
    """Student directory for professor access"""
    __tablename__ = "student_directory"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Contact information
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    address = Column(Text)
    
    # Academic information
    major = Column(String(100))
    year_level = Column(String(20))
    gpa = Column(Float)
    enrollment_status = Column(String(20), default="active")  # active, inactive, graduated, suspended
    
    # Additional information
    advisor_id = Column(Integer, ForeignKey("professors.id"))
    notes = Column(Text)  # Professor notes about student
    
    # Privacy settings
    show_contact_info = Column(Boolean, default=True)
    show_academic_info = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="directory_entry")
    advisor = relationship("Professor", backref="advised_students")

class StudentPerformance(Base):
    """Student performance tracking model"""
    __tablename__ = "student_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Performance metrics
    current_grade = Column(Float)  # Current calculated grade
    participation_score = Column(Float, default=0.0)
    attendance_score = Column(Float, default=0.0)
    assignment_average = Column(Float, default=0.0)
    exam_average = Column(Float, default=0.0)
    
    # Performance indicators
    is_at_risk = Column(Boolean, default=False)  # Academic risk flag
    risk_factors = Column(Text)  # JSON string of risk factors
    improvement_areas = Column(Text)  # Areas needing improvement
    
    # Professor notes
    professor_notes = Column(Text)
    last_contact_date = Column(DateTime)
    next_follow_up = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="performance_records")
    course = relationship("Course", backref="student_performance")

class CommunicationLog(Base):
    """Log of all communications between professor and student"""
    __tablename__ = "communication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    # Communication details
    communication_type = Column(String(50), nullable=False)  # email, message, meeting, call
    subject = Column(String(200))
    content = Column(Text)
    direction = Column(String(10), nullable=False)  # sent, received
    
    # Follow-up information
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # Timestamps
    communication_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    professor = relationship("Professor", backref="communication_logs")
    student = relationship("Student", backref="communication_logs")
    course = relationship("Course", backref="communication_logs")
