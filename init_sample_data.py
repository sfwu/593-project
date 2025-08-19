#!/usr/bin/env python3
"""
Initialize database with sample data for testing and demonstration
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_sample_data():
    """Create sample students for testing and demonstration"""
    # TODO: Update imports when new structure is implemented
    # from models.student import Student
    # from schemas.student_schemas import StudentCreate
    # from repositories.student_repository import StudentRepository
    # from config.database import SessionLocal, init_db
    
    print("⚠️  Database initialization requires implementation of new backend structure")
    return False
    
    print("📊 Initializing Academic Management Database")
    print("=" * 50)
    
    # Initialize database (create tables)
    init_db()
    print("✅ Database tables created")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Sample students data
        sample_students = [
            {
                "first_name": "John",
                "last_name": "Doe", 
                "email": "john.doe@university.edu",
                "student_id": "CS001"
            },
            {
                "first_name": "Jane", 
                "last_name": "Smith",
                "email": "jane.smith@university.edu", 
                "student_id": "CS002"
            },
            {
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@university.edu",
                "student_id": "CS003"  
            },
            {
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "bob.wilson@university.edu",
                "student_id": "CS004"
            },
            {
                "first_name": "Carol",
                "last_name": "Brown",
                "email": "carol.brown@university.edu", 
                "student_id": "CS005"
            }
        ]
        
        print(f"📝 Creating {len(sample_students)} sample students...")
        
        created_count = 0
        for student_data in sample_students:
            try:
                # Check if student already exists
                existing = crud.get_student_by_email(db, student_data["email"])
                if existing:
                    print(f"   ⚠️  Student {student_data['first_name']} {student_data['last_name']} already exists")
                    continue
                
                # Create student
                student_schema = schemas.StudentCreate(**student_data)
                created_student = crud.create_student(db, student_schema)
                created_count += 1
                print(f"   ✅ Created: {created_student.first_name} {created_student.last_name} (ID: {created_student.id})")
                
            except Exception as e:
                print(f"   ❌ Failed to create {student_data['first_name']} {student_data['last_name']}: {e}")
        
        print(f"\n🎉 Successfully created {created_count} students!")
        
        # Show summary
        all_students = crud.get_students(db)
        print(f"📊 Total students in database: {len(all_students)}")
        
        if all_students:
            print("\n👥 Current students:")
            for student in all_students:
                print(f"   • {student.first_name} {student.last_name} ({student.student_id}) - {student.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        return False
    finally:
        db.close()

def clear_data():
    """Clear all data from database"""
    import models
    from database import SessionLocal, engine
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
        print("   • View frontend: http://localhost:9200")
        print("   • View API docs: http://localhost:9100/docs")
        print("   • Run tests: python run_tests.py")
    else:
        print("\n❌ Database initialization failed!")
        
    sys.exit(0 if success else 1)
