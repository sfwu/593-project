"""
Unit Tests for Course Controller
Tests the general /courses endpoints with authentication and role-based filtering
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

# Import mock data manager
from . import mock_data_manager

from controllers.course_controller import (
    get_all_courses, get_course_by_id, get_course_enrollment,
    get_departments, get_semesters
)
from models import User, Student, Professor, Course, UserRole
from schemas.student_schemas import CourseWithProfessor


class TestGeneralCourseEndpoints:
    """Test general course endpoints accessible to all authenticated users"""
    
    @pytest.mark.asyncio
    async def test_get_all_courses_as_student(self):
        """Test getting all courses as a student"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        mock_user.role = UserRole.STUDENT
        mock_user.id = 1
        
        # Mock courses
        mock_course1 = Mock()
        mock_course1.id = 1
        mock_course1.course_code = "CS101"
        mock_course1.title = "Intro to Programming"
        mock_course1.is_active = True
        mock_course1.professor_id = 1
        
        mock_course2 = Mock()
        mock_course2.id = 2
        mock_course2.course_code = "CS201"
        mock_course2.title = "Data Structures"
        mock_course2.is_active = True
        mock_course2.professor_id = 1
        
        # Mock professor
        mock_professor = Mock()
        mock_professor.id = 1
        mock_professor.first_name = "Dr. Smith"
        mock_professor.last_name = "Johnson"
        
        # Mock student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course1, mock_course2]
        mock_db.query.return_value = mock_query
        
        # Mock professor query
        def mock_professor_query(model):
            if model == Professor:
                prof_query = Mock()
                prof_query.filter.return_value.first.return_value = mock_professor
                return prof_query
            elif model == Student:
                student_query = Mock()
                student_query.filter.return_value.first.return_value = mock_student
                return student_query
            return mock_query
        
        mock_db.query.side_effect = mock_professor_query
        
        # Mock enrollment count
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Mock enrollment check
        mock_db.query.return_value.filter.return_value.first.return_value = None  # Not enrolled
        
        # Act
        result = await get_all_courses(
            current_user=mock_user,
            db=mock_db
        )
        
        # Assert
        assert len(result) == 2
        assert result[0]["course_code"] == "CS101"
        assert result[0]["is_enrolled"] == False
        assert "professor" in result[0]
    
    @pytest.mark.asyncio
    async def test_get_all_courses_as_professor(self):
        """Test getting all courses as a professor"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        mock_user.role = UserRole.PROFESSOR
        mock_user.id = 1
        
        mock_course = Mock()
        mock_course.id = 1
        mock_course.course_code = "CS101"
        mock_course.professor_id = 1
        
        mock_professor = Mock()
        mock_professor.id = 1
        mock_professor.first_name = "Dr. Smith"
        
        # Mock queries
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course]
        
        def mock_query_side_effect(model):
            if model == Professor:
                prof_query = Mock()
                prof_query.filter.return_value.first.return_value = mock_professor
                return prof_query
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Act
        result = await get_all_courses(
            current_user=mock_user,
            db=mock_db
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["is_teaching"] == True
    
    @pytest.mark.asyncio
    async def test_get_course_by_id_success(self, test_db):
        """Test getting a specific course by ID using real database"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        student_user = test_data['student_user']
        active_course = test_data['active_course']
        
        try:
            # Act - get the course by ID
            result = await get_course_by_id(
                course_id=active_course.id,
                current_user=student_user,
                db=test_db
            )
            
            # Assert
            assert result["id"] == active_course.id
            assert result["course_code"] == "CS101"
            assert "is_enrolled" in result
            assert "professor" in result
            
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)
    
    @pytest.mark.asyncio
    async def test_get_course_by_id_not_found(self):
        """Test getting a course that doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        mock_user.role = UserRole.STUDENT
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_course_by_id(
                course_id=999,
                current_user=mock_user,
                db=mock_db
            )
        
        assert exc_info.value.status_code == 404
        assert "Course not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_course_enrollment_basic(self, test_db):
        """Test getting course enrollment information using real database"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        student_user = test_data['student_user']
        active_course = test_data['active_course']
        
        try:
            # Act - get course enrollment info
            result = await get_course_enrollment(
                course_id=active_course.id,
                current_user=student_user,
                db=test_db
            )
            
            # Assert
            assert result["course_id"] == active_course.id
            assert "enrolled_count" in result
            assert "available_spots" in result
            assert "enrollment_percentage" in result
            assert result["enrolled_count"] >= 1  # At least one student enrolled
            
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)
    
    @pytest.mark.asyncio
    async def test_get_departments(self):
        """Test getting list of departments"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        
        mock_db.query.return_value.distinct.return_value.all.return_value = [
            ("Computer Science",),
            ("Mathematics",),
            ("Physics",)
        ]
        
        # Act
        result = await get_departments(
            current_user=mock_user,
            db=mock_db
        )
        
        # Assert
        assert "departments" in result
        assert len(result["departments"]) == 3
        assert "Computer Science" in result["departments"]
    
    @pytest.mark.asyncio
    async def test_get_semesters(self):
        """Test getting list of semesters"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        
        mock_db.query.return_value.distinct.return_value.order_by.return_value.all.return_value = [
            ("Fall", 2024),
            ("Spring", 2024),
            ("Summer", 2024)
        ]
        
        # Act
        result = await get_semesters(
            current_user=mock_user,
            db=mock_db
        )
        
        # Assert
        assert "semesters" in result
        assert len(result["semesters"]) == 3
        assert result["semesters"][0]["semester"] == "Fall"
        assert result["semesters"][0]["year"] == 2024


