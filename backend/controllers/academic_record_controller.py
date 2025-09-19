"""
Academic Record Controller - API endpoints for academic record access
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from config.database import get_db
from config.auth import get_current_student
from models.student import Student
from services.academic_record_service import AcademicRecordService
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate, AcademicRecordResponse,
    TranscriptCreate, TranscriptUpdate, TranscriptResponse,
    AcademicProgressCreate, AcademicProgressUpdate, AcademicProgressResponse,
    SemesterGPAResponse, GPACalculationResponse, TranscriptGenerationRequest,
    TranscriptGenerationResponse, AcademicProgressSummary, StudentGradeHistory,
    GradeStatus
)
import os

router = APIRouter()

# Grade Management Endpoints
@router.get("/grades", response_model=List[AcademicRecordResponse])
async def get_student_grades(
    semester: Optional[str] = Query(None, description="Filter by semester (e.g., Fall 2024)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    status: Optional[GradeStatus] = Query(None, description="Filter by grade status"),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's academic records (grades) with optional filtering"""
    service = AcademicRecordService(db)
    return service.get_student_grades(current_student.id, semester, year, status)

@router.get("/grades/{record_id}", response_model=AcademicRecordResponse)
async def get_grade_details(
    record_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific grade"""
    service = AcademicRecordService(db)
    grades = service.get_student_grades(current_student.id)
    
    # Find the specific grade
    grade = next((g for g in grades if g.id == record_id), None)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    return grade

@router.put("/grades/{record_id}", response_model=AcademicRecordResponse)
async def update_grade(
    record_id: int,
    grade_data: AcademicRecordUpdate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update a grade record (limited fields for students)"""
    service = AcademicRecordService(db)
    
    # Students can only update their own notes
    if any(field in grade_data.dict(exclude_unset=True) for field in ['letter_grade', 'numeric_grade', 'percentage_grade', 'status']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only update their own notes"
        )
    
    updated_grade = service.update_grade(record_id, grade_data, current_student.id)
    if not updated_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )
    
    return updated_grade

