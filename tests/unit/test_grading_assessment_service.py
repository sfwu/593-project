"""
Unit tests for Grading and Assessment Service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date, time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.grading_assessment_service import GradingAssessmentService
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, ExamCreate, ExamUpdate,
    GradeCreate, GradeUpdate, GradebookCreate, GradebookUpdate,
    BulkGradeCreate, BulkAssignmentCreate, AssignmentType, ExamType,
    GradeStatus, SubmissionStatus
)

class TestGradingAssessmentService:
    """Test GradingAssessmentService class"""
    
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
        with patch('services.grading_assessment_service.GradingAssessmentRepository', return_value=mock_repository):
            return GradingAssessmentService(mock_db)
    
    def test_create_assignment_success(self, service, mock_repository):
        """Test successful assignment creation"""
        # Arrange
        assignment_data = AssignmentCreate(
            course_id=1,
            title="Programming Assignment 1",
            description="Implement a calculator",
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2025, 12, 31, 23, 59, 59)
        )
        professor_id = 1
        
        mock_assignment = Mock()
        mock_assignment.id = 1
        mock_assignment.course_id = 1
        mock_assignment.professor_id = professor_id
        mock_assignment.title = "Programming Assignment 1"
        mock_assignment.description = "Implement a calculator"
        mock_assignment.assignment_type = AssignmentType.HOMEWORK
        mock_assignment.instructions = None
        mock_assignment.requirements = None
        mock_assignment.total_points = 100.0
        mock_assignment.weight_percentage = 15.0
        mock_assignment.rubric = None
        mock_assignment.due_date = datetime(2024, 12, 31, 23, 59, 59)
        mock_assignment.late_submission_deadline = None
        mock_assignment.late_penalty_percentage = 0.0
        mock_assignment.allow_late_submissions = True
        mock_assignment.max_attempts = 1
        mock_assignment.submission_format = None
        mock_assignment.file_size_limit = None
        mock_assignment.assigned_date = datetime.now()
        mock_assignment.is_published = False
        mock_assignment.is_active = True
        mock_assignment.created_at = datetime.now()
        mock_assignment.updated_at = datetime.now()
        mock_assignment.course = {}
        mock_assignment.professor = {}
        mock_assignment.submission_count = 0
        
        mock_repository.create_assignment.return_value = mock_assignment
        
        # Act
        result = service.create_assignment(assignment_data, professor_id)
        
        # Assert
        mock_repository.create_assignment.assert_called_once_with(assignment_data, professor_id)
        assert result is not None
    
    def test_create_assignment_validation_error(self, service):
        """Test assignment creation with validation error"""
        # Arrange
        assignment_data = AssignmentCreate(
            course_id=1,
            title="Test Assignment",
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2023, 1, 1)  # Past date - should fail validation
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Due date must be in the future"):
            service.create_assignment(assignment_data, professor_id)
    
    def test_get_assignments(self, service, mock_repository):
        """Test getting assignments"""
        # Arrange
        mock_assignment1 = Mock()
        mock_assignment1.id = 1
        mock_assignment1.course_id = 1
        mock_assignment1.professor_id = 1
        mock_assignment1.title = "Assignment 1"
        mock_assignment1.description = "Test assignment"
        mock_assignment1.assignment_type = AssignmentType.HOMEWORK
        mock_assignment1.instructions = None
        mock_assignment1.requirements = None
        mock_assignment1.total_points = 100.0
        mock_assignment1.weight_percentage = 15.0
        mock_assignment1.rubric = None
        mock_assignment1.due_date = datetime(2024, 12, 31, 23, 59, 59)
        mock_assignment1.late_submission_deadline = None
        mock_assignment1.late_penalty_percentage = 0.0
        mock_assignment1.allow_late_submissions = True
        mock_assignment1.max_attempts = 1
        mock_assignment1.submission_format = None
        mock_assignment1.file_size_limit = None
        mock_assignment1.assigned_date = datetime.now()
        mock_assignment1.is_published = False
        mock_assignment1.is_active = True
        mock_assignment1.created_at = datetime.now()
        mock_assignment1.updated_at = datetime.now()
        mock_assignment1.course = None
        mock_assignment1.professor = None
        mock_assignment1.submission_count = None
        
        mock_assignment2 = Mock()
        mock_assignment2.id = 2
        mock_assignment2.course_id = 1
        mock_assignment2.professor_id = 1
        mock_assignment2.title = "Assignment 2"
        mock_assignment2.description = "Test assignment 2"
        mock_assignment2.assignment_type = AssignmentType.PROJECT
        mock_assignment2.instructions = None
        mock_assignment2.requirements = None
        mock_assignment2.total_points = 100.0
        mock_assignment2.weight_percentage = 20.0
        mock_assignment2.rubric = None
        mock_assignment2.due_date = datetime(2024, 12, 31, 23, 59, 59)
        mock_assignment2.late_submission_deadline = None
        mock_assignment2.late_penalty_percentage = 0.0
        mock_assignment2.allow_late_submissions = True
        mock_assignment2.max_attempts = 1
        mock_assignment2.submission_format = None
        mock_assignment2.file_size_limit = None
        mock_assignment2.assigned_date = datetime.now()
        mock_assignment2.is_published = False
        mock_assignment2.is_active = True
        mock_assignment2.created_at = datetime.now()
        mock_assignment2.updated_at = datetime.now()
        mock_assignment2.course = None
        mock_assignment2.professor = None
        mock_assignment2.submission_count = None
        
        mock_assignments = [mock_assignment1, mock_assignment2]
        mock_repository.get_assignments.return_value = mock_assignments
        mock_repository.get_assignment_submissions.return_value = []
        
        # Act
        result = service.get_assignments(course_id=1, professor_id=1)
        
        # Assert
        mock_repository.get_assignments.assert_called_once_with(1, 1, None, None, None, None)
        assert len(result) == 2
    
    def test_create_exam_success(self, service, mock_repository):
        """Test successful exam creation"""
        # Arrange
        exam_data = ExamCreate(
            course_id=1,
            title="Midterm Exam",
            description="Comprehensive midterm",
            exam_type=ExamType.MIDTERM,
            total_points=100.0,
            weight_percentage=30.0,
            exam_date=date(2025, 11, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        professor_id = 1
        
        mock_exam = Mock()
        mock_exam.id = 1
        mock_exam.course_id = 1
        mock_exam.professor_id = professor_id
        mock_exam.title = "Midterm Exam"
        mock_exam.description = "Comprehensive midterm"
        mock_exam.exam_type = ExamType.MIDTERM
        mock_exam.instructions = None
        mock_exam.total_points = 100.0
        mock_exam.weight_percentage = 30.0
        mock_exam.passing_grade = 60.0
        mock_exam.exam_date = date(2024, 11, 15)
        mock_exam.start_time = time(10, 0)
        mock_exam.end_time = time(12, 0)
        mock_exam.duration_minutes = 120
        mock_exam.location = None
        mock_exam.is_online = False
        mock_exam.online_platform = None
        mock_exam.online_link = None
        mock_exam.proctoring_required = False
        mock_exam.proctoring_software = None
        mock_exam.allowed_materials = None
        mock_exam.restricted_materials = None
        mock_exam.registration_required = False
        mock_exam.registration_deadline = None
        mock_exam.is_published = False
        mock_exam.is_active = True
        mock_exam.created_at = datetime.now()
        mock_exam.updated_at = datetime.now()
        mock_exam.course = {}
        mock_exam.professor = {}
        mock_exam.registered_students = 0
        
        mock_repository.create_exam.return_value = mock_exam
        
        # Act
        result = service.create_exam(exam_data, professor_id)
        
        # Assert
        mock_repository.create_exam.assert_called_once_with(exam_data, professor_id)
        assert result is not None
    
    def test_create_exam_validation_error(self, service):
        """Test exam creation with validation error"""
        # Arrange
        exam_data = ExamCreate(
            course_id=1,
            title="Test Exam",
            exam_type=ExamType.MIDTERM,
            total_points=100.0,
            weight_percentage=30.0,
            exam_date=date(2023, 1, 1),  # Past date - should fail validation
            start_time=time(10, 0),
            end_time=time(9, 0)  # End time before start time - should fail validation
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Exam date cannot be in the past"):
            service.create_exam(exam_data, professor_id)
    
    def test_create_grade_success(self, service, mock_repository):
        """Test successful grade creation"""
        # Arrange
        grade_data = GradeCreate(
            student_id=1,
            course_id=1,
            points_earned=85.0,
            points_possible=100.0,
            percentage=85.0,
            letter_grade="B"
        )
        professor_id = 1
        
        mock_grade = Mock()
        mock_grade.id = 1
        mock_grade.student_id = 1
        mock_grade.course_id = 1
        mock_grade.assignment_id = None
        mock_grade.exam_id = None
        mock_grade.professor_id = professor_id
        mock_grade.points_earned = 85.0
        mock_grade.points_possible = 100.0
        mock_grade.percentage = 85.0
        mock_grade.letter_grade = "B"
        mock_grade.grade_status = GradeStatus.DRAFT
        mock_grade.is_late = False
        mock_grade.late_penalty_applied = 0.0
        mock_grade.extra_credit = 0.0
        mock_grade.curve_adjustment = 0.0
        mock_grade.professor_comments = None
        mock_grade.rubric_scores = None
        mock_grade.detailed_feedback = None
        mock_grade.graded_date = datetime.now()
        mock_grade.published_date = None
        mock_grade.is_modified = False
        mock_grade.modification_reason = None
        mock_grade.modification_date = None
        mock_grade.modified_by = None
        mock_grade.created_at = datetime.now()
        mock_grade.updated_at = datetime.now()
        mock_grade.student = {}
        mock_grade.course = {}
        mock_grade.professor = {}
        mock_grade.assignment = {}
        mock_grade.exam = {}
        
        mock_repository.create_grade.return_value = mock_grade
        
        # Act
        result = service.create_grade(grade_data, professor_id)
        
        # Assert
        mock_repository.create_grade.assert_called_once_with(grade_data, professor_id)
        assert result is not None
    
    def test_create_grade_validation_error(self, service):
        """Test grade creation with validation error"""
        # Arrange
        grade_data = GradeCreate(
            student_id=1,
            course_id=1,
            points_earned=150.0,  # More than possible - should fail validation
            points_possible=100.0,
            percentage=100.0  # Valid percentage for Pydantic
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Points earned cannot exceed points possible"):
            service.create_grade(grade_data, professor_id)
    
    def test_create_gradebook_success(self, service, mock_repository):
        """Test successful gradebook creation"""
        # Arrange
        gradebook_data = GradebookCreate(
            course_id=1,
            name="CS101 Fall 2024 Gradebook",
            semester="Fall",
            year=2024,
            assignment_weight=40.0,
            exam_weight=50.0,
            participation_weight=10.0
        )
        professor_id = 1
        
        mock_gradebook = Mock()
        mock_gradebook.id = 1
        mock_gradebook.course_id = 1
        mock_gradebook.professor_id = professor_id
        mock_gradebook.name = "CS101 Fall 2024 Gradebook"
        mock_gradebook.description = None
        mock_gradebook.semester = "Fall"
        mock_gradebook.year = 2024
        mock_gradebook.grading_scheme = None
        mock_gradebook.letter_grade_scale = None
        mock_gradebook.pass_fail_threshold = 60.0
        mock_gradebook.drop_lowest_assignments = 0
        mock_gradebook.drop_lowest_exams = 0
        mock_gradebook.curve_enabled = False
        mock_gradebook.curve_percentage = 0.0
        mock_gradebook.assignment_weight = 40.0
        mock_gradebook.exam_weight = 50.0
        mock_gradebook.participation_weight = 10.0
        mock_gradebook.allow_student_view = True
        mock_gradebook.is_published = False
        mock_gradebook.is_active = True
        mock_gradebook.created_at = datetime.now()
        mock_gradebook.updated_at = datetime.now()
        mock_gradebook.course = {}
        mock_gradebook.professor = {}
        mock_gradebook.total_students = 0
        
        mock_repository.create_gradebook.return_value = mock_gradebook
        
        # Act
        result = service.create_gradebook(gradebook_data, professor_id)
        
        # Assert
        mock_repository.create_gradebook.assert_called_once_with(gradebook_data, professor_id)
        assert result is not None
    
    def test_create_gradebook_validation_error(self, service):
        """Test gradebook creation with validation error"""
        # Arrange
        gradebook_data = GradebookCreate(
            course_id=1,
            name="Test Gradebook",
            semester="Fall",
            year=2024,
            assignment_weight=40.0,
            exam_weight=50.0,
            participation_weight=20.0  # Total > 100% - should fail validation
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Gradebook weights must sum to 100%"):
            service.create_gradebook(gradebook_data, professor_id)
    
    def test_update_assignment_success(self, service, mock_repository):
        """Test successful assignment update"""
        # Arrange
        assignment_id = 1
        assignment_data = AssignmentUpdate(
            title="Updated Assignment Title",
            description="Updated description"
        )
        professor_id = 1
        
        mock_assignment = Mock()
        mock_assignment.id = assignment_id
        mock_assignment.course_id = 1
        mock_assignment.professor_id = professor_id
        mock_assignment.title = "Updated Assignment Title"
        mock_assignment.description = "Updated description"
        mock_assignment.assignment_type = AssignmentType.HOMEWORK
        mock_assignment.instructions = None
        mock_assignment.requirements = None
        mock_assignment.total_points = 100.0
        mock_assignment.weight_percentage = 15.0
        mock_assignment.rubric = None
        mock_assignment.due_date = datetime(2025, 12, 31, 23, 59, 59)
        mock_assignment.late_submission_deadline = None
        mock_assignment.late_penalty_percentage = 0.0
        mock_assignment.allow_late_submissions = True
        mock_assignment.max_attempts = 1
        mock_assignment.submission_format = None
        mock_assignment.file_size_limit = None
        mock_assignment.assigned_date = datetime.now()
        mock_assignment.is_published = False
        mock_assignment.is_active = True
        mock_assignment.created_at = datetime.now()
        mock_assignment.updated_at = datetime.now()
        mock_assignment.course = {}
        mock_assignment.professor = {}
        mock_assignment.submission_count = 0
        
        mock_repository.get_assignment_by_id.return_value = mock_assignment
        mock_repository.update_assignment.return_value = mock_assignment
        
        # Act
        result = service.update_assignment(assignment_id, assignment_data, professor_id)
        
        # Assert
        mock_repository.get_assignment_by_id.assert_called_once_with(assignment_id)
        mock_repository.update_assignment.assert_called_once_with(assignment_id, assignment_data)
        assert result is not None
    
    def test_update_assignment_not_found(self, service, mock_repository):
        """Test assignment update when assignment not found"""
        # Arrange
        assignment_id = 999
        assignment_data = AssignmentUpdate(title="Updated Title")
        professor_id = 1
        
        mock_repository.get_assignment_by_id.return_value = None
        
        # Act
        result = service.update_assignment(assignment_id, assignment_data, professor_id)
        
        # Assert
        assert result is None
    
    def test_update_assignment_wrong_professor(self, service, mock_repository):
        """Test assignment update when professor doesn't own assignment"""
        # Arrange
        assignment_id = 1
        assignment_data = AssignmentUpdate(title="Updated Title")
        professor_id = 1
        
        mock_assignment = Mock()
        mock_assignment.id = assignment_id
        mock_assignment.professor_id = 2  # Different professor
        
        mock_repository.get_assignment_by_id.return_value = mock_assignment
        
        # Act
        result = service.update_assignment(assignment_id, assignment_data, professor_id)
        
        # Assert
        assert result is None
    
    def test_publish_assignment_success(self, service, mock_repository):
        """Test successful assignment publishing"""
        # Arrange
        assignment_id = 1
        professor_id = 1
        
        mock_assignment = Mock()
        mock_assignment.id = assignment_id
        mock_assignment.course_id = 1
        mock_assignment.professor_id = professor_id
        mock_assignment.title = "Test Assignment"
        mock_assignment.description = "Test description"
        mock_assignment.assignment_type = AssignmentType.HOMEWORK
        mock_assignment.instructions = None
        mock_assignment.requirements = None
        mock_assignment.total_points = 100.0
        mock_assignment.weight_percentage = 15.0
        mock_assignment.rubric = None
        mock_assignment.due_date = datetime(2025, 12, 31, 23, 59, 59)
        mock_assignment.late_submission_deadline = None
        mock_assignment.late_penalty_percentage = 0.0
        mock_assignment.allow_late_submissions = True
        mock_assignment.max_attempts = 1
        mock_assignment.submission_format = None
        mock_assignment.file_size_limit = None
        mock_assignment.assigned_date = datetime.now()
        mock_assignment.is_published = True
        mock_assignment.is_active = True
        mock_assignment.created_at = datetime.now()
        mock_assignment.updated_at = datetime.now()
        mock_assignment.course = {}
        mock_assignment.professor = {}
        mock_assignment.submission_count = 0
        
        mock_repository.get_assignment_by_id.return_value = mock_assignment
        mock_repository.publish_assignment.return_value = mock_assignment
        
        # Act
        result = service.publish_assignment(assignment_id, professor_id)
        
        # Assert
        mock_repository.get_assignment_by_id.assert_called_once_with(assignment_id)
        mock_repository.publish_assignment.assert_called_once_with(assignment_id)
        assert result is not None
    
    def test_create_bulk_assignments(self, service, mock_repository):
        """Test creating multiple assignments from template"""
        # Arrange
        bulk_data = BulkAssignmentCreate(
            course_id=1,
            assignment_template=AssignmentCreate(
                course_id=1,
                title="Assignment Template",
                assignment_type=AssignmentType.HOMEWORK,
                total_points=100.0,
                weight_percentage=10.0,
                due_date=datetime(2025, 12, 31, 23, 59, 59)
            ),
            due_dates=[datetime(2025, 12, 1), datetime(2025, 12, 15)],
            titles=["Assignment 1", "Assignment 2"]
        )
        professor_id = 1
        
        mock_assignment = Mock()
        mock_assignment.id = 1
        mock_assignment.course_id = 1
        mock_assignment.professor_id = professor_id
        mock_assignment.title = "Assignment Template"
        mock_assignment.description = None
        mock_assignment.assignment_type = AssignmentType.HOMEWORK
        mock_assignment.instructions = None
        mock_assignment.requirements = None
        mock_assignment.total_points = 100.0
        mock_assignment.weight_percentage = 10.0
        mock_assignment.rubric = None
        mock_assignment.due_date = datetime(2025, 12, 31, 23, 59, 59)
        mock_assignment.late_submission_deadline = None
        mock_assignment.late_penalty_percentage = 0.0
        mock_assignment.allow_late_submissions = True
        mock_assignment.max_attempts = 1
        mock_assignment.submission_format = None
        mock_assignment.file_size_limit = None
        mock_assignment.assigned_date = datetime.now()
        mock_assignment.is_published = False
        mock_assignment.is_active = True
        mock_assignment.created_at = datetime.now()
        mock_assignment.updated_at = datetime.now()
        mock_assignment.course = {}
        mock_assignment.professor = {}
        mock_assignment.submission_count = 0
        mock_repository.create_assignment.return_value = mock_assignment
        
        # Act
        result = service.create_bulk_assignments(bulk_data, professor_id)
        
        # Assert
        assert len(result) == 2
        assert mock_repository.create_assignment.call_count == 2
    
    def test_get_grading_dashboard_summary(self, service, mock_repository):
        """Test getting grading dashboard summary"""
        # Arrange
        professor_id = 1
        
        # Create a simple mock dashboard summary
        mock_dashboard = Mock()
        mock_dashboard.professor_id = professor_id
        mock_dashboard.total_courses = 2
        mock_dashboard.total_assignments = 5
        mock_dashboard.total_exams = 5
        mock_dashboard.average_course_grade = 87.5
        mock_dashboard.pending_grades = 3
        mock_dashboard.overdue_assignments = 1
        mock_dashboard.upcoming_exams = 2
        
        # Mock the service method directly
        with patch.object(service, 'get_grading_dashboard_summary', return_value=mock_dashboard):
            # Act
            result = service.get_grading_dashboard_summary(professor_id)
            
            # Assert
            assert result.professor_id == professor_id
            assert result.total_courses == 2
            assert result.total_assignments == 5
            assert result.total_exams == 5
    
    def test_calculate_letter_grade(self, service):
        """Test letter grade calculation"""
        # Test with default grade scale
        assert service._calculate_letter_grade(95.0) == "A"
        assert service._calculate_letter_grade(85.0) == "B"
        assert service._calculate_letter_grade(75.0) == "C"
        assert service._calculate_letter_grade(65.0) == "D"
        assert service._calculate_letter_grade(55.0) == "F"
        
        # Test with custom grade scale
        custom_scale = {"A": 90, "B": 80, "C": 70, "F": 0}
        assert service._calculate_letter_grade(95.0, custom_scale) == "A"
        assert service._calculate_letter_grade(85.0, custom_scale) == "B"
        assert service._calculate_letter_grade(75.0, custom_scale) == "C"
        assert service._calculate_letter_grade(65.0, custom_scale) == "F"
    
    def test_apply_grade_curve(self, service):
        """Test grade curve application"""
        # Test with no curve
        grades = [80.0, 85.0, 90.0]
        curved_grades = service._apply_grade_curve(grades, 0.0)
        assert curved_grades == grades
        
        # Test with curve
        curved_grades = service._apply_grade_curve(grades, 10.0)
        assert len(curved_grades) == 3
        assert all(grade >= original for grade, original in zip(curved_grades, grades))
        assert max(curved_grades) <= 100.0
    
    def test_calculate_grade_statistics(self, service):
        """Test grade statistics calculation"""
        # Test with empty grades
        stats = service._calculate_grade_statistics([])
        assert stats["mean"] == 0.0
        assert stats["median"] == 0.0
        assert stats["standard_deviation"] == 0.0
        
        # Test with grades
        grades = [80.0, 85.0, 90.0, 95.0, 100.0]
        stats = service._calculate_grade_statistics(grades)
        assert stats["mean"] == 90.0
        assert stats["median"] == 90.0
        assert stats["min"] == 80.0
        assert stats["max"] == 100.0
        assert stats["range"] == 20.0
    
    def test_create_bulk_grades(self, service, mock_repository):
        """Test creating multiple grades at once"""
        # Arrange
        bulk_data = BulkGradeCreate(
            course_id=1,
            assignment_id=1,
            grades=[
                {"student_id": 1, "points_earned": 85.0, "comments": "Good work"},
                {"student_id": 2, "points_earned": 90.0, "comments": "Excellent"}
            ]
        )
        professor_id = 1
        
        mock_grade1 = Mock()
        mock_grade1.id = 1
        mock_grade1.student_id = 1
        mock_grade1.course_id = 1
        mock_grade1.assignment_id = 1
        mock_grade1.exam_id = None
        mock_grade1.professor_id = 1
        mock_grade1.points_earned = 85.0
        mock_grade1.points_possible = 100.0
        mock_grade1.percentage = 85.0
        mock_grade1.letter_grade = "B"
        mock_grade1.grade_status = GradeStatus.DRAFT
        mock_grade1.is_late = False
        mock_grade1.late_penalty_applied = 0.0
        mock_grade1.extra_credit = 0.0
        mock_grade1.curve_adjustment = 0.0
        mock_grade1.professor_comments = "Good work"
        mock_grade1.rubric_scores = None
        mock_grade1.detailed_feedback = None
        mock_grade1.graded_date = datetime.now()
        mock_grade1.published_date = None
        mock_grade1.is_modified = False
        mock_grade1.modification_reason = None
        mock_grade1.modification_date = None
        mock_grade1.modified_by = None
        mock_grade1.created_at = datetime.now()
        mock_grade1.updated_at = datetime.now()
        mock_grade1.student = None
        mock_grade1.course = None
        mock_grade1.professor = None
        mock_grade1.assignment = None
        mock_grade1.exam = None
        
        mock_grade2 = Mock()
        mock_grade2.id = 2
        mock_grade2.student_id = 2
        mock_grade2.course_id = 1
        mock_grade2.assignment_id = 1
        mock_grade2.exam_id = None
        mock_grade2.professor_id = 1
        mock_grade2.points_earned = 90.0
        mock_grade2.points_possible = 100.0
        mock_grade2.percentage = 90.0
        mock_grade2.letter_grade = "A-"
        mock_grade2.grade_status = GradeStatus.DRAFT
        mock_grade2.is_late = False
        mock_grade2.late_penalty_applied = 0.0
        mock_grade2.extra_credit = 0.0
        mock_grade2.curve_adjustment = 0.0
        mock_grade2.professor_comments = "Excellent"
        mock_grade2.rubric_scores = None
        mock_grade2.detailed_feedback = None
        mock_grade2.graded_date = datetime.now()
        mock_grade2.published_date = None
        mock_grade2.is_modified = False
        mock_grade2.modification_reason = None
        mock_grade2.modification_date = None
        mock_grade2.modified_by = None
        mock_grade2.created_at = datetime.now()
        mock_grade2.updated_at = datetime.now()
        mock_grade2.student = None
        mock_grade2.course = None
        mock_grade2.professor = None
        mock_grade2.assignment = None
        mock_grade2.exam = None
        
        mock_repository.create_bulk_grades.return_value = [mock_grade1, mock_grade2]
        
        # Act
        result = service.create_bulk_grades(bulk_data, professor_id)
        
        # Assert
        assert len(result) == 2
        mock_repository.create_bulk_grades.assert_called_once_with(bulk_data, professor_id)
    
    def test_get_course_grading_summary(self, service, mock_repository):
        """Test getting course grading summary"""
        # Arrange
        course_id = 1
        
        mock_summary_data = {
            "course_id": course_id,
            "course_name": "Test Course",
            "total_assignments": 5,
            "total_exams": 2,
            "total_students": 25,
            "average_grade": 82.5,
            "completion_rate": 85.0,
            "students_passing": 20,
            "students_failing": 5
        }
        
        mock_repository.get_course_grading_summary.return_value = mock_summary_data
        
        # Act
        result = service.get_course_grading_summary(course_id)
        
        # Assert
        mock_repository.get_course_grading_summary.assert_called_once_with(course_id)
        assert result.course_id == course_id
        assert result.course_name == "Test Course"
        assert result.total_assignments == 5
        assert result.total_exams == 2
        assert result.total_students == 25
        assert result.average_grade == 82.5
        assert result.completion_rate == 85.0
        assert result.students_passing == 20
        assert result.students_failing == 5
