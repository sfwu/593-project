"""
Unit Tests for Academic Record Controller
Tests API endpoints for academic record access
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from controllers.academic_record_controller import router
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate, AcademicRecordResponse,
    TranscriptCreate, TranscriptUpdate, TranscriptResponse,
    AcademicProgressCreate, AcademicProgressUpdate, AcademicProgressResponse,
    SemesterGPAResponse, GPACalculationResponse, TranscriptGenerationRequest,
    TranscriptGenerationResponse, AcademicProgressSummary, StudentGradeHistory,
    GradeStatus, TranscriptStatus
)
from models.student import Student
from models.user import User, UserRole

class TestAcademicRecordController:
    """Unit tests for Academic Record Controller"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def mock_student(self):
        """Mock student user"""
        student = Mock(spec=Student)
        student.id = 1
        student.user_id = 1
        student.student_id = "STU001"
        student.first_name = "John"
        student.last_name = "Doe"
        return student
    
    @pytest.fixture
    def mock_academic_record_response(self):
        """Mock academic record response"""
        return AcademicRecordResponse(
            id=1,
            student_id=1,
            course_id=1,
            semester="Fall",
            year=2024,
            letter_grade="A",
            numeric_grade=4.0,
            percentage_grade=95.0,
            credits_earned=3,
            credits_attempted=3,
            status=GradeStatus.GRADED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_gpa_response(self):
        """Mock GPA calculation response"""
        return GPACalculationResponse(
            cumulative_gpa=3.5,
            major_gpa=3.7,
            semester_gpa=3.6,
            total_credits_earned=60,
            total_credits_attempted=60,
            total_quality_points=210.0,
            semester_breakdown=[],
            grade_distribution={"A": 5, "B": 3}
        )
    
    @pytest.fixture
    def mock_transcript_response(self):
        """Mock transcript response"""
        return TranscriptResponse(
            id=1,
            student_id=1,
            transcript_type="official",
            status=TranscriptStatus.OFFICIAL,
            generated_date=datetime.now(),
            requested_date=datetime.now(),
            total_credits_earned=60,
            total_credits_attempted=60,
            cumulative_gpa=3.5,
            major_gpa=3.7,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_academic_progress_response(self):
        """Mock academic progress response"""
        return AcademicProgressResponse(
            id=1,
            student_id=1,
            degree_program="Bachelor of Science in Computer Science",
            major="Computer Science",
            catalog_year=2022,
            total_credits_required=120,
            major_credits_required=60,
            general_education_credits_required=30,
            elective_credits_required=30,
            total_credits_earned=60,
            major_credits_earned=30,
            general_education_credits_earned=15,
            elective_credits_earned=15,
            cumulative_gpa=3.5,
            major_gpa=3.7,
            semester_gpa=3.6,
            is_on_track=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_student_grades_success(self, mock_service_class, mock_db, mock_student, mock_academic_record_response):
        """Test successful retrieval of student grades"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_grades.return_value = [mock_academic_record_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_student_grades
        
        # Call the function
        result = await get_student_grades(
            semester="Fall",
            year=2024,
            status=GradeStatus.GRADED,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_grades.assert_called_once_with(1, "Fall", 2024, GradeStatus.GRADED)
        assert result == [mock_academic_record_response]
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_student_grades_no_filters(self, mock_service_class, mock_db, mock_student, mock_academic_record_response):
        """Test retrieval of student grades without filters"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_grades.return_value = [mock_academic_record_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_student_grades
        
        # Call the function without filters
        result = await get_student_grades(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions - Note: FastAPI Query parameters are wrapped in Query objects
        mock_service.get_student_grades.assert_called_once()
        call_args = mock_service.get_student_grades.call_args[0]
        assert call_args[0] == 1  # student_id
        assert result == [mock_academic_record_response]
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_grade_details_success(self, mock_service_class, mock_db, mock_student, mock_academic_record_response):
        """Test successful retrieval of specific grade details"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_grades.return_value = [mock_academic_record_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_grade_details
        
        # Call the function
        result = await get_grade_details(
            record_id=1,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_grades.assert_called_once_with(1)
        assert result == mock_academic_record_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_grade_details_not_found(self, mock_service_class, mock_db, mock_student):
        """Test grade details not found"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_grades.return_value = []
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_grade_details
        
        # Call the function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_grade_details(
                record_id=999,
                current_student=mock_student,
                db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Grade record not found" in str(exc_info.value.detail)
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_update_grade_success(self, mock_service_class, mock_db, mock_student, mock_academic_record_response):
        """Test successful grade update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_grade.return_value = mock_academic_record_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import update_grade
        
        # Create update data - students can only update their own notes
        update_data = AcademicRecordUpdate(
            student_notes="Updated my notes for this course"
        )
        
        # Call the function
        result = await update_grade(
            record_id=1,
            grade_data=update_data,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_grade.assert_called_once_with(1, update_data, 1)
        assert result == mock_academic_record_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_gpa_calculation(self, mock_service_class, mock_db, mock_student, mock_gpa_response):
        """Test GPA calculation retrieval"""
        # Mock service instance
        mock_service = Mock()
        mock_service.calculate_gpa.return_value = mock_gpa_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_gpa_calculation
        
        # Call the function
        result = await get_gpa_calculation(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.calculate_gpa.assert_called_once_with(1)
        assert result == mock_gpa_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_semester_gpa_breakdown(self, mock_service_class, mock_db, mock_student):
        """Test semester GPA breakdown retrieval"""
        # Mock service instance
        mock_service = Mock()
        mock_semester_gpa = SemesterGPAResponse(
            id=1,
            student_id=1,
            semester="Fall",
            year=2024,
            semester_gpa=3.5,
            credits_earned=15,
            credits_attempted=15,
            quality_points=52.5,
            courses_completed=5,
            courses_attempted=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.get_semester_gpa_breakdown.return_value = [mock_semester_gpa]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_semester_gpa_breakdown
        
        # Call the function
        result = await get_semester_gpa_breakdown(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_semester_gpa_breakdown.assert_called_once_with(1)
        assert result == [mock_semester_gpa]
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_generate_transcript_success(self, mock_service_class, mock_db, mock_student, mock_transcript_response):
        """Test successful transcript generation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.generate_transcript.return_value = mock_transcript_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import generate_transcript
        
        # Create request data
        request_data = TranscriptGenerationRequest(
            transcript_type="official",
            include_incomplete=True,
            include_withdrawn=False
        )
        
        # Call the function
        result = await generate_transcript(
            request=request_data,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.generate_transcript.assert_called_once_with(1, request_data)
        assert result == mock_transcript_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_transcripts(self, mock_service_class, mock_db, mock_student, mock_transcript_response):
        """Test retrieval of student transcripts"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_transcripts.return_value = [mock_transcript_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_student_transcripts
        
        # Call the function
        result = await get_student_transcripts(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_transcripts.assert_called_once_with(1)
        assert result == [mock_transcript_response]
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_academic_progress(self, mock_service_class, mock_db, mock_student, mock_academic_progress_response):
        """Test retrieval of academic progress"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_academic_progress.return_value = mock_academic_progress_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_academic_progress
        
        # Call the function
        result = await get_academic_progress(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_academic_progress.assert_called_once_with(1)
        assert result == mock_academic_progress_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_update_academic_progress(self, mock_service_class, mock_db, mock_student, mock_academic_progress_response):
        """Test academic progress update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_academic_progress.return_value = mock_academic_progress_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import update_academic_progress
        
        # Create update data
        update_data = AcademicProgressUpdate(
            expected_graduation_date=datetime(2025, 5, 15)
        )
        
        # Call the function
        result = await update_academic_progress(
            progress_data=update_data,
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_academic_progress.assert_called_once_with(1, update_data)
        assert result == mock_academic_progress_response
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_grade_history(self, mock_service_class, mock_db, mock_student):
        """Test retrieval of grade history"""
        # Mock service instance
        mock_service = Mock()
        mock_grade_history = StudentGradeHistory(
            student_id=1,
            total_courses=10,
            courses_completed=8,
            courses_incomplete=1,
            courses_withdrawn=1,
            cumulative_gpa=3.5,
            major_gpa=3.7,
            grade_summary=[],
            semester_breakdown=[]
        )
        mock_service.get_grade_history.return_value = mock_grade_history
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_grade_history
        
        # Call the function
        result = await get_grade_history(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_grade_history.assert_called_once_with(1)
        assert result == mock_grade_history
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_academic_summary(self, mock_service_class, mock_db, mock_student):
        """Test retrieval of academic summary"""
        # Mock service instance
        mock_service = Mock()
        
        # Mock GPA data
        mock_gpa_data = Mock()
        mock_gpa_data.cumulative_gpa = 3.5
        mock_gpa_data.major_gpa = 3.7
        mock_gpa_data.semester_gpa = 3.6
        mock_gpa_data.total_credits_earned = 60
        mock_gpa_data.total_credits_attempted = 60
        mock_gpa_data.grade_distribution = {"A": 5, "B": 3}
        mock_gpa_data.semester_breakdown = []
        
        # Mock progress summary
        mock_progress_summary = Mock()
        mock_progress_summary.dict.return_value = {"completion_percentage": 50.0}
        
        # Mock grade history
        mock_grade_history = Mock()
        mock_grade_history.total_courses = 20
        mock_grade_history.courses_completed = 18
        mock_grade_history.courses_incomplete = 1
        mock_grade_history.courses_withdrawn = 1
        
        mock_service.calculate_gpa.return_value = mock_gpa_data
        mock_service.get_academic_progress_summary.return_value = mock_progress_summary
        mock_service.get_grade_history.return_value = mock_grade_history
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_academic_summary
        
        # Call the function
        result = await get_academic_summary(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.calculate_gpa.assert_called_once_with(1)
        mock_service.get_academic_progress_summary.assert_called_once_with(1)
        mock_service.get_grade_history.assert_called_once_with(1)
        assert result is not None
    
    @patch('controllers.academic_record_controller.AcademicRecordService')
    @pytest.mark.asyncio
    async def test_get_dashboard(self, mock_service_class, mock_db, mock_student):
        """Test retrieval of academic dashboard"""
        # Mock service instance
        mock_service = Mock()
        
        # Mock GPA data
        mock_gpa_data = Mock()
        mock_gpa_data.cumulative_gpa = 3.5
        mock_gpa_data.major_gpa = 3.7
        mock_gpa_data.semester_gpa = 3.6
        mock_gpa_data.total_credits_earned = 60
        mock_gpa_data.total_credits_attempted = 60
        mock_gpa_data.grade_distribution = {"A": 5, "B": 3}
        
        # Mock recent grades
        mock_recent_grade = Mock()
        mock_recent_grade.dict.return_value = {"course": "CS101", "grade": "A"}
        mock_recent_grades = [mock_recent_grade]
        
        # Mock progress summary
        mock_progress_summary = Mock()
        mock_progress_summary.is_on_track = True
        mock_progress_summary.dict.return_value = {"completion_percentage": 50.0}
        
        # Mock semester breakdown
        mock_semester = Mock()
        mock_semester.dict.return_value = {"semester": "Fall 2024", "gpa": 3.5}
        mock_semester_breakdown = [mock_semester]
        
        mock_service.calculate_gpa.return_value = mock_gpa_data
        mock_service.get_student_grades.return_value = mock_recent_grades
        mock_service.get_academic_progress_summary.return_value = mock_progress_summary
        mock_service.get_semester_gpa_breakdown.return_value = mock_semester_breakdown
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.academic_record_controller import get_academic_dashboard
        
        # Call the function
        result = await get_academic_dashboard(
            current_student=mock_student,
            db=mock_db
        )
        
        # Assertions
        mock_service.calculate_gpa.assert_called_once_with(1)
        mock_service.get_student_grades.assert_called_once_with(1)
        mock_service.get_academic_progress_summary.assert_called_once_with(1)
        mock_service.get_semester_gpa_breakdown.assert_called_once_with(1)
        assert result is not None

if __name__ == "__main__":
    pytest.main([__file__])