# GPA Calculation Endpoints
@router.get("/gpa", response_model=GPACalculationResponse)
async def get_gpa_calculation(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get comprehensive GPA calculation including cumulative, major, and semester breakdown"""
    service = AcademicRecordService(db)
    return service.calculate_gpa(current_student.id)

@router.get("/gpa/semester-breakdown", response_model=List[SemesterGPAResponse])
async def get_semester_gpa_breakdown(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get semester-wise GPA breakdown"""
    service = AcademicRecordService(db)
    return service.get_semester_gpa_breakdown(current_student.id)

@router.get("/gpa/current-semester")
async def get_current_semester_gpa(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get current semester GPA"""
    service = AcademicRecordService(db)
    gpa_data = service.calculate_gpa(current_student.id)
    
    return {
        "current_semester_gpa": gpa_data.semester_gpa,
        "cumulative_gpa": gpa_data.cumulative_gpa,
        "major_gpa": gpa_data.major_gpa,
        "total_credits_earned": gpa_data.total_credits_earned,
        "total_credits_attempted": gpa_data.total_credits_attempted
    }

# Transcript Management Endpoints
@router.post("/transcripts/generate", response_model=TranscriptGenerationResponse)
async def generate_transcript(
    request: TranscriptGenerationRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Generate an official academic transcript"""
    service = AcademicRecordService(db)
    
    try:
        return service.generate_transcript(current_student.id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/transcripts", response_model=List[TranscriptResponse])
async def get_student_transcripts(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get all transcripts for the student"""
    service = AcademicRecordService(db)
    return service.get_student_transcripts(current_student.id)

@router.get("/transcripts/{transcript_id}/download")
async def download_transcript(
    transcript_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Download a transcript file"""
    service = AcademicRecordService(db)
    transcripts = service.get_student_transcripts(current_student.id)
    
    # Find the specific transcript
    transcript = next((t for t in transcripts if t.id == transcript_id), None)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    if not transcript.file_path or not os.path.exists(transcript.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript file not available"
        )
    
    # Return file content
    with open(transcript.file_path, 'rb') as f:
        content = f.read()
    
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=transcript_{current_student.student_id}_{transcript_id}.txt"
        }
    )

# Academic Progress Endpoints
@router.get("/progress", response_model=AcademicProgressResponse)
async def get_academic_progress(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get academic progress information"""
    service = AcademicRecordService(db)
    progress = service.get_academic_progress(current_student.id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic progress not found. Please contact academic advisor."
        )
    
    return progress

@router.get("/progress/summary", response_model=AcademicProgressSummary)
async def get_academic_progress_summary(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get comprehensive academic progress summary"""
    service = AcademicRecordService(db)
    
    try:
        return service.get_academic_progress_summary(current_student.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/progress", response_model=AcademicProgressResponse)
async def update_academic_progress(
    progress_data: AcademicProgressUpdate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update academic progress (limited fields for students)"""
    service = AcademicRecordService(db)
    
    # Students can only update certain fields
    allowed_fields = ['expected_graduation_date']
    update_data = {k: v for k, v in progress_data.dict(exclude_unset=True).items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    updated_progress = service.update_academic_progress(current_student.id, AcademicProgressUpdate(**update_data))
    if not updated_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic progress not found"
        )
    
    return updated_progress

# Grade History and Summary Endpoints
@router.get("/grade-history", response_model=StudentGradeHistory)
async def get_grade_history(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get complete grade history for the student"""
    service = AcademicRecordService(db)
    return service.get_grade_history(current_student.id)

@router.get("/academic-summary")
async def get_academic_summary(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get comprehensive academic summary"""
    service = AcademicRecordService(db)
    
    # Get GPA data
    gpa_data = service.calculate_gpa(current_student.id)
    
    # Get progress summary
    try:
        progress_summary = service.get_academic_progress_summary(current_student.id)
    except ValueError:
        progress_summary = None
    
    # Get grade history
    grade_history = service.get_grade_history(current_student.id)
    
    return {
        "student_info": {
            "student_id": current_student.student_id,
            "name": f"{current_student.first_name} {current_student.last_name}",
            "major": current_student.major,
            "year_level": current_student.year_level
        },
        "gpa_summary": {
            "cumulative_gpa": gpa_data.cumulative_gpa,
            "major_gpa": gpa_data.major_gpa,
            "current_semester_gpa": gpa_data.semester_gpa,
            "total_credits_earned": gpa_data.total_credits_earned,
            "total_credits_attempted": gpa_data.total_credits_attempted
        },
        "progress_summary": progress_summary.dict() if progress_summary else None,
        "grade_statistics": {
            "total_courses": grade_history.total_courses,
            "courses_completed": grade_history.courses_completed,
            "courses_incomplete": grade_history.courses_incomplete,
            "courses_withdrawn": grade_history.courses_withdrawn,
            "grade_distribution": gpa_data.grade_distribution
        },
        "semester_breakdown": [semester.dict() for semester in gpa_data.semester_breakdown]
    }

# Academic Record Dashboard
@router.get("/dashboard")
async def get_academic_dashboard(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get academic dashboard with key metrics and recent activity"""
    service = AcademicRecordService(db)
    
    # Get key metrics
    gpa_data = service.calculate_gpa(current_student.id)
    
    # Get recent grades (last 2 semesters)
    recent_grades = service.get_student_grades(current_student.id)
    recent_grades = [g for g in recent_grades if g.status == GradeStatus.GRADED][:10]  # Last 10 graded courses
    
    # Get progress summary
    try:
        progress_summary = service.get_academic_progress_summary(current_student.id)
    except ValueError:
        progress_summary = None
    
    # Get semester breakdown
    semester_breakdown = service.get_semester_gpa_breakdown(current_student.id)
    
    return {
        "overview": {
            "cumulative_gpa": gpa_data.cumulative_gpa,
            "major_gpa": gpa_data.major_gpa,
            "current_semester_gpa": gpa_data.semester_gpa,
            "total_credits_earned": gpa_data.total_credits_earned,
            "is_on_track": progress_summary.is_on_track if progress_summary else True
        },
        "recent_grades": [grade.dict() for grade in recent_grades],
        "progress": progress_summary.dict() if progress_summary else None,
        "semester_trend": [semester.dict() for semester in semester_breakdown[-6:]],  # Last 6 semesters
        "grade_distribution": gpa_data.grade_distribution
    }

