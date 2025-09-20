"""
Grading and Assessment Repository - Data access layer for grading and assessment management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case
from models.grading_assessment import (
    Assignment, AssignmentSubmission, Exam, ExamSession, Grade, Gradebook,
    GradebookEntry, GradeStatistics, GradeModification, AssignmentType,
    ExamType, GradeStatus, SubmissionStatus
)
from models.student import Student
from models.course import Course
from models.professor import Professor
from models import student_course_association
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentSubmissionCreate, AssignmentSubmissionUpdate,
    ExamCreate, ExamUpdate, ExamSessionCreate, ExamSessionUpdate,
    GradeCreate, GradeUpdate, GradebookCreate, GradebookUpdate,
    GradebookEntryCreate, GradebookEntryUpdate, GradeStatisticsCreate,
    GradeModificationCreate, BulkGradeCreate, BulkAssignmentCreate,
    AssignmentFilters, ExamFilters, GradeFilters
)
from datetime import datetime, date, timedelta
import json
import statistics

class GradingAssessmentRepository:
    """Repository for grading and assessment data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Assignment Operations
    def create_assignment(self, assignment_data: AssignmentCreate, professor_id: int) -> Assignment:
        """Create a new assignment"""
        assignment = Assignment(
            **assignment_data.dict(),
            professor_id=professor_id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_assignment_by_id(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID"""
        return self.db.query(Assignment).options(
            joinedload(Assignment.course),
            joinedload(Assignment.professor)
        ).filter(Assignment.id == assignment_id).first()
    
    def get_assignments(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        assignment_type: Optional[AssignmentType] = None,
        is_published: Optional[bool] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None
    ) -> List[Assignment]:
        """Get assignments with optional filters"""
        query = self.db.query(Assignment).options(
            joinedload(Assignment.course),
            joinedload(Assignment.professor)
        )
        
        if course_id:
            query = query.filter(Assignment.course_id == course_id)
        if professor_id:
            query = query.filter(Assignment.professor_id == professor_id)
        if assignment_type:
            query = query.filter(Assignment.assignment_type == assignment_type)
        if is_published is not None:
            query = query.filter(Assignment.is_published == is_published)
        if due_date_from:
            query = query.filter(Assignment.due_date >= due_date_from)
        if due_date_to:
            query = query.filter(Assignment.due_date <= due_date_to)
        
        return query.order_by(desc(Assignment.due_date)).all()
    
    def update_assignment(self, assignment_id: int, assignment_data: AssignmentUpdate) -> Optional[Assignment]:
        """Update an assignment"""
        assignment = self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return None
        
        for field, value in assignment_data.dict(exclude_unset=True).items():
            setattr(assignment, field, value)
        
        assignment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Delete an assignment (soft delete)"""
        assignment = self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return False
        
        assignment.is_active = False
        self.db.commit()
        return True
    
    def publish_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Publish an assignment"""
        assignment = self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return None
        
        assignment.is_published = True
        assignment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    # Assignment Submission Operations
    def create_assignment_submission(self, submission_data: AssignmentSubmissionCreate, student_id: int) -> AssignmentSubmission:
        """Create an assignment submission"""
        # Check if assignment exists and is published
        assignment = self.db.query(Assignment).filter(Assignment.id == submission_data.assignment_id).first()
        if not assignment or not assignment.is_published:
            raise ValueError("Assignment not found or not published")
        
        # Check if student is enrolled in the course
        enrollment = self.db.query(student_course_association).filter(
            and_(
                student_course_association.c.student_id == student_id,
                student_course_association.c.course_id == assignment.course_id
            )
        ).first()
        
        if not enrollment:
            raise ValueError("Student not enrolled in course")
        
        # Check attempt limit
        existing_submissions = self.db.query(AssignmentSubmission).filter(
            and_(
                AssignmentSubmission.assignment_id == submission_data.assignment_id,
                AssignmentSubmission.student_id == student_id
            )
        ).count()
        
        if existing_submissions >= assignment.max_attempts:
            raise ValueError("Maximum attempts exceeded")
        
        # Determine if submission is late
        is_late = datetime.utcnow() > assignment.due_date
        late_hours = 0.0
        if is_late:
            late_hours = (datetime.utcnow() - assignment.due_date).total_seconds() / 3600
        
        submission = AssignmentSubmission(
            **submission_data.dict(),
            student_id=student_id,
            is_late=is_late,
            late_hours=late_hours,
            attempt_number=existing_submissions + 1,
            submission_status=SubmissionStatus.SUBMITTED
        )
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
    
    def get_assignment_submissions(
        self,
        assignment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        submission_status: Optional[SubmissionStatus] = None
    ) -> List[AssignmentSubmission]:
        """Get assignment submissions with optional filters"""
        query = self.db.query(AssignmentSubmission).options(
            joinedload(AssignmentSubmission.assignment),
            joinedload(AssignmentSubmission.student)
        )
        
        if assignment_id:
            query = query.filter(AssignmentSubmission.assignment_id == assignment_id)
        if student_id:
            query = query.filter(AssignmentSubmission.student_id == student_id)
        if submission_status:
            query = query.filter(AssignmentSubmission.submission_status == submission_status)
        
        return query.order_by(desc(AssignmentSubmission.submitted_at)).all()
    
    def update_assignment_submission(self, submission_id: int, submission_data: AssignmentSubmissionUpdate) -> Optional[AssignmentSubmission]:
        """Update an assignment submission"""
        submission = self.db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        if not submission:
            return None
        
        for field, value in submission_data.dict(exclude_unset=True).items():
            setattr(submission, field, value)
        
        if submission_data.professor_feedback:
            submission.feedback_date = datetime.utcnow()
        
        submission.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(submission)
        return submission
    
    # Exam Operations
    def create_exam(self, exam_data: ExamCreate, professor_id: int) -> Exam:
        """Create a new exam"""
        exam = Exam(
            **exam_data.dict(),
            professor_id=professor_id
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam
    
    def get_exam_by_id(self, exam_id: int) -> Optional[Exam]:
        """Get exam by ID"""
        return self.db.query(Exam).options(
            joinedload(Exam.course),
            joinedload(Exam.professor)
        ).filter(Exam.id == exam_id).first()
    
    def get_exams(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        exam_type: Optional[ExamType] = None,
        is_published: Optional[bool] = None,
        exam_date_from: Optional[date] = None,
        exam_date_to: Optional[date] = None
    ) -> List[Exam]:
        """Get exams with optional filters"""
        query = self.db.query(Exam).options(
            joinedload(Exam.course),
            joinedload(Exam.professor)
        )
        
        if course_id:
            query = query.filter(Exam.course_id == course_id)
        if professor_id:
            query = query.filter(Exam.professor_id == professor_id)
        if exam_type:
            query = query.filter(Exam.exam_type == exam_type)
        if is_published is not None:
            query = query.filter(Exam.is_published == is_published)
        if exam_date_from:
            query = query.filter(Exam.exam_date >= exam_date_from)
        if exam_date_to:
            query = query.filter(Exam.exam_date <= exam_date_to)
        
        return query.order_by(Exam.exam_date, Exam.start_time).all()
    
    def update_exam(self, exam_id: int, exam_data: ExamUpdate) -> Optional[Exam]:
        """Update an exam"""
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return None
        
        for field, value in exam_data.dict(exclude_unset=True).items():
            setattr(exam, field, value)
        
        exam.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(exam)
        return exam
    
    def publish_exam(self, exam_id: int) -> Optional[Exam]:
        """Publish an exam"""
        exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return None
        
        exam.is_published = True
        exam.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(exam)
        return exam
    
    # Exam Session Operations
    def create_exam_session(self, session_data: ExamSessionCreate) -> ExamSession:
        """Create an exam session"""
        session = ExamSession(**session_data.dict())
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_exam_sessions(
        self,
        exam_id: Optional[int] = None,
        student_id: Optional[int] = None
    ) -> List[ExamSession]:
        """Get exam sessions with optional filters"""
        query = self.db.query(ExamSession).options(
            joinedload(ExamSession.exam),
            joinedload(ExamSession.student)
        )
        
        if exam_id:
            query = query.filter(ExamSession.exam_id == exam_id)
        if student_id:
            query = query.filter(ExamSession.student_id == student_id)
        
        return query.order_by(desc(ExamSession.session_start_time)).all()
    
    def update_exam_session(self, session_id: int, session_data: ExamSessionUpdate) -> Optional[ExamSession]:
        """Update an exam session"""
        session = self.db.query(ExamSession).filter(ExamSession.id == session_id).first()
        if not session:
            return None
        
        for field, value in session_data.dict(exclude_unset=True).items():
            setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
    
    # Grade Operations
    def create_grade(self, grade_data: GradeCreate, professor_id: int) -> Grade:
        """Create a new grade"""
        # Calculate percentage
        percentage = (grade_data.points_earned / grade_data.points_possible) * 100
        
        # Apply late penalty if applicable
        if grade_data.is_late and grade_data.late_penalty_applied > 0:
            percentage = percentage * (1 - grade_data.late_penalty_applied / 100)
        
        # Apply curve adjustment
        percentage = percentage + grade_data.curve_adjustment
        
        # Add extra credit
        percentage = min(100.0, percentage + grade_data.extra_credit)
        
        grade = Grade(
            **grade_data.dict(),
            professor_id=professor_id,
            percentage=percentage
        )
        
        self.db.add(grade)
        self.db.commit()
        self.db.refresh(grade)
        
        # Update gradebook entry
        self._update_gradebook_entry(grade.student_id, grade.course_id)
        
        return grade
    
    def get_grade_by_id(self, grade_id: int) -> Optional[Grade]:
        """Get grade by ID"""
        return self.db.query(Grade).options(
            joinedload(Grade.student),
            joinedload(Grade.course),
            joinedload(Grade.professor),
            joinedload(Grade.assignment),
            joinedload(Grade.exam)
        ).filter(Grade.id == grade_id).first()
    
    def get_grades(
        self,
        course_id: Optional[int] = None,
        student_id: Optional[int] = None,
        assignment_id: Optional[int] = None,
        exam_id: Optional[int] = None,
        grade_status: Optional[GradeStatus] = None,
        professor_id: Optional[int] = None
    ) -> List[Grade]:
        """Get grades with optional filters"""
        query = self.db.query(Grade).options(
            joinedload(Grade.student),
            joinedload(Grade.course),
            joinedload(Grade.professor),
            joinedload(Grade.assignment),
            joinedload(Grade.exam)
        )
        
        if course_id:
            query = query.filter(Grade.course_id == course_id)
        if student_id:
            query = query.filter(Grade.student_id == student_id)
        if assignment_id:
            query = query.filter(Grade.assignment_id == assignment_id)
        if exam_id:
            query = query.filter(Grade.exam_id == exam_id)
        if grade_status:
            query = query.filter(Grade.grade_status == grade_status)
        if professor_id:
            query = query.filter(Grade.professor_id == professor_id)
        
        return query.order_by(desc(Grade.graded_date)).all()
    
    def update_grade(self, grade_id: int, grade_data: GradeUpdate) -> Optional[Grade]:
        """Update a grade"""
        grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if not grade:
            return None
        
        # Store old values for modification tracking
        old_points = grade.points_earned
        old_percentage = grade.percentage
        old_letter_grade = grade.letter_grade
        
        for field, value in grade_data.dict(exclude_unset=True).items():
            setattr(grade, field, value)
        
        # Recalculate percentage if points changed
        if grade_data.points_earned is not None or grade_data.points_possible is not None:
            percentage = (grade.points_earned / grade.points_possible) * 100
            
            # Apply late penalty if applicable
            if grade.is_late and grade.late_penalty_applied > 0:
                percentage = percentage * (1 - grade.late_penalty_applied / 100)
            
            # Apply curve adjustment
            percentage = percentage + grade.curve_adjustment
            
            # Add extra credit
            percentage = min(100.0, percentage + grade.extra_credit)
            
            grade.percentage = percentage
        
        # Mark as modified if values changed
        if (grade_data.points_earned is not None and grade_data.points_earned != old_points) or \
           (grade_data.points_possible is not None and grade.points_possible != grade.points_possible):
            grade.is_modified = True
            grade.modification_date = datetime.utcnow()
        
        grade.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grade)
        
        # Update gradebook entry
        self._update_gradebook_entry(grade.student_id, grade.course_id)
        
        return grade
    
    def publish_grade(self, grade_id: int) -> Optional[Grade]:
        """Publish a grade"""
        grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if not grade:
            return None
        
        grade.grade_status = GradeStatus.PUBLISHED
        grade.published_date = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grade)
        return grade
    
    def create_bulk_grades(self, bulk_data: BulkGradeCreate, professor_id: int) -> List[Grade]:
        """Create multiple grades at once"""
        grades = []
        
        for grade_info in bulk_data.grades:
            # Get assignment or exam for points_possible
            points_possible = 100.0  # Default
            if bulk_data.assignment_id:
                assignment = self.db.query(Assignment).filter(Assignment.id == bulk_data.assignment_id).first()
                if assignment:
                    points_possible = assignment.total_points
            elif bulk_data.exam_id:
                exam = self.db.query(Exam).filter(Exam.id == bulk_data.exam_id).first()
                if exam:
                    points_possible = exam.total_points
            
            grade_data = GradeCreate(
                student_id=grade_info["student_id"],
                course_id=bulk_data.course_id,
                assignment_id=bulk_data.assignment_id,
                exam_id=bulk_data.exam_id,
                points_earned=grade_info["points_earned"],
                points_possible=points_possible,
                percentage=0.0,  # Will be calculated
                professor_comments=grade_info.get("comments")
            )
            
            grade = self.create_grade(grade_data, professor_id)
            grades.append(grade)
        
        return grades
    
    # Gradebook Operations
    def create_gradebook(self, gradebook_data: GradebookCreate, professor_id: int) -> Gradebook:
        """Create a new gradebook"""
        gradebook = Gradebook(
            **gradebook_data.dict(),
            professor_id=professor_id
        )
        self.db.add(gradebook)
        self.db.commit()
        self.db.refresh(gradebook)
        
        # Create gradebook entries for all enrolled students
        self._create_gradebook_entries(gradebook.id, gradebook.course_id)
        
        return gradebook
    
    def get_gradebook_by_id(self, gradebook_id: int) -> Optional[Gradebook]:
        """Get gradebook by ID"""
        return self.db.query(Gradebook).options(
            joinedload(Gradebook.course),
            joinedload(Gradebook.professor)
        ).filter(Gradebook.id == gradebook_id).first()
    
    def get_gradebooks(
        self,
        course_id: Optional[int] = None,
        professor_id: Optional[int] = None,
        semester: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Gradebook]:
        """Get gradebooks with optional filters"""
        query = self.db.query(Gradebook).options(
            joinedload(Gradebook.course),
            joinedload(Gradebook.professor)
        )
        
        if course_id:
            query = query.filter(Gradebook.course_id == course_id)
        if professor_id:
            query = query.filter(Gradebook.professor_id == professor_id)
        if semester:
            query = query.filter(Gradebook.semester == semester)
        if year:
            query = query.filter(Gradebook.year == year)
        
        return query.order_by(desc(Gradebook.created_at)).all()
    
    def update_gradebook(self, gradebook_id: int, gradebook_data: GradebookUpdate) -> Optional[Gradebook]:
        """Update a gradebook"""
        gradebook = self.db.query(Gradebook).filter(Gradebook.id == gradebook_id).first()
        if not gradebook:
            return None
        
        for field, value in gradebook_data.dict(exclude_unset=True).items():
            setattr(gradebook, field, value)
        
        gradebook.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(gradebook)
        
        # Recalculate all gradebook entries if weights changed
        if any(field in gradebook_data.dict(exclude_unset=True) for field in 
               ['assignment_weight', 'exam_weight', 'participation_weight', 'curve_enabled', 'curve_percentage']):
            self._recalculate_gradebook_entries(gradebook_id)
        
        return gradebook
    
    def get_gradebook_entries(self, gradebook_id: int) -> List[GradebookEntry]:
        """Get all gradebook entries for a gradebook"""
        return self.db.query(GradebookEntry).options(
            joinedload(GradebookEntry.student)
        ).filter(GradebookEntry.gradebook_id == gradebook_id).all()
    
    def get_gradebook_entry(self, gradebook_id: int, student_id: int) -> Optional[GradebookEntry]:
        """Get specific gradebook entry"""
        return self.db.query(GradebookEntry).options(
            joinedload(GradebookEntry.student)
        ).filter(
            and_(
                GradebookEntry.gradebook_id == gradebook_id,
                GradebookEntry.student_id == student_id
            )
        ).first()
    
    # Grade Statistics Operations
    def calculate_grade_statistics(self, course_id: int, gradebook_id: Optional[int] = None) -> GradeStatistics:
        """Calculate grade statistics for a course"""
        # Get all grades for the course
        grades_query = self.db.query(Grade).filter(Grade.course_id == course_id)
        if gradebook_id:
            # Filter by gradebook if specified
            pass  # Would need to join with gradebook entries
        
        grades = grades_query.all()
        
        if not grades:
            # Return empty statistics
            return GradeStatistics(
                course_id=course_id,
                gradebook_id=gradebook_id,
                total_students=0,
                students_passing=0,
                students_failing=0,
                average_grade=0.0,
                median_grade=0.0,
                highest_grade=0.0,
                lowest_grade=0.0,
                standard_deviation=0.0
            )
        
        # Calculate statistics
        percentages = [grade.percentage for grade in grades]
        total_students = len(grades)
        students_passing = len([g for g in grades if g.percentage >= 60.0])
        students_failing = total_students - students_passing
        
        average_grade = statistics.mean(percentages)
        median_grade = statistics.median(percentages)
        highest_grade = max(percentages)
        lowest_grade = min(percentages)
        standard_deviation = statistics.stdev(percentages) if len(percentages) > 1 else 0.0
        
        # Count letter grades
        a_grades = len([g for g in grades if g.percentage >= 90])
        b_grades = len([g for g in grades if 80 <= g.percentage < 90])
        c_grades = len([g for g in grades if 70 <= g.percentage < 80])
        d_grades = len([g for g in grades if 60 <= g.percentage < 70])
        f_grades = len([g for g in grades if g.percentage < 60])
        
        # Calculate category averages
        assignment_grades = [g for g in grades if g.assignment_id is not None]
        exam_grades = [g for g in grades if g.exam_id is not None]
        
        assignment_average = statistics.mean([g.percentage for g in assignment_grades]) if assignment_grades else 0.0
        exam_average = statistics.mean([g.percentage for g in exam_grades]) if exam_grades else 0.0
        participation_average = 0.0  # Would need to be calculated from participation grades
        
        statistics_obj = GradeStatistics(
            course_id=course_id,
            gradebook_id=gradebook_id,
            total_students=total_students,
            students_passing=students_passing,
            students_failing=students_failing,
            average_grade=average_grade,
            median_grade=median_grade,
            highest_grade=highest_grade,
            lowest_grade=lowest_grade,
            standard_deviation=standard_deviation,
            a_grades=a_grades,
            b_grades=b_grades,
            c_grades=c_grades,
            d_grades=d_grades,
            f_grades=f_grades,
            assignment_average=assignment_average,
            exam_average=exam_average,
            participation_average=participation_average
        )
        
        self.db.add(statistics_obj)
        self.db.commit()
        self.db.refresh(statistics_obj)
        
        return statistics_obj
    
    # Grade Modification Operations
    def create_grade_modification(self, modification_data: GradeModificationCreate, professor_id: int) -> GradeModification:
        """Create a grade modification record"""
        modification = GradeModification(
            **modification_data.dict(),
            professor_id=professor_id
        )
        self.db.add(modification)
        self.db.commit()
        self.db.refresh(modification)
        return modification
    
    def get_grade_modifications(self, grade_id: int) -> List[GradeModification]:
        """Get all modifications for a grade"""
        return self.db.query(GradeModification).options(
            joinedload(GradeModification.professor),
            joinedload(GradeModification.approver)
        ).filter(GradeModification.grade_id == grade_id).order_by(desc(GradeModification.modified_at)).all()
    
    def approve_grade_modification(self, modification_id: int, approver_id: int) -> Optional[GradeModification]:
        """Approve a grade modification"""
        modification = self.db.query(GradeModification).filter(GradeModification.id == modification_id).first()
        if not modification:
            return None
        
        modification.is_approved = True
        modification.approved_by = approver_id
        modification.approval_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(modification)
        return modification
    
    # Private helper methods
    def _create_gradebook_entries(self, gradebook_id: int, course_id: int):
        """Create gradebook entries for all enrolled students"""
        # Get all students enrolled in the course
        students = self.db.query(Student).join(
            student_course_association,
            Student.id == student_course_association.c.student_id
        ).filter(student_course_association.c.course_id == course_id).all()
        
        for student in students:
            entry = GradebookEntry(
                gradebook_id=gradebook_id,
                student_id=student.id
            )
            self.db.add(entry)
        
        self.db.commit()
    
    def _update_gradebook_entry(self, student_id: int, course_id: int):
        """Update gradebook entry for a student"""
        # Find the active gradebook for the course
        gradebook = self.db.query(Gradebook).filter(
            and_(
                Gradebook.course_id == course_id,
                Gradebook.is_active == True
            )
        ).first()
        
        if not gradebook:
            return
        
        entry = self.get_gradebook_entry(gradebook.id, student_id)
        if not entry:
            return
        
        # Get all grades for the student in this course
        grades = self.get_grades(course_id=course_id, student_id=student_id)
        
        # Calculate totals
        total_points_earned = sum(grade.points_earned for grade in grades)
        total_points_possible = sum(grade.points_possible for grade in grades)
        
        if total_points_possible > 0:
            overall_percentage = (total_points_earned / total_points_possible) * 100
        else:
            overall_percentage = 0.0
        
        # Calculate category averages
        assignment_grades = [g for g in grades if g.assignment_id is not None]
        exam_grades = [g for g in grades if g.exam_id is not None]
        
        assignment_average = statistics.mean([g.percentage for g in assignment_grades]) if assignment_grades else 0.0
        exam_average = statistics.mean([g.percentage for g in exam_grades]) if exam_grades else 0.0
        
        # Update entry
        entry.total_points_earned = total_points_earned
        entry.total_points_possible = total_points_possible
        entry.overall_percentage = overall_percentage
        entry.assignment_average = assignment_average
        entry.exam_average = exam_average
        entry.assignments_completed = len(assignment_grades)
        entry.exams_completed = len(exam_grades)
        entry.is_passing = overall_percentage >= gradebook.pass_fail_threshold
        entry.is_at_risk = overall_percentage < 70.0
        entry.needs_attention = overall_percentage < 60.0
        entry.last_calculated = datetime.utcnow()
        
        self.db.commit()
    
    def _recalculate_gradebook_entries(self, gradebook_id: int):
        """Recalculate all gradebook entries for a gradebook"""
        entries = self.get_gradebook_entries(gradebook_id)
        gradebook = self.get_gradebook_by_id(gradebook_id)
        
        if not gradebook:
            return
        
        for entry in entries:
            self._update_gradebook_entry(entry.student_id, gradebook.course_id)
    
    # Analytics and Reporting
    def get_course_grading_summary(self, course_id: int) -> Dict[str, Any]:
        """Get comprehensive grading summary for a course"""
        # Get course info
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return {}
        
        # Get counts
        total_assignments = self.db.query(Assignment).filter(Assignment.course_id == course_id).count()
        total_exams = self.db.query(Exam).filter(Exam.course_id == course_id).count()
        
        # Get enrolled students
        enrolled_students = self.db.query(Student).join(
            student_course_association,
            Student.id == student_course_association.c.student_id
        ).filter(student_course_association.c.course_id == course_id).all()
        
        total_students = len(enrolled_students)
        
        # Get grade statistics
        grades = self.get_grades(course_id=course_id)
        if grades:
            average_grade = statistics.mean([g.percentage for g in grades])
            students_passing = len([g for g in grades if g.percentage >= 60.0])
            students_failing = total_students - students_passing
        else:
            average_grade = 0.0
            students_passing = 0
            students_failing = 0
        
        # Calculate completion rate
        total_possible_grades = total_students * (total_assignments + total_exams)
        actual_grades = len(grades)
        completion_rate = (actual_grades / total_possible_grades * 100) if total_possible_grades > 0 else 0.0
        
        return {
            "course_id": course_id,
            "course_name": course.title,
            "total_assignments": total_assignments,
            "total_exams": total_exams,
            "total_students": total_students,
            "average_grade": round(average_grade, 2),
            "completion_rate": round(completion_rate, 2),
            "students_passing": students_passing,
            "students_failing": students_failing
        }
    
    def get_assignment_analytics(self, assignment_id: int) -> Dict[str, Any]:
        """Get analytics for a specific assignment"""
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return {}
        
        # Get submissions
        submissions = self.get_assignment_submissions(assignment_id=assignment_id)
        total_submissions = len(submissions)
        
        # Get grades
        grades = self.get_grades(assignment_id=assignment_id)
        
        # Calculate statistics
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
        
        # Calculate submission rate
        enrolled_students = self.db.query(Student).join(
            student_course_association,
            Student.id == student_course_association.c.student_id
        ).filter(student_course_association.c.course_id == assignment.course_id).count()
        
        submission_rate = (total_submissions / enrolled_students * 100) if enrolled_students > 0 else 0.0
        
        # Count late submissions
        late_submissions = len([s for s in submissions if s.is_late])
        
        return {
            "assignment_id": assignment_id,
            "assignment_title": assignment.title,
            "total_submissions": total_submissions,
            "submission_rate": round(submission_rate, 2),
            "average_grade": round(average_grade, 2),
            "grade_distribution": grade_distribution,
            "late_submissions": late_submissions
        }
