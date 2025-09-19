"""
Grading and Assessment Controller - API endpoints for grading and assessment management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from config.database import get_db
from config.auth import get_current_professor
from models.professor import Professor
from services.grading_assessment_service import GradingAssessmentService
from schemas.grading_assessment_schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentSubmissionCreate, AssignmentSubmissionUpdate, AssignmentSubmissionResponse,
    ExamCreate, ExamUpdate, ExamResponse, ExamSessionCreate, ExamSessionUpdate, ExamSessionResponse,
    GradeCreate, GradeUpdate, GradeResponse, GradebookCreate, GradebookUpdate, GradebookResponse,
    GradebookEntryResponse, GradeStatisticsResponse, GradeModificationCreate, GradeModificationResponse,
    BulkGradeCreate, BulkAssignmentCreate, AssignmentFilters, ExamFilters, GradeFilters,
    GradingDashboardSummary, CourseGradingSummary, GradeDistributionReport,
    AssignmentAnalytics, ExamAnalytics, AssignmentType, ExamType, GradeStatus, SubmissionStatus
)
from datetime import datetime, date

router = APIRouter()

# Assignment Management Endpoints
@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new assignment"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_assignment(assignment_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    assignment_type: Optional[AssignmentType] = Query(None, description="Filter by assignment type"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    due_date_from: Optional[datetime] = Query(None, description="Filter from due date"),
    due_date_to: Optional[datetime] = Query(None, description="Filter to due date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get assignments with optional filtering"""
    service = GradingAssessmentService(db)
    return service.get_assignments(
        course_id=course_id,
        professor_id=current_professor.id,
        assignment_type=assignment_type,
        is_published=is_published,
        due_date_from=due_date_from,
        due_date_to=due_date_to
    )

@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific assignment"""
    service = GradingAssessmentService(db)
    assignment = service.get_assignment_by_id(assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment

@router.put("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update an assignment"""
    service = GradingAssessmentService(db)
    assignment = service.update_assignment(assignment_id, assignment_data, current_professor.id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission to modify it"
        )
    
    return assignment

