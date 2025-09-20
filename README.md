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
- **Academic Records**: View transcripts, GPA calculations, and academic progress
- **Grade Tracking**: Access assignment grades, exam results, and gradebook information

### 👨‍🏫 **Professor Features**
- **Academic Profile**: Manage professional information, office hours, specialization
- **Course Administration**: Create, update, and manage course offerings
- **Enrollment Management**: View student rosters and enrollment statistics
- **Teaching Load**: Track assigned courses and calculate workload
- **Grading & Assessment**: Create assignments, schedule exams, manage gradebooks
- **Student Communication**: Send messages, track attendance, monitor performance

## 🛠️ Tech Stack

- **Language**: Python 3.12
- **Frontend**: Streamlit (port 9700)
- **Backend**: FastAPI (port 9600) 
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with passlib/bcrypt
- **Testing**: pytest with 200+ comprehensive unit tests
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
│   │   ├── course.py                 # Course & enrollment models
│   │   ├── academic_record.py        # Academic records & transcripts
│   │   ├── grading_assessment.py     # Assignments, exams, grades
│   │   └── student_information.py    # Attendance, messages, directory
│   ├── schemas/                      # Pydantic schemas
│   │   ├── student_schemas.py        # Core API request/response models
│   │   ├── academic_record_schemas.py # Academic record schemas
│   │   ├── grading_assessment_schemas.py # Grading & assessment schemas
│   │   └── student_information_schemas.py # Student info schemas
│   ├── controllers/                  # API endpoints
│   │   ├── auth_controller.py        # Authentication endpoints
│   │   ├── student_controller.py     # Student functionality
│   │   ├── professor_controller.py   # Professor functionality
│   │   ├── course_controller.py      # General course endpoints
│   │   ├── academic_record_controller.py # Academic record management
│   │   ├── grading_assessment_controller.py # Grading & assessment
│   │   └── student_information_controller.py # Student information
│   └── main.py                       # FastAPI app with all routes
├── frontend/
│   └── app.py                        # Streamlit web interface
├── tests/                            # Comprehensive test suite
│   ├── unit/                         # Unit tests (200+ tests, 100% passing)
│   │   ├── test_auth.py              # Authentication tests
│   │   ├── test_models.py            # Database model tests
│   │   ├── test_schemas.py           # Schema validation tests
│   │   ├── test_auth_controller.py   # Auth endpoint tests
│   │   ├── test_student_controller.py # Student endpoint tests
│   │   ├── test_professor_controller.py # Professor endpoint tests
│   │   ├── test_course_controller.py  # Course endpoint tests
│   │   ├── test_academic_record_controller.py # Academic record tests
│   │   ├── test_academic_record_service.py # Academic record service tests
│   │   ├── test_grading_assessment_controller.py # Grading assessment tests
│   │   ├── test_grading_assessment_service.py # Grading assessment service tests
│   │   ├── test_student_information_controller.py # Student info tests
│   │   └── test_student_information_service.py # Student info service tests
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

### Comprehensive Test Suite - 100% Success Rate
- **200+ unit tests** covering all functionality (100% passing)
- **66 model tests** for database integrity across all modules
- **62 schema tests** for validation across all modules
- **19 authentication tests** for security
- **100+ API endpoint tests** for all controllers and services
- **Async/await implementation** fully tested and working
- **Module-specific tests** for academic records, grading assessment, and student information

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

# Run module-specific tests
python run_unit_tests.py --module academic_record_controller
python run_unit_tests.py --module academic_record_service
python run_unit_tests.py --module grading_assessment_controller
python run_unit_tests.py --module grading_assessment_service
python run_unit_tests.py --module student_information_controller
python run_unit_tests.py --module student_information_service

# Generate coverage report
python run_unit_tests.py --coverage

# Individual test files
pytest tests/unit/test_auth.py -v
pytest tests/unit/test_models.py -v
pytest tests/unit/test_grading_assessment_controller.py -v
```

### Enhanced Test Runner Features

The `run_unit_tests.py` script now supports **13 different module options** for targeted testing:

```bash
# Core modules
python run_unit_tests.py --module auth
python run_unit_tests.py --module models
python run_unit_tests.py --module schemas

# Controller modules
python run_unit_tests.py --module auth_controller
python run_unit_tests.py --module student_controller
python run_unit_tests.py --module professor_controller
python run_unit_tests.py --module course_controller

# Academic Record module
python run_unit_tests.py --module academic_record_controller
python run_unit_tests.py --module academic_record_service

# Grading Assessment module
python run_unit_tests.py --module grading_assessment_controller
python run_unit_tests.py --module grading_assessment_service

# Student Information module
python run_unit_tests.py --module student_information_controller
python run_unit_tests.py --module student_information_service

# Additional options
python run_unit_tests.py --verbose          # Detailed output
python run_unit_tests.py --coverage         # Generate coverage report
python run_unit_tests.py --summary          # Show test summary only
python run_unit_tests.py --lint             # Run code quality checks
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

