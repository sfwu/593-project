# Testing Guide: Unit Tests vs Integration Tests

This guide explains the testing strategy used in the Academic Information Management System, with a focus on **Unit Tests** and **Integration Tests**.

## 🧪 Testing Philosophy

For a software testing course, it's crucial to understand different types of tests and when to use them. Our project demonstrates both **Unit Testing** and **Integration Testing** approaches.

## 📁 Test Organization

```
tests/
├── unit/                           # Unit Tests (Fast, Isolated)
│   ├── test_schemas.py            # Schema validation tests
│   └── test_crud_unit.py          # CRUD logic tests with mocks
├── integration/                    # Integration Tests (Real environment)
│   ├── test_api_integration.py    # Full API stack tests
│   └── test_crud_integration.py   # Database persistence tests
├── conftest.py                    # Shared test configuration
└── TEST_GUIDE.md                  # This guide
```

## 🔬 Unit Tests

**Definition**: Unit tests verify individual components in isolation, without external dependencies.

### Characteristics:
- ⚡ **Fast**: Run in milliseconds
- 🔒 **Isolated**: No database, network, or file system
- 🎭 **Mocked**: Use mocks/stubs for external dependencies
- 🎯 **Focused**: Test single functions/methods
- 🔄 **Repeatable**: Same result every time

### Examples in our project:

#### 1. Schema Validation Tests (`tests/unit/test_schemas.py`)
```python
def test_student_create_valid(self):
    """Test creating valid StudentCreate schema"""
    student_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "student_id": "S12345"
    }
    
    student = schemas.StudentCreate(**student_data)
    assert student.first_name == "John"
```

**Why this is a unit test:**
- Tests only Pydantic schema validation
- No database or external dependencies
- Fast and isolated

#### 2. CRUD Logic Tests (`tests/unit/test_crud_unit.py`)
```python
@patch('crud.models.Student')
def test_create_student_success(self, mock_student_model):
    """Test creating a student - mocked database and model"""
    mock_db = Mock()
    mock_student_instance = Mock()
    mock_student_model.return_value = mock_student_instance
    
    result = crud.create_student(mock_db, student_data)
    
    mock_student_model.assert_called_once()
    mock_db.add.assert_called_once()
```

**Why this is a unit test:**
- Uses mocks for database (`Mock()`)
- Tests CRUD function logic in isolation
- No real database connection
- Verifies function calls and behavior

### Running Unit Tests:
```bash
python run_tests.py --type unit
# OR
pytest tests/unit/ -v
```

## 🔗 Integration Tests

**Definition**: Integration tests verify that different components work together correctly in a real environment.

### Characteristics:
- 🐌 **Slower**: Involve real database/network operations
- 🌍 **Real Environment**: Use actual databases, APIs
- 🔄 **End-to-End**: Test complete workflows
- 🎯 **Component Interaction**: Verify components work together
- 📊 **Data Persistence**: Test actual data storage/retrieval

### Examples in our project:

#### 1. API Integration Tests (`tests/integration/test_api_integration.py`)
```python
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
```

**Why this is an integration test:**
- Uses real FastAPI test client
- Real database connection
- Tests complete API request/response cycle
- Verifies data persistence

#### 2. Database Integration Tests (`tests/integration/test_crud_integration.py`)
```python
def test_create_student_integration(self, test_db):
    """Test creating a student with real database persistence"""
    created_student = crud.create_student(test_db, student_data)
    
    # Verify data persisted in database
    db_student = test_db.query(models.Student).filter(
        models.Student.id == created_student.id
    ).first()
    assert db_student is not None
```

**Why this is an integration test:**
- Uses real SQLite database
- Tests actual data persistence
- Verifies database constraints
- Tests complete CRUD workflow

### Running Integration Tests:
```bash
python run_tests.py --type integration
# OR
pytest tests/integration/ -v
```

## 🏃‍♂️ Running Tests

