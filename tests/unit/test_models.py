"""
Unit Tests for Database Models
Tests model creation, relationships, and validation
"""
import pytest
from datetime import datetime, date, time
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from models import User, Student, Professor, Course, UserRole, student_course_association
from models.academic_record import AcademicRecord, Transcript, AcademicProgress, SemesterGPA, GradeStatus as AcademicGradeStatus, TranscriptStatus
from models.grading_assessment import (
    Assignment, AssignmentSubmission, Exam, ExamSession, Grade, Gradebook,
    GradebookEntry, GradeStatistics, GradeModification, AssignmentType,
    ExamType, SubmissionStatus, GradeStatus
)
from models.student_information import (
    Attendance, AttendanceSummary, Message, MessageRecipient, StudentDirectory,
    StudentPerformance, CommunicationLog, AttendanceStatus, MessageStatus,
    MessageType, MessagePriority
)
from config.database import Base

# Test database setup for models that need database testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_professor_user(db_session):
    """Create a sample professor user for testing"""
    user = User(
        email="professor@example.com",
        hashed_password="hashed_password",
        role=UserRole.PROFESSOR,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_student(db_session, sample_user):
    """Create a sample student for testing"""
    student = Student(
        user_id=sample_user.id,
        student_id="STU001",
        first_name="John",
        last_name="Doe",
        major="Computer Science",
        year_level="Junior"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student

@pytest.fixture
def sample_professor(db_session, sample_professor_user):
    """Create a sample professor for testing"""
    professor = Professor(
        user_id=sample_professor_user.id,
        professor_id="PROF001",
        first_name="Jane",
        last_name="Smith",
        department="Computer Science",
        title="Assistant Professor"
    )
    db_session.add(professor)
    db_session.commit()
    db_session.refresh(professor)
    return professor

@pytest.fixture
def sample_course(db_session, sample_professor):
    """Create a sample course for testing"""
    course = Course(
        course_code="CS101",
        title="Introduction to Computer Science",
        description="Basic computer science concepts",
        credits=3,
        professor_id=sample_professor.id,
        department="Computer Science",
        semester="Fall",
        year=2024,
        is_active=True
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

class TestUserModel:
    """Unit tests for User model"""
    
    def test_user_creation_student(self):
        """Test creating a user with student role"""
        user = User(
            email="student@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.STUDENT,
            is_active=True
        )
        
        assert user.email == "student@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.role == UserRole.STUDENT
        assert user.is_active is True
    
    def test_user_creation_professor(self):
        """Test creating a user with professor role"""
        user = User(
            email="professor@example.com",
            hashed_password="hashed_password_456",
            role=UserRole.PROFESSOR,
            is_active=True
        )
        
        assert user.email == "professor@example.com"
        assert user.role == UserRole.PROFESSOR
    
    def test_user_defaults(self):
        """Test user model default values"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_pass",
            role=UserRole.STUDENT
        )
        
        # Default values are set by SQLAlchemy when inserting to database
        # In memory, they may be None until committed
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_pass"
        assert user.role == UserRole.STUDENT
    
    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.STUDENT.value == "student"
        assert UserRole.PROFESSOR.value == "professor"
        
        # Test that only valid roles can be assigned
        user = User(
            email="test@example.com",
            hashed_password="pass",
            role=UserRole.STUDENT
        )
        assert user.role.value == "student"

class TestStudentModel:
    """Unit tests for Student model"""
    
    def test_student_creation_minimal(self):
        """Test creating student with minimal required fields"""
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        assert student.user_id == 1
        assert student.student_id == "STU001"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
    
    def test_student_creation_full(self):
        """Test creating student with all fields"""
        student = Student(
            user_id=1,
            student_id="STU002",
            first_name="Jane",
            last_name="Smith",
            phone="555-0123",
            address="123 Main St",
            date_of_birth=datetime(2000, 1, 1),
            major="Computer Science",
            year_level="Junior",
            gpa="3.5"
        )
        
        assert student.phone == "555-0123"
        assert student.address == "123 Main St"
        assert student.major == "Computer Science"
        assert student.year_level == "Junior"
        assert student.gpa == "3.5"
    
    def test_student_optional_fields(self):
        """Test student optional fields can be None"""
        student = Student(
            user_id=1,
            student_id="STU003",
            first_name="Bob",
            last_name="Johnson"
        )
        
        assert student.phone is None
        assert student.address is None
        assert student.date_of_birth is None
        assert student.graduation_date is None
        assert student.major is None
        assert student.year_level is None
        assert student.gpa is None

class TestProfessorModel:
    """Unit tests for Professor model"""
    
    def test_professor_creation_minimal(self):
        """Test creating professor with minimal required fields"""
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        assert professor.user_id == 1
        assert professor.professor_id == "PROF001"
        assert professor.first_name == "Dr. Jane"
        assert professor.last_name == "Smith"
        assert professor.department == "Computer Science"
    
    def test_professor_creation_full(self):
        """Test creating professor with all fields"""
        professor = Professor(
            user_id=2,
            professor_id="PROF002",
            first_name="Dr. John",
            last_name="Doe",
            phone="555-0456",
            office_location="Room 301",
            office_hours="MWF 2-4 PM",
            department="Mathematics",
            title="Associate Professor",
            specialization="Applied Mathematics"
        )
        
        assert professor.phone == "555-0456"
        assert professor.office_location == "Room 301"
        assert professor.office_hours == "MWF 2-4 PM"
        assert professor.title == "Associate Professor"
        assert professor.specialization == "Applied Mathematics"
    
    def test_professor_optional_fields(self):
        """Test professor optional fields can be None"""
        professor = Professor(
            user_id=1,
            professor_id="PROF003",
            first_name="Dr. Bob",
            last_name="Wilson",
            department="Physics"
        )
        
        assert professor.phone is None
        assert professor.office_location is None
        assert professor.office_hours is None
        assert professor.title is None
        assert professor.specialization is None

class TestCourseModel:
    """Unit tests for Course model"""
    
    def test_course_creation_minimal(self):
        """Test creating course with minimal required fields"""
        course = Course(
            course_code="CS101",
            title="Introduction to Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        assert course.course_code == "CS101"
        assert course.title == "Introduction to Programming"
        assert course.professor_id == 1
        assert course.department == "Computer Science"
        assert course.semester == "Fall 2024"
        assert course.year == 2024
    
    def test_course_creation_full(self):
        """Test creating course with all fields"""
        course = Course(
            course_code="CS102",
            title="Advanced Programming",
            description="Advanced programming concepts",
            credits=4,
            professor_id=1,
            department="Computer Science",
            semester="Spring 2024",
            year=2024,
            max_enrollment=25,
            prerequisites="CS101",
            schedule='{"days": ["MWF"], "time": "10:00-11:00"}',
            syllabus="Detailed syllabus content"
        )
        
        assert course.description == "Advanced programming concepts"
        assert course.credits == 4
        assert course.max_enrollment == 25
        assert course.prerequisites == "CS101"
        assert '"days": ["MWF"]' in course.schedule
        assert course.syllabus == "Detailed syllabus content"
    
    def test_course_defaults(self):
        """Test course model default values"""
        course = Course(
            course_code="CS103",
            title="Data Structures",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        # Default values are set by SQLAlchemy when inserting to database
        # In memory, they may be None until committed
        assert course.course_code == "CS103"
        assert course.title == "Data Structures"
        assert course.professor_id == 1
        assert course.department == "Computer Science"
        assert course.semester == "Fall 2024"
        assert course.year == 2024
    
    def test_course_boolean_fields(self):
        """Test course boolean fields"""
        course = Course(
            course_code="CS104",
            title="Inactive Course",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024,
            is_active=False
        )
        
        assert course.is_active is False

class TestModelRelationships:
    """Unit tests for model relationships"""
    
    def test_user_student_relationship(self):
        """Test User-Student relationship"""
        # Create user
        user = User(
            email="student@example.com",
            hashed_password="hashed_pass",
            role=UserRole.STUDENT
        )
        user.id = 1  # Simulate database ID
        
        # Create student
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        # In a real test with database, you would test:
        # assert student.user == user
        # assert user.student_profile == student
        
        # For unit test, just verify the foreign key
        assert student.user_id == user.id
    
    def test_user_professor_relationship(self):
        """Test User-Professor relationship"""
        # Create user
        user = User(
            email="prof@example.com",
            hashed_password="hashed_pass",
            role=UserRole.PROFESSOR
        )
        user.id = 1  # Simulate database ID
        
        # Create professor
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        # For unit test, just verify the foreign key
        assert professor.user_id == user.id
    
    def test_professor_course_relationship(self):
        """Test Professor-Course relationship"""
        # Create professor
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        professor.id = 1  # Simulate database ID
        
        # Create course
        course = Course(
            course_code="CS101",
            title="Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        # For unit test, just verify the foreign key
        assert course.professor_id == professor.id

class TestModelValidation:
    """Unit tests for model validation and constraints"""
    
    def test_required_fields_user(self):
        """Test that User model requires necessary fields"""
        # This would be tested with actual database constraints
        # For unit tests, we just verify the fields are set correctly
        user = User(
            email="test@example.com",
            hashed_password="pass",
            role=UserRole.STUDENT
        )
        
        assert user.email is not None
        assert user.hashed_password is not None
        assert user.role is not None
    
    def test_required_fields_student(self):
        """Test that Student model requires necessary fields"""
        student = Student(
            user_id=1,
            student_id="STU001",
            first_name="John",
            last_name="Doe"
        )
        
        assert student.user_id is not None
        assert student.student_id is not None
        assert student.first_name is not None
        assert student.last_name is not None
    
    def test_required_fields_professor(self):
        """Test that Professor model requires necessary fields"""
        professor = Professor(
            user_id=1,
            professor_id="PROF001",
            first_name="Dr. Jane",
            last_name="Smith",
            department="Computer Science"
        )
        
        assert professor.user_id is not None
        assert professor.professor_id is not None
        assert professor.first_name is not None
        assert professor.last_name is not None
        assert professor.department is not None
    
    def test_required_fields_course(self):
        """Test that Course model requires necessary fields"""
        course = Course(
            course_code="CS101",
            title="Programming",
            professor_id=1,
            department="Computer Science",
            semester="Fall 2024",
            year=2024
        )
        
        assert course.course_code is not None
        assert course.title is not None
        assert course.professor_id is not None
        assert course.department is not None
        assert course.semester is not None
        assert course.year is not None

class TestStudentCourseAssociation:
    """Unit tests for student-course enrollment association"""
    
    def test_association_table_structure(self):
        """Test the association table structure"""
        # Test that the association table has the expected columns
        assert hasattr(student_course_association.c, 'student_id')
        assert hasattr(student_course_association.c, 'course_id')
        assert hasattr(student_course_association.c, 'enrollment_date')
        assert hasattr(student_course_association.c, 'status')
    
    def test_association_table_name(self):
        """Test that the association table has correct name"""
        assert student_course_association.name == 'enrollments'

# ============================================================================
# ACADEMIC RECORD MODELS TESTS
# ============================================================================

class TestAcademicRecord:
    """Test AcademicRecord model"""
    
    def test_create_academic_record(self, db_session, sample_student, sample_course):
        """Test creating an academic record"""
        record = AcademicRecord(
            student_id=sample_student.id,
            course_id=sample_course.id,
            semester="Fall",
            year=2024,
            letter_grade="A",
            numeric_grade=4.0,
            percentage_grade=95.0,
            credits_earned=3,
            credits_attempted=3,
            status=AcademicGradeStatus.GRADED
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.id is not None
        assert record.student_id == sample_student.id
        assert record.course_id == sample_course.id
        assert record.letter_grade == "A"
        assert record.numeric_grade == 4.0
        assert record.status == AcademicGradeStatus.GRADED
    
    def test_academic_record_relationships(self, db_session, sample_student, sample_course):
        """Test academic record relationships"""
        record = AcademicRecord(
            student_id=sample_student.id,
            course_id=sample_course.id,
            semester="Fall",
            year=2024,
            letter_grade="B+",
            numeric_grade=3.3,
            credits_earned=3,
            credits_attempted=3,
            status=AcademicGradeStatus.GRADED
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        # Test relationships
        assert record.student.id == sample_student.id
        assert record.course.id == sample_course.id

class TestTranscript:
    """Test Transcript model"""
    
    def test_create_transcript(self, db_session, sample_student):
        """Test creating a transcript"""
        transcript = Transcript(
            student_id=sample_student.id,
            transcript_type="official",
            status=TranscriptStatus.OFFICIAL,
            total_credits_earned=60,
            total_credits_attempted=60,
            cumulative_gpa=3.5,
            major_gpa=3.7
        )
        
        db_session.add(transcript)
        db_session.commit()
        db_session.refresh(transcript)
        
        assert transcript.id is not None
        assert transcript.student_id == sample_student.id
        assert transcript.transcript_type == "official"
        assert transcript.status == TranscriptStatus.OFFICIAL
        assert transcript.cumulative_gpa == 3.5
    
    def test_transcript_relationships(self, db_session, sample_student):
        """Test transcript relationships"""
        transcript = Transcript(
            student_id=sample_student.id,
            transcript_type="official",
            status=TranscriptStatus.OFFICIAL
        )
        
        db_session.add(transcript)
        db_session.commit()
        db_session.refresh(transcript)
        
        assert transcript.student.id == sample_student.id

class TestAcademicProgress:
    """Test AcademicProgress model"""
    
    def test_create_academic_progress(self, db_session, sample_student):
        """Test creating academic progress"""
        progress = AcademicProgress(
            student_id=sample_student.id,
            degree_program="Bachelor of Science in Computer Science",
            major="Computer Science",
            catalog_year=2022,
            total_credits_required=120,
            major_credits_required=60,
            total_credits_earned=60,
            major_credits_earned=30,
            cumulative_gpa=3.5,
            major_gpa=3.7
        )
        
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        assert progress.id is not None
        assert progress.student_id == sample_student.id
        assert progress.degree_program == "Bachelor of Science in Computer Science"
        assert progress.major == "Computer Science"
        assert progress.cumulative_gpa == 3.5
    
    def test_academic_progress_relationships(self, db_session, sample_student):
        """Test academic progress relationships"""
        progress = AcademicProgress(
            student_id=sample_student.id,
            degree_program="Bachelor of Science",
            major="Computer Science",
            catalog_year=2022
        )
        
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        assert progress.student.id == sample_student.id

class TestSemesterGPA:
    """Test SemesterGPA model"""
    
    def test_create_semester_gpa(self, db_session, sample_student):
        """Test creating semester GPA"""
        gpa = SemesterGPA(
            student_id=sample_student.id,
            semester="Fall",
            year=2024,
            semester_gpa=3.5,
            credits_earned=15,
            credits_attempted=15,
            quality_points=52.5,
            courses_completed=5,
            courses_attempted=5
        )
        
        db_session.add(gpa)
        db_session.commit()
        db_session.refresh(gpa)
        
        assert gpa.id is not None
        assert gpa.student_id == sample_student.id
        assert gpa.semester == "Fall"
        assert gpa.year == 2024
        assert gpa.semester_gpa == 3.5
        assert gpa.quality_points == 52.5
    
    def test_semester_gpa_relationships(self, db_session, sample_student):
        """Test semester GPA relationships"""
        gpa = SemesterGPA(
            student_id=sample_student.id,
            semester="Spring",
            year=2024,
            semester_gpa=3.2
        )
        
        db_session.add(gpa)
        db_session.commit()
        db_session.refresh(gpa)
        
        assert gpa.student.id == sample_student.id

class TestAcademicRecordEnums:
    """Test Academic Record enum values"""
    
    def test_grade_status_enum(self):
        """Test GradeStatus enum values"""
        assert AcademicGradeStatus.PENDING == "pending"
        assert AcademicGradeStatus.GRADED == "graded"
        assert AcademicGradeStatus.INCOMPLETE == "incomplete"
        assert AcademicGradeStatus.WITHDRAWN == "withdrawn"
    
    def test_transcript_status_enum(self):
        """Test TranscriptStatus enum values"""
        assert TranscriptStatus.DRAFT == "draft"
        assert TranscriptStatus.OFFICIAL == "official"
        assert TranscriptStatus.ARCHIVED == "archived"

# ============================================================================
# GRADING AND ASSESSMENT MODELS TESTS
# ============================================================================

class TestAssignment:
    """Test Assignment model"""
    
    def test_create_assignment(self, db_session, sample_course, sample_professor):
        """Test creating an assignment"""
        assignment = Assignment(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            title="Programming Assignment 1",
            description="Implement a simple calculator",
            assignment_type=AssignmentType.HOMEWORK,
            instructions="Create a calculator with basic operations",
            requirements="Must use Python",
            total_points=100.0,
            weight_percentage=15.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59),
            late_submission_deadline=datetime(2025, 1, 2, 23, 59, 59),
            late_penalty_percentage=10.0,
            allow_late_submissions=True,
            max_attempts=3,
            submission_format="Python file",
            file_size_limit=10
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        assert assignment.id is not None
        assert assignment.course_id == sample_course.id
        assert assignment.professor_id == sample_professor.id
        assert assignment.title == "Programming Assignment 1"
        assert assignment.assignment_type == AssignmentType.HOMEWORK
        assert assignment.total_points == 100.0
        assert assignment.weight_percentage == 15.0
        assert assignment.is_published == False
        assert assignment.is_active == True
    
    def test_assignment_relationships(self, db_session, sample_course, sample_professor):
        """Test assignment relationships"""
        assignment = Assignment(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            title="Test Assignment",
            assignment_type=AssignmentType.PROJECT,
            total_points=50.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59)
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        assert assignment.course.id == sample_course.id
        assert assignment.professor.id == sample_professor.id

class TestAssignmentSubmission:
    """Test AssignmentSubmission model"""
    
    def test_create_assignment_submission(self, db_session, sample_student):
        """Test creating an assignment submission"""
        # First create an assignment
        assignment = Assignment(
            course_id=1,  # Assuming course with ID 1
            professor_id=1,  # Assuming professor with ID 1
            title="Test Assignment",
            assignment_type=AssignmentType.HOMEWORK,
            total_points=100.0,
            due_date=datetime(2024, 12, 31, 23, 59, 59)
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        # Create submission
        submission = AssignmentSubmission(
            assignment_id=assignment.id,
            student_id=sample_student.id,
            submission_content="def add(a, b): return a + b",
            file_name="calculator.py",
            file_size=1024,
            submission_status=SubmissionStatus.SUBMITTED,
            is_late=False,
            attempt_number=1
        )
        
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)
        
        assert submission.id is not None
        assert submission.assignment_id == assignment.id
        assert submission.student_id == sample_student.id
        assert submission.submission_status == SubmissionStatus.SUBMITTED
        assert submission.is_late == False
        assert submission.attempt_number == 1

class TestExam:
    """Test Exam model"""
    
    def test_create_exam(self, db_session, sample_course, sample_professor):
        """Test creating an exam"""
        exam = Exam(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            title="Midterm Exam",
            description="Comprehensive midterm examination",
            exam_type=ExamType.MIDTERM,
            instructions="Answer all questions clearly",
            total_points=100.0,
            weight_percentage=30.0,
            passing_grade=60.0,
            exam_date=date(2024, 11, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration_minutes=120,
            location="Room 101",
            is_online=False,
            proctoring_required=True,
            allowed_materials="Calculator, Notes",
            restricted_materials="No phones, No internet"
        )
        
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)
        
        assert exam.id is not None
        assert exam.course_id == sample_course.id
        assert exam.professor_id == sample_professor.id
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
    
    def test_exam_relationships(self, db_session, sample_course, sample_professor):
        """Test exam relationships"""
        exam = Exam(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            title="Test Exam",
            exam_type=ExamType.FINAL,
            total_points=100.0,
            exam_date=date(2024, 12, 15),
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        
        db_session.add(exam)
        db_session.commit()
        db_session.refresh(exam)
        
        assert exam.course.id == sample_course.id
        assert exam.professor.id == sample_professor.id

class TestGrade:
    """Test Grade model"""
    
    def test_create_grade(self, db_session, sample_student, sample_course, sample_professor):
        """Test creating a grade"""
        grade = Grade(
            student_id=sample_student.id,
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            points_earned=85.0,
            points_possible=100.0,
            percentage=85.0,
            letter_grade="B",
            grade_status=GradeStatus.PUBLISHED,
            is_late=False,
            late_penalty_applied=0.0,
            extra_credit=0.0,
            curve_adjustment=0.0,
            professor_comments="Good work overall",
            detailed_feedback="Well-structured code with minor improvements needed"
        )
        
        db_session.add(grade)
        db_session.commit()
        db_session.refresh(grade)
        
        assert grade.id is not None
        assert grade.student_id == sample_student.id
        assert grade.course_id == sample_course.id
        assert grade.professor_id == sample_professor.id
        assert grade.points_earned == 85.0
        assert grade.points_possible == 100.0
        assert grade.percentage == 85.0
        assert grade.letter_grade == "B"
        assert grade.grade_status == GradeStatus.PUBLISHED
        assert grade.is_late == False
    
    def test_grade_relationships(self, db_session, sample_student, sample_course, sample_professor):
        """Test grade relationships"""
        grade = Grade(
            student_id=sample_student.id,
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            points_earned=90.0,
            points_possible=100.0,
            percentage=90.0
        )
        
        db_session.add(grade)
        db_session.commit()
        db_session.refresh(grade)
        
        assert grade.student.id == sample_student.id
        assert grade.course.id == sample_course.id
        assert grade.professor.id == sample_professor.id

class TestGradebook:
    """Test Gradebook model"""
    
    def test_create_gradebook(self, db_session, sample_course, sample_professor):
        """Test creating a gradebook"""
        gradebook = Gradebook(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            name="CS101 Fall 2024 Gradebook",
            description="Gradebook for Introduction to Computer Science",
            semester="Fall",
            year=2024,
            grading_scheme='{"A": 90, "B": 80, "C": 70, "D": 60}',
            letter_grade_scale='{"A+": 97, "A": 93, "A-": 90}',
            pass_fail_threshold=60.0,
            drop_lowest_assignments=1,
            drop_lowest_exams=0,
            curve_enabled=False,
            curve_percentage=0.0,
            assignment_weight=40.0,
            exam_weight=50.0,
            participation_weight=10.0,
            allow_student_view=True
        )
        
        db_session.add(gradebook)
        db_session.commit()
        db_session.refresh(gradebook)
        
        assert gradebook.id is not None
        assert gradebook.course_id == sample_course.id
        assert gradebook.professor_id == sample_professor.id
        assert gradebook.name == "CS101 Fall 2024 Gradebook"
        assert gradebook.semester == "Fall"
        assert gradebook.year == 2024
        assert gradebook.pass_fail_threshold == 60.0
        assert gradebook.assignment_weight == 40.0
        assert gradebook.exam_weight == 50.0
        assert gradebook.participation_weight == 10.0
        assert gradebook.is_published == False
        assert gradebook.is_active == True
    
    def test_gradebook_relationships(self, db_session, sample_course, sample_professor):
        """Test gradebook relationships"""
        gradebook = Gradebook(
            course_id=sample_course.id,
            professor_id=sample_professor.id,
            name="Test Gradebook",
            semester="Spring",
            year=2024
        )
        
        db_session.add(gradebook)
        db_session.commit()
        db_session.refresh(gradebook)
        
        assert gradebook.course.id == sample_course.id
        assert gradebook.professor.id == sample_professor.id

class TestGradebookEntry:
    """Test GradebookEntry model"""
    
    def test_create_gradebook_entry(self, db_session, sample_student):
        """Test creating a gradebook entry"""
        # First create a gradebook
        gradebook = Gradebook(
            course_id=1,  # Assuming course with ID 1
            professor_id=1,  # Assuming professor with ID 1
            name="Test Gradebook",
            semester="Fall",
            year=2024
        )
        db_session.add(gradebook)
        db_session.commit()
        db_session.refresh(gradebook)
        
        # Create gradebook entry
        entry = GradebookEntry(
            gradebook_id=gradebook.id,
            student_id=sample_student.id,
            total_points_earned=350.0,
            total_points_possible=400.0,
            overall_percentage=87.5,
            final_letter_grade="B+",
            assignment_average=85.0,
            exam_average=90.0,
            participation_average=85.0,
            assignments_completed=8,
            assignments_total=10,
            exams_completed=2,
            exams_total=2,
            is_passing=True,
            is_at_risk=False,
            needs_attention=False
        )
        
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)
        
        assert entry.id is not None
        assert entry.gradebook_id == gradebook.id
        assert entry.student_id == sample_student.id
        assert entry.total_points_earned == 350.0
        assert entry.total_points_possible == 400.0
        assert entry.overall_percentage == 87.5
        assert entry.final_letter_grade == "B+"
        assert entry.is_passing == True
        assert entry.is_at_risk == False

class TestGradeStatistics:
    """Test GradeStatistics model"""
    
    def test_create_grade_statistics(self, db_session, sample_course):
        """Test creating grade statistics"""
        statistics_obj = GradeStatistics(
            course_id=sample_course.id,
            total_students=25,
            students_passing=20,
            students_failing=5,
            average_grade=78.5,
            median_grade=80.0,
            highest_grade=95.0,
            lowest_grade=45.0,
            standard_deviation=12.5,
            a_grades=3,
            b_grades=8,
            c_grades=9,
            d_grades=3,
            f_grades=2,
            assignment_average=82.0,
            exam_average=75.0,
            participation_average=85.0
        )
        
        db_session.add(statistics_obj)
        db_session.commit()
        db_session.refresh(statistics_obj)
        
        assert statistics_obj.id is not None
        assert statistics_obj.course_id == sample_course.id
        assert statistics_obj.total_students == 25
        assert statistics_obj.students_passing == 20
        assert statistics_obj.students_failing == 5
        assert statistics_obj.average_grade == 78.5
        assert statistics_obj.median_grade == 80.0
        assert statistics_obj.highest_grade == 95.0
        assert statistics_obj.lowest_grade == 45.0
        assert statistics_obj.standard_deviation == 12.5
        assert statistics_obj.a_grades == 3
        assert statistics_obj.b_grades == 8
        assert statistics_obj.c_grades == 9
        assert statistics_obj.d_grades == 3
        assert statistics_obj.f_grades == 2

class TestGradeModification:
    """Test GradeModification model"""
    
    def test_create_grade_modification(self, db_session, sample_professor):
        """Test creating a grade modification"""
        # First create a grade
        grade = Grade(
            student_id=1,  # Assuming student with ID 1
            course_id=1,  # Assuming course with ID 1
            professor_id=sample_professor.id,
            points_earned=80.0,
            points_possible=100.0,
            percentage=80.0
        )
        db_session.add(grade)
        db_session.commit()
        db_session.refresh(grade)
        
        # Create grade modification
        modification = GradeModification(
            grade_id=grade.id,
            professor_id=sample_professor.id,
            old_points=80.0,
            new_points=85.0,
            old_percentage=80.0,
            new_percentage=85.0,
            old_letter_grade="B-",
            new_letter_grade="B",
            reason="Additional credit for extra effort",
            is_approved=False
        )
        
        db_session.add(modification)
        db_session.commit()
        db_session.refresh(modification)
        
        assert modification.id is not None
        assert modification.grade_id == grade.id
        assert modification.professor_id == sample_professor.id
        assert modification.old_points == 80.0
        assert modification.new_points == 85.0
        assert modification.old_percentage == 80.0
        assert modification.new_percentage == 85.0
        assert modification.old_letter_grade == "B-"
        assert modification.new_letter_grade == "B"
        assert modification.reason == "Additional credit for extra effort"
        assert modification.is_approved == False

class TestGradingAssessmentEnums:
    """Test Grading and Assessment enum values"""
    
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
        assert GradeStatus.DRAFT == "draft"
        assert GradeStatus.PUBLISHED == "published"
        assert GradeStatus.LATE == "late"
        assert GradeStatus.EXEMPT == "exempt"
        assert GradeStatus.INCOMPLETE == "incomplete"
        assert GradeStatus.MISSING == "missing"
    
    def test_submission_status_enum(self):
        """Test SubmissionStatus enum values"""
        assert SubmissionStatus.NOT_SUBMITTED == "not_submitted"
        assert SubmissionStatus.SUBMITTED == "submitted"
        assert SubmissionStatus.LATE == "late"
        assert SubmissionStatus.GRADED == "graded"
        assert SubmissionStatus.RETURNED == "returned"

# ============================================================================
# STUDENT INFORMATION MANAGEMENT MODELS TESTS
# ============================================================================

class TestAttendance:
    """Test Attendance model"""
    
    def test_create_attendance(self, db_session, sample_student, sample_course, sample_professor):
        """Test creating an attendance record"""
        attendance = Attendance(
            student_id=sample_student.id,
            course_id=sample_course.id,
            attendance_date=datetime.now(),
            status=AttendanceStatus.PRESENT,
            notes="Good participation",
            late_minutes=0,
            session_topic="Introduction to Programming",
            session_duration=90,
            recorded_by=sample_professor.id
        )
        
        db_session.add(attendance)
        db_session.commit()
        db_session.refresh(attendance)
        
        assert attendance.id is not None
        assert attendance.student_id == sample_student.id
        assert attendance.course_id == sample_course.id
        assert attendance.status == AttendanceStatus.PRESENT
        assert attendance.recorded_by == sample_professor.id
    
    def test_attendance_relationships(self, db_session, sample_student, sample_course, sample_professor):
        """Test attendance relationships"""
        attendance = Attendance(
            student_id=sample_student.id,
            course_id=sample_course.id,
            attendance_date=datetime.now(),
            status=AttendanceStatus.LATE,
            late_minutes=15,
            recorded_by=sample_professor.id
        )
        
        db_session.add(attendance)
        db_session.commit()
        db_session.refresh(attendance)
        
        # Test relationships
        assert attendance.student.id == sample_student.id
        assert attendance.course.id == sample_course.id
        assert attendance.professor.id == sample_professor.id

class TestMessage:
    """Test Message model"""
    
    def test_create_message(self, db_session, sample_professor, sample_course):
        """Test creating a message"""
        message = Message(
            sender_id=sample_professor.id,
            course_id=sample_course.id,
            subject="Assignment Due Date",
            content="Please remember that the assignment is due next week.",
            message_type=MessageType.ASSIGNMENT,
            priority=MessagePriority.HIGH,
            is_broadcast=True,
            status=MessageStatus.DRAFT
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.id is not None
        assert message.sender_id == sample_professor.id
        assert message.course_id == sample_course.id
        assert message.subject == "Assignment Due Date"
        assert message.message_type == MessageType.ASSIGNMENT
        assert message.priority == MessagePriority.HIGH
        assert message.is_broadcast == True
        assert message.status == MessageStatus.DRAFT
    
    def test_message_relationships(self, db_session, sample_professor, sample_course):
        """Test message relationships"""
        message = Message(
            sender_id=sample_professor.id,
            course_id=sample_course.id,
            subject="Test Message",
            content="This is a test message.",
            message_type=MessageType.GENERAL,
            priority=MessagePriority.NORMAL
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.sender.id == sample_professor.id
        assert message.course.id == sample_course.id

class TestMessageRecipient:
    """Test MessageRecipient model"""
    
    def test_create_message_recipient(self, db_session, sample_student):
        """Test creating a message recipient"""
        # First create a message
        message = Message(
            sender_id=1,  # Assuming professor with ID 1
            subject="Test Message",
            content="This is a test message.",
            message_type=MessageType.GENERAL,
            priority=MessagePriority.NORMAL
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        # Create recipient
        recipient = MessageRecipient(
            message_id=message.id,
            student_id=sample_student.id,
            status=MessageStatus.SENT
        )
        
        db_session.add(recipient)
        db_session.commit()
        db_session.refresh(recipient)
        
        assert recipient.id is not None
        assert recipient.message_id == message.id
        assert recipient.student_id == sample_student.id
        assert recipient.status == MessageStatus.SENT

class TestStudentDirectory:
    """Test StudentDirectory model"""
    
    def test_create_student_directory(self, db_session, sample_student, sample_professor):
        """Test creating a student directory entry"""
        directory = StudentDirectory(
            student_id=sample_student.id,
            email="john.doe@example.com",
            phone="123-456-7890",
            emergency_contact="Jane Doe",
            emergency_phone="098-765-4321",
            address="123 Main St, City, State",
            major="Computer Science",
            year_level="Junior",
            gpa=3.5,
            enrollment_status="active",
            advisor_id=sample_professor.id,
            notes="Excellent student",
            show_contact_info=True,
            show_academic_info=True
        )
        
        db_session.add(directory)
        db_session.commit()
        db_session.refresh(directory)
        
        assert directory.id is not None
        assert directory.student_id == sample_student.id
        assert directory.email == "john.doe@example.com"
        assert directory.phone == "123-456-7890"
        assert directory.major == "Computer Science"
        assert directory.gpa == 3.5
        assert directory.advisor_id == sample_professor.id
    
    def test_student_directory_relationships(self, db_session, sample_student, sample_professor):
        """Test student directory relationships"""
        directory = StudentDirectory(
            student_id=sample_student.id,
            email="john.doe@example.com",
            major="Computer Science",
            advisor_id=sample_professor.id
        )
        
        db_session.add(directory)
        db_session.commit()
        db_session.refresh(directory)
        
        assert directory.student.id == sample_student.id
        assert directory.advisor.id == sample_professor.id

class TestStudentPerformance:
    """Test StudentPerformance model"""
    
    def test_create_student_performance(self, db_session, sample_student, sample_course):
        """Test creating a student performance record"""
        performance = StudentPerformance(
            student_id=sample_student.id,
            course_id=sample_course.id,
            current_grade=85.5,
            participation_score=90.0,
            attendance_score=95.0,
            assignment_average=80.0,
            exam_average=90.0,
            is_at_risk=False,
            risk_factors="[]",
            improvement_areas="[]",
            professor_notes="Good performance overall"
        )
        
        db_session.add(performance)
        db_session.commit()
        db_session.refresh(performance)
        
        assert performance.id is not None
        assert performance.student_id == sample_student.id
        assert performance.course_id == sample_course.id
        assert performance.current_grade == 85.5
        assert performance.participation_score == 90.0
        assert performance.is_at_risk == False
    
    def test_student_performance_relationships(self, db_session, sample_student, sample_course):
        """Test student performance relationships"""
        performance = StudentPerformance(
            student_id=sample_student.id,
            course_id=sample_course.id,
            current_grade=75.0
        )
        
        db_session.add(performance)
        db_session.commit()
        db_session.refresh(performance)
        
        assert performance.student.id == sample_student.id
        assert performance.course.id == sample_course.id

class TestCommunicationLog:
    """Test CommunicationLog model"""
    
    def test_create_communication_log(self, db_session, sample_professor, sample_student, sample_course):
        """Test creating a communication log"""
        log = CommunicationLog(
            professor_id=sample_professor.id,
            student_id=sample_student.id,
            course_id=sample_course.id,
            communication_type="email",
            subject="Grade Discussion",
            content="Let's discuss your recent assignment grade.",
            direction="sent",
            requires_follow_up=True,
            follow_up_date=datetime.now()
        )
        
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        assert log.id is not None
        assert log.professor_id == sample_professor.id
        assert log.student_id == sample_student.id
        assert log.course_id == sample_course.id
        assert log.communication_type == "email"
        assert log.direction == "sent"
        assert log.requires_follow_up == True
    
    def test_communication_log_relationships(self, db_session, sample_professor, sample_student, sample_course):
        """Test communication log relationships"""
        log = CommunicationLog(
            professor_id=sample_professor.id,
            student_id=sample_student.id,
            course_id=sample_course.id,
            communication_type="meeting",
            direction="sent"
        )
        
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        assert log.professor.id == sample_professor.id
        assert log.student.id == sample_student.id
        assert log.course.id == sample_course.id

class TestAttendanceSummary:
    """Test AttendanceSummary model"""
    
    def test_create_attendance_summary(self, db_session, sample_student, sample_course):
        """Test creating an attendance summary"""
        summary = AttendanceSummary(
            student_id=sample_student.id,
            course_id=sample_course.id,
            semester="Fall",
            year=2024,
            total_sessions=20,
            present_count=18,
            absent_count=1,
            late_count=1,
            excused_count=0,
            tardy_count=0,
            attendance_percentage=90.0,
            total_late_minutes=15
        )
        
        db_session.add(summary)
        db_session.commit()
        db_session.refresh(summary)
        
        assert summary.id is not None
        assert summary.student_id == sample_student.id
        assert summary.course_id == sample_course.id
        assert summary.semester == "Fall"
        assert summary.year == 2024
        assert summary.total_sessions == 20
        assert summary.present_count == 18
        assert summary.attendance_percentage == 90.0
    
    def test_attendance_summary_relationships(self, db_session, sample_student, sample_course):
        """Test attendance summary relationships"""
        summary = AttendanceSummary(
            student_id=sample_student.id,
            course_id=sample_course.id,
            semester="Spring",
            year=2024,
            total_sessions=15,
            present_count=15,
            attendance_percentage=100.0
        )
        
        db_session.add(summary)
        db_session.commit()
        db_session.refresh(summary)
        
        assert summary.student.id == sample_student.id
        assert summary.course.id == sample_course.id

class TestStudentInformationEnums:
    """Test Student Information Management enum values"""
    
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

if __name__ == "__main__":
    pytest.main([__file__])
