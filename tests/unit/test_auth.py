"""
Unit Tests for Authentication System
Tests JWT token creation, password hashing, and authentication functions
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from config.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user
)
from models.student import User, UserRole
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

class TestPasswordHashing:
    """Unit tests for password hashing functions"""
    
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        
        # Hash the password
        hashed = get_password_hash(password)
        
        # Verify it's not the same as original
        assert hashed != password
        assert len(hashed) > 20  # Hashed password should be much longer
        
        # Verify password verification works
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Due to salt, hashes should be different
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestJWTTokens:
    """Unit tests for JWT token creation and verification"""
    
    def test_create_access_token_basic(self):
        """Test basic JWT token creation"""
        data = {"sub": "test@example.com", "user_id": 1}
        
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long strings
        assert "." in token  # JWT tokens have dots as separators
    
    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry"""
        data = {"sub": "test@example.com", "user_id": 1}
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 20
    
    @patch('config.auth.jwt.decode')
    def test_verify_token_valid(self, mock_decode):
        """Test token verification with valid token"""
        # Mock JWT decode to return valid payload
        mock_decode.return_value = {
            "sub": "test@example.com",
            "user_id": 1,
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.jwt.token"
        )
        
        token_data = verify_token(credentials)
        
        assert token_data.email == "test@example.com"
        assert token_data.user_id == 1
    
    @patch('config.auth.jwt.decode')
    def test_verify_token_invalid(self, mock_decode):
        """Test token verification with invalid token"""
        from jose import JWTError
        
        # Mock JWT decode to raise JWTError
        mock_decode.side_effect = JWTError("Invalid token")
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.jwt.token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @patch('config.auth.jwt.decode')
    def test_verify_token_missing_data(self, mock_decode):
        """Test token verification with missing required data"""
        # Mock JWT decode to return payload without required fields
        mock_decode.return_value = {
            "sub": "test@example.com"
            # Missing user_id
        }
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="incomplete.jwt.token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)
        
        assert exc_info.value.status_code == 401

class TestUserAuthentication:
    """Unit tests for user authentication"""
    
    def test_authenticate_user_valid(self):
        """Test user authentication with valid credentials"""
        # Create a mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("correct_password")
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = authenticate_user(mock_db, "test@example.com", "correct_password")
        
        assert result == mock_user
        mock_db.query.assert_called_once()
    
    def test_authenticate_user_invalid_email(self):
        """Test user authentication with invalid email"""
        # Mock database session - no user found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = authenticate_user(mock_db, "nonexistent@example.com", "password")
        
        assert result is False
    
    def test_authenticate_user_invalid_password(self):
        """Test user authentication with invalid password"""
        # Create a mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("correct_password")
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = authenticate_user(mock_db, "test@example.com", "wrong_password")
        
        assert result is False

class TestAuthenticationHelpers:
    """Unit tests for authentication helper functions"""
    
    @patch('config.auth.get_db')
    def test_get_current_user_valid(self, mock_get_db):
        """Test getting current user with valid token data"""
        from config.auth import get_current_user
        from schemas.student_schemas import TokenData
        
        # Create mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock token data
        token_data = TokenData(email="test@example.com", user_id=1)
        
        result = get_current_user(mock_db, token_data)
        
        assert result == mock_user
    
    @patch('config.auth.get_db')
    def test_get_current_user_not_found(self, mock_get_db):
        """Test getting current user when user not found"""
        from config.auth import get_current_user
        from schemas.student_schemas import TokenData
        
        # Mock database session - no user found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock token data
        token_data = TokenData(email="nonexistent@example.com", user_id=1)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_db, token_data)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail
    
    def test_get_current_active_user_active(self):
        """Test getting current active user when user is active"""
        from config.auth import get_current_active_user
        
        # Create mock active user
        mock_user = Mock()
        mock_user.is_active = True
        
        result = get_current_active_user(mock_user)
        
        assert result == mock_user
    
    def test_get_current_active_user_inactive(self):
        """Test getting current active user when user is inactive"""
        from config.auth import get_current_active_user
        
        # Create mock inactive user
        mock_user = Mock()
        mock_user.is_active = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(mock_user)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail

class TestRoleBasedAccess:
    """Unit tests for role-based access control"""
    
    @patch('config.auth.get_db')
    def test_get_current_student_valid(self, mock_get_db):
        """Test getting current student with valid student user"""
        from config.auth import get_current_student
        from models.student import UserRole
        
        # Create mock user with student role
        mock_user = Mock()
        mock_user.role = UserRole.STUDENT
        mock_user.id = 1
        
        # Create mock student
        mock_student = Mock()
        mock_student.user_id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_student
        
        result = get_current_student(mock_db, mock_user)
        
        assert result == mock_student
    
    def test_get_current_student_wrong_role(self):
        """Test getting current student with professor user"""
        from config.auth import get_current_student
        from models.student import UserRole
        
        # Create mock user with professor role
        mock_user = Mock()
        mock_user.role = UserRole.PROFESSOR
        
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_student(mock_db, mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Student role required" in exc_info.value.detail
    
    @patch('config.auth.get_db')
    def test_get_current_professor_valid(self, mock_get_db):
        """Test getting current professor with valid professor user"""
        from config.auth import get_current_professor
        from models.student import UserRole
        
        # Create mock user with professor role
        mock_user = Mock()
        mock_user.role = UserRole.PROFESSOR
        mock_user.id = 1
        
        # Create mock professor
        mock_professor = Mock()
        mock_professor.user_id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_professor
        
        result = get_current_professor(mock_db, mock_user)
        
        assert result == mock_professor
    
    def test_get_current_professor_wrong_role(self):
        """Test getting current professor with student user"""
        from config.auth import get_current_professor
        from models.student import UserRole
        
        # Create mock user with student role
        mock_user = Mock()
        mock_user.role = UserRole.STUDENT
        
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_professor(mock_db, mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Professor role required" in exc_info.value.detail

if __name__ == "__main__":
    pytest.main([__file__])
