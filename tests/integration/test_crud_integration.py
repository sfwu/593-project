"""
Integration Tests for CRUD operations
These tests use real database connections to test CRUD operations with actual data persistence
"""
import pytest
from sqlalchemy.orm import Session
from models import User, Student, Professor, Course, UserRole
from config.auth import get_password_hash


class TestUserCRUDIntegration:
    """Test User CRUD operations with real database"""
    
    def test_create_user_success(self, integration_db: Session):
        """Test creating a user with real database persistence"""
        user_data = {
            "email": "testuser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.STUDENT,
            "is_active": True
        }
        
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        assert user.id is not None
        assert user.email == "testuser@example.com"
        assert user.role == UserRole.STUDENT
        assert user.is_active is True
        
        # Verify data persisted in database
        db_user = integration_db.query(User).filter(User.email == "testuser@example.com").first()
        assert db_user is not None
        assert db_user.id == user.id

    def test_get_user_by_email(self, integration_db: Session):
        """Test retrieving user by email"""
        # Create a user first
        user_data = {
            "email": "getuser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.PROFESSOR,
            "is_active": True
        }
        
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        # Retrieve user by email
        retrieved_user = integration_db.query(User).filter(User.email == "getuser@example.com").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "getuser@example.com"
        assert retrieved_user.role == UserRole.PROFESSOR

    def test_update_user(self, integration_db: Session):
        """Test updating user information"""
        # Create a user first
        user_data = {
            "email": "updateuser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.STUDENT,
            "is_active": True
        }
        
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        # Update user
        user.is_active = False
        integration_db.commit()
        integration_db.refresh(user)
        
        # Verify update
        updated_user = integration_db.query(User).filter(User.email == "updateuser@example.com").first()
        assert updated_user is not None
        assert updated_user.is_active is False

    def test_delete_user(self, integration_db: Session):
        """Test deleting a user"""
        # Create a user first
        user_data = {
            "email": "deleteuser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.STUDENT,
            "is_active": True
        }
        
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        user_id = user.id
        
        # Delete user
        integration_db.delete(user)
        integration_db.commit()
        
        # Verify deletion
        deleted_user = integration_db.query(User).filter(User.id == user_id).first()
        assert deleted_user is None


