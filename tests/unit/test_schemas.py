"""
Unit Tests for Pydantic schemas
These are pure unit tests - no external dependencies, no database, no network calls
"""
import pytest
from pydantic import ValidationError
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from schemas.student_schemas import (
    UserLogin, UserRegister, Token, TokenData, UserRole,
    StudentCreate, StudentUpdate, StudentResponse,
    ProfessorCreate, ProfessorUpdate, ProfessorResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    EnrollmentCreate, EnrollmentResponse
)

class TestAuthenticationSchemas:
    """Unit tests for authentication-related schemas"""
    
    def test_user_login_valid(self):
        """Test valid user login schema"""
        login_data = {
            "email": "user@example.com",
            "password": "password123"
        }
        
        login = UserLogin(**login_data)
        assert login.email == "user@example.com"
        assert login.password == "password123"
    
    def test_user_login_invalid_email(self):
        """Test user login with invalid email"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)
    
    def test_user_register_valid(self):
        """Test valid user registration"""
        register_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "role": UserRole.STUDENT
        }
        
        register = UserRegister(**register_data)
        assert register.email == "newuser@example.com"
        assert register.password == "password123"
        assert register.role == UserRole.STUDENT
    
    def test_user_register_password_too_short(self):
        """Test user registration with password too short"""
        register_data = {
            "email": "newuser@example.com",
            "password": "123",  # Too short
            "role": UserRole.STUDENT
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**register_data)
        
        errors = exc_info.value.errors()
        assert any("at least 6 characters" in str(error) for error in errors)
    
    def test_token_schema(self):
        """Test token schema"""
        token_data = {
            "access_token": "fake-jwt-token",
            "token_type": "bearer",
            "user_role": UserRole.PROFESSOR,
            "user_id": 1
        }
        
        token = Token(**token_data)
        assert token.access_token == "fake-jwt-token"
        assert token.token_type == "bearer"
        assert token.user_role == UserRole.PROFESSOR
        assert token.user_id == 1

class TestStudentSchemas:
    """Unit test class for student schemas"""
    
    def test_student_create_valid(self):
        """Test creating valid StudentCreate schema"""
        student_data = {
            "email": "student@example.com",
            "password": "password123",
            "student_id": "STU001",
            "first_name": "John",
            "last_name": "Doe",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        student = StudentCreate(**student_data)
        assert student.email == "student@example.com"
        assert student.password == "password123"
        assert student.student_id == "STU001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.major == "Computer Science"
        assert student.year_level == "Junior"
    
    def test_student_create_minimal(self):
        """Test creating StudentCreate with minimal required fields"""
        student_data = {
            "email": "jane@example.com",
            "password": "password123",
            "student_id": "STU002",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        student = StudentCreate(**student_data)
        assert student.first_name == "Jane"
        assert student.last_name == "Smith"
        assert student.major is None
        assert student.year_level is None
    
    def test_student_update_partial(self):
        """Test StudentUpdate with partial data"""
        update_data = {
            "first_name": "Updated",
            "major": "Mathematics"
        }
        
        update = StudentUpdate(**update_data)
        assert update.first_name == "Updated"
        assert update.major == "Mathematics"
        assert update.last_name is None
    
    def test_student_response(self):
        """Test StudentResponse schema"""
        response_data = {
            "id": 1,
            "student_id": "STU001",
            "first_name": "John",
            "last_name": "Doe",
            "enrollment_date": datetime.now()
        }
        
        response = StudentResponse(**response_data)
        assert response.id == 1
        assert response.student_id == "STU001"

class TestProfessorSchemas:
    """Unit tests for professor schemas"""
    
    def test_professor_create_valid(self):
        """Test valid professor creation"""
        professor_data = {
            "email": "prof@example.com",
            "password": "password123",
            "professor_id": "PROF001",
            "first_name": "Jane",
            "last_name": "Smith",
            "department": "Computer Science",
            "title": "Associate Professor"
        }
        
        professor = ProfessorCreate(**professor_data)
        assert professor.email == "prof@example.com"
        assert professor.professor_id == "PROF001"
        assert professor.department == "Computer Science"
        assert professor.title == "Associate Professor"
    
    def test_professor_update(self):
        """Test professor update schema"""
        update_data = {
            "office_hours": "MWF 2-4 PM",
            "specialization": "Machine Learning"
        }
        
        update = ProfessorUpdate(**update_data)
        assert update.office_hours == "MWF 2-4 PM"
        assert update.specialization == "Machine Learning"
        assert update.first_name is None

class TestCourseSchemas:
    """Unit tests for course schemas"""
    
    def test_course_create_valid(self):
        """Test valid course creation"""
        course_data = {
            "course_code": "CS101",
            "title": "Introduction to Programming",
            "description": "Learn basic programming",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        course = CourseCreate(**course_data)
        assert course.course_code == "CS101"
        assert course.title == "Introduction to Programming"
        assert course.credits == 3
        assert course.year == 2024
    
    def test_course_create_defaults(self):
        """Test course creation with default values"""
        course_data = {
            "course_code": "CS102",
            "title": "Advanced Programming",
            "department": "Computer Science",
            "semester": "Spring 2024",
            "year": 2024
        }
        
        course = CourseCreate(**course_data)
        assert course.credits == 3  # Default value
        assert course.max_enrollment == 30  # Default value
    
    def test_course_update(self):
        """Test course update schema"""
        update_data = {
            "title": "Updated Course Title",
            "max_enrollment": 25
        }
        
        update = CourseUpdate(**update_data)
        assert update.title == "Updated Course Title"
        assert update.max_enrollment == 25
        assert update.description is None
    
    def test_course_response(self):
        """Test course response schema"""
        response_data = {
            "id": 1,
            "course_code": "CS101",
            "title": "Programming",
            "credits": 3,
            "professor_id": 1,
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": True,
            "created_at": datetime.now(),
            "enrolled_count": 15
        }
        
        response = CourseResponse(**response_data)
        assert response.course_code == "CS101"
        assert response.enrolled_count == 15

class TestEnrollmentSchemas:
    """Unit tests for enrollment schemas"""
    
    def test_enrollment_create(self):
        """Test enrollment creation"""
        enrollment_data = {"course_id": 1}
        
        enrollment = EnrollmentCreate(**enrollment_data)
        assert enrollment.course_id == 1
    
    def test_enrollment_response(self):
        """Test enrollment response"""
        course_data = {
            "id": 1,
            "course_code": "CS101",
            "title": "Programming",
            "credits": 3,
            "professor_id": 1,
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": True,
            "created_at": datetime.now()
        }
        
        response_data = {
            "student_id": 1,
            "course_id": 1,
            "enrollment_date": datetime.now(),
            "status": "enrolled",
            "course": course_data
        }
        
        response = EnrollmentResponse(**response_data)
        assert response.student_id == 1
        assert response.status == "enrolled"

class TestSchemaValidation:
    """Unit test class for schema validation edge cases"""
    
    def test_email_validation(self):
        """Test email validation across schemas"""
        invalid_emails = ["invalid-email", "@example.com", "user@", ""]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                UserLogin(email=invalid_email, password="password")
    
    def test_password_length_validation(self):
        """Test password length validation"""
        short_passwords = ["", "1", "12", "123", "1234", "12345"]
        
        for short_password in short_passwords:
            with pytest.raises(ValidationError):
                UserRegister(
                    email="test@example.com",
                    password=short_password,
                    role=UserRole.STUDENT
                )
    
    def test_role_validation(self):
        """Test user role validation"""
        valid_roles = ["student", "professor"]
        
        for role in valid_roles:
            register = UserRegister(
                email="test@example.com",
                password="password123",
                role=role
            )
            assert register.role in [UserRole.STUDENT, UserRole.PROFESSOR]
    
    def test_credits_validation(self):
        """Test course credits validation"""
        course_data = {
            "course_code": "CS101",
            "title": "Programming",
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "credits": -1  # Invalid negative credits
        }
        
        # This should still pass as we don't have custom validation for negative credits
        # But in a real application, you might want to add such validation
        course = CourseCreate(**course_data)
        assert course.credits == -1

if __name__ == "__main__":
    pytest.main([__file__])
