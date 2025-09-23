"""
Sample data initialization script for Student Information Management module
This script creates sample attendance records, messages, and student directory data for testing
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
from backend.models.student_information import (
    Attendance, AttendanceSummary, Message, MessageRecipient, StudentDirectory,
    StudentPerformance, CommunicationLog, AttendanceStatus, MessageStatus,
    MessageType, MessagePriority
)
from backend.config.auth import get_password_hash

def create_sample_data():
    """Create sample student information data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Attendance).first():
            print("Sample student information data already exists. Skipping initialization.")
            return
        
        print("Creating sample student information data...")
        
        # Get existing students, professors, and courses
        students = db.query(Student).all()
        professors = db.query(Professor).all()
        courses = db.query(Course).all()
        
        if not students:
            print("No students found. Please run init_sample_data.py first.")
            return
        
        if not professors:
            print("No professors found. Please run init_sample_data.py first.")
            return
        
        if not courses:
            print("No courses found. Please run init_sample_data.py first.")
            return
        
        # Create student directory entries
        for student in students:
            print(f"Creating directory entry for {student.first_name} {student.last_name}")
            
            directory = StudentDirectory(
                student_id=student.id,
                email=f"{student.first_name.lower()}.{student.last_name.lower()}@university.edu",
                phone=f"555-{1000 + student.id:04d}",
                emergency_contact=f"Emergency Contact {student.id}",
                emergency_phone=f"555-{2000 + student.id:04d}",
                address=f"{100 + student.id} University Ave, City, State 12345",
                major=student.major or "Computer Science",
                year_level=student.year_level or "Junior",
                gpa=3.0 + (student.id % 10) * 0.1,  # GPA between 3.0 and 3.9
                enrollment_status="active",
                advisor_id=professors[0].id if professors else None,
                notes=f"Notes for {student.first_name} {student.last_name}",
                show_contact_info=True,
                show_academic_info=True
            )
            db.add(directory)
        
        # Create student performance records
        for student in students:
            for course in courses[:2]:  # First 2 courses for each student
                performance = StudentPerformance(
                    student_id=student.id,
                    course_id=course.id,
                    current_grade=70.0 + (student.id % 30),  # Grade between 70-99
                    participation_score=80.0 + (student.id % 20),  # Participation 80-99
                    attendance_score=85.0 + (student.id % 15),  # Attendance 85-99
                    assignment_average=75.0 + (student.id % 25),  # Assignments 75-99
                    exam_average=80.0 + (student.id % 20),  # Exams 80-99
                    is_at_risk=student.id % 5 == 0,  # Every 5th student is at risk
                    risk_factors='["Low attendance", "Poor assignment performance"]' if student.id % 5 == 0 else '[]',
                    improvement_areas='["Attend office hours", "Complete assignments on time"]' if student.id % 5 == 0 else '[]',
                    professor_notes=f"Performance notes for {student.first_name} in {course.title}",
                    last_contact_date=datetime.now() - timedelta(days=student.id % 30),
                    next_follow_up=datetime.now() + timedelta(days=7) if student.id % 5 == 0 else None
                )
                db.add(performance)
        
        # Create attendance records
        for course in courses:
            course_students = db.query(Student).join(
                student_course_association,
                Student.id == student_course_association.c.student_id
            ).filter(student_course_association.c.course_id == course.id).all()
            
            if not course_students:
                continue
            
            professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
            if not professor:
                continue
            
            # Create attendance for the last 10 class sessions
            for session in range(10):
                session_date = datetime.now() - timedelta(days=session * 3)  # Every 3 days
                
                for student in course_students:
                    # Random attendance status
                    status_options = [AttendanceStatus.PRESENT, AttendanceStatus.PRESENT, AttendanceStatus.PRESENT, 
                                    AttendanceStatus.LATE, AttendanceStatus.ABSENT]
                    status = status_options[student.id % len(status_options)]
                    
                    late_minutes = 0
                    if status == AttendanceStatus.LATE:
                        late_minutes = 5 + (student.id % 20)  # 5-24 minutes late
                    
                    attendance = Attendance(
                        student_id=student.id,
                        course_id=course.id,
                        attendance_date=session_date,
                        status=status,
                        notes=f"Session {session + 1} notes" if status == AttendanceStatus.ABSENT else None,
                        late_minutes=late_minutes,
                        session_topic=f"Topic {session + 1}: Introduction to {course.title}",
                        session_duration=90,
                        recorded_by=professor.id
                    )
                    db.add(attendance)
        
        # Create messages
        for professor in professors:
            professor_courses = db.query(Course).filter(Course.professor_id == professor.id).all()
            
            for course in professor_courses:
                # Create different types of messages
                message_types = [
                    (MessageType.ANNOUNCEMENT, "Important Announcement", "This is an important announcement for the class."),
                    (MessageType.ASSIGNMENT, "Assignment Due Date Reminder", "Don't forget that the assignment is due next week."),
                    (MessageType.REMINDER, "Class Schedule Reminder", "Remember that we have class tomorrow at the usual time."),
                    (MessageType.GENERAL, "General Information", "Here is some general information about the course.")
                ]
                
                for msg_type, subject, content in message_types:
                    message = Message(
                        sender_id=professor.id,
                        course_id=course.id,
                        subject=subject,
                        content=content,
                        message_type=msg_type,
                        priority=MessagePriority.NORMAL,
                        is_broadcast=True,
                        status=MessageStatus.SENT,
                        sent_at=datetime.now() - timedelta(days=msg_type.value.count('a'))  # Different send times
                    )
                    db.add(message)
                    db.flush()  # Get the message ID
                    
                    # Create recipients for the message
                    course_students = db.query(Student).join(
                        student_course_association,
                        Student.id == student_course_association.c.student_id
                    ).filter(student_course_association.c.course_id == course.id).all()
                    
                    for student in course_students:
                        recipient = MessageRecipient(
                            message_id=message.id,
                            student_id=student.id,
                            status=MessageStatus.DELIVERED if student.id % 2 == 0 else MessageStatus.READ,
                            delivered_at=datetime.now() - timedelta(hours=1),
                            read_at=datetime.now() - timedelta(minutes=30) if student.id % 2 == 1 else None
                        )
                        db.add(recipient)
        
        # Create communication logs
        for professor in professors:
            for student in students[:5]:  # First 5 students
                communication_types = ["email", "meeting", "phone", "message"]
                
                for i, comm_type in enumerate(communication_types):
                    log = CommunicationLog(
                        professor_id=professor.id,
                        student_id=student.id,
                        course_id=courses[0].id if courses else None,
                        communication_type=comm_type,
                        subject=f"{comm_type.title()} Communication",
                        content=f"This is a {comm_type} communication with {student.first_name}.",
                        direction="sent",
                        requires_follow_up=i % 2 == 0,
                        follow_up_date=datetime.now() + timedelta(days=7) if i % 2 == 0 else None,
                        follow_up_notes=f"Follow up notes for {comm_type}" if i % 2 == 0 else None,
                        communication_date=datetime.now() - timedelta(days=i * 2)
                    )
                    db.add(log)
        
        db.commit()
        print("Sample student information data created successfully!")
        
        # Print summary
        print("\nSummary:")
        print(f"- Created directory entries for {len(students)} students")
        print(f"- Created performance records for {len(students) * min(len(courses), 2)} student-course combinations")
        print(f"- Created attendance records for {len(courses)} courses")
        print(f"- Created messages from {len(professors)} professors")
        print(f"- Created communication logs")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function"""
    print("Initializing Student Information Management module sample data...")
    
    # Initialize database
    init_db()
    
    # Create sample data
    create_sample_data()
    
    print("\nStudent Information Management module sample data initialization complete!")
    print("\nYou can now test the following features:")
    print("- Student Directory: GET /student-information/directory")
    print("- Academic Records: GET /student-information/academic-records/{student_id}")
    print("- Attendance Tracking: GET /student-information/attendance")
    print("- Student Communication: GET /student-information/messages")
    print("- Professor Dashboard: GET /student-information/dashboard")

if __name__ == "__main__":
    main()
