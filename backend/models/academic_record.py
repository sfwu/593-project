"""
Academic Record models for grades, transcripts, and academic progress
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class GradeStatus(str, enum.Enum):
    PENDING = "pending"
    GRADED = "graded"
    INCOMPLETE = "incomplete"
    WITHDRAWN = "withdrawn"

class TranscriptStatus(str, enum.Enum):
    DRAFT = "draft"
    OFFICIAL = "official"
    ARCHIVED = "archived"

class AcademicRecord(Base):
    """Academic Record model - stores individual course grades"""
    __tablename__ = "academic_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(String(20), nullable=False)  # Fall 2024, Spring 2025, etc.
    year = Column(Integer, nullable=False)
    
    # Grade information
    letter_grade = Column(String(2))  # A, B+, B, C+, C, D, F
    numeric_grade = Column(Float)  # 4.0, 3.5, 3.0, etc.
    percentage_grade = Column(Float)  # 95.5, 87.2, etc.
    credits_earned = Column(Integer, nullable=False, default=0)
    credits_attempted = Column(Integer, nullable=False, default=0)
    
    # Status and metadata
    status = Column(Enum(GradeStatus), default=GradeStatus.PENDING)
    grade_date = Column(DateTime)
    professor_notes = Column(Text)
    student_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="academic_records")
    course = relationship("Course", backref="academic_records")

class Transcript(Base):
    """Transcript model - official academic transcripts"""
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Transcript metadata
    transcript_type = Column(String(20), default="official")  # official, unofficial
    status = Column(Enum(TranscriptStatus), default=TranscriptStatus.DRAFT)
    generated_date = Column(DateTime, default=func.now())
    requested_date = Column(DateTime, default=func.now())
    
    # Academic summary
    total_credits_earned = Column(Integer, default=0)
    total_credits_attempted = Column(Integer, default=0)
    cumulative_gpa = Column(Float, default=0.0)
    major_gpa = Column(Float, default=0.0)
    
    # File information
    file_path = Column(String(500))  # Path to generated PDF
    file_hash = Column(String(64))  # For integrity verification
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="transcripts")

class AcademicProgress(Base):
    """Academic Progress model - tracks degree requirements and completion status"""
    __tablename__ = "academic_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Degree information
    degree_program = Column(String(100), nullable=False)  # Bachelor of Science in Computer Science
    major = Column(String(100), nullable=False)
    concentration = Column(String(100))  # Optional concentration/specialization
    catalog_year = Column(Integer, nullable=False)  # Academic year when student started
    
    # Credit requirements
    total_credits_required = Column(Integer, default=120)
    major_credits_required = Column(Integer, default=60)
    general_education_credits_required = Column(Integer, default=30)
    elective_credits_required = Column(Integer, default=30)
    
    # Current progress
    total_credits_earned = Column(Integer, default=0)
    major_credits_earned = Column(Integer, default=0)
    general_education_credits_earned = Column(Integer, default=0)
    elective_credits_earned = Column(Integer, default=0)
    
    # GPA tracking
    cumulative_gpa = Column(Float, default=0.0)
    major_gpa = Column(Float, default=0.0)
    semester_gpa = Column(Float, default=0.0)
    
    # Status tracking
    is_on_track = Column(Boolean, default=True)
    expected_graduation_date = Column(DateTime)
    actual_graduation_date = Column(DateTime)
    
    # Requirements tracking (JSON strings for flexibility)
    completed_requirements = Column(Text)  # JSON list of completed requirement IDs
    remaining_requirements = Column(Text)  # JSON list of remaining requirement IDs
    warnings = Column(Text)  # JSON list of academic warnings/issues
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="academic_progress")

class SemesterGPA(Base):
    """Semester GPA tracking model"""
    __tablename__ = "semester_gpa"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    semester = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    
    # GPA calculations
    semester_gpa = Column(Float, default=0.0)
    credits_earned = Column(Integer, default=0)
    credits_attempted = Column(Integer, default=0)
    quality_points = Column(Float, default=0.0)
    
    # Course count
    courses_completed = Column(Integer, default=0)
    courses_attempted = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="semester_gpas")

