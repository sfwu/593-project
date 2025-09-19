# Academic Record Information Grade Management System

A **comprehensive full-stack application** for academic information management with role-based authentication, featuring students and professors with complete academic record management, grading, and student information administration capabilities.

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
- **Academic Records**: Access grades, transcripts, GPA calculations, and academic progress
- **Grade Tracking**: View detailed grade information and academic performance

### 👨‍🏫 **Professor Features**
- **Academic Profile**: Manage professional information, office hours, specialization
- **Course Administration**: Create, update, and manage course offerings
- **Enrollment Management**: View student rosters and enrollment statistics
- **Teaching Load**: Track assigned courses and calculate workload
- **Grading & Assessment**: Create assignments, schedule exams, manage grades and gradebooks
- **Student Information Management**: Access student directory, track attendance, communicate with students
- **Academic Record Management**: Manage student grades, generate transcripts, track academic progress

## 🛠️ Tech Stack

- **Language**: Python 3.12
- **Frontend**: Streamlit (port 9700)
- **Backend**: FastAPI (port 9600) 
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with passlib/bcrypt
- **Testing**: pytest with 113 comprehensive unit tests
- **Validation**: Pydantic schemas

## 📁 Project Structure

```
593-project-academic-record-information-grade/
├── backend/                           # FastAPI backend
│   ├── config/                       # Configuration
│   │   ├── auth.py                   # JWT authentication system
│   │   ├── database.py               # Database configuration
│   │   └── settings.py               # Application settings
│   ├── models/                       # Database models
│   │   ├── user.py                   # User & UserRole models
│   │   ├── student.py                # Student model
│   │   ├── professor.py              # Professor model
│   │   ├── course.py                 # Course & enrollment models
│   │   ├── academic_record.py        # Academic records & transcripts
│   │   ├── grading_assessment.py     # Grading & assessment models
│   │   └── student_information.py    # Student information management
│   ├── schemas/                      # Pydantic schemas
│   │   ├── student_schemas.py        # Student API schemas
│   │   ├── academic_record_schemas.py # Academic record schemas
│   │   ├── grading_assessment_schemas.py # Grading schemas
│   │   └── student_information_schemas.py # Student info schemas
│   ├── controllers/                  # API endpoints
│   │   ├── auth_controller.py        # Authentication endpoints
│   │   ├── student_controller.py     # Student functionality
│   │   ├── professor_controller.py   # Professor functionality
│   │   ├── course_controller.py      # General course endpoints
│   │   ├── academic_record_controller.py # Academic record endpoints
│   │   ├── grading_assessment_controller.py # Grading endpoints
│   │   └── student_information_controller.py # Student info endpoints
│   ├── services/                     # Business logic layer
│   │   ├── academic_record_service.py # Academic record services
│   │   ├── grading_assessment_service.py # Grading services
│   │   ├── student_information_service.py # Student info services
│   │   └── student_service.py        # Student services
│   ├── repositories/                 # Data access layer
│   │   ├── academic_record_repository.py # Academic record data access
│   │   ├── grading_assessment_repository.py # Grading data access
│   │   ├── student_information_repository.py # Student info data access
│   │   └── student_repository.py     # Student data access
│   ├── main.py                       # FastAPI app with all routes
│   └── README.md                     # Backend documentation
├── frontend/
│   └── app.py                        # Streamlit web interface
├── tests/                            # Comprehensive test suite
│   ├── unit/                         # Unit tests (113 tests, 100% passing)
│   │   ├── test_auth.py              # Authentication tests
│   │   ├── test_models.py            # Database model tests
│   │   ├── test_schemas.py           # Schema validation tests
│   │   ├── test_auth_controller.py   # Auth endpoint tests
│   │   ├── test_student_controller.py # Student endpoint tests
│   │   ├── test_professor_controller.py # Professor endpoint tests
│   │   ├── test_course_controller.py  # Course endpoint tests
│   │   ├── test_academic_record_controller.py # Academic record tests
│   │   ├── test_grading_assessment_controller.py # Grading tests
│   │   ├── test_student_information_controller.py # Student info tests
│   │   ├── test_academic_record_service.py # Academic record service tests
│   │   ├── test_grading_assessment_service.py # Grading service tests
│   │   └── test_student_information_service.py # Student info service tests
│   ├── integration/                  # Integration tests
│   │   ├── test_academic_record_integration.py # Academic record integration
│   │   ├── test_student_information_integration.py # Student info integration
│   │   ├── test_api_integration.py   # API integration tests
│   │   └── test_crud_integration.py  # CRUD integration tests
│   ├── conftest.py                   # Test configuration
│   ├── TEST_GUIDE.md                 # Testing guide
│   └── UNIT_TESTS_GUIDE.md           # Unit tests guide
├── data/                             # SQLite database files
│   ├── academic_management.db        # Main database
│   ├── test_integration.db           # Integration test database
│   ├── test_student_information_integration.db # Student info test database
│   └── transcripts/                  # Generated transcript files
├── run_unit_tests.py                 # Comprehensive test runner
├── run_tests.py                      # Test runner
├── run_backend.py                    # Backend runner
├── run_frontend.py                   # Frontend runner
├── init_sample_data.py               # Sample data initialization
├── init_academic_record_sample_data.py # Academic record sample data
├── init_grading_assessment_sample_data.py # Grading sample data
├── init_student_information_sample_data.py # Student info sample data
├── BACKEND_API_GUIDE.md              # Complete API documentation
├── ACADEMIC_RECORD_ACCESS_GUIDE.md   # Academic record module guide
├── GRADING_ASSESSMENT_GUIDE.md       # Grading module guide
├── STUDENT_INFORMATION_MANAGEMENT_GUIDE.md # Student info module guide
├── start.sh                          # Service startup script
├── status.sh                         # Service status script
├── stop.sh                           # Service stop script
└── requirements.txt                  # Python dependencies
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

### Sample Data Initialization
```bash
# Initialize basic sample data
python init_sample_data.py

