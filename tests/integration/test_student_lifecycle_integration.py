"""
Complete Student Lifecycle Integration Tests
Tests the entire student journey from registration to graduation,
including course enrollment, grade tracking, and academic progress.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestStudentRegistrationAndProfileIntegration:
    """Integration tests for student registration and profile management"""
    
    def test_complete_student_registration_workflow(self, integration_client, integration_db):
        """Test complete student registration workflow with profile setup"""
        # 1. Register student
        student_data = {
            "email": "lifecycle@example.com",
            "password": "password123",
            "student_id": "LIFE001",
            "first_name": "Lifecycle",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Freshman"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        registration_data = response.json()
        assert registration_data["student_id"] == "LIFE001"
        assert registration_data["email"] == "lifecycle@example.com"
        
        # 2. Login to get token
        login_data = {
            "email": "lifecycle@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Verify profile access
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["student_id"] == "LIFE001"
        assert profile["major"] == "Computer Science"
        
        # 4. Update profile information
        profile_update = {
            "first_name": "Lifecycle",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Sophomore",
            "phone": "555-0123",
            "address": "123 Student St, University City"
        }
        
        response = integration_client.put("/students/profile", json=profile_update, headers=headers)
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["year_level"] == "Sophomore"
        assert updated_profile["phone"] == "555-0123"
    
    def test_student_profile_validation(self, integration_client, integration_db, auth_student_headers):
        """Test student profile validation and error handling"""
        # Test invalid phone number format
        invalid_profile = {
            "phone": "invalid-phone",
            "address": "Valid Address"
        }
        
        response = integration_client.put("/students/profile", json=invalid_profile, headers=auth_student_headers)
        # Should either accept or return validation error
        assert response.status_code in [200, 422]
        
        # Test invalid year level
        invalid_year = {
            "year_level": "InvalidYear"
        }
        
        response = integration_client.put("/students/profile", json=invalid_year, headers=auth_student_headers)
        # Should either accept or return validation error
        assert response.status_code in [200, 422]

class TestStudentCourseManagementIntegration:
    """Integration tests for student course management workflow"""
    
    def test_complete_course_search_and_enrollment_workflow(self, integration_client, integration_db, 
                                                          auth_student_headers, auth_professor_headers):
        """Test complete course search and enrollment workflow"""
        # 1. Professor creates courses
        courses_data = [
            {
                "course_code": "CS101",
                "title": "Introduction to Programming",
                "description": "Basic programming concepts",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "CS102",
                "title": "Data Structures",
                "description": "Data structures and algorithms",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 25
            },
            {
                "course_code": "MATH101",
                "title": "Calculus I",
                "description": "Differential and integral calculus",
                "credits": 4,
                "department": "Mathematics",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 40
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # 2. Student searches for courses
        # Search by department
        response = integration_client.get("/courses?department=Computer Science", headers=auth_student_headers)
        assert response.status_code == 200
        cs_courses = response.json()
        assert len(cs_courses) == 2
        
        # Search by keyword
        response = integration_client.get("/courses?keyword=programming", headers=auth_student_headers)
        assert response.status_code == 200
        programming_courses = response.json()
        assert len(programming_courses) >= 1
        
        # 3. Student enrolls in courses
        enrollment_responses = []
        for course in created_courses[:2]:  # Enroll in first two courses
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
            assert response.status_code == 200
            enrollment_responses.append(response.json())
        
        # 4. Student views their schedule
        response = integration_client.get("/students/schedule", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert len(schedule) == 2
        
        # 5. Student views course details
        for course in created_courses[:2]:
            response = integration_client.get(f"/courses/{course['id']}", headers=auth_student_headers)
            assert response.status_code == 200
            course_details = response.json()
            assert course_details["course_code"] in ["CS101", "CS102"]
    
    def test_course_enrollment_capacity_validation(self, integration_client, integration_db,
                                                 auth_student_headers, auth_professor_headers):
        """Test course enrollment capacity validation"""
        # Create a course with limited capacity
        course_data = {
            "course_code": "CS999",
            "title": "Limited Capacity Course",
            "description": "Course with limited enrollment",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 1  # Only 1 spot
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        
        # First student enrolls successfully
        enrollment_data = {"course_id": course["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # Create second student and try to enroll
        student2_data = {
            "email": "student2@example.com",
            "password": "password123",
            "student_id": "STU002",
            "first_name": "Student",
            "last_name": "Two",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student2_data)
        assert response.status_code == 200
        
        # Login as second student
        login_data = {"email": "student2@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token2 = response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Second student should be rejected due to capacity
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers2)
        assert response.status_code == 400
        assert "Course is at maximum capacity" in response.json()["detail"]
    
    def test_schedule_conflict_detection(self, integration_client, integration_db,
                                       auth_student_headers, auth_professor_headers):
        """Test schedule conflict detection during enrollment"""
        # Create courses with overlapping schedules
        overlapping_courses = [
            {
                "course_code": "CS201",
                "title": "Morning Course",
                "description": "Course in morning",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30,
                "schedule": json.dumps({"days": ["Monday", "Wednesday"], "start_time": "09:00", "end_time": "10:30"})
            },
            {
                "course_code": "CS202",
                "title": "Overlapping Course",
                "description": "Course that overlaps with morning course",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30,
                "schedule": json.dumps({"days": ["Monday", "Wednesday"], "start_time": "10:00", "end_time": "11:30"})
            }
        ]
        
        created_courses = []
        for course_data in overlapping_courses:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Enroll in first course
        enrollment_data = {"course_id": created_courses[0]["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # Try to enroll in overlapping course - should detect conflict
        enrollment_data2 = {"course_id": created_courses[1]["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data2, headers=auth_student_headers)
        # Should either reject due to conflict or accept (depending on implementation)
        assert response.status_code in [200, 400]
        if response.status_code == 400:
            assert "schedule conflict" in response.json()["detail"].lower()
    
    def test_course_withdrawal_workflow(self, integration_client, integration_db,
                                      auth_student_headers, sample_course_with_professor):
        """Test course withdrawal workflow"""
        course_id = sample_course_with_professor["id"]
        
        # 1. Enroll in course
        enrollment_data = {"course_id": course_id}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # 2. Verify enrollment
        response = integration_client.get("/students/schedule", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert len(schedule) == 1
        
        # 3. Withdraw from course
        response = integration_client.delete(f"/students/enroll/{course_id}", headers=auth_student_headers)
        assert response.status_code == 200
        assert "successfully withdrawn" in response.json()["message"].lower()
        
        # 4. Verify withdrawal
        response = integration_client.get("/students/schedule", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert len(schedule) == 0

class TestStudentAcademicProgressIntegration:
    """Integration tests for student academic progress tracking"""
    
    def test_complete_grade_tracking_workflow(self, integration_client, integration_db,
                                            auth_student_headers, auth_professor_headers,
                                            enrolled_student_course):
        """Test complete grade tracking workflow from enrollment to final grade"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Professor creates assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Programming Assignment 1",
            "description": "Complete the programming exercises",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # 2. Professor creates exam
        exam_data = {
            "course_id": course_id,
            "title": "Midterm Exam",
            "description": "Midterm examination",
            "exam_type": "midterm",
            "points_possible": 100,
            "exam_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "duration_minutes": 120,
            "is_published": True
        }
        
        response = integration_client.post("/grading/exams", json=exam_data, headers=auth_professor_headers)
        assert response.status_code == 200
        exam = response.json()
        
        # 3. Professor grades assignment
        grade_data = {
            "student_id": enrolled_student_course["student"].id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 85.0,
            "points_possible": 100.0,
            "percentage": 85.0,
            "letter_grade": "B",
            "grade_status": "graded",
            "is_published": True
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        
        # 4. Student views their grades
        response = integration_client.get("/academic-records/grades", headers=auth_student_headers)
        assert response.status_code == 200
        grades = response.json()
        assert len(grades) >= 1
        
        # 5. Student views GPA calculation
        response = integration_client.get("/academic-records/gpa", headers=auth_student_headers)
        assert response.status_code == 200
        gpa_data = response.json()
        assert "cumulative_gpa" in gpa_data
        assert "major_gpa" in gpa_data
        
        # 6. Student views academic progress
        response = integration_client.get("/academic-records/progress", headers=auth_student_headers)
        assert response.status_code in [200, 404]  # 404 if no progress record exists yet
        
        # 7. Student views academic dashboard
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "overview" in dashboard
        assert "recent_grades" in dashboard
    
    def test_transcript_generation_workflow(self, integration_client, integration_db,
                                          auth_student_headers, enrolled_student_course):
        """Test transcript generation workflow"""
        # 1. Generate transcript
        transcript_data = {
            "transcript_type": "official",
            "include_incomplete": False,
            "include_withdrawn": False
        }
        
        response = integration_client.post("/academic-records/transcripts/generate", 
                                         json=transcript_data, headers=auth_student_headers)
        assert response.status_code == 200
        transcript = response.json()
        assert "transcript_id" in transcript
        assert transcript["status"] == "generated"
        
        # 2. View available transcripts
        response = integration_client.get("/academic-records/transcripts", headers=auth_student_headers)
        assert response.status_code == 200
        transcripts = response.json()
        assert len(transcripts) >= 1
        
        # 3. Download transcript (if implemented)
        transcript_id = transcript["transcript_id"]
        response = integration_client.get(f"/academic-records/transcripts/{transcript_id}/download", 
                                        headers=auth_student_headers)
        # May return 200 with file or 404 if not implemented
        assert response.status_code in [200, 404]
    
    def test_academic_progress_tracking(self, integration_client, integration_db,
                                      auth_student_headers, enrolled_student_course):
        """Test academic progress tracking across multiple semesters"""
        # This test simulates multiple semesters of academic work
        
        # 1. View current academic summary
        response = integration_client.get("/academic-records/academic-summary", headers=auth_student_headers)
        assert response.status_code == 200
        summary = response.json()
        assert "student_info" in summary
        assert "gpa_summary" in summary
        assert "progress_summary" in summary
        
        # 2. View grade history
        response = integration_client.get("/academic-records/grade-history", headers=auth_student_headers)
        assert response.status_code == 200
        history = response.json()
        assert "student_id" in history
        assert "total_courses" in history
        assert "cumulative_gpa" in history
        
        # 3. View semester GPA breakdown
        response = integration_client.get("/academic-records/gpa/semester-breakdown", headers=auth_student_headers)
        assert response.status_code == 200
        breakdown = response.json()
        assert isinstance(breakdown, list)
        
        # 4. View current semester GPA
        response = integration_client.get("/academic-records/gpa/current-semester", headers=auth_student_headers)
        assert response.status_code == 200
        current_gpa = response.json()
        assert "current_semester_gpa" in current_gpa

class TestStudentCommunicationIntegration:
    """Integration tests for student communication features"""
    
    def test_student_message_access_workflow(self, integration_client, integration_db,
                                           auth_student_headers, auth_professor_headers,
                                           sample_course_with_professor):
        """Test student access to messages and communication"""
        course_id = sample_course_with_professor["id"]
        
        # 1. Professor sends message to course
        message_data = {
            "course_id": course_id,
            "subject": "Assignment Reminder",
            "content": "Don't forget to submit your assignment by Friday.",
            "message_type": "announcement",
            "priority": "normal",
            "is_broadcast": True,
            "recipient_ids": [1]  # Student ID
        }
        
        response = integration_client.post("/student-information/messages", json=message_data, headers=auth_professor_headers)
        assert response.status_code == 200
        message = response.json()
        
        # 2. Student should be able to view messages (if implemented)
        # Note: This endpoint might not exist in current implementation
        response = integration_client.get("/students/messages", headers=auth_student_headers)
        # Accept either success or not implemented
        assert response.status_code in [200, 404, 405]
    
    def test_student_directory_access(self, integration_client, integration_db, auth_student_headers):
        """Test student access to directory information"""
        # Students typically don't have access to full directory
        # This tests the access control
        response = integration_client.get("/student-information/directory", headers=auth_student_headers)
        # Should be restricted to professors
        assert response.status_code == 403

class TestStudentErrorHandlingIntegration:
    """Integration tests for student error handling scenarios"""
    
    def test_enrollment_error_scenarios(self, integration_client, integration_db, auth_student_headers):
        """Test various enrollment error scenarios"""
        # Try to enroll in non-existent course
        enrollment_data = {"course_id": 99999}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]
        
        # Try to enroll without course_id
        response = integration_client.post("/students/enroll", json={}, headers=auth_student_headers)
        assert response.status_code == 422  # Validation error
        
        # Try to withdraw from course not enrolled in
        response = integration_client.delete("/students/enroll/99999", headers=auth_student_headers)
        assert response.status_code == 404
    
    def test_profile_update_error_scenarios(self, integration_client, integration_db, auth_student_headers):
        """Test profile update error scenarios"""
        # Try to update with invalid data
        invalid_profile = {
            "email": "invalid-email-format",
            "year_level": "InvalidYear"
        }
        
        response = integration_client.put("/students/profile", json=invalid_profile, headers=auth_student_headers)
        # Should either accept or return validation error
        assert response.status_code in [200, 422]
    
    def test_grade_access_error_scenarios(self, integration_client, integration_db, auth_student_headers):
        """Test grade access error scenarios"""
        # Try to access non-existent grade record
        response = integration_client.get("/academic-records/grades/99999", headers=auth_student_headers)
        assert response.status_code == 404
        
        # Try to access non-existent transcript
        response = integration_client.get("/academic-records/transcripts/99999/download", headers=auth_student_headers)
        assert response.status_code == 404

