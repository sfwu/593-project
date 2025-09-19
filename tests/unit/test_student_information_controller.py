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
            recorded_by=1,
            created_at=datetime.now(),
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
            updated_at=datetime.now()
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
        mock_service.update_student_directory.return_value = mock_student_directory_response
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import update_student_directory
        
        # Create update data
        update_data = StudentDirectoryUpdate(
            phone="987-654-3210",
            gpa=3.7,
            notes="Updated notes"
        )
        
        # Call the function
        result = await update_student_directory(
            student_id=1,
            directory_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_student_directory.assert_called_once_with(1, update_data)
        assert result == mock_student_directory_response

    # Academic Records Tests
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_academic_records(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of student academic records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_student_academic_records.return_value = [mock_student_performance_response]
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
        mock_service.get_student_academic_records.assert_called_once_with(1)
        assert result == [mock_student_performance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_course_academic_records(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of course academic records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_course_academic_records.return_value = [mock_student_performance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_course_academic_records
        
        # Call the function
        result = await get_course_academic_records(
            course_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_course_academic_records.assert_called_once_with(1)
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
            performance_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_student_performance.assert_called_once_with(1, update_data)
        assert result == mock_student_performance_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_at_risk_students(self, mock_service_class, mock_db, mock_professor, mock_student_performance_response):
        """Test retrieval of at-risk students"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_at_risk_students.return_value = [mock_student_performance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_at_risk_students
        
        # Call the function
        result = await get_at_risk_students(
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_at_risk_students.assert_called_once()
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
        mock_service.get_student_risk_assessment.return_value = mock_risk_assessment
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_student_risk_assessment
        
        # Call the function
        result = await get_student_risk_assessment(
            student_id=1,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_student_risk_assessment.assert_called_once_with(1)
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
        mock_service.bulk_create_attendance.return_value = [mock_attendance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import bulk_create_attendance
        
        # Create bulk data
        bulk_data = BulkAttendanceCreate(
            course_id=1,
            attendance_date=datetime.now(),
            attendances=[
                AttendanceCreate(
                    student_id=1,
                    course_id=1,
                    attendance_date=datetime.now(),
                    status=AttendanceStatus.PRESENT
                )
            ]
        )
        
        # Call the function
        result = await bulk_create_attendance(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.bulk_create_attendance.assert_called_once_with(bulk_data, 1)
        assert result == [mock_attendance_response]
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_attendance(self, mock_service_class, mock_db, mock_professor, mock_attendance_response):
        """Test retrieval of attendance records"""
        # Mock service instance
        mock_service = Mock()
        mock_service.get_attendance.return_value = [mock_attendance_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_attendance
        
        # Call the function
        result = await get_attendance(
            course_id=1,
            student_id=1,
            date_from=datetime.now() - timedelta(days=30),
            date_to=datetime.now(),
            status=AttendanceStatus.PRESENT,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_attendance.assert_called_once()
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
        from controllers.student_information_controller import update_attendance
        
        # Create update data
        update_data = AttendanceUpdate(
            status=AttendanceStatus.LATE,
            late_minutes=15,
            notes="Student arrived late"
        )
        
        # Call the function
        result = await update_attendance(
            attendance_id=1,
            attendance_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_attendance.assert_called_once_with(1, update_data)
        assert result == mock_attendance_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_attendance_summary(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of attendance summary"""
        # Mock service instance
        mock_service = Mock()
        mock_summary = AttendanceSummaryResponse(
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
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_attendance_summary.assert_called_once_with(1)
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
            sender_id=1,
            course_id=1,
            subject="Assignment Due Date",
            content="Please remember that the assignment is due next week.",
            message_type=MessageType.ASSIGNMENT,
            priority=MessagePriority.HIGH,
            is_broadcast=True,
            status=MessageStatus.DRAFT
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
            priority=MessagePriority.HIGH,
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
            content="Updated content",
            status=MessageStatus.SENT
        )
        
        # Call the function
        result = await update_message(
            message_id=1,
            message_update=update_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.update_message.assert_called_once_with(1, update_data)
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
        mock_service.send_message.assert_called_once_with(1)
        assert result == mock_message_response
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_bulk_create_messages(self, mock_service_class, mock_db, mock_professor, mock_message_response):
        """Test bulk message creation"""
        # Mock service instance
        mock_service = Mock()
        mock_service.bulk_create_messages.return_value = [mock_message_response]
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import bulk_create_messages
        
        # Create bulk data
        bulk_data = BulkMessageCreate(
            course_id=1,
            messages=[
                MessageCreate(
                    sender_id=1,
                    subject="Test Message",
                    content="This is a test message.",
                    message_type=MessageType.GENERAL,
                    priority=MessagePriority.NORMAL
                )
            ]
        )
        
        # Call the function
        result = await bulk_create_messages(
            bulk_data=bulk_data,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.bulk_create_messages.assert_called_once_with(bulk_data, 1)
        assert result == [mock_message_response]

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
            at_risk_students=5,
            recent_attendance_rate=85.0,
            pending_messages=10,
            upcoming_deadlines=3,
            recent_activities=[],
            generated_at=datetime.now()
        )
        mock_service.get_professor_dashboard.return_value = mock_dashboard
        mock_service_class.return_value = mock_service
        
        # Import the function
        from controllers.student_information_controller import get_professor_dashboard
        
        # Call the function
        result = await get_professor_dashboard(
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_professor_dashboard.assert_called_once_with(1)
        assert result == mock_dashboard
    
    @patch('controllers.student_information_controller.StudentInformationService')
    @pytest.mark.asyncio
    async def test_get_student_dashboard(self, mock_service_class, mock_db, mock_professor):
        """Test retrieval of student dashboard"""
        # Mock service instance
        mock_service = Mock()
        mock_dashboard = StudentDashboardSummary(
            student_id=1,
            current_gpa=3.5,
            attendance_rate=90.0,
            courses_enrolled=5,
            assignments_due=3,
            recent_grades=[],
            attendance_summary=[],
            messages_unread=2,
            generated_at=datetime.now()
        )
        mock_service.get_student_dashboard.return_value = mock_dashboard
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
        mock_service.get_student_dashboard.assert_called_once_with(1)
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
            created_at=datetime.now(),
            updated_at=datetime.now()
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
            requires_follow_up=True,
            current_professor=mock_professor,
            db=mock_db
        )
        
        # Assertions
        mock_service.get_communication_logs.assert_called_once()
        assert result == [mock_log]

if __name__ == "__main__":
    pytest.main([__file__])
