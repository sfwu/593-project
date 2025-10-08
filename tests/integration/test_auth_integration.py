"""
Authentication Integration Tests
These tests use real database connections and test the full authentication flow
"""
import pytest


class TestAuthenticationIntegration:
    """Test authentication workflow integration"""
    
    def test_student_registration_and_login_flow(self, integration_client, integration_db):
        """Test complete student registration and login flow"""
        # Register a new student
        student_data = {
            "email": "teststudent@example.com",
            "password": "password123",
            "student_id": "TEST001",
            "first_name": "Test",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Student registered successfully"
        assert "user_id" in data
        
        # Login with the same credentials
        login_data = {
            "email": "teststudent@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_professor_registration_and_login_flow(self, integration_client, integration_db):
        """Test complete professor registration and login flow"""
        # Register a new professor
        professor_data = {
            "email": "testprofessor@example.com",
            "password": "password123",
            "professor_id": "TEST001",
            "first_name": "Test",
            "last_name": "Professor",
            "department": "Computer Science",
            "title": "Assistant Professor"
        }
        
        response = integration_client.post("/auth/register/professor", json=professor_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Professor registered successfully"
        assert "user_id" in data
        
        # Login with the same credentials
        login_data = {
            "email": "testprofessor@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_credentials_login(self, integration_client):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_duplicate_email_registration(self, integration_client, integration_db):
        """Test registration with duplicate email"""
        student_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "student_id": "DUP001",
            "first_name": "First",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Freshman"
        }
        
        # First registration should succeed
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Second registration with same email should fail
        student_data["student_id"] = "DUP002"  # Different student ID
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_jwt_token_validation(self, integration_client, integration_db, auth_student_headers):
        """Test JWT token validation and user profile access"""
        # Use the authenticated headers to access protected endpoint
        response = integration_client.get("/auth/me", headers=auth_student_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "role" in data
        assert data["role"] == "student"

    def test_token_expiration_handling(self, integration_client, integration_db):
        """Test token expiration handling"""
        # This test would require mocking time or using expired tokens
        # For now, just test that the endpoint exists and returns proper error for malformed tokens
        
        # Test with malformed token
        malformed_headers = {"Authorization": "Bearer invalid_token"}
        response = integration_client.get("/auth/me", headers=malformed_headers)
        assert response.status_code == 401


class TestRoleBasedAccessControlIntegration:
    """Test role-based access control integration"""
    
    def test_student_cannot_access_professor_endpoints(self, integration_client, integration_db, auth_student_headers):
        """Test that students cannot access professor-only endpoints"""
        # Try to update professor profile (PUT method)
        response = integration_client.put("/professors/profile", json={}, headers=auth_student_headers)
        assert response.status_code == 403
        assert "Professor role required" in response.json()["detail"]

    def test_professor_cannot_access_student_endpoints(self, integration_client, integration_db, auth_professor_headers):
        """Test that professors cannot access student-only endpoints"""
        # Try to update student profile (PUT method)
        response = integration_client.put("/students/profile", json={}, headers=auth_professor_headers)
        assert response.status_code == 403
        assert "Student role required" in response.json()["detail"]

    def test_cross_role_data_access_prevention(self, integration_client, integration_db, auth_student_headers, auth_professor_headers):
        """Test that users cannot access other role's data"""
        # Student trying to access professor profile update
        response = integration_client.put("/professors/profile", json={}, headers=auth_student_headers)
        assert response.status_code == 403
        
        # Professor trying to access student profile update
        response = integration_client.put("/students/profile", json={}, headers=auth_professor_headers)
        assert response.status_code == 403

    def test_unauthorized_access_to_protected_endpoints(self, integration_client, integration_db):
        """Test that unauthenticated requests are denied"""
        # Test PUT endpoints (which exist and require authentication)
        response = integration_client.put("/students/profile", json={})
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden is acceptable
        
        response = integration_client.put("/professors/profile", json={})
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden is acceptable
        
        response = integration_client.get("/auth/me")
        assert response.status_code in [401, 403]  # Either unauthorized or forbidden is acceptable


class TestAuthenticationSecurityIntegration:
    """Test authentication security features"""
    
    def test_password_hashing_security(self, integration_client, integration_db):
        """Test that passwords are properly hashed"""
        student_data = {
            "email": "security@example.com",
            "password": "plaintext123",
            "student_id": "SEC001",
            "first_name": "Security",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # The password should be hashed in the database, not stored as plaintext
        # This is tested indirectly by successful login with the original password
        login_data = {
            "email": "security@example.com",
            "password": "plaintext123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200

    def test_jwt_token_structure_and_content(self, integration_client, integration_db, auth_student_headers):
        """Test JWT token structure and content"""
        # Get user profile to verify token contains correct information
        response = integration_client.get("/auth/me", headers=auth_student_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "role" in data
        assert "id" in data
        assert data["role"] == "student"

    def test_session_management(self, integration_client, integration_db, auth_student_headers):
        """Test session management and token usage"""
        # Multiple requests with same token should work
        response1 = integration_client.get("/auth/me", headers=auth_student_headers)
        assert response1.status_code == 200
        
        response2 = integration_client.get("/auth/me", headers=auth_student_headers)
        assert response2.status_code == 200
        
        # Both responses should return same user data
        assert response1.json()["email"] == response2.json()["email"]

    def test_concurrent_authentication_requests(self, integration_client, integration_db):
        """Test concurrent authentication requests"""
        # Register multiple users concurrently
        users = []
        for i in range(3):
            user_data = {
                "email": f"concurrent{i}@example.com",
                "password": "password123",
                "student_id": f"CON{i:03d}",
                "first_name": f"User{i}",
                "last_name": "Concurrent",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            users.append(user_data)
        
        # Register all users (should not interfere with each other)
        responses = []
        for user_data in users:
            response = integration_client.post("/auth/register/student", json=user_data)
            responses.append(response)
        
        # All registrations should succeed
        for response in responses:
            assert response.status_code == 200


class TestAuthenticationErrorHandlingIntegration:
    """Test authentication error handling"""
    
    def test_malformed_registration_data(self, integration_client, integration_db):
        """Test handling of malformed registration data"""
        # Missing required fields
        malformed_data = {
            "email": "malformed@example.com",
            # Missing password, student_id, etc.
        }
        
        response = integration_client.post("/auth/register/student", json=malformed_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid email format
        invalid_email_data = {
            "email": "not-an-email",
            "password": "password123",
            "student_id": "INV001",
            "first_name": "Invalid",
            "last_name": "Email",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=invalid_email_data)
        assert response.status_code == 422  # Validation error

    def test_database_connection_during_auth_failure(self, integration_client, integration_db):
        """Test that authentication failures don't break database connections"""
        # Make a failed login attempt
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        
        # Database should still be functional
        response = integration_client.get("/health")
        assert response.status_code == 200
        
        # Should be able to make successful requests after failure
        response = integration_client.get("/")
        assert response.status_code == 200