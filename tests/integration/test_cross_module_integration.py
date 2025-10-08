"""
Cross-Module Integration Tests
Tests interactions and data flow between different modules of the system.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestBasicCrossModuleIntegration:
    """Basic integration tests across modules"""
    
    def test_student_registration_and_course_access(self, integration_client, integration_db):
        """Test student can register and access courses"""
        # Register student
        student_data = {
            "email": "crossmod1@example.com",
            "password": "password123",
            "student_id": "CM001",
            "first_name": "Cross",
            "last_name": "Module",
            "major": "Computer Science",
            "year_level": "Sophomore"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login
        login_data = {"email": "crossmod1@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access courses
        response = integration_client.get("/courses", headers=headers)
        assert response.status_code == 200
    
    def test_professor_registration_and_course_creation(self, integration_client, integration_db):
        """Test professor can register and create courses"""
        # Register professor
        prof_data = {
            "email": "crossprof1@example.com",
            "password": "password123",
            "professor_id": "CPROF001",
            "first_name": "Cross",
            "last_name": "Professor",
            "department": "Computer Science",
            "title": "Assistant Professor"
        }
        
        response = integration_client.post("/auth/register/professor", json=prof_data)
        assert response.status_code == 200
        
        # Login
        login_data = {"email": "crossprof1@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create course
        course_data = {
            "course_code": "CM101",
            "title": "Cross Module Test Course",
            "description": "Test course",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=headers)
        assert response.status_code == 200
    
    def test_enrollment_and_grade_access(self, integration_client, integration_db,
                                        auth_professor_headers, auth_student_headers):
        """Test student enrollment and grade access"""
        # Professor creates course
        course_data = {
            "course_code": "CM102",
            "title": "Enrollment Grade Test",
            "description": "Test course",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        
        # Student enrolls
        enrollment_data = {"course_id": course["id"]}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # Student checks grades
        response = integration_client.get("/academic-records/grades", headers=auth_student_headers)
        assert response.status_code == 200
    
    def test_course_and_academic_records(self, integration_client, integration_db, auth_student_headers):
        """Test course enrollment affects academic records"""
        # Check academic dashboard
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "overview" in dashboard
    
    def test_authentication_and_authorization(self, integration_client, integration_db,
                                             auth_student_headers, auth_professor_headers):
        """Test authentication works across modules"""
        # Student access
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        
        # Professor access
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        assert response.status_code == 200
    
    def test_role_based_access_control(self, integration_client, integration_db,
                                      auth_student_headers, auth_professor_headers):
        """Test role-based access control across modules"""
        # Student cannot access professor endpoints
        response = integration_client.get("/professors/courses", headers=auth_student_headers)
        assert response.status_code == 403
        
        # Professor cannot access student endpoints
        response = integration_client.put("/students/profile", json={}, headers=auth_professor_headers)
        assert response.status_code == 403
    
    def test_data_consistency_across_modules(self, integration_client, integration_db, auth_student_headers):
        """Test data remains consistent across different module accesses"""
        # Access GPA
        response = integration_client.get("/academic-records/gpa", headers=auth_student_headers)
        assert response.status_code == 200
        
        # Access progress
        response = integration_client.get("/academic-records/progress", headers=auth_student_headers)
        assert response.status_code in [200, 404]  # 404 if no progress exists
    
    def test_error_handling_across_modules(self, integration_client, integration_db, auth_student_headers):
        """Test error handling works consistently across modules"""
        # Try to access non-existent course
        response = integration_client.get("/courses/99999", headers=auth_student_headers)
        assert response.status_code == 404
        
        # Try to enroll in non-existent course
        enrollment_data = {"course_id": 99999}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 404
