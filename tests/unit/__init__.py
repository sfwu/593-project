# Unit tests package with mock data utilities

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from sqlalchemy.orm import Session
from datetime import datetime
from models import User, Student, Professor, Course, UserRole, student_course_association
from config.auth import get_password_hash

class MockDataManager:
    """Manages mock data for unit tests"""
    
    def __init__(self):
        self.created_users = []
        self.created_students = []
        self.created_professors = []
        self.created_courses = []
        self.created_enrollments = []
    
    def create_mock_user(self, db: Session, email: str, role: UserRole, **kwargs) -> User:
        """Create a mock user"""
        user = User(
            email=email,
            hashed_password=get_password_hash("password123"),
            role=role,
            is_active=True,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        self.created_users.append(user)
        return user
    
    def create_mock_student(self, db: Session, user: User, **kwargs) -> Student:
        """Create a mock student"""
        defaults = {
            'student_id': f'STU{user.id:03d}',
            'first_name': 'John',
            'last_name': 'Doe',
            'major': 'Computer Science',
            'year_level': 'Junior',
            'gpa': 3.5,
            'phone': '555-0123',
            'address': '123 Main St'
        }
        defaults.update(kwargs)
        
        student = Student(
            user_id=user.id,
            **defaults
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        self.created_students.append(student)
        return student
    
    def create_mock_professor(self, db: Session, user: User, **kwargs) -> Professor:
        """Create a mock professor"""
        defaults = {
            'professor_id': f'PROF{user.id:03d}',
            'first_name': 'Dr. Jane',
            'last_name': 'Smith',
            'department': 'Computer Science',
            'office_location': 'Room 101',
            'office_hours': 'MWF 2-4 PM',
            'specialization': 'Machine Learning',
            'phone': '555-0456',
            'title': 'Associate Professor'
        }
        defaults.update(kwargs)
        
        professor = Professor(
            user_id=user.id,
            **defaults
        )
        db.add(professor)
        db.commit()
        db.refresh(professor)
        self.created_professors.append(professor)
        return professor
    
    def create_mock_course(self, db: Session, professor: Professor, **kwargs) -> Course:
        """Create a mock course"""
        defaults = {
            'course_code': f'CS{len(self.created_courses) + 101}',
            'title': 'Introduction to Programming',
            'description': 'Learn programming basics',
            'credits': 3,
            'department': 'Computer Science',
            'semester': 'Fall 2024',
            'year': 2024,
            'max_enrollment': 30,
            'schedule': '{"days": ["MWF"], "time": "10:00-11:00", "location": "Room 201"}',
            'prerequisites': '',
            'is_active': True
        }
        defaults.update(kwargs)
        
        course = Course(
            professor_id=professor.id,
            **defaults
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        self.created_courses.append(course)
        return course
    
    def enroll_student_in_course(self, db: Session, student: Student, course: Course):
        """Enroll a student in a course"""
        # Check if already enrolled
        if course not in student.enrolled_courses:
            # Use SQLAlchemy ORM relationship to enroll
            student.enrolled_courses.append(course)
            db.commit()
            self.created_enrollments.append((student.id, course.id))
    
    def setup_complete_test_data(self, db: Session):
        """Set up complete test data for all scenarios"""
        # Create student user and profile
        student_user = self.create_mock_user(db, "student@test.com", UserRole.STUDENT)
        student = self.create_mock_student(db, student_user)
        
        # Create professor user and profile  
        professor_user = self.create_mock_user(db, "professor@test.com", UserRole.PROFESSOR)
        professor = self.create_mock_professor(db, professor_user)
        
        # Create active course
        active_course = self.create_mock_course(db, professor, 
            course_code="CS101",
            title="Programming Basics",
            is_active=True
        )
        
        # Create inactive course
        inactive_course = self.create_mock_course(db, professor,
            course_code="CS999", 
            title="Archived Course",
            is_active=False
        )
        
        # Create additional courses for search
        search_course1 = self.create_mock_course(db, professor,
            course_code="CS201",
            title="Data Structures",
            department="Computer Science"
        )
        
        search_course2 = self.create_mock_course(db, professor,
            course_code="MATH101", 
            title="Calculus I",
            department="Mathematics"
        )
        
        # Enroll student in active course
        self.enroll_student_in_course(db, student, active_course)
        
        return {
            'student_user': student_user,
            'student': student,
            'professor_user': professor_user, 
            'professor': professor,
            'active_course': active_course,
            'inactive_course': inactive_course,
            'search_course1': search_course1,
            'search_course2': search_course2
        }
    
    def cleanup_all_data(self, db: Session):
        """Clean up all created test data"""
        try:
            # Clear enrollments by removing relationships
            for student in self.created_students:
                student.enrolled_courses.clear()
            
            # Delete courses
            for course in self.created_courses:
                db.delete(course)
            
            # Delete students
            for student in self.created_students:
                db.delete(student)
            
            # Delete professors
            for professor in self.created_professors:
                db.delete(professor)
            
            # Delete users
            for user in self.created_users:
                db.delete(user)
            
            db.commit()
            
            # Clear tracking lists
            self.created_users.clear()
            self.created_students.clear() 
            self.created_professors.clear()
            self.created_courses.clear()
            self.created_enrollments.clear()
            
        except Exception as e:
            db.rollback()
            print(f"Cleanup error: {e}")

# Global instance for easy access
mock_data_manager = MockDataManager()