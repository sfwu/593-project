"""
Student Information Controller - API endpoints for student information management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from config.database import get_db
from config.auth import get_current_professor
from models.professor import Professor
from services.student_information_service import StudentInformationService
from schemas.student_information_schemas import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceSummaryResponse,
    MessageCreate, MessageUpdate, MessageResponse, MessageRecipientResponse,
    StudentDirectoryResponse, StudentDirectoryUpdate,
    StudentPerformanceResponse, StudentPerformanceUpdate,
    CommunicationLogResponse, BulkAttendanceCreate, BulkMessageCreate,
    StudentSearchFilters, AttendanceFilters, MessageFilters,
    StudentDashboardSummary, ProfessorDashboardSummary, AttendanceReport, MessageReport,
    AttendanceStatus, MessageStatus, MessageType, MessagePriority
)
from datetime import datetime, timedelta

router = APIRouter()

# Student Directory Endpoints
@router.get("/directory", response_model=List[StudentDirectoryResponse])
async def get_student_directory(
    name: Optional[str] = Query(None, description="Search by student name"),
    major: Optional[str] = Query(None, description="Filter by major"),
    year_level: Optional[str] = Query(None, description="Filter by year level"),
    enrollment_status: Optional[str] = Query(None, description="Filter by enrollment status"),
    gpa_min: Optional[float] = Query(None, description="Minimum GPA"),
    gpa_max: Optional[float] = Query(None, description="Maximum GPA"),
    is_at_risk: Optional[bool] = Query(None, description="Filter by risk status"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get student directory with optional filtering"""
    service = StudentInformationService(db)
    return service.get_student_directory(
        name, major, year_level, enrollment_status, gpa_min, gpa_max, is_at_risk
    )

@router.get("/directory/{student_id}", response_model=StudentDirectoryResponse)
async def get_student_directory_entry(
    student_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific student directory entry"""
    service = StudentInformationService(db)
    entry = service.get_student_directory_entry(student_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student directory entry not found"
        )
    
    return entry

@router.put("/directory/{student_id}", response_model=StudentDirectoryResponse)
async def update_student_directory_entry(
    student_id: int,
    directory_data: StudentDirectoryUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update student directory entry"""
    service = StudentInformationService(db)
    entry = service.update_student_directory_entry(student_id, directory_data)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student directory entry not found"
        )
    
    return entry

