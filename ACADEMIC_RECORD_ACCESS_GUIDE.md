# Academic Record Access Module

## Overview

The Academic Record Access module provides comprehensive functionality for students to access and manage their academic records, including grades, transcripts, GPA calculations, and academic progress tracking.

## Features

### 1. View Grades
- Access grades for completed courses
- Filter grades by semester, year, and status
- View detailed grade information including letter grades, numeric grades, and percentage grades
- Track grade history and trends

### 2. Transcript Generation
- Generate official academic transcripts
- Download transcript files
- View transcript history
- Support for both official and unofficial transcripts

### 3. GPA Calculation
- Real-time GPA tracking
- Cumulative GPA calculation
- Major-specific GPA calculation
- Semester-wise GPA breakdown
- Current semester GPA tracking

### 4. Academic Progress
- Track degree requirements and completion status
- Monitor progress toward graduation
- View completion percentages
- Track major and general education requirements
- Academic warnings and alerts

## API Endpoints

### Grade Management
- `GET /academic-records/grades` - Get student grades with optional filtering
- `GET /academic-records/grades/{record_id}` - Get detailed grade information
- `PUT /academic-records/grades/{record_id}` - Update grade notes (students can only update their own notes)

### GPA Calculation
- `GET /academic-records/gpa` - Get comprehensive GPA calculation
- `GET /academic-records/gpa/semester-breakdown` - Get semester-wise GPA breakdown
- `GET /academic-records/gpa/current-semester` - Get current semester GPA

### Transcript Management
- `GET /academic-records/transcripts` - List all transcripts for student
- `POST /academic-records/transcripts/generate` - Generate new transcript
- `GET /academic-records/transcripts/{transcript_id}/download` - Download transcript file

### Academic Progress
- `GET /academic-records/progress` - Get academic progress information
- `GET /academic-records/progress/summary` - Get comprehensive progress summary
- `PUT /academic-records/progress` - Update academic progress (limited fields for students)

### Dashboard and Summary
- `GET /academic-records/dashboard` - Get academic dashboard with key metrics
- `GET /academic-records/academic-summary` - Get comprehensive academic summary
- `GET /academic-records/grade-history` - Get complete grade history

## Database Models

### AcademicRecord
Stores individual course grades and academic records.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `course_id` - Foreign key to Course
- `semester` - Semester (e.g., "Fall 2024")
- `year` - Academic year
- `letter_grade` - Letter grade (A, B+, B, etc.)
- `numeric_grade` - Numeric grade (4.0, 3.5, etc.)
- `percentage_grade` - Percentage grade (95.5, 87.2, etc.)
- `credits_earned` - Credits earned for the course
- `credits_attempted` - Credits attempted for the course
- `status` - Grade status (pending, graded, incomplete, withdrawn)
- `grade_date` - Date when grade was assigned
- `professor_notes` - Notes from professor
- `student_notes` - Notes from student

### Transcript
Stores official academic transcripts.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `transcript_type` - Type of transcript (official, unofficial)
- `status` - Transcript status (draft, official, archived)
- `generated_date` - Date when transcript was generated
- `requested_date` - Date when transcript was requested
- `total_credits_earned` - Total credits earned
- `total_credits_attempted` - Total credits attempted
- `cumulative_gpa` - Cumulative GPA at time of generation
- `major_gpa` - Major-specific GPA
- `file_path` - Path to generated transcript file
- `file_hash` - Hash for file integrity verification

### AcademicProgress
Tracks degree requirements and completion status.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `degree_program` - Degree program name
- `major` - Student's major
- `concentration` - Optional concentration/specialization
- `catalog_year` - Academic year when student started
- `total_credits_required` - Total credits required for degree
- `major_credits_required` - Major-specific credits required
- `general_education_credits_required` - General education credits required
- `elective_credits_required` - Elective credits required
- `total_credits_earned` - Total credits earned
- `major_credits_earned` - Major-specific credits earned
- `general_education_credits_earned` - General education credits earned
- `elective_credits_earned` - Elective credits earned
- `cumulative_gpa` - Cumulative GPA
- `major_gpa` - Major-specific GPA
- `semester_gpa` - Current semester GPA
- `is_on_track` - Whether student is on track for graduation
- `expected_graduation_date` - Expected graduation date
- `actual_graduation_date` - Actual graduation date
- `completed_requirements` - JSON list of completed requirements
- `remaining_requirements` - JSON list of remaining requirements
- `warnings` - JSON list of academic warnings

