"""
Unit tests for Student Information Service
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.student_information_service import StudentInformationService
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, MessageCreate, MessageUpdate,
    StudentDirectoryUpdate, StudentPerformanceUpdate, BulkAttendanceCreate,
    AttendanceStatus, MessageStatus, MessageType, MessagePriority
)

class TestStudentInformationService:
    """Test StudentInformationService class"""
    
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
        with patch('services.student_information_service.StudentInformationRepository', return_value=mock_repository):
            return StudentInformationService(mock_db)
    
    def test_create_attendance_success(self, service, mock_repository):
        """Test successful attendance creation"""
        # Arrange
        attendance_data = AttendanceCreate(
            student_id=1,
            course_id=1,
            attendance_date=datetime.now(),
            status=AttendanceStatus.PRESENT,
            notes="Good participation",
            late_minutes=0,
            session_topic="Introduction to Programming",
            session_duration=90
        )
        professor_id = 1
        
        mock_attendance = Mock()
        mock_attendance.id = 1
        mock_attendance.student_id = 1
        mock_attendance.course_id = 1
        mock_attendance.status = AttendanceStatus.PRESENT
        mock_attendance.attendance_date = datetime.now()
        
        mock_repository.create_attendance.return_value = mock_attendance
        
        # Act
        result = service.create_attendance(attendance_data, professor_id)
        
        # Assert
        mock_repository.create_attendance.assert_called_once_with(attendance_data, professor_id)
        assert result is not None
    
    def test_create_attendance_validation_error(self, service):
        """Test attendance creation with validation error"""
        # Arrange
        attendance_data = AttendanceCreate(
            student_id=1,
            course_id=1,
            attendance_date=datetime.now(),
            status=AttendanceStatus.PRESENT,
            late_minutes=-5  # Invalid negative value
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Late minutes cannot be negative"):
            service.create_attendance(attendance_data, professor_id)
    
    def test_get_attendance_records(self, service, mock_repository):
        """Test getting attendance records"""
        # Arrange
        mock_records = [Mock(), Mock()]
        mock_repository.get_attendance_records.return_value = mock_records
        
        # Act
        result = service.get_attendance_records(course_id=1, professor_id=1)
        
        # Assert
        mock_repository.get_attendance_records.assert_called_once_with(
            course_id=1, student_id=None, professor_id=1, 
            date_from=None, date_to=None, status=None
        )
        assert len(result) == 2
    
    def test_create_message_success(self, service, mock_repository):
        """Test successful message creation"""
        # Arrange
        message_data = MessageCreate(
            course_id=1,
            subject="Assignment Due Date",
            content="Please remember that the assignment is due next week.",
            message_type=MessageType.ASSIGNMENT,
            priority=MessagePriority.HIGH,
            recipient_ids=[1, 2, 3]
        )
        sender_id = 1
        
        mock_message = Mock()
        mock_message.id = 1
        mock_message.sender_id = sender_id
        mock_message.subject = "Assignment Due Date"
        mock_message.message_type = MessageType.ASSIGNMENT
        
        mock_repository.create_message.return_value = mock_message
        
        # Act
        result = service.create_message(message_data, sender_id)
        
        # Assert
        mock_repository.create_message.assert_called_once_with(message_data, sender_id)
        mock_repository.create_message_recipients.assert_called_once_with(1, [1, 2, 3])
        assert result is not None
    
    def test_create_message_validation_error(self, service):
        """Test message creation with validation error"""
        # Arrange
        message_data = MessageCreate(
            course_id=1,
            subject="Test Message",
            content="This is a test message.",
            is_broadcast=True,
            recipient_ids=[]  # Empty recipients for broadcast message
        )
        sender_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Broadcast messages must have recipient IDs"):
            service.create_message(message_data, sender_id)
    
    def test_send_message_success(self, service, mock_repository):
        """Test successful message sending"""
        # Arrange
        message_id = 1
        sender_id = 1
        
        mock_message = Mock()
        mock_message.id = message_id
        mock_message.sender_id = sender_id
        mock_message.course_id = 1
        
        mock_recipient = Mock()
        mock_recipient.student_id = 1
        
        mock_repository.get_message_by_id.return_value = mock_message
        mock_repository.send_message.return_value = mock_message
        mock_repository.get_message_recipients.return_value = [mock_recipient]
        
        # Act
        result = service.send_message(message_id, sender_id)
        
        # Assert
        mock_repository.get_message_by_id.assert_called_once_with(message_id)
        mock_repository.send_message.assert_called_once_with(message_id)
        mock_repository.get_message_recipients.assert_called_once_with(message_id)
        assert result is not None
    
    def test_send_message_not_found(self, service, mock_repository):
        """Test sending non-existent message"""
        # Arrange
        message_id = 999
        sender_id = 1
        
        mock_repository.get_message_by_id.return_value = None
        
        # Act
        result = service.send_message(message_id, sender_id)
        
        # Assert
        assert result is None
    
    def test_get_student_directory(self, service, mock_repository):
        """Test getting student directory"""
        # Arrange
        mock_entries = [Mock(), Mock()]
        mock_repository.get_student_directory.return_value = mock_entries
        
        # Act
        result = service.get_student_directory(name="John", major="Computer Science")
        
        # Assert
        mock_repository.get_student_directory.assert_called_once_with(
            name="John", major="Computer Science", year_level=None,
            enrollment_status=None, gpa_min=None, gpa_max=None, is_at_risk=None
        )
        assert len(result) == 2
    
    def test_update_student_performance(self, service, mock_repository):
        """Test updating student performance"""
        # Arrange
        performance_id = 1
        performance_data = StudentPerformanceUpdate(
            current_grade=85.5,
            participation_score=90.0,
            is_at_risk=False,
            professor_notes="Good improvement"
        )
        professor_id = 1
        
        mock_performance = Mock()
        mock_performance.id = performance_id
        mock_performance.student_id = 1
        mock_performance.course_id = 1
        mock_performance.current_grade = 85.5
        
        mock_repository.update_student_performance.return_value = mock_performance
        
        # Act
        result = service.update_student_performance(performance_id, performance_data, professor_id)
        
        # Assert
        mock_repository.update_student_performance.assert_called_once_with(performance_id, performance_data)
        assert result is not None
    
    def test_assess_student_risk_low_attendance(self, service, mock_repository):
        """Test student risk assessment with low attendance"""
        # Arrange
        student_id = 1
        course_id = 1
        
        # Mock performance record
        mock_performance = Mock()
        mock_performance.current_grade = 80.0
        mock_performance.participation_score = 85.0
        mock_performance.assignment_average = 75.0
        mock_performance.exam_average = 85.0
        mock_performance.is_at_risk = False
        mock_performance.id = 1
        
        # Mock attendance summary with low attendance
        mock_attendance = Mock()
        mock_attendance.attendance_percentage = 65.0
        
        mock_repository.get_student_performance.return_value = mock_performance
        mock_repository.get_attendance_summary.return_value = mock_attendance
        
        # Act
        result = service.assess_student_risk(student_id, course_id)
        
        # Assert
        assert result["is_at_risk"] == True
        assert "Low attendance" in result["risk_factors"]
        assert "Schedule meeting to discuss attendance issues" in result["recommendations"]
    
    def test_assess_student_risk_low_grades(self, service, mock_repository):
        """Test student risk assessment with low grades"""
        # Arrange
        student_id = 1
        course_id = 1
        
        # Mock performance record with low grades
        mock_performance = Mock()
        mock_performance.current_grade = 55.0
        mock_performance.participation_score = 85.0
        mock_performance.assignment_average = 50.0
        mock_performance.exam_average = 60.0
        mock_performance.is_at_risk = False
        mock_performance.id = 1
        
        # Mock attendance summary with good attendance
        mock_attendance = Mock()
        mock_attendance.attendance_percentage = 90.0
        
        mock_repository.get_student_performance.return_value = mock_performance
        mock_repository.get_attendance_summary.return_value = mock_attendance
        
        # Act
        result = service.assess_student_risk(student_id, course_id)
        
        # Assert
        assert result["is_at_risk"] == True
        assert "Low academic performance" in result["risk_factors"]
        assert "Poor assignment performance" in result["risk_factors"]
        assert "Provide additional academic support" in result["recommendations"]
    
    def test_assess_student_risk_no_risk(self, service, mock_repository):
        """Test student risk assessment with no risk factors"""
        # Arrange
        student_id = 1
        course_id = 1
        
        # Mock performance record with good performance
        mock_performance = Mock()
        mock_performance.current_grade = 85.0
        mock_performance.participation_score = 90.0
        mock_performance.assignment_average = 80.0
        mock_performance.exam_average = 90.0
        mock_performance.is_at_risk = False
        mock_performance.id = 1
        
        # Mock attendance summary with good attendance
        mock_attendance = Mock()
        mock_attendance.attendance_percentage = 95.0
        
        mock_repository.get_student_performance.return_value = mock_performance
        mock_repository.get_attendance_summary.return_value = mock_attendance
        
        # Act
        result = service.assess_student_risk(student_id, course_id)
        
        # Assert
        assert result["is_at_risk"] == False
        assert len(result["risk_factors"]) == 0
        assert len(result["recommendations"]) == 0
    
    def test_get_professor_dashboard_summary(self, service, mock_repository):
        """Test getting professor dashboard summary"""
        # Arrange
        professor_id = 1
        
        mock_summary_data = {
            "total_students": 50,
            "total_courses": 3,
            "pending_messages": 5,
            "students_at_risk": 2,
            "attendance_alerts": 3,
            "recent_communications": 10
        }
        
        mock_repository.get_professor_dashboard_summary.return_value = mock_summary_data
        
        # Act
        result = service.get_professor_dashboard_summary(professor_id)
        
        # Assert
        mock_repository.get_professor_dashboard_summary.assert_called_once_with(professor_id)
        assert result.professor_id == professor_id
        assert result.total_students == 50
        assert result.total_courses == 3
        assert result.pending_messages == 5
        assert result.students_at_risk == 2
    
    def test_get_student_dashboard_summary(self, service, mock_repository):
        """Test getting student dashboard summary"""
        # Arrange
        student_id = 1
        
        mock_summary_data = {
            "student_id": 1,
            "student_name": "John Doe",
            "student_email": "john.doe@example.com",
            "courses_enrolled": 4,
            "total_attendance_percentage": 85.5,
            "average_grade": 82.0,
            "unread_messages": 3,
            "upcoming_assignments": 2,
            "is_at_risk": False,
            "last_contact_date": datetime.now()
        }
        
        mock_repository.get_student_dashboard_summary.return_value = mock_summary_data
        
        # Act
        result = service.get_student_dashboard_summary(student_id)
        
        # Assert
        mock_repository.get_student_dashboard_summary.assert_called_once_with(student_id)
        assert result.student_id == 1
        assert result.student_name == "John Doe"
        assert result.courses_enrolled == 4
        assert result.total_attendance_percentage == 85.5
        assert result.average_grade == 82.0
        assert result.is_at_risk == False
    
    def test_create_bulk_attendance_validation_error(self, service):
        """Test bulk attendance creation with validation error"""
        # Arrange
        bulk_data = BulkAttendanceCreate(
            course_id=1,
            attendance_date=datetime.now(),
            attendance_records=[
                {"student_id": 1, "status": AttendanceStatus.PRESENT, "late_minutes": -5}  # Invalid
            ]
        )
        professor_id = 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Late minutes cannot be negative"):
            service.create_bulk_attendance(bulk_data, professor_id)
    
    def test_get_course_attendance_report(self, service, mock_repository):
        """Test getting course attendance report"""
        # Arrange
        course_id = 1
        
        # Mock course
        mock_course = Mock()
        mock_course.id = course_id
        mock_course.title = "Introduction to Programming"
        mock_course.semester = "Fall"
        mock_course.year = 2024
        
        # Mock attendance summaries
        mock_summary1 = Mock()
        mock_summary1.student_id = 1
        mock_summary1.attendance_percentage = 95.0
        mock_summary1.absent_count = 1
        mock_summary1.student = Mock()
        mock_summary1.student.first_name = "John"
        mock_summary1.student.last_name = "Doe"
        
        mock_summary2 = Mock()
        mock_summary2.student_id = 2
        mock_summary2.attendance_percentage = 65.0
        mock_summary2.absent_count = 5
        mock_summary2.student = Mock()
        mock_summary2.student.first_name = "Jane"
        mock_summary2.student.last_name = "Smith"
        
        service.db.query.return_value.filter.return_value.first.return_value = mock_course
        mock_repository.get_course_attendance_summaries.return_value = [mock_summary1, mock_summary2]
        
        # Act
        result = service.get_course_attendance_report(course_id)
        
        # Assert
        assert result.course_id == course_id
        assert result.course_name == "Introduction to Programming"
        assert result.overall_attendance_percentage == 80.0  # Average of 95 and 65
        assert len(result.students_at_risk) == 1  # Only Jane with 65% attendance
        assert result.students_at_risk[0]["student_name"] == "Jane Smith"
