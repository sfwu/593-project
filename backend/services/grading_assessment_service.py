"""
Grading and Assessment Service - Business logic layer for grading and assessment management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from repositories.grading_assessment_repository import GradingAssessmentRepository
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentSubmissionCreate, AssignmentSubmissionUpdate, AssignmentSubmissionResponse,
    ExamCreate, ExamUpdate, ExamResponse, ExamSessionCreate, ExamSessionUpdate, ExamSessionResponse,
    GradeCreate, GradeUpdate, GradeResponse, GradebookCreate, GradebookUpdate, GradebookResponse,
    GradebookEntryResponse, GradeStatisticsResponse, GradeModificationCreate, GradeModificationResponse,
    BulkGradeCreate, BulkAssignmentCreate, AssignmentFilters, ExamFilters, GradeFilters,
    GradingDashboardSummary, CourseGradingSummary, GradeDistributionReport,
    AssignmentAnalytics, ExamAnalytics, AssignmentType, ExamType, GradeStatus, SubmissionStatus
)
from models.grading_assessment import AssignmentType, ExamType, GradeStatus, SubmissionStatus
from models.student import Student
from models.course import Course
from models.professor import Professor
from datetime import datetime, date, timedelta
import json
import statistics

class GradingAssessmentService:
    """Service layer for grading and assessment business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = GradingAssessmentRepository(db)
    
    # Assignment Management Operations
    def create_assignment(self, assignment_data: AssignmentCreate, professor_id: int) -> AssignmentResponse:
        """Create a new assignment with validation"""
        # Validate assignment data
        self._validate_assignment_data(assignment_data)
        
        # Create the assignment
        assignment = self.repository.create_assignment(assignment_data, professor_id)
        
        return AssignmentResponse.from_orm(assignment)
    
    def get_assignments(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        assignment_type: Optional[AssignmentType] = None,
        is_published: Optional[bool] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None
    ) -> List[AssignmentResponse]:
        """Get assignments with optional filtering"""
        assignments = self.repository.get_assignments(
            course_id, professor_id, assignment_type, is_published, due_date_from, due_date_to
        )
        
        # Add submission count for each assignment
        result = []
        for assignment in assignments:
            assignment_dict = AssignmentResponse.from_orm(assignment).dict()
            submission_count = self.repository.get_assignment_submissions(assignment_id=assignment.id)
            assignment_dict["submission_count"] = len(submission_count)
            result.append(AssignmentResponse(**assignment_dict))
        
        return result
    
    def get_assignment_by_id(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """Get specific assignment by ID"""
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        assignment_dict = AssignmentResponse.from_orm(assignment).dict()
        submission_count = self.repository.get_assignment_submissions(assignment_id=assignment.id)
        assignment_dict["submission_count"] = len(submission_count)
        
        return AssignmentResponse(**assignment_dict)
    
    def update_assignment(self, assignment_id: int, assignment_data: AssignmentUpdate, professor_id: int) -> Optional[AssignmentResponse]:
        """Update an assignment"""
        # Verify assignment belongs to professor
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment or assignment.professor_id != professor_id:
            return None
        
        updated_assignment = self.repository.update_assignment(assignment_id, assignment_data)
        if not updated_assignment:
            return None
        
        return AssignmentResponse.from_orm(updated_assignment)
    
    def publish_assignment(self, assignment_id: int, professor_id: int) -> Optional[AssignmentResponse]:
        """Publish an assignment"""
        # Verify assignment belongs to professor
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment or assignment.professor_id != professor_id:
            return None
        
        published_assignment = self.repository.publish_assignment(assignment_id)
        if not published_assignment:
            return None
        
        return AssignmentResponse.from_orm(published_assignment)
    
    def delete_assignment(self, assignment_id: int, professor_id: int) -> bool:
        """Delete an assignment (soft delete)"""
        # Verify assignment belongs to professor
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment or assignment.professor_id != professor_id:
            return False
        
        return self.repository.delete_assignment(assignment_id)
    
    def create_bulk_assignments(self, bulk_data: BulkAssignmentCreate, professor_id: int) -> List[AssignmentResponse]:
        """Create multiple assignments from a template"""
        assignments = []
        
        for i, (due_date, title) in enumerate(zip(bulk_data.due_dates, bulk_data.titles)):
            assignment_data = AssignmentCreate(
                course_id=bulk_data.course_id,
                title=f"{title} {i+1}",
                description=bulk_data.assignment_template.description,
                assignment_type=bulk_data.assignment_template.assignment_type,
                instructions=bulk_data.assignment_template.instructions,
                requirements=bulk_data.assignment_template.requirements,
                total_points=bulk_data.assignment_template.total_points,
                weight_percentage=bulk_data.assignment_template.weight_percentage,
                rubric=bulk_data.assignment_template.rubric,
                due_date=due_date,
                late_submission_deadline=bulk_data.assignment_template.late_submission_deadline,
                late_penalty_percentage=bulk_data.assignment_template.late_penalty_percentage,
                allow_late_submissions=bulk_data.assignment_template.allow_late_submissions,
                max_attempts=bulk_data.assignment_template.max_attempts,
                submission_format=bulk_data.assignment_template.submission_format,
                file_size_limit=bulk_data.assignment_template.file_size_limit
            )
            
            assignment = self.create_assignment(assignment_data, professor_id)
            assignments.append(assignment)
        
        return assignments
    
    # Assignment Submission Operations
    def create_assignment_submission(self, submission_data: AssignmentSubmissionCreate, student_id: int) -> AssignmentSubmissionResponse:
        """Create an assignment submission"""
        try:
            submission = self.repository.create_assignment_submission(submission_data, student_id)
            return AssignmentSubmissionResponse.from_orm(submission)
        except ValueError as e:
            raise ValueError(str(e))
    
    def get_assignment_submissions(
        self,
        assignment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        submission_status: Optional[SubmissionStatus] = None
    ) -> List[AssignmentSubmissionResponse]:
        """Get assignment submissions with optional filtering"""
        submissions = self.repository.get_assignment_submissions(
            assignment_id, student_id, submission_status
        )
        return [AssignmentSubmissionResponse.from_orm(submission) for submission in submissions]
    
    def update_assignment_submission(self, submission_id: int, submission_data: AssignmentSubmissionUpdate, professor_id: int) -> Optional[AssignmentSubmissionResponse]:
        """Update an assignment submission (professor feedback)"""
        submission = self.repository.update_assignment_submission(submission_id, submission_data)
        if not submission:
            return None
        
        return AssignmentSubmissionResponse.from_orm(submission)
    
    # Exam Management Operations
    def create_exam(self, exam_data: ExamCreate, professor_id: int) -> ExamResponse:
        """Create a new exam with validation"""
        # Validate exam data
        self._validate_exam_data(exam_data)
        
        # Create the exam
        exam = self.repository.create_exam(exam_data, professor_id)
        
        return ExamResponse.from_orm(exam)
    
    def get_exams(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        exam_type: Optional[ExamType] = None,
        is_published: Optional[bool] = None,
        exam_date_from: Optional[date] = None,
        exam_date_to: Optional[date] = None
    ) -> List[ExamResponse]:
        """Get exams with optional filtering"""
        exams = self.repository.get_exams(
            course_id, professor_id, exam_type, is_published, exam_date_from, exam_date_to
        )
        
        # Add registered students count for each exam
        result = []
        for exam in exams:
            exam_dict = ExamResponse.from_orm(exam).dict()
            # Count registered students (would need to implement exam registration)
            exam_dict["registered_students"] = 0
            result.append(ExamResponse(**exam_dict))
        
        return result
    
    def get_exam_by_id(self, exam_id: int) -> Optional[ExamResponse]:
        """Get specific exam by ID"""
        exam = self.repository.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        exam_dict = ExamResponse.from_orm(exam).dict()
        exam_dict["registered_students"] = 0  # Would need to implement exam registration
        
        return ExamResponse(**exam_dict)
    
    def update_exam(self, exam_id: int, exam_data: ExamUpdate, professor_id: int) -> Optional[ExamResponse]:
        """Update an exam"""
        # Verify exam belongs to professor
        exam = self.repository.get_exam_by_id(exam_id)
        if not exam or exam.professor_id != professor_id:
            return None
        
        updated_exam = self.repository.update_exam(exam_id, exam_data)
        if not updated_exam:
            return None
        
        return ExamResponse.from_orm(updated_exam)
    
    def publish_exam(self, exam_id: int, professor_id: int) -> Optional[ExamResponse]:
        """Publish an exam"""
        # Verify exam belongs to professor
        exam = self.repository.get_exam_by_id(exam_id)
        if not exam or exam.professor_id != professor_id:
            return None
        
        published_exam = self.repository.publish_exam(exam_id)
        if not published_exam:
            return None
        
        return ExamResponse.from_orm(published_exam)
    
    # Exam Session Operations
    def create_exam_session(self, session_data: ExamSessionCreate) -> ExamSessionResponse:
        """Create an exam session"""
        session = self.repository.create_exam_session(session_data)
        return ExamSessionResponse.from_orm(session)
    
    def get_exam_sessions(
        self,
        exam_id: Optional[int] = None,
        student_id: Optional[int] = None
    ) -> List[ExamSessionResponse]:
        """Get exam sessions with optional filtering"""
        sessions = self.repository.get_exam_sessions(exam_id, student_id)
        return [ExamSessionResponse.from_orm(session) for session in sessions]
    
    def update_exam_session(self, session_id: int, session_data: ExamSessionUpdate) -> Optional[ExamSessionResponse]:
        """Update an exam session"""
        session = self.repository.update_exam_session(session_id, session_data)
        if not session:
            return None
        
        return ExamSessionResponse.from_orm(session)
    
    # Grade Management Operations
    def create_grade(self, grade_data: GradeCreate, professor_id: int) -> GradeResponse:
        """Create a new grade with validation"""
        # Validate grade data
        self._validate_grade_data(grade_data)
        
        # Create the grade
        grade = self.repository.create_grade(grade_data, professor_id)
        
        return GradeResponse.from_orm(grade)
    
    def get_grades(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[int] = None,
        assignment_id: Optional[int] = None,
        exam_id: Optional[int] = None,
        grade_status: Optional[GradeStatus] = None,
        professor_id: Optional[int] = None
    ) -> List[GradeResponse]:
        """Get grades with optional filtering"""
        grades = self.repository.get_grades(
            course_id, student_id, assignment_id, exam_id, grade_status, professor_id
        )
        return [GradeResponse.from_orm(grade) for grade in grades]
    
    def get_grade_by_id(self, grade_id: int) -> Optional[GradeResponse]:
        """Get specific grade by ID"""
        grade = self.repository.get_grade_by_id(grade_id)
        if not grade:
            return None
        
        return GradeResponse.from_orm(grade)
    
    def update_grade(self, grade_id: int, grade_data: GradeUpdate, professor_id: int) -> Optional[GradeResponse]:
        """Update a grade"""
        # Verify grade belongs to professor
        grade = self.repository.get_grade_by_id(grade_id)
        if not grade or grade.professor_id != professor_id:
            return None
        
        updated_grade = self.repository.update_grade(grade_id, grade_data)
        if not updated_grade:
            return None
        
        return GradeResponse.from_orm(updated_grade)
    
    def publish_grade(self, grade_id: int, professor_id: int) -> Optional[GradeResponse]:
        """Publish a grade"""
        # Verify grade belongs to professor
        grade = self.repository.get_grade_by_id(grade_id)
        if not grade or grade.professor_id != professor_id:
            return None
        
        published_grade = self.repository.publish_grade(grade_id)
        if not published_grade:
            return None
        
        return GradeResponse.from_orm(published_grade)
    
    def create_bulk_grades(self, bulk_data: BulkGradeCreate, professor_id: int) -> List[GradeResponse]:
        """Create multiple grades at once"""
        grades = self.repository.create_bulk_grades(bulk_data, professor_id)
        return [GradeResponse.from_orm(grade) for grade in grades]
    
    # Gradebook Management Operations
    def create_gradebook(self, gradebook_data: GradebookCreate, professor_id: int) -> GradebookResponse:
        """Create a new gradebook with validation"""
        # Validate gradebook data
        self._validate_gradebook_data(gradebook_data)
        
        # Create the gradebook
        gradebook = self.repository.create_gradebook(gradebook_data, professor_id)
        
        return GradebookResponse.from_orm(gradebook)
    
    def get_gradebooks(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        semester: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[GradebookResponse]:
        """Get gradebooks with optional filtering"""
        gradebooks = self.repository.get_gradebooks(course_id, professor_id, semester, year)
        
        # Add total students count for each gradebook
        result = []
        for gradebook in gradebooks:
            gradebook_dict = GradebookResponse.from_orm(gradebook).dict()
            entries = self.repository.get_gradebook_entries(gradebook.id)
            gradebook_dict["total_students"] = len(entries)
            result.append(GradebookResponse(**gradebook_dict))
        
        return result
    
    def get_gradebook_by_id(self, gradebook_id: int) -> Optional[GradebookResponse]:
        """Get specific gradebook by ID"""
        gradebook = self.repository.get_gradebook_by_id(gradebook_id)
        if not gradebook:
            return None
        
        gradebook_dict = GradebookResponse.from_orm(gradebook).dict()
        entries = self.repository.get_gradebook_entries(gradebook.id)
        gradebook_dict["total_students"] = len(entries)
        
        return GradebookResponse(**gradebook_dict)
    
    def update_gradebook(self, gradebook_id: int, gradebook_data: GradebookUpdate, professor_id: int) -> Optional[GradebookResponse]:
        """Update a gradebook"""
        # Verify gradebook belongs to professor
        gradebook = self.repository.get_gradebook_by_id(gradebook_id)
        if not gradebook or gradebook.professor_id != professor_id:
            return None
        
        updated_gradebook = self.repository.update_gradebook(gradebook_id, gradebook_data)
        if not updated_gradebook:
            return None
        
        return GradebookResponse.from_orm(updated_gradebook)
    
    def get_gradebook_entries(self, gradebook_id: int) -> List[GradebookEntryResponse]:
        """Get all gradebook entries for a gradebook"""
        entries = self.repository.get_gradebook_entries(gradebook_id)
        return [GradebookEntryResponse.from_orm(entry) for entry in entries]
    
    def get_gradebook_entry(self, gradebook_id: int, student_id: int) -> Optional[GradebookEntryResponse]:
        """Get specific gradebook entry"""
        entry = self.repository.get_gradebook_entry(gradebook_id, student_id)
        if not entry:
            return None
        
        return GradebookEntryResponse.from_orm(entry)
    
    # Grade Statistics Operations
    def calculate_grade_statistics(self, course_id: int, gradebook_id: Optional[int] = None) -> GradeStatisticsResponse:
        """Calculate grade statistics for a course"""
        statistics_obj = self.repository.calculate_grade_statistics(course_id, gradebook_id)
        return GradeStatisticsResponse.from_orm(statistics_obj)
    
    # Grade Modification Operations
    def create_grade_modification(self, modification_data: GradeModificationCreate, professor_id: int) -> GradeModificationResponse:
        """Create a grade modification record"""
        modification = self.repository.create_grade_modification(modification_data, professor_id)
        return GradeModificationResponse.from_orm(modification)
    
    def get_grade_modifications(self, grade_id: int) -> List[GradeModificationResponse]:
        """Get all modifications for a grade"""
        modifications = self.repository.get_grade_modifications(grade_id)
        return [GradeModificationResponse.from_orm(mod) for mod in modifications]
    
    def approve_grade_modification(self, modification_id: int, approver_id: int) -> Optional[GradeModificationResponse]:
        """Approve a grade modification"""
        modification = self.repository.approve_grade_modification(modification_id, approver_id)
        if not modification:
            return None
        
        return GradeModificationResponse.from_orm(modification)
    
    # Dashboard and Analytics Operations
    def get_grading_dashboard_summary(self, professor_id: int) -> GradingDashboardSummary:
        """Get professor grading dashboard summary"""
        # Get professor's courses
        courses = self.db.query(Course).filter(Course.professor_id == professor_id).all()
        course_ids = [course.id for course in courses]
        
        # Get counts
        total_courses = len(courses)
        total_assignments = self.db.query(Assignment).filter(Assignment.professor_id == professor_id).count()
        total_exams = self.db.query(Exam).filter(Exam.professor_id == professor_id).count()
        
        # Get pending grades (draft status)
        pending_grades = self.db.query(Grade).filter(
            and_(
                Grade.professor_id == professor_id,
                Grade.grade_status == GradeStatus.DRAFT
            )
        ).count()
        
        # Get overdue assignments
        overdue_assignments = self.db.query(Assignment).filter(
            and_(
                Assignment.professor_id == professor_id,
                Assignment.due_date < datetime.utcnow(),
                Assignment.is_published == True
            )
        ).count()
        
        # Get upcoming exams (next 7 days)
        upcoming_exams = self.db.query(Exam).filter(
            and_(
                Exam.professor_id == professor_id,
                Exam.exam_date >= date.today(),
                Exam.exam_date <= date.today() + timedelta(days=7),
                Exam.is_published == True
            )
        ).count()
        
        # Get students at risk (from gradebook entries)
        students_at_risk = 0
        for course_id in course_ids:
            gradebooks = self.repository.get_gradebooks(course_id=course_id, professor_id=professor_id)
            for gradebook in gradebooks:
                entries = self.repository.get_gradebook_entries(gradebook.id)
                students_at_risk += len([entry for entry in entries if entry.is_at_risk])
        
        # Calculate average course grade
        all_grades = self.db.query(Grade).filter(Grade.professor_id == professor_id).all()
        average_course_grade = statistics.mean([grade.percentage for grade in all_grades]) if all_grades else 0.0
        
        return GradingDashboardSummary(
            professor_id=professor_id,
            total_courses=total_courses,
            total_assignments=total_assignments,
            total_exams=total_exams,
            pending_grades=pending_grades,
            overdue_assignments=overdue_assignments,
            upcoming_exams=upcoming_exams,
            students_at_risk=students_at_risk,
            average_course_grade=round(average_course_grade, 2)
        )
    
    def get_course_grading_summary(self, course_id: int) -> CourseGradingSummary:
        """Get comprehensive grading summary for a course"""
        summary_data = self.repository.get_course_grading_summary(course_id)
        
        return CourseGradingSummary(
            course_id=summary_data["course_id"],
            course_name=summary_data["course_name"],
            total_assignments=summary_data["total_assignments"],
            total_exams=summary_data["total_exams"],
            total_students=summary_data["total_students"],
            average_grade=summary_data["average_grade"],
            completion_rate=summary_data["completion_rate"],
            students_passing=summary_data["students_passing"],
            students_failing=summary_data["students_failing"]
        )
    
    def get_grade_distribution_report(self, course_id: int) -> GradeDistributionReport:
        """Generate grade distribution report for a course"""
        # Get course info
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError("Course not found")
        
        # Get grade statistics
        statistics_obj = self.calculate_grade_statistics(course_id)
        
        # Get grade distribution
        grade_distribution = {
            "A": statistics_obj.a_grades,
            "B": statistics_obj.b_grades,
            "C": statistics_obj.c_grades,
            "D": statistics_obj.d_grades,
            "F": statistics_obj.f_grades
        }
        
        # Get grade trends (would need to implement historical data)
        grade_trends = []  # Placeholder for grade trends over time
        
        return GradeDistributionReport(
            course_id=course_id,
            course_name=course.title,
            total_students=statistics_obj.total_students,
            grade_distribution=grade_distribution,
            statistics=statistics_obj,
            grade_trends=grade_trends
        )
    
    def get_assignment_analytics(self, assignment_id: int) -> AssignmentAnalytics:
        """Get analytics for a specific assignment"""
        analytics_data = self.repository.get_assignment_analytics(assignment_id)
        
        return AssignmentAnalytics(
            assignment_id=analytics_data["assignment_id"],
            assignment_title=analytics_data["assignment_title"],
            total_submissions=analytics_data["total_submissions"],
            submission_rate=analytics_data["submission_rate"],
            average_grade=analytics_data["average_grade"],
            grade_distribution=analytics_data["grade_distribution"],
            late_submissions=analytics_data["late_submissions"],
            completion_time_stats={}  # Would need to implement completion time tracking
        )
    
    def get_exam_analytics(self, exam_id: int) -> ExamAnalytics:
        """Get analytics for a specific exam"""
        exam = self.repository.get_exam_by_id(exam_id)
        if not exam:
            raise ValueError("Exam not found")
        
        # Get exam sessions
        sessions = self.repository.get_exam_sessions(exam_id=exam_id)
        
        # Calculate analytics
        total_registered = len(sessions)
        attendance_rate = len([s for s in sessions if s.attended]) / total_registered * 100 if total_registered > 0 else 0.0
        
        # Get grades for the exam
        grades = self.repository.get_grades(exam_id=exam_id)
        if grades:
            average_grade = statistics.mean([g.percentage for g in grades])
            grade_distribution = {
                "A": len([g for g in grades if g.percentage >= 90]),
                "B": len([g for g in grades if 80 <= g.percentage < 90]),
                "C": len([g for g in grades if 70 <= g.percentage < 80]),
                "D": len([g for g in grades if 60 <= g.percentage < 70]),
                "F": len([g for g in grades if g.percentage < 60])
            }
        else:
            average_grade = 0.0
            grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        
        return ExamAnalytics(
            exam_id=exam_id,
            exam_title=exam.title,
            total_registered=total_registered,
            attendance_rate=round(attendance_rate, 2),
            average_grade=round(average_grade, 2),
            grade_distribution=grade_distribution,
            time_analysis={},  # Would need to implement time analysis
            difficulty_analysis={}  # Would need to implement difficulty analysis
        )
    
    # Private helper methods
    def _validate_assignment_data(self, assignment_data: AssignmentCreate) -> None:
        """Validate assignment data"""
        if assignment_data.due_date <= datetime.utcnow():
            raise ValueError("Due date must be in the future")
        
        if assignment_data.late_submission_deadline and assignment_data.late_submission_deadline <= assignment_data.due_date:
            raise ValueError("Late submission deadline must be after due date")
        
        if assignment_data.late_penalty_percentage < 0 or assignment_data.late_penalty_percentage > 100:
            raise ValueError("Late penalty percentage must be between 0 and 100")
        
        if assignment_data.weight_percentage < 0 or assignment_data.weight_percentage > 100:
            raise ValueError("Weight percentage must be between 0 and 100")
        
        if assignment_data.total_points <= 0:
            raise ValueError("Total points must be greater than 0")
        
        if assignment_data.max_attempts < 1:
            raise ValueError("Maximum attempts must be at least 1")
    
    def _validate_exam_data(self, exam_data: ExamCreate) -> None:
        """Validate exam data"""
        if exam_data.exam_date < date.today():
            raise ValueError("Exam date cannot be in the past")
        
        if exam_data.start_time >= exam_data.end_time:
            raise ValueError("Start time must be before end time")
        
        if exam_data.weight_percentage < 0 or exam_data.weight_percentage > 100:
            raise ValueError("Weight percentage must be between 0 and 100")
        
        if exam_data.total_points <= 0:
            raise ValueError("Total points must be greater than 0")
        
        if exam_data.passing_grade < 0 or exam_data.passing_grade > 100:
            raise ValueError("Passing grade must be between 0 and 100")
        
        if exam_data.duration_minutes and exam_data.duration_minutes <= 0:
            raise ValueError("Duration must be greater than 0")
    
    def _validate_grade_data(self, grade_data: GradeCreate) -> None:
        """Validate grade data"""
        if grade_data.points_earned < 0:
            raise ValueError("Points earned cannot be negative")
        
        if grade_data.points_possible <= 0:
            raise ValueError("Points possible must be greater than 0")
        
        if grade_data.points_earned > grade_data.points_possible:
            raise ValueError("Points earned cannot exceed points possible")
        
        if grade_data.percentage < 0 or grade_data.percentage > 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        if grade_data.late_penalty_applied < 0 or grade_data.late_penalty_applied > 100:
            raise ValueError("Late penalty must be between 0 and 100")
        
        if grade_data.extra_credit < 0:
            raise ValueError("Extra credit cannot be negative")
        
        if grade_data.curve_adjustment < -50 or grade_data.curve_adjustment > 50:
            raise ValueError("Curve adjustment must be between -50 and 50")
    
    def _validate_gradebook_data(self, gradebook_data: GradebookCreate) -> None:
        """Validate gradebook data"""
        total_weight = gradebook_data.assignment_weight + gradebook_data.exam_weight + gradebook_data.participation_weight
        if abs(total_weight - 100.0) > 0.01:  # Allow small floating point differences
            raise ValueError("Gradebook weights must sum to 100%")
        
        if gradebook_data.pass_fail_threshold < 0 or gradebook_data.pass_fail_threshold > 100:
            raise ValueError("Pass/fail threshold must be between 0 and 100")
        
        if gradebook_data.curve_percentage < 0 or gradebook_data.curve_percentage > 50:
            raise ValueError("Curve percentage must be between 0 and 50")
        
        if gradebook_data.drop_lowest_assignments < 0:
            raise ValueError("Drop lowest assignments cannot be negative")
        
        if gradebook_data.drop_lowest_exams < 0:
            raise ValueError("Drop lowest exams cannot be negative")
        
        if gradebook_data.year < 2000 or gradebook_data.year > 3000:
            raise ValueError("Year must be between 2000 and 3000")
    
    def _calculate_letter_grade(self, percentage: float, grade_scale: Optional[Dict[str, float]] = None) -> str:
        """Calculate letter grade from percentage"""
        if grade_scale is None:
            # Default grade scale
            grade_scale = {
                "A+": 97, "A": 93, "A-": 90,
                "B+": 87, "B": 83, "B-": 80,
                "C+": 77, "C": 73, "C-": 70,
                "D+": 67, "D": 63, "D-": 60,
                "F": 0
            }
        
        for grade, threshold in grade_scale.items():
            if percentage >= threshold:
                return grade
        
        return "F"
    
    def _apply_grade_curve(self, grades: List[float], curve_percentage: float) -> List[float]:
        """Apply curve to a list of grades"""
        if not grades or curve_percentage == 0:
            return grades
        
        # Calculate the curve adjustment
        max_grade = max(grades)
        curve_adjustment = (100 - max_grade) * (curve_percentage / 100)
        
        # Apply curve to all grades
        curved_grades = [min(100.0, grade + curve_adjustment) for grade in grades]
        
        return curved_grades
    
    def _calculate_grade_statistics(self, grades: List[float]) -> Dict[str, float]:
        """Calculate comprehensive grade statistics"""
        if not grades:
            return {
                "mean": 0.0,
                "median": 0.0,
                "mode": 0.0,
                "standard_deviation": 0.0,
                "variance": 0.0,
                "min": 0.0,
                "max": 0.0,
                "range": 0.0,
                "quartile_1": 0.0,
                "quartile_3": 0.0,
                "interquartile_range": 0.0
            }
        
        grades_sorted = sorted(grades)
        n = len(grades)
        
        return {
            "mean": statistics.mean(grades),
            "median": statistics.median(grades),
            "mode": statistics.mode(grades) if len(set(grades)) < len(grades) else grades[0],
            "standard_deviation": statistics.stdev(grades) if n > 1 else 0.0,
            "variance": statistics.variance(grades) if n > 1 else 0.0,
            "min": min(grades),
            "max": max(grades),
            "range": max(grades) - min(grades),
            "quartile_1": grades_sorted[n // 4] if n >= 4 else grades_sorted[0],
            "quartile_3": grades_sorted[3 * n // 4] if n >= 4 else grades_sorted[-1],
            "interquartile_range": grades_sorted[3 * n // 4] - grades_sorted[n // 4] if n >= 4 else 0.0
        }
