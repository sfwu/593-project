"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), '../backend')
sys.path.insert(0, backend_path)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    yield
    # Cleanup after all tests
    test_db_files = [
        "test_academic_management.db",
        "test_crud.db",
        "academic_management.db"
    ]
    for db_file in test_db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except OSError:
                pass  # File might be in use
