#!/usr/bin/env python3
"""
Initialize database with sample data for testing and demonstration
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.database import SessionLocal, init_db
from backend.models.student import Student
from backend.schemas.student_schemas import StudentCreate
from backend.repositories.student_repository import StudentRepository
from backend.models.user import User, UserRole
from backend.config.auth import get_password_hash

def create_sample_data():
    """Create sample students for testing and demonstration"""
    print("📊 Initializing Academic Management Database")
    print("=" * 50)
    # Initialize database (create tables)
    init_db()
    print("✅ Database tables created")
    db = SessionLocal()
    try:
        sample_students = [
            {"first_name": "John", "last_name": "Doe", "email": "john.doe@university.edu", "student_id": "CS001", "password": "password123"},
            {"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@university.edu", "student_id": "CS002", "password": "password123"},
            {"first_name": "Alice", "last_name": "Johnson", "email": "alice.johnson@university.edu", "student_id": "CS003", "password": "password123"},
            {"first_name": "Bob", "last_name": "Wilson", "email": "bob.wilson@university.edu", "student_id": "CS004", "password": "password123"},
            {"first_name": "Carol", "last_name": "Brown", "email": "carol.brown@university.edu", "student_id": "CS005", "password": "password123"}
        ]
        print(f"📝 Creating {len(sample_students)} sample students...")
        created_count = 0
        for student_data in sample_students:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == student_data["email"]).first()
            if existing_user:
                print(f"   ⚠️  User {student_data['email']} already exists")
                continue
            # Create user
            user = User(
                email=student_data["email"],
                hashed_password=get_password_hash(student_data["password"]),
                role=UserRole.STUDENT
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            # Create student linked to user
            student = Student(
                user_id=user.id,
                student_id=student_data["student_id"],
                first_name=student_data["first_name"],
                last_name=student_data["last_name"]
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            created_count += 1
            print(f"   ✅ Created: {student.first_name} {student.last_name} (ID: {student.id}, User: {user.email})")
        print(f"\n🎉 Successfully created {created_count} students!")
        all_students = db.query(Student).all()
        print(f"📊 Total students in database: {len(all_students)}")
        if all_students:
            print("\n👥 Current students:")
            for student in all_students:
                user = db.query(User).filter(User.id == student.user_id).first()
                print(f"   • {student.first_name} {student.last_name} ({student.student_id}) - {user.email if user else 'N/A'}")
        return True
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        return False
    finally:
        db.close()

def clear_data():
    """Clear all data from database"""
    import backend.models
    from backend.config.database import SessionLocal, engine
    from sqlalchemy import text
    
    print("🗑️  Clearing all data from database...")
    
    db = SessionLocal()
    try:
        # Delete all students
        db.execute(text("DELETE FROM students"))
        db.commit()
        print("✅ All data cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Academic Management Database")
    parser.add_argument("--clear", action="store_true", help="Clear all data before initializing")
    parser.add_argument("--clear-only", action="store_true", help="Only clear data, don't initialize")
    
    args = parser.parse_args()
    
    success = True
    
    if args.clear or args.clear_only:
        success &= clear_data()
        
    if not args.clear_only:
        success &= create_sample_data()
    
    if success:
        print("\n✅ Database initialization completed!")
        print("\n🚀 Quick start:")
        print("   • Start services: ./start.sh")
        print("   • View frontend: http://localhost:9700")
        print("   • View API docs: http://localhost:9600/docs")
        print("   • Run tests: python run_tests.py")
    else:
        print("\n❌ Database initialization failed!")
        
    sys.exit(0 if success else 1)