# Initialize academic record sample data
python init_academic_record_sample_data.py

# Initialize grading assessment sample data
python init_grading_assessment_sample_data.py

# Initialize student information sample data
python init_student_information_sample_data.py
```

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
- **113 unit tests** covering all functionality (100% passing)
- **23 model tests** for database integrity
- **21 schema tests** for validation  
- **19 authentication tests** for security
- **50 API endpoint tests** for all controllers
- **Async/await implementation** fully tested and working

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

### Course Endpoints (`/courses`)
- Browse all courses with role-based filtering
- Get detailed course information
- View enrollment statistics
- Department and semester listings

### Academic Record Endpoints (`/academic-records`)
- `GET /academic-records/grades` - View student grades
- `GET /academic-records/gpa` - Get GPA calculation
- `GET /academic-records/transcripts` - List transcripts
- `POST /academic-records/transcripts/generate` - Generate transcript
- `GET /academic-records/progress` - View academic progress
- `GET /academic-records/dashboard` - Academic dashboard

### Grading & Assessment Endpoints (`/grading`)
- `POST /grading/assignments` - Create assignments
- `GET /grading/assignments` - View assignments
- `POST /grading/exams` - Schedule exams
- `GET /grading/exams` - View exams
- `POST /grading/grades` - Create grades
- `GET /grading/grades` - View grades
- `POST /grading/gradebooks` - Create gradebooks
- `GET /grading/gradebooks` - View gradebooks
- `GET /grading/dashboard` - Grading dashboard

### Student Information Management Endpoints (`/student-information`)
- `GET /student-information/directory` - Access student directory
- `GET /student-information/academic-records` - View student academic history
- `POST /student-information/attendance` - Record attendance
- `GET /student-information/attendance` - View attendance records
- `POST /student-information/messages` - Send messages to students
- `GET /student-information/messages` - View sent messages
- `GET /student-information/dashboard` - Professor dashboard

**📚 Complete API Guide**: See [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md) for detailed documentation with examples.

**📋 Module-Specific Guides**:
- [Academic Record Access Guide](ACADEMIC_RECORD_ACCESS_GUIDE.md)
- [Grading Assessment Guide](GRADING_ASSESSMENT_GUIDE.md)
- [Student Information Management Guide](STUDENT_INFORMATION_MANAGEMENT_GUIDE.md)

## 🗄️ Database Schema

### Core Models
- **User**: Authentication with email, password, role
- **Student**: Academic profile with enrollment tracking
- **Professor**: Academic staff with course assignments
- **Course**: Course information with enrollment management
- **Enrollments**: Many-to-many student-course relationships

### Academic Record Models
- **AcademicRecord**: Individual course grades and academic records
- **Transcript**: Official academic transcripts with file storage
- **AcademicProgress**: Degree requirements and completion tracking
- **SemesterGPA**: Semester-wise GPA calculations

### Grading & Assessment Models
- **Assignment**: Assignment information and requirements
- **AssignmentSubmission**: Student submissions and feedback
- **Exam**: Exam scheduling and logistics
- **ExamSession**: Individual exam sessions and attendance
- **Grade**: Individual grades with detailed feedback
- **Gradebook**: Gradebook configuration and settings
- **GradebookEntry**: Calculated gradebook entries
- **GradeStatistics**: Statistical analysis of grades
- **GradeModification**: Grade modification tracking

### Student Information Models
- **Attendance**: Individual attendance records
- **AttendanceSummary**: Semester-wise attendance statistics
- **Message**: Professor-to-student communications
- **MessageRecipient**: Message delivery tracking
- **StudentDirectory**: Student contact and academic information
- **StudentPerformance**: Student performance tracking
- **CommunicationLog**: Communication history logging

### Features
- **Role-based permissions** (Student/Professor)
- **Enrollment capacity** validation
- **Schedule conflict** detection
- **Course prerequisites** tracking
- **Academic progress** monitoring
- **Grade management** with detailed feedback
- **Transcript generation** with file storage
- **Attendance tracking** with analytics
- **Student communication** system
- **Performance monitoring** and risk assessment

## 🔧 Development

### Model Organization
Models are logically separated by responsibility:
- `models/user.py` - Authentication and roles
- `models/student.py` - Student-specific data
- `models/professor.py` - Professor-specific data  
- `models/course.py` - Course and enrollment data
- `models/academic_record.py` - Academic records and transcripts
- `models/grading_assessment.py` - Grading and assessment data
- `models/student_information.py` - Student information management

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
- **Academic Record Management**: Grades, transcripts, GPA calculations, progress tracking
- **Grading & Assessment**: Assignments, exams, gradebooks, statistical analysis
- **Student Information Management**: Directory access, attendance tracking, communication
- **Database Layer**: Complete SQLAlchemy models with relationships
- **API Layer**: RESTful endpoints with proper HTTP status codes
- **Async/Await Implementation**: Full async support throughout FastAPI
- **Testing Suite**: 113 comprehensive unit tests (100% passing)
- **Documentation**: Complete API guide and module-specific documentation
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
- **Database design** with proper relationships
- **API development** with FastAPI and Pydantic
- **Test-driven development** with comprehensive test coverage
- **Clean architecture** with separation of concerns
- **Professional documentation** and code organization

Perfect for learning enterprise-level software development patterns! 🚀

## 📝 Additional Resources

- **API Documentation**: [BACKEND_API_GUIDE.md](BACKEND_API_GUIDE.md)
- **Test Documentation**: [tests/UNIT_TESTS_GUIDE.md](tests/UNIT_TESTS_GUIDE.md)
- **Testing Guide**: [tests/TEST_GUIDE.md](tests/TEST_GUIDE.md)
- **Academic Record Guide**: [ACADEMIC_RECORD_ACCESS_GUIDE.md](ACADEMIC_RECORD_ACCESS_GUIDE.md)
- **Grading Assessment Guide**: [GRADING_ASSESSMENT_GUIDE.md](GRADING_ASSESSMENT_GUIDE.md)
- **Student Information Guide**: [STUDENT_INFORMATION_MANAGEMENT_GUIDE.md](STUDENT_INFORMATION_MANAGEMENT_GUIDE.md)
- **Backend Architecture**: [backend/README.md](backend/README.md)
- **Interactive API Docs**: http://localhost:9600/docs (when running)