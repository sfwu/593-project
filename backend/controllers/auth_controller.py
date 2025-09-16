"""
Authentication controller - Login, registration, and profile endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from config.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_active_user,
    get_current_student,
    get_current_professor,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User, Student, Professor, UserRole
from schemas.student_schemas import (
    UserLogin, 
    Token, 
    StudentCreate, 
    StudentResponse,
    ProfessorCreate,
    ProfessorResponse,
    UserResponse
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - authenticate user and return JWT token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user.role,
        "user_id": user.id
    }

@router.post("/register/student", response_model=dict)
async def register_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """Register a new student"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == student_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if student ID already exists
    existing_student = db.query(Student).filter(Student.student_id == student_data.student_id).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(student_data.password)
    user = User(
        email=student_data.email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create student profile
    student = Student(
        user_id=user.id,
        student_id=student_data.student_id,
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        phone=student_data.phone,
        address=student_data.address,
        date_of_birth=student_data.date_of_birth,
        major=student_data.major,
        year_level=student_data.year_level
    )
    db.add(student)
    db.commit()
    
    return {"message": "Student registered successfully", "user_id": user.id}

@router.post("/register/professor", response_model=dict)
async def register_professor(professor_data: ProfessorCreate, db: Session = Depends(get_db)):
    """Register a new professor"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == professor_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if professor ID already exists
    existing_professor = db.query(Professor).filter(Professor.professor_id == professor_data.professor_id).first()
    if existing_professor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professor ID already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(professor_data.password)
    user = User(
        email=professor_data.email,
        hashed_password=hashed_password,
        role=UserRole.PROFESSOR
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create professor profile
    professor = Professor(
        user_id=user.id,
        professor_id=professor_data.professor_id,
        first_name=professor_data.first_name,
        last_name=professor_data.last_name,
        phone=professor_data.phone,
        office_location=professor_data.office_location,
        office_hours=professor_data.office_hours,
        department=professor_data.department,
        title=professor_data.title,
        specialization=professor_data.specialization
    )
    db.add(professor)
    db.commit()
    
    return {"message": "Professor registered successfully", "user_id": user.id}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.get("/me/student", response_model=StudentResponse)
async def get_current_student_profile(current_student: Student = Depends(get_current_student)):
    """Get current student profile (students only)"""
    return current_student

@router.get("/me/professor", response_model=ProfessorResponse)
async def get_current_professor_profile(current_professor: Professor = Depends(get_current_professor)):
    """Get current professor profile (professors only)"""
    return current_professor
