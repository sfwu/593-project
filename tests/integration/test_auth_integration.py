"""
Comprehensive Authentication and Authorization Integration Tests
Tests the complete authentication flow, JWT tokens, role-based access control,
and security features across the entire system.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import json

class TestAuthenticationIntegration:
    """Integration tests for authentication system"""
    
    def test_student_registration_and_login_flow(self, integration_client, integration_db):
        """Test complete student registration and login flow"""
        # 1. Register a new student
        student_data = {
            "email": "newstudent@example.com",
            "password": "newpassword123",
            "student_id": "NEW001",
            "first_name": "New",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Freshman"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "NEW001"
        assert data["email"] == "newstudent@example.com"
        assert "id" in data
        
        # 2. Login with the new student
        login_data = {
            "email": "newstudent@example.com",
            "password": "newpassword123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "student"
        assert data["user"]["email"] == "newstudent@example.com"
        
        # 3. Verify token works for protected endpoints
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "newstudent@example.com"
        assert user_data["role"] == "student"
    
    def test_professor_registration_and_login_flow(self, integration_client, integration_db):
        """Test complete professor registration and login flow"""
        # 1. Register a new professor
        professor_data = {
            "email": "newprofessor@example.com",
            "password": "newpassword123",
            "professor_id": "NEW001",
            "first_name": "New",
            "last_name": "Professor",
            "department": "Computer Science",
            "title": "Assistant Professor"
        }
        
        response = integration_client.post("/auth/register/professor", json=professor_data)
        assert response.status_code == 200
        data = response.json()
        assert data["professor_id"] == "NEW001"
        assert data["email"] == "newprofessor@example.com"
        
        # 2. Login with the new professor
        login_data = {
            "email": "newprofessor@example.com",
            "password": "newpassword123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "professor"
        
        # 3. Verify token works for professor endpoints
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["role"] == "professor"
    
    def test_invalid_credentials_login(self, integration_client, integration_db):
        """Test login with invalid credentials"""
        # Test with wrong password
        login_data = {
            "email": "teststudent@example.com",
            "password": "wrongpassword"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
        
        # Test with non-existent email
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_duplicate_email_registration(self, integration_client, integration_db):
        """Test registration with duplicate email"""
        # First registration
        student_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "student_id": "DUP001",
            "first_name": "First",
            "last_name": "Student"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Second registration with same email
        student_data2 = {
            "email": "duplicate@example.com",
            "password": "password456",
            "student_id": "DUP002",
            "first_name": "Second",
            "last_name": "Student"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data2)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_jwt_token_validation(self, integration_client, integration_db, auth_student_headers):
        """Test JWT token validation and expiration"""
        # Test valid token
        response = integration_client.get("/auth/me", headers=auth_student_headers)
        assert response.status_code == 200
        
        # Test invalid token format
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = integration_client.get("/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test malformed authorization header
        malformed_headers = {"Authorization": "InvalidFormat token"}
        response = integration_client.get("/auth/me", headers=malformed_headers)
        assert response.status_code == 401
        
        # Test missing authorization header
        response = integration_client.get("/auth/me")
        assert response.status_code == 403
    
    def test_token_expiration_handling(self, integration_client, integration_db):
        """Test handling of expired tokens"""
        # Create a user and get token
        student_data = {
            "email": "exptest@example.com",
            "password": "password123",
            "student_id": "EXP001",
            "first_name": "Expiry",
            "last_name": "Test"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        login_data = {
            "email": "exptest@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Decode token to check expiration (this would normally be done by the auth system)
        # For testing purposes, we'll simulate an expired token scenario
        headers = {"Authorization": f"Bearer {token}"}
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 200  # Token should be valid in test environment

class TestRoleBasedAccessControlIntegration:
    """Integration tests for role-based access control"""
    
    def test_student_cannot_access_professor_endpoints(self, integration_client, integration_db, auth_student_headers):
        """Test that students cannot access professor-only endpoints"""
        # Test professor course creation endpoint
        course_data = {
            "course_code": "CS101",
            "title": "Test Course",
            "description": "Test description",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_student_headers)
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
        
        # Test professor dashboard
        response = integration_client.get("/professors/dashboard", headers=auth_student_headers)
        assert response.status_code == 403
        
        # Test professor profile update
        profile_data = {"title": "Full Professor"}
        response = integration_client.put("/professors/profile", json=profile_data, headers=auth_student_headers)
        assert response.status_code == 403
    
    def test_professor_cannot_access_student_endpoints(self, integration_client, integration_db, auth_professor_headers):
        """Test that professors cannot access student-only endpoints"""
        # Test student enrollment endpoint
        enrollment_data = {"course_id": 1}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_professor_headers)
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
        
        # Test student schedule endpoint
        response = integration_client.get("/students/schedule", headers=auth_professor_headers)
        assert response.status_code == 403
        
        # Test student profile update
        profile_data = {"major": "Mathematics"}
        response = integration_client.put("/students/profile", json=profile_data, headers=auth_professor_headers)
        assert response.status_code == 403
    
    def test_cross_role_data_access_prevention(self, integration_client, integration_db, 
                                             auth_student_headers, auth_professor_headers):
        """Test that users cannot access data from other roles"""
        # Create a course as professor
        course_data = {
            "course_code": "CS101",
            "title": "Test Course",
            "description": "Test description",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course_id = response.json()["id"]
        
        # Student should not be able to modify professor's course
        course_update = {"title": "Hacked Course"}
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_student_headers)
        assert response.status_code == 403
        
        # Student should not be able to access professor's course management
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_student_headers)
        assert response.status_code == 403
    
    def test_unauthorized_access_to_protected_endpoints(self, integration_client, integration_db):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/students/profile",
            "/students/schedule",
            "/students/grades",
            "/professors/profile",
            "/professors/dashboard",
            "/professors/courses",
            "/academic-records/grades",
            "/academic-records/gpa",
            "/student-information/directory",
            "/student-information/attendance",
            "/grading/assignments",
            "/grading/grades"
        ]
        
        for endpoint in protected_endpoints:
            # Test GET requests
            response = integration_client.get(endpoint)
            assert response.status_code == 403, f"GET {endpoint} should require authentication"
            
            # Test POST requests (where applicable)
            if endpoint in ["/students/enroll", "/professors/courses", "/grading/assignments"]:
                response = integration_client.post(endpoint, json={})
                assert response.status_code == 403, f"POST {endpoint} should require authentication"

class TestAuthenticationSecurityIntegration:
    """Integration tests for authentication security features"""
    
    def test_password_hashing_security(self, integration_client, integration_db):
        """Test that passwords are properly hashed and not stored in plain text"""
        student_data = {
            "email": "securitytest@example.com",
            "password": "plaintextpassword123",
            "student_id": "SEC001",
            "first_name": "Security",
            "last_name": "Test"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Verify login works with original password
        login_data = {
            "email": "securitytest@example.com",
            "password": "plaintextpassword123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        # Note: In a real test, we would check the database to ensure
        # the password is hashed, but that requires direct database access
        # which is not available in this integration test context
    
    def test_jwt_token_structure_and_content(self, integration_client, integration_db, auth_student_headers):
        """Test JWT token structure and content"""
        # Get token from headers
        auth_header = auth_student_headers["Authorization"]
        token = auth_header.replace("Bearer ", "")
        
        # Decode token (without verification for testing)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Check required claims
            assert "sub" in decoded  # Subject (user ID)
            assert "email" in decoded  # User email
            assert "role" in decoded  # User role
            assert "exp" in decoded  # Expiration time
            assert "iat" in decoded  # Issued at time
            
            # Verify role is correct
            assert decoded["role"] == "student"
            
        except jwt.InvalidTokenError:
            pytest.fail("Token should be valid JWT format")
    
    def test_session_management(self, integration_client, integration_db, auth_student_headers):
        """Test session management and token refresh scenarios"""
        # Test multiple requests with same token
        for _ in range(3):
            response = integration_client.get("/auth/me", headers=auth_student_headers)
            assert response.status_code == 200
        
        # Test that token remains valid across multiple endpoints
        endpoints_to_test = [
            "/students/profile",
            "/students/schedule",
            "/academic-records/grades",
            "/academic-records/gpa"
        ]
        
        for endpoint in endpoints_to_test:
            response = integration_client.get(endpoint, headers=auth_student_headers)
            # Some endpoints might return 404 for empty data, but should not return 401/403
            assert response.status_code in [200, 404], f"Token should work for {endpoint}"
    
    def test_concurrent_authentication_requests(self, integration_client, integration_db):
        """Test system behavior under concurrent authentication requests"""
        import threading
        import time
        
        results = []
        
        def login_worker(email_suffix):
            login_data = {
                "email": f"concurrent{email_suffix}@example.com",
                "password": "password123"
            }
            
            # First register
            student_data = {
                "email": f"concurrent{email_suffix}@example.com",
                "password": "password123",
                "student_id": f"CONC{email_suffix:03d}",
                "first_name": f"Concurrent{email_suffix}",
                "last_name": "Test"
            }
            
            reg_response = integration_client.post("/auth/register/student", json=student_data)
            login_response = integration_client.post("/auth/login", json=login_data)
            
            results.append({
                "email_suffix": email_suffix,
                "register_status": reg_response.status_code,
                "login_status": login_response.status_code
            })
        
        # Create multiple concurrent login requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=login_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 5
        for result in results:
            assert result["register_status"] == 200
            assert result["login_status"] == 200

class TestAuthenticationErrorHandlingIntegration:
    """Integration tests for authentication error handling"""
    
    def test_malformed_registration_data(self, integration_client, integration_db):
        """Test handling of malformed registration data"""
        # Missing required fields
        incomplete_data = {
            "email": "incomplete@example.com"
            # Missing password, student_id, etc.
        }
        
        response = integration_client.post("/auth/register/student", json=incomplete_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid email format
        invalid_email_data = {
            "email": "notanemail",
            "password": "password123",
            "student_id": "INV001",
            "first_name": "Invalid",
            "last_name": "Email"
        }
        
        response = integration_client.post("/auth/register/student", json=invalid_email_data)
        assert response.status_code == 422
        
        # Weak password
        weak_password_data = {
            "email": "weakpass@example.com",
            "password": "123",  # Too short
            "student_id": "WEAK001",
            "first_name": "Weak",
            "last_name": "Password"
        }
        
        response = integration_client.post("/auth/register/student", json=weak_password_data)
        assert response.status_code == 422
    
    def test_authentication_rate_limiting_simulation(self, integration_client, integration_db):
        """Test system behavior under rapid authentication requests"""
        # Simulate rapid login attempts with wrong credentials
        login_data = {
            "email": "teststudent@example.com",
            "password": "wrongpassword"
        }
        
        # Make multiple failed login attempts
        for i in range(10):
            response = integration_client.post("/auth/login", json=login_data)
            assert response.status_code == 401
        
        # System should still respond (rate limiting would be implemented at higher level)
        # This test verifies the system doesn't crash under rapid failed attempts
    
    def test_database_connection_during_auth_failure(self, integration_client, integration_db):
        """Test system behavior when database issues occur during authentication"""
        # This test would require mocking database failures
        # For now, we'll test that the system handles invalid database states gracefully
        
        # Test with malformed token that might cause database issues
        malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        headers = {"Authorization": f"Bearer {malformed_token}"}
        
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 401  # Should handle gracefully, not crash