### Run All Tests:
```bash
python run_tests.py
# OR
python run_tests.py --type all
```

### Run Specific Test Types:
```bash
# Unit tests only (fast)
python run_tests.py --type unit

# Integration tests only (slower but comprehensive)
python run_tests.py --type integration

# Skip linting
python run_tests.py --no-lint
```

### Direct pytest commands:
```bash
# All tests with coverage
pytest tests/ -v --cov=backend --cov-report=term-missing

# Only unit tests
pytest tests/unit/ -v

# Only integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_schemas.py -v

# Specific test function
pytest tests/unit/test_schemas.py::TestStudentSchemas::test_student_create_valid -v
```

## 📊 Test Coverage and Quality

### What Each Test Type Covers:

**Unit Tests Cover:**
- ✅ Input validation logic
- ✅ Business logic correctness
- ✅ Error handling
- ✅ Edge cases
- ✅ Function behavior in isolation

**Integration Tests Cover:**
- ✅ Database operations
- ✅ API endpoint functionality
- ✅ Data persistence
- ✅ Component interaction
- ✅ End-to-end workflows
- ✅ Database constraints

### Test Metrics:
```bash
# Get detailed coverage report
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html to see detailed coverage
```

## 🎯 Testing Best Practices Demonstrated

### 1. **Test Isolation**
- Each test is independent
- Database cleanup between tests
- No shared state between tests

### 2. **Arrange-Act-Assert Pattern**
```python
def test_example(self):
    # Arrange
    student_data = {"first_name": "John"}
    
    # Act
    result = create_student(student_data)
    
    # Assert
    assert result.first_name == "John"
```

### 3. **Descriptive Test Names**
- `test_create_student_success` (what it tests)
- `test_create_student_duplicate_email` (specific scenario)
- `test_get_student_not_found` (edge case)

### 4. **Test Categories**
- **Happy Path**: Normal, expected behavior
- **Edge Cases**: Boundary conditions
- **Error Cases**: Invalid inputs, failures
- **Integration**: Component interaction

### 5. **Mock Usage in Unit Tests**
```python
# Mock external dependencies
@patch('crud.models.Student')
def test_with_mock(self, mock_model):
    # Test logic without real database
    pass
```

### 6. **Fixtures for Setup/Teardown**
```python
@pytest.fixture(scope="function")
def setup_database():
    """Setup test database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

## 🎓 Learning Objectives for Software Testing Course

This test structure demonstrates:

1. **Test Types**: Unit vs Integration testing
2. **Test Organization**: Logical separation of test types
3. **Mocking**: Using mocks to isolate units
4. **Test Fixtures**: Setup and teardown patterns
5. **Database Testing**: Isolated test databases
6. **API Testing**: HTTP endpoint testing
7. **Coverage**: Measuring test effectiveness
8. **TDD/BDD**: Test-first development approach
9. **CI/CD Ready**: Automated test execution
10. **Real-world Practices**: Professional testing patterns

## 🔧 Troubleshooting Tests

### Common Issues:

1. **Database lock errors**:
   ```bash
   # Clean up test databases
   rm -f *.db
   ```

2. **Import errors**:
   ```bash
   # Ensure you're in the project root
   cd /path/to/593-project
   python -m pytest tests/
   ```

3. **Mock not working**:
   ```python
   # Correct path for mocking
   @patch('crud.models.Student')  # Patch where it's used
   ```

4. **Test database not cleaned**:
   - Each test should use `setup_database` fixture
   - Check fixture scope (`function` vs `session`)

## 📚 Further Reading

- **Unit Testing**: Tests individual components in isolation
- **Integration Testing**: Tests component interactions
- **End-to-End Testing**: Tests complete user workflows
- **Test-Driven Development (TDD)**: Write tests first
- **Behavior-Driven Development (BDD)**: Tests based on behavior
- **Continuous Integration**: Automated testing in CI/CD

This testing structure provides a solid foundation for understanding and practicing different testing methodologies in your software testing course!
