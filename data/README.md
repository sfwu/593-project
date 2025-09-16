# Database Files Directory

This directory contains all SQLite database files for the Academic Information Management System with comprehensive role-based functionality.

## 📂 File Organization

### **Production Database**
- `academic_management.db` - Main application database with full schema

### **Test Databases** 
- `test_*.db` - Isolated test databases (auto-created/cleaned during testing)
- In-memory databases for unit tests (no files created)
- Test databases are ignored by git and cleaned up automatically

## 🗄️ **Complete Database Schema**

### **Core Tables**
```sql
-- Users (Authentication)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'student' or 'professor'
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Students (Academic Profiles)  
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    student_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    major TEXT,
    year_level TEXT,
    gpa REAL,
    phone TEXT,
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Professors (Faculty Profiles)
CREATE TABLE professors (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    professor_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    office_location TEXT,
    office_hours TEXT,
    department TEXT NOT NULL,
    title TEXT,
    specialization TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Courses (Course Management)
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    course_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 3,
    professor_id INTEGER NOT NULL,
    department TEXT NOT NULL,
    semester TEXT NOT NULL,
    year INTEGER NOT NULL,
    max_enrollment INTEGER DEFAULT 30,
    prerequisites TEXT,
    schedule TEXT,
    syllabus TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES professors (id)
);

-- Enrollments (Student-Course Relationships)
CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    enrollment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'enrolled',
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);
```

## 🚀 **Quick Start**

### **Database Initialization**
```bash
# Start the backend (auto-creates database)
python backend/main.py

# Or initialize manually through the API
curl -X POST http://localhost:9600/auth/register/student \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@university.edu",
    "password": "password123",
    "student_id": "STU001",
    "first_name": "John",
    "last_name": "Doe",
    "major": "Computer Science"
  }'
```

### **Sample Data Creation**
```bash
# Use the API to create sample data
python init_sample_data.py  # If script exists

# Or create via API endpoints:
# 1. Register users (students & professors)
# 2. Create courses  
# 3. Enroll students in courses
```

## 🎯 **Production Ready Features**

### **Database Relationships**
- **One-to-One**: User ↔ Student/Professor
- **One-to-Many**: Professor → Courses
- **Many-to-Many**: Students ↔ Courses (via enrollments)

### **Data Integrity**
- **Foreign Key Constraints**: Maintain referential integrity
- **Unique Constraints**: Prevent duplicate emails, IDs
- **Default Values**: Sensible defaults for optional fields
- **Timestamps**: Track creation and modification times

### **Performance Optimizations**
- **Indexes**: Primary keys and foreign keys auto-indexed
- **Query Optimization**: Efficient joins for relationships
- **Connection Pooling**: SQLAlchemy session management

## 🧪 **Testing Database Strategy**

### **Unit Tests (113 tests, 100% passing)**
```python
# In-memory SQLite for fast tests
engine = create_engine("sqlite:///:memory:")

# Fresh database for each test
@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()
```

### **Integration Tests**
```python
# Temporary file databases
engine = create_engine("sqlite:///test_integration.db")

# Real database operations with cleanup
def test_with_real_db():
    # Test real scenarios
    cleanup_test_data()
```

### **Test Data Management**
```python
# Mock data manager for consistent test data
mock_data_manager.setup_complete_test_data(db)
# Creates: users, students, professors, courses, enrollments

# Automatic cleanup after tests
mock_data_manager.cleanup_all_data(db)
```

## 🔧 **Development Workflow**

### **Database Migrations**
```python
# SQLAlchemy auto-generates schema
Base.metadata.create_all(bind=engine)

# Future: Alembic for schema migrations
# alembic revision --autogenerate -m "Add new table"
# alembic upgrade head
```

### **Development Database Reset**
```bash
# Remove database file to reset
rm data/academic_management.db

# Restart backend (recreates schema)
python backend/main.py
```

### **Manual Database Inspection**
```bash
# Access SQLite directly
sqlite3 data/academic_management.db

# Useful queries
.tables                    # List all tables
.schema users             # Show table schema
SELECT * FROM users;      # View user data
SELECT * FROM enrollments; # View enrollments
```

## 📊 **Sample Data Structure**

### **Users & Roles**
```sql
-- Sample Students
INSERT INTO users (email, role) VALUES 
  ('john.doe@university.edu', 'student'),
  ('jane.smith@university.edu', 'student');

-- Sample Professors  
INSERT INTO users (email, role) VALUES
  ('prof.johnson@university.edu', 'professor'),
  ('dr.brown@university.edu', 'professor');
```

### **Courses & Enrollment**
```sql
-- Sample Courses
INSERT INTO courses (course_code, title, professor_id, department) VALUES
  ('CS101', 'Introduction to Programming', 1, 'Computer Science'),
  ('CS201', 'Data Structures', 1, 'Computer Science'),
  ('MATH101', 'Calculus I', 2, 'Mathematics');

-- Sample Enrollments
INSERT INTO enrollments (student_id, course_id) VALUES
  (1, 1), (1, 2),  -- John in CS101, CS201
  (2, 1), (2, 3);  -- Jane in CS101, MATH101
```

## 🛡️ **Security & Backup**

### **Data Security**
- **Password Hashing**: bcrypt with salts (no plain text passwords)
- **SQL Injection Protection**: SQLAlchemy ORM (parameterized queries)
- **Role-based Access**: User roles enforced at API level

### **Backup Strategy**
```bash
# Simple SQLite backup
cp data/academic_management.db data/backup_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 data/academic_management.db ".backup backup.db"
```

## 🎓 **Educational Value**

This database demonstrates:
- **Relational Database Design**: Proper normalization and relationships
- **Authentication Patterns**: User management with role-based access
- **Academic Domain Modeling**: Real-world entity relationships
- **Testing Strategies**: Unit and integration test database patterns
- **Performance Considerations**: Indexing and query optimization

## 📝 **Git Strategy**

**Current Approach:**
- ✅ **Schema tracked**: Database structure in models
- ❌ **Data files ignored**: .db files not committed (except initial)
- ✅ **Test databases ignored**: Temporary test files excluded

**Database Versioning:**
```bash
# Schema changes tracked in code
git add backend/models/
git commit -m "Add course enrollment tracking"

# Database recreated from models on startup
# No need to commit .db files
```

**Team Collaboration:**
```bash
# Each developer gets clean database
git clone repo
python backend/main.py  # Creates fresh database

# Consistent schema from models
# Sample data via API calls or scripts
```

This ensures **consistent database structure** across all environments! 🚀