### SemesterGPA
Tracks semester-wise GPA calculations.

**Fields:**
- `id` - Primary key
- `student_id` - Foreign key to Student
- `semester` - Semester (e.g., "Fall")
- `year` - Academic year
- `semester_gpa` - GPA for the semester
- `credits_earned` - Credits earned in the semester
- `credits_attempted` - Credits attempted in the semester
- `quality_points` - Quality points for the semester
- `courses_completed` - Number of courses completed
- `courses_attempted` - Number of courses attempted

## Usage Examples

### Get Student Grades
```bash
curl -X GET "http://localhost:9600/academic-records/grades" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get GPA Calculation
```bash
curl -X GET "http://localhost:9600/academic-records/gpa" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Generate Transcript
```bash
curl -X POST "http://localhost:9600/academic-records/transcripts/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_type": "official",
    "include_incomplete": false,
    "include_withdrawn": false
  }'
```

### Get Academic Dashboard
```bash
curl -X GET "http://localhost:9600/academic-records/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Authentication

All endpoints require student authentication. Students can only access their own academic records.

## Error Handling

The module includes comprehensive error handling:
- 401 Unauthorized - Invalid or missing authentication token
- 403 Forbidden - Student trying to access/modify restricted fields
- 404 Not Found - Academic record, transcript, or progress not found
- 400 Bad Request - Invalid request data or validation errors

## Testing

### Unit Tests
- `tests/unit/test_academic_record_models.py` - Tests for database models
- `tests/unit/test_academic_record_service.py` - Tests for business logic

### Integration Tests
- `tests/integration/test_academic_record_integration.py` - Tests for API endpoints

### Running Tests
```bash
# Run unit tests
python -m pytest tests/unit/test_academic_record_*.py -v

# Run integration tests
python -m pytest tests/integration/test_academic_record_integration.py -v

# Run all academic record tests
python -m pytest tests/unit/test_academic_record_*.py tests/integration/test_academic_record_integration.py -v
```

## Sample Data

To initialize sample data for testing:

```bash
python init_academic_record_sample_data.py
```

This will create:
- Sample academic records (grades) for existing students
- Academic progress records
- Semester GPA records
- Sample transcripts

## File Structure

```
backend/
├── models/
│   └── academic_record.py          # Database models
├── schemas/
│   └── academic_record_schemas.py  # Pydantic schemas
├── repositories/
│   └── academic_record_repository.py # Data access layer
├── services/
│   └── academic_record_service.py  # Business logic layer
├── controllers/
│   └── academic_record_controller.py # API endpoints
└── main.py                         # Updated with new router

tests/
├── unit/
│   ├── test_academic_record_models.py
│   └── test_academic_record_service.py
└── integration/
    └── test_academic_record_integration.py

init_academic_record_sample_data.py  # Sample data initialization
ACADEMIC_RECORD_ACCESS_GUIDE.md     # This documentation
```

## Future Enhancements

1. **PDF Transcript Generation** - Generate professional PDF transcripts
2. **Grade Analytics** - Advanced analytics and trends
3. **Academic Alerts** - Automated alerts for academic issues
4. **Degree Audit** - Automated degree requirement checking
5. **Grade Prediction** - Predict final grades based on current performance
6. **Academic Planning** - Course planning and scheduling assistance
7. **Mobile App Support** - Optimized endpoints for mobile applications
8. **Bulk Operations** - Support for bulk grade imports and updates
9. **Audit Trail** - Track all changes to academic records
10. **Integration** - Integration with external systems (LMS, SIS)

## Security Considerations

1. **Data Privacy** - Students can only access their own records
2. **File Security** - Transcript files are stored securely with integrity verification
3. **Input Validation** - All inputs are validated and sanitized
4. **Rate Limiting** - Consider implementing rate limiting for transcript generation
5. **Audit Logging** - Log all access to sensitive academic records

## Performance Considerations

1. **Database Indexing** - Proper indexes on frequently queried fields
2. **Caching** - Consider caching GPA calculations and progress summaries
3. **Pagination** - Implement pagination for large grade histories
4. **File Storage** - Optimize transcript file storage and retrieval
5. **Query Optimization** - Optimize complex queries for better performance

