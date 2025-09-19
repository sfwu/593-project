"""
Integration tests for Student Information Management functionality
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from main import app
from config.database import Base, get_db
from models.user import User, UserRole
from models.student import Student
from models.professor import Professor
from models.course import Course
from models.student_information import Attendance, Message, AttendanceStatus, MessageStatus
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_student_information_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_professor_user():
    """Test professor user data"""
    return {
        "email": "testprofessor@example.com",
        "password": "testpassword123",
        "role": "professor"
    }

@pytest.fixture
def test_professor_data():
    """Test professor data"""
    return {
        "professor_id": "PROF001",
        "first_name": "Jane",
        "last_name": "Smith",
        "department": "Computer Science",
        "title": "Assistant Professor"
    }

@pytest.fixture
def auth_headers(client, test_professor_user, test_professor_data):
    """Get authentication headers for test professor"""
    # Register professor
    register_data = {**test_professor_user, **test_professor_data}
    response = client.post("/auth/register/professor", json=register_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "email": test_professor_user["email"],
        "password": test_professor_user["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_course(client, auth_headers):
    """Create a sample course for testing"""
    course_data = {
        "course_code": "CS101",
        "title": "Introduction to Computer Science",
        "description": "Basic computer science concepts",
        "credits": 3,
        "department": "Computer Science",
        "semester": "Fall",
        "year": 2024,
        "max_enrollment": 30
    }
    
    response = client.post("/professors/courses", json=course_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()

class TestStudentInformationIntegration:
    """Integration tests for student information endpoints"""
    
    def test_get_student_directory_empty(self, client, auth_headers):
        """Test getting student directory when empty"""
        response = client.get("/student-information/directory", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_student_directory_with_filters(self, client, auth_headers):
        """Test getting student directory with filters"""
        # Test with name filter
        response = client.get("/student-information/directory?name=John", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with major filter
        response = client.get("/student-information/directory?major=Computer Science", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with year level filter
        response = client.get("/student-information/directory?year_level=Junior", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_student_directory_entry_not_found(self, client, auth_headers):
        """Test getting non-existent student directory entry"""
        response = client.get("/student-information/directory/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Student directory entry not found" in response.json()["detail"]
    
    def test_get_academic_records_empty(self, client, auth_headers):
        """Test getting academic records when none exist"""
        response = client.get("/student-information/academic-records/1", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_course_student_performance_empty(self, client, auth_headers, sample_course):
        """Test getting course student performance when none exist"""
        response = client.get(f"/student-information/academic-records/course/{sample_course['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_students_at_risk_empty(self, client, auth_headers):
        """Test getting students at risk when none exist"""
        response = client.get("/student-information/academic-records/at-risk", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_assess_student_risk_not_found(self, client, auth_headers):
        """Test assessing risk for non-existent student"""
        response = client.get("/student-information/academic-records/risk-assessment/999?course_id=1", headers=auth_headers)
        assert response.status_code == 200
        # Should return default no-risk assessment
        data = response.json()
        assert data["is_at_risk"] == False
        assert data["risk_factors"] == []
    
    def test_create_attendance_validation_error(self, client, auth_headers, sample_course):
        """Test creating attendance with validation error"""
        attendance_data = {
            "student_id": 1,
            "course_id": sample_course["id"],
            "attendance_date": "2024-01-15T10:00:00",
            "status": "present",
            "late_minutes": -5  # Invalid negative value
        }
        
        response = client.post("/student-information/attendance", json=attendance_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Late minutes cannot be negative" in response.json()["detail"]
    
    def test_get_attendance_records_empty(self, client, auth_headers):
        """Test getting attendance records when none exist"""
        response = client.get("/student-information/attendance", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_attendance_records_with_filters(self, client, auth_headers, sample_course):
        """Test getting attendance records with filters"""
        # Test with course filter
        response = client.get(f"/student-information/attendance?course_id={sample_course['id']}", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with status filter
        response = client.get("/student-information/attendance?status=present", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with date filters
        response = client.get("/student-information/attendance?date_from=2024-01-01&date_to=2024-12-31", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_attendance_record_not_found(self, client, auth_headers):
        """Test getting non-existent attendance record"""
        response = client.get("/student-information/attendance/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Attendance record not found" in response.json()["detail"]
    
    def test_get_attendance_summary_not_found(self, client, auth_headers):
        """Test getting non-existent attendance summary"""
        response = client.get("/student-information/attendance/summary/999?course_id=1", headers=auth_headers)
        assert response.status_code == 404
        assert "Attendance summary not found" in response.json()["detail"]
    
    def test_get_attendance_report_course_not_found(self, client, auth_headers):
        """Test getting attendance report for non-existent course"""
        response = client.get("/student-information/attendance/report/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]
    
    def test_create_message_validation_error(self, client, auth_headers):
        """Test creating message with validation error"""
        message_data = {
            "course_id": 1,
            "subject": "Test Message",
            "content": "This is a test message.",
            "is_broadcast": True,
            "recipient_ids": []  # Empty recipients for broadcast message
        }
        
        response = client.post("/student-information/messages", json=message_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Broadcast messages must have recipient IDs" in response.json()["detail"]
    
    def test_get_messages_empty(self, client, auth_headers):
        """Test getting messages when none exist"""
        response = client.get("/student-information/messages", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_messages_with_filters(self, client, auth_headers, sample_course):
        """Test getting messages with filters"""
        # Test with course filter
        response = client.get(f"/student-information/messages?course_id={sample_course['id']}", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with message type filter
        response = client.get("/student-information/messages?message_type=announcement", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with status filter
        response = client.get("/student-information/messages?status=draft", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_message_not_found(self, client, auth_headers):
        """Test getting non-existent message"""
        response = client.get("/student-information/messages/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Message not found" in response.json()["detail"]
    
    def test_send_message_not_found(self, client, auth_headers):
        """Test sending non-existent message"""
        response = client.post("/student-information/messages/999/send", headers=auth_headers)
        assert response.status_code == 404
        assert "Message not found or cannot be sent" in response.json()["detail"]
    
    def test_get_message_recipients_not_found(self, client, auth_headers):
        """Test getting recipients for non-existent message"""
        response = client.get("/student-information/messages/999/recipients", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_message_report(self, client, auth_headers):
        """Test getting message report"""
        response = client.get("/student-information/messages/report", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_messages_sent" in data
        assert "messages_by_type" in data
        assert "messages_by_priority" in data
        assert "delivery_stats" in data
        assert "recent_messages" in data
    
    def test_get_communication_logs_empty(self, client, auth_headers):
        """Test getting communication logs when none exist"""
        response = client.get("/student-information/communication-logs", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_communication_logs_with_filters(self, client, auth_headers, sample_course):
        """Test getting communication logs with filters"""
        # Test with student filter
        response = client.get("/student-information/communication-logs?student_id=1", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with course filter
        response = client.get(f"/student-information/communication-logs?course_id={sample_course['id']}", headers=auth_headers)
        assert response.status_code == 200
        
        # Test with communication type filter
        response = client.get("/student-information/communication-logs?communication_type=email", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_professor_dashboard(self, client, auth_headers):
        """Test getting professor dashboard"""
        response = client.get("/student-information/dashboard", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "professor_id" in data
        assert "total_students" in data
        assert "total_courses" in data
        assert "pending_messages" in data
        assert "students_at_risk" in data
        assert "attendance_alerts" in data
        assert "recent_communications" in data
    
    def test_get_student_dashboard(self, client, auth_headers):
        """Test getting student dashboard"""
        response = client.get("/student-information/dashboard/student/1", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "student_id" in data
        assert "student_name" in data
        assert "student_email" in data
        assert "courses_enrolled" in data
        assert "total_attendance_percentage" in data
        assert "unread_messages" in data
        assert "is_at_risk" in data
    
    def test_search_students(self, client, auth_headers):
        """Test searching students"""
        response = client.get("/student-information/search/students?query=John", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "total" in data
        assert data["query"] == "John"
    
    def test_get_attendance_trends(self, client, auth_headers, sample_course):
        """Test getting attendance trends"""
        response = client.get(f"/student-information/analytics/attendance-trends?course_id={sample_course['id']}&days=30", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "course_id" in data
        assert "period_days" in data
        assert "trends" in data
        assert data["course_id"] == sample_course["id"]
        assert data["period_days"] == 30
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        endpoints = [
            "/student-information/directory",
            "/student-information/academic-records/1",
            "/student-information/attendance",
            "/student-information/messages",
            "/student-information/dashboard"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403
    
    def test_bulk_attendance_validation_error(self, client, auth_headers, sample_course):
        """Test bulk attendance creation with validation error"""
        bulk_data = {
            "course_id": sample_course["id"],
            "attendance_date": "2024-01-15T10:00:00",
            "attendance_records": [
                {
                    "student_id": 1,
                    "status": "present",
                    "late_minutes": -5  # Invalid negative value
                }
            ]
        }
        
        response = client.post("/student-information/attendance/bulk", json=bulk_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Late minutes cannot be negative" in response.json()["detail"]
    
    def test_bulk_messages_creation(self, client, auth_headers, sample_course):
        """Test bulk message creation"""
        bulk_data = {
            "course_id": sample_course["id"],
            "subject": "Bulk Test Message",
            "content": "This is a bulk test message.",
            "message_type": "general",
            "priority": "normal",
            "recipient_ids": [1, 2, 3]
        }
        
        response = client.post("/student-information/bulk/messages", json=bulk_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Should return a list of messages
        messages = response.json()
        assert isinstance(messages, list)
