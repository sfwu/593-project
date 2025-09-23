"""
Unit Tests for Pydantic schemas
These are pure unit tests - no external dependencies, no database, no network calls
"""
import pytest
from pydantic import ValidationError
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from schemas.student_schemas import (
    UserLogin, UserRegister, Token, TokenData, UserRole,
    StudentCreate, StudentUpdate, StudentResponse,
    ProfessorCreate, ProfessorUpdate, ProfessorResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    EnrollmentCreate, EnrollmentResponse
)
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate, AcademicRecordResponse,
    TranscriptCreate, TranscriptUpdate, TranscriptResponse,
    AcademicProgressCreate, AcademicProgressUpdate, AcademicProgressResponse,
    SemesterGPACreate, SemesterGPAUpdate, SemesterGPAResponse,
    GPACalculationResponse, TranscriptGenerationResponse,
    GradeStatus, TranscriptStatus
)
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentSubmissionCreate, AssignmentSubmissionUpdate, AssignmentSubmissionResponse,
    ExamCreate, ExamUpdate, ExamResponse,
    ExamSessionCreate, ExamSessionUpdate, ExamSessionResponse,
    GradeCreate, GradeUpdate, GradeResponse,
    GradebookCreate, GradebookUpdate, GradebookResponse,
    GradebookEntryCreate, GradebookEntryUpdate, GradebookEntryResponse,
    GradeStatisticsCreate, GradeStatisticsResponse,
    GradeModificationCreate, GradeModificationUpdate, GradeModificationResponse,
    BulkGradeCreate, BulkAssignmentCreate,
    AssignmentType, ExamType, GradeStatus as GradingGradeStatus, SubmissionStatus
)
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    AttendanceSummaryCreate, AttendanceSummaryUpdate, AttendanceSummaryResponse,
    MessageCreate, MessageUpdate, MessageResponse,
    MessageRecipientCreate, MessageRecipientUpdate, MessageRecipientResponse,
    StudentDirectoryCreate, StudentDirectoryUpdate, StudentDirectoryResponse,
    StudentPerformanceCreate, StudentPerformanceUpdate, StudentPerformanceResponse,
    CommunicationLogCreate, CommunicationLogUpdate, CommunicationLogResponse,
    BulkAttendanceCreate, BulkMessageCreate,
    AttendanceStatus, MessageStatus, MessageType, MessagePriority
)

