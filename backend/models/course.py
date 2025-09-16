"""
Course model and enrollment associations
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

# Association table for student-course enrollment
student_course_association = Table(
    'enrollments',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('enrollment_date', DateTime, default=func.now()),
    Column('status', String(20), default='enrolled')  # enrolled, dropped, completed
)

class Course(Base):
    """Course model"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    credits = Column(Integer, default=3)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    department = Column(String(100), nullable=False)
    semester = Column(String(20), nullable=False)  # Fall 2024, Spring 2025, etc.
    year = Column(Integer, nullable=False)
    max_enrollment = Column(Integer, default=30)
    prerequisites = Column(Text)  # JSON string of prerequisite course codes
    schedule = Column(Text)  # JSON string with days and times
    syllabus = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    professor = relationship("Professor", back_populates="courses")
    enrolled_students = relationship("Student", secondary=student_course_association, back_populates="enrolled_courses")
