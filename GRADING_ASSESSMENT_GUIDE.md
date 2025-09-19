# Grading and Assessment Module

## Overview

The Grading and Assessment module provides comprehensive functionality for professors to manage assignments, schedule exams, create and publish grades, and maintain detailed gradebooks with statistical analysis.

## Features

### 1. Grade Management
- Create, modify, and publish grades for assignments and exams
- Apply late penalties and extra credit
- Support for grade curves and modifications
- Bulk grade operations

### 2. Gradebook Management
- Maintain comprehensive grade records with statistical analysis
- Automatic grade calculations and letter grade assignment
- Weight-based grading schemes
- Student performance tracking and risk identification

### 3. Assignment Creation
- Design and distribute assignments with due dates
- Support for multiple assignment types (homework, project, lab, quiz)
- Late submission policies and penalties
- File upload and submission tracking

### 4. Exam Scheduling
- Schedule and manage examination logistics
- Support for online and in-person exams
- Proctoring requirements and material restrictions
- Exam session tracking and attendance

## API Endpoints

### Assignment Management
- `POST /grading/assignments` - Create new assignment
- `GET /grading/assignments` - Get assignments with filtering
- `GET /grading/assignments/{assignment_id}` - Get specific assignment
- `PUT /grading/assignments/{assignment_id}` - Update assignment
- `POST /grading/assignments/{assignment_id}/publish` - Publish assignment
- `DELETE /grading/assignments/{assignment_id}` - Delete assignment
- `POST /grading/assignments/bulk` - Create multiple assignments

### Assignment Submissions
- `GET /grading/assignments/{assignment_id}/submissions` - Get assignment submissions
- `PUT /grading/submissions/{submission_id}` - Update submission (provide feedback)

### Exam Management
- `POST /grading/exams` - Create new exam
- `GET /grading/exams` - Get exams with filtering
- `GET /grading/exams/{exam_id}` - Get specific exam
- `PUT /grading/exams/{exam_id}` - Update exam
- `POST /grading/exams/{exam_id}/publish` - Publish exam

### Exam Sessions
- `POST /grading/exam-sessions` - Create exam session
- `GET /grading/exam-sessions` - Get exam sessions with filtering
- `PUT /grading/exam-sessions/{session_id}` - Update exam session

### Grade Management
- `POST /grading/grades` - Create new grade
- `GET /grading/grades` - Get grades with filtering
- `GET /grading/grades/{grade_id}` - Get specific grade
- `PUT /grading/grades/{grade_id}` - Update grade
- `POST /grading/grades/{grade_id}/publish` - Publish grade
- `POST /grading/grades/bulk` - Create multiple grades

### Gradebook Management
- `POST /grading/gradebooks` - Create new gradebook
- `GET /grading/gradebooks` - Get gradebooks with filtering
- `GET /grading/gradebooks/{gradebook_id}` - Get specific gradebook
- `PUT /grading/gradebooks/{gradebook_id}` - Update gradebook
- `GET /grading/gradebooks/{gradebook_id}/entries` - Get gradebook entries
- `GET /grading/gradebooks/{gradebook_id}/entries/{student_id}` - Get specific entry

### Grade Statistics
- `GET /grading/statistics/course/{course_id}` - Get course grade statistics

### Grade Modifications
- `POST /grading/grade-modifications` - Create grade modification
- `GET /grading/grade-modifications/{grade_id}` - Get grade modifications
- `POST /grading/grade-modifications/{modification_id}/approve` - Approve modification

### Dashboard and Analytics
- `GET /grading/dashboard` - Get professor grading dashboard
- `GET /grading/dashboard/course/{course_id}` - Get course grading summary
- `GET /grading/analytics/grade-distribution/{course_id}` - Get grade distribution report
- `GET /grading/analytics/assignment/{assignment_id}` - Get assignment analytics
- `GET /grading/analytics/exam/{exam_id}` - Get exam analytics

### Search and Bulk Operations
- `GET /grading/search/assignments` - Search assignments
- `GET /grading/search/exams` - Search exams
- `POST /grading/bulk/publish-grades` - Bulk publish grades
- `POST /grading/bulk/publish-assignments` - Bulk publish assignments

## Database Models

### Assignment
Stores assignment information and requirements.

