"""
Grading and Assessment models for assignments, exams, grades, and gradebook management
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum

class AssignmentType(str, enum.Enum):
    HOMEWORK = "homework"
    PROJECT = "project"
    LAB = "lab"
    QUIZ = "quiz"
    PRESENTATION = "presentation"
    ESSAY = "essay"
    RESEARCH = "research"
    OTHER = "other"

class ExamType(str, enum.Enum):
    MIDTERM = "midterm"
    FINAL = "final"
    QUIZ = "quiz"
    POP_QUIZ = "pop_quiz"
    PRACTICAL = "practical"
    ORAL = "oral"
    WRITTEN = "written"
    ONLINE = "online"

class GradeStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LATE = "late"
    EXEMPT = "exempt"
    INCOMPLETE = "incomplete"
    MISSING = "missing"

class SubmissionStatus(str, enum.Enum):
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    LATE = "late"
    GRADED = "graded"
    RETURNED = "returned"

class Assignment(Base):
    """Assignment model for creating and managing assignments"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    
    # Assignment details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    assignment_type = Column(Enum(AssignmentType), nullable=False)
    instructions = Column(Text)
    requirements = Column(Text)
    
    # Grading information
    total_points = Column(Float, nullable=False, default=100.0)
    weight_percentage = Column(Float, nullable=False, default=10.0)  # Weight in final grade
    rubric = Column(Text)  # JSON string of grading rubric
    
    # Due dates and timing
    assigned_date = Column(DateTime, default=func.now())
    due_date = Column(DateTime, nullable=False)
    late_submission_deadline = Column(DateTime)  # Optional late submission deadline
    late_penalty_percentage = Column(Float, default=10.0)  # Penalty for late submissions
    
    # Submission settings
    allow_late_submissions = Column(Boolean, default=True)
    max_attempts = Column(Integer, default=1)
    submission_format = Column(String(100))  # e.g., "PDF", "Word", "Online"
    file_size_limit = Column(Integer)  # File size limit in MB
    
    # Status and visibility
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", backref="assignments")
    professor = relationship("Professor", backref="created_assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment")
    grades = relationship("Grade", back_populates="assignment")

class AssignmentSubmission(Base):
    """Assignment submission model"""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Submission details
    submission_content = Column(Text)  # Text submission or file path
    file_path = Column(String(500))  # Path to uploaded file
    file_name = Column(String(200))  # Original file name
    file_size = Column(Integer)  # File size in bytes
    
    # Submission status and timing
    submission_status = Column(Enum(SubmissionStatus), default=SubmissionStatus.SUBMITTED)
    submitted_at = Column(DateTime, default=func.now())
    is_late = Column(Boolean, default=False)
    late_hours = Column(Float, default=0.0)  # Hours late
    
    # Attempt tracking
    attempt_number = Column(Integer, default=1)
    
    # Professor feedback
    professor_feedback = Column(Text)
    feedback_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", backref="assignment_submissions")

class Exam(Base):
    """Exam model for scheduling and managing examinations"""
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    
    # Exam details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    exam_type = Column(Enum(ExamType), nullable=False)
    instructions = Column(Text)
    
    # Grading information
    total_points = Column(Float, nullable=False, default=100.0)
    weight_percentage = Column(Float, nullable=False, default=30.0)  # Weight in final grade
    passing_grade = Column(Float, default=60.0)  # Minimum passing grade
    
    # Scheduling information
    exam_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer)  # Exam duration in minutes
    location = Column(String(200))  # Exam location/room
    
    # Exam settings
    is_online = Column(Boolean, default=False)
    online_platform = Column(String(100))  # e.g., "Canvas", "Blackboard", "Zoom"
    online_link = Column(String(500))  # Online exam link
    proctoring_required = Column(Boolean, default=False)
    proctoring_software = Column(String(100))
    
    # Materials and resources
    allowed_materials = Column(Text)  # e.g., "Calculator", "Notes", "Textbook"
    restricted_materials = Column(Text)  # e.g., "No phones", "No internet"
    
    # Status and visibility
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    registration_required = Column(Boolean, default=False)
    registration_deadline = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", backref="exams")
    professor = relationship("Professor", backref="created_exams")
    exam_sessions = relationship("ExamSession", back_populates="exam")
    grades = relationship("Grade", back_populates="exam")

class ExamSession(Base):
    """Exam session model for tracking individual exam sessions"""
    __tablename__ = "exam_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Session details
    session_start_time = Column(DateTime)
    session_end_time = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    
    # Attendance and participation
    attended = Column(Boolean, default=False)
    late_arrival_minutes = Column(Integer, default=0)
    early_departure_minutes = Column(Integer, default=0)
    
    # Technical issues
    technical_issues = Column(Text)
    issues_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam", back_populates="exam_sessions")
    student = relationship("Student", backref="exam_sessions")

