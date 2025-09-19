# Student Information Management Module

## Overview

The Student Information Management module provides comprehensive functionality for professors to access and manage student information, including directory access, academic records, attendance tracking, and student communication.

## Features

### 1. Student Directory
- Access enrolled student information and contact details
- Search and filter students by various criteria
- View student academic information and performance
- Manage student directory entries

### 2. Academic Records
- View student academic history and performance
- Track student progress and grades
- Identify students at academic risk
- Monitor student performance trends

### 3. Attendance Tracking
- Record and monitor student attendance
- Track attendance patterns and trends
- Generate attendance reports
- Identify attendance issues early

### 4. Student Communication
- Send messages to individual students or entire classes
- Track message delivery and read status
- Schedule messages for future delivery
- Maintain communication logs

## API Endpoints

### Student Directory
- `GET /student-information/directory` - Get student directory with optional filtering
- `GET /student-information/directory/{student_id}` - Get specific student directory entry
- `PUT /student-information/directory/{student_id}` - Update student directory entry

### Academic Records
- `GET /student-information/academic-records/{student_id}` - Get student academic records
- `GET /student-information/academic-records/course/{course_id}` - Get course student performance
- `PUT /student-information/academic-records/{performance_id}` - Update student performance
- `GET /student-information/academic-records/at-risk` - Get students at academic risk
- `GET /student-information/academic-records/risk-assessment/{student_id}` - Assess student risk

### Attendance Tracking
- `POST /student-information/attendance` - Create attendance record
- `POST /student-information/attendance/bulk` - Create multiple attendance records
- `GET /student-information/attendance` - Get attendance records with filtering
- `GET /student-information/attendance/{attendance_id}` - Get specific attendance record
- `PUT /student-information/attendance/{attendance_id}` - Update attendance record
- `GET /student-information/attendance/summary/{student_id}` - Get attendance summary
- `GET /student-information/attendance/report/{course_id}` - Get attendance report

### Student Communication
- `POST /student-information/messages` - Create new message
- `GET /student-information/messages` - Get messages with filtering
- `GET /student-information/messages/{message_id}` - Get specific message
- `PUT /student-information/messages/{message_id}` - Update message
- `POST /student-information/messages/{message_id}/send` - Send message
- `GET /student-information/messages/{message_id}/recipients` - Get message recipients
- `GET /student-information/messages/report` - Get message report

### Communication Logs
- `GET /student-information/communication-logs` - Get communication logs with filtering

### Dashboard and Analytics
- `GET /student-information/dashboard` - Get professor dashboard
- `GET /student-information/dashboard/student/{student_id}` - Get student dashboard
- `GET /student-information/search/students` - Search students
- `GET /student-information/analytics/attendance-trends` - Get attendance trends

### Bulk Operations
- `POST /student-information/bulk/messages` - Create multiple messages

## Database Models

### Attendance
Tracks individual student attendance records.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course
- `attendance_date` - Date of the class session
- `status` - Attendance status (present, absent, late, excused, tardy)
- `notes` - Professor notes about attendance
- `late_minutes` - Minutes late if status is late/tardy
- `session_topic` - What was covered in class
- `session_duration` - Duration in minutes
- `recorded_at` - When the record was created
- `recorded_by` - Foreign key to Professor

### AttendanceSummary
Tracks semester-wise attendance statistics.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course
- `semester` - Semester (e.g., "Fall 2024")
- `year` - Academic year
- `total_sessions` - Total number of sessions
- `present_count` - Number of present sessions
- `absent_count` - Number of absent sessions
- `late_count` - Number of late sessions
- `excused_count` - Number of excused sessions
- `tardy_count` - Number of tardy sessions
- `attendance_percentage` - Calculated attendance percentage
- `total_late_minutes` - Total minutes late

### Message
Stores messages sent by professors to students.

**Fields:**
- `id` - Primary key
- `sender_id` - Foreign key to Professor
- `course_id` - Foreign key to Course (optional)
- `subject` - Message subject
- `content` - Message content
- `message_type` - Type of message (announcement, reminder, assignment, etc.)
- `priority` - Message priority (low, normal, high, urgent)
- `status` - Message status (draft, sent, delivered, read, archived)
- `is_broadcast` - Whether sent to multiple students
- `created_at` - When message was created
- `sent_at` - When message was sent
- `scheduled_at` - When message is scheduled to be sent

### MessageRecipient
Tracks message delivery to individual students.

**Fields:**
- `id` - Primary key
- `message_id` - Foreign key to Message
- `student_id` - Foreign key to Student
- `status` - Delivery status (sent, delivered, read, archived)
- `read_at` - When message was read
- `delivered_at` - When message was delivered

### StudentDirectory
Stores student contact and academic information for professor access.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `email` - Student email
- `phone` - Student phone number
- `emergency_contact` - Emergency contact name
- `emergency_phone` - Emergency contact phone
- `address` - Student address
- `major` - Student major
- `year_level` - Student year level
- `gpa` - Student GPA
- `enrollment_status` - Enrollment status (active, inactive, graduated, suspended)
- `advisor_id` - Foreign key to Professor (advisor)
- `notes` - Professor notes about student
- `show_contact_info` - Whether to show contact information
- `show_academic_info` - Whether to show academic information

### StudentPerformance
Tracks student performance in courses.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course
- `current_grade` - Current calculated grade
- `participation_score` - Participation score
- `attendance_score` - Attendance score
- `assignment_average` - Assignment average
- `exam_average` - Exam average
- `is_at_risk` - Academic risk flag
- `risk_factors` - JSON string of risk factors
- `improvement_areas` - Areas needing improvement
- `professor_notes` - Professor notes
- `last_contact_date` - Last contact date
- `next_follow_up` - Next follow-up date