class TestCourseEndpointFiltering:
    """Test filtering and search functionality"""
    
    @pytest.mark.asyncio
    async def test_get_all_courses_with_filters(self):
        """Test course filtering by department, semester, year, keyword"""
        # Arrange
        mock_db = Mock()
        mock_user = Mock()
        mock_user.role = UserRole.STUDENT
        mock_user.id = 1
        
        mock_course = Mock()
        mock_course.id = 1
        mock_course.course_code = "CS101"
        
        mock_professor = Mock()
        mock_professor.id = 1
        
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course]
        mock_db.query.return_value = mock_query
        
        def mock_query_side_effect(model):
            if model == Professor:
                prof_query = Mock()
                prof_query.filter.return_value.first.return_value = mock_professor
                return prof_query
            elif model == Student:
                student_query = Mock()
                student_query.filter.return_value.first.return_value = mock_student
                return student_query
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Act
        result = await get_all_courses(
            department="Computer Science",
            semester="Fall",
            year=2024,
            keyword="programming",
            current_user=mock_user,
            db=mock_db
        )
        
        # Assert
        assert len(result) == 1
        # Verify that filters were applied (query.filter was called multiple times)
        assert mock_query.filter.call_count >= 4  # At least 4 filters applied


class TestRoleBasedAccess:
    """Test role-based access to course information"""
    
    @pytest.mark.asyncio
    async def test_student_cannot_see_inactive_courses(self, test_db):
        """Test that students can't see inactive courses unless enrolled"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        student_user = test_data['student_user']
        inactive_course = test_data['inactive_course']
        
        try:
            # Act & Assert - student should not be able to see inactive course
            with pytest.raises(HTTPException) as exc_info:
                await get_course_by_id(
                    course_id=inactive_course.id,
                    current_user=student_user,
                    db=test_db
                )
            
            assert exc_info.value.status_code == 404
            
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)
    
    @pytest.mark.asyncio
    async def test_professor_can_see_inactive_courses(self, test_db):
        """Test that professors can see inactive courses using real database"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        professor_user = test_data['professor_user']
        inactive_course = test_data['inactive_course']
        
        try:
            # Act - professor should be able to see their inactive course
            result = await get_course_by_id(
                course_id=inactive_course.id,
                current_user=professor_user,
                db=test_db
            )
            
            # Assert
            assert result["id"] == inactive_course.id
            assert result["course_code"] == "CS999"
            assert "is_teaching" in result
            
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)


if __name__ == "__main__":
    pytest.main([__file__])
