"""
Sample data initialization script for Academic Record Access module
This script creates sample academic records, transcripts, and progress data for testing
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.database import SessionLocal, init_db
from backend.models.user import User, UserRole
from backend.models.student import Student
from backend.models.professor import Professor
from backend.models.course import Course, student_course_association
from backend.models.academic_record import (
    AcademicRecord, Transcript, AcademicProgress, SemesterGPA,
    GradeStatus, TranscriptStatus
)
from backend.config.auth import get_password_hash

def create_sample_data():
    """Create sample academic record data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(AcademicRecord).first():
            print("Sample academic record data already exists. Skipping initialization.")
            return
        
        print("Creating sample academic record data...")
        
        # Get existing students and courses
        students = db.query(Student).all()
        courses = db.query(Course).all()
        
        if not students:
            print("No students found. Please run init_sample_data.py first.")
            return
        
        if not courses:
            print("No courses found. Please run init_sample_data.py first.")
            return
        
        # Create academic records for each student
        for student in students:
            print(f"Creating academic records for {student.first_name} {student.last_name}")
            
            # Create academic progress
            progress = AcademicProgress(
                student_id=student.id,
                degree_program="Bachelor of Science in Computer Science",
                major=student.major or "Computer Science",
                catalog_year=2022,
                total_credits_required=120,
                major_credits_required=60,
                general_education_credits_required=30,
                elective_credits_required=30,
                total_credits_earned=0,
                major_credits_earned=0,
                general_education_credits_earned=0,
                elective_credits_earned=0,
                cumulative_gpa=0.0,
                major_gpa=0.0,
                semester_gpa=0.0,
                is_on_track=True,
                expected_graduation_date=datetime.now() + timedelta(days=365),
                completed_requirements='["CS101", "CS102", "MATH101"]',
                remaining_requirements='["CS201", "CS202", "MATH102"]',
                warnings='[]'
            )
            db.add(progress)
            
            # Create sample academic records (grades)
            sample_grades = [
                {"semester": "Fall", "year": 2022, "letter_grade": "A", "numeric_grade": 4.0, "percentage_grade": 95.0},
                {"semester": "Fall", "year": 2022, "letter_grade": "B+", "numeric_grade": 3.3, "percentage_grade": 87.0},
                {"semester": "Spring", "year": 2023, "letter_grade": "A-", "numeric_grade": 3.7, "percentage_grade": 92.0},
                {"semester": "Spring", "year": 2023, "letter_grade": "B", "numeric_grade": 3.0, "percentage_grade": 83.0},
                {"semester": "Fall", "year": 2023, "letter_grade": "A", "numeric_grade": 4.0, "percentage_grade": 96.0},
                {"semester": "Fall", "year": 2023, "letter_grade": "B+", "numeric_grade": 3.3, "percentage_grade": 88.0},
                {"semester": "Spring", "year": 2024, "letter_grade": "A-", "numeric_grade": 3.7, "percentage_grade": 91.0},
                {"semester": "Spring", "year": 2024, "letter_grade": "B", "numeric_grade": 3.0, "percentage_grade": 82.0},
            ]
            
            # Assign grades to courses
            for i, grade_data in enumerate(sample_grades):
                if i < len(courses):
                    course = courses[i]
                    record = AcademicRecord(
                        student_id=student.id,
                        course_id=course.id,
                        semester=grade_data["semester"],
                        year=grade_data["year"],
                        letter_grade=grade_data["letter_grade"],
                        numeric_grade=grade_data["numeric_grade"],
                        percentage_grade=grade_data["percentage_grade"],
                        credits_earned=course.credits,
                        credits_attempted=course.credits,
                        status=GradeStatus.GRADED,
                        grade_date=datetime.now() - timedelta(days=30),
                        professor_notes=f"Good performance in {course.title}",
                        student_notes=""
                    )
                    db.add(record)
            
            # Create semester GPA records
            semester_data = [
                {"semester": "Fall", "year": 2022, "gpa": 3.65, "credits": 6},
                {"semester": "Spring", "year": 2023, "gpa": 3.35, "credits": 6},
                {"semester": "Fall", "year": 2023, "gpa": 3.65, "credits": 6},
                {"semester": "Spring", "year": 2024, "gpa": 3.35, "credits": 6},
            ]
            
            for sem_data in semester_data:
                semester_gpa = SemesterGPA(
                    student_id=student.id,
                    semester=sem_data["semester"],
                    year=sem_data["year"],
                    semester_gpa=sem_data["gpa"],
                    credits_earned=sem_data["credits"],
                    credits_attempted=sem_data["credits"],
                    quality_points=sem_data["gpa"] * sem_data["credits"],
                    courses_completed=2,
                    courses_attempted=2
                )
                db.add(semester_gpa)
            
            # Create a sample transcript
            transcript = Transcript(
                student_id=student.id,
                transcript_type="official",
                status=TranscriptStatus.OFFICIAL,
                generated_date=datetime.now() - timedelta(days=7),
                requested_date=datetime.now() - timedelta(days=10),
                total_credits_earned=24,
                total_credits_attempted=24,
                cumulative_gpa=3.5,
                major_gpa=3.6,
                file_path=f"data/transcripts/transcript_{student.id}_{student.student_id}.txt",
                file_hash="sample_hash_123"
            )
            db.add(transcript)
        
        # Update academic progress with calculated values
        for student in students:
            progress = db.query(AcademicProgress).filter(AcademicProgress.student_id == student.id).first()
            if progress:
                # Calculate totals from academic records
                records = db.query(AcademicRecord).filter(
                    AcademicRecord.student_id == student.id,
                    AcademicRecord.status == GradeStatus.GRADED
                ).all()
                
                total_credits_earned = sum(record.credits_earned for record in records)
                total_credits_attempted = sum(record.credits_attempted for record in records)
                total_quality_points = sum(record.numeric_grade * record.credits_attempted for record in records if record.numeric_grade)
                
                cumulative_gpa = total_quality_points / total_credits_attempted if total_credits_attempted > 0 else 0.0
                
                progress.total_credits_earned = total_credits_earned
                progress.cumulative_gpa = round(cumulative_gpa, 3)
                progress.major_gpa = round(cumulative_gpa + 0.1, 3)  # Slightly higher major GPA
                progress.semester_gpa = 3.35  # Current semester GPA
        
        db.commit()
        print("Sample academic record data created successfully!")
        
        # Print summary
        print("\nSummary:")
        print(f"- Created academic records for {len(students)} students")
        print(f"- Created academic progress records for {len(students)} students")
        print(f"- Created semester GPA records")
        print(f"- Created sample transcripts")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function"""
    print("Initializing Academic Record Access module sample data...")
    
    # Initialize database
    init_db()
    
    # Create sample data
    create_sample_data()
    
    print("\nAcademic Record Access module sample data initialization complete!")
    print("\nYou can now test the following features:")
    print("- View student grades: GET /academic-records/grades")
    print("- Calculate GPA: GET /academic-records/gpa")
    print("- Generate transcripts: POST /academic-records/transcripts/generate")
    print("- View academic progress: GET /academic-records/progress")
    print("- Academic dashboard: GET /academic-records/dashboard")

if __name__ == "__main__":
    main()