### CommunicationLog
Logs all communications between professors and students.

**Fields:**
- `id` - Primary key
- `professor_id` - Foreign key to Professor
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course (optional)
- `communication_type` - Type of communication (email, meeting, call, message)
- `subject` - Communication subject
- `content` - Communication content
- `direction` - Direction (sent, received)
- `requires_follow_up` - Whether follow-up is required
- `follow_up_date` - Follow-up date
- `follow_up_notes` - Follow-up notes
- `communication_date` - Date of communication

## Usage Examples

### Get Student Directory
```bash
curl -X GET "http://localhost:9600/student-information/directory" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Record Attendance
```bash
curl -X POST "http://localhost:9600/student-information/attendance" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "attendance_date": "2024-01-15T10:00:00",
    "status": "present",
    "session_topic": "Introduction to Programming",
    "session_duration": 90
  }'
```

### Send Message to Students
```bash
curl -X POST "http://localhost:9600/student-information/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "subject": "Assignment Due Date",
    "content": "Please remember that the assignment is due next week.",
    "message_type": "assignment",
    "priority": "high",
    "recipient_ids": [1, 2, 3]
  }'
```

### Get Attendance Report
```bash
curl -X GET "http://localhost:9600/student-information/attendance/report/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Professor Dashboard
```bash
curl -X GET "http://localhost:9600/student-information/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Authentication

All endpoints require professor authentication. Professors can only access information for students in their courses.

## Error Handling

The module includes comprehensive error handling:
- 401 Unauthorized - Invalid or missing authentication token
- 403 Forbidden - Professor trying to access restricted information
- 404 Not Found - Student, course, or record not found
- 400 Bad Request - Invalid request data or validation errors

## Testing

### Unit Tests
- `tests/unit/test_student_information_models.py` - Tests for database models
- `tests/unit/test_student_information_service.py` - Tests for business logic

### Integration Tests
- `tests/integration/test_student_information_integration.py` - Tests for API endpoints

### Running Tests
```bash
# Run unit tests
python -m pytest tests/unit/test_student_information_*.py -v

# Run integration tests
python -m pytest tests/integration/test_student_information_integration.py -v

# Run all student information tests
python -m pytest tests/unit/test_student_information_*.py tests/integration/test_student_information_integration.py -v
```

## Sample Data

To initialize sample data for testing:

```bash
python init_student_information_sample_data.py
```

This will create:
- Sample student directory entries
- Student performance records
- Attendance records for multiple sessions
- Messages from professors to students
- Communication logs

## File Structure

```
backend/
├── models/
│   └── student_information.py          # Database models
├── schemas/
│   └── student_information_schemas.py  # Pydantic schemas
├── repositories/
│   └── student_information_repository.py # Data access layer
├── services/
│   └── student_information_service.py  # Business logic layer
├── controllers/
│   └── student_information_controller.py # API endpoints
└── main.py                             # Updated with new router

tests/
├── unit/
│   ├── test_student_information_models.py
│   └── test_student_information_service.py
└── integration/
    └── test_student_information_integration.py

init_student_information_sample_data.py  # Sample data initialization
STUDENT_INFORMATION_MANAGEMENT_GUIDE.md  # This documentation
```

## Key Features

### Attendance Tracking
- **Real-time Recording**: Record attendance during class sessions
- **Bulk Operations**: Record attendance for entire classes at once
- **Status Tracking**: Track present, absent, late, excused, and tardy statuses
- **Automatic Summaries**: Generate attendance summaries and statistics
- **Risk Identification**: Identify students with attendance issues

### Student Communication
- **Multiple Message Types**: Announcements, reminders, assignments, grades
- **Priority Levels**: Low, normal, high, and urgent message priorities
- **Delivery Tracking**: Track message delivery and read status
- **Scheduled Messages**: Schedule messages for future delivery
- **Broadcast Capability**: Send messages to multiple students

### Academic Monitoring
- **Performance Tracking**: Monitor student grades and performance
- **Risk Assessment**: Automatically assess academic risk factors
- **Progress Monitoring**: Track student progress over time
- **Early Intervention**: Identify students needing additional support

### Dashboard and Analytics
- **Professor Dashboard**: Overview of teaching load and student status
- **Student Dashboard**: Individual student performance summary
- **Attendance Trends**: Analyze attendance patterns and trends
- **Communication Analytics**: Track communication effectiveness

## Future Enhancements

1. **Mobile App Support** - Optimized endpoints for mobile applications
2. **Email Integration** - Send messages via email
3. **SMS Notifications** - Send urgent messages via SMS
4. **Calendar Integration** - Sync with calendar systems
5. **Advanced Analytics** - Machine learning for risk prediction
6. **Automated Alerts** - Automated alerts for attendance issues
7. **Parent Communication** - Communication with parents/guardians
8. **Video Conferencing** - Integration with video conferencing tools
9. **Document Sharing** - Share documents and assignments
10. **Grade Book Integration** - Integration with grade book systems

## Security Considerations

1. **Data Privacy** - Professors can only access their students' information
2. **Message Security** - Secure message storage and transmission
3. **Audit Trail** - Complete audit trail of all communications
4. **Access Control** - Role-based access control for different functions
5. **Data Encryption** - Encrypt sensitive student information

## Performance Considerations

1. **Database Indexing** - Proper indexes on frequently queried fields
2. **Caching** - Cache frequently accessed student information
3. **Pagination** - Implement pagination for large datasets
4. **Bulk Operations** - Optimize bulk attendance and message operations
5. **Query Optimization** - Optimize complex queries for better performance
