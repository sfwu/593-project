# Unit Tests Guide - Academic Information Management System

## Overview

This comprehensive unit test suite covers all the major components of the Academic Information Management System backend. The tests are designed to validate functionality, security, and reliability across all layers of the application.

## Test Structure

```
tests/
├── conftest.py                    # Test configuration and fixtures
├── unit/
│   ├── test_auth.py              # Authentication system tests
│   ├── test_models.py            # Database model tests
│   ├── test_schemas.py           # Pydantic schema validation tests
│   ├── test_auth_controller.py   # Authentication endpoint tests
│   ├── test_student_controller.py # Student functionality tests
│   └── test_professor_controller.py # Professor functionality tests
└── UNIT_TESTS_GUIDE.md          # This documentation
```

## Test Categories

### 🔐 Authentication System Tests (`test_auth.py`)

**Password Security:**
- Password hashing with bcrypt
- Password verification
- Unique salt generation
- Hash collision prevention

**JWT Token Management:**
- Token creation with correct payload
- Token expiration handling
- Token verification and validation
- Invalid token handling
- Missing data in token payload

**User Authentication:**
- Valid credential authentication
- Invalid email handling
- Invalid password handling
- User not found scenarios

**Role-Based Access Control:**
- Student role verification
- Professor role verification
- Permission denial for wrong roles
- Active user validation

### 🗄️ Database Model Tests (`test_models.py`)

**User Model:**
- Student and professor role creation
- Default value assignment
- Email and password storage
- User status management

**Student Model:**
- Required field validation
- Optional field handling
- Academic information storage
- Profile completeness

**Professor Model:**
- Academic profile creation
- Department assignment
- Office hours and contact info
- Specialization tracking

**Course Model:**
- Course creation with defaults
- Credit and enrollment limits
- Schedule and prerequisite handling
- Active/inactive status

**Model Relationships:**
- User-Student associations
- User-Professor associations
- Professor-Course assignments
- Student-Course enrollments

### 📋 Schema Validation Tests (`test_schemas.py`)

**Authentication Schemas:**
- User login validation
- Registration with role verification
- Token structure validation
- Password length requirements
- Email format validation

**Student Schemas:**
- Complete student registration
- Partial profile updates
- Required field enforcement
- Optional field handling

**Professor Schemas:**
- Professor registration validation
- Academic profile updates
- Department and title handling

**Course Schemas:**
- Course creation with defaults
- Update validation
- Credit and enrollment limits
- Schedule format validation

**Enrollment Schemas:**
- Enrollment request validation
- Response structure verification

### 🌐 API Controller Tests

#### Authentication Controller (`test_auth_controller.py`)

**Login Functionality:**
- Successful authentication
- Invalid credential handling
- Token generation and format
- Token expiration settings

**Student Registration:**
- Complete registration process
- Duplicate email prevention
- Duplicate student ID prevention
- Password hashing verification

**Professor Registration:**
- Academic account creation
- Duplicate professor ID prevention
- Profile data validation

**Profile Endpoints:**
- Current user retrieval
- Role-specific profile access
- Authentication requirement enforcement

#### Student Controller (`test_student_controller.py`)

**Profile Management:**
- Profile update functionality
- Partial field updates
- Password change verification
- Current password validation

**Course Search:**
- Filter-based searching
- Keyword search functionality
- Department and semester filtering
- Professor information inclusion

**Course Enrollment:**
- Successful enrollment process
- Duplicate enrollment prevention
- Course capacity validation
- Prerequisites checking
- Schedule conflict detection

**Schedule Management:**
- Personal schedule retrieval
- Semester/year filtering
- Credit calculation
- Conflict identification

**Course Withdrawal:**
- Successful withdrawal process
- Enrollment verification
- Timeframe validation

#### Professor Controller (`test_professor_controller.py`)

**Profile Management:**
- Academic profile updates
- Office hours management
- Specialization tracking
- Contact information updates

**Teaching Load:**
- Course assignment tracking
- Credit hour calculation
- Student count aggregation
- Department workload analysis

