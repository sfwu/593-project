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
