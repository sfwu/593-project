"""
Academic Record Pipeline Integration Tests
Tests the complete academic record workflow from grades to transcripts.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class TestBasicAcademicRecordIntegration:
    """Basic academic record integration tests"""
    
    def test_academic_records_access(self, integration_client, integration_db, auth_student_headers):
        """Test basic academic records access"""
        response = integration_client.get("/academic-records/grades", headers=auth_student_headers)
        assert response.status_code == 200
        grades = response.json()
        assert isinstance(grades, list)
    
    def test_gpa_calculation_access(self, integration_client, integration_db, auth_student_headers):
        """Test GPA calculation access"""
        response = integration_client.get("/academic-records/gpa", headers=auth_student_headers)
        assert response.status_code == 200
        gpa_data = response.json()
        assert "cumulative_gpa" in gpa_data
        assert "major_gpa" in gpa_data
    
    def test_academic_progress_access(self, integration_client, integration_db, auth_student_headers):
        """Test academic progress access"""
        response = integration_client.get("/academic-records/progress", headers=auth_student_headers)
        assert response.status_code in [200, 404]  # 404 if no progress record exists
    
    def test_grade_history_access(self, integration_client, integration_db, auth_student_headers):
        """Test grade history access"""
        response = integration_client.get("/academic-records/grade-history", headers=auth_student_headers)
        assert response.status_code == 200
        history = response.json()
        assert "student_id" in history
        assert "total_courses" in history
        assert "cumulative_gpa" in history
    
    def test_semester_gpa_breakdown(self, integration_client, integration_db, auth_student_headers):
        """Test semester GPA breakdown"""
        response = integration_client.get("/academic-records/gpa/semester-breakdown", headers=auth_student_headers)
        assert response.status_code == 200
        breakdown = response.json()
        assert isinstance(breakdown, list)
    
    def test_current_semester_gpa(self, integration_client, integration_db, auth_student_headers):
        """Test current semester GPA"""
        response = integration_client.get("/academic-records/gpa/current-semester", headers=auth_student_headers)
        assert response.status_code == 200
        current_gpa = response.json()
        assert "current_semester_gpa" in current_gpa
    
    def test_academic_dashboard(self, integration_client, integration_db, auth_student_headers):
        """Test academic dashboard"""
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "overview" in dashboard
        assert "recent_grades" in dashboard
    
    def test_academic_summary(self, integration_client, integration_db, auth_student_headers):
        """Test academic summary"""
        response = integration_client.get("/academic-records/academic-summary", headers=auth_student_headers)
        assert response.status_code == 200
        summary = response.json()
        assert "student_info" in summary
        assert "gpa_summary" in summary
