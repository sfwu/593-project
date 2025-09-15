"""
Unit Tests for Student Controller
Tests student profile management and course-related functionality
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch
from fastapi import HTTPException
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

# Import mock data manager
from . import mock_data_manager

from controllers.student_controller import (
    update_student_profile, change_password, search_courses,
    enroll_in_course, get_enrolled_courses, withdraw_from_course,
    get_student_schedule
)
from schemas.student_schemas import StudentUpdate, EnrollmentCreate
from models import Student, Course, Professor, User

class TestStudentProfileManagement:
    """Unit tests for student profile management"""
    
    @pytest.mark.asyncio
    async def test_update_student_profile_success(self):
        """Test successful student profile update"""
        # Mock current student
        mock_student = Mock()
        mock_student.first_name = "John"
        mock_student.last_name = "Doe"
        mock_student.major = "Computer Science"
        
        # Mock database session
        mock_db = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Create update data
        update_data = StudentUpdate(
            first_name="Johnny",
            major="Mathematics"
        )
        
        # Call update function
        result = await update_student_profile(update_data, mock_student, mock_db)
        
        # Assertions
        assert mock_student.first_name == "Johnny"
        assert mock_student.major == "Mathematics"
        assert mock_student.last_name == "Doe"  # Unchanged
        assert result == mock_student
        
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_student)
    
    @pytest.mark.asyncio
    async def test_update_student_profile_partial(self):
        """Test partial student profile update"""
        # Mock current student
        mock_student = Mock()
        mock_student.first_name = "John"
        mock_student.phone = "555-0123"
        
        # Mock database session
        mock_db = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Create update data with only one field
        update_data = StudentUpdate(phone="555-9999")
        
        # Call update function
        result = await update_student_profile(update_data, mock_student, mock_db)
        
        # Assertions
        assert mock_student.phone == "555-9999"
        assert mock_student.first_name == "John"  # Unchanged
    
    @patch('controllers.student_controller.verify_password')
    @patch('controllers.student_controller.get_password_hash')
    @pytest.mark.asyncio
    async def test_change_password_success(self, mock_hash_password, mock_verify_password):
        """Test successful password change"""
        # Mock password verification and hashing
        mock_verify_password.return_value = True
        mock_hash_password.return_value = "new_hashed_password"
        
        # Mock current student and user
        mock_student = Mock()
        mock_student.user_id = 1
        
        mock_user = Mock()
        mock_user.hashed_password = "old_hashed_password"
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit = Mock()
        
        # Call change password function
        result = await change_password("old_password", "new_password", mock_student, mock_db)
        
        # Assertions
        assert result["message"] == "Password updated successfully"
        assert mock_user.hashed_password == "new_hashed_password"
        
        mock_verify_password.assert_called_once_with("old_password", "old_hashed_password")
        mock_hash_password.assert_called_once_with("new_password")
        mock_db.commit.assert_called_once()
    
    @patch('controllers.student_controller.verify_password')
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, mock_verify_password):
        """Test password change with wrong current password"""
        # Mock password verification to return False
        mock_verify_password.return_value = False
        
        # Mock current student and user
        mock_student = Mock()
        mock_student.user_id = 1
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Call change password function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await change_password("wrong_password", "new_password", mock_student, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Current password is incorrect" in exc_info.value.detail

class TestCourseSearch:
    """Unit tests for course search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_courses_no_filters(self, test_db):
        """Test course search without filters using real database"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        
        try:
            # Call search function with real database (pass explicit None values)
            result = await search_courses(
                department=None,
                semester=None, 
                year=None,
                keyword=None,
                db=test_db
            )
            
            # Assertions - should find at least the active courses we created
            assert len(result) >= 3  # We created 3 active courses (1 inactive filtered out)
            
            # Check that courses have expected structure
            course_codes = [course["course_code"] for course in result]
            assert "CS101" in course_codes
            assert "CS201" in course_codes
            
            # Verify each course has required fields
            for course in result:
                assert "course_code" in course
                assert "title" in course
                assert "professor" in course
                assert "enrolled_count" in course
                
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)
    
    @pytest.mark.asyncio
    async def test_search_courses_with_filters(self):
        """Test course search with filters"""
        # Mock database session and query
        mock_db = Mock()
        mock_query = Mock()
        
        # Chain the filter calls
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # Call search function with filters
        result = await search_courses(
            department="Computer Science",
            semester="Fall 2024",
            year=2024,
            keyword="programming",
            db=mock_db
        )
        
        # Verify that filters were applied (filter was called multiple times)
        assert mock_query.filter.call_count >= 4  # One for is_active, plus 4 filters
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_courses_keyword_search(self):
        """Test course search with keyword"""
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # Call search function with keyword (pass explicit None values for other params)
        result = await search_courses(
            department=None,
            semester=None,
            year=None,
            keyword="machine learning",
            db=mock_db
        )
        
        # Verify that keyword filter was applied
        assert mock_query.filter.call_count >= 2  # is_active + keyword filter

class TestCourseEnrollment:
    """Unit tests for course enrollment functionality"""
    
    @pytest.mark.asyncio
    async def test_enroll_in_course_success(self):
        """Test successful course enrollment"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.max_enrollment = 30
        mock_course.is_active = True
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session
        mock_db = Mock()
        
        # Mock course query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        
        # Mock enrollment checks (no existing enrollment, course not full)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_course, None]  # Course exists, no existing enrollment
        mock_db.query.return_value.filter.return_value.count.return_value = 20  # Current enrollment
        
        # Mock enrolled courses query for conflict check
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
        
        # Mock enrollment insertion
        mock_db.execute = Mock()
        mock_db.commit = Mock()
        
        # Create enrollment request
        enrollment_data = EnrollmentCreate(course_id=1)
        
        # Call enrollment function
        result = await enroll_in_course(enrollment_data, mock_student, mock_db)
        
        # Assertions
        assert result["message"] == "Successfully enrolled in course"
        assert result["course_id"] == 1
        
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enroll_in_course_not_found(self):
        """Test enrollment in non-existent course"""
        # Mock database session - no course found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Create enrollment request
        enrollment_data = EnrollmentCreate(course_id=999)
        
        # Call enrollment function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await enroll_in_course(enrollment_data, mock_student, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "Course not found or inactive" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_enroll_in_course_already_enrolled(self):
        """Test enrollment when already enrolled"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.is_active = True
        
        # Mock existing enrollment
        mock_enrollment = Mock()
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_course, mock_enrollment]
        
        # Create enrollment request
        enrollment_data = EnrollmentCreate(course_id=1)
        
        # Call enrollment function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await enroll_in_course(enrollment_data, mock_student, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Already enrolled in this course" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_enroll_in_course_full(self):
        """Test enrollment when course is full"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.max_enrollment = 30
        mock_course.is_active = True
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session
        mock_db = Mock()
        
        # Mock queries: course exists, no existing enrollment, but course is full
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_course, None]
        mock_db.query.return_value.filter.return_value.count.return_value = 30  # Course is full
        
        # Create enrollment request
        enrollment_data = EnrollmentCreate(course_id=1)
        
        # Call enrollment function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await enroll_in_course(enrollment_data, mock_student, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Course is full" in exc_info.value.detail