### Course Endpoints (`/courses`)
- Browse all courses with role-based filtering
- Get detailed course information
- View enrollment statistics
- Department and semester listings

### Academic Record Endpoints (`/academic-records`)
- Transcript generation and management
- GPA calculations and academic progress tracking
- Semester GPA tracking and analysis
- Academic record creation and updates

### Grading & Assessment Endpoints (`/grading`)
- Assignment creation, management, and publishing
- Exam scheduling and session management
- Grade entry, modification, and publishing
- Gradebook management and statistics
- Bulk operations for assignments and grades

### Student Information Endpoints (`/student-info`)
- Attendance tracking and reporting
- Student communication and messaging
- Student directory and contact management
- Performance monitoring and analytics

**📚 Complete API Guide**: See [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md) for detailed documentation with examples.

## 🗄️ Database Schema

### Core Models
- **User**: Authentication with email, password, role
- **Student**: Academic profile with enrollment tracking
- **Professor**: Academic staff with course assignments
- **Course**: Course information with enrollment management
- **Enrollments**: Many-to-many student-course relationships

### Academic Record Models
- **AcademicRecord**: Individual course grades and academic performance
- **Transcript**: Official academic transcripts with GPA calculations
- **AcademicProgress**: Degree requirements and progress tracking
- **SemesterGPA**: Semester-level GPA tracking and analysis

### Grading & Assessment Models
- **Assignment**: Assignment creation, management, and publishing
- **AssignmentSubmission**: Student submissions and feedback
- **Exam**: Exam scheduling and management
- **ExamSession**: Individual exam sessions and attendance
- **Grade**: Grade entry, modification, and publishing
- **Gradebook**: Comprehensive gradebook management
- **GradeStatistics**: Statistical analysis and reporting

### Student Information Models
- **Attendance**: Attendance tracking and reporting
- **AttendanceSummary**: Attendance summaries and analytics
- **Message**: Student communication and messaging
- **StudentDirectory**: Student contact and directory information
- **StudentPerformance**: Performance monitoring and analytics
- **CommunicationLog**: Communication history and tracking

### Features
- **Role-based permissions** (Student/Professor)
- **Enrollment capacity** validation
- **Schedule conflict** detection
- **Course prerequisites** tracking
- **Academic progress** monitoring
- **Grading and assessment** management
- **Attendance tracking** and reporting
- **Student communication** and messaging
- **Transcript generation** and GPA calculations
- **Bulk operations** for efficiency

## 🔧 Development

### Model Organization
Models are logically separated by responsibility:
- `models/user.py` - Authentication and roles
- `models/student.py` - Student-specific data
- `models/professor.py` - Professor-specific data  
- `models/course.py` - Course and enrollment data
- `models/academic_record.py` - Academic records and transcripts
- `models/grading_assessment.py` - Grading and assessment data
- `models/student_information.py` - Student information and communication

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

### ✅ **Fully Implemented & Production Ready**
- **Authentication System**: JWT, password hashing, role-based access
- **User Management**: Student and professor registration/profiles
- **Course Management**: Full CRUD operations with enrollment
- **Academic Record Management**: Transcript generation, GPA calculations, progress tracking
- **Grading & Assessment**: Assignment/exam management, gradebook operations, statistics
- **Student Information**: Attendance tracking, communication, directory management
- **Database Layer**: Complete SQLAlchemy models with relationships across all modules
- **API Layer**: RESTful endpoints with proper HTTP status codes for all modules
- **Async/Await Implementation**: Full async support throughout FastAPI
- **Testing Suite**: 200+ comprehensive unit tests (100% passing)
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
- **Asynchronous programming** with FastAPI and async/await patterns
- **Authentication and authorization** best practices
- **Database design** with proper relationships across multiple modules
- **API development** with FastAPI and Pydantic for complex academic systems
- **Test-driven development** with comprehensive test coverage (200+ tests)
- **Clean architecture** with separation of concerns and modular design
- **Professional documentation** and code organization
- **Academic system management** including grading, assessment, and student information
- **Bulk operations** and performance optimization techniques

Perfect for learning enterprise-level software development patterns! 🚀

## 📝 Additional Resources

- **API Documentation**: [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md)
- **Test Documentation**: [tests/UNIT_TESTS_GUIDE.md](tests/UNIT_TESTS_GUIDE.md)
- **Academic Record Guide**: [ACADEMIC_RECORD_ACCESS_GUIDE.md](ACADEMIC_RECORD_ACCESS_GUIDE.md)
- **Grading Assessment Guide**: [GRADING_ASSESSMENT_GUIDE.md](GRADING_ASSESSMENT_GUIDE.md)
- **Student Information Guide**: [STUDENT_INFORMATION_MANAGEMENT_GUIDE.md](STUDENT_INFORMATION_MANAGEMENT_GUIDE.md)
- **Interactive API Docs**: http://localhost:9600/docs (when running)