**Fields:**
- `id` - Primary key
- `course_id` - Foreign key to Course
- `professor_id` - Foreign key to Professor
- `title` - Assignment title
- `description` - Assignment description
- `assignment_type` - Type (homework, project, lab, quiz, etc.)
- `instructions` - Detailed instructions
- `requirements` - Assignment requirements
- `total_points` - Maximum points possible
- `weight_percentage` - Weight in final grade
- `rubric` - Grading rubric (JSON)
- `due_date` - Assignment due date
- `late_submission_deadline` - Late submission deadline
- `late_penalty_percentage` - Penalty for late submissions
- `allow_late_submissions` - Whether late submissions are allowed
- `max_attempts` - Maximum submission attempts
- `submission_format` - Required submission format
- `file_size_limit` - File size limit in MB
- `is_published` - Whether assignment is published
- `is_active` - Whether assignment is active

### AssignmentSubmission
Tracks student submissions for assignments.

**Fields:**
- `id` - Primary key
- `assignment_id` - Foreign key to Assignment
- `student_id` - Foreign key to Student
- `submission_content` - Text submission or file path
- `file_path` - Path to uploaded file
- `file_name` - Original file name
- `file_size` - File size in bytes
- `submission_status` - Status (not_submitted, submitted, late, graded, returned)
- `submitted_at` - Submission timestamp
- `is_late` - Whether submission is late
- `late_hours` - Hours late
- `attempt_number` - Submission attempt number
- `professor_feedback` - Professor feedback
- `feedback_date` - When feedback was provided

### Exam
Stores exam information and scheduling details.

**Fields:**
- `id` - Primary key
- `course_id` - Foreign key to Course
- `professor_id` - Foreign key to Professor
- `title` - Exam title
- `description` - Exam description
- `exam_type` - Type (midterm, final, quiz, etc.)
- `instructions` - Exam instructions
- `total_points` - Maximum points possible
- `weight_percentage` - Weight in final grade
- `passing_grade` - Minimum passing grade
- `exam_date` - Exam date
- `start_time` - Exam start time
- `end_time` - Exam end time
- `duration_minutes` - Exam duration
- `location` - Exam location/room
- `is_online` - Whether exam is online
- `online_platform` - Online platform used
- `online_link` - Online exam link
- `proctoring_required` - Whether proctoring is required
- `proctoring_software` - Proctoring software used
- `allowed_materials` - Allowed materials
- `restricted_materials` - Restricted materials
- `registration_required` - Whether registration is required
- `registration_deadline` - Registration deadline
- `is_published` - Whether exam is published
- `is_active` - Whether exam is active

### ExamSession
Tracks individual exam sessions for students.

**Fields:**
- `id` - Primary key
- `exam_id` - Foreign key to Exam
- `student_id` - Foreign key to Student
- `session_start_time` - Session start time
- `session_end_time` - Session end time
- `actual_duration_minutes` - Actual duration
- `attended` - Whether student attended
- `late_arrival_minutes` - Minutes late
- `early_departure_minutes` - Minutes early departure
- `technical_issues` - Technical issues encountered
- `issues_resolved` - Whether issues were resolved

### Grade
Stores individual grades for assignments and exams.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course
- `professor_id` - Foreign key to Professor
- `assignment_id` - Foreign key to Assignment (optional)
- `exam_id` - Foreign key to Exam (optional)
- `points_earned` - Points earned by student
- `points_possible` - Total points possible
- `percentage` - Calculated percentage
- `letter_grade` - Letter grade (A+, A, A-, etc.)
- `grade_status` - Status (draft, published, late, exempt, incomplete, missing)
- `graded_date` - When grade was assigned
- `published_date` - When grade was published
- `is_late` - Whether submission was late
- `late_penalty_applied` - Late penalty percentage applied
- `extra_credit` - Extra credit points
- `curve_adjustment` - Curve adjustment applied
- `professor_comments` - Professor comments
- `rubric_scores` - Rubric scores (JSON)
- `detailed_feedback` - Detailed feedback
- `is_modified` - Whether grade was modified
- `modification_reason` - Reason for modification
- `modification_date` - When grade was modified
- `modified_by` - Who modified the grade

### Gradebook
Stores gradebook configuration and settings.

**Fields:**
- `id` - Primary key
- `course_id` - Foreign key to Course
- `professor_id` - Foreign key to Professor
- `name` - Gradebook name
- `description` - Gradebook description
- `semester` - Academic semester
- `year` - Academic year
- `grading_scheme` - Grading scheme (JSON)
- `letter_grade_scale` - Letter grade scale (JSON)
- `pass_fail_threshold` - Pass/fail threshold
- `drop_lowest_assignments` - Number of lowest assignments to drop
- `drop_lowest_exams` - Number of lowest exams to drop
- `curve_enabled` - Whether curve is enabled
- `curve_percentage` - Curve percentage
- `assignment_weight` - Assignment weight percentage
- `exam_weight` - Exam weight percentage
- `participation_weight` - Participation weight percentage
- `allow_student_view` - Whether students can view gradebook
- `is_published` - Whether gradebook is published
- `is_active` - Whether gradebook is active

