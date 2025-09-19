"""
Unit tests for Academic Record Service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.academic_record_service import AcademicRecordService
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate,
    TranscriptGenerationRequest, GPACalculationResponse
)
from models.academic_record import GradeStatus, TranscriptStatus

class TestAcademicRecordService:
    """Test AcademicRecordService class"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db, mock_repository):
        """Create service instance with mocked dependencies"""
        with patch('services.academic_record_service.AcademicRecordRepository', return_value=mock_repository):
            return AcademicRecordService(mock_db)
    
    def test_create_academic_record_success(self, service, mock_repository):
        """Test successful academic record creation"""
        # Arrange
        record_data = AcademicRecordCreate(
            course_id=1,
            semester="Fall",
            year=2024,
            letter_grade="A",
            numeric_grade=4.0,
            credits_earned=3,
            credits_attempted=3,
            status=GradeStatus.GRADED
        )
        student_id = 1
        
        mock_record = Mock()
        mock_record.id = 1
        mock_record.student_id = student_id
        mock_record.semester = "Fall"
        mock_record.year = 2024
        mock_record.status = GradeStatus.GRADED
        
        mock_repository.create_academic_record.return_value = mock_record
        
        # Act
        result = service.create_academic_record(record_data, student_id)
        
        # Assert
        mock_repository.create_academic_record.assert_called_once_with(record_data, student_id)
        mock_repository._update_semester_gpa.assert_called_once_with(student_id, "Fall", 2024)
        mock_repository._update_academic_progress.assert_called_once_with(student_id)
        assert result is not None
    
    def test_create_academic_record_validation_error(self, service):
        """Test academic record creation with validation error"""
        # Arrange
        record_data = AcademicRecordCreate(
            course_id=1,
            semester="Fall",
            year=2024,
            letter_grade="A",
            numeric_grade=3.0,  # Mismatched with letter grade
            credits_earned=3,
            credits_attempted=3,
            status=GradeStatus.GRADED
        )
        student_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Letter grade and numeric grade do not match"):
            service.create_academic_record(record_data, student_id)
    
    def test_get_student_grades(self, service, mock_repository):
        """Test getting student grades"""
        # Arrange
        student_id = 1
        semester = "Fall"
        year = 2024
        
        mock_records = [Mock(), Mock()]
        mock_repository.get_student_academic_records.return_value = mock_records
        
        # Act
        result = service.get_student_grades(student_id, semester, year)
        
        # Assert
        mock_repository.get_student_academic_records.assert_called_once_with(student_id, semester, year, None)
        assert len(result) == 2
    
    def test_calculate_gpa(self, service, mock_repository):
        """Test GPA calculation"""
        # Arrange
        student_id = 1
        
        cumulative_data = {
            "cumulative_gpa": 3.5,
            "total_quality_points": 105.0,
            "total_credits_earned": 30,
            "total_credits_attempted": 30,
            "grade_distribution": {"A": 5, "B": 3}
        }
        
        major_data = {
            "major_gpa": 3.7,
            "total_quality_points": 55.5,
            "total_credits_attempted": 15
        }
        
        mock_semester_gpas = [Mock(), Mock()]
        
        mock_repository.calculate_cumulative_gpa.return_value = cumulative_data
        mock_repository.calculate_major_gpa.return_value = major_data
        mock_repository.get_student_semester_gpas.return_value = mock_semester_gpas
        
        # Mock student for major
        mock_student = Mock()
        mock_student.major = "Computer Science"
        service.db.query.return_value.filter.return_value.first.return_value = mock_student
        
        # Act
        result = service.calculate_gpa(student_id)
        
        # Assert
        assert isinstance(result, GPACalculationResponse)
        assert result.cumulative_gpa == 3.5
        assert result.major_gpa == 3.7
        mock_repository.calculate_cumulative_gpa.assert_called_once_with(student_id)
        mock_repository.calculate_major_gpa.assert_called_once_with(student_id, "Computer Science")
    
    def test_generate_transcript(self, service, mock_repository):
        """Test transcript generation"""
        # Arrange
        student_id = 1
        request = TranscriptGenerationRequest(transcript_type="official")
        
        mock_student = Mock()
        mock_student.id = student_id
        mock_student.student_id = "STU001"
        mock_student.first_name = "John"
        mock_student.last_name = "Doe"
        mock_student.major = "Computer Science"
        
        mock_transcript = Mock()
        mock_transcript.id = 1
        mock_transcript.generated_date = datetime.now()
        
        service.db.query.return_value.filter.return_value.first.return_value = mock_student
        mock_repository.create_transcript.return_value = mock_transcript
        
        # Mock GPA calculation
        with patch.object(service, 'calculate_gpa') as mock_calculate_gpa:
            mock_gpa_response = Mock()
            mock_gpa_response.total_credits_earned = 60
            mock_gpa_response.total_credits_attempted = 60
            mock_gpa_response.cumulative_gpa = 3.5
            mock_gpa_response.major_gpa = 3.7
            mock_calculate_gpa.return_value = mock_gpa_response
            
            # Mock grade history
            mock_repository.get_grade_history.return_value = []
            
            # Mock file generation
            with patch.object(service, '_generate_transcript_file', return_value="/path/to/file.txt"):
                with patch.object(service, '_calculate_file_hash', return_value="hash123"):
                    # Act
                    result = service.generate_transcript(student_id, request)
                    
                    # Assert
                    assert result.transcript_id == 1
                    assert result.status == "generated"
                    mock_repository.create_transcript.assert_called_once()
    
    def test_get_academic_progress_summary(self, service, mock_repository):
        """Test getting academic progress summary"""
        # Arrange
        student_id = 1
        
        mock_progress = Mock()
        mock_progress.student_id = student_id
        mock_progress.degree_program = "Bachelor of Science"
        mock_progress.major = "Computer Science"
        mock_progress.catalog_year = 2022
        mock_progress.total_credits_earned = 60
        mock_progress.total_credits_required = 120
        mock_progress.cumulative_gpa = 3.5
        mock_progress.major_gpa = 3.7
        mock_progress.expected_graduation_date = None
        mock_progress.completed_requirements = '["req1", "req2"]'
        mock_progress.remaining_requirements = '["req3", "req4"]'
        mock_progress.warnings = '[]'
        
        mock_repository.get_academic_progress_by_student_id.return_value = mock_progress
        
        # Act
        result = service.get_academic_progress_summary(student_id)
        
        # Assert
        assert result.student_id == student_id
        assert result.degree_program == "Bachelor of Science"
        assert result.major == "Computer Science"
        assert result.total_credits_earned == 60
        assert result.total_credits_required == 120
        assert result.credits_remaining == 60
        assert result.completion_percentage == 50.0
        assert result.cumulative_gpa == 3.5
    
    def test_get_academic_progress_summary_not_found(self, service, mock_repository):
        """Test getting academic progress summary when not found"""
        # Arrange
        student_id = 1
        mock_repository.get_academic_progress_by_student_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Academic progress not found for student"):
            service.get_academic_progress_summary(student_id)
    
    def test_letter_grade_to_numeric(self, service):
        """Test letter grade to numeric conversion"""
        # Test various letter grades
        assert service._letter_grade_to_numeric("A+") == 4.0
        assert service._letter_grade_to_numeric("A") == 4.0
        assert service._letter_grade_to_numeric("A-") == 3.7
        assert service._letter_grade_to_numeric("B+") == 3.3
        assert service._letter_grade_to_numeric("B") == 3.0
        assert service._letter_grade_to_numeric("B-") == 2.7
        assert service._letter_grade_to_numeric("C+") == 2.3
        assert service._letter_grade_to_numeric("C") == 2.0
        assert service._letter_grade_to_numeric("C-") == 1.7
        assert service._letter_grade_to_numeric("D+") == 1.3
        assert service._letter_grade_to_numeric("D") == 1.0
        assert service._letter_grade_to_numeric("D-") == 0.7
        assert service._letter_grade_to_numeric("F") == 0.0
        assert service._letter_grade_to_numeric("P") == 4.0
        assert service._letter_grade_to_numeric("NP") == 0.0
        assert service._letter_grade_to_numeric("INVALID") == 0.0
    
    def test_assess_academic_progress_on_track(self, service):
        """Test academic progress assessment - on track"""
        # Arrange
        mock_progress = Mock()
        mock_progress.cumulative_gpa = 3.2
        mock_progress.total_credits_earned = 90
        mock_progress.total_credits_required = 120
        
        # Act
        result = service._assess_academic_progress(mock_progress)
        
        # Assert
        assert result is True
    
    def test_assess_academic_progress_not_on_track_gpa(self, service):
        """Test academic progress assessment - not on track due to low GPA"""
        # Arrange
        mock_progress = Mock()
        mock_progress.cumulative_gpa = 1.8  # Below 2.0
        mock_progress.total_credits_earned = 90
        mock_progress.total_credits_required = 120
        
        # Act
        result = service._assess_academic_progress(mock_progress)
        
        # Assert
        assert result is False
    
    def test_assess_academic_progress_not_on_track_time(self, service):
        """Test academic progress assessment - not on track due to time"""
        # Arrange
        mock_progress = Mock()
        mock_progress.cumulative_gpa = 3.2
        mock_progress.total_credits_earned = 30  # Too few credits
        mock_progress.total_credits_required = 120
        
        # Act
        result = service._assess_academic_progress(mock_progress)
        
        # Assert
        assert result is False
