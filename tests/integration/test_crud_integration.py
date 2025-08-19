"""
Integration Tests for CRUD operations
These tests use real database connections to test CRUD operations with actual data persistence
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from database import Base
import models
import crud
import schemas

# Create test database in data/ directory
import os
os.makedirs("data", exist_ok=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test_crud_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create test database session for integration testing"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestStudentCRUDIntegration:
    """Integration test class for student CRUD operations with real database"""
    
    def test_create_student_integration(self, test_db):
        """Test creating a student with real database persistence"""
        student_data = schemas.StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            student_id="S12345",
            major="Computer Science",
            gpa=3.8
        )
        
        created_student = crud.create_student(test_db, student_data)
        
        assert created_student.id is not None
        assert created_student.first_name == "John"
        assert created_student.last_name == "Doe"
        assert created_student.email == "john.doe@example.com"
        assert created_student.student_id == "S12345"
        assert created_student.major == "Computer Science"
        assert created_student.gpa == 3.8
        assert created_student.created_at is not None
        
        # Verify data persisted in database
        db_student = test_db.query(models.Student).filter(models.Student.id == created_student.id).first()
        assert db_student is not None
        assert db_student.first_name == "John"
    
    def test_get_student_by_id_integration(self, test_db):
        """Test getting student by ID with real database"""
        # Create a student first
        student_data = schemas.StudentCreate(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            student_id="S12346",
            major="Mathematics"
        )
        created_student = crud.create_student(test_db, student_data)
        
        # Get the student by ID
        retrieved_student = crud.get_student(test_db, created_student.id)
        
        assert retrieved_student is not None
        assert retrieved_student.id == created_student.id
        assert retrieved_student.first_name == "Jane"
        assert retrieved_student.email == "jane.smith@example.com"
    
    def test_get_student_by_id_not_found_integration(self, test_db):
        """Test getting student by ID when not found"""
        retrieved_student = crud.get_student(test_db, 999)
        assert retrieved_student is None
    
    def test_get_student_by_email_integration(self, test_db):
        """Test getting student by email with real database"""
        # Create a student first
        student_data = schemas.StudentCreate(
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            student_id="S12347",
            major="Physics"
        )
        created_student = crud.create_student(test_db, student_data)
        
        # Get the student by email
        retrieved_student = crud.get_student_by_email(test_db, "bob.johnson@example.com")
        
        assert retrieved_student is not None
        assert retrieved_student.id == created_student.id
        assert retrieved_student.email == "bob.johnson@example.com"
    
    def test_get_student_by_email_not_found_integration(self, test_db):
        """Test getting student by email when not found"""
        retrieved_student = crud.get_student_by_email(test_db, "nonexistent@example.com")
        assert retrieved_student is None
    
    def test_get_student_by_student_id_integration(self, test_db):
        """Test getting student by student ID with real database"""
        # Create a student first
        student_data = schemas.StudentCreate(
            first_name="Alice",
            last_name="Brown",
            email="alice.brown@example.com",
            student_id="S12348",
            major="Chemistry"
        )
        created_student = crud.create_student(test_db, student_data)
        
        # Get the student by student ID
        retrieved_student = crud.get_student_by_student_id(test_db, "S12348")
        
        assert retrieved_student is not None
        assert retrieved_student.id == created_student.id
        assert retrieved_student.student_id == "S12348"
    
    def test_get_students_empty_integration(self, test_db):
        """Test getting all students when none exist"""
        students = crud.get_students(test_db)
        assert students == []
    
    def test_get_students_with_data_integration(self, test_db):
        """Test getting all students when data exists"""
        # Create multiple students
        student_data_1 = schemas.StudentCreate(
            first_name="Student",
            last_name="One",
            email="student1@example.com",
            student_id="S001"
        )
        student_data_2 = schemas.StudentCreate(
            first_name="Student",
            last_name="Two",
            email="student2@example.com",
            student_id="S002"
        )
        
        crud.create_student(test_db, student_data_1)
        crud.create_student(test_db, student_data_2)
        
        students = crud.get_students(test_db)
        assert len(students) == 2
        assert students[0].first_name == "Student"
        assert students[1].first_name == "Student"
    
    def test_get_students_pagination_integration(self, test_db):
        """Test getting students with pagination and real database"""
        # Create multiple students
        for i in range(5):
            student_data = schemas.StudentCreate(
                first_name=f"Student{i}",
                last_name="Test",
                email=f"student{i}@example.com",
                student_id=f"S{i:03d}"
            )
            crud.create_student(test_db, student_data)
        
        # Test pagination
        students_page_1 = crud.get_students(test_db, skip=0, limit=2)
        students_page_2 = crud.get_students(test_db, skip=2, limit=2)
        
        assert len(students_page_1) == 2
        assert len(students_page_2) == 2
        assert students_page_1[0].id != students_page_2[0].id
    
    def test_update_student_success_integration(self, test_db):
        """Test updating student successfully with real database persistence"""
        # Create a student first
        student_data = schemas.StudentCreate(
            first_name="Charlie",
            last_name="Wilson",
            email="charlie.wilson@example.com",
            student_id="S12349",
            major="Engineering",
            gpa=3.5
        )
        created_student = crud.create_student(test_db, student_data)
        
        # Update the student
        updated_data = schemas.StudentCreate(
            first_name="Charlie",
            last_name="Wilson-Smith",
            email="charlie.wilson.smith@example.com",
            student_id="S12349",
            major="Software Engineering",
            gpa=3.8
        )
        updated_student = crud.update_student(test_db, created_student.id, updated_data)
        
        assert updated_student is not None
        assert updated_student.last_name == "Wilson-Smith"
        assert updated_student.email == "charlie.wilson.smith@example.com"
        assert updated_student.major == "Software Engineering"
        assert updated_student.gpa == 3.8
        assert updated_student.updated_at is not None
        
        # Verify changes persisted in database
        db_student = test_db.query(models.Student).filter(models.Student.id == created_student.id).first()
        assert db_student.last_name == "Wilson-Smith"
        assert db_student.gpa == 3.8
    
    def test_update_student_not_found_integration(self, test_db):
        """Test updating student when not found"""
        updated_data = schemas.StudentCreate(
            first_name="NonExistent",
            last_name="Student",
            email="nonexistent@example.com",
            student_id="S99999"
        )
        updated_student = crud.update_student(test_db, 999, updated_data)
        assert updated_student is None
    
    def test_delete_student_success_integration(self, test_db):
        """Test deleting student successfully with real database"""
        # Create a student first
        student_data = schemas.StudentCreate(
            first_name="David",
            last_name="Miller",
            email="david.miller@example.com",
            student_id="S12350",
            major="Biology"
        )
        created_student = crud.create_student(test_db, student_data)
        
        # Delete the student
        deleted_student = crud.delete_student(test_db, created_student.id)
        
        assert deleted_student is not None
        assert deleted_student.id == created_student.id
        
        # Verify student is deleted from database
        retrieved_student = crud.get_student(test_db, created_student.id)
        assert retrieved_student is None
        
        # Also verify with direct database query
        db_student = test_db.query(models.Student).filter(models.Student.id == created_student.id).first()
        assert db_student is None
    
    def test_delete_student_not_found_integration(self, test_db):
        """Test deleting student when not found"""
        deleted_student = crud.delete_student(test_db, 999)
        assert deleted_student is None

class TestStudentModelIntegration:
    """Integration test class for student model with real database"""
    
    def test_student_model_creation_integration(self, test_db):
        """Test creating student model directly with database persistence"""
        student = models.Student(
            first_name="Test",
            last_name="Student",
            email="test.student@example.com",
            student_id="TEST001",
            major="Test Major",
            gpa=3.0
        )
        
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)
        
        assert student.id is not None
        assert student.created_at is not None
        assert str(student).startswith("<Student(id=")
        
        # Verify in database
        db_student = test_db.query(models.Student).filter(models.Student.id == student.id).first()
        assert db_student is not None
        assert db_student.first_name == "Test"
    
    def test_student_model_defaults_integration(self, test_db):
        """Test student model with default values and database"""
        student = models.Student(
            first_name="Minimal",
            last_name="Student",
            email="minimal@example.com",
            student_id="MIN001"
        )
        
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)
        
        assert student.major is None
        assert student.gpa == 0.0
        
        # Verify defaults persisted
        db_student = test_db.query(models.Student).filter(models.Student.id == student.id).first()
        assert db_student.major is None
        assert db_student.gpa == 0.0

class TestDatabaseConstraintsIntegration:
    """Integration test class for database constraints"""
    
    def test_unique_email_constraint_integration(self, test_db):
        """Test unique email constraint at database level"""
        # Create first student
        student1 = models.Student(
            first_name="First",
            last_name="Student",
            email="duplicate@example.com",
            student_id="FIRST001"
        )
        test_db.add(student1)
        test_db.commit()
        
        # Try to create second student with same email
        student2 = models.Student(
            first_name="Second",
            last_name="Student",
            email="duplicate@example.com",  # Same email
            student_id="SECOND001"
        )
        test_db.add(student2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLite raises different exceptions
            test_db.commit()
    
    def test_unique_student_id_constraint_integration(self, test_db):
        """Test unique student_id constraint at database level"""
        # Create first student
        student1 = models.Student(
            first_name="First",
            last_name="Student",
            email="first@example.com",
            student_id="DUPLICATE001"
        )
        test_db.add(student1)
        test_db.commit()
        
        # Try to create second student with same student_id
        student2 = models.Student(
            first_name="Second",
            last_name="Student",
            email="second@example.com",
            student_id="DUPLICATE001"  # Same student_id
        )
        test_db.add(student2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLite raises different exceptions
            test_db.commit()

if __name__ == "__main__":
    pytest.main([__file__])
