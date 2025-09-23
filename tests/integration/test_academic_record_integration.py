"""
Integration tests for Academic Record functionality
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
from models.course import Course
from models.academic_record import AcademicRecord, GradeStatus
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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
def test_user():
    """Create test user"""
    return {
        "email": "teststudent@example.com",
        "password": "testpassword123",
        "role": "student"
    }

@pytest.fixture
def test_student_data():
    """Test student data"""
    return {
        "student_id": "STU001",
        "first_name": "John",
        "last_name": "Doe",
        "major": "Computer Science",
        "year_level": "Junior"
    }

@pytest.fixture
def auth_headers(client, test_user, test_student_data):
    """Get authentication headers for test user"""
    # Register student
    register_data = {**test_user, **test_student_data}
    response = client.post("/auth/register/student", json=register_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_course(client, auth_headers):
    """Create a sample course for testing"""
    # This would typically be done by a professor, but for testing we'll create it directly
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
    
    # Note: In a real scenario, this would be created by a professor
    # For testing purposes, we'll assume the course exists
    return course_data

class TestAcademicRecordIntegration:
    """Integration tests for academic record endpoints"""
    
    def test_get_student_grades_empty(self, client, auth_headers):
        """Test getting student grades when none exist"""
        response = client.get("/academic-records/grades", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_gpa_calculation_empty(self, client, auth_headers):
        """Test GPA calculation when no grades exist"""
        response = client.get("/academic-records/gpa", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["cumulative_gpa"] == 0.0
        assert data["major_gpa"] == 0.0
        assert data["semester_gpa"] == 0.0
        assert data["total_credits_earned"] == 0
        assert data["total_credits_attempted"] == 0
        assert data["grade_distribution"] == {}
        assert data["semester_breakdown"] == []
    
    def test_get_academic_progress_not_found(self, client, auth_headers):
        """Test getting academic progress when not initialized"""
        response = client.get("/academic-records/progress", headers=auth_headers)
        assert response.status_code == 404
        assert "Academic progress not found" in response.json()["detail"]
    
    def test_get_academic_progress_summary_not_found(self, client, auth_headers):
        """Test getting academic progress summary when not initialized"""
        response = client.get("/academic-records/progress/summary", headers=auth_headers)
        assert response.status_code == 404
        assert "Academic progress not found" in response.json()["detail"]
    
    def test_get_grade_history_empty(self, client, auth_headers):
        """Test getting grade history when none exist"""
        response = client.get("/academic-records/grade-history", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["student_id"] is not None
        assert data["total_courses"] == 0
        assert data["courses_completed"] == 0
        assert data["courses_incomplete"] == 0
        assert data["courses_withdrawn"] == 0
        assert data["cumulative_gpa"] == 0.0
        assert data["grade_summary"] == []
        assert data["semester_breakdown"] == []
    
    def test_get_academic_dashboard_empty(self, client, auth_headers):
        """Test getting academic dashboard when no data exists"""
        response = client.get("/academic-records/dashboard", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "recent_grades" in data
        assert "progress" in data
        assert "semester_trend" in data
        assert "grade_distribution" in data
        
        overview = data["overview"]
        assert overview["cumulative_gpa"] == 0.0
        assert overview["major_gpa"] == 0.0
        assert overview["current_semester_gpa"] == 0.0
        assert overview["total_credits_earned"] == 0
        assert data["recent_grades"] == []
        assert data["semester_trend"] == []
        assert data["grade_distribution"] == {}
    
    def test_get_semester_gpa_breakdown_empty(self, client, auth_headers):
        """Test getting semester GPA breakdown when none exist"""
        response = client.get("/academic-records/gpa/semester-breakdown", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_current_semester_gpa_empty(self, client, auth_headers):
        """Test getting current semester GPA when none exist"""
        response = client.get("/academic-records/gpa/current-semester", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["current_semester_gpa"] == 0.0
        assert data["cumulative_gpa"] == 0.0
        assert data["major_gpa"] == 0.0
        assert data["total_credits_earned"] == 0
        assert data["total_credits_attempted"] == 0
    
    def test_get_transcripts_empty(self, client, auth_headers):
        """Test getting transcripts when none exist"""
        response = client.get("/academic-records/transcripts", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_generate_transcript_success(self, client, auth_headers):
        """Test generating a transcript"""
        request_data = {
            "transcript_type": "official",
            "include_incomplete": False,
            "include_withdrawn": False
        }
        
        response = client.post("/academic-records/transcripts/generate", 
                             json=request_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "transcript_id" in data
        assert data["status"] == "generated"
        assert "generated_at" in data
    
    def test_get_academic_summary_empty(self, client, auth_headers):
        """Test getting academic summary when no data exists"""
        response = client.get("/academic-records/academic-summary", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "student_info" in data
        assert "gpa_summary" in data
        assert "progress_summary" in data
        assert "grade_statistics" in data
        assert "semester_breakdown" in data
        
        student_info = data["student_info"]
        assert "student_id" in student_info
        assert "name" in student_info
        assert "major" in student_info
        assert "year_level" in student_info
        
        gpa_summary = data["gpa_summary"]
        assert gpa_summary["cumulative_gpa"] == 0.0
        assert gpa_summary["major_gpa"] == 0.0
        assert gpa_summary["current_semester_gpa"] == 0.0
        assert gpa_summary["total_credits_earned"] == 0
        assert gpa_summary["total_credits_attempted"] == 0
        
        grade_stats = data["grade_statistics"]
        assert grade_stats["total_courses"] == 0
        assert grade_stats["courses_completed"] == 0
        assert grade_stats["courses_incomplete"] == 0
        assert grade_stats["courses_withdrawn"] == 0
        assert grade_stats["grade_distribution"] == {}
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        endpoints = [
            "/academic-records/grades",
            "/academic-records/gpa",
            "/academic-records/transcripts",
            "/academic-records/progress",
            "/academic-records/dashboard"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 403
    
    def test_invalid_grade_record_access(self, client, auth_headers):
        """Test accessing non-existent grade record"""
        response = client.get("/academic-records/grades/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Grade record not found" in response.json()["detail"]
    
    def test_invalid_transcript_download(self, client, auth_headers):
        """Test downloading non-existent transcript"""
        response = client.get("/academic-records/transcripts/999/download", headers=auth_headers)
        assert response.status_code == 404
        assert "Transcript not found" in response.json()["detail"]
    
    def test_grade_filtering(self, client, auth_headers):
        """Test grade filtering by semester and year"""
        # Test filtering by semester
        response = client.get("/academic-records/grades?semester=Fall", headers=auth_headers)
        assert response.status_code == 200
        
        # Test filtering by year
        response = client.get("/academic-records/grades?year=2024", headers=auth_headers)
        assert response.status_code == 200
        
        # Test filtering by status
        response = client.get("/academic-records/grades?status=graded", headers=auth_headers)
        assert response.status_code == 200
        
        # Test combined filtering
        response = client.get("/academic-records/grades?semester=Fall&year=2024&status=graded", headers=auth_headers)
        assert response.status_code == 200
