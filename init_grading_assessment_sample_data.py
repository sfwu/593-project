"""
Sample data initialization script for Grading and Assessment module
This script creates sample assignments, exams, grades, and gradebooks for testing
"""
import os
import sys
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.database import SessionLocal, init_db
from backend.models.user import User, UserRole
from backend.models.student import Student
from backend.models.professor import Professor
from backend.models.course import Course, student_course_association
from backend.models.grading_assessment import (
    Assignment, AssignmentSubmission, Exam, ExamSession, Grade, Gradebook,
    GradebookEntry, GradeStatistics, AssignmentType, ExamType, GradeStatus,
    SubmissionStatus
)
from backend.config.auth import get_password_hash

def create_sample_data():
    """Create sample grading and assessment data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Assignment).first():
            print("Sample grading and assessment data already exists. Skipping initialization.")
            return
        
        print("Creating sample grading and assessment data...")
        
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
        
        # Create assignments for each course
        assignment_types = [AssignmentType.HOMEWORK, AssignmentType.PROJECT, AssignmentType.LAB, AssignmentType.QUIZ]
        assignment_titles = [
            "Programming Assignment", "Data Structures Project", "Algorithm Lab", "Quiz on Basics",
            "Database Design", "Web Development Project", "Machine Learning Lab", "Theory Quiz"
        ]
        
        for course in courses:
            professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
            if not professor:
                continue
            
            # Create 4-6 assignments per course
            for i in range(4):
                assignment_type = assignment_types[i % len(assignment_types)]
                title = f"{assignment_titles[i % len(assignment_titles)]} {i+1}"
                
                # Calculate due dates (spread over the semester)
                due_date = datetime.now() + timedelta(days=30 + (i * 14))
                late_deadline = due_date + timedelta(days=2)
                
                assignment = Assignment(
                    course_id=course.id,
                    professor_id=professor.id,
                    title=title,
                    description=f"Complete the {title.lower()} for {course.title}",
                    assignment_type=assignment_type,
                    instructions=f"Follow the instructions carefully for {title}",
                    requirements="Submit your work on time with proper documentation",
                    total_points=100.0 if assignment_type != AssignmentType.QUIZ else 50.0,
                    weight_percentage=15.0 if assignment_type != AssignmentType.QUIZ else 10.0,
                    due_date=due_date,
                    late_submission_deadline=late_deadline,
                    late_penalty_percentage=10.0,
                    allow_late_submissions=True,
                    max_attempts=3 if assignment_type == AssignmentType.QUIZ else 1,
                    submission_format="PDF or source code",
                    file_size_limit=10,
                    is_published=True
                )
                db.add(assignment)
        
        # Create exams for each course
        exam_types = [ExamType.MIDTERM, ExamType.FINAL, ExamType.QUIZ]
        exam_titles = ["Midterm Examination", "Final Examination", "Pop Quiz"]
        
        for course in courses:
            professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
            if not professor:
                continue
            
            # Create 2-3 exams per course
            for i in range(2):
                exam_type = exam_types[i]
                title = exam_titles[i]
                
                # Calculate exam dates
                exam_date = date.today() + timedelta(days=60 + (i * 30))
                
                exam = Exam(
                    course_id=course.id,
                    professor_id=professor.id,
                    title=f"{title} - {course.title}",
                    description=f"Comprehensive {title.lower()} for {course.title}",
                    exam_type=exam_type,
                    instructions="Answer all questions clearly and show your work",
                    total_points=100.0,
                    weight_percentage=30.0 if exam_type == ExamType.MIDTERM else 40.0,
                    passing_grade=60.0,
                    exam_date=exam_date,
                    start_time=time(10, 0),
                    end_time=time(12, 0),
                    duration_minutes=120,
                    location=f"Room {100 + course.id}",
                    is_online=False,
                    proctoring_required=True,
                    allowed_materials="Calculator, Notes" if exam_type != ExamType.FINAL else "Calculator only",
                    restricted_materials="No phones, No internet access",
                    is_published=True
                )
                db.add(exam)
        
        db.commit()
        
        # Create gradebooks for each course
        for course in courses:
            professor = db.query(Professor).filter(Professor.id == course.professor_id).first()
            if not professor:
                continue
            
            gradebook = Gradebook(
                course_id=course.id,
                professor_id=professor.id,
                name=f"{course.course_code} {course.semester} {course.year} Gradebook",
                description=f"Comprehensive gradebook for {course.title}",
                semester=course.semester,
                year=course.year,
                grading_scheme='{"A": 90, "B": 80, "C": 70, "D": 60, "F": 0}',
                letter_grade_scale='{"A+": 97, "A": 93, "A-": 90, "B+": 87, "B": 83, "B-": 80, "C+": 77, "C": 73, "C-": 70, "D+": 67, "D": 63, "D-": 60, "F": 0}',
                pass_fail_threshold=60.0,
                drop_lowest_assignments=1,
                drop_lowest_exams=0,
                curve_enabled=False,
                curve_percentage=0.0,
                assignment_weight=40.0,
                exam_weight=50.0,
                participation_weight=10.0,
                allow_student_view=True,
                is_published=True
            )
            db.add(gradebook)
        
        db.commit()
        
        # Create assignment submissions and grades
        assignments = db.query(Assignment).all()
        for assignment in assignments:
            # Get students enrolled in this course
            course_students = db.query(Student).join(
                student_course_association,
                Student.id == student_course_association.c.student_id
            ).filter(student_course_association.c.course_id == assignment.course_id).all()
            
            for student in course_students:
                # Create submission (80% of students submit)
                if student.id % 5 != 0:  # Skip every 5th student
                    is_late = student.id % 7 == 0  # Some students submit late
                    submission_date = assignment.due_date
                    if is_late:
                        submission_date = assignment.due_date + timedelta(hours=2)
                    
                    submission = AssignmentSubmission(
                        assignment_id=assignment.id,
                        student_id=student.id,
                        submission_content=f"Submission for {assignment.title} by {student.first_name}",
                        file_name=f"{assignment.title.replace(' ', '_')}_{student.student_id}.py",
                        file_size=1024 + (student.id * 100),
                        submission_status=SubmissionStatus.SUBMITTED,
                        submitted_at=submission_date,
                        is_late=is_late,
                        late_hours=2.0 if is_late else 0.0,
                        attempt_number=1,
                        professor_feedback=f"Good work on {assignment.title}" if student.id % 3 != 0 else None,
                        feedback_date=submission_date + timedelta(days=3) if student.id % 3 != 0 else None
                    )
                    db.add(submission)
                    
                    # Create grade for the submission
                    base_grade = 70 + (student.id % 30)  # Grade between 70-99
                    if is_late:
                        base_grade = base_grade * 0.9  # Apply late penalty
                    
                    grade = Grade(
                        student_id=student.id,
                        course_id=assignment.course_id,
                        professor_id=assignment.professor_id,
                        assignment_id=assignment.id,
                        points_earned=base_grade,
                        points_possible=assignment.total_points,
                        percentage=(base_grade / assignment.total_points) * 100,
                        letter_grade="A" if base_grade >= 90 else "B" if base_grade >= 80 else "C" if base_grade >= 70 else "D" if base_grade >= 60 else "F",
                        grade_status=GradeStatus.PUBLISHED,
                        graded_date=submission_date + timedelta(days=2),
                        published_date=submission_date + timedelta(days=3),
                        is_late=is_late,
                        late_penalty_applied=10.0 if is_late else 0.0,
                        professor_comments=f"Good work on {assignment.title}" if student.id % 3 != 0 else None,
                        detailed_feedback=f"Detailed feedback for {student.first_name} on {assignment.title}" if student.id % 4 == 0 else None
                    )
                    db.add(grade)
        
        # Create exam sessions and grades
        exams = db.query(Exam).all()
        for exam in exams:
            # Get students enrolled in this course
            course_students = db.query(Student).join(
                student_course_association,
                Student.id == student_course_association.c.student_id
            ).filter(student_course_association.c.course_id == exam.course_id).all()
            
            for student in course_students:
                # Create exam session (90% of students attend)
                if student.id % 10 != 0:  # Skip every 10th student
                    attended = student.id % 8 != 0  # Some students don't attend
                    late_arrival = student.id % 6 == 0  # Some students arrive late
                    
                    session_start = datetime.combine(exam.exam_date, exam.start_time)
                    if late_arrival and attended:
                        session_start += timedelta(minutes=15)
                    
                    session = ExamSession(
                        exam_id=exam.id,
                        student_id=student.id,
                        session_start_time=session_start if attended else None,
                        session_end_time=session_start + timedelta(hours=2) if attended else None,
                        actual_duration_minutes=120 if attended else 0,
                        attended=attended,
                        late_arrival_minutes=15 if late_arrival and attended else 0,
                        early_departure_minutes=0,
                        technical_issues=None,
                        issues_resolved=True
                    )
                    db.add(session)
                    
                    # Create grade for the exam (only if attended)
                    if attended:
                        base_grade = 60 + (student.id % 40)  # Grade between 60-99
                        
                        grade = Grade(
                            student_id=student.id,
                            course_id=exam.course_id,
                            professor_id=exam.professor_id,
                            exam_id=exam.id,
                            points_earned=base_grade,
                            points_possible=exam.total_points,
                            percentage=(base_grade / exam.total_points) * 100,
                            letter_grade="A" if base_grade >= 90 else "B" if base_grade >= 80 else "C" if base_grade >= 70 else "D" if base_grade >= 60 else "F",
                            grade_status=GradeStatus.PUBLISHED,
                            graded_date=session_start + timedelta(days=1),
                            published_date=session_start + timedelta(days=2),
                            professor_comments=f"Good performance on {exam.title}" if base_grade >= 80 else f"Room for improvement on {exam.title}",
                            detailed_feedback=f"Detailed exam feedback for {student.first_name}" if student.id % 5 == 0 else None
                        )
                        db.add(grade)
        
        db.commit()
        
        # Create gradebook entries
        gradebooks = db.query(Gradebook).all()
        for gradebook in gradebooks:
            # Get students enrolled in this course
            course_students = db.query(Student).join(
                student_course_association,
                Student.id == student_course_association.c.student_id
            ).filter(student_course_association.c.course_id == gradebook.course_id).all()
            
            for student in course_students:
                # Get all grades for this student in this course
                student_grades = db.query(Grade).filter(
                    Grade.student_id == student.id,
                    Grade.course_id == gradebook.course_id
                ).all()
                
                if student_grades:
                    total_earned = sum(grade.points_earned for grade in student_grades)
                    total_possible = sum(grade.points_possible for grade in student_grades)
                    overall_percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0.0
                    
                    # Calculate category averages
                    assignment_grades = [g for g in student_grades if g.assignment_id is not None]
                    exam_grades = [g for g in student_grades if g.exam_id is not None]
                    
                    assignment_avg = sum(g.percentage for g in assignment_grades) / len(assignment_grades) if assignment_grades else 0.0
                    exam_avg = sum(g.percentage for g in exam_grades) / len(exam_grades) if exam_grades else 0.0
                    
                    # Determine final letter grade
                    if overall_percentage >= 97:
                        final_grade = "A+"
                    elif overall_percentage >= 93:
                        final_grade = "A"
                    elif overall_percentage >= 90:
                        final_grade = "A-"
                    elif overall_percentage >= 87:
                        final_grade = "B+"
                    elif overall_percentage >= 83:
                        final_grade = "B"
                    elif overall_percentage >= 80:
                        final_grade = "B-"
                    elif overall_percentage >= 77:
                        final_grade = "C+"
                    elif overall_percentage >= 73:
                        final_grade = "C"
                    elif overall_percentage >= 70:
                        final_grade = "C-"
                    elif overall_percentage >= 67:
                        final_grade = "D+"
                    elif overall_percentage >= 63:
                        final_grade = "D"
                    elif overall_percentage >= 60:
                        final_grade = "D-"
                    else:
                        final_grade = "F"
                    
                    entry = GradebookEntry(
                        gradebook_id=gradebook.id,
                        student_id=student.id,
                        total_points_earned=total_earned,
                        total_points_possible=total_possible,
                        overall_percentage=overall_percentage,
                        final_letter_grade=final_grade,
                        assignment_average=assignment_avg,
                        exam_average=exam_avg,
                        participation_average=85.0,  # Default participation
                        assignments_completed=len(assignment_grades),
                        assignments_total=len([a for a in db.query(Assignment).filter(Assignment.course_id == gradebook.course_id).all()]),
                        exams_completed=len(exam_grades),
                        exams_total=len([e for e in db.query(Exam).filter(Exam.course_id == gradebook.course_id).all()]),
                        is_passing=overall_percentage >= gradebook.pass_fail_threshold,
                        is_at_risk=overall_percentage < 70.0,
                        needs_attention=overall_percentage < 60.0
                    )
                    db.add(entry)
        
        db.commit()
        
        # Create grade statistics for each course
        for course in courses:
            # Get all grades for this course
            course_grades = db.query(Grade).filter(Grade.course_id == course.id).all()
            
            if course_grades:
                percentages = [grade.percentage for grade in course_grades]
                total_students = len(set(grade.student_id for grade in course_grades))
                students_passing = len([g for g in course_grades if g.percentage >= 60.0])
                students_failing = total_students - students_passing
                
                import statistics
                average_grade = statistics.mean(percentages)
                median_grade = statistics.median(percentages)
                highest_grade = max(percentages)
                lowest_grade = min(percentages)
                std_dev = statistics.stdev(percentages) if len(percentages) > 1 else 0.0
                
                # Count letter grades
                a_grades = len([g for g in course_grades if g.percentage >= 90])
                b_grades = len([g for g in course_grades if 80 <= g.percentage < 90])
                c_grades = len([g for g in course_grades if 70 <= g.percentage < 80])
                d_grades = len([g for g in course_grades if 60 <= g.percentage < 70])
                f_grades = len([g for g in course_grades if g.percentage < 60])
                
                # Calculate category averages
                assignment_grades = [g for g in course_grades if g.assignment_id is not None]
                exam_grades = [g for g in course_grades if g.exam_id is not None]
                
                assignment_avg = statistics.mean([g.percentage for g in assignment_grades]) if assignment_grades else 0.0
                exam_avg = statistics.mean([g.percentage for g in exam_grades]) if exam_grades else 0.0
                
                stats = GradeStatistics(
                    course_id=course.id,
                    total_students=total_students,
                    students_passing=students_passing,
                    students_failing=students_failing,
                    average_grade=average_grade,
                    median_grade=median_grade,
                    highest_grade=highest_grade,
                    lowest_grade=lowest_grade,
                    standard_deviation=std_dev,
                    a_grades=a_grades,
                    b_grades=b_grades,
                    c_grades=c_grades,
                    d_grades=d_grades,
                    f_grades=f_grades,
                    assignment_average=assignment_avg,
                    exam_average=exam_avg,
                    participation_average=85.0  # Default
                )
                db.add(stats)
        
        db.commit()
        
        print("Sample grading and assessment data created successfully!")
        
        # Print summary
        print("\nSummary:")
        print(f"- Created {len(assignments)} assignments across {len(courses)} courses")
        print(f"- Created {len(exams)} exams across {len(courses)} courses")
        print(f"- Created {len(gradebooks)} gradebooks")
        print(f"- Created assignment submissions and grades")
        print(f"- Created exam sessions and grades")
        print(f"- Created gradebook entries")
        print(f"- Created grade statistics")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function"""
    print("Initializing Grading and Assessment module sample data...")
    
    # Initialize database
    init_db()
    
    # Create sample data
    create_sample_data()
    
    print("\nGrading and Assessment module sample data initialization complete!")
    print("\nYou can now test the following features:")
    print("- Assignment Management: POST /grading/assignments")
    print("- Exam Scheduling: POST /grading/exams")
    print("- Grade Management: POST /grading/grades")
    print("- Gradebook Management: POST /grading/gradebooks")
    print("- Grading Dashboard: GET /grading/dashboard")
    print("- Grade Statistics: GET /grading/statistics/course/{course_id}")

if __name__ == "__main__":
    main()