# Academic Records Endpoints
@router.get("/academic-records/{student_id}", response_model=List[StudentPerformanceResponse])
async def get_student_academic_records(
    student_id: int,
    course_id: Optional[int] = Query(None, description="Filter by course"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get student academic records and performance"""
    service = StudentInformationService(db)
    
    if course_id:
        # Get specific course performance
        performance = service.get_student_performance(student_id, course_id)
        return [performance] if performance else []
    else:
        # Get all course performances for the student
        # This would need to be implemented in the service
        return []

@router.get("/academic-records/course/{course_id}", response_model=List[StudentPerformanceResponse])
async def get_course_student_performance(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get performance records for all students in a course"""
    service = StudentInformationService(db)
    return service.get_course_student_performance(course_id)

@router.put("/academic-records/{performance_id}", response_model=StudentPerformanceResponse)
async def update_student_performance(
    performance_id: int,
    performance_data: StudentPerformanceUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update student performance record"""
    service = StudentInformationService(db)
    performance = service.update_student_performance(performance_id, performance_data, current_professor.id)
    
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student performance record not found"
        )
    
    return performance

@router.get("/academic-records/at-risk", response_model=List[StudentPerformanceResponse])
async def get_students_at_risk(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get students at academic risk"""
    service = StudentInformationService(db)
    return service.get_students_at_risk(course_id)

@router.get("/academic-records/risk-assessment/{student_id}")
async def assess_student_risk(
    student_id: int,
    course_id: int = Query(..., description="Course ID for assessment"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Assess if a student is at academic risk"""
    service = StudentInformationService(db)
    return service.assess_student_risk(student_id, course_id)

# Attendance Tracking Endpoints
@router.post("/attendance", response_model=AttendanceResponse)
async def create_attendance(
    attendance_data: AttendanceCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new attendance record"""
    service = StudentInformationService(db)
    
    try:
        return service.create_attendance(attendance_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/attendance/bulk", response_model=List[AttendanceResponse])
async def create_bulk_attendance(
    bulk_data: BulkAttendanceCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create multiple attendance records at once"""
    service = StudentInformationService(db)
    
    try:
        return service.create_bulk_attendance(bulk_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/attendance", response_model=List[AttendanceResponse])
async def get_attendance_records(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    status: Optional[AttendanceStatus] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get attendance records with optional filtering"""
    service = StudentInformationService(db)
    return service.get_attendance_records(
        course_id=course_id,
        student_id=student_id,
        professor_id=current_professor.id,
        date_from=date_from,
        date_to=date_to,
        status=status
    )

@router.get("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance_record(
    attendance_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific attendance record"""
    service = StudentInformationService(db)
    records = service.get_attendance_records(professor_id=current_professor.id)
    
    # Find the specific record
    record = next((r for r in records if r.id == attendance_id), None)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    return record

@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance_record(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update an attendance record"""
    service = StudentInformationService(db)
    attendance = service.update_attendance(attendance_id, attendance_data, current_professor.id)
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    return attendance

@router.get("/attendance/summary/{student_id}", response_model=AttendanceSummaryResponse)
async def get_attendance_summary(
    student_id: int,
    course_id: int = Query(..., description="Course ID"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get attendance summary for a student in a course"""
    service = StudentInformationService(db)
    summary = service.get_attendance_summary(student_id, course_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance summary not found"
        )
    
    return summary

@router.get("/attendance/report/{course_id}", response_model=AttendanceReport)
async def get_attendance_report(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Generate comprehensive attendance report for a course"""
    service = StudentInformationService(db)
    
    try:
        return service.get_course_attendance_report(course_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Student Communication Endpoints
@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new message"""
    service = StudentInformationService(db)
    
    try:
        return service.create_message(message_data, current_professor.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    message_type: Optional[MessageType] = Query(None, description="Filter by message type"),
    status: Optional[MessageStatus] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get messages with optional filtering"""
    service = StudentInformationService(db)
    return service.get_messages(
        sender_id=current_professor.id,
        course_id=course_id,
        message_type=message_type,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get specific message"""
    service = StudentInformationService(db)
    messages = service.get_messages(sender_id=current_professor.id)
    
    # Find the specific message
    message = next((m for m in messages if m.id == message_id), None)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message

@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update a message (only if it's a draft)"""
    service = StudentInformationService(db)
    message = service.update_message(message_id, message_data, current_professor.id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or cannot be updated"
        )
    
    return message

@router.post("/messages/{message_id}/send", response_model=MessageResponse)
async def send_message(
    message_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Send a message"""
    service = StudentInformationService(db)
    message = service.send_message(message_id, current_professor.id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or cannot be sent"
        )
    
    return message

@router.get("/messages/{message_id}/recipients", response_model=List[MessageRecipientResponse])
async def get_message_recipients(
    message_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get all recipients for a message"""
    service = StudentInformationService(db)
    return service.get_message_recipients(message_id)

@router.get("/messages/report", response_model=MessageReport)
async def get_message_report(
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Generate message report for the professor"""
    service = StudentInformationService(db)
    return service.get_message_report(current_professor.id, date_from, date_to)

# Communication Log Endpoints
@router.get("/communication-logs", response_model=List[CommunicationLogResponse])
async def get_communication_logs(
    student_id: Optional[int] = Query(None, description="Filter by student"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    communication_type: Optional[str] = Query(None, description="Filter by communication type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get communication logs with optional filtering"""
    service = StudentInformationService(db)
    return service.get_communication_logs(
        professor_id=current_professor.id,
        student_id=student_id,
        course_id=course_id,
        communication_type=communication_type,
        date_from=date_from,
        date_to=date_to
    )

# Dashboard Endpoints
@router.get("/dashboard", response_model=ProfessorDashboardSummary)
async def get_professor_dashboard(
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get professor dashboard summary"""
    service = StudentInformationService(db)
    return service.get_professor_dashboard_summary(current_professor.id)

@router.get("/dashboard/student/{student_id}", response_model=StudentDashboardSummary)
async def get_student_dashboard(
    student_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get student dashboard summary"""
    service = StudentInformationService(db)
    return service.get_student_dashboard_summary(student_id)

# Bulk Operations Endpoints
@router.post("/bulk/messages", response_model=List[MessageResponse])
async def create_bulk_messages(
    bulk_data: BulkMessageCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create multiple messages at once"""
    service = StudentInformationService(db)
    
    messages = []
    for recipient_id in bulk_data.recipient_ids:
        message_data = MessageCreate(
            course_id=bulk_data.course_id,
            subject=bulk_data.subject,
            content=bulk_data.content,
            message_type=bulk_data.message_type,
            priority=bulk_data.priority,
            recipient_ids=[recipient_id],
            scheduled_at=bulk_data.scheduled_at
        )
        
        try:
            message = service.create_message(message_data, current_professor.id)
            messages.append(message)
        except ValueError as e:
            # Log error but continue with other messages
            continue
    
    return messages

# Search and Analytics Endpoints
@router.get("/search/students")
async def search_students(
    query: str = Query(..., description="Search query"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Search students by name, major, or other criteria"""
    service = StudentInformationService(db)
    
    # Simple search implementation
    students = service.get_student_directory(name=query)
    
    return {
        "query": query,
        "results": students,
        "total": len(students)
    }

@router.get("/analytics/attendance-trends")
async def get_attendance_trends(
    course_id: int = Query(..., description="Course ID"),
    days: int = Query(30, description="Number of days to analyze"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get attendance trends for a course"""
    service = StudentInformationService(db)
    
    # Get attendance records for the specified period
    date_from = datetime.utcnow() - timedelta(days=days)
    attendance_records = service.get_attendance_records(
        course_id=course_id,
        professor_id=current_professor.id,
        date_from=date_from
    )
    
    # Calculate trends
    daily_attendance = {}
    for record in attendance_records:
        date_key = record.attendance_date.date()
        if date_key not in daily_attendance:
            daily_attendance[date_key] = {"present": 0, "absent": 0, "late": 0, "total": 0}
        
        daily_attendance[date_key]["total"] += 1
        if record.status == AttendanceStatus.PRESENT:
            daily_attendance[date_key]["present"] += 1
        elif record.status == AttendanceStatus.ABSENT:
            daily_attendance[date_key]["absent"] += 1
        elif record.status in [AttendanceStatus.LATE, AttendanceStatus.TARDY]:
            daily_attendance[date_key]["late"] += 1
    
    # Calculate percentages
    trends = []
    for date, stats in daily_attendance.items():
        if stats["total"] > 0:
            attendance_percentage = (stats["present"] / stats["total"]) * 100
            trends.append({
                "date": date.isoformat(),
                "attendance_percentage": round(attendance_percentage, 2),
                "present": stats["present"],
                "absent": stats["absent"],
                "late": stats["late"],
                "total": stats["total"]
            })
    
    return {
        "course_id": course_id,
        "period_days": days,
        "trends": sorted(trends, key=lambda x: x["date"])
    }
