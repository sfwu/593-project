"""
Database models for the Academic Information Management System
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum
from sqlalchemy import Enum

# Association table for student-course enrollment
student_course_association = Table(
    'enrollments',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('enrollment_date', DateTime, default=func.now()),
    Column('status', String(20), default='enrolled')  # enrolled, dropped, completed
)

class UserRole(enum.Enum):
    STUDENT = "student"
    PROFESSOR = "professor"

class User(Base):
    """Base User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(DateTime)
    enrollment_date = Column(DateTime, default=func.now())
    graduation_date = Column(DateTime)
    gpa = Column(String(5))
    major = Column(String(100))
    year_level = Column(String(20))  # Freshman, Sophomore, Junior, Senior
    
    # Relationships
    user = relationship("User", backref="student_profile")
    enrolled_courses = relationship("Course", secondary=student_course_association, back_populates="enrolled_students")

class Professor(Base):
    """Professor model"""
    __tablename__ = "professors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    professor_id = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    office_location = Column(String(100))
    office_hours = Column(Text)
    department = Column(String(100), nullable=False)
    title = Column(String(100))  # Assistant Professor, Associate Professor, etc.
    specialization = Column(Text)
    
    # Relationships
    user = relationship("User", backref="professor_profile")
    courses = relationship("Course", back_populates="professor")

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
