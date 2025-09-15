"""
Course controller - General course endpoints with authentication
Provides centralized course access with role-based filtering
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from config.database import get_db
from config.auth import get_current_active_user
from models import User, Student, Professor, Course, student_course_association, UserRole
from schemas.student_schemas import (
    CourseResponse,
    CourseWithProfessor,
    CourseWithStudents,
    StudentResponse
)

router = APIRouter()

@router.get("/", response_model=List[CourseWithProfessor])
async def get_all_courses(
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    year: Optional[int] = Query(None, description="Filter by year"),
    keyword: Optional[str] = Query(None, description="Search in course title or description"),
    include_inactive: bool = Query(False, description="Include inactive courses (professors only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all courses with role-based filtering
    - Students: Only see active courses
    - Professors: Can see all courses, including inactive ones if requested
    """
    query = db.query(Course)
    
    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        # Students only see active courses
        query = query.filter(Course.is_active == True)
    elif current_user.role == UserRole.PROFESSOR:
        # Professors can choose to see inactive courses
        if not include_inactive:
            query = query.filter(Course.is_active == True)
    
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
    
    # Build response with professor info and enrollment data
    result = []
    for course in courses:
        professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
        enrolled_count = db.query(student_course_association).filter(
            student_course_association.c.course_id == course.id
        ).count()
        
        # Build course data
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
        
        # Role-specific data enhancement
        if current_user.role == UserRole.STUDENT:
            # Check if current student is enrolled
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if student:
                is_enrolled = db.query(student_course_association).filter(
                    and_(
                        student_course_association.c.student_id == student.id,
                        student_course_association.c.course_id == course.id
                    )
                ).first() is not None
                course_dict["is_enrolled"] = is_enrolled
            else:
                course_dict["is_enrolled"] = False
        elif current_user.role == UserRole.PROFESSOR:
            # Check if current professor teaches this course
            professor = db.query(Professor).filter(Professor.user_id == current_user.id).first()
            if professor:
                is_teaching = course.professor_id == professor.id
                course_dict["is_teaching"] = is_teaching
            else:
                course_dict["is_teaching"] = False
        
        result.append(course_dict)
    
    return result

@router.get("/{course_id}", response_model=CourseWithProfessor)
async def get_course_by_id(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific course details by ID
    Returns different levels of detail based on user role
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Students can only see active courses unless they're enrolled
    if current_user.role == UserRole.STUDENT and not course.is_active:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            is_enrolled = db.query(student_course_association).filter(
                and_(
                    student_course_association.c.student_id == student.id,
                    student_course_association.c.course_id == course.id
                )
            ).first() is not None
            if not is_enrolled:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
    
    # Get professor and enrollment info
    professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
    enrolled_count = db.query(student_course_association).filter(
        student_course_association.c.course_id == course.id
    ).count()
    
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
        "enrolled_count": enrolled_count,
        "professor": professor
    }
    
    # Add role-specific information
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            is_enrolled = db.query(student_course_association).filter(
                and_(
                    student_course_association.c.student_id == student.id,
                    student_course_association.c.course_id == course.id
                )
            ).first() is not None
            course_dict["is_enrolled"] = is_enrolled
        else:
            course_dict["is_enrolled"] = False
    elif current_user.role == UserRole.PROFESSOR:
        professor = db.query(Professor).filter(Professor.user_id == current_user.id).first()
        if professor:
            is_teaching = course.professor_id == professor.id
            course_dict["is_teaching"] = is_teaching
            
            # If teaching this course, include student list
            if is_teaching:
                students = db.query(Student).join(
                    student_course_association,
                    Student.id == student_course_association.c.student_id
                ).filter(
                    student_course_association.c.course_id == course.id
                ).all()
                course_dict["enrolled_students"] = students
        else:
            course_dict["is_teaching"] = False
    
    return course_dict

@router.get("/{course_id}/enrollment")
async def get_course_enrollment(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get course enrollment information
    - Students: Basic enrollment stats
    - Professors: Detailed student list if teaching the course
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Basic enrollment stats available to all authenticated users
    enrolled_count = db.query(student_course_association).filter(
        student_course_association.c.course_id == course_id
    ).count()
    
    result = {
        "course_id": course_id,
        "course_code": course.course_code,
        "course_title": course.title,
        "enrolled_count": enrolled_count,
        "max_enrollment": course.max_enrollment,
        "available_spots": max(0, course.max_enrollment - enrolled_count),
        "enrollment_percentage": (enrolled_count / course.max_enrollment * 100) if course.max_enrollment > 0 else 0
    }
    
    # Detailed information for professors teaching the course
    if current_user.role == UserRole.PROFESSOR:
        professor = db.query(Professor).filter(Professor.user_id == current_user.id).first()
        if professor and course.professor_id == professor.id:
            # Get enrolled students with details
            students = db.query(Student).join(
                student_course_association,
                Student.id == student_course_association.c.student_id
            ).filter(
                student_course_association.c.course_id == course_id
            ).all()
            
            # Year level distribution
            year_level_stats = {}
            for student in students:
                year_level = student.year_level or "Unknown"
                year_level_stats[year_level] = year_level_stats.get(year_level, 0) + 1
            
            result.update({
                "enrolled_students": students,
                "year_level_distribution": year_level_stats,
                "can_manage": True
            })
        else:
            result["can_manage"] = False
    elif current_user.role == UserRole.STUDENT:
        # Check if student is enrolled
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            is_enrolled = db.query(student_course_association).filter(
                and_(
                    student_course_association.c.student_id == student.id,
                    student_course_association.c.course_id == course_id
                )
            ).first() is not None
            result["is_enrolled"] = is_enrolled
        else:
            result["is_enrolled"] = False
    
    return result

@router.get("/departments/list")
async def get_departments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all departments offering courses"""
    departments = db.query(Course.department).distinct().all()
    return {"departments": [dept[0] for dept in departments if dept[0]]}

@router.get("/semesters/list")
async def get_semesters(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all available semesters"""
    semesters = db.query(Course.semester, Course.year).distinct().order_by(Course.year.desc(), Course.semester).all()
    return {"semesters": [{"semester": sem[0], "year": sem[1]} for sem in semesters]}
