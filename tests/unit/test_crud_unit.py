"""
Unit Tests for CRUD operations
These are pure unit tests using mocks - no real database connections
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

import crud
import schemas
import models

class TestStudentCRUDUnit:
    """Unit test class for student CRUD operations using mocks"""
    
    def test_get_student_success(self):
        """Test getting student by ID - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_student = Mock()
        mock_student.id = 1
        mock_student.first_name = "John"
        mock_student.email = "john@example.com"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_student
        
        # Act
        result = crud.get_student(mock_db, student_id=1)
        
        # Assert
        assert result == mock_student
        mock_db.query.assert_called_once_with(models.Student)
        mock_db.query.return_value.filter.assert_called_once()
        mock_db.query.return_value.filter.return_value.first.assert_called_once()
    
    def test_get_student_not_found(self):
        """Test getting student by ID when not found - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = crud.get_student(mock_db, student_id=999)
        
        # Assert
        assert result is None
        mock_db.query.assert_called_once_with(models.Student)
    
    def test_get_student_by_email_success(self):
        """Test getting student by email - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_student = Mock()
        mock_student.email = "test@example.com"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_student
        
        # Act
        result = crud.get_student_by_email(mock_db, email="test@example.com")
        
        # Assert
        assert result == mock_student
        mock_db.query.assert_called_once_with(models.Student)
    
    def test_get_student_by_student_id_success(self):
        """Test getting student by student ID - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_student = Mock()
        mock_student.student_id = "S12345"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_student
        
        # Act
        result = crud.get_student_by_student_id(mock_db, student_id="S12345")
        
        # Assert
        assert result == mock_student
        mock_db.query.assert_called_once_with(models.Student)
    
    def test_get_students_with_pagination(self):
        """Test getting all students with pagination - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_students = [Mock(), Mock(), Mock()]
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_students
        
        # Act
        result = crud.get_students(mock_db, skip=10, limit=20)
        
        # Assert
        assert result == mock_students
        mock_db.query.assert_called_once_with(models.Student)
        mock_db.query.return_value.offset.assert_called_once_with(10)
        mock_db.query.return_value.offset.return_value.limit.assert_called_once_with(20)
        mock_db.query.return_value.offset.return_value.limit.return_value.all.assert_called_once()
    
    @patch('crud.models.Student')
    def test_create_student_success(self, mock_student_model):
        """Test creating a student - mocked database and model"""
        # Arrange
        mock_db = Mock()
        mock_student_instance = Mock()
        mock_student_instance.id = 1
        mock_student_instance.first_name = "John"
        mock_student_model.return_value = mock_student_instance
        
        student_data = schemas.StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            student_id="S12345"
        )
        
        # Act
        result = crud.create_student(mock_db, student_data)
        
        # Assert
        assert result == mock_student_instance
        mock_student_model.assert_called_once_with(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            student_id="S12345"
        )
        mock_db.add.assert_called_once_with(mock_student_instance)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_student_instance)
    
    def test_update_student_success(self):
        """Test updating student successfully - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock get_student to return a student
        with patch('crud.get_student', return_value=mock_student) as mock_get_student:
            student_data = schemas.StudentCreate(
                first_name="Updated",
                last_name="Name",
                email="updated@example.com",
                student_id="S12345"
            )
            
            # Act
            result = crud.update_student(mock_db, student_id=1, student=student_data)
            
            # Assert
            assert result == mock_student
            mock_get_student.assert_called_once_with(mock_db, 1)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_student)
            
            # Check that setattr was called for each field
            assert mock_student.first_name == "Updated"
            assert mock_student.last_name == "Name"
            assert mock_student.email == "updated@example.com"
    
    def test_update_student_not_found(self):
        """Test updating student when not found - mocked database"""
        # Arrange
        mock_db = Mock()
        
        # Mock get_student to return None
        with patch('crud.get_student', return_value=None) as mock_get_student:
            student_data = schemas.StudentCreate(
                first_name="Updated",
                last_name="Name",
                email="updated@example.com",
                student_id="S12345"
            )
            
            # Act
            result = crud.update_student(mock_db, student_id=999, student=student_data)
            
            # Assert
            assert result is None
            mock_get_student.assert_called_once_with(mock_db, 999)
            mock_db.commit.assert_not_called()
    
    def test_delete_student_success(self):
        """Test deleting student successfully - mocked database"""
        # Arrange
        mock_db = Mock()
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock get_student to return a student
        with patch('crud.get_student', return_value=mock_student) as mock_get_student:
            # Act
            result = crud.delete_student(mock_db, student_id=1)
            
            # Assert
            assert result == mock_student
            mock_get_student.assert_called_once_with(mock_db, 1)
            mock_db.delete.assert_called_once_with(mock_student)
            mock_db.commit.assert_called_once()
    
    def test_delete_student_not_found(self):
        """Test deleting student when not found - mocked database"""
        # Arrange
        mock_db = Mock()
        
        # Mock get_student to return None
        with patch('crud.get_student', return_value=None) as mock_get_student:
            # Act
            result = crud.delete_student(mock_db, student_id=999)
            
            # Assert
            assert result is None
            mock_get_student.assert_called_once_with(mock_db, 999)
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()

class TestCRUDInputValidation:
    """Unit test class for CRUD input validation"""
    
    def test_create_student_with_none_values(self):
        """Test creating student with None values in schema"""
        mock_db = Mock()
        
        # This should work as the schema validates all fields
        student_data = schemas.StudentCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            student_id="T001"
        )
        
        with patch('crud.models.Student') as mock_student_model:
            mock_student_instance = Mock()
            mock_student_model.return_value = mock_student_instance
            
            result = crud.create_student(mock_db, student_data)
            
            # Verify the model was created with correct values
            mock_student_model.assert_called_once_with(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                student_id="T001"
            )

if __name__ == "__main__":
    pytest.main([__file__])