class Grade(Base):
    """Grade model for storing individual grades"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    
    # Grade source (either assignment or exam)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    
    # Grade details
    points_earned = Column(Float, nullable=False)
    points_possible = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)  # Calculated percentage
    letter_grade = Column(String(5))  # A+, A, A-, B+, etc.
    
    # Grade status and timing
    grade_status = Column(Enum(GradeStatus), default=GradeStatus.DRAFT)
    graded_date = Column(DateTime, default=func.now())
    published_date = Column(DateTime)
    
    # Grading details
    is_late = Column(Boolean, default=False)
    late_penalty_applied = Column(Float, default=0.0)
    extra_credit = Column(Float, default=0.0)
    curve_adjustment = Column(Float, default=0.0)
    
    # Feedback and comments
    professor_comments = Column(Text)
    rubric_scores = Column(Text)  # JSON string of rubric scores
    detailed_feedback = Column(Text)
    
    # Grade modifications
    is_modified = Column(Boolean, default=False)
    modification_reason = Column(Text)
    modification_date = Column(DateTime)
    modified_by = Column(Integer, ForeignKey("professors.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="grades")
    course = relationship("Course", backref="grades")
    professor = relationship("Professor", backref="graded_items", foreign_keys=[professor_id])
    assignment = relationship("Assignment", back_populates="grades")
    exam = relationship("Exam", back_populates="grades")
    modifier = relationship("Professor", foreign_keys=[modified_by])

class Gradebook(Base):
    """Gradebook model for comprehensive grade management"""
    __tablename__ = "gradebooks"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    
    # Gradebook settings
    name = Column(String(200), nullable=False)
    description = Column(Text)
    semester = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Grading scheme
    grading_scheme = Column(Text)  # JSON string of grading scheme
    letter_grade_scale = Column(Text)  # JSON string of letter grade scale
    pass_fail_threshold = Column(Float, default=60.0)
    
    # Grade calculation settings
    drop_lowest_assignments = Column(Integer, default=0)
    drop_lowest_exams = Column(Integer, default=0)
    curve_enabled = Column(Boolean, default=False)
    curve_percentage = Column(Float, default=0.0)
    
    # Weight distribution
    assignment_weight = Column(Float, default=40.0)
    exam_weight = Column(Float, default=50.0)
    participation_weight = Column(Float, default=10.0)
    
    # Status and visibility
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    allow_student_view = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", backref="gradebooks")
    professor = relationship("Professor", backref="gradebooks")

class GradebookEntry(Base):
    """Gradebook entry model for individual student gradebook records"""
    __tablename__ = "gradebook_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    gradebook_id = Column(Integer, ForeignKey("gradebooks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Calculated grades
    total_points_earned = Column(Float, default=0.0)
    total_points_possible = Column(Float, default=0.0)
    overall_percentage = Column(Float, default=0.0)
    final_letter_grade = Column(String(5))
    
    # Category breakdowns
    assignment_average = Column(Float, default=0.0)
    exam_average = Column(Float, default=0.0)
    participation_average = Column(Float, default=0.0)
    
    # Grade statistics
    assignments_completed = Column(Integer, default=0)
    assignments_total = Column(Integer, default=0)
    exams_completed = Column(Integer, default=0)
    exams_total = Column(Integer, default=0)
    
    # Status indicators
    is_passing = Column(Boolean, default=True)
    is_at_risk = Column(Boolean, default=False)
    needs_attention = Column(Boolean, default=False)
    
    # Last updated
    last_calculated = Column(DateTime, default=func.now())
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    gradebook = relationship("Gradebook", backref="entries")
    student = relationship("Student", backref="gradebook_entries")

class GradeStatistics(Base):
    """Grade statistics model for course-level analytics"""
    __tablename__ = "grade_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    gradebook_id = Column(Integer, ForeignKey("gradebooks.id"), nullable=True)
    
    # Statistical data
    total_students = Column(Integer, default=0)
    students_passing = Column(Integer, default=0)
    students_failing = Column(Integer, default=0)
    
    # Grade distribution
    average_grade = Column(Float, default=0.0)
    median_grade = Column(Float, default=0.0)
    highest_grade = Column(Float, default=0.0)
    lowest_grade = Column(Float, default=0.0)
    standard_deviation = Column(Float, default=0.0)
    
    # Letter grade distribution
    a_grades = Column(Integer, default=0)
    b_grades = Column(Integer, default=0)
    c_grades = Column(Integer, default=0)
    d_grades = Column(Integer, default=0)
    f_grades = Column(Integer, default=0)
    
    # Category statistics
    assignment_average = Column(Float, default=0.0)
    exam_average = Column(Float, default=0.0)
    participation_average = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    course = relationship("Course", backref="grade_statistics")
    gradebook = relationship("Gradebook", backref="statistics")

class GradeModification(Base):
    """Grade modification model for tracking grade changes"""
    __tablename__ = "grade_modifications"
    
    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), nullable=False)
    
    # Modification details
    old_points = Column(Float, nullable=False)
    new_points = Column(Float, nullable=False)
    old_percentage = Column(Float, nullable=False)
    new_percentage = Column(Float, nullable=False)
    old_letter_grade = Column(String(5))
    new_letter_grade = Column(String(5))
    
    # Modification reason and approval
    reason = Column(Text, nullable=False)
    approved_by = Column(Integer, ForeignKey("professors.id"))
    approval_date = Column(DateTime)
    is_approved = Column(Boolean, default=False)
    
    # Timestamps
    modified_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    grade = relationship("Grade", backref="modifications")
    professor = relationship("Professor", backref="grade_modifications", foreign_keys=[professor_id])
    approver = relationship("Professor", foreign_keys=[approved_by])
