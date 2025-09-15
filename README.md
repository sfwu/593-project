# Academic Information Management System

A **complete full-stack application** for academic course management with role-based authentication, featuring students and professors with comprehensive course administration capabilities.

## 🎯 Features

### 🔐 **Authentication & Security**
- JWT-based authentication with role-based access control
- Password hashing with bcrypt
- Student and Professor user types with different permissions

### 👨‍🎓 **Student Features**
- **Profile Management**: View and update personal information, change passwords
- **Course Search**: Browse courses by department, semester, year, or keywords
- **Course Registration**: Enroll in courses with capacity and prerequisite validation
- **Schedule Management**: View personal class schedule with conflict detection
- **Course Withdrawal**: Drop courses within allowed timeframes

### 👨‍🏫 **Professor Features**
- **Academic Profile**: Manage professional information, office hours, specialization
- **Course Administration**: Create, update, and manage course offerings
- **Enrollment Management**: View student rosters and enrollment statistics
- **Teaching Load**: Track assigned courses and calculate workload

## 🛠️ Tech Stack

- **Language**: Python 3.12
- **Frontend**: Streamlit (port 9700)
- **Backend**: FastAPI (port 9600) 
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with passlib/bcrypt
- **Testing**: pytest with 150+ unit tests
- **Validation**: Pydantic schemas

## 📁 Project Structure

```
593-project/
├── backend/                           # FastAPI backend
│   ├── config/                       # Configuration
│   │   ├── auth.py                   # JWT authentication system
│   │   ├── database.py               # Database configuration
│   │   └── settings.py               # Application settings
│   ├── models/                       # Database models (reorganized)
│   │   ├── user.py                   # User & UserRole models
│   │   ├── student.py                # Student model
│   │   ├── professor.py              # Professor model
│   │   └── course.py                 # Course & enrollment models
│   ├── schemas/                      # Pydantic schemas
│   │   └── student_schemas.py        # API request/response models
│   ├── controllers/                  # API endpoints
│   │   ├── auth_controller.py        # Authentication endpoints
│   │   ├── student_controller.py     # Student functionality
│   │   └── professor_controller.py   # Professor functionality
│   └── main.py                       # FastAPI app with all routes
├── frontend/
│   └── app.py                        # Streamlit web interface
├── tests/                            # Comprehensive test suite
│   ├── unit/                         # Unit tests (150+ tests)
│   │   ├── test_auth.py              # Authentication tests
│   │   ├── test_models.py            # Database model tests
│   │   ├── test_schemas.py           # Schema validation tests
│   │   ├── test_auth_controller.py   # Auth endpoint tests
│   │   ├── test_student_controller.py # Student endpoint tests
│   │   └── test_professor_controller.py # Professor endpoint tests
│   └── integration/                  # Integration tests
├── data/                             # SQLite database files
├── logs/                             # Application logs
├── run_unit_tests.py                 # Comprehensive test runner
├── BACKEND_API_GUIDE.md              # Complete API documentation
└── *.sh                              # Service management scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)

### Installation & Setup

```bash
# Clone and navigate to project
cd 593-project

# Activate virtual environment (if using)
python-c593  # or your venv activation command

# Install dependencies
pip install -r requirements.txt

# Start all services
./start.sh
```

### Service URLs
- **🌐 Frontend**: http://localhost:9700
- **📊 Backend API**: http://localhost:9600
- **📚 API Documentation**: http://localhost:9600/docs
- **🏥 Health Check**: http://localhost:9600/health

### Service Management

```bash
# Start services
./start.sh

# Check status
./status.sh

# Stop services
./stop.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🧪 Testing

### Comprehensive Test Suite
- **150+ unit tests** covering all functionality
- **23 model tests** for database integrity
- **21 schema tests** for validation
- **Authentication tests** for security
- **API endpoint tests** for all controllers

### Running Tests

```bash
# Run all unit tests
python run_unit_tests.py

# Run with verbose output
python run_unit_tests.py --verbose

# Run specific test modules
python run_unit_tests.py --module auth
python run_unit_tests.py --module models
python run_unit_tests.py --module schemas

# Generate coverage report
python run_unit_tests.py --coverage

# Individual test files
pytest tests/unit/test_auth.py -v
pytest tests/unit/test_models.py -v
```

## 📖 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login with JWT token
- `POST /auth/register/student` - Student registration
- `POST /auth/register/professor` - Professor registration
- `GET /auth/me` - Get current user profile

### Student Endpoints (`/students`)
- Profile management and password changes
- Course search with advanced filters
- Course enrollment and withdrawal
- Personal schedule with conflict detection

### Professor Endpoints (`/professors`)
- Academic profile and teaching load management
- Course creation and administration
- Student enrollment management
- Course statistics and analytics

**📚 Complete API Guide**: See [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md) for detailed documentation with examples.

## 🗄️ Database Schema

### Core Models
- **User**: Authentication with email, password, role
- **Student**: Academic profile with enrollment tracking
- **Professor**: Academic staff with course assignments
- **Course**: Course information with enrollment management
- **Enrollments**: Many-to-many student-course relationships

### Features
- **Role-based permissions** (Student/Professor)
- **Enrollment capacity** validation
- **Schedule conflict** detection
- **Course prerequisites** tracking
- **Academic progress** monitoring

## 🔧 Development

### Model Organization
Models are logically separated by responsibility:
- `models/user.py` - Authentication and roles
- `models/student.py` - Student-specific data
- `models/professor.py` - Professor-specific data  
- `models/course.py` - Course and enrollment data

### Testing Philosophy
- **Unit tests** with mocked dependencies for fast execution
- **Integration tests** with real database for end-to-end validation
- **Schema tests** for input validation
- **Security tests** for authentication and authorization

### Code Quality
- Comprehensive error handling
- Input validation with Pydantic
- SQL injection protection via ORM
- Professional logging and monitoring

## 📊 Project Status

### ✅ **Fully Implemented**
- **Authentication System**: JWT, password hashing, role-based access
- **User Management**: Student and professor registration/profiles
- **Course Management**: Full CRUD operations with enrollment
- **Database Layer**: Complete SQLAlchemy models with relationships
- **API Layer**: RESTful endpoints with proper HTTP status codes
- **Testing Suite**: 150+ comprehensive unit tests
- **Documentation**: Complete API guide and examples
- **Security**: Input validation, authentication, authorization

### 🎯 **Production Ready Features**
- Error handling and logging
- Database migrations support
- Environment-based configuration
- Service health monitoring
- Comprehensive test coverage
- Professional code structure

## 🎓 Educational Value

This project demonstrates:
- **Full-stack development** with modern Python frameworks
- **Authentication and authorization** best practices
- **Database design** with proper relationships
- **API development** with FastAPI and Pydantic
- **Test-driven development** with comprehensive test coverage
- **Clean architecture** with separation of concerns
- **Professional documentation** and code organization

Perfect for learning enterprise-level software development patterns! 🚀

## 📝 Additional Resources

- **API Documentation**: [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md)
- **Test Documentation**: [tests/UNIT_TESTS_GUIDE.md](tests/UNIT_TESTS_GUIDE.md)
- **Interactive API Docs**: http://localhost:9600/docs (when running)