class TestEnrolledCourses:
    """Unit tests for getting enrolled courses"""
    
    @pytest.mark.asyncio
    async def test_get_enrolled_courses_success(self, test_db):
        """Test getting enrolled courses using real database"""
        # Setup test data
        test_data = mock_data_manager.setup_complete_test_data(test_db)
        student = test_data['student']
        
        try:
            # Call function with real student and database
            result = await get_enrolled_courses(student, test_db)
            
            # Assertions - student should be enrolled in at least one course
            assert len(result) >= 1
            
            # Check the enrolled course structure
            enrolled_course = result[0]
            assert "course_code" in enrolled_course
            assert "title" in enrolled_course
            assert "professor" in enrolled_course
            assert "enrolled_count" in enrolled_course
            
            # Verify it's the course we enrolled the student in
            assert enrolled_course["course_code"] == "CS101"
            
        finally:
            # Cleanup
            mock_data_manager.cleanup_all_data(test_db)

class TestCourseWithdrawal:
    """Unit tests for course withdrawal"""
    
    @pytest.mark.asyncio
    async def test_withdraw_from_course_success(self):
        """Test successful course withdrawal"""
        # Mock enrollment
        mock_enrollment = Mock()
        
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_enrollment, mock_course]
        mock_db.execute = Mock()
        mock_db.commit = Mock()
        
        # Call withdrawal function
        result = await withdraw_from_course(1, mock_student, mock_db)
        
        # Assertions
        assert result["message"] == "Successfully withdrawn from course"
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_withdraw_from_course_not_enrolled(self):
        """Test withdrawal when not enrolled"""
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session - no enrollment found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Call withdrawal function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await withdraw_from_course(1, mock_student, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "Not enrolled in this course" in exc_info.value.detail

class TestStudentSchedule:
    """Unit tests for student schedule functionality"""
    
    @pytest.mark.asyncio
    async def test_get_student_schedule_success(self):
        """Test getting student schedule"""
        # Mock enrolled courses
        mock_course1 = Mock()
        mock_course1.id = 1
        mock_course1.course_code = "CS101"
        mock_course1.title = "Programming"
        mock_course1.credits = 3
        mock_course1.semester = "Fall 2024"
        mock_course1.year = 2024
        mock_course1.schedule = '{"days": ["MWF"], "time": "10:00-11:00"}'
        mock_course1.professor_id = 1
        
        # Mock professor
        mock_professor = Mock()
        mock_professor.first_name = "Dr. Jane"
        mock_professor.last_name = "Smith"
        
        # Mock current student
        mock_student = Mock()
        mock_student.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course1]
        mock_db.query.return_value = mock_query
        
        # Mock professor query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_professor
        
        # Call schedule function
        result = await get_student_schedule(
            semester="Fall 2024",
            year=2024,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        assert len(result["schedule"]) == 1
        assert result["schedule"][0]["course_code"] == "CS101"
        assert result["schedule"][0]["professor_name"] == "Dr. Jane Smith"
        assert result["total_credits"] == 3
        assert "conflicts" in result

if __name__ == "__main__":
    pytest.main([__file__])