### GradebookEntry
Stores calculated gradebook entries for individual students.

**Fields:**
- `id` - Primary key
- `gradebook_id` - Foreign key to Gradebook
- `student_id` - Foreign key to Student
- `total_points_earned` - Total points earned
- `total_points_possible` - Total points possible
- `overall_percentage` - Overall percentage
- `final_letter_grade` - Final letter grade
- `assignment_average` - Assignment average
- `exam_average` - Exam average
- `participation_average` - Participation average
- `assignments_completed` - Number of assignments completed
- `assignments_total` - Total number of assignments
- `exams_completed` - Number of exams completed
- `exams_total` - Total number of exams
- `is_passing` - Whether student is passing
- `is_at_risk` - Whether student is at risk
- `needs_attention` - Whether student needs attention
- `last_calculated` - When entry was last calculated

### GradeStatistics
Stores statistical analysis of grades for courses.

**Fields:**
- `id` - Primary key
- `course_id` - Foreign key to Course
- `gradebook_id` - Foreign key to Gradebook (optional)
- `total_students` - Total number of students
- `students_passing` - Number of students passing
- `students_failing` - Number of students failing
- `average_grade` - Average grade
- `median_grade` - Median grade
- `highest_grade` - Highest grade
- `lowest_grade` - Lowest grade
- `standard_deviation` - Standard deviation
- `a_grades` - Number of A grades
- `b_grades` - Number of B grades
- `c_grades` - Number of C grades
- `d_grades` - Number of D grades
- `f_grades` - Number of F grades
- `assignment_average` - Assignment average
- `exam_average` - Exam average
- `participation_average` - Participation average
- `calculated_at` - When statistics were calculated

### GradeModification
Tracks grade modifications and approvals.

**Fields:**
- `id` - Primary key
- `grade_id` - Foreign key to Grade
- `professor_id` - Foreign key to Professor (who made modification)
- `old_points` - Original points
- `new_points` - New points
- `old_percentage` - Original percentage
- `new_percentage` - New percentage
- `old_letter_grade` - Original letter grade
- `new_letter_grade` - New letter grade
- `reason` - Reason for modification
- `approved_by` - Who approved the modification
- `approval_date` - When modification was approved
- `is_approved` - Whether modification is approved
- `modified_at` - When modification was made

## Usage Examples

### Create Assignment
```bash
curl -X POST "http://localhost:9600/grading/assignments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "title": "Programming Assignment 1",
    "description": "Implement a simple calculator",
    "assignment_type": "homework",
    "total_points": 100.0,
    "weight_percentage": 15.0,
    "due_date": "2024-12-31T23:59:59",
    "late_penalty_percentage": 10.0,
    "allow_late_submissions": true,
    "max_attempts": 1
  }'
```

### Create Exam
```bash
curl -X POST "http://localhost:9600/grading/exams" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "title": "Midterm Exam",
    "description": "Comprehensive midterm examination",
    "exam_type": "midterm",
    "total_points": 100.0,
    "weight_percentage": 30.0,
    "exam_date": "2024-11-15",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "duration_minutes": 120,
    "location": "Room 101",
    "proctoring_required": true
  }'
```

### Create Grade
```bash
curl -X POST "http://localhost:9600/grading/grades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "assignment_id": 1,
    "points_earned": 85.0,
    "points_possible": 100.0,
    "percentage": 85.0,
    "letter_grade": "B",
    "grade_status": "published",
    "professor_comments": "Good work overall"
  }'
```

### Create Gradebook
```bash
curl -X POST "http://localhost:9600/grading/gradebooks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "name": "CS101 Fall 2024 Gradebook",
    "semester": "Fall",
    "year": 2024,
    "assignment_weight": 40.0,
    "exam_weight": 50.0,
    "participation_weight": 10.0,
    "pass_fail_threshold": 60.0,
    "allow_student_view": true
  }'
```

### Get Grading Dashboard
```bash
curl -X GET "http://localhost:9600/grading/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Grade Statistics
```bash
curl -X GET "http://localhost:9600/grading/statistics/course/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Authentication

All endpoints require professor authentication. Professors can only access and modify grades, assignments, and exams for their own courses.

## Error Handling

