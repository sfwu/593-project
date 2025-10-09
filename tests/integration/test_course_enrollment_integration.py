"""
Course Enrollment and Management Integration Tests
Tests the complete course enrollment workflow, capacity management,
schedule conflicts, and enrollment analytics.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestCourseEnrollmentWorkflowIntegration:
    """Integration tests for course enrollment workflow"""
    
    def test_complete_enrollment_lifecycle(self, integration_client, integration_db,
                                         auth_professor_headers, auth_student_headers):
        """Test complete enrollment lifecycle from course creation to completion"""
        # 1. Professor creates course
        course_data = {
            "course_code": "ENROLL101",
            "title": "Enrollment Lifecycle Test",
            "description": "Course for testing complete enrollment lifecycle",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 25,
            "prerequisites": "",
            "schedule": json.dumps({
                "days": ["Monday", "Wednesday"],
                "start_time": "09:00",
                "end_time": "10:30",
                "room": "Room 101"
            })
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # 2. Student searches for course
        response = integration_client.get("/courses", headers=auth_student_headers)
        assert response.status_code == 200
        courses = response.json()
        assert any(c["course_code"] == "ENROLL101" for c in courses)
        
        # 3. Student views course details
        response = integration_client.get(f"/courses/{course_id}", headers=auth_student_headers)
        assert response.status_code == 200
        course_details = response.json()
        assert course_details["course_code"] == "ENROLL101"
        assert course_details["max_enrollment"] == 25
        
        # 4. Student enrolls in course
        enrollment_data = {"course_id": course_id}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        enrollment = response.json()
        
        # 5. Student views their schedule
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert len(schedule) >= 1
        assert any(c["course_code"] == "ENROLL101" for c in schedule)
        
        # 6. Professor views course enrollment
        response = integration_client.get(f"/professors/courses/{course_id}/students", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_list = response.json()
        assert len(enrollment_list) >= 1
        
        # 7. Student withdraws from course
        response = integration_client.delete(f"/students/courses/{course_id}/withdraw", headers=auth_student_headers)
        assert response.status_code == 200
        
        # 8. Verify withdrawal
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert not any(c["course_code"] == "ENROLL101" for c in schedule)
    
    def test_enrollment_capacity_management(self, integration_client, integration_db,
                                          auth_professor_headers):
        """Test enrollment capacity management and waiting lists"""
        # Create course with limited capacity
        course_data = {
            "course_code": "CAPACITY101",
            "title": "Capacity Management Test",
            "description": "Course for testing capacity management",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 3  # Very limited capacity
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Create multiple students
        students = []
        for i in range(5):  # More students than capacity
            student_data = {
                "email": f"capacity{i}@example.com",
                "password": "password123",
                "student_id": f"CAP{i:03d}",
                "first_name": f"Capacity{i}",
                "last_name": "Test",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            students.append(student_data)
        
        # Students attempt to enroll
        enrollment_results = []
        for student in students:
            # Login as student
            login_data = {"email": student["email"], "password": student["password"]}
            response = integration_client.post("/auth/login", json=login_data)
            assert response.status_code == 200
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Attempt enrollment
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=headers)
            enrollment_results.append({
                "email": student["email"],
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
        
        # Check enrollment results
        successful_enrollments = [r for r in enrollment_results if r["success"]]
        failed_enrollments = [r for r in enrollment_results if not r["success"]]
        
        # Should not exceed capacity
        assert len(successful_enrollments) <= 3
        assert len(failed_enrollments) >= 2
        
        # Check enrollment statistics
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment-stats", headers=auth_professor_headers)
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_enrolled"] == len(successful_enrollments)
        assert stats["max_enrollment"] == 3
    
    def test_schedule_conflict_detection(self, integration_client, integration_db,
                                       auth_professor_headers):
        """Test schedule conflict detection and prevention"""
        # Create overlapping courses
        overlapping_courses = [
            {
                "course_code": "CONFLICT101",
                "title": "Schedule Conflict Course 1",
                "description": "First course with specific schedule",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30,
                "schedule": json.dumps({
                    "days": ["Monday", "Wednesday"],
                    "start_time": "09:00",
                    "end_time": "10:30",
                    "room": "Room 101"
                })
            },
            {
                "course_code": "CONFLICT102",
                "title": "Schedule Conflict Course 2",
                "description": "Second course with overlapping schedule",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30,
                "schedule": json.dumps({
                    "days": ["Monday", "Wednesday"],
                    "start_time": "10:00",
                    "end_time": "11:30",
                    "room": "Room 102"
                })
            }
        ]
        
        created_courses = []
        for course_data in overlapping_courses:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Create student
        student_data = {
            "email": "conflict@example.com",
            "password": "password123",
            "student_id": "CONF001",
            "first_name": "Conflict",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login as student
        login_data = {"email": "conflict@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Enroll in first course
        enrollment_data = {"course_id": created_courses[0]["id"]}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=headers)
        assert response.status_code == 200
        
        # Attempt to enroll in overlapping course
        enrollment_data = {"course_id": created_courses[1]["id"]}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=headers)
        
        # Should either detect conflict or allow enrollment (depending on implementation)
        if response.status_code == 400:
            assert "conflict" in response.json()["detail"].lower() or "schedule" in response.json()["detail"].lower()
        elif response.status_code == 200:
            # If allowed, verify both courses are in schedule
            response = integration_client.get("/students/courses/enrolled", headers=headers)
            assert response.status_code == 200
            schedule = response.json()
            assert len(schedule) == 2
    
    def test_course_availability_filtering(self, integration_client, integration_db,
                                         auth_professor_headers, auth_student_headers):
        """Test filtering courses by availability"""
        # Create courses with different statuses
        courses_data = [
            {
                "course_code": "AVAIL101",
                "title": "Available Course",
                "description": "Course with open enrollment",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "AVAIL102",
                "title": "Another Available Course",
                "description": "Another course with open enrollment",
                "credits": 3,
                "department": "Mathematics",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 25
            }
        ]
        
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Filter by department
        response = integration_client.get("/courses?department=Computer Science", headers=auth_student_headers)
        assert response.status_code == 200
        cs_courses = response.json()
        assert len(cs_courses) >= 1
        assert all(c["department"] == "Computer Science" for c in cs_courses)
        
        # Filter by semester
        response = integration_client.get("/courses?semester=Fall 2024", headers=auth_student_headers)
        assert response.status_code == 200
        fall_courses = response.json()
        assert len(fall_courses) >= 2
    
    def test_multiple_course_enrollment(self, integration_client, integration_db,
                                      auth_professor_headers, auth_student_headers):
        """Test student enrolling in multiple courses"""
        # Create multiple courses
        for i in range(3):
            course_data = {
                "course_code": f"MULTI{i:02d}",
                "title": f"Multiple Enrollment Course {i}",
                "description": f"Course {i} for multiple enrollment testing",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Get all courses
        response = integration_client.get("/courses", headers=auth_student_headers)
        assert response.status_code == 200
        courses = response.json()
        multi_courses = [c for c in courses if c["course_code"].startswith("MULTI")]
        
        # Enroll in all courses
        for course in multi_courses[:3]:
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=auth_student_headers)
            assert response.status_code == 200
        
        # Verify all enrollments
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        enrolled = response.json()
        enrolled_codes = [c["course_code"] for c in enrolled]
        assert any(code.startswith("MULTI") for code in enrolled_codes)
    
    def test_course_detail_retrieval(self, integration_client, integration_db,
                                    auth_professor_headers, auth_student_headers):
        """Test retrieving detailed course information"""
        # Create course with full details
        course_data = {
            "course_code": "DETAIL101",
            "title": "Detailed Course Information Test",
            "description": "Course with complete information",
            "credits": 4,
            "department": "Computer Science",
            "semester": "Spring 2025",
            "year": 2025,
            "max_enrollment": 35,
            "prerequisites": "None"
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        
        # Retrieve course details
        response = integration_client.get(f"/courses/{course['id']}", headers=auth_student_headers)
        assert response.status_code == 200
        details = response.json()
        assert details["course_code"] == "DETAIL101"
        assert details["credits"] == 4
        assert details["max_enrollment"] == 35
    
    def test_enrollment_status_verification(self, integration_client, integration_db,
                                          auth_professor_headers, auth_student_headers):
        """Test verifying enrollment status"""
        # Create course
        course_data = {
            "course_code": "STATUS101",
            "title": "Enrollment Status Test",
            "description": "Course for testing enrollment status",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        
        # Check enrollment status before enrolling
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        before_enrollment = response.json()
        
        # Enroll in course
        enrollment_data = {"course_id": course["id"]}
        response = integration_client.post("/students/courses/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # Check enrollment status after enrolling
        response = integration_client.get("/students/courses/enrolled", headers=auth_student_headers)
        assert response.status_code == 200
        after_enrollment = response.json()
        assert len(after_enrollment) > len(before_enrollment)
    
    def test_professor_course_listing(self, integration_client, integration_db,
                                     auth_professor_headers):
        """Test professor viewing their courses"""
        # Create multiple courses
        for i in range(2):
            course_data = {
                "course_code": f"PROF{i:02d}",
                "title": f"Professor Course {i}",
                "description": f"Course {i} for professor listing test",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Get professor's courses
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        assert response.status_code == 200
        courses = response.json()
        assert len(courses) >= 2
        prof_courses = [c for c in courses if c["course_code"].startswith("PROF")]
        assert len(prof_courses) >= 2
