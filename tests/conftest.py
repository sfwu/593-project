"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), '../backend')
sys.path.insert(0, backend_path)

from config.database import Base, get_db
from main import app

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["DB_NAME"] = "test_academic_management.db"
    yield
    # Cleanup after all tests
    test_db_files = [
        "test_academic_management.db",
        "test_crud.db",
        "academic_management.db",
        "data/test_academic_management.db"
    ]
    for db_file in test_db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except OSError:
                pass  # File might be in use

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    # Create test engine with in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    """Mock database session for pure unit tests"""
    return Mock()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "student"
    }

@pytest.fixture
def sample_student_data():
    """Sample student data for testing"""
    return {
        "email": "student@example.com",
        "password": "password123",
        "student_id": "STU001",
        "first_name": "John",
        "last_name": "Doe",
        "major": "Computer Science",
        "year_level": "Junior"
    }

@pytest.fixture
def sample_professor_data():
    """Sample professor data for testing"""
    return {
        "email": "professor@example.com",
        "password": "password123",
        "professor_id": "PROF001",
        "first_name": "Jane",
        "last_name": "Smith",
        "department": "Computer Science",
        "title": "Associate Professor"
    }

@pytest.fixture
def sample_course_data():
    """Sample course data for testing"""
    return {
        "course_code": "CS101",
        "title": "Introduction to Computer Science",
        "description": "Basic programming concepts",
        "credits": 3,
        "department": "Computer Science",
        "semester": "Fall 2024",
        "year": 2024,
        "max_enrollment": 30
    }

# Integration test fixtures
@pytest.fixture(scope="function")
def integration_db():
    """Create a test database for integration testing"""
    # Create test engine with file-based SQLite database
    engine = create_engine("sqlite:///./data/test_integration.db", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def integration_client(integration_db):
    """Create a test client for integration testing"""
    return TestClient(app)

@pytest.fixture
def auth_student_headers(integration_client, integration_db):
    """Create authentication headers for a student user"""
    # Register a student first
    student_data = {
        "email": "student@example.com",
        "password": "password123",
        "student_id": "STU001",
        "first_name": "John",
        "last_name": "Doe",
        "major": "Computer Science",
        "year_level": "Junior"
    }
    
    # Register student
    response = integration_client.post("/auth/register/student", json=student_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {
        "email": "student@example.com",
        "password": "password123"
    }
    response = integration_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_professor_headers(integration_client, integration_db):
    """Create authentication headers for a professor user"""
    # Register a professor first
    professor_data = {
        "email": "professor@example.com",
        "password": "password123",
        "professor_id": "PROF001",
        "first_name": "Jane",
        "last_name": "Smith",
        "department": "Computer Science",
        "title": "Associate Professor"
    }
    
    # Register professor
    response = integration_client.post("/auth/register/professor", json=professor_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {
        "email": "professor@example.com",
        "password": "password123"
    }
    response = integration_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Additional fixtures for complex integration tests
@pytest.fixture
def sample_course_with_professor(integration_client, integration_db, auth_professor_headers):
    """Create a sample course with professor for testing"""
    # Create a course
    course_data = {
        "course_code": "TEST101",
        "title": "Test Course",
        "description": "A test course for integration testing",
        "credits": 3,
        "department": "Computer Science",
        "semester": "Fall 2024",
        "year": 2024,
        "max_enrollment": 30
    }
    
    response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
    if response.status_code == 200:
        return response.json()
    return None

@pytest.fixture
def enrolled_student_course(integration_client, integration_db, auth_student_headers, sample_course_with_professor):
    """Create a student enrolled in a course"""
    if not sample_course_with_professor:
        return None
    
    # Enroll student in the course
    course_id = sample_course_with_professor["id"]
    response = integration_client.post(f"/students/courses/{course_id}/enroll", headers=auth_student_headers)
    if response.status_code == 200:
        return {
            "course": sample_course_with_professor,
            "enrollment": response.json()
        }
    return None

@pytest.fixture
def sample_grading_data(integration_client, integration_db, auth_professor_headers, sample_course_with_professor):
    """Create sample grading data for testing"""
    if not sample_course_with_professor:
        return None
    
    # Create an assignment
    assignment_data = {
        "title": "Test Assignment",
        "description": "A test assignment",
        "assignment_type": "homework",
        "max_points": 100,
        "due_date": "2024-12-31T23:59:59"
    }
    
    response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
    if response.status_code == 200:
        return {
            "course": sample_course_with_professor,
            "assignment": response.json()
        }
    return None
