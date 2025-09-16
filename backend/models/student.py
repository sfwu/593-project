"""
Student model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base

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
    enrolled_courses = relationship("Course", secondary="enrollments", back_populates="enrolled_students")