The module includes comprehensive error handling:
- 401 Unauthorized - Invalid or missing authentication token
- 403 Forbidden - Professor trying to access restricted information
- 404 Not Found - Assignment, exam, grade, or gradebook not found
- 400 Bad Request - Invalid request data or validation errors

## Testing

### Unit Tests
- `tests/unit/test_grading_assessment_models.py` - Tests for database models
- `tests/unit/test_grading_assessment_service.py` - Tests for business logic

### Running Tests
```bash
# Run unit tests
python -m pytest tests/unit/test_grading_assessment_*.py -v

# Run all grading tests
python -m pytest tests/unit/test_grading_assessment_*.py -v
```

## Sample Data

To initialize sample data for testing:

```bash
python init_grading_assessment_sample_data.py
```

This will create:
- Sample assignments for each course
- Sample exams with scheduling information
- Assignment submissions and grades
- Exam sessions and grades
- Gradebooks with entries
- Grade statistics

## File Structure

```
backend/
├── models/
│   └── grading_assessment.py          # Database models
├── schemas/
│   └── grading_assessment_schemas.py  # Pydantic schemas
├── repositories/
│   └── grading_assessment_repository.py # Data access layer
├── services/
│   └── grading_assessment_service.py  # Business logic layer
├── controllers/
│   └── grading_assessment_controller.py # API endpoints
└── main.py                             # Updated with new router

tests/
├── unit/
│   ├── test_grading_assessment_models.py
│   └── test_grading_assessment_service.py

init_grading_assessment_sample_data.py  # Sample data initialization
GRADING_ASSESSMENT_GUIDE.md             # This documentation
```

## Key Features

### Assignment Management
- **Multiple Types**: Support for homework, projects, labs, quizzes, presentations, essays, research
- **Flexible Grading**: Configurable point values and weight percentages
- **Late Policies**: Configurable late submission deadlines and penalties
- **Submission Tracking**: Track submission attempts, file uploads, and feedback
- **Bulk Operations**: Create multiple assignments from templates

### Exam Management
- **Comprehensive Scheduling**: Date, time, duration, and location management
- **Online Support**: Support for online exams with platform integration
- **Proctoring**: Configurable proctoring requirements and software
- **Material Policies**: Define allowed and restricted materials
- **Session Tracking**: Track individual exam sessions and attendance

### Grade Management
- **Flexible Grading**: Support for points, percentages, and letter grades
- **Late Penalties**: Automatic late penalty application
- **Extra Credit**: Support for extra credit points
- **Grade Curves**: Apply curves to entire grade distributions
- **Grade Modifications**: Track and approve grade changes
- **Bulk Operations**: Create and publish multiple grades at once

### Gradebook Management
- **Weighted Grading**: Configurable category weights (assignments, exams, participation)
- **Automatic Calculations**: Automatic grade calculations and letter grade assignment
- **Drop Policies**: Drop lowest assignments or exams
- **Student Tracking**: Track completion rates and identify at-risk students
- **Statistical Analysis**: Comprehensive grade statistics and analytics

### Analytics and Reporting
- **Grade Distribution**: Visual grade distribution reports
- **Performance Analytics**: Assignment and exam performance analytics
- **Student Progress**: Track individual student progress over time
- **Course Statistics**: Comprehensive course-level statistics
- **Risk Identification**: Identify students at academic risk

## Future Enhancements

1. **Rubric Integration** - Advanced rubric-based grading
2. **Peer Review** - Peer review and peer grading capabilities
3. **Plagiarism Detection** - Integration with plagiarism detection services
4. **Grade Export** - Export grades to various formats (CSV, Excel, PDF)
5. **Grade Import** - Import grades from external systems
6. **Automated Grading** - Integration with automated grading systems
7. **Grade Notifications** - Email notifications for grade publications
8. **Grade Appeals** - Student grade appeal process
9. **Grade Analytics** - Advanced analytics and machine learning insights
10. **Integration APIs** - Integration with LMS and other educational systems

## Security Considerations

1. **Data Privacy** - Professors can only access their own course data
2. **Grade Security** - Secure grade storage and transmission
3. **Audit Trail** - Complete audit trail of all grade modifications
4. **Access Control** - Role-based access control for different functions
5. **Data Encryption** - Encrypt sensitive grade information

## Performance Considerations

1. **Database Indexing** - Proper indexes on frequently queried fields
2. **Caching** - Cache frequently accessed grade information
3. **Pagination** - Implement pagination for large datasets
4. **Bulk Operations** - Optimize bulk grade and assignment operations
5. **Query Optimization** - Optimize complex grade calculation queries
