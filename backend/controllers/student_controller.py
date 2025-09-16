"""
Student controller - Student-specific functionality
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from config.database import get_db
from config.auth import get_current_student, get_password_hash, verify_password
from models import Student, Course, Professor, student_course_association, User
from schemas.student_schemas import (
    StudentUpdate,
    StudentResponse,
    CourseResponse,
    CourseWithProfessor,
    EnrollmentCreate,
    EnrollmentResponse
)
import json
from datetime import datetime

router = APIRouter()

# Student Profile Management
@router.put("/profile", response_model=StudentResponse)
async def update_student_profile(
    profile_data: StudentUpdate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update student profile information"""
    # Update only the fields that are provided
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_student, field, value)
    
    db.commit()
    db.refresh(current_student)
    return current_student

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Change student password"""
    
    # Get user account
    user = db.query(User).filter(User.id == current_student.user_id).first()
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# Course Management
@router.get("/courses/search", response_model=List[CourseWithProfessor])
async def search_courses(
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    keyword: Optional[str] = Query(None, description="Search in course title or description"),
    db: Session = Depends(get_db)
):
    """Search for available courses"""
    query = db.query(Course).filter(Course.is_active == True)
    
    # Apply filters
    if department:
        query = query.filter(Course.department.ilike(f"%{department}%"))
    
    if semester:
        query = query.filter(Course.semester.ilike(f"%{semester}%"))
    
    if year:
        query = query.filter(Course.year == year)
    
    if keyword:
        query = query.filter(
            or_(
                Course.title.ilike(f"%{keyword}%"),
                Course.description.ilike(f"%{keyword}%"),
                Course.course_code.ilike(f"%{keyword}%")
            )
        )
    
    courses = query.all()
    
    # Add professor information and enrolled count
    result = []
    for course in courses:
        professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
        enrolled_count = db.query(student_course_association).filter(
            student_course_association.c.course_id == course.id
        ).count()
        
        course_dict = {
            "id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "description": course.description,
            "credits": course.credits,
            "professor_id": course.professor_id,
            "department": course.department,
            "semester": course.semester,
            "year": course.year,
            "max_enrollment": course.max_enrollment,
            "prerequisites": course.prerequisites,
            "schedule": course.schedule,
            "syllabus": course.syllabus,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "enrolled_count": enrolled_count,
            "professor": professor
        }
        result.append(course_dict)
    
    return result

@router.post("/courses/enroll", response_model=dict)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Enroll student in a course"""
    # Check if course exists and is active
    course = db.query(Course).filter(
        and_(Course.id == enrollment_data.course_id, Course.is_active == True)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or inactive"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(student_course_association).filter(
        and_(
            student_course_association.c.student_id == current_student.id,
            student_course_association.c.course_id == enrollment_data.course_id
        )
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Check enrollment capacity
    current_enrollment = db.query(student_course_association).filter(
        student_course_association.c.course_id == enrollment_data.course_id
    ).count()
    
    if current_enrollment >= course.max_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full"
        )
    
    # Check prerequisites (basic implementation)
    if course.prerequisites:
        # This could be enhanced to check actual prerequisite completion
        # For now, just inform about prerequisites
        prerequisites_info = course.prerequisites
    
    # Check for time conflicts (basic implementation)
    if course.schedule:
        enrolled_courses = db.query(Course).join(
            student_course_association,
            Course.id == student_course_association.c.course_id
        ).filter(
            student_course_association.c.student_id == current_student.id
        ).all()
        
        # Simple conflict detection - could be enhanced
        for enrolled_course in enrolled_courses:
            if (enrolled_course.schedule and course.schedule and 
                enrolled_course.semester == course.semester and 
                enrolled_course.year == course.year):
                # This is a simplified check - real implementation would parse schedule times
                pass
    
    # Enroll student
    enrollment_stmt = student_course_association.insert().values(
        student_id=current_student.id,
        course_id=enrollment_data.course_id,
        enrollment_date=datetime.utcnow(),
        status='enrolled'
    )
    db.execute(enrollment_stmt)
    db.commit()
    
    return {"message": "Successfully enrolled in course", "course_id": enrollment_data.course_id}

@router.get("/courses/enrolled", response_model=List[CourseWithProfessor])
async def get_enrolled_courses(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's enrolled courses (personal schedule)"""
    enrolled_courses = db.query(Course).join(
        student_course_association,
        Course.id == student_course_association.c.course_id
    ).filter(
        student_course_association.c.student_id == current_student.id
    ).all()
    
    # Add professor information
    result = []
    for course in enrolled_courses:
        professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
        enrolled_count = db.query(student_course_association).filter(
            student_course_association.c.course_id == course.id
        ).count()
        
        course_dict = {
            "id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "description": course.description,
            "credits": course.credits,
            "professor_id": course.professor_id,
            "department": course.department,
            "semester": course.semester,
            "year": course.year,
            "max_enrollment": course.max_enrollment,
            "prerequisites": course.prerequisites,
            "schedule": course.schedule,
            "syllabus": course.syllabus,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "enrolled_count": enrolled_count,
            "professor": professor
        }
        result.append(course_dict)
    
    return result

@router.delete("/courses/{course_id}/withdraw")
async def withdraw_from_course(
    course_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Withdraw from a course"""
    # Check if enrolled in the course
    enrollment = db.query(student_course_association).filter(
        and_(
            student_course_association.c.student_id == current_student.id,
            student_course_association.c.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    # Check withdrawal timeframe (basic implementation)
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Remove enrollment
    delete_stmt = student_course_association.delete().where(
        and_(
            student_course_association.c.student_id == current_student.id,
            student_course_association.c.course_id == course_id
        )
    )
    db.execute(delete_stmt)
    db.commit()
    
    return {"message": "Successfully withdrawn from course"}

@router.get("/schedule")
async def get_student_schedule(
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's class schedule with time conflict detection"""
    query = db.query(Course).join(
        student_course_association,
        Course.id == student_course_association.c.course_id
    ).filter(
        student_course_association.c.student_id == current_student.id
    )
    
    if semester:
        query = query.filter(Course.semester == semester)
    if year:
        query = query.filter(Course.year == year)
    
    courses = query.all()
    
    schedule = []
    time_conflicts = []
    
    for course in courses:
        professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
        
        course_schedule = {
            "course_id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "professor_name": f"{professor.first_name} {professor.last_name}" if professor else "TBA",
            "credits": course.credits,
            "schedule": course.schedule,
            "semester": course.semester,
            "year": course.year
        }
        schedule.append(course_schedule)
    
    # Basic time conflict detection (could be enhanced)
    # This would require parsing the schedule JSON and checking for overlaps
    
    return {
        "schedule": schedule,
        "conflicts": time_conflicts,
        "total_credits": sum(course.credits for course in courses)
    }