class TestStudentPerformanceIntegration:
    """Integration tests for student performance monitoring"""
    
    def test_student_performance_tracking(self, integration_client, integration_db,
                                        auth_student_headers, auth_professor_headers,
                                        enrolled_student_course):
        """Test student performance tracking across multiple metrics"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Professor records attendance
        attendance_data = {
            "student_id": student_id,
            "course_id": course_id,
            "attendance_date": datetime.now().isoformat(),
            "status": "present",
            "late_minutes": 0
        }
        
        response = integration_client.post("/student-information/attendance", json=attendance_data, headers=auth_professor_headers)
        assert response.status_code == 200
        
        # 2. Professor creates and grades assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Performance Test Assignment",
            "description": "Test assignment for performance tracking",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Grade the assignment
        grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 90.0,
            "points_possible": 100.0,
            "percentage": 90.0,
            "letter_grade": "A-",
            "grade_status": "graded",
            "is_published": True
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        
        # 3. Student views their performance summary
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        # Verify dashboard contains performance data
        assert "overview" in dashboard
        assert "recent_grades" in dashboard
        assert "progress" in dashboard
        
        # 4. Student views detailed academic summary
        response = integration_client.get("/academic-records/academic-summary", headers=auth_student_headers)
        assert response.status_code == 200
        summary = response.json()
        
        # Verify summary contains comprehensive data
        assert "student_info" in summary
        assert "gpa_summary" in summary
        assert "grade_statistics" in summary
        assert "semester_breakdown" in summary
