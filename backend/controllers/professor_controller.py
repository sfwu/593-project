"""
Professor controller - Professor-specific functionality
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from config.database import get_db
from config.auth import get_current_professor, get_password_hash
from models.student import Professor, Course, Student, student_course_association, User
from schemas.student_schemas import (
    ProfessorUpdate,
    ProfessorResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseWithStudents,
    StudentResponse
)
from datetime import datetime

router = APIRouter()

# Professor Profile Management
@router.put("/profile", response_model=ProfessorResponse)
async def update_professor_profile(
    profile_data: ProfessorUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update professor profile information"""
    # Update only the fields that are provided
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_professor, field, value)
    
    db.commit()
    db.refresh(current_professor)
    return current_professor

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Change professor password"""
    from config.auth import verify_password
    
    # Get user account
    user = db.query(User).filter(User.id == current_professor.user_id).first()
    
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

@router.get("/profile/teaching-load")
async def get_teaching_load(
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get professor's teaching load and schedule"""
    query = db.query(Course).filter(
        and_(Course.professor_id == current_professor.id, Course.is_active == True)
    )
    
    if semester:
        query = query.filter(Course.semester == semester)
    if year:
        query = query.filter(Course.year == year)
    
    courses = query.all()
    
    # Calculate teaching load
    total_credits = sum(course.credits for course in courses)
    total_students = 0
    course_list = []
    
    for course in courses:
        enrolled_count = db.query(student_course_association).filter(
            student_course_association.c.course_id == course.id
        ).count()
        total_students += enrolled_count
        
        course_info = {
            "course_id": course.id,
            "course_code": course.course_code,
            "title": course.title,
            "credits": course.credits,
            "enrolled_count": enrolled_count,
            "max_enrollment": course.max_enrollment,
            "schedule": course.schedule,
            "semester": course.semester,
            "year": course.year
        }
        course_list.append(course_info)
    
    return {
        "courses": course_list,
        "total_courses": len(courses),
        "total_credits": total_credits,
        "total_students": total_students,
        "department": current_professor.department
    }

# Course Administration
@router.post("/courses", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new course offering"""
    # Check if course code already exists for the same semester/year
    existing_course = db.query(Course).filter(
        and_(
            Course.course_code == course_data.course_code,
            Course.semester == course_data.semester,
            Course.year == course_data.year
        )
    ).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this code already exists for the specified semester/year"
        )
    
    # Create new course
    course = Course(
        course_code=course_data.course_code,
        title=course_data.title,
        description=course_data.description,
        credits=course_data.credits,
        professor_id=current_professor.id,
        department=course_data.department,
        semester=course_data.semester,
        year=course_data.year,
        max_enrollment=course_data.max_enrollment,
        prerequisites=course_data.prerequisites,
        schedule=course_data.schedule,
        syllabus=course_data.syllabus
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Add enrolled_count for response
    course.enrolled_count = 0
    
    return course

@router.get("/courses", response_model=List[CourseResponse])
async def get_professor_courses(
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    include_inactive: bool = Query(False, description="Include inactive courses"),
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get courses taught by the professor"""
    query = db.query(Course).filter(Course.professor_id == current_professor.id)
    
    if not include_inactive:
        query = query.filter(Course.is_active == True)
    
    if semester:
        query = query.filter(Course.semester == semester)
    if year:
        query = query.filter(Course.year == year)
    
    courses = query.all()
    
    # Add enrolled count for each course
    result = []
    for course in courses:
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
            "enrolled_count": enrolled_count
        }
        result.append(course_dict)
    
    return result

@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update course information"""
    # Check if course exists and belongs to current professor
    course = db.query(Course).filter(
        and_(Course.id == course_id, Course.professor_id == current_professor.id)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission to modify it"
        )
    
    # Update only the fields that are provided
    for field, value in course_data.dict(exclude_unset=True).items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    # Add enrolled_count for response
    enrolled_count = db.query(student_course_association).filter(
        student_course_association.c.course_id == course.id
    ).count()
    course.enrolled_count = enrolled_count
    
    return course

@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Deactivate a course (soft delete)"""
    # Check if course exists and belongs to current professor
    course = db.query(Course).filter(
        and_(Course.id == course_id, Course.professor_id == current_professor.id)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission to modify it"
        )
    
    # Check if there are enrolled students
    enrolled_count = db.query(student_course_association).filter(
        student_course_association.c.course_id == course.id
    ).count()
    
    if enrolled_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete course with enrolled students. Please remove all students first."
        )
    
    # Soft delete (deactivate) the course
    course.is_active = False
    db.commit()
    
    return {"message": "Course deactivated successfully"}

# Enrollment Management
@router.get("/courses/{course_id}/students", response_model=CourseWithStudents)
async def get_course_students(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get list of students enrolled in a specific course"""
    # Check if course exists and belongs to current professor
    course = db.query(Course).filter(
        and_(Course.id == course_id, Course.professor_id == current_professor.id)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission to access it"
        )
    
    # Get enrolled students
    students = db.query(Student).join(
        student_course_association,
        Student.id == student_course_association.c.student_id
    ).filter(
        student_course_association.c.course_id == course_id
    ).all()
    
    # Build response
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
        "enrolled_count": len(students),
        "enrolled_students": students
    }
    
    return course_dict

@router.delete("/courses/{course_id}/students/{student_id}")
async def remove_student_from_course(
    course_id: int,
    student_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Remove a student from the course"""
    # Check if course exists and belongs to current professor
    course = db.query(Course).filter(
        and_(Course.id == course_id, Course.professor_id == current_professor.id)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission to modify it"
        )
    
    # Check if student is enrolled in the course
    enrollment = db.query(student_course_association).filter(
        and_(
            student_course_association.c.course_id == course_id,
            student_course_association.c.student_id == student_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in this course"
        )
    
    # Remove enrollment
    delete_stmt = student_course_association.delete().where(
        and_(
            student_course_association.c.course_id == course_id,
            student_course_association.c.student_id == student_id
        )
    )
    db.execute(delete_stmt)
    db.commit()
    
    return {"message": "Student removed from course successfully"}

@router.get("/courses/{course_id}/enrollment-stats")
async def get_course_enrollment_stats(
    course_id: int,
    current_professor: Professor = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get enrollment statistics for a course"""
    # Check if course exists and belongs to current professor
    course = db.query(Course).filter(
        and_(Course.id == course_id, Course.professor_id == current_professor.id)
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission to access it"
        )
    
    # Get enrollment statistics
    total_enrolled = db.query(student_course_association).filter(
        student_course_association.c.course_id == course_id
    ).count()
    
    # Get students by year level
    year_level_stats = {}
    students = db.query(Student).join(
        student_course_association,
        Student.id == student_course_association.c.student_id
    ).filter(
        student_course_association.c.course_id == course_id
    ).all()
    
    for student in students:
        year_level = student.year_level or "Unknown"
        year_level_stats[year_level] = year_level_stats.get(year_level, 0) + 1
    
    return {
        "course_id": course_id,
        "course_code": course.course_code,
        "course_title": course.title,
        "total_enrolled": total_enrolled,
        "max_enrollment": course.max_enrollment,
        "enrollment_percentage": (total_enrolled / course.max_enrollment * 100) if course.max_enrollment > 0 else 0,
        "available_spots": max(0, course.max_enrollment - total_enrolled),
        "year_level_distribution": year_level_stats
    }
