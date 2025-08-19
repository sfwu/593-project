"""
Integration Tests for FastAPI endpoints
These tests use real database connections and test the full API stack
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from main import app, get_db
from database import Base
import models

# Create test database in data/ directory
import os
os.makedirs("data", exist_ok=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test_api_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    """Setup test database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestAPIEndpointsIntegration:
    """Integration test class for API endpoints - testing full stack"""
    
    def test_root_endpoint(self, setup_database):
        """Test root endpoint returns hello world message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Hello World" in data["message"]
        assert "Academic Information Management System" in data["message"]
    
    def test_health_check(self, setup_database):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "academic-management-api" in data["service"]
    
    def test_create_student_success(self, setup_database):
        """Test successful student creation through API"""
        student_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "student_id": "S12345"
        }
        response = client.post("/students/", json=student_data)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["student_id"] == "S12345"
        assert data["id"] is not None
    

    
    def test_get_students_empty(self, setup_database):
        """Test getting students when none exist"""
        response = client.get("/students/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_students_with_data(self, setup_database):
        """Test getting students when data exists"""
        # Create a student first
        student_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "student_id": "S12347"
        }
        client.post("/students/", json=student_data)
        
        response = client.get("/students/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Jane"
    
    def test_get_student_by_id_success(self, setup_database):
        """Test getting student by ID - success case"""
        # Create a student first
        student_data = {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "student_id": "S12348",
            "major": "Physics",
            "gpa": 3.7
        }
        create_response = client.post("/students/", json=student_data)
        student_id = create_response.json()["id"]
        
        response = client.get(f"/students/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Bob"
        assert data["id"] == student_id
    
    def test_get_student_by_id_not_found(self, setup_database):
        """Test getting student by ID - not found case"""
        response = client.get("/students/999")
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]
    
    def test_update_student_success(self, setup_database):
        """Test updating student - success case"""
        # Create a student first
        student_data = {
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice.brown@example.com",
            "student_id": "S12349",
            "major": "Chemistry",
            "gpa": 3.6
        }
        create_response = client.post("/students/", json=student_data)
        student_id = create_response.json()["id"]
        
        # Update the student
        updated_data = {
            "first_name": "Alice",
            "last_name": "Brown-Smith",
            "email": "alice.brown.smith@example.com",
            "student_id": "S12349",
            "major": "Biochemistry",
            "gpa": 3.8
        }
        response = client.put(f"/students/{student_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["last_name"] == "Brown-Smith"
        assert data["major"] == "Biochemistry"
        assert data["gpa"] == 3.8
        assert data["updated_at"] is not None
    
    def test_update_student_not_found(self, setup_database):
        """Test updating student - not found case"""
        updated_data = {
            "first_name": "NonExistent",
            "last_name": "Student",
            "email": "nonexistent@example.com",
            "student_id": "S99999",
            "major": "Unknown",
            "gpa": 0.0
        }
        response = client.put("/students/999", json=updated_data)
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]
    
    def test_delete_student_success(self, setup_database):
        """Test deleting student - success case"""
        # Create a student first
        student_data = {
            "first_name": "Charlie",
            "last_name": "Wilson",
            "email": "charlie.wilson@example.com",
            "student_id": "S12350",
            "major": "Engineering",
            "gpa": 3.5
        }
        create_response = client.post("/students/", json=student_data)
        student_id = create_response.json()["id"]
        
        # Delete the student
        response = client.delete(f"/students/{student_id}")
        assert response.status_code == 200
        assert "Student deleted successfully" in response.json()["message"]
        
        # Verify student is deleted
        get_response = client.get(f"/students/{student_id}")
        assert get_response.status_code == 404
    
    def test_delete_student_not_found(self, setup_database):
        """Test deleting student - not found case"""
        response = client.delete("/students/999")
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]

class TestAPIInputValidationIntegration:
    """Integration test class for input validation through API"""
    
    def test_create_student_missing_required_fields(self, setup_database):
        """Test creating student with missing required fields"""
        # Missing first_name
        student_data = {
            "last_name": "Doe",
            "email": "incomplete@example.com",
            "student_id": "S99999"
        }
        response = client.post("/students/", json=student_data)
        assert response.status_code == 422  # Validation error
        
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "first_name"] for error in errors)
    
    def test_create_student_invalid_gpa(self, setup_database):
        """Test creating student with invalid GPA"""
        student_data = {
            "first_name": "Test",
            "last_name": "Student",
            "email": "test@example.com",
            "student_id": "S99999",
            "gpa": "invalid_gpa"  # Should be a number
        }
        response = client.post("/students/", json=student_data)
        assert response.status_code == 422  # Validation error

class TestAPIWorkflowIntegration:
    """Integration test class for complete workflows"""
    
    def test_complete_student_lifecycle(self, setup_database):
        """Test complete student CRUD lifecycle through API"""
        # 1. Create student
        student_data = {
            "first_name": "Lifecycle",
            "last_name": "Test",
            "email": "lifecycle@example.com",
            "student_id": "LIFE001",
            "major": "Testing",
            "gpa": 3.0
        }
        create_response = client.post("/students/", json=student_data)
        assert create_response.status_code == 200
        student_id = create_response.json()["id"]
        
        # 2. Read student
        read_response = client.get(f"/students/{student_id}")
        assert read_response.status_code == 200
        read_data = read_response.json()
        assert read_data["first_name"] == "Lifecycle"
        
        # 3. Update student
        updated_data = {
            "first_name": "Updated",
            "last_name": "Test",
            "email": "updated.lifecycle@example.com",
            "student_id": "LIFE001",
            "major": "Advanced Testing",
            "gpa": 3.5
        }
        update_response = client.put(f"/students/{student_id}", json=updated_data)
        assert update_response.status_code == 200
        assert update_response.json()["first_name"] == "Updated"
        
        # 4. Verify update
        verify_response = client.get(f"/students/{student_id}")
        assert verify_response.status_code == 200
        assert verify_response.json()["first_name"] == "Updated"
        assert verify_response.json()["gpa"] == 3.5
        
        # 5. Delete student
        delete_response = client.delete(f"/students/{student_id}")
        assert delete_response.status_code == 200
        
        # 6. Verify deletion
        final_response = client.get(f"/students/{student_id}")
        assert final_response.status_code == 404
    
    def test_pagination_workflow(self, setup_database):
        """Test pagination workflow with multiple students"""
        # Create multiple students
        students = []
        for i in range(5):
            student_data = {
                "first_name": f"Student{i}",
                "last_name": "Test",
                "email": f"student{i}@example.com",
                "student_id": f"S{i:03d}",
                "major": "Testing",
                "gpa": 3.0 + (i * 0.1)
            }
            response = client.post("/students/", json=student_data)
            assert response.status_code == 200
            students.append(response.json())
        
        # Test pagination
        page1_response = client.get("/students/?skip=0&limit=2")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data) == 2
        
        page2_response = client.get("/students/?skip=2&limit=2")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert len(page2_data) == 2
        
        # Verify no overlap
        page1_ids = {student["id"] for student in page1_data}
        page2_ids = {student["id"] for student in page2_data}
        assert len(page1_ids.intersection(page2_ids)) == 0

if __name__ == "__main__":
    pytest.main([__file__])
