"""
Unit Tests for Grading and Assessment Controller
Tests API endpoints for grading and assessment management
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, date, time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from controllers.grading_assessment_controller import router
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentSubmissionCreate, AssignmentSubmissionResponse,
    ExamCreate, ExamUpdate, ExamResponse,
    ExamSessionCreate, ExamSessionResponse,
    GradeCreate, GradeUpdate, GradeResponse,
    GradebookCreate, GradebookUpdate, GradebookResponse,
    GradebookEntryResponse, GradeStatisticsResponse,
    GradeModificationCreate, GradeModificationResponse,
    BulkGradeCreate, BulkAssignmentCreate,
    AssignmentType, ExamType, GradeStatus, SubmissionStatus
)
from models.professor import Professor
from models.user import User, UserRole

class TestGradingAssessmentController:
    """Unit tests for Grading and Assessment Controller"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def mock_professor(self):
        """Mock professor user"""
        professor = Mock(spec=Professor)
        professor.id = 1
        professor.user_id = 1
        professor.professor_id = "PROF001"
        professor.first_name = "Dr. Jane"
        professor.last_name = "Smith"
        professor.department = "Computer Science"
        return professor
    
    @pytest.fixture
    def mock_assignment_response(self):
        """Mock assignment response"""
        return AssignmentResponse(
            id=1,
            course_id=1,
            professor_id=1,
            title="Programming Assignment 1",
            description="Implement a simple calculator",
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59),
            is_published=False,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_exam_response(self):
        """Mock exam response"""
        return ExamResponse(
            id=1,
            course_id=1,
            professor_id=1,
            title="Midterm Exam",
            description="Comprehensive midterm examination",
            exam_type=ExamType.MIDTERM,
            total_points=100.0,
            weight_percentage=30.0,
            passing_grade=60.0,
            exam_date=date(2024, 11, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration_minutes=120,
            location="Room 101",
            is_online=False,
            proctoring_required=True,
            is_published=False,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_grade_response(self):
        """Mock grade response"""
        return GradeResponse(
            id=1,
            student_id=1,
            course_id=1,
            professor_id=1,
            points_earned=85.0,
            points_possible=100.0,
            percentage=85.0,
            letter_grade="B",
            grade_status=GradeStatus.PUBLISHED,
            is_late=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_gradebook_response(self):
        """Mock gradebook response"""
        return GradebookResponse(
            id=1,
            course_id=1,
            professor_id=1,
            name="CS101 Fall 2024 Gradebook",
            description="Gradebook for Introduction to Computer Science",
            semester="Fall",
            year=2024,
            pass_fail_threshold=60.0,
            assignment_weight=40.0,
            exam_weight=50.0,
            participation_weight=10.0,
            is_published=False,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    # Assignment Management Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_create_assignment_success(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test successful assignment creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_assignment.return_value = mock_assignment_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import create_assignment
        
        # Create assignment data
        assignment_data = AssignmentCreate(
            course_id=1,
            title="Programming Assignment 1",
            description="Implement a simple calculator",
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59)
        )
        
        # Call the function
        result = await create_assignment(
            assignment_data=assignment_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_assignment.assert_called_once_with(assignment_data, 1)
        assert result == mock_assignment_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_create_assignment_validation_error(self, mock_service_class, mock_db, mock_professor):
        """Test assignment creation with validation error"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_assignment.side_effect = ValueError("Invalid assignment data")
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import create_assignment
        
        # Create invalid assignment data
        assignment_data = AssignmentCreate(
            course_id=1,
            title="",  # Invalid empty title
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59)
        )
        
        # Call the function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await create_assignment(
                assignment_data=assignment_data,
                current_professor=mock_professor,
                db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid assignment data" in str(exc_info.value.detail)
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_assignments(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test retrieval of assignments"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_assignments.return_value = [mock_assignment_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_assignments
        
        # Call the function
        result = await get_assignments(
            course_id=1,
            assignment_type=AssignmentType.HOMEWORK,
            is_published=False,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_assignments.assert_called_once()
        assert result == [mock_assignment_response]
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_assignment_by_id(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test retrieval of specific assignment"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_assignment_by_id.return_value = mock_assignment_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_assignment_by_id
        
        # Call the function
        result = await get_assignment_by_id(
            assignment_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_assignment_by_id.assert_called_once_with(1)
        assert result == mock_assignment_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_update_assignment(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test assignment update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_assignment.return_value = mock_assignment_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import update_assignment
        
        # Create update data
        update_data = AssignmentUpdate(
            title="Updated Assignment Title",
            description="Updated description",
            total_points=75.0
        )
        
        # Call the function
        result = await update_assignment(
            assignment_id=1,
            assignment_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_assignment.assert_called_once_with(1, update_data)
        assert result == mock_assignment_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_publish_assignment(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test assignment publishing"""
        # Mock service instance
        mock_service = Mock()
        mock_service.publish_assignment.return_value = mock_assignment_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import publish_assignment
        
        # Call the function
        result = await publish_assignment(
            assignment_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.publish_assignment.assert_called_once_with(1)
        assert result == mock_assignment_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_delete_assignment(self, mock_service_class, mock_db, mock_professor):
        """Test assignment deletion"""
        # Mock service instance
        mock_service = Mock()
        mock_service.delete_assignment.return_value = True
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import delete_assignment
        
        # Call the function
        result = await delete_assignment(
            assignment_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.delete_assignment.assert_called_once_with(1)
        assert result == {"message": "Assignment deleted successfully"}

    # Exam Management Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_create_exam_success(self, mock_service_class, mock_db, mock_professor, mock_exam_response):
        """Test successful exam creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_exam.return_value = mock_exam_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import create_exam
        
        # Create exam data
        exam_data = ExamCreate(
            course_id=1,
            title="Midterm Exam",
            description="Comprehensive midterm examination",
            exam_type=ExamType.MIDTERM,
            total_points=100.0,
            weight_percentage=30.0,
            passing_grade=60.0,
            exam_date=date(2024, 11, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration_minutes=120,
            location="Room 101",
            is_online=False,
            proctoring_required=True
        )
        
        # Call the function
        result = await create_exam(
            exam_data=exam_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_exam.assert_called_once_with(exam_data, 1)
        assert result == mock_exam_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_exams(self, mock_service_class, mock_db, mock_professor, mock_exam_response):
        """Test retrieval of exams"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_exams.return_value = [mock_exam_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_exams
        
        # Call the function
        result = await get_exams(
            course_id=1,
            exam_type=ExamType.MIDTERM,
            is_published=False,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_exams.assert_called_once()
        assert result == [mock_exam_response]
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_update_exam(self, mock_service_class, mock_db, mock_professor, mock_exam_response):
        """Test exam update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_exam.return_value = mock_exam_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import update_exam
        
        # Create update data
        update_data = ExamUpdate(
            title="Updated Exam Title",
            location="Room 201",
            is_online=True
        )
        
        # Call the function
        result = await update_exam(
            exam_id=1,
            exam_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_exam.assert_called_once_with(1, update_data)
        assert result == mock_exam_response

    # Grade Management Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_create_grade_success(self, mock_service_class, mock_db, mock_professor, mock_grade_response):
        """Test successful grade creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_grade.return_value = mock_grade_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import create_grade
        
        # Create grade data
        grade_data = GradeCreate(
            student_id=1,
            course_id=1,
            points_earned=85.0,
            points_possible=100.0,
            percentage=85.0,
            letter_grade="B",
            grade_status=GradeStatus.PUBLISHED,
            is_late=False
        )
        
        # Call the function
        result = await create_grade(
            grade_data=grade_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_grade.assert_called_once_with(grade_data, 1)
        assert result == mock_grade_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_grades(self, mock_service_class, mock_db, mock_professor, mock_grade_response):
        """Test retrieval of grades"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_grades.return_value = [mock_grade_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_grades
        
        # Call the function
        result = await get_grades(
            course_id=1,
            student_id=1,
            grade_status=GradeStatus.PUBLISHED,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_grades.assert_called_once()
        assert result == [mock_grade_response]
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_update_grade(self, mock_service_class, mock_db, mock_professor, mock_grade_response):
        """Test grade update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_grade.return_value = mock_grade_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import update_grade
        
        # Create update data
        update_data = GradeUpdate(
            points_earned=90.0,
            percentage=90.0,
            letter_grade="A-",
            professor_comments="Excellent work!"
        )
        
        # Call the function
        result = await update_grade(
            grade_id=1,
            grade_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_grade.assert_called_once_with(1, update_data)
        assert result == mock_grade_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_publish_grade(self, mock_service_class, mock_db, mock_professor, mock_grade_response):
        """Test grade publishing"""
        # Mock service instance
        mock_service = Mock()
        mock_service.publish_grade.return_value = mock_grade_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import publish_grade
        
        # Call the function
        result = await publish_grade(
            grade_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.publish_grade.assert_called_once_with(1)
        assert result == mock_grade_response

    # Gradebook Management Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_create_gradebook_success(self, mock_service_class, mock_db, mock_professor, mock_gradebook_response):
        """Test successful gradebook creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_gradebook.return_value = mock_gradebook_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import create_gradebook
        
        # Create gradebook data
        gradebook_data = GradebookCreate(
            course_id=1,
            name="CS101 Fall 2024 Gradebook",
            description="Gradebook for Introduction to Computer Science",
            semester="Fall",
            year=2024,
            pass_fail_threshold=60.0,
            assignment_weight=40.0,
            exam_weight=50.0,
            participation_weight=10.0,
            allow_student_view=True
        )
        
        # Call the function
        result = await create_gradebook(
            gradebook_data=gradebook_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_gradebook.assert_called_once_with(gradebook_data, 1)
        assert result == mock_gradebook_response
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_gradebooks(self, mock_service_class, mock_db, mock_professor, mock_gradebook_response):
        """Test retrieval of gradebooks"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_gradebooks.return_value = [mock_gradebook_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_gradebooks
        
        # Call the function
        result = await get_gradebooks(
            course_id=1,
            semester="Fall",
            year=2024,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_gradebooks.assert_called_once()
        assert result == [mock_gradebook_response]
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_update_gradebook(self, mock_service_class, mock_db, mock_professor, mock_gradebook_response):
        """Test gradebook update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_gradebook.return_value = mock_gradebook_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import update_gradebook
        
        # Create update data
        update_data = GradebookUpdate(
            name="Updated Gradebook Name",
            allow_student_view=False,
            curve_enabled=True,
            curve_percentage=5.0
        )
        
        # Call the function
        result = await update_gradebook(
            gradebook_id=1,
            gradebook_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_gradebook.assert_called_once_with(1, update_data)
        assert result == mock_gradebook_response

    # Statistics and Analytics Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_get_grade_statistics(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of grade statistics"""
        # Mock service instance
        mock_service = Mock()
        mock_statistics = GradeStatisticsResponse(
            course_id=1,
            total_students=25,
            students_passing=20,
            students_failing=5,
            average_grade=78.5,
            median_grade=80.0,
            highest_grade=95.0,
            lowest_grade=45.0,
            standard_deviation=12.5,
            a_grades=3,
            b_grades=8,
            c_grades=9,
            d_grades=3,
            f_grades=2,
            assignment_average=82.0,
            exam_average=75.0,
            participation_average=85.0,
            generated_at=datetime.now()
        )
        mock_service.get_grade_statistics.return_value = mock_statistics
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import get_grade_statistics
        
        # Call the function
        result = await get_grade_statistics(
            course_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_grade_statistics.assert_called_once_with(1)
        assert result == mock_statistics

    # Bulk Operations Tests
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_bulk_create_assignments(self, mock_service_class, mock_db, mock_professor, mock_assignment_response):
        """Test bulk assignment creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.bulk_create_assignments.return_value = [mock_assignment_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import bulk_create_assignments
        
        # Create bulk data
        bulk_data = BulkAssignmentCreate(
            course_id=1,
            assignments=[
                AssignmentCreate(
                    course_id=1,
                    title="Assignment 1",
                    assignment_type=AssignmentType.HOMEWORK,
                    total_points=100.0,
                    weight_percentage=10.0,
                    due_date=datetime(2024, 12, 31, 23, 59, 59)
                )
            ]
        )
        
        # Call the function
        result = await bulk_create_assignments(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.bulk_create_assignments.assert_called_once_with(bulk_data, 1)
        assert result == [mock_assignment_response]
    
    @patch('controllers.grading_assessment_controller.GradingAssessmentService')
    @pytest.mark.asyncio
    async def test_bulk_create_grades(self, mock_service_class, mock_db, mock_professor, mock_grade_response):
        """Test bulk grade creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.bulk_create_grades.return_value = [mock_grade_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.grading_assessment_controller import bulk_create_grades
        
        # Create bulk data
        bulk_data = BulkGradeCreate(
            course_id=1,
            grades=[
                GradeCreate(
                    student_id=1,
                    course_id=1,
                    points_earned=85.0,
                    points_possible=100.0,
                    percentage=85.0,
                    letter_grade="B",
                    grade_status=GradeStatus.PUBLISHED
                )
            ]
        )
        
        # Call the function
        result = await bulk_create_grades(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.bulk_create_grades.assert_called_once_with(bulk_data, 1)
        assert result == [mock_grade_response]

if __name__ == "__main__":
    pytest.main([__file__])
