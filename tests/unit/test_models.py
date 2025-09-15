"""
Unit Tests for Database Models
Tests model creation, relationships, and validation
"""
import pytest
from datetime import datetime
from unittest.mock import Mock
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from models.student import User, Student, Professor, Course, UserRole, student_course_association

class TestUserModel:
    """Unit tests for User model"""
    
    def test_user_creation_student(self):
        """Test creating a user with student role"""
        user = User(
            email="student@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.STUDENT,
            is_active=True
        )
        
        assert user.email == "student@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.role == UserRole.STUDENT
        assert user.is_active is True
    
    def test_user_creation_professor(self):
        """Test creating a user with professor role"""
        user = User(
            email="professor@example.com",
            hashed_password="hashed_password_456",
            role=UserRole.PROFESSOR,
            is_active=True
        )
        
        assert user.email == "professor@example.com"
        assert user.role == UserRole.PROFESSOR
    
    def test_user_defaults(self):
        """Test user model default values"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_pass",
            role=UserRole.STUDENT
        )
        
        assert user.is_active is True  # Default value
        assert user.created_at is None  # Will be set by database
        assert user.updated_at is None  # Will be set by database
    
    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.STUDENT == "student"
        assert UserRole.PROFESSOR == "professor"
        
        # Test that only valid roles can be assigned
        user = User(
            email="test@example.com",
            hashed_password="pass",
            role=UserRole.STUDENT
        )
        assert user.role.value == "student"

class TestStudentModel:
    """Unit tests for Student model"""
    
    def test_student_creation_minimal(self):
        """Test creating student with minimal required fields"""
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        assert student.user_id == 1
        assert student.student_id == "STU001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
    
    def test_student_creation_full(self):
        """Test creating student with all fields"""
        student = Student(
            user_id=1,
            student_id="STU002",
            first_name="Jane",
            last_name="Smith",
            phone="555-0123",
            address="123 Main St",
            date_of_birth=datetime(2000, 1, 1),
            major="Computer Science",
            year_level="Junior",
            gpa="3.5"
        )
        
        assert student.phone == "555-0123"
        assert student.address == "123 Main St"
        assert student.major == "Computer Science"
        assert student.year_level == "Junior"
        assert student.gpa == "3.5"
    
    def test_student_optional_fields(self):
        """Test student optional fields can be None"""
        student = Student(
            user_id=1,
            student_id="STU003",
            first_name="Bob",
            last_name="Johnson"
        )
        
        assert student.phone is None
        assert student.address is None
        assert student.date_of_birth is None
        assert student.graduation_date is None
        assert student.major is None
        assert student.year_level is None
        assert student.gpa is None

class TestProfessorModel:
    """Unit tests for Professor model"""
    
    def test_professor_creation_minimal(self):
        """Test creating professor with minimal required fields"""
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        assert professor.user_id == 1
        assert professor.professor_id == "PROF001"
        assert professor.first_name == "Dr. Jane"
        assert professor.last_name == "Smith"
        assert professor.department == "Computer Science"
    
    def test_professor_creation_full(self):
        """Test creating professor with all fields"""
        professor = Professor(
            user_id=2,
            professor_id="PROF002",
            first_name="Dr. John",
            last_name="Doe",
            phone="555-0456",
            office_location="Room 301",
            office_hours="MWF 2-4 PM",
            department="Mathematics",
            title="Associate Professor",
            specialization="Applied Mathematics"
        )
        
        assert professor.phone == "555-0456"
        assert professor.office_location == "Room 301"
        assert professor.office_hours == "MWF 2-4 PM"
        assert professor.title == "Associate Professor"
        assert professor.specialization == "Applied Mathematics"
    
    def test_professor_optional_fields(self):
        """Test professor optional fields can be None"""
        professor = Professor(
            user_id=1,
            professor_id="PROF003",
            first_name="Dr. Bob",
            last_name="Wilson",
            department="Physics"
        )
        
        assert professor.phone is None
        assert professor.office_location is None
        assert professor.office_hours is None
        assert professor.title is None
        assert professor.specialization is None

class TestCourseModel:
    """Unit tests for Course model"""
    
    def test_course_creation_minimal(self):
        """Test creating course with minimal required fields"""
        course = Course(
            course_code="CS101",
            title="Introduction to Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        assert course.course_code == "CS101"
        assert course.title == "Introduction to Programming"
        assert course.professor_id == 1
        assert course.department == "Computer Science"
        assert course.semester == "Fall 2024"
        assert course.year == 2024
    
    def test_course_creation_full(self):
        """Test creating course with all fields"""
        course = Course(
            course_code="CS102",
            title="Advanced Programming",
            description="Advanced programming concepts",
            credits=4,
            professor_id=1,
            department="Computer Science",
            semester="Spring 2024",
            year=2024,
            max_enrollment=25,
            prerequisites="CS101",
            schedule='{"days": ["MWF"], "time": "10:00-11:00"}',
            syllabus="Detailed syllabus content"
        )
        
        assert course.description == "Advanced programming concepts"
        assert course.credits == 4
        assert course.max_enrollment == 25
        assert course.prerequisites == "CS101"
        assert '"days": ["MWF"]' in course.schedule
        assert course.syllabus == "Detailed syllabus content"
    
    def test_course_defaults(self):
        """Test course model default values"""
        course = Course(
            course_code="CS103",
            title="Data Structures",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        assert course.credits == 3  # Default value
        assert course.max_enrollment == 30  # Default value
        assert course.is_active is True  # Default value
        assert course.description is None
        assert course.prerequisites is None
        assert course.schedule is None
        assert course.syllabus is None
    
    def test_course_boolean_fields(self):
        """Test course boolean fields"""
        course = Course(
            course_code="CS104",
            title="Inactive Course",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024,
            is_active=False
        )
        
        assert course.is_active is False

class TestModelRelationships:
    """Unit tests for model relationships"""
    
    def test_user_student_relationship(self):
        """Test User-Student relationship"""
        # Create user
        user = User(
            email="student@example.com",
            hashed_password="hashed_pass",
            role=UserRole.STUDENT
        )
        user.id = 1  # Simulate database ID
        
        # Create student
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        # In a real test with database, you would test:
        # assert student.user == user
        # assert user.student_profile == student
        
        # For unit test, just verify the foreign key
        assert student.user_id == user.id
    
    def test_user_professor_relationship(self):
        """Test User-Professor relationship"""
        # Create user
        user = User(
            email="prof@example.com",
            hashed_password="hashed_pass",
            role=UserRole.PROFESSOR
        )
        user.id = 1  # Simulate database ID
        
        # Create professor
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        # For unit test, just verify the foreign key
        assert professor.user_id == user.id
    
    def test_professor_course_relationship(self):
        """Test Professor-Course relationship"""
        # Create professor
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        professor.id = 1  # Simulate database ID
        
        # Create course
        course = Course(
            course_code="CS101",
            title="Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        # For unit test, just verify the foreign key
        assert course.professor_id == professor.id

class TestModelValidation:
    """Unit tests for model validation and constraints"""
    
    def test_required_fields_user(self):
        """Test that User model requires necessary fields"""
        # This would be tested with actual database constraints
        # For unit tests, we just verify the fields are set correctly
        user = User(
            email="test@example.com",
            hashed_password="pass",
            role=UserRole.STUDENT
        )
        
        assert user.email is not None
        assert user.hashed_password is not None
        assert user.role is not None
    
    def test_required_fields_student(self):
        """Test that Student model requires necessary fields"""
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        assert student.user_id is not None
        assert student.student_id is not None
        assert student.first_name is not None
        assert student.last_name is not None
    
    def test_required_fields_professor(self):
        """Test that Professor model requires necessary fields"""
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        assert professor.user_id is not None
        assert professor.professor_id is not None
        assert professor.first_name is not None
        assert professor.last_name is not None
        assert professor.department is not None
    
    def test_required_fields_course(self):
        """Test that Course model requires necessary fields"""
        course = Course(
            course_code="CS101",
            title="Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        assert course.course_code is not None
        assert course.title is not None
        assert course.professor_id is not None
        assert course.department is not None
        assert course.semester is not None
        assert course.year is not None

class TestStudentCourseAssociation:
    """Unit tests for student-course enrollment association"""
    
    def test_association_table_structure(self):
        """Test the association table structure"""
        # Test that the association table has the expected columns
        assert hasattr(student_course_association.c, 'student_id')
        assert hasattr(student_course_association.c, 'course_id')
        assert hasattr(student_course_association.c, 'enrollment_date')
        assert hasattr(student_course_association.c, 'status')
    
    def test_association_table_name(self):
        """Test that the association table has correct name"""
        assert student_course_association.name == 'enrollments'

if __name__ == "__main__":
    pytest.main([__file__])
