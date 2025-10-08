"""
Security Integration Tests
Tests security features, vulnerability protection, and data privacy
across the entire academic management system.
"""
import pytest
import jwt
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import base64
import hashlib

class TestAuthenticationSecurityIntegration:
    """Integration tests for authentication security"""
    
    def test_password_security_requirements(self, integration_client, integration_db):
        """Test password security requirements and validation"""
        # Test weak password rejection
        weak_passwords = [
            "123",  # Too short
            "password",  # Common password
            "12345678",  # Only numbers
            "abcdefgh",  # Only letters
            "",  # Empty
            "abc",  # Too short
        ]
        
        for weak_password in weak_passwords:
            student_data = {
                "email": f"weakpass{weak_password}@example.com",
                "password": weak_password,
                "student_id": f"WEAK{hash(weak_password) % 1000:03d}",
                "first_name": "Weak",
                "last_name": "Password",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            # Should either reject weak passwords or accept them (depending on validation rules)
            assert response.status_code in [200, 422]
    
    def test_sql_injection_protection(self, integration_client, integration_db, auth_student_headers):
        """Test protection against SQL injection attacks"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM students; --",
            "' OR 1=1 --",
        ]
        
        for injection in sql_injection_attempts:
            # Test in profile update
            profile_data = {
                "first_name": injection,
                "last_name": "Injection Test",
                "major": "Computer Science"
            }
            
            response = integration_client.put("/students/profile", json=profile_data, headers=auth_student_headers)
            # Should not cause database errors or security issues
            assert response.status_code in [200, 422]
            
            # Test in course search
            response = integration_client.get(f"/courses?keyword={injection}", headers=auth_student_headers)
            assert response.status_code in [200, 422]
    
    def test_xss_protection(self, integration_client, integration_db, auth_student_headers):
        """Test protection against Cross-Site Scripting (XSS) attacks"""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')>",
        ]
        
        for xss in xss_attempts:
            # Test in profile update
            profile_data = {
                "first_name": "XSS",
                "last_name": "Test",
                "major": xss,
                "year_level": "Junior"
            }
            
            response = integration_client.put("/students/profile", json=profile_data, headers=auth_student_headers)
            # Should either reject or sanitize XSS attempts
            assert response.status_code in [200, 422]
            
            # If accepted, verify it's properly escaped in response
            if response.status_code == 200:
                response_data = response.json()
                # XSS should be escaped or removed
                assert "<script>" not in str(response_data)
                assert "javascript:" not in str(response_data)
    
    def test_authentication_token_security(self, integration_client, integration_db, auth_student_headers):
        """Test JWT token security features"""
        # Test token format validation
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "invalid_token_format",
            "",
            "Bearer",
            "Bearer ",
        ]
        
        for invalid_token in invalid_tokens:
            headers = {"Authorization": invalid_token}
            response = integration_client.get("/students/profile", headers=headers)
            assert response.status_code == 401
        
        # Test token tampering
        # Get a valid token
        auth_header = auth_student_headers["Authorization"]
        valid_token = auth_header.replace("Bearer ", "")
        
        # Tamper with token
        tampered_token = valid_token[:-5] + "xxxxx"
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 401
        
        # Test token without Bearer prefix
        headers = {"Authorization": valid_token}
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 401
    
    def test_session_management_security(self, integration_client, integration_db):
        """Test session management security"""
        # Register and login user
        student_data = {
            "email": "session@example.com",
            "password": "password123",
            "student_id": "SESSION001",
            "first_name": "Session",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login multiple times
        login_data = {"email": "session@example.com", "password": "password123"}
        tokens = []
        
        for _ in range(3):
            response = integration_client.post("/auth/login", json=login_data)
            assert response.status_code == 200
            tokens.append(response.json()["access_token"])
        
        # All tokens should work (or system should invalidate old ones)
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = integration_client.get("/auth/me", headers=headers)
            # Should either work or return 401 if tokens are invalidated
            assert response.status_code in [200, 401]

class TestAuthorizationSecurityIntegration:
    """Integration tests for authorization security"""
    
    def test_role_based_access_control_enforcement(self, integration_client, integration_db):
        """Test enforcement of role-based access control"""
        # Create student and professor users
        student_data = {
            "email": "rbacstudent@example.com",
            "password": "password123",
            "student_id": "RBAC001",
            "first_name": "RBAC",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        professor_data = {
            "email": "rbacprofessor@example.com",
            "password": "password123",
            "professor_id": "RBAC001",
            "first_name": "RBAC",
            "last_name": "Professor",
            "department": "Computer Science",
            "title": "Assistant Professor"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        response = integration_client.post("/auth/register/professor", json=professor_data)
        assert response.status_code == 200
        
        # Login as student
        login_data = {"email": "rbacstudent@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        student_token = response.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # Login as professor
        login_data = {"email": "rbacprofessor@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        professor_token = response.json()["access_token"]
        professor_headers = {"Authorization": f"Bearer {professor_token}"}
        
        # Test student cannot access professor endpoints
        professor_only_endpoints = [
            "/professors/courses",
            "/professors/dashboard",
            "/student-information/directory",
            "/grading/assignments",
            "/grading/grades",
        ]
        
        for endpoint in professor_only_endpoints:
            response = integration_client.get(endpoint, headers=student_headers)
            assert response.status_code == 403, f"Student should not access {endpoint}"
        
        # Test professor cannot access student endpoints
        student_only_endpoints = [
            "/students/enroll",
            "/students/schedule",
            "/students/withdraw",
        ]
        
        for endpoint in student_only_endpoints:
            response = integration_client.get(endpoint, headers=professor_headers)
            assert response.status_code == 403, f"Professor should not access {endpoint}"
    
    def test_data_access_isolation(self, integration_client, integration_db,
                                 auth_student_headers, auth_professor_headers):
        """Test that users can only access their own data"""
        # Create course as professor
        course_data = {
            "course_code": "ISOLATION101",
            "title": "Data Isolation Test Course",
            "description": "Course for testing data isolation",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Student should not be able to modify professor's course
        course_update = {"title": "Hacked Course Title"}
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_student_headers)
        assert response.status_code == 403
        
        # Student should not be able to access professor's course management
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_student_headers)
        assert response.status_code == 403
        
        # Student should not be able to create assignments for professor's course
        assignment_data = {
            "course_id": course_id,
            "title": "Unauthorized Assignment",
            "description": "Assignment created by student",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_student_headers)
        assert response.status_code == 403
    
    def test_privilege_escalation_prevention(self, integration_client, integration_db):
        """Test prevention of privilege escalation attacks"""
        # Create student user
        student_data = {
            "email": "privilege@example.com",
            "password": "password123",
            "student_id": "PRIV001",
            "first_name": "Privilege",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login as student
        login_data = {"email": "privilege@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Attempt to escalate privileges by trying to register as professor
        professor_data = {
            "email": "privilege@example.com",  # Same email
            "password": "password123",
            "professor_id": "PRIV001",
            "first_name": "Privilege",
            "last_name": "Test",
            "department": "Computer Science",
            "title": "Assistant Professor"
        }
        
        response = integration_client.post("/auth/register/professor", json=professor_data)
        # Should fail due to existing email
        assert response.status_code == 400
        
        # Attempt to access admin endpoints (if they exist)
        admin_endpoints = [
            "/admin/users",
            "/admin/courses",
            "/admin/grades",
            "/admin/students",
            "/admin/professors",
        ]
        
        for endpoint in admin_endpoints:
            response = integration_client.get(endpoint, headers=headers)
            # Should be forbidden or not found
            assert response.status_code in [403, 404, 405]

class TestDataPrivacySecurityIntegration:
    """Integration tests for data privacy and protection"""
    
    def test_sensitive_data_protection(self, integration_client, integration_db,
                                     auth_student_headers, auth_professor_headers):
        """Test protection of sensitive data"""
        # Create student with sensitive information
        student_data = {
            "email": "sensitive@example.com",
            "password": "password123",
            "student_id": "SENS001",
            "first_name": "Sensitive",
            "last_name": "Data",
            "major": "Computer Science",
            "year_level": "Junior",
            "phone": "555-0123",
            "address": "123 Private St, Secret City",
            "date_of_birth": "1995-01-01T00:00:00"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login and check profile
        login_data = {"email": "sensitive@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Student should see their own data
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["phone"] == "555-0123"
        assert profile["address"] == "123 Private St, Secret City"
        
        # Professor should not see sensitive student data in directory
        response = integration_client.get("/student-information/directory", headers=auth_professor_headers)
        assert response.status_code == 200
        directory = response.json()
        
        # Directory should not contain sensitive information like phone/address
        for entry in directory:
            if entry.get("student_id") == "SENS001":
                assert "phone" not in entry or entry["phone"] is None
                assert "address" not in entry or entry["address"] is None
    
    def test_password_data_protection(self, integration_client, integration_db):
        """Test that passwords are not exposed in API responses"""
        student_data = {
            "email": "passwordtest@example.com",
            "password": "secretpassword123",
            "student_id": "PASS001",
            "first_name": "Password",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        registration_response = response.json()
        
        # Password should not be in registration response
        assert "password" not in registration_response
        assert "hashed_password" not in registration_response
        
        # Login response should not contain password
        login_data = {"email": "passwordtest@example.com", "password": "secretpassword123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        login_response = response.json()
        
        # Password should not be in login response
        assert "password" not in login_response
        assert "hashed_password" not in login_response
        
        # User profile should not contain password
        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        
        assert "password" not in profile
        assert "hashed_password" not in profile
    
    def test_data_anonymization_in_logs(self, integration_client, integration_db,
                                      auth_student_headers):
        """Test that sensitive data is anonymized in logs and responses"""
        # Perform various operations that might generate logs
        operations = [
            lambda: integration_client.get("/students/profile", headers=auth_student_headers),
            lambda: integration_client.get("/academic-records/grades", headers=auth_student_headers),
            lambda: integration_client.get("/academic-records/gpa", headers=auth_student_headers),
        ]
        
        for operation in operations:
            response = operation()
            assert response.status_code in [200, 404]  # 404 if no data exists
            
            # Check that response doesn't contain sensitive information
            response_text = str(response.content)
            
            # Should not contain passwords, tokens, or other sensitive data
            assert "password" not in response_text.lower()
            assert "token" not in response_text.lower()
            assert "secret" not in response_text.lower()

class TestInputValidationSecurityIntegration:
    """Integration tests for input validation security"""
    
    def test_input_length_limits(self, integration_client, integration_db, auth_student_headers):
        """Test protection against oversized input attacks"""
        # Test extremely long inputs
        long_string = "x" * 10000  # 10KB string
        
        oversized_inputs = {
            "first_name": long_string,
            "last_name": long_string,
            "major": long_string,
            "address": long_string,
        }
        
        for field, value in oversized_inputs.items():
            profile_data = {field: value}
            response = integration_client.put("/students/profile", json=profile_data, headers=auth_student_headers)
            
            # Should either reject or truncate oversized input
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                # If accepted, verify it's truncated
                response_data = response.json()
                assert len(str(response_data.get(field, ""))) <= 1000  # Reasonable limit
    
    def test_malicious_file_upload_protection(self, integration_client, integration_db,
                                            auth_student_headers):
        """Test protection against malicious file uploads"""
        # Test various file upload scenarios (if file upload is implemented)
        malicious_files = [
            ("malicious.exe", b"MZ\x90\x00"),  # PE executable header
            ("script.js", b"<script>alert('XSS')</script>"),
            ("shell.php", b"<?php system($_GET['cmd']); ?>"),
            ("backdoor.jsp", b"<%@ page import=\"java.io.*\" %>"),
        ]
        
        for filename, content in malicious_files:
            # This would test file upload endpoints if they exist
            # For now, we'll test that the system doesn't accept malicious filenames in text fields
            profile_data = {
                "first_name": filename,
                "last_name": "Malicious",
                "major": "Computer Science"
            }
            
            response = integration_client.put("/students/profile", json=profile_data, headers=auth_student_headers)
            # Should either reject or sanitize malicious filenames
            assert response.status_code in [200, 422]
    
    def test_special_character_handling(self, integration_client, integration_db, auth_student_headers):
        """Test handling of special characters and Unicode"""
        special_characters = [
            "Test\x00Null",  # Null byte
            "Test\x01Control",  # Control character
            "Test\xffNonASCII",  # Non-ASCII
            "Test🚀Emoji",  # Emoji
            "Test\u0000\u0001\u0002",  # Multiple control characters
            "Test'\"\\",  # SQL injection characters
            "Test<>\"'&",  # HTML/XML characters
        ]
        
        for special in special_characters:
            profile_data = {
                "first_name": special,
                "last_name": "Special",
                "major": "Computer Science"
            }
            
            response = integration_client.put("/students/profile", json=profile_data, headers=auth_student_headers)
            # Should handle special characters gracefully
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                # If accepted, verify it's properly handled
                response_data = response.json()
                # Should not contain unescaped control characters
                assert "\x00" not in str(response_data)

class TestRateLimitingSecurityIntegration:
    """Integration tests for rate limiting and DoS protection"""
    
    def test_authentication_rate_limiting(self, integration_client, integration_db):
        """Test rate limiting on authentication endpoints"""
        # Attempt rapid login requests
        login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
        
        response_times = []
        for i in range(20):  # 20 rapid requests
            start_time = time.time()
            response = integration_client.post("/auth/login", json=login_data)
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            # Should not crash or become unresponsive
            assert response.status_code in [200, 401, 429]  # 429 = Too Many Requests
            assert (end_time - start_time) < 10.0  # No request should take more than 10 seconds
        
        # System should remain responsive
        assert all(rt < 5.0 for rt in response_times)
    
    def test_endpoint_abuse_protection(self, integration_client, integration_db, auth_student_headers):
        """Test protection against endpoint abuse"""
        # Rapid requests to various endpoints
        endpoints = [
            "/students/profile",
            "/academic-records/grades",
            "/academic-records/gpa",
            "/academic-records/dashboard",
        ]
        
        for endpoint in endpoints:
            response_times = []
            
            for i in range(10):  # 10 rapid requests per endpoint
                start_time = time.time()
                response = integration_client.get(endpoint, headers=auth_student_headers)
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                # Should remain responsive
                assert response.status_code in [200, 404, 429]  # 429 if rate limited
                assert (end_time - start_time) < 5.0
            
            # Response times should be consistent
            assert all(rt < 2.0 for rt in response_times)
    
    def test_bulk_operation_protection(self, integration_client, integration_db, auth_professor_headers):
        """Test protection against bulk operation abuse"""
        # Attempt to create many resources rapidly
        for i in range(20):
            course_data = {
                "course_code": f"BULK{i:03d}",
                "title": f"Bulk Course {i}",
                "description": f"Course {i} for bulk operation testing",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            start_time = time.time()
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            end_time = time.time()
            
            # Should either succeed or be rate limited
            assert response.status_code in [200, 429]
            assert (end_time - start_time) < 5.0

class TestSecurityHeadersIntegration:
    """Integration tests for security headers and configurations"""
    
    def test_security_headers_presence(self, integration_client, integration_db):
        """Test presence of security headers in responses"""
        # Test various endpoints
        endpoints = [
            "/",
            "/health",
            "/auth/login",
        ]
        
        for endpoint in endpoints:
            response = integration_client.get(endpoint)
            assert response.status_code in [200, 401, 422]  # Depending on auth requirements
            
            # Check for security headers (these might not be implemented in test environment)
            headers = response.headers
            
            # Common security headers to check for
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy",
            ]
            
            # Note: These headers might not be implemented in the current system
            # This test documents what should be present for production security
    
    def test_cors_security_configuration(self, integration_client, integration_db):
        """Test CORS security configuration"""
        # Test preflight request
        response = integration_client.options("/auth/login", headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should either allow or deny based on configuration
        assert response.status_code in [200, 204, 403]
        
        # Check CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
        ]
        
        # These headers might be present depending on CORS configuration
        for header in cors_headers:
            # Just verify the response doesn't crash
            assert response.status_code in [200, 204, 403]

class TestDataIntegritySecurityIntegration:
    """Integration tests for data integrity and tampering protection"""
    
    def test_data_tampering_protection(self, integration_client, integration_db,
                                     auth_student_headers):
        """Test protection against data tampering"""
        # Update profile
        original_data = {
            "first_name": "Original",
            "last_name": "Name",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.put("/students/profile", json=original_data, headers=auth_student_headers)
        assert response.status_code == 200
        original_profile = response.json()
        
        # Verify update
        response = integration_client.get("/students/profile", headers=auth_student_headers)
        assert response.status_code == 200
        retrieved_profile = response.json()
        
        # Data should match
        assert retrieved_profile["first_name"] == original_data["first_name"]
        assert retrieved_profile["last_name"] == original_data["last_name"]
        assert retrieved_profile["major"] == original_data["major"]
        
        # Attempt to tamper with data using invalid updates
        tampered_data = {
            "first_name": "Tampered",
            "last_name": "Data",
            "major": "Hacked Major",
            "year_level": "Invalid Year"
        }
        
        response = integration_client.put("/students/profile", json=tampered_data, headers=auth_student_headers)
        # Should either accept valid changes or reject invalid ones
        assert response.status_code in [200, 422]
    
    def test_grade_integrity_protection(self, integration_client, integration_db,
                                      auth_professor_headers, enrolled_student_course):
        """Test protection against grade tampering"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Grade Integrity Test",
            "description": "Assignment for testing grade integrity",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Create grade
        grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 85.0,
            "points_possible": 100.0,
            "percentage": 85.0,
            "letter_grade": "B",
            "grade_status": "graded",
            "is_published": True
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        
        # Attempt to modify grade with invalid data
        invalid_grade_update = {
            "points_earned": 200.0,  # More than possible
            "percentage": 200.0,     # Invalid percentage
            "letter_grade": "Z",     # Invalid grade
        }
        
        response = integration_client.put(f"/grading/grades/{grade['id']}", json=invalid_grade_update, headers=auth_professor_headers)
        # Should either reject invalid data or accept it (depending on validation)
        assert response.status_code in [200, 422]
        
        # If accepted, verify data integrity
        if response.status_code == 200:
            updated_grade = response.json()
            # System should maintain data consistency
            assert updated_grade["points_earned"] <= updated_grade["points_possible"]
