"""
Models package - Import all models here for database initialization
"""
from .user import User, UserRole
from .student import Student
from .professor import Professor
from .course import Course, student_course_association

__all__ = ["User", "UserRole", "Student", "Professor", "Course", "student_course_association"]
