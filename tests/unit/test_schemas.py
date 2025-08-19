"""
Unit Tests for Pydantic schemas
These are pure unit tests - no external dependencies, no database, no network calls
"""
import pytest
from pydantic import ValidationError
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

import schemas

class TestStudentSchemas:
    """Unit test class for student schemas"""
    
    def test_student_create_valid(self):
        """Test creating valid StudentCreate schema"""
        student_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "student_id": "S12345"
        }
        
        student = schemas.StudentCreate(**student_data)
        
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.email == "john.doe@example.com"
        assert student.student_id == "S12345"
    
    def test_student_create_minimal(self):
        """Test creating StudentCreate with minimal required fields"""
        student_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "student_id": "S12346"
        }
        
        student = schemas.StudentCreate(**student_data)
        
        assert student.first_name == "Jane"
        assert student.last_name == "Smith"
        assert student.email == "jane.smith@example.com"
        assert student.student_id == "S12346"
    
    def test_student_create_missing_required_field(self):
        """Test creating StudentCreate with missing required field"""
        student_data = {
            "last_name": "Doe",
            "email": "incomplete@example.com",
            "student_id": "S99999"
            # Missing first_name
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schemas.StudentCreate(**student_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("first_name",)
        assert errors[0]["type"] == "missing"
    

    
    def test_student_response_schema(self):
        """Test Student response schema"""
        student_data = {
            "id": 1,
            "first_name": "Response",
            "last_name": "Test",
            "email": "response@example.com",
            "student_id": "R001"
        }
        
        student = schemas.Student(**student_data)
        
        assert student.id == 1
        assert student.first_name == "Response"
        assert student.last_name == "Test"
        assert student.email == "response@example.com"
        assert student.student_id == "R001"

class TestSchemaValidation:
    """Unit test class for schema validation edge cases"""
    
    def test_empty_string_validation(self):
        """Test validation with empty strings"""
        student_data = {
            "first_name": "",  # Empty string
            "last_name": "Doe",
            "email": "empty@example.com",
            "student_id": "E001"
        }
        
        # This should pass (empty string is valid, though not ideal)
        student = schemas.StudentCreate(**student_data)
        assert student.first_name == ""
    
    def test_whitespace_string_validation(self):
        """Test validation with whitespace-only strings"""
        student_data = {
            "first_name": "   ",  # Whitespace only
            "last_name": "Doe",
            "email": "whitespace@example.com",
            "student_id": "W001"
        }
        
        # This should pass (whitespace is valid, though not ideal)
        student = schemas.StudentCreate(**student_data)
        assert student.first_name == "   "

if __name__ == "__main__":
    pytest.main([__file__])
