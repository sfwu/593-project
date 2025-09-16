# Academic Information Management System - Backend API Guide

## Overview

This backend provides a comprehensive authentication and course management system with role-based access control for students and professors.

## Features Implemented

### 🔐 Authentication System
- JWT-based authentication
- Role-based access control (Student/Professor)
- Password hashing with bcrypt
- User registration for both students and professors

### 👨‍🎓 Student Features
1. **Profile Management**
   - View/update personal information
   - Change password
   
2. **Course Management**
   - Search courses by department, semester, year, or keywords
   - Enroll in courses with prerequisite validation
   - View personal class schedule
   - Withdraw from courses within allowed timeframes
   - Time conflict detection

### 👨‍🏫 Professor Features
1. **Profile Management**
   - Manage academic information and office hours
   - View department affiliation
   - Track teaching load

2. **Course Administration**
   - Create new course offerings
   - Update course information and syllabus
   - View and manage student enrollments
   - Get enrollment statistics
   - Remove students from courses

## API Endpoints

### Authentication Endpoints

#### POST `/auth/login`
Login with email and password
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST `/auth/register/student`
Register a new student
```json
{
  "email": "student@example.com",
  "password": "password123",
  "student_id": "STU001",
  "first_name": "John",
  "last_name": "Doe",
  "major": "Computer Science",
  "year_level": "Junior"
}
```

#### POST `/auth/register/professor`
Register a new professor
```json
{
  "email": "prof@example.com",
  "password": "password123",
  "professor_id": "PROF001",
  "first_name": "Jane",
  "last_name": "Smith",
  "department": "Computer Science",
  "title": "Associate Professor"
}
```

#### GET `/auth/me`
Get current user profile (requires authentication)

### Student Endpoints (prefix: `/students`)

#### PUT `/students/profile`
Update student profile (requires student authentication)

#### POST `/students/change-password`
Change student password

#### GET `/students/courses/search`
Search available courses with optional filters:
- `department`: Filter by department
- `semester`: Filter by semester  
- `year`: Filter by year
- `keyword`: Search in title/description

#### POST `/students/courses/enroll`
Enroll in a course
```json
{
  "course_id": 1
}
```

#### GET `/students/courses/enrolled`
Get student's enrolled courses

#### DELETE `/students/courses/{course_id}/withdraw`
Withdraw from a course

#### GET `/students/schedule`
Get student's class schedule with optional filters

### Professor Endpoints (prefix: `/professors`)

#### PUT `/professors/profile`
Update professor profile (requires professor authentication)

#### POST `/professors/change-password`
Change professor password

#### GET `/professors/profile/teaching-load`
Get teaching load and schedule

#### POST `/professors/courses`
Create a new course
```json
{
  "course_code": "CS101",
  "title": "Introduction to Computer Science",
  "description": "Basic concepts of programming",
  "credits": 3,
  "department": "Computer Science",
  "semester": "Fall 2024",
  "year": 2024,
  "max_enrollment": 30,
  "schedule": "MWF 10:00-11:00"
}
```

#### GET `/professors/courses`
Get professor's courses with optional filters

#### PUT `/professors/courses/{course_id}`
Update course information

#### DELETE `/professors/courses/{course_id}`
Deactivate a course (soft delete)

#### GET `/professors/courses/{course_id}/students`
Get students enrolled in a course

#### DELETE `/professors/courses/{course_id}/students/{student_id}`
Remove student from course

#### GET `/professors/courses/{course_id}/enrollment-stats`
Get enrollment statistics for a course

## Database Models

### User
Base authentication model with email, password, and role

### Student
Extended profile with student ID, academic information, and enrollment data

### Professor  
Extended profile with professor ID, department, office hours, and specialization

### Course
Course information including prerequisites, schedule, and enrollment limits

### Enrollment
Many-to-many relationship between students and courses

## Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the backend**:
   ```bash
   cd backend
   python main.py
   ```

3. **Access the API**:
   - Server runs on `http://localhost:9600`
   - API documentation: `http://localhost:9600/docs`
   - Alternative docs: `http://localhost:9600/redoc`

## Authentication Usage

1. **Register a user** (student or professor)
2. **Login** to get JWT token
3. **Include token** in Authorization header: `Bearer <token>`
4. **Access protected endpoints** based on user role

## Database

- Uses SQLite database stored in `data/academic_management.db`
- Database is automatically created on first run
- All tables are created via SQLAlchemy models

## Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- Role-based access control
- Input validation with Pydantic schemas
- SQL injection protection via SQLAlchemy ORM

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid credentials)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

## Testing

Use tools like:
- **Postman** or **Insomnia** for manual API testing
- **FastAPI docs** at `/docs` for interactive testing
- **curl** commands for command-line testing

Example curl command:
```bash
# Login
curl -X POST "http://localhost:9600/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "student@example.com", "password": "password123"}'

# Search courses (with token)
curl -X GET "http://localhost:9600/students/courses/search?department=Computer%20Science" \
     -H "Authorization: Bearer <your-jwt-token>"
```

## Next Steps for Production

1. **Change SECRET_KEY** in `config/auth.py`
2. **Use environment variables** for configuration
3. **Add rate limiting**
4. **Implement proper logging**
5. **Add comprehensive test suite**
6. **Use production database** (PostgreSQL/MySQL)
7. **Add API versioning**
8. **Implement caching** for frequently accessed data