@router.post("/assignments/{assignment_id}/publish", response_model=AssignmentResponse)
async def publish_assignment(
    assignment_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish an assignment"""
    service = GradingAssessmentService(db)
    assignment = service.publish_assignment(assignment_id, current_professor.id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission to publish it"
        )
    
    return assignment

@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Delete an assignment (soft delete)"""
    service = GradingAssessmentService(db)
    success = service.delete_assignment(assignment_id, current_professor.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission to delete it"
        )
    
    return {"message": "Assignment deleted successfully"}

@router.post("/assignments/bulk", response_model=List[AssignmentResponse])
async def create_bulk_assignments(
    bulk_data: BulkAssignmentCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create multiple assignments from a template"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_bulk_assignments(bulk_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Assignment Submission Endpoints
@router.get("/assignments/{assignment_id}/submissions", response_model=List[AssignmentSubmissionResponse])
async def get_assignment_submissions(
    assignment_id: int,
    submission_status: Optional[SubmissionStatus] = Query(None, description="Filter by submission status"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get submissions for a specific assignment"""
    service = GradingAssessmentService(db)
    return service.get_assignment_submissions(
        assignment_id=assignment_id,
        submission_status=submission_status
    )

@router.put("/submissions/{submission_id}", response_model=AssignmentSubmissionResponse)
async def update_assignment_submission(
    submission_id: int,
    submission_data: AssignmentSubmissionUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update an assignment submission (provide feedback)"""
    service = GradingAssessmentService(db)
    submission = service.update_assignment_submission(submission_id, submission_data, current_professor.id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    return submission

# Exam Management Endpoints
@router.post("/exams", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new exam"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_exam(exam_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    exam_type: Optional[ExamType] = Query(None, description="Filter by exam type"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    exam_date_from: Optional[date] = Query(None, description="Filter from exam date"),
    exam_date_to: Optional[date] = Query(None, description="Filter to exam date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get exams with optional filtering"""
    service = GradingAssessmentService(db)
    return service.get_exams(
        course_id=course_id,
        professor_id=current_professor.id,
        exam_type=exam_type,
        is_published=is_published,
        exam_date_from=exam_date_from,
        exam_date_to=exam_date_to
    )

@router.get("/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific exam"""
    service = GradingAssessmentService(db)
    exam = service.get_exam_by_id(exam_id)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )
    
    return exam

@router.put("/exams/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update an exam"""
    service = GradingAssessmentService(db)
    exam = service.update_exam(exam_id, exam_data, current_professor.id)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or you don't have permission to modify it"
        )
    
    return exam

@router.post("/exams/{exam_id}/publish", response_model=ExamResponse)
async def publish_exam(
    exam_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish an exam"""
    service = GradingAssessmentService(db)
    exam = service.publish_exam(exam_id, current_professor.id)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or you don't have permission to publish it"
        )
    
    return exam

# Exam Session Endpoints
@router.post("/exam-sessions", response_model=ExamSessionResponse)
async def create_exam_session(
    session_data: ExamSessionCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create an exam session"""
    service = GradingAssessmentService(db)
    return service.create_exam_session(session_data)

@router.get("/exam-sessions", response_model=List[ExamSessionResponse])
async def get_exam_sessions(
    exam_id: Optional[int] = Query(None, description="Filter by exam"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get exam sessions with optional filtering"""
    service = GradingAssessmentService(db)
    return service.get_exam_sessions(exam_id=exam_id, student_id=student_id)

@router.put("/exam-sessions/{session_id}", response_model=ExamSessionResponse)
async def update_exam_session(
    session_id: int,
    session_data: ExamSessionUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update an exam session"""
    service = GradingAssessmentService(db)
    session = service.update_exam_session(session_id, session_data)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam session not found"
        )
    
    return session

# Grade Management Endpoints
@router.post("/grades", response_model=GradeResponse)
async def create_grade(
    grade_data: GradeCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new grade"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_grade(grade_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/grades", response_model=List[GradeResponse])
async def get_grades(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    assignment_id: Optional[int] = Query(None, description="Filter by assignment"),
    exam_id: Optional[int] = Query(None, description="Filter by exam"),
    grade_status: Optional[GradeStatus] = Query(None, description="Filter by grade status"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get grades with optional filtering"""
    service = GradingAssessmentService(db)
    return service.get_grades(
        course_id=course_id,
        student_id=student_id,
        assignment_id=assignment_id,
        exam_id=exam_id,
        grade_status=grade_status,
        professor_id=current_professor.id
    )

@router.get("/grades/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific grade"""
    service = GradingAssessmentService(db)
    grade = service.get_grade_by_id(grade_id)
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    return grade

@router.put("/grades/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update a grade"""
    service = GradingAssessmentService(db)
    grade = service.update_grade(grade_id, grade_data, current_professor.id)
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found or you don't have permission to modify it"
        )
    
    return grade

@router.post("/grades/{grade_id}/publish", response_model=GradeResponse)
async def publish_grade(
    grade_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish a grade"""
    service = GradingAssessmentService(db)
    grade = service.publish_grade(grade_id, current_professor.id)
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found or you don't have permission to publish it"
        )
    
    return grade

@router.post("/grades/bulk", response_model=List[GradeResponse])
async def create_bulk_grades(
    bulk_data: BulkGradeCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create multiple grades at once"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_bulk_grades(bulk_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Gradebook Management Endpoints
@router.post("/gradebooks", response_model=GradebookResponse)
async def create_gradebook(
    gradebook_data: GradebookCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new gradebook"""
    service = GradingAssessmentService(db)
    
    try:
        return service.create_gradebook(gradebook_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/gradebooks", response_model=List[GradebookResponse])
async def get_gradebooks(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get gradebooks with optional filtering"""
    service = GradingAssessmentService(db)
    return service.get_gradebooks(
        course_id=course_id,
        professor_id=current_professor.id,
        semester=semester,
        year=year
    )

@router.get("/gradebooks/{gradebook_id}", response_model=GradebookResponse)
async def get_gradebook(
    gradebook_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific gradebook"""
    service = GradingAssessmentService(db)
    gradebook = service.get_gradebook_by_id(gradebook_id)
    
    if not gradebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gradebook not found"
        )
    
    return gradebook

@router.put("/gradebooks/{gradebook_id}", response_model=GradebookResponse)
async def update_gradebook(
    gradebook_id: int,
    gradebook_data: GradebookUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update a gradebook"""
    service = GradingAssessmentService(db)
    gradebook = service.update_gradebook(gradebook_id, gradebook_data, current_professor.id)
    
    if not gradebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gradebook not found or you don't have permission to modify it"
        )
    
    return gradebook

@router.get("/gradebooks/{gradebook_id}/entries", response_model=List[GradebookEntryResponse])
async def get_gradebook_entries(
    gradebook_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get all gradebook entries for a gradebook"""
    service = GradingAssessmentService(db)
    return service.get_gradebook_entries(gradebook_id)

@router.get("/gradebooks/{gradebook_id}/entries/{student_id}", response_model=GradebookEntryResponse)
async def get_gradebook_entry(
    gradebook_id: int,
    student_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific gradebook entry"""
    service = GradingAssessmentService(db)
    entry = service.get_gradebook_entry(gradebook_id, student_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gradebook entry not found"
        )
    
    return entry

# Grade Statistics Endpoints
@router.get("/statistics/course/{course_id}", response_model=GradeStatisticsResponse)
async def get_course_grade_statistics(
    course_id: int,
    gradebook_id: Optional[int] = Query(None, description="Filter by gradebook"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get grade statistics for a course"""
    service = GradingAssessmentService(db)
    return service.calculate_grade_statistics(course_id, gradebook_id)

# Grade Modification Endpoints
@router.post("/grade-modifications", response_model=GradeModificationResponse)
async def create_grade_modification(
    modification_data: GradeModificationCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a grade modification record"""
    service = GradingAssessmentService(db)
    return service.create_grade_modification(modification_data, current_professor.id)

@router.get("/grade-modifications/{grade_id}", response_model=List[GradeModificationResponse])
async def get_grade_modifications(
    grade_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get all modifications for a grade"""
    service = GradingAssessmentService(db)
    return service.get_grade_modifications(grade_id)

@router.post("/grade-modifications/{modification_id}/approve", response_model=GradeModificationResponse)
async def approve_grade_modification(
    modification_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Approve a grade modification"""
    service = GradingAssessmentService(db)
    modification = service.approve_grade_modification(modification_id, current_professor.id)
    
    if not modification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade modification not found"
        )
    
    return modification

# Dashboard and Analytics Endpoints
@router.get("/dashboard", response_model=GradingDashboardSummary)
async def get_grading_dashboard(
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get professor grading dashboard summary"""
    service = GradingAssessmentService(db)
    return service.get_grading_dashboard_summary(current_professor.id)

@router.get("/dashboard/course/{course_id}", response_model=CourseGradingSummary)
async def get_course_grading_summary(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get comprehensive grading summary for a course"""
    service = GradingAssessmentService(db)
    return service.get_course_grading_summary(course_id)

@router.get("/analytics/grade-distribution/{course_id}", response_model=GradeDistributionReport)
async def get_grade_distribution_report(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Generate grade distribution report for a course"""
    service = GradingAssessmentService(db)
    
    try:
        return service.get_grade_distribution_report(course_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/analytics/assignment/{assignment_id}", response_model=AssignmentAnalytics)
async def get_assignment_analytics(
    assignment_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific assignment"""
    service = GradingAssessmentService(db)
    
    try:
        return service.get_assignment_analytics(assignment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/analytics/exam/{exam_id}", response_model=ExamAnalytics)
async def get_exam_analytics(
    exam_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific exam"""
    service = GradingAssessmentService(db)
    
    try:
        return service.get_exam_analytics(exam_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Search and Filter Endpoints
@router.get("/search/assignments")
async def search_assignments(
    query: str = Query(..., description="Search query"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Search assignments by title or description"""
    service = GradingAssessmentService(db)
    
    # Simple search implementation
    assignments = service.get_assignments(professor_id=current_professor.id)
    
    # Filter by search query
    filtered_assignments = [
        assignment for assignment in assignments
        if query.lower() in assignment.title.lower() or 
           (assignment.description and query.lower() in assignment.description.lower())
    ]
    
    return {
        "query": query,
        "results": filtered_assignments,
        "total": len(filtered_assignments)
    }

@router.get("/search/exams")
async def search_exams(
    query: str = Query(..., description="Search query"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Search exams by title or description"""
    service = GradingAssessmentService(db)
    
    # Simple search implementation
    exams = service.get_exams(professor_id=current_professor.id)
    
    # Filter by search query
    filtered_exams = [
        exam for exam in exams
        if query.lower() in exam.title.lower() or 
           (exam.description and query.lower() in exam.description.lower())
    ]
    
    return {
        "query": query,
        "results": filtered_exams,
        "total": len(filtered_exams)
    }

# Bulk Operations Endpoints
@router.post("/bulk/publish-grades")
async def bulk_publish_grades(
    grade_ids: List[int],
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish multiple grades at once"""
    service = GradingAssessmentService(db)
    
    published_grades = []
    failed_grades = []
    
    for grade_id in grade_ids:
        try:
            grade = service.publish_grade(grade_id, current_professor.id)
            if grade:
                published_grades.append(grade)
            else:
                failed_grades.append({"grade_id": grade_id, "error": "Grade not found or no permission"})
        except Exception as e:
            failed_grades.append({"grade_id": grade_id, "error": str(e)})
    
    return {
        "published_count": len(published_grades),
        "failed_count": len(failed_grades),
        "published_grades": published_grades,
        "failed_grades": failed_grades
    }

@router.post("/bulk/publish-assignments")
async def bulk_publish_assignments(
    assignment_ids: List[int],
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish multiple assignments at once"""
    service = GradingAssessmentService(db)
    
    published_assignments = []
    failed_assignments = []
    
    for assignment_id in assignment_ids:
        try:
            assignment = service.publish_assignment(assignment_id, current_professor.id)
            if assignment:
                published_assignments.append(assignment)
            else:
                failed_assignments.append({"assignment_id": assignment_id, "error": "Assignment not found or no permission"})
        except Exception as e:
            failed_assignments.append({"assignment_id": assignment_id, "error": str(e)})
    
    return {
        "published_count": len(published_assignments),
        "failed_count": len(failed_assignments),
        "published_assignments": published_assignments,
        "failed_assignments": failed_assignments
    }
