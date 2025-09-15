"""
Unit Tests for Professor Controller
Tests professor profile management and course administration functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from controllers.professor_controller import (
    update_professor_profile, change_password, get_teaching_load,
    create_course, get_professor_courses, update_course, delete_course,
    get_course_students, remove_student_from_course, get_course_enrollment_stats
)
from schemas.student_schemas import ProfessorUpdate, CourseCreate, CourseUpdate
from models import Professor, Course, Student, User

class TestProfessorProfileManagement:
    """Unit tests for professor profile management"""
    
    def test_update_professor_profile_success(self):
        """Test successful professor profile update"""
        # Mock current professor
        mock_professor = Mock()
        mock_professor.first_name = "Dr. Jane"
        mock_professor.last_name = "Smith"
        mock_professor.office_hours = "MWF 2-4 PM"
        mock_professor.specialization = "Machine Learning"
        
        # Mock database session
        mock_db = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Create update data
        update_data = ProfessorUpdate(
            office_hours="TTH 1-3 PM",
            specialization="Deep Learning"
        )
        
        # Call update function
        result = update_professor_profile(update_data, mock_professor, mock_db)
        
        # Assertions
        assert mock_professor.office_hours == "TTH 1-3 PM"
        assert mock_professor.specialization == "Deep Learning"
        assert mock_professor.first_name == "Dr. Jane"  # Unchanged
        assert result == mock_professor
        
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_professor)
    
    @patch('controllers.professor_controller.verify_password')
    @patch('controllers.professor_controller.get_password_hash')
    def test_change_password_success(self, mock_hash_password, mock_verify_password):
        """Test successful password change"""
        # Mock password verification and hashing
        mock_verify_password.return_value = True
        mock_hash_password.return_value = "new_hashed_password"
        
        # Mock current professor and user
        mock_professor = Mock()
        mock_professor.user_id = 1
        
        mock_user = Mock()
        mock_user.hashed_password = "old_hashed_password"
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit = Mock()
        
        # Call change password function
        result = change_password("old_password", "new_password", mock_professor, mock_db)
        
        # Assertions
        assert result["message"] == "Password updated successfully"
        assert mock_user.hashed_password == "new_hashed_password"
        
        mock_verify_password.assert_called_once_with("old_password", "old_hashed_password")
        mock_hash_password.assert_called_once_with("new_password")
        mock_db.commit.assert_called_once()

class TestTeachingLoad:
    """Unit tests for teaching load functionality"""
    
    def test_get_teaching_load_success(self):
        """Test getting teaching load"""
        # Mock courses
        mock_course1 = Mock()
        mock_course1.id = 1
        mock_course1.course_code = "CS101"
        mock_course1.title = "Programming"
        mock_course1.credits = 3
        mock_course1.max_enrollment = 30
        mock_course1.schedule = '{"days": ["MWF"], "time": "10:00-11:00"}'
        mock_course1.semester = "Fall 2024"
        mock_course1.year = 2024
        
        mock_course2 = Mock()
        mock_course2.id = 2
        mock_course2.course_code = "CS102"
        mock_course2.title = "Data Structures"
        mock_course2.credits = 4
        mock_course2.max_enrollment = 25
        mock_course2.schedule = '{"days": ["TTH"], "time": "2:00-3:30"}'
        mock_course2.semester = "Fall 2024"
        mock_course2.year = 2024
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        mock_professor.department = "Computer Science"
        
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course1, mock_course2]
        mock_db.query.return_value = mock_query
        
        # Mock enrollment counts
        mock_db.query.return_value.filter.return_value.count.side_effect = [20, 15]
        
        # Call teaching load function
        result = get_teaching_load(
            semester="Fall 2024",
            year=2024,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        assert len(result["courses"]) == 2
        assert result["total_courses"] == 2
        assert result["total_credits"] == 7  # 3 + 4
        assert result["total_students"] == 35  # 20 + 15
        assert result["department"] == "Computer Science"
        assert result["courses"][0]["course_code"] == "CS101"
        assert result["courses"][0]["enrolled_count"] == 20

class TestCourseCreation:
    """Unit tests for course creation"""
    
    def test_create_course_success(self):
        """Test successful course creation"""
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing course
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Mock the created course
        mock_created_course = Mock()
        mock_created_course.id = 1
        mock_created_course.course_code = "CS101"
        mock_created_course.title = "Programming"
        mock_created_course.enrolled_count = 0
        
        # Configure refresh to set the course
        def set_course(course):
            course.id = 1
        mock_db.refresh.side_effect = set_course
        
        # Create course data
        course_data = CourseCreate(
            course_code="CS101",
            title="Introduction to Programming",
            description="Learn programming basics",
            credits=3,
            department="Computer Science",
            semester="Fall 2024",
            year=2024,
            max_enrollment=30
        )
        
        # Call create course function
        result = create_course(course_data, mock_professor, mock_db)
        
        # Assertions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_course_duplicate(self):
        """Test course creation with duplicate course code"""
        # Mock existing course
        mock_existing_course = Mock()
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session - existing course found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing_course
        
        # Create course data
        course_data = CourseCreate(
            course_code="CS101",
            title="Programming",
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        # Call create course function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            create_course(course_data, mock_professor, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Course with this code already exists" in exc_info.value.detail

class TestCourseManagement:
    """Unit tests for course management"""
    
    def test_get_professor_courses_success(self):
        """Test getting professor's courses"""
        # Mock courses
        mock_course1 = Mock()
        mock_course1.id = 1
        mock_course1.course_code = "CS101"
        mock_course1.title = "Programming"
        mock_course1.credits = 3
        mock_course1.professor_id = 1
        mock_course1.department = "CS"
        mock_course1.semester = "Fall 2024"
        mock_course1.year = 2024
        mock_course1.max_enrollment = 30
        mock_course1.is_active = True
        mock_course1.created_at = datetime.now()
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_course1]
        mock_db.query.return_value = mock_query
        
        # Mock enrollment count
        mock_db.query.return_value.filter.return_value.count.return_value = 25
        
        # Call function
        result = get_professor_courses(
            semester="Fall 2024",
            year=2024,
            include_inactive=False,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        assert len(result) == 1
        assert result[0]["course_code"] == "CS101"
        assert result[0]["enrolled_count"] == 25
    
    def test_update_course_success(self):
        """Test successful course update"""
        # Mock course owned by professor
        mock_course = Mock()
        mock_course.id = 1
        mock_course.professor_id = 1
        mock_course.title = "Old Title"
        mock_course.max_enrollment = 30
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.query.return_value.filter.return_value.count.return_value = 20
        
        # Create update data
        update_data = CourseUpdate(
            title="New Title",
            max_enrollment=25
        )
        
        # Call update function
        result = update_course(1, update_data, mock_professor, mock_db)
        
        # Assertions
        assert mock_course.title == "New Title"
        assert mock_course.max_enrollment == 25
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_course_not_owned(self):
        """Test course update when course is not owned by professor"""
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session - no course found for this professor
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Create update data
        update_data = CourseUpdate(title="New Title")
        
        # Call update function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            update_course(1, update_data, mock_professor, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "Course not found or you don't have permission" in exc_info.value.detail
    
    def test_delete_course_success(self):
        """Test successful course deletion (deactivation)"""
        # Mock course with no enrolled students
        mock_course = Mock()
        mock_course.id = 1
        mock_course.professor_id = 1
        mock_course.is_active = True
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_db.query.return_value.filter.return_value.count.return_value = 0  # No enrolled students
        mock_db.commit = Mock()
        
        # Call delete function
        result = delete_course(1, mock_professor, mock_db)
        
        # Assertions
        assert result["message"] == "Course deactivated successfully"
        assert mock_course.is_active is False
        mock_db.commit.assert_called_once()
    
    def test_delete_course_with_students(self):
        """Test course deletion with enrolled students"""
        # Mock course with enrolled students
        mock_course = Mock()
        mock_course.id = 1
        mock_course.professor_id = 1
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_db.query.return_value.filter.return_value.count.return_value = 5  # Has enrolled students
        
        # Call delete function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            delete_course(1, mock_professor, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Cannot delete course with enrolled students" in exc_info.value.detail

class TestEnrollmentManagement:
    """Unit tests for enrollment management"""
    
    def test_get_course_students_success(self):
        """Test getting students enrolled in course"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.course_code = "CS101"
        mock_course.title = "Programming"
        mock_course.professor_id = 1
        mock_course.credits = 3
        mock_course.department = "CS"
        mock_course.semester = "Fall 2024"
        mock_course.year = 2024
        mock_course.max_enrollment = 30
        mock_course.is_active = True
        mock_course.created_at = datetime.now()
        
        # Mock enrolled students
        mock_student1 = Mock()
        mock_student1.id = 1
        mock_student1.student_id = "STU001"
        mock_student1.first_name = "John"
        mock_student1.last_name = "Doe"
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_student1]
        
        # Call function
        result = get_course_students(1, mock_professor, mock_db)
        
        # Assertions
        assert result["course_code"] == "CS101"
        assert len(result["enrolled_students"]) == 1
        assert result["enrolled_count"] == 1
        assert result["enrolled_students"][0] == mock_student1
    
    def test_remove_student_from_course_success(self):
        """Test successful student removal from course"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.professor_id = 1
        
        # Mock enrollment
        mock_enrollment = Mock()
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_course, mock_enrollment]
        mock_db.execute = Mock()
        mock_db.commit = Mock()
        
        # Call function
        result = remove_student_from_course(1, 1, mock_professor, mock_db)
        
        # Assertions
        assert result["message"] == "Student removed from course successfully"
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_remove_student_not_enrolled(self):
        """Test removing student who is not enrolled"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.professor_id = 1
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_course, None]  # No enrollment
        
        # Call function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            remove_student_from_course(1, 1, mock_professor, mock_db)
        
        assert exc_info.value.status_code == 404
        assert "Student not enrolled in this course" in exc_info.value.detail

class TestEnrollmentStatistics:
    """Unit tests for enrollment statistics"""
    
    def test_get_course_enrollment_stats_success(self):
        """Test getting course enrollment statistics"""
        # Mock course
        mock_course = Mock()
        mock_course.id = 1
        mock_course.course_code = "CS101"
        mock_course.title = "Programming"
        mock_course.professor_id = 1
        mock_course.max_enrollment = 30
        
        # Mock enrolled students with different year levels
        mock_student1 = Mock()
        mock_student1.year_level = "Junior"
        
        mock_student2 = Mock()
        mock_student2.year_level = "Senior"
        
        mock_student3 = Mock()
        mock_student3.year_level = "Junior"
        
        # Mock current professor
        mock_professor = Mock()
        mock_professor.id = 1
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_student1, mock_student2, mock_student3
        ]
        
        # Call function
        result = get_course_enrollment_stats(1, mock_professor, mock_db)
        
        # Assertions
        assert result["course_code"] == "CS101"
        assert result["total_enrolled"] == 3
        assert result["max_enrollment"] == 30
        assert result["enrollment_percentage"] == 10.0  # 3/30 * 100
        assert result["available_spots"] == 27
        assert result["year_level_distribution"]["Junior"] == 2
        assert result["year_level_distribution"]["Senior"] == 1

if __name__ == "__main__":
    pytest.main([__file__])