class TestAuthenticationSchemas:
    """Unit tests for authentication-related schemas"""
    
    def test_user_login_valid(self):
        """Test valid user login schema"""
        login_data = {
            "email": "user@example.com",
            "password": "password123"
        }
        
        login = UserLogin(**login_data)
        assert login.email == "user@example.com"
        assert login.password == "password123"
    
    def test_user_login_invalid_email(self):
        """Test user login with invalid email"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)
    
    def test_user_register_valid(self):
        """Test valid user registration"""
        register_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "role": UserRole.STUDENT
        }
        
        register = UserRegister(**register_data)
        assert register.email == "newuser@example.com"
        assert register.password == "password123"
        assert register.role == UserRole.STUDENT
    
    def test_user_register_password_too_short(self):
        """Test user registration with password too short"""
        register_data = {
            "email": "newuser@example.com",
            "password": "123",  # Too short
            "role": UserRole.STUDENT
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**register_data)
        
        errors = exc_info.value.errors()
        assert any("at least 6 characters" in str(error) for error in errors)
    
    def test_token_schema(self):
        """Test token schema"""
        token_data = {
            "access_token": "fake-jwt-token",
            "token_type": "bearer",
            "user_role": UserRole.PROFESSOR,
            "user_id": 1
        }
        
        token = Token(**token_data)
        assert token.access_token == "fake-jwt-token"
        assert token.token_type == "bearer"
        assert token.user_role == UserRole.PROFESSOR
        assert token.user_id == 1

class TestStudentSchemas:
    """Unit test class for student schemas"""
    
    def test_student_create_valid(self):
        """Test creating valid StudentCreate schema"""
        student_data = {
            "email": "student@example.com",
            "password": "password123",
            "student_id": "STU001",
            "first_name": "John",
            "last_name": "Doe",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        student = StudentCreate(**student_data)
        assert student.email == "student@example.com"
        assert student.password == "password123"
        assert student.student_id == "STU001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.major == "Computer Science"
        assert student.year_level == "Junior"
    
    def test_student_create_minimal(self):
        """Test creating StudentCreate with minimal required fields"""
        student_data = {
            "email": "jane@example.com",
            "password": "password123",
            "student_id": "STU002",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        student = StudentCreate(**student_data)
        assert student.first_name == "Jane"
        assert student.last_name == "Smith"
        assert student.major is None
        assert student.year_level is None
    
    def test_student_update_partial(self):
        """Test StudentUpdate with partial data"""
        update_data = {
            "first_name": "Updated",
            "major": "Mathematics"
        }
        
        update = StudentUpdate(**update_data)
        assert update.first_name == "Updated"
        assert update.major == "Mathematics"
        assert update.last_name is None
    
    def test_student_response(self):
        """Test StudentResponse schema"""
        response_data = {
            "id": 1,
            "student_id": "STU001",
            "first_name": "John",
            "last_name": "Doe",
            "enrollment_date": datetime.now()
        }
        
        response = StudentResponse(**response_data)
        assert response.id == 1
        assert response.student_id == "STU001"

class TestProfessorSchemas:
    """Unit tests for professor schemas"""
    
    def test_professor_create_valid(self):
        """Test valid professor creation"""
        professor_data = {
            "email": "prof@example.com",
            "password": "password123",
            "professor_id": "PROF001",
            "first_name": "Jane",
            "last_name": "Smith",
            "department": "Computer Science",
            "title": "Associate Professor"
        }
        
        professor = ProfessorCreate(**professor_data)
        assert professor.email == "prof@example.com"
        assert professor.professor_id == "PROF001"
        assert professor.department == "Computer Science"
        assert professor.title == "Associate Professor"
    
    def test_professor_update(self):
        """Test professor update schema"""
        update_data = {
            "office_hours": "MWF 2-4 PM",
            "specialization": "Machine Learning"
        }
        
        update = ProfessorUpdate(**update_data)
        assert update.office_hours == "MWF 2-4 PM"
        assert update.specialization == "Machine Learning"
        assert update.first_name is None

class TestCourseSchemas:
    """Unit tests for course schemas"""
    
    def test_course_create_valid(self):
        """Test valid course creation"""
        course_data = {
            "course_code": "CS101",
            "title": "Introduction to Programming",
            "description": "Learn basic programming",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        course = CourseCreate(**course_data)
        assert course.course_code == "CS101"
        assert course.title == "Introduction to Programming"
        assert course.credits == 3
        assert course.year == 2024
    
    def test_course_create_defaults(self):
        """Test course creation with default values"""
        course_data = {
            "course_code": "CS102",
            "title": "Advanced Programming",
            "department": "Computer Science",
            "semester": "Spring 2024",
            "year": 2024
        }
        
        course = CourseCreate(**course_data)
        assert course.credits == 3  # Default value
        assert course.max_enrollment == 30  # Default value
    
    def test_course_update(self):
        """Test course update schema"""
        update_data = {
            "title": "Updated Course Title",
            "max_enrollment": 25
        }
        
        update = CourseUpdate(**update_data)
        assert update.title == "Updated Course Title"
        assert update.max_enrollment == 25
        assert update.description is None
    
    def test_course_response(self):
        """Test course response schema"""
        response_data = {
            "id": 1,
            "course_code": "CS101",
            "title": "Programming",
            "credits": 3,
            "professor_id": 1,
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": True,
            "created_at": datetime.now(),
            "enrolled_count": 15
        }
        
        response = CourseResponse(**response_data)
        assert response.course_code == "CS101"
        assert response.enrolled_count == 15

class TestEnrollmentSchemas:
    """Unit tests for enrollment schemas"""
    
    def test_enrollment_create(self):
        """Test enrollment creation"""
        enrollment_data = {"course_id": 1}
        
        enrollment = EnrollmentCreate(**enrollment_data)
        assert enrollment.course_id == 1
    
    def test_enrollment_response(self):
        """Test enrollment response"""
        course_data = {
            "id": 1,
            "course_code": "CS101",
            "title": "Programming",
            "credits": 3,
            "professor_id": 1,
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": True,
            "created_at": datetime.now()
        }
        
        response_data = {
            "student_id": 1,
            "course_id": 1,
            "enrollment_date": datetime.now(),
            "status": "enrolled",
            "course": course_data
        }
        
        response = EnrollmentResponse(**response_data)
        assert response.student_id == 1
        assert response.status == "enrolled"

# ============================================================================
# ACADEMIC RECORD SCHEMAS TESTS
# ============================================================================

class TestAcademicRecordSchemas:
    """Unit tests for Academic Record schemas"""
    
    def test_academic_record_create_valid(self):
        """Test valid academic record creation"""
        record_data = {
            "course_id": 1,
            "semester": "Fall",
            "year": 2024,
            "letter_grade": "A",
            "numeric_grade": 4.0,
            "percentage_grade": 95.0,
            "credits_earned": 3,
            "credits_attempted": 3,
            "status": GradeStatus.GRADED
        }
        
        record = AcademicRecordCreate(**record_data)
        assert record.course_id == 1
        assert record.semester == "Fall"
        assert record.year == 2024
        assert record.letter_grade == "A"
        assert record.numeric_grade == 4.0
        assert record.percentage_grade == 95.0
        assert record.credits_earned == 3
        assert record.credits_attempted == 3
        assert record.status == GradeStatus.GRADED
    
    def test_academic_record_create_minimal(self):
        """Test academic record creation with minimal data"""
        record_data = {
            "course_id": 1,
            "semester": "Spring",
            "year": 2024
        }
        
        record = AcademicRecordCreate(**record_data)
        assert record.course_id == 1
        assert record.semester == "Spring"
        assert record.year == 2024
        assert record.letter_grade is None
        assert record.numeric_grade is None
        assert record.credits_earned == 0
        assert record.credits_attempted == 0
        assert record.status == GradeStatus.PENDING
    
    def test_academic_record_update(self):
        """Test academic record update"""
        update_data = {
            "letter_grade": "B+",
            "numeric_grade": 3.3,
            "status": GradeStatus.GRADED
        }
        
        update = AcademicRecordUpdate(**update_data)
        assert update.letter_grade == "B+"
        assert update.numeric_grade == 3.3
        assert update.status == GradeStatus.GRADED
        # course_id is not in AcademicRecordUpdate schema
    
    def test_academic_record_response(self):
        """Test academic record response"""
        response_data = {
            "id": 1,
            "student_id": 1,
            "course_id": 1,
            "semester": "Fall",
            "year": 2024,
            "letter_grade": "A",
            "numeric_grade": 4.0,
            "percentage_grade": 95.0,
            "credits_earned": 3,
            "credits_attempted": 3,
            "status": GradeStatus.GRADED,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        response = AcademicRecordResponse(**response_data)
        assert response.id == 1
        assert response.student_id == 1
        assert response.course_id == 1
        assert response.letter_grade == "A"

class TestTranscriptSchemas:
    """Unit tests for Transcript schemas"""
    
    def test_transcript_create_valid(self):
        """Test valid transcript creation"""
        transcript_data = {
            "transcript_type": "official",
            "status": TranscriptStatus.OFFICIAL
        }
        
        transcript = TranscriptCreate(**transcript_data)
        # student_id is not in TranscriptCreate schema
        assert transcript.transcript_type == "official"
        assert transcript.status == TranscriptStatus.OFFICIAL
        # total_credits_earned and cumulative_gpa are not in TranscriptCreate schema
    
    def test_transcript_update(self):
        """Test transcript update"""
        update_data = {
            "status": TranscriptStatus.ARCHIVED,
            "file_path": "/path/to/archived/transcript.pdf"
        }
        
        update = TranscriptUpdate(**update_data)
        assert update.status == TranscriptStatus.ARCHIVED
        assert update.file_path == "/path/to/archived/transcript.pdf"
        # notes and student_id are not in TranscriptUpdate schema

class TestAcademicProgressSchemas:
    """Unit tests for Academic Progress schemas"""
    
    def test_academic_progress_create_valid(self):
        """Test valid academic progress creation"""
        progress_data = {
            "degree_program": "Bachelor of Science in Computer Science",
            "major": "Computer Science",
            "catalog_year": 2022,
            "total_credits_required": 120,
            "major_credits_required": 60
        }
        
        progress = AcademicProgressCreate(**progress_data)
        # student_id is not in AcademicProgressCreate schema
        assert progress.degree_program == "Bachelor of Science in Computer Science"
        assert progress.major == "Computer Science"
        assert progress.catalog_year == 2022
        assert progress.total_credits_required == 120
        # cumulative_gpa is not in AcademicProgressCreate schema
    
    def test_academic_progress_update(self):
        """Test academic progress update"""
        update_data = {
            "total_credits_required": 125,
            "major_credits_required": 65
        }
        
        update = AcademicProgressUpdate(**update_data)
        assert update.total_credits_required == 125
        assert update.major_credits_required == 65
        # total_credits_earned, cumulative_gpa, and student_id are not in AcademicProgressUpdate schema

class TestSemesterGPASchemas:
    """Unit tests for Semester GPA schemas"""
    
    def test_semester_gpa_create_valid(self):
        """Test valid semester GPA creation"""
        gpa_data = {
            "semester": "Fall",
            "year": 2024,
            "semester_gpa": 3.5,
            "credits_earned": 15,
            "credits_attempted": 15,
            "quality_points": 52.5,
            "courses_completed": 5,
            "courses_attempted": 5
        }
        
        gpa = SemesterGPACreate(**gpa_data)
        # student_id is not in SemesterGPACreate schema
        assert gpa.semester == "Fall"
        assert gpa.year == 2024
        assert gpa.semester_gpa == 3.5
        assert gpa.credits_earned == 15
        assert gpa.quality_points == 52.5
    
    def test_semester_gpa_update(self):
        """Test semester GPA update"""
        update_data = {
            "semester_gpa": 3.7,
            "quality_points": 55.5
        }
        
        update = SemesterGPAUpdate(**update_data)
        assert update.semester_gpa == 3.7
        assert update.quality_points == 55.5
        # student_id is not in SemesterGPAUpdate schema

class TestAcademicRecordEnums:
    """Unit tests for Academic Record enums"""
    
    def test_grade_status_enum(self):
        """Test GradeStatus enum values"""
        assert GradeStatus.PENDING == "pending"
        assert GradeStatus.GRADED == "graded"
        assert GradeStatus.INCOMPLETE == "incomplete"
        assert GradeStatus.WITHDRAWN == "withdrawn"
    
    def test_transcript_status_enum(self):
        """Test TranscriptStatus enum values"""
        assert TranscriptStatus.DRAFT == "draft"
        assert TranscriptStatus.OFFICIAL == "official"
        assert TranscriptStatus.ARCHIVED == "archived"

# ============================================================================
# GRADING AND ASSESSMENT SCHEMAS TESTS
# ============================================================================

class TestAssignmentSchemas:
    """Unit tests for Assignment schemas"""
    
    def test_assignment_create_valid(self):
        """Test valid assignment creation"""
        assignment_data = {
            "course_id": 1,
            "title": "Programming Assignment 1",
            "description": "Implement a simple calculator",
            "assignment_type": AssignmentType.HOMEWORK,
            "instructions": "Create a calculator with basic operations",
            "requirements": "Must use Python",
            "total_points": 100.0,
            "weight_percentage": 15.0,
            "due_date": datetime(2024, 12, 31, 23, 59, 59),
            "late_submission_deadline": datetime(2025, 1, 2, 23, 59, 59),
            "late_penalty_percentage": 10.0,
            "allow_late_submissions": True,
            "max_attempts": 3,
            "submission_format": "Python file",
            "file_size_limit": 10
        }
        
        assignment = AssignmentCreate(**assignment_data)
        assert assignment.course_id == 1
        assert assignment.title == "Programming Assignment 1"
        assert assignment.assignment_type == AssignmentType.HOMEWORK
        assert assignment.total_points == 100.0
        assert assignment.weight_percentage == 15.0
        assert assignment.allow_late_submissions == True
        assert assignment.max_attempts == 3
    
    def test_assignment_create_minimal(self):
        """Test assignment creation with minimal data"""
        assignment_data = {
            "course_id": 1,
            "title": "Test Assignment",
            "assignment_type": AssignmentType.PROJECT,
            "total_points": 50.0,
            "weight_percentage": 10.0,
            "due_date": datetime(2024, 12, 31, 23, 59, 59)
        }
        
        assignment = AssignmentCreate(**assignment_data)
        assert assignment.course_id == 1
        assert assignment.title == "Test Assignment"
        assert assignment.assignment_type == AssignmentType.PROJECT
        assert assignment.total_points == 50.0
        assert assignment.weight_percentage == 10.0
        assert assignment.description is None
        assert assignment.allow_late_submissions == True  # Default value is True
        assert assignment.max_attempts == 1
    
    def test_assignment_update(self):
        """Test assignment update"""
        update_data = {
            "title": "Updated Assignment Title",
            "description": "Updated description",
            "total_points": 75.0
        }
        
        update = AssignmentUpdate(**update_data)
        assert update.title == "Updated Assignment Title"
        assert update.description == "Updated description"
        assert update.total_points == 75.0
        # course_id is not in AssignmentUpdate schema

class TestExamSchemas:
    """Unit tests for Exam schemas"""
    
    def test_exam_create_valid(self):
        """Test valid exam creation"""
        from datetime import date, time
        
        exam_data = {
            "course_id": 1,
            "title": "Midterm Exam",
            "description": "Comprehensive midterm examination",
            "exam_type": ExamType.MIDTERM,
            "instructions": "Answer all questions clearly",
            "total_points": 100.0,
            "weight_percentage": 30.0,
            "passing_grade": 60.0,
            "exam_date": date(2024, 11, 15),
            "start_time": time(10, 0),
            "end_time": time(12, 0),
            "duration_minutes": 120,
            "location": "Room 101",
            "is_online": False,
            "proctoring_required": True,
            "allowed_materials": "Calculator, Notes",
            "restricted_materials": "No phones, No internet"
        }
        
        exam = ExamCreate(**exam_data)
        assert exam.course_id == 1
        assert exam.title == "Midterm Exam"
        assert exam.exam_type == ExamType.MIDTERM
        assert exam.total_points == 100.0
        assert exam.weight_percentage == 30.0
        assert exam.passing_grade == 60.0
        assert exam.exam_date == date(2024, 11, 15)
        assert exam.start_time == time(10, 0)
        assert exam.end_time == time(12, 0)
        assert exam.is_online == False
        assert exam.proctoring_required == True
    
    def test_exam_update(self):
        """Test exam update"""
        update_data = {
            "title": "Updated Exam Title",
            "location": "Room 201",
            "is_online": True
        }
        
        update = ExamUpdate(**update_data)
        assert update.title == "Updated Exam Title"
        assert update.location == "Room 201"
        assert update.is_online == True
        # course_id is not in ExamUpdate schema

class TestGradeSchemas:
    """Unit tests for Grade schemas"""
    
    def test_grade_create_valid(self):
        """Test valid grade creation"""
        grade_data = {
            "student_id": 1,
            "course_id": 1,
            "points_earned": 85.0,
            "points_possible": 100.0,
            "percentage": 85.0,
            "letter_grade": "B",
            "grade_status": GradingGradeStatus.PUBLISHED,
            "is_late": False,
            "late_penalty_applied": 0.0,
            "extra_credit": 0.0,
            "curve_adjustment": 0.0,
            "professor_comments": "Good work overall",
            "detailed_feedback": "Well-structured code with minor improvements needed"
        }
        
        grade = GradeCreate(**grade_data)
        assert grade.student_id == 1
        assert grade.course_id == 1
        assert grade.points_earned == 85.0
        assert grade.points_possible == 100.0
        assert grade.percentage == 85.0
        assert grade.letter_grade == "B"
        assert grade.grade_status == GradingGradeStatus.PUBLISHED
        assert grade.is_late == False
    
    def test_grade_update(self):
        """Test grade update"""
        update_data = {
            "points_earned": 90.0,
            "percentage": 90.0,
            "letter_grade": "A-",
            "professor_comments": "Excellent work!"
        }
        
        update = GradeUpdate(**update_data)
        assert update.points_earned == 90.0
        assert update.percentage == 90.0
        assert update.letter_grade == "A-"
        assert update.professor_comments == "Excellent work!"
        # student_id is not in GradeUpdate schema

class TestGradebookSchemas:
    """Unit tests for Gradebook schemas"""
    
    def test_gradebook_create_valid(self):
        """Test valid gradebook creation"""
        gradebook_data = {
            "course_id": 1,
            "name": "CS101 Fall 2024 Gradebook",
            "description": "Gradebook for Introduction to Computer Science",
            "semester": "Fall",
            "year": 2024,
            "grading_scheme": '{"A": 90, "B": 80, "C": 70, "D": 60}',
            "letter_grade_scale": '{"A+": 97, "A": 93, "A-": 90}',
            "pass_fail_threshold": 60.0,
            "drop_lowest_assignments": 1,
            "drop_lowest_exams": 0,
            "curve_enabled": False,
            "curve_percentage": 0.0,
            "assignment_weight": 40.0,
            "exam_weight": 50.0,
            "participation_weight": 10.0,
            "allow_student_view": True
        }
        
        gradebook = GradebookCreate(**gradebook_data)
        assert gradebook.course_id == 1
        assert gradebook.name == "CS101 Fall 2024 Gradebook"
        assert gradebook.semester == "Fall"
        assert gradebook.year == 2024
        assert gradebook.pass_fail_threshold == 60.0
        assert gradebook.assignment_weight == 40.0
        assert gradebook.exam_weight == 50.0
        assert gradebook.participation_weight == 10.0
        assert gradebook.allow_student_view == True
    
    def test_gradebook_update(self):
        """Test gradebook update"""
        update_data = {
            "name": "Updated Gradebook Name",
            "allow_student_view": False,
            "curve_enabled": True,
            "curve_percentage": 5.0
        }
        
        update = GradebookUpdate(**update_data)
        assert update.name == "Updated Gradebook Name"
        assert update.allow_student_view == False
        assert update.curve_enabled == True
        assert update.curve_percentage == 5.0
        # course_id is not in GradebookUpdate schema

class TestGradingAssessmentEnums:
    """Unit tests for Grading and Assessment enums"""
    
    def test_assignment_type_enum(self):
        """Test AssignmentType enum values"""
        assert AssignmentType.HOMEWORK == "homework"
        assert AssignmentType.PROJECT == "project"
        assert AssignmentType.LAB == "lab"
        assert AssignmentType.QUIZ == "quiz"
        assert AssignmentType.PRESENTATION == "presentation"
        assert AssignmentType.ESSAY == "essay"
        assert AssignmentType.RESEARCH == "research"
        assert AssignmentType.OTHER == "other"
    
    def test_exam_type_enum(self):
        """Test ExamType enum values"""
        assert ExamType.MIDTERM == "midterm"
        assert ExamType.FINAL == "final"
        assert ExamType.QUIZ == "quiz"
        assert ExamType.POP_QUIZ == "pop_quiz"
        assert ExamType.PRACTICAL == "practical"
        assert ExamType.ORAL == "oral"
        assert ExamType.WRITTEN == "written"
        assert ExamType.ONLINE == "online"
    
    def test_grade_status_enum(self):
        """Test GradeStatus enum values"""
        assert GradingGradeStatus.DRAFT == "draft"
        assert GradingGradeStatus.PUBLISHED == "published"
        assert GradingGradeStatus.LATE == "late"
        assert GradingGradeStatus.EXEMPT == "exempt"
        assert GradingGradeStatus.INCOMPLETE == "incomplete"
        assert GradingGradeStatus.MISSING == "missing"
    
    def test_submission_status_enum(self):
        """Test SubmissionStatus enum values"""
        assert SubmissionStatus.NOT_SUBMITTED == "not_submitted"
        assert SubmissionStatus.SUBMITTED == "submitted"
        assert SubmissionStatus.LATE == "late"
        assert SubmissionStatus.GRADED == "graded"
        assert SubmissionStatus.RETURNED == "returned"

# ============================================================================
# STUDENT INFORMATION MANAGEMENT SCHEMAS TESTS
# ============================================================================

class TestAttendanceSchemas:
    """Unit tests for Attendance schemas"""
    
    def test_attendance_create_valid(self):
        """Test valid attendance creation"""
        attendance_data = {
            "student_id": 1,
            "course_id": 1,
            "attendance_date": datetime.now(),
            "status": AttendanceStatus.PRESENT,
            "notes": "Good participation",
            "late_minutes": 0,
            "session_topic": "Introduction to Programming",
            "session_duration": 90
        }
        
        attendance = AttendanceCreate(**attendance_data)
        assert attendance.student_id == 1
        assert attendance.course_id == 1
        assert attendance.status == AttendanceStatus.PRESENT
        assert attendance.notes == "Good participation"
        assert attendance.late_minutes == 0
        assert attendance.session_topic == "Introduction to Programming"
        assert attendance.session_duration == 90
    
    def test_attendance_create_minimal(self):
        """Test attendance creation with minimal data"""
        attendance_data = {
            "student_id": 1,
            "course_id": 1,
            "attendance_date": datetime.now(),
            "status": AttendanceStatus.ABSENT
        }
        
        attendance = AttendanceCreate(**attendance_data)
        assert attendance.student_id == 1
        assert attendance.course_id == 1
        assert attendance.status == AttendanceStatus.ABSENT
        assert attendance.notes is None
        assert attendance.late_minutes == 0
        assert attendance.session_topic is None
    
    def test_attendance_update(self):
        """Test attendance update"""
        update_data = {
            "status": AttendanceStatus.LATE,
            "late_minutes": 15,
            "notes": "Student arrived late"
        }
        
        update = AttendanceUpdate(**update_data)
        assert update.status == AttendanceStatus.LATE
        assert update.late_minutes == 15
        assert update.notes == "Student arrived late"
        # student_id is not in AttendanceUpdate schema

class TestMessageSchemas:
    """Unit tests for Message schemas"""
    
    def test_message_create_valid(self):
        """Test valid message creation"""
        message_data = {
            "course_id": 1,
            "subject": "Assignment Due Date",
            "content": "Please remember that the assignment is due next week.",
            "message_type": MessageType.ASSIGNMENT,
            "priority": MessagePriority.HIGH,
            "is_broadcast": True
        }
        
        message = MessageCreate(**message_data)
        # sender_id is not in MessageCreate schema
        assert message.course_id == 1
        assert message.subject == "Assignment Due Date"
        assert message.content == "Please remember that the assignment is due next week."
        assert message.message_type == MessageType.ASSIGNMENT
        assert message.priority == MessagePriority.HIGH
        assert message.is_broadcast == True
        # status is not in MessageCreate schema
    
    def test_message_create_minimal(self):
        """Test message creation with minimal data"""
        message_data = {
            "subject": "Test Message",
            "content": "This is a test message.",
            "message_type": MessageType.GENERAL,
            "priority": MessagePriority.NORMAL
        }
        
        message = MessageCreate(**message_data)
        # sender_id is not in MessageCreate schema
        assert message.subject == "Test Message"
        assert message.content == "This is a test message."
        assert message.message_type == MessageType.GENERAL
        assert message.priority == MessagePriority.NORMAL
        assert message.course_id is None
        assert message.is_broadcast == False
        # status is not in MessageCreate schema
    
    def test_message_update(self):
        """Test message update"""
        update_data = {
            "subject": "Updated Subject",
            "content": "Updated content",
            "priority": MessagePriority.HIGH
        }
        
        update = MessageUpdate(**update_data)
        assert update.subject == "Updated Subject"
        assert update.content == "Updated content"
        assert update.priority == MessagePriority.HIGH
        # status and sender_id are not in MessageUpdate schema

class TestStudentDirectorySchemas:
    """Unit tests for Student Directory schemas"""
    
    def test_student_directory_create_valid(self):
        """Test valid student directory creation"""
        directory_data = {
            "student_id": 1,
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "emergency_contact": "Jane Doe",
            "emergency_phone": "098-765-4321",
            "address": "123 Main St, City, State",
            "major": "Computer Science",
            "year_level": "Junior",
            "gpa": 3.5,
            "enrollment_status": "active",
            "advisor_id": 1,
            "notes": "Excellent student",
            "show_contact_info": True,
            "show_academic_info": True
        }
        
        directory = StudentDirectoryCreate(**directory_data)
        assert directory.student_id == 1
        assert directory.email == "john.doe@example.com"
        assert directory.phone == "123-456-7890"
        assert directory.emergency_contact == "Jane Doe"
        assert directory.major == "Computer Science"
        assert directory.year_level == "Junior"
        assert directory.gpa == 3.5
        assert directory.enrollment_status == "active"
        assert directory.advisor_id == 1
        assert directory.show_contact_info == True
        assert directory.show_academic_info == True
    
    def test_student_directory_update(self):
        """Test student directory update"""
        update_data = {
            "phone": "987-654-3210",
            "gpa": 3.7,
            "notes": "Updated notes"
        }
        
        update = StudentDirectoryUpdate(**update_data)
        assert update.phone == "987-654-3210"
        assert update.gpa == 3.7
        assert update.notes == "Updated notes"
        # student_id is not in StudentDirectoryUpdate schema

class TestStudentPerformanceSchemas:
    """Unit tests for Student Performance schemas"""
    
    def test_student_performance_create_valid(self):
        """Test valid student performance creation"""
        performance_data = {
            "student_id": 1,
            "course_id": 1,
            "current_grade": 85.5,
            "participation_score": 90.0,
            "attendance_score": 95.0,
            "assignment_average": 80.0,
            "exam_average": 90.0,
            "is_at_risk": False,
            "risk_factors": "[]",
            "improvement_areas": "[]",
            "professor_notes": "Good performance overall"
        }
        
        performance = StudentPerformanceCreate(**performance_data)
        assert performance.student_id == 1
        assert performance.course_id == 1
        assert performance.current_grade == 85.5
        assert performance.participation_score == 90.0
        assert performance.attendance_score == 95.0
        assert performance.assignment_average == 80.0
        assert performance.exam_average == 90.0
        assert performance.is_at_risk == False
        assert performance.professor_notes == "Good performance overall"
    
    def test_student_performance_update(self):
        """Test student performance update"""
        update_data = {
            "current_grade": 88.0,
            "is_at_risk": True,
            "professor_notes": "Needs improvement"
        }
        
        update = StudentPerformanceUpdate(**update_data)
        assert update.current_grade == 88.0
        assert update.is_at_risk == True
        assert update.professor_notes == "Needs improvement"
        # student_id is not in StudentPerformanceUpdate schema

class TestCommunicationLogSchemas:
    """Unit tests for Communication Log schemas"""
    
    def test_communication_log_create_valid(self):
        """Test valid communication log creation"""
        log_data = {
            "professor_id": 1,
            "student_id": 1,
            "course_id": 1,
            "communication_type": "email",
            "subject": "Grade Discussion",
            "content": "Let's discuss your recent assignment grade.",
            "direction": "sent",
            "requires_follow_up": True,
            "follow_up_date": datetime.now()
        }
        
        log = CommunicationLogCreate(**log_data)
        assert log.professor_id == 1
        assert log.student_id == 1
        assert log.course_id == 1
        assert log.communication_type == "email"
        assert log.subject == "Grade Discussion"
        assert log.content == "Let's discuss your recent assignment grade."
        assert log.direction == "sent"
        assert log.requires_follow_up == True
    
    def test_communication_log_update(self):
        """Test communication log update"""
        update_data = {
            "communication_type": "meeting",
            "requires_follow_up": False,
            "follow_up_notes": "Meeting completed"
        }
        
        update = CommunicationLogUpdate(**update_data)
        assert update.communication_type == "meeting"
        assert update.requires_follow_up == False
        assert update.follow_up_notes == "Meeting completed"
        # notes and professor_id are not in CommunicationLogUpdate schema

class TestStudentInformationEnums:
    """Unit tests for Student Information Management enums"""
    
    def test_attendance_status_enum(self):
        """Test AttendanceStatus enum values"""
        assert AttendanceStatus.PRESENT == "present"
        assert AttendanceStatus.ABSENT == "absent"
        assert AttendanceStatus.LATE == "late"
        assert AttendanceStatus.EXCUSED == "excused"
        assert AttendanceStatus.TARDY == "tardy"
    
    def test_message_status_enum(self):
        """Test MessageStatus enum values"""
        assert MessageStatus.DRAFT == "draft"
        assert MessageStatus.SENT == "sent"
        assert MessageStatus.DELIVERED == "delivered"
        assert MessageStatus.READ == "read"
        assert MessageStatus.ARCHIVED == "archived"
    
    def test_message_type_enum(self):
        """Test MessageType enum values"""
        assert MessageType.ANNOUNCEMENT == "announcement"
        assert MessageType.REMINDER == "reminder"
        assert MessageType.ASSIGNMENT == "assignment"
        assert MessageType.GRADE == "grade"
        assert MessageType.GENERAL == "general"
        assert MessageType.URGENT == "urgent"
    
    def test_message_priority_enum(self):
        """Test MessagePriority enum values"""
        assert MessagePriority.LOW == "low"
        assert MessagePriority.NORMAL == "normal"
        assert MessagePriority.HIGH == "high"
        assert MessagePriority.URGENT == "urgent"

class TestSchemaValidation:
    """Unit test class for schema validation edge cases"""
    
    def test_email_validation(self):
        """Test email validation across schemas"""
        invalid_emails = ["invalid-email", "@example.com", "user@", ""]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                UserLogin(email=invalid_email, password="password")
    
    def test_password_length_validation(self):
        """Test password length validation"""
        short_passwords = ["", "1", "12", "123", "1234", "12345"]
        
        for short_password in short_passwords:
            with pytest.raises(ValidationError):
                UserRegister(
                    email="test@example.com",
                    password=short_password,
                    role=UserRole.STUDENT
                )
    
    def test_role_validation(self):
        """Test user role validation"""
        valid_roles = ["student", "professor"]
        
        for role in valid_roles:
            register = UserRegister(
                email="test@example.com",
                password="password123",
                role=role
            )
            assert register.role in [UserRole.STUDENT, UserRole.PROFESSOR]
    
    def test_credits_validation(self):
        """Test course credits validation"""
        course_data = {
            "course_code": "CS101",
            "title": "Programming",
            "department": "CS",
            "semester": "Fall 2024",
            "year": 2024,
            "credits": -1  # Invalid negative credits
        }
        
        # This should still pass as we don't have custom validation for negative credits
        # But in a real application, you might want to add such validation
        course = CourseCreate(**course_data)
        assert course.credits == -1

if __name__ == "__main__":
    pytest.main([__file__])
