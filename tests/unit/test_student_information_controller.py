"""
Unit Tests for Student Information Controller
Tests API endpoints for student information management
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from controllers.student_information_controller import router
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceSummaryResponse,
    MessageCreate, MessageUpdate, MessageResponse, MessageRecipientResponse,
    StudentDirectoryResponse, StudentDirectoryUpdate,
    StudentPerformanceResponse, StudentPerformanceUpdate,
    CommunicationLogResponse, BulkAttendanceCreate, BulkMessageCreate,
    StudentSearchFilters, AttendanceFilters, MessageFilters,
    StudentDashboardSummary, ProfessorDashboardSummary, AttendanceReport, MessageReport,
    AttendanceStatus, MessageStatus, MessageType, MessagePriority
)
from models.professor import Professor
from models.user import User, UserRole

class TestStudentInformationController:
    """Unit tests for Student Information Controller"""
    
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
    def mock_attendance_response(self):
        """Mock attendance response"""
        return AttendanceResponse(
            id=1,
            student_id=1,
            course_id=1,
            attendance_date=datetime.now(),
            status=AttendanceStatus.PRESENT,
            notes="Good participation",
            late_minutes=0,
            session_topic="Introduction to Programming",
            session_duration=90,
            recorded_at=datetime.now(),
            recorded_by=1,
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_message_response(self):
        """Mock message response"""
        return MessageResponse(
            id=1,
            sender_id=1,
            course_id=1,
            subject="Assignment Due Date",
            content="Please remember that the assignment is due next week.",
            message_type=MessageType.ASSIGNMENT,
            priority=MessagePriority.HIGH,
            is_broadcast=True,
            status=MessageStatus.DRAFT,
            created_at=datetime.now(),
            sent_at=None,
            scheduled_at=None
        )
    
    @pytest.fixture
    def mock_student_directory_response(self):
        """Mock student directory response"""
        return StudentDirectoryResponse(
            id=1,
            student_id=1,
            email="john.doe@example.com",
            phone="123-456-7890",
            emergency_contact="Jane Doe",
            emergency_phone="098-765-4321",
            address="123 Main St, City, State",
            major="Computer Science",
            year_level="Junior",
            gpa=3.5,
            enrollment_status="active",
            advisor_id=1,
            notes="Excellent student",
            show_contact_info=True,
            show_academic_info=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_student_performance_response(self):
        """Mock student performance response"""
        return StudentPerformanceResponse(
            id=1,
            student_id=1,
            course_id=1,
            current_grade=85.5,
            participation_score=90.0,
            attendance_score=95.0,
            assignment_average=80.0,
            exam_average=90.0,
            is_at_risk=False,
            risk_factors="[]",
            improvement_areas="[]",
            professor_notes="Good performance overall",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    # Student Directory Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_directory(self, mock_service_class, mock_db, mock_professor, mock_student_directory_response):
        """Test retrieval of student directory"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_directory.return_value = [mock_student_directory_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_student_directory
        
        # Call the function
        result = await get_student_directory(
            name="John",
            major="Computer Science",
            year_level="Junior",
            enrollment_status="active",
            gpa_min=3.0,
            gpa_max=4.0,
            is_at_risk=False,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_directory.assert_called_once_with(
            "John", "Computer Science", "Junior", "active", 3.0, 4.0, False
        )
        assert result == [mock_student_directory_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_directory_entry(self, mock_service_class, mock_db, mock_professor, mock_student_directory_response):
        """Test retrieval of specific student directory entry"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_directory_entry.return_value = mock_student_directory_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_student_directory_entry
        
        # Call the function
        result = await get_student_directory_entry(
            student_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_directory_entry.assert_called_once_with(1)
        assert result == mock_student_directory_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_update_student_directory(self, mock_service_class, mock_db, mock_professor, mock_student_directory_response):
        """Test student directory update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_student_directory_entry.return_value = mock_student_directory_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import update_student_directory_entry
        
        # Create update data
        update_data = StudentDirectoryUpdate(
            phone="987-654-3210",
            gpa=3.7,
            notes="Updated notes"
        )
        
        # Call the function
        result = await update_student_directory_entry(
            student_id=1,
            directory_data=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_student_directory_entry.assert_called_once_with(1, update_data)
        assert result == mock_student_directory_response

    # Academic Records Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_academic_records(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of student academic records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_performance.return_value = mock_student_performance_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_student_academic_records
        
        # Call the function
        result = await get_student_academic_records(
            student_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_performance.assert_called_once()
        # Check that the first argument is 1 (student_id)
        assert mock_service.get_student_performance.call_args[0][0] == 1
        assert result == [mock_student_performance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_course_academic_records(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of course academic records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_course_student_performance.return_value = [mock_student_performance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_course_student_performance
        
        # Call the function
        result = await get_course_student_performance(
            course_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_course_student_performance.assert_called_once_with(1)
        assert result == [mock_student_performance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_update_student_performance(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test student performance update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_student_performance.return_value = mock_student_performance_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import update_student_performance
        
        # Create update data
        update_data = StudentPerformanceUpdate(
            current_grade=88.0,
            is_at_risk=True,
            professor_notes="Needs improvement"
        )
        
        # Call the function
        result = await update_student_performance(
            performance_id=1,
            performance_data=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_student_performance.assert_called_once_with(1, update_data, 1)
        assert result == mock_student_performance_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_at_risk_students(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of at-risk students"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_students_at_risk.return_value = [mock_student_performance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_students_at_risk
        
        # Call the function
        result = await get_students_at_risk(
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_students_at_risk.assert_called_once()
        assert result == [mock_student_performance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_risk_assessment(self, mock_service_class, mock_db, mock_professor):
        """Test student risk assessment"""
        # Mock service instance
        mock_service = Mock()
        mock_risk_assessment = {
            "student_id": 1,
            "risk_level": "Medium",
            "risk_factors": ["Low attendance", "Declining grades"],
            "recommendations": ["Schedule meeting", "Provide additional support"],
            "last_assessed": datetime.now()
        }
        mock_service.assess_student_risk.return_value = mock_risk_assessment
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import assess_student_risk
        
        # Call the function
        result = await assess_student_risk(
            student_id=1,
            course_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.assess_student_risk.assert_called_once_with(1, 1)
        assert result == mock_risk_assessment

    # Attendance Management Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_create_attendance(self, mock_service_class, mock_db, mock_professor, mock_attendance_response):
        """Test attendance creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_attendance.return_value = mock_attendance_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import create_attendance
        
        # Create attendance data
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
        
        # Call the function
        result = await create_attendance(
            attendance_data=attendance_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_attendance.assert_called_once_with(attendance_data, 1)
        assert result == mock_attendance_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_bulk_create_attendance(self, mock_service_class, mock_db, mock_professor, mock_attendance_response):
        """Test bulk attendance creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_bulk_attendance.return_value = [mock_attendance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import create_bulk_attendance
        
        # Create bulk data
        bulk_data = BulkAttendanceCreate(
            course_id=1,
            attendance_date=datetime.now(),
            attendance_records=[
                {
                    "student_id": 1,
                    "course_id": 1,
                    "attendance_date": datetime.now(),
                    "status": AttendanceStatus.PRESENT
                }
            ]
        )
        
        # Call the function
        result = await create_bulk_attendance(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_bulk_attendance.assert_called_once_with(bulk_data, 1)
        assert result == [mock_attendance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_attendance(self, mock_service_class, mock_db, mock_professor, mock_attendance_response):
        """Test retrieval of attendance records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_attendance_records.return_value = [mock_attendance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_attendance_records
        
        # Call the function
        result = await get_attendance_records(
            course_id=1,
            student_id=1,
            date_from=datetime.now() - timedelta(days=30),
            date_to=datetime.now(),
            status=AttendanceStatus.PRESENT,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_attendance_records.assert_called_once()
        # Check the call was made with the correct parameters
        call_args = mock_service.get_attendance_records.call_args
        assert call_args.kwargs['course_id'] == 1
        assert call_args.kwargs['student_id'] == 1
        assert call_args.kwargs['status'] == AttendanceStatus.PRESENT
        assert result == [mock_attendance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_update_attendance(self, mock_service_class, mock_db, mock_professor, mock_attendance_response):
        """Test attendance update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_attendance.return_value = mock_attendance_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import update_attendance_record
        
        # Create update data
        update_data = AttendanceUpdate(
            status=AttendanceStatus.LATE,
            late_minutes=15,
            notes="Student arrived late"
        )
        
        # Call the function
        result = await update_attendance_record(
            attendance_id=1,
            attendance_data=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_attendance.assert_called_once_with(1, update_data, 1)
        assert result == mock_attendance_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_attendance_summary(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of attendance summary"""
        # Mock service instance
        mock_service = Mock()
        mock_summary = AttendanceSummaryResponse(
            id=1,
            student_id=1,
            course_id=1,
            semester="Fall",
            year=2024,
            total_sessions=20,
            present_count=18,
            absent_count=1,
            late_count=1,
            excused_count=0,
            tardy_count=0,
            attendance_percentage=90.0,
            total_late_minutes=15,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.get_attendance_summary.return_value = mock_summary
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_attendance_summary
        
        # Call the function
        result = await get_attendance_summary(
            student_id=1,
            course_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_attendance_summary.assert_called_once_with(1, 1)
        assert result == mock_summary

    # Message Management Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_create_message(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test message creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_message.return_value = mock_message_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import create_message
        
        # Create message data
        message_data = MessageCreate(
            course_id=1,
            subject="Assignment Due Date",
            content="Please remember that the assignment is due next week.",
            message_type=MessageType.ASSIGNMENT,
            priority=MessagePriority.HIGH,
            is_broadcast=True,
            recipient_ids=[1, 2, 3]
        )
        
        # Call the function
        result = await create_message(
            message_data=message_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.create_message.assert_called_once_with(message_data, 1)
        assert result == mock_message_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_messages(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test retrieval of messages"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_messages.return_value = [mock_message_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_messages
        
        # Call the function
        result = await get_messages(
            course_id=1,
            message_type=MessageType.ASSIGNMENT,
            status=MessageStatus.DRAFT,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_messages.assert_called_once()
        assert result == [mock_message_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_update_message(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test message update"""
        # Mock service instance
        mock_service = Mock()
        mock_service.update_message.return_value = mock_message_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import update_message
        
        # Create update data
        update_data = MessageUpdate(
            subject="Updated Subject",
            content="Updated content"
        )
        
        # Call the function
        result = await update_message(
            message_id=1,
            message_data=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_message.assert_called_once_with(1, update_data, 1)
        assert result == mock_message_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_send_message(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test message sending"""
        # Mock service instance
        mock_service = Mock()
        mock_service.send_message.return_value = mock_message_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import send_message
        
        # Call the function
        result = await send_message(
            message_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.send_message.assert_called_once_with(1, 1)
        assert result == mock_message_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_bulk_create_messages(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test bulk message creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.create_message.return_value = mock_message_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import create_bulk_messages
        
        # Create bulk data
        bulk_data = BulkMessageCreate(
            course_id=1,
            subject="Test Message",
            content="This is a test message.",
            message_type=MessageType.GENERAL,
            priority=MessagePriority.NORMAL,
            recipient_ids=[1, 2, 3]
        )
        
        # Call the function
        result = await create_bulk_messages(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        # The function should call create_message for each recipient
        assert mock_service.create_message.call_count == 3  # 3 recipients
        assert len(result) == 3

    # Dashboard and Analytics Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_professor_dashboard(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of professor dashboard"""
        # Mock service instance
        mock_service = Mock()
        mock_dashboard = ProfessorDashboardSummary(
            professor_id=1,
            total_students=50,
            total_courses=3,
            pending_messages=10,
            students_at_risk=5,
            attendance_alerts=3,
            recent_communications=15
        )
        mock_service.get_professor_dashboard_summary.return_value = mock_dashboard
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_professor_dashboard
        
        # Call the function
        result = await get_professor_dashboard(
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_professor_dashboard_summary.assert_called_once_with(1)
        assert result == mock_dashboard
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_dashboard(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of student dashboard"""
        # Mock service instance
        mock_service = Mock()
        mock_dashboard = StudentDashboardSummary(
            student_id=1,
            student_name="John Doe",
            student_email="john.doe@example.com",
            courses_enrolled=5,
            total_attendance_percentage=90.0,
            average_grade=3.5,
            unread_messages=2,
            upcoming_assignments=3,
            is_at_risk=False,
            last_contact_date=datetime.now()
        )
        mock_service.get_student_dashboard_summary.return_value = mock_dashboard
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_student_dashboard
        
        # Call the function
        result = await get_student_dashboard(
            student_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_dashboard_summary.assert_called_once_with(1)
        assert result == mock_dashboard

    # Communication Logs Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_communication_logs(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of communication logs"""
        # Mock service instance
        mock_service = Mock()
        mock_log = CommunicationLogResponse(
            id=1,
            professor_id=1,
            student_id=1,
            course_id=1,
            communication_type="email",
            subject="Grade Discussion",
            content="Let's discuss your recent assignment grade.",
            direction="sent",
            requires_follow_up=True,
            follow_up_date=datetime.now(),
            communication_date=datetime.now(),
            created_at=datetime.now()
        )
        mock_service.get_communication_logs.return_value = [mock_log]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_communication_logs
        
        # Call the function
        result = await get_communication_logs(
            student_id=1,
            course_id=1,
            communication_type="email",
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_communication_logs.assert_called_once()
        assert result == [mock_log]

if __name__ == "__main__":
    pytest.main([__file__])