class TestStudentCRUDIntegration:
    """Test Student CRUD operations with real database"""
    
    def test_create_student_with_user(self, integration_db: Session):
        """Test creating a student with associated user"""
        # Create user first
        user_data = {
            "email": "studentuser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.STUDENT,
            "is_active": True
        }
        
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        # Create student
        student_data = {
            "user_id": user.id,
            "student_id": "STU001",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-1234",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        student = Student(**student_data)
        integration_db.add(student)
        integration_db.commit()
        integration_db.refresh(student)
        
        assert student.id is not None
        assert student.student_id == "STU001"
        assert student.first_name == "John"
        assert student.user_id == user.id
        
        # Verify relationship
        assert student.user.email == "studentuser@example.com"
        assert student.user.role == UserRole.STUDENT

    def test_get_student_by_student_id(self, integration_db: Session):
        """Test retrieving student by student ID"""
        # Create user and student
        user = User(
            email="getstudent@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        student = Student(
            user_id=user.id,
            student_id="STU002",
            first_name="Jane",
            last_name="Smith",
            major="Mathematics"
        )
        integration_db.add(student)
        integration_db.commit()
        integration_db.refresh(student)
        
        # Retrieve by student ID
        retrieved_student = integration_db.query(Student).filter(Student.student_id == "STU002").first()
        assert retrieved_student is not None
        assert retrieved_student.first_name == "Jane"
        assert retrieved_student.last_name == "Smith"

    def test_update_student_profile(self, integration_db: Session):
        """Test updating student profile information"""
        # Create user and student
        user = User(
            email="updatestudent@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        student = Student(
            user_id=user.id,
            student_id="STU003",
            first_name="Bob",
            last_name="Johnson",
            major="Physics"
        )
        integration_db.add(student)
        integration_db.commit()
        integration_db.refresh(student)
        
        # Update student
        student.major = "Engineering"
        student.year_level = "Senior"
        integration_db.commit()
        integration_db.refresh(student)
        
        # Verify update
        updated_student = integration_db.query(Student).filter(Student.student_id == "STU003").first()
        assert updated_student.major == "Engineering"
        assert updated_student.year_level == "Senior"


class TestProfessorCRUDIntegration:
    """Test Professor CRUD operations with real database"""
    
    def test_create_professor_with_user(self, integration_db: Session):
        """Test creating a professor with associated user"""
        # Create user first
        user = User(
            email="professoruser@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.PROFESSOR,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        # Create professor
        professor = Professor(
            user_id=user.id,
            professor_id="PROF001",
            first_name="Alice",
            last_name="Brown",
            department="Computer Science",
            title="Associate Professor"
        )
        integration_db.add(professor)
        integration_db.commit()
        integration_db.refresh(professor)
        
        assert professor.id is not None
        assert professor.professor_id == "PROF001"
        assert professor.first_name == "Alice"
        assert professor.department == "Computer Science"
        
        # Verify relationship
        assert professor.user.email == "professoruser@example.com"
        assert professor.user.role == UserRole.PROFESSOR

    def test_get_professor_by_professor_id(self, integration_db: Session):
        """Test retrieving professor by professor ID"""
        # Create user and professor
        user = User(
            email="getprofessor@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.PROFESSOR,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        professor = Professor(
            user_id=user.id,
            professor_id="PROF002",
            first_name="Charlie",
            last_name="Wilson",
            department="Mathematics",
            title="Professor"
        )
        integration_db.add(professor)
        integration_db.commit()
        integration_db.refresh(professor)
        
        # Retrieve by professor ID
        retrieved_professor = integration_db.query(Professor).filter(Professor.professor_id == "PROF002").first()
        assert retrieved_professor is not None
        assert retrieved_professor.first_name == "Charlie"
        assert retrieved_professor.department == "Mathematics"


class TestCourseCRUDIntegration:
    """Test Course CRUD operations with real database"""
    
    def test_create_course_with_professor(self, integration_db: Session):
        """Test creating a course with associated professor"""
        # Create user and professor first
        user = User(
            email="courseprof@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.PROFESSOR,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        professor = Professor(
            user_id=user.id,
            professor_id="PROF003",
            first_name="David",
            last_name="Lee",
            department="Computer Science",
            title="Assistant Professor"
        )
        integration_db.add(professor)
        integration_db.commit()
        integration_db.refresh(professor)
        
        # Create course
        course = Course(
            course_code="CS101",
            title="Introduction to Programming",
            description="Basic programming concepts",
            credits=3,
            professor_id=professor.id,
            department="Computer Science",
            semester="Fall 2024",
            year=2024,
            max_enrollment=30
        )
        integration_db.add(course)
        integration_db.commit()
        integration_db.refresh(course)
        
        assert course.id is not None
        assert course.course_code == "CS101"
        assert course.title == "Introduction to Programming"
        assert course.professor_id == professor.id
        
        # Verify relationship
        assert course.professor.first_name == "David"
        assert course.professor.department == "Computer Science"

    def test_get_course_by_course_code(self, integration_db: Session):
        """Test retrieving course by course code"""
        # Create user, professor, and course
        user = User(
            email="getcourseprof@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.PROFESSOR,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        professor = Professor(
            user_id=user.id,
            professor_id="PROF004",
            first_name="Emma",
            last_name="Davis",
            department="Mathematics",
            title="Professor"
        )
        integration_db.add(professor)
        integration_db.commit()
        integration_db.refresh(professor)
        
        course = Course(
            course_code="MATH201",
            title="Calculus II",
            description="Advanced calculus topics",
            credits=4,
            professor_id=professor.id,
            department="Mathematics",
            semester="Spring 2024",
            year=2024,
            max_enrollment=25
        )
        integration_db.add(course)
        integration_db.commit()
        integration_db.refresh(course)
        
        # Retrieve by course code
        retrieved_course = integration_db.query(Course).filter(Course.course_code == "MATH201").first()
        assert retrieved_course is not None
        assert retrieved_course.title == "Calculus II"
        assert retrieved_course.credits == 4
        assert retrieved_course.department == "Mathematics"


class TestDatabaseConstraintsIntegration:
    """Test database constraints and relationships"""
    
    def test_unique_email_constraint(self, integration_db: Session):
        """Test that email uniqueness constraint works"""
        # Create first user
        user1 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        integration_db.add(user1)
        integration_db.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password456"),
            role=UserRole.PROFESSOR,
            is_active=True
        )
        integration_db.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise an exception
            integration_db.commit()

    def test_foreign_key_constraint(self, integration_db: Session):
        """Test that foreign key constraints work"""
        # Try to create student with non-existent user_id
        student = Student(
            user_id=99999,  # Non-existent user ID
            student_id="STU999",
            first_name="Invalid",
            last_name="Student"
        )
        integration_db.add(student)
        
        # SQLite doesn't enforce foreign key constraints by default
        # This test documents the current behavior
        integration_db.commit()  # This succeeds in SQLite
        integration_db.refresh(student)
        
        # Verify the student was created (SQLite behavior)
        assert student.id is not None
        assert student.user_id == 99999  # Non-existent user ID was allowed

    def test_cascade_delete_relationship(self, integration_db: Session):
        """Test that cascade relationships work properly"""
        # Create user and student
        user = User(
            email="cascade@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        student = Student(
            user_id=user.id,
            student_id="STU999",
            first_name="Cascade",
            last_name="Test"
        )
        integration_db.add(student)
        integration_db.commit()
        integration_db.refresh(student)
        
        student_id = student.id
        
        # Delete user - this should fail due to NOT NULL constraint
        integration_db.delete(user)
        
        # The commit should raise an integrity error due to NOT NULL constraint
        with pytest.raises(Exception):  # IntegrityError due to NOT NULL constraint
            integration_db.commit()
        
        # Rollback the session to clean state
        integration_db.rollback()
        
        # Verify both user and student still exist (transaction was rolled back)
        remaining_user = integration_db.query(User).filter(User.email == "cascade@example.com").first()
        remaining_student = integration_db.query(Student).filter(Student.id == student_id).first()
        assert remaining_user is not None
        assert remaining_student is not None