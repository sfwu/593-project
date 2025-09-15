"""
Models package - Import all models here for database initialization
"""
from .student import User, Student, Professor, Course, UserRole, student_course_association

__all__ = ["User", "Student", "Professor", "Course", "UserRole", "student_course_association"]
