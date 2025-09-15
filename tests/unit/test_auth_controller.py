"""
Unit Tests for Authentication Controller
Tests login, registration, and authentication endpoints
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from controllers.auth_controller import (
    login, register_student, register_professor,
    get_current_user_profile, get_current_student_profile,
    get_current_professor_profile
)
from schemas.student_schemas import UserLogin, StudentCreate, ProfessorCreate
from models import User, Student, Professor, UserRole

class TestAuthController:
    """Unit tests for authentication controller functions"""
    
    @patch('controllers.auth_controller.authenticate_user')
    @patch('controllers.auth_controller.create_access_token')
    def test_login_success(self, mock_create_token, mock_authenticate):
        """Test successful login"""
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.STUDENT
        
        # Mock authenticate_user to return the user
        mock_authenticate.return_value = mock_user
        
        # Mock create_access_token to return a token
        mock_create_token.return_value = "fake.jwt.token"
        
        # Mock database session
        mock_db = Mock()
        
        # Create login request
        login_request = UserLogin(email="test@example.com", password="password123")
        
        # Call login function
        result = login(login_request, mock_db)
        
        # Assertions
        assert result["access_token"] == "fake.jwt.token"
        assert result["token_type"] == "bearer"
        assert result["user_role"] == UserRole.STUDENT
        assert result["user_id"] == 1
        
        mock_authenticate.assert_called_once_with(mock_db, "test@example.com", "password123")
        mock_create_token.assert_called_once()
    
    @patch('controllers.auth_controller.authenticate_user')
    def test_login_invalid_credentials(self, mock_authenticate):
        """Test login with invalid credentials"""
        # Mock authenticate_user to return False
        mock_authenticate.return_value = False
        
        # Mock database session
        mock_db = Mock()
        
        # Create login request
        login_request = UserLogin(email="test@example.com", password="wrongpassword")
        
        # Call login function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            login(login_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in exc_info.value.detail

class TestStudentRegistration:
    """Unit tests for student registration"""
    
    @patch('controllers.auth_controller.get_password_hash')
    def test_register_student_success(self, mock_hash_password):
        """Test successful student registration"""
        # Mock password hashing
        mock_hash_password.return_value = "hashed_password"
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Mock the created user
        mock_user = Mock()
        mock_user.id = 1
        
        # Configure the refresh method to set the ID
        def set_user_id(user):
            user.id = 1
        mock_db.refresh.side_effect = set_user_id
        
        # Create registration request
        student_data = StudentCreate(
            email="student@example.com",
            password="password123",
            student_id="STU001",
            first_name="John",
            last_name="Doe",
            major="Computer Science"
        )
        
        # Call registration function
        result = register_student(student_data, mock_db)
        
        # Assertions
        assert result["message"] == "Student registered successfully"
        assert "user_id" in result
        
        # Verify database operations
        assert mock_db.add.call_count == 2  # User and Student
        assert mock_db.commit.call_count == 2
        mock_hash_password.assert_called_once_with("password123")
    
    def test_register_student_existing_email(self):
        """Test student registration with existing email"""
        # Mock database session with existing user
        mock_existing_user = Mock()
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing_user
        
        # Create registration request
        student_data = StudentCreate(
            email="existing@example.com",
            password="password123",
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        # Call registration function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            register_student(student_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail
    
    def test_register_student_existing_student_id(self):
        """Test student registration with existing student ID"""
        # Mock database session
        mock_db = Mock()
        
        # First call (check email) returns None, second call (check student_id) returns existing student
        mock_existing_student = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_existing_student]
        
        # Create registration request
        student_data = StudentCreate(
            email="new@example.com",
            password="password123",
            student_id="EXISTING001",
            first_name="John",
            last_name="Doe"
        )
        
        # Call registration function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            register_student(student_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Student ID already registered" in exc_info.value.detail

class TestProfessorRegistration:
    """Unit tests for professor registration"""
    
    @patch('controllers.auth_controller.get_password_hash')
    def test_register_professor_success(self, mock_hash_password):
        """Test successful professor registration"""
        # Mock password hashing
        mock_hash_password.return_value = "hashed_password"
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Mock the created user
        mock_user = Mock()
        mock_user.id = 1
        
        # Configure the refresh method to set the ID
        def set_user_id(user):
            user.id = 1
        mock_db.refresh.side_effect = set_user_id
        
        # Create registration request
        professor_data = ProfessorCreate(
            email="prof@example.com",
            password="password123",
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science",
            title="Associate Professor"
        )
        
        # Call registration function
        result = register_professor(professor_data, mock_db)
        
        # Assertions
        assert result["message"] == "Professor registered successfully"
        assert "user_id" in result
        
        # Verify database operations
        assert mock_db.add.call_count == 2  # User and Professor
        assert mock_db.commit.call_count == 2
        mock_hash_password.assert_called_once_with("password123")
    
    def test_register_professor_existing_professor_id(self):
        """Test professor registration with existing professor ID"""
        # Mock database session
        mock_db = Mock()
        
        # First call (check email) returns None, second call (check professor_id) returns existing professor
        mock_existing_professor = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_existing_professor]
        
        # Create registration request
        professor_data = ProfessorCreate(
            email="new@example.com",
            password="password123",
            professor_id="EXISTING001",
            first_name="Dr. John",
            last_name="Doe",
            department="Mathematics"
        )
        
        # Call registration function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            register_professor(professor_data, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Professor ID already registered" in exc_info.value.detail

class TestProfileEndpoints:
    """Unit tests for profile endpoints"""
    
    def test_get_current_user_profile(self):
        """Test getting current user profile"""
        # Mock current user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.STUDENT
        mock_user.is_active = True
        mock_user.created_at = datetime.now()
        
        result = get_current_user_profile(mock_user)
        
        assert result == mock_user
    
    def test_get_current_student_profile(self):
        """Test getting current student profile"""
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        mock_student.student_id = "STU001"
        mock_student.first_name = "John"
        mock_student.last_name = "Doe"
        
        result = get_current_student_profile(mock_student)
        
        assert result == mock_student
    
    def test_get_current_professor_profile(self):
        """Test getting current professor profile"""
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        mock_professor.professor_id = "PROF001"
        mock_professor.first_name = "Dr. Jane"
        mock_professor.last_name = "Smith"
        mock_professor.department = "Computer Science"
        
        result = get_current_professor_profile(mock_professor)
        
        assert result == mock_professor

class TestAuthControllerIntegration:
    """Integration-style tests using mocked dependencies"""
    
    @patch('controllers.auth_controller.authenticate_user')
    @patch('controllers.auth_controller.create_access_token')
    @patch('controllers.auth_controller.ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    def test_login_token_expiry(self, mock_create_token, mock_authenticate):
        """Test that login creates token with correct expiry"""
        from datetime import timedelta
        
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.STUDENT
        
        mock_authenticate.return_value = mock_user
        mock_create_token.return_value = "fake.jwt.token"
        
        mock_db = Mock()
        login_request = UserLogin(email="test@example.com", password="password123")
        
        # Call login
        result = login(login_request, mock_db)
        
        # Verify create_access_token was called with correct parameters
        mock_create_token.assert_called_once()
        call_args = mock_create_token.call_args
        
        # Check the data parameter
        data = call_args[1]['data']
        assert data['sub'] == "test@example.com"
        assert data['user_id'] == 1
        
        # Check the expires_delta parameter
        expires_delta = call_args[1]['expires_delta']
        assert isinstance(expires_delta, timedelta)
        assert expires_delta.total_seconds() == 30 * 60  # 30 minutes

if __name__ == "__main__":
    pytest.main([__file__])
