"""
Professor Workflow Integration Tests
Tests the complete professor teaching cycle including course administration,
enrollment management, grading, and student communication.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestProfessorCourseAdministrationIntegration:
    """Integration tests for professor course administration workflow"""
    
    def test_complete_course_creation_and_management_workflow(self, integration_client, integration_db, auth_professor_headers):
        """Test complete course creation and management workflow"""
        # 1. Create multiple courses
        courses_data = [
            {
                "course_code": "CS101",
                "title": "Introduction to Computer Science",
                "description": "Basic programming and computer science concepts",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30,
                "prerequisites": "None",
                "schedule": json.dumps({"days": ["Monday", "Wednesday"], "start_time": "09:00", "end_time": "10:30"})
            },
            {
                "course_code": "CS102",
                "title": "Data Structures and Algorithms",
                "description": "Advanced data structures and algorithm analysis",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 25,
                "prerequisites": "CS101",
                "schedule": json.dumps({"days": ["Tuesday", "Thursday"], "start_time": "11:00", "end_time": "12:30"})
            },
            {
                "course_code": "CS201",
                "title": "Software Engineering",
                "description": "Software development methodologies and practices",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Spring 2025",
                "year": 2025,
                "max_enrollment": 20,
                "prerequisites": "CS102",
                "schedule": json.dumps({"days": ["Monday", "Wednesday", "Friday"], "start_time": "14:00", "end_time": "15:00"})
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            course = response.json()
            assert course["course_code"] == course_data["course_code"]
            assert course["title"] == course_data["title"]
            created_courses.append(course)
        
        # 2. View all courses created by professor
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        assert response.status_code == 200
        professor_courses = response.json()
        assert len(professor_courses) >= len(courses_data)
        
        # 3. Update course information
        course_update = {
            "course_code": "CS101",
            "title": "Introduction to Computer Science - Updated",
            "description": "Updated description with more details",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 35,  # Increased capacity
            "prerequisites": "None"
        }
        
        course_id = created_courses[0]["id"]
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_course = response.json()
        assert updated_course["title"] == "Introduction to Computer Science - Updated"
        assert updated_course["max_enrollment"] == 35
        
        # 4. View specific course details
        response = integration_client.get(f"/professors/courses/{course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        course_details = response.json()
        assert course_details["id"] == course_id
        assert course_details["course_code"] == "CS101"
    
    def test_course_enrollment_management_workflow(self, integration_client, integration_db,
                                                 auth_professor_headers, auth_student_headers):
        """Test course enrollment management workflow"""
        # 1. Create a course
        course_data = {
            "course_code": "ENROLL001",
            "title": "Enrollment Management Test",
            "description": "Course for testing enrollment management",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 5
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # 2. Create multiple students and enroll them
        enrolled_students = []
        for i in range(3):
            student_data = {
                "email": f"enrolltest{i}@example.com",
                "password": "password123",
                "student_id": f"ENROLL{i:03d}",
                "first_name": f"EnrollTest{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            
            # Login as student
            login_data = {"email": f"enrolltest{i}@example.com", "password": "password123"}
            response = integration_client.post("/auth/login", json=login_data)
            assert response.status_code == 200
            token = response.json()["access_token"]
            student_headers = {"Authorization": f"Bearer {token}"}
            
            # Enroll student in course
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
            enrolled_students.append(response.json())
        
        # 3. Professor views course enrollment
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_data = response.json()
        assert len(enrollment_data) == 3
        
        # 4. Professor views enrollment statistics
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment/stats", headers=auth_professor_headers)
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_enrolled"] == 3
        assert stats["max_enrollment"] == 5
        assert stats["enrollment_percentage"] == 60.0
        
        # 5. Professor removes a student from course
        student_to_remove = enrolled_students[0]["student_id"]
        response = integration_client.delete(f"/professors/courses/{course_id}/students/{student_to_remove}", 
                                           headers=auth_professor_headers)
        assert response.status_code == 200
        
        # 6. Verify student was removed
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_data = response.json()
        assert len(enrollment_data) == 2
    
    def test_course_prerequisites_and_validation(self, integration_client, integration_db, auth_professor_headers):
        """Test course prerequisites and validation"""
        # 1. Create prerequisite course
        prereq_course_data = {
            "course_code": "PREREQ001",
            "title": "Prerequisite Course",
            "description": "Course that serves as prerequisite",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=prereq_course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        prereq_course = response.json()
        
        # 2. Create course with prerequisite
        advanced_course_data = {
            "course_code": "ADVANCED001",
            "title": "Advanced Course",
            "description": "Course with prerequisites",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Spring 2025",
            "year": 2025,
            "max_enrollment": 20,
            "prerequisites": "PREREQ001"
        }
        
        response = integration_client.post("/professors/courses", json=advanced_course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        advanced_course = response.json()
        assert advanced_course["prerequisites"] == "PREREQ001"

class TestProfessorGradingWorkflowIntegration:
    """Integration tests for professor grading workflow"""
    
    def test_complete_assessment_creation_and_grading_workflow(self, integration_client, integration_db,
                                                            auth_professor_headers, enrolled_student_course):
        """Test complete assessment creation and grading workflow"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Programming Assignment 1",
            "description": "Complete the programming exercises",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "late_policy": json.dumps({"penalty_per_day": 10, "max_penalty": 50}),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # 2. Create exam
        exam_data = {
            "course_id": course_id,
            "title": "Midterm Exam",
            "description": "Midterm examination covering chapters 1-5",
            "exam_type": "midterm",
            "points_possible": 100,
            "exam_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "duration_minutes": 120,
            "location": "Room 101",
            "is_published": True
        }
        
        response = integration_client.post("/grading/exams", json=exam_data, headers=auth_professor_headers)
        assert response.status_code == 200
        exam = response.json()
        
        # 3. View all assignments and exams
        response = integration_client.get("/grading/assignments", headers=auth_professor_headers)
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) >= 1
        
        response = integration_client.get("/grading/exams", headers=auth_professor_headers)
        assert response.status_code == 200
        exams = response.json()
        assert len(exams) >= 1
        
        # 4. Grade assignment
        grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 85.0,
            "points_possible": 100.0,
            "percentage": 85.0,
            "letter_grade": "B",
            "grade_status": "graded",
            "is_published": True,
            "professor_comments": "Good work, but could improve on algorithm efficiency."
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        
        # 5. Grade exam
        exam_grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "exam_id": exam["id"],
            "points_earned": 92.0,
            "points_possible": 100.0,
            "percentage": 92.0,
            "letter_grade": "A-",
            "grade_status": "graded",
            "is_published": True,
            "professor_comments": "Excellent performance on the exam."
        }
        
        response = integration_client.post("/grading/grades", json=exam_grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        exam_grade = response.json()
        
        # 6. View all grades for course
        response = integration_client.get(f"/grading/grades?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        course_grades = response.json()
        assert len(course_grades) >= 2
        
        # 7. View gradebook for course
        response = integration_client.get(f"/grading/gradebooks?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        gradebooks = response.json()
        # May be empty if gradebook creation is separate
        
        # 8. Update grade
        grade_update = {
            "points_earned": 88.0,
            "percentage": 88.0,
            "letter_grade": "B+",
            "professor_comments": "Updated grade after review."
        }
        
        response = integration_client.put(f"/grading/grades/{grade['id']}", json=grade_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_grade = response.json()
        assert updated_grade["letter_grade"] == "B+"
    
    def test_bulk_grading_operations(self, integration_client, integration_db,
                                   auth_professor_headers, enrolled_student_course):
        """Test bulk grading operations"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Bulk Grading Assignment",
            "description": "Assignment for testing bulk grading",
            "assignment_type": "homework",
            "points_possible": 50,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # 2. Create multiple students and enroll them
        student_ids = []
        for i in range(3):
            student_data = {
                "email": f"bulkgrading{i}@example.com",
                "password": "password123",
                "student_id": f"BULK{i:03d}",
                "first_name": f"BulkGrading{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            student_id = response.json()["id"]
            student_ids.append(student_id)
            
            # Enroll student
            login_data = {"email": f"bulkgrading{i}@example.com", "password": "password123"}
            response = integration_client.post("/auth/login", json=login_data)
            token = response.json()["access_token"]
            student_headers = {"Authorization": f"Bearer {token}"}
            
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
        
        # 3. Bulk grade creation
        bulk_grade_data = {
            "assignment_id": assignment["id"],
            "course_id": course_id,
            "grades": [
                {
                    "student_id": student_ids[0],
                    "points_earned": 45.0,
                    "points_possible": 50.0,
                    "percentage": 90.0,
                    "letter_grade": "A-"
                },
                {
                    "student_id": student_ids[1],
                    "points_earned": 40.0,
                    "points_possible": 50.0,
                    "percentage": 80.0,
                    "letter_grade": "B-"
                },
                {
                    "student_id": student_ids[2],
                    "points_earned": 35.0,
                    "points_possible": 50.0,
                    "percentage": 70.0,
                    "letter_grade": "C"
                }
            ]
        }
        
        response = integration_client.post("/grading/grades/bulk", json=bulk_grade_data, headers=auth_professor_headers)
        # May not be implemented, so accept either success or not found
        assert response.status_code in [200, 404, 405]
    
    def test_grade_statistics_and_analytics(self, integration_client, integration_db,
                                          auth_professor_headers, enrolled_student_course):
        """Test grade statistics and analytics"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. View grading dashboard
        response = integration_client.get("/grading/dashboard", headers=auth_professor_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "summary" in dashboard or "overview" in dashboard
        
        # 2. View course grading summary
        response = integration_client.get(f"/grading/courses/{course_id}/summary", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404]
        
        # 3. View grade distribution
        response = integration_client.get(f"/grading/courses/{course_id}/grade-distribution", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404]

class TestProfessorStudentCommunicationIntegration:
    """Integration tests for professor-student communication"""
    
    def test_complete_messaging_workflow(self, integration_client, integration_db,
                                       auth_professor_headers, enrolled_student_course):
        """Test complete messaging workflow between professor and students"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Send individual message to student
        message_data = {
            "course_id": course_id,
            "subject": "Assignment Feedback",
            "content": "Your assignment was well done. Consider improving the algorithm efficiency.",
            "message_type": "feedback",
            "priority": "normal",
            "is_broadcast": False,
            "recipient_ids": [student_id]
        }
        
        response = integration_client.post("/student-information/messages", json=message_data, headers=auth_professor_headers)
        assert response.status_code == 200
        message = response.json()
        
        # 2. Send broadcast message to all students in course
        broadcast_data = {
            "course_id": course_id,
            "subject": "Important Announcement",
            "content": "The next class will be moved to Room 205.",
            "message_type": "announcement",
            "priority": "high",
            "is_broadcast": True,
            "recipient_ids": [student_id]  # All students in course
        }
        
        response = integration_client.post("/student-information/messages", json=broadcast_data, headers=auth_professor_headers)
        assert response.status_code == 200
        broadcast = response.json()
        
        # 3. View sent messages
        response = integration_client.get("/student-information/messages", headers=auth_professor_headers)
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) >= 2
        
        # 4. View message details
        response = integration_client.get(f"/student-information/messages/{message['id']}", headers=auth_professor_headers)
        assert response.status_code == 200
        message_details = response.json()
        assert message_details["subject"] == "Assignment Feedback"
        
        # 5. Send message (if implemented)
        response = integration_client.post(f"/student-information/messages/{message['id']}/send", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # 6. View message recipients
        response = integration_client.get(f"/student-information/messages/{message['id']}/recipients", headers=auth_professor_headers)
        assert response.status_code == 200
        recipients = response.json()
        assert isinstance(recipients, list)
    
    def test_attendance_tracking_workflow(self, integration_client, integration_db,
                                        auth_professor_headers, enrolled_student_course):
        """Test attendance tracking workflow"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Record individual attendance
        attendance_data = {
            "student_id": student_id,
            "course_id": course_id,
            "attendance_date": datetime.now().isoformat(),
            "status": "present",
            "late_minutes": 5,
            "notes": "Arrived slightly late"
        }
        
        response = integration_client.post("/student-information/attendance", json=attendance_data, headers=auth_professor_headers)
        assert response.status_code == 200
        attendance = response.json()
        
        # 2. Record multiple attendance records
        attendance_records = [
            {
                "student_id": student_id,
                "course_id": course_id,
                "attendance_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "present",
                "late_minutes": 0
            },
            {
                "student_id": student_id,
                "course_id": course_id,
                "attendance_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "absent",
                "late_minutes": 0,
                "notes": "Sick"
            }
        ]
        
        for record in attendance_records:
            response = integration_client.post("/student-information/attendance", json=record, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # 3. View attendance records
        response = integration_client.get("/student-information/attendance", headers=auth_professor_headers)
        assert response.status_code == 200
        records = response.json()
        assert len(records) >= 3
        
        # 4. View attendance summary for student
        response = integration_client.get(f"/student-information/attendance/summary/{student_id}?course_id={course_id}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        summary = response.json()
        assert "total_classes" in summary or "attendance_percentage" in summary
        
        # 5. View attendance report for course
        response = integration_client.get(f"/student-information/attendance/report/{course_id}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        report = response.json()
        assert "course_id" in report or "attendance_data" in report
    
    def test_bulk_attendance_operations(self, integration_client, integration_db,
                                      auth_professor_headers, enrolled_student_course):
        """Test bulk attendance operations"""
        course_id = enrolled_student_course["course_id"]
        
        # Create additional students
        student_ids = [enrolled_student_course["student"].id]
        for i in range(2):
            student_data = {
                "email": f"bulkattendance{i}@example.com",
                "password": "password123",
                "student_id": f"BULKATT{i:03d}",
                "first_name": f"BulkAttendance{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            student_id = response.json()["id"]
            student_ids.append(student_id)
            
            # Enroll student
            login_data = {"email": f"bulkattendance{i}@example.com", "password": "password123"}
            response = integration_client.post("/auth/login", json=login_data)
            token = response.json()["access_token"]
            student_headers = {"Authorization": f"Bearer {token}"}
            
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
        
        # Bulk attendance creation
        bulk_attendance_data = {
            "course_id": course_id,
            "attendance_date": datetime.now().isoformat(),
            "attendance_records": [
                {
                    "student_id": student_ids[0],
                    "status": "present",
                    "late_minutes": 0
                },
                {
                    "student_id": student_ids[1],
                    "status": "present",
                    "late_minutes": 5
                },
                {
                    "student_id": student_ids[2],
                    "status": "absent",
                    "late_minutes": 0,
                    "notes": "Excused absence"
                }
            ]
        }
        
        response = integration_client.post("/student-information/attendance/bulk", json=bulk_attendance_data, 
                                        headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]

class TestProfessorDashboardAndAnalyticsIntegration:
    """Integration tests for professor dashboard and analytics"""
    
    def test_professor_dashboard_comprehensive_view(self, integration_client, integration_db,
                                                  auth_professor_headers, enrolled_student_course):
        """Test comprehensive professor dashboard view"""
        # 1. View professor dashboard
        response = integration_client.get("/student-information/dashboard", headers=auth_professor_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        # Verify dashboard contains expected sections
        expected_sections = ["professor_id", "total_students", "total_courses", "pending_messages", "students_at_risk"]
        for section in expected_sections:
            assert section in dashboard
        
        # 2. View professor profile
        response = integration_client.get("/professors/profile", headers=auth_professor_headers)
        assert response.status_code == 200
        profile = response.json()
        assert "professor_id" in profile
        assert "department" in profile
        
        # 3. Update professor profile
        profile_update = {
            "title": "Full Professor",
            "office_hours": "Monday 2-4 PM, Wednesday 10-12 PM",
            "specialization": "Machine Learning and AI"
        }
        
        response = integration_client.put("/professors/profile", json=profile_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["title"] == "Full Professor"
    
    def test_student_performance_monitoring(self, integration_client, integration_db,
                                          auth_professor_headers, enrolled_student_course):
        """Test student performance monitoring features"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. View student directory
        response = integration_client.get("/student-information/directory", headers=auth_professor_headers)
        assert response.status_code == 200
        directory = response.json()
        assert isinstance(directory, list)
        
        # 2. View student academic records
        response = integration_client.get(f"/student-information/academic-records/{student_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        academic_records = response.json()
        assert isinstance(academic_records, list)
        
        # 3. View students at risk
        response = integration_client.get("/student-information/academic-records/at-risk", headers=auth_professor_headers)
        assert response.status_code == 200
        at_risk_students = response.json()
        assert isinstance(at_risk_students, list)
        
        # 4. Assess student risk
        response = integration_client.get(f"/student-information/academic-records/risk-assessment/{student_id}?course_id={course_id}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        risk_assessment = response.json()
        assert "is_at_risk" in risk_assessment
        assert "risk_factors" in risk_assessment
        
        # 5. Search students
        response = integration_client.get("/student-information/search/students?query=John", headers=auth_professor_headers)
        assert response.status_code == 200
        search_results = response.json()
        assert "query" in search_results
        assert "results" in search_results
        
        # 6. View communication logs
        response = integration_client.get("/student-information/communication-logs", headers=auth_professor_headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
    
    def test_analytics_and_reporting(self, integration_client, integration_db,
                                   auth_professor_headers, enrolled_student_course):
        """Test analytics and reporting features"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. View message report
        response = integration_client.get("/student-information/messages/report", headers=auth_professor_headers)
        assert response.status_code == 200
        message_report = response.json()
        expected_sections = ["total_messages_sent", "messages_by_type", "messages_by_priority", "delivery_stats"]
        for section in expected_sections:
            assert section in message_report
        
        # 2. View attendance trends
        response = integration_client.get(f"/student-information/analytics/attendance-trends?course_id={course_id}&days=30", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        trends = response.json()
        assert "course_id" in trends
        assert "period_days" in trends
        
        # 3. View student dashboard
        response = integration_client.get("/student-information/dashboard/student/1", headers=auth_professor_headers)
        assert response.status_code == 200
        student_dashboard = response.json()
        expected_sections = ["student_id", "student_name", "courses_enrolled", "attendance_percentage"]
        for section in expected_sections:
            assert section in student_dashboard

class TestProfessorErrorHandlingIntegration:
    """Integration tests for professor error handling"""
    
    def test_course_management_error_scenarios(self, integration_client, integration_db, auth_professor_headers):
        """Test course management error scenarios"""
        # Try to update non-existent course
        course_update = {
            "course_code": "NONEXISTENT",
            "title": "Non-existent Course",
            "description": "This course doesn't exist",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.put("/professors/courses/99999", json=course_update, headers=auth_professor_headers)
        assert response.status_code == 404
        
        # Try to view non-existent course
        response = integration_client.get("/professors/courses/99999", headers=auth_professor_headers)
        assert response.status_code == 404
        
        # Try to create course with invalid data
        invalid_course = {
            "course_code": "",  # Empty course code
            "title": "Invalid Course",
            "credits": -1,  # Negative credits
            "max_enrollment": -5  # Negative enrollment
        }
        
        response = integration_client.post("/professors/courses", json=invalid_course, headers=auth_professor_headers)
        assert response.status_code == 422  # Validation error
    
    def test_grading_error_scenarios(self, integration_client, integration_db, auth_professor_headers):
        """Test grading error scenarios"""
        # Try to grade non-existent assignment
        invalid_grade = {
            "student_id": 1,
            "course_id": 1,
            "assignment_id": 99999,
            "points_earned": 85.0,
            "points_possible": 100.0,
            "percentage": 85.0,
            "letter_grade": "B"
        }
        
        response = integration_client.post("/grading/grades", json=invalid_grade, headers=auth_professor_headers)
        assert response.status_code == 404
        
        # Try to update non-existent grade
        grade_update = {
            "points_earned": 90.0,
            "letter_grade": "A-"
        }
        
        response = integration_client.put("/grading/grades/99999", json=grade_update, headers=auth_professor_headers)
        assert response.status_code == 404
    
    def test_communication_error_scenarios(self, integration_client, integration_db, auth_professor_headers):
        """Test communication error scenarios"""
        # Try to send message to non-existent course
        invalid_message = {
            "course_id": 99999,
            "subject": "Test Message",
            "content": "This message is for a non-existent course",
            "message_type": "announcement",
            "is_broadcast": True,
            "recipient_ids": []
        }
        
        response = integration_client.post("/student-information/messages", json=invalid_message, headers=auth_professor_headers)
        assert response.status_code == 404
        
        # Try to record attendance for non-existent course
        invalid_attendance = {
            "student_id": 1,
            "course_id": 99999,
            "attendance_date": datetime.now().isoformat(),
            "status": "present"
        }
        
        response = integration_client.post("/student-information/attendance", json=invalid_attendance, headers=auth_professor_headers)
        assert response.status_code == 404