**Course Administration:**
- New course creation
- Duplicate course prevention
- Course information updates
- Course deactivation (soft delete)
- Enrolled student protection

**Enrollment Management:**
- Student roster viewing
- Enrollment statistics
- Student removal from courses
- Year-level distribution analysis

## Test Fixtures and Utilities

### Database Fixtures
- `test_db`: In-memory SQLite database for each test
- `mock_db_session`: Mock database session for pure unit tests

### Sample Data Fixtures
- `sample_user_data`: Standard user account data
- `sample_student_data`: Complete student profile data
- `sample_professor_data`: Academic profile data
- `sample_course_data`: Course information data

### Test Client
- `client`: FastAPI test client with database overrides

## Running the Tests

### Basic Test Execution
```bash
# Run all unit tests
python run_unit_tests.py

# Run with verbose output
python run_unit_tests.py --verbose

# Run specific module tests
python run_unit_tests.py --module auth
python run_unit_tests.py --module models
python run_unit_tests.py --module schemas
```

### Coverage Reports
```bash
# Generate coverage report
python run_unit_tests.py --coverage

# View HTML coverage report
open htmlcov/index.html
```

### Individual Test Files
```bash
# Run specific test file
pytest tests/unit/test_auth.py -v

# Run specific test class
pytest tests/unit/test_auth.py::TestPasswordHashing -v

# Run specific test method
pytest tests/unit/test_auth.py::TestPasswordHashing::test_password_hashing_and_verification -v
```

## Test Best Practices

### Unit Test Principles
1. **Isolation**: Each test is independent and doesn't rely on others
2. **Mocking**: External dependencies are mocked to focus on unit logic
3. **Coverage**: All code paths and edge cases are tested
4. **Clarity**: Test names clearly describe what is being tested

### Mocking Strategy
- Database sessions are mocked for pure unit tests
- Authentication dependencies are mocked in controller tests
- External API calls would be mocked (if any)
- File system operations are mocked

### Error Testing
- Invalid input validation
- Permission and authorization failures
- Database constraint violations
- Business rule enforcement

## Test Data Management

### Sample Data
All test fixtures provide realistic but non-sensitive sample data:
- Email addresses use `example.com` domain
- Student/Professor IDs follow standard formats
- Passwords meet security requirements
- Course codes follow academic conventions

### Database State
- Each test gets a fresh in-memory database
- No test data persists between test runs
- Database schemas are created automatically
- Cleanup is handled by pytest fixtures

## Error Scenarios Covered

### Authentication Errors
- Invalid credentials
- Expired tokens
- Malformed tokens
- Insufficient permissions
- Inactive user accounts

### Validation Errors
- Missing required fields
- Invalid email formats
- Password length violations
- Duplicate unique values
- Invalid enum values

### Business Logic Errors
- Course enrollment limits
- Schedule conflicts
- Prerequisite violations
- Permission boundaries
- State consistency

## Integration with CI/CD

The test suite is designed to work seamlessly with continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: |
    pip install -r requirements.txt
    python run_unit_tests.py --coverage
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

## Future Test Enhancements

### Potential Additions
1. **Property-based testing** with Hypothesis
2. **Performance testing** for database queries
3. **Security testing** for injection vulnerabilities
4. **API rate limiting** tests
5. **Concurrency testing** for race conditions

### Test Metrics Goals
- **Line Coverage**: > 95%
- **Branch Coverage**: > 90%
- **Function Coverage**: 100%
- **Test Execution Time**: < 30 seconds

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure backend path is in Python path
2. **Database Errors**: Check SQLAlchemy model imports
3. **Mock Failures**: Verify mock patch paths are correct
4. **Fixture Errors**: Check pytest fixture dependencies

### Debug Tips
- Use `pytest --pdb` to drop into debugger on failures
- Add `print()` statements in tests for debugging
- Use `pytest --capture=no` to see print output
- Check `conftest.py` for fixture configuration

This comprehensive test suite ensures the reliability, security, and maintainability of the Academic Information Management System backend.
