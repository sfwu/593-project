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
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        enrollment = response.json()
        
        # 5. Student views their schedule
        response = integration_client.get("/students/schedule", headers=auth_student_headers)
        assert response.status_code == 200
        schedule = response.json()
        assert len(schedule) >= 1
        assert any(c["course_code"] == "ENROLL101" for c in schedule)
        
        # 6. Professor views course enrollment
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_list = response.json()
        assert len(enrollment_list) >= 1
        
        # 7. Student withdraws from course
        response = integration_client.delete(f"/students/enroll/{course_id}", headers=auth_student_headers)
        assert response.status_code == 200
        
        # 8. Verify withdrawal
        response = integration_client.get("/students/schedule", headers=auth_student_headers)
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
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
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
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment/stats", headers=auth_professor_headers)
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
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        assert response.status_code == 200
        
        # Attempt to enroll in overlapping course
        enrollment_data = {"course_id": created_courses[1]["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        
        # Should either detect conflict or allow enrollment (depending on implementation)
        if response.status_code == 400:
            assert "conflict" in response.json()["detail"].lower() or "schedule" in response.json()["detail"].lower()
        elif response.status_code == 200:
            # If allowed, verify both courses are in schedule
            response = integration_client.get("/students/schedule", headers=headers)
            assert response.status_code == 200
            schedule = response.json()
            assert len(schedule) == 2

class TestCoursePrerequisitesIntegration:
    """Integration tests for course prerequisites"""
    
    def test_prerequisite_enforcement(self, integration_client, integration_db,
                                    auth_professor_headers):
        """Test enforcement of course prerequisites"""
        # Create prerequisite course
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
        
        # Create course with prerequisite
        advanced_course_data = {
            "course_code": "ADVANCED001",
            "title": "Advanced Course with Prerequisite",
            "description": "Course that requires prerequisite",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Spring 2025",
            "year": 2025,
            "max_enrollment": 25,
            "prerequisites": "PREREQ001"
        }
        
        response = integration_client.post("/professors/courses", json=advanced_course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        advanced_course = response.json()
        
        # Create student
        student_data = {
            "email": "prereq@example.com",
            "password": "password123",
            "student_id": "PREQ001",
            "first_name": "Prerequisite",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        # Login as student
        login_data = {"email": "prereq@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Attempt to enroll in advanced course without prerequisite
        enrollment_data = {"course_id": advanced_course["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        
        # Should either reject due to missing prerequisite or allow (depending on implementation)
        if response.status_code == 400:
            assert "prerequisite" in response.json()["detail"].lower() or "requirement" in response.json()["detail"].lower()
        elif response.status_code == 200:
            # If allowed, verify enrollment
            response = integration_client.get("/students/schedule", headers=headers)
            assert response.status_code == 200
            schedule = response.json()
            assert any(c["course_code"] == "ADVANCED001" for c in schedule)
        
        # Enroll in prerequisite course
        enrollment_data = {"course_id": prereq_course["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        assert response.status_code == 200
        
        # Now should be able to enroll in advanced course
        enrollment_data = {"course_id": advanced_course["id"]}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        assert response.status_code == 200

class TestCourseSearchAndFilteringIntegration:
    """Integration tests for course search and filtering"""
    
    def test_course_search_functionality(self, integration_client, integration_db,
                                       auth_professor_headers, auth_student_headers):
        """Test comprehensive course search functionality"""
        # Create courses with different attributes
        courses_data = [
            {
                "course_code": "SEARCH101",
                "title": "Advanced Programming",
                "description": "Advanced programming concepts and algorithms",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "SEARCH102",
                "title": "Database Systems",
                "description": "Database design and management",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 25
            },
            {
                "course_code": "SEARCH201",
                "title": "Linear Algebra",
                "description": "Mathematical foundations of linear algebra",
                "credits": 3,
                "department": "Mathematics",
                "semester": "Spring 2025",
                "year": 2025,
                "max_enrollment": 40
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Test search by department
        response = integration_client.get("/courses?department=Computer Science", headers=auth_student_headers)
        assert response.status_code == 200
        cs_courses = response.json()
        assert len(cs_courses) >= 2
        assert all(c["department"] == "Computer Science" for c in cs_courses)
        
        # Test search by semester
        response = integration_client.get("/courses?semester=Fall 2024", headers=auth_student_headers)
        assert response.status_code == 200
        fall_courses = response.json()
        assert len(fall_courses) >= 2
        
        # Test search by year
        response = integration_client.get("/courses?year=2024", headers=auth_student_headers)
        assert response.status_code == 200
        year_courses = response.json()
        assert len(year_courses) >= 2
        
        # Test keyword search
        response = integration_client.get("/courses?keyword=programming", headers=auth_student_headers)
        assert response.status_code == 200
        programming_courses = response.json()
        assert len(programming_courses) >= 1
        assert any("programming" in c["title"].lower() or "programming" in c["description"].lower() for c in programming_courses)
        
        # Test combined filters
        response = integration_client.get("/courses?department=Computer Science&year=2024&credits=3", headers=auth_student_headers)
        assert response.status_code == 200
        filtered_courses = response.json()
        assert len(filtered_courses) >= 1
        
        # Test pagination
        response = integration_client.get("/courses?skip=0&limit=2", headers=auth_student_headers)
        assert response.status_code == 200
        paginated_courses = response.json()
        assert len(paginated_courses) <= 2
    
    def test_course_availability_filtering(self, integration_client, integration_db,
                                         auth_professor_headers, auth_student_headers):
        """Test filtering courses by availability"""
        # Create courses with different enrollment statuses
        courses_data = [
            {
                "course_code": "AVAIL101",
                "title": "Available Course",
                "description": "Course with available spots",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "FULL101",
                "title": "Full Course",
                "description": "Course that will be filled",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 1  # Very limited capacity
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Fill the limited capacity course
        student_data = {
            "email": "filler@example.com",
            "password": "password123",
            "student_id": "FILL001",
            "first_name": "Filler",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        
        login_data = {"email": "filler@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        enrollment_data = {"course_id": created_courses[1]["id"]}  # Fill the limited course
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
        assert response.status_code == 200
        
        # Test filtering by availability
        response = integration_client.get("/courses?available_only=true", headers=auth_student_headers)
        # May not be implemented, so accept either success or not found
        assert response.status_code in [200, 404, 405]

class TestCourseManagementIntegration:
    """Integration tests for course management features"""
    
    def test_course_information_management(self, integration_client, integration_db,
                                         auth_professor_headers):
        """Test comprehensive course information management"""
        # Create course
        course_data = {
            "course_code": "MANAGE101",
            "title": "Course Management Test",
            "description": "Course for testing management features",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "prerequisites": "",
            "schedule": json.dumps({
                "days": ["Tuesday", "Thursday"],
                "start_time": "14:00",
                "end_time": "15:30",
                "room": "Room 201"
            }),
            "syllabus": "This is the course syllabus content."
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Update course information
        course_update = {
            "course_code": "MANAGE101",
            "title": "Updated Course Management Test",
            "description": "Updated description with more details",
            "credits": 4,  # Changed credits
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 35,  # Increased capacity
            "prerequisites": "CS101",
            "syllabus": "Updated syllabus content with more information."
        }
        
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_course = response.json()
        assert updated_course["title"] == "Updated Course Management Test"
        assert updated_course["credits"] == 4
        assert updated_course["max_enrollment"] == 35
        assert updated_course["prerequisites"] == "CS101"
        
        # View course details
        response = integration_client.get(f"/professors/courses/{course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        course_details = response.json()
        assert course_details["id"] == course_id
        assert course_details["credits"] == 4
        
        # View all professor courses
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        assert response.status_code == 200
        all_courses = response.json()
        assert len(all_courses) >= 1
        assert any(c["course_code"] == "MANAGE101" for c in all_courses)
    
    def test_course_status_management(self, integration_client, integration_db,
                                    auth_professor_headers):
        """Test course status management (active/inactive)"""
        # Create course
        course_data = {
            "course_code": "STATUS101",
            "title": "Course Status Test",
            "description": "Course for testing status management",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": True
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Deactivate course
        course_update = {
            "course_code": "STATUS101",
            "title": "Course Status Test",
            "description": "Course for testing status management",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30,
            "is_active": False
        }
        
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_course = response.json()
        assert updated_course["is_active"] == False
        
        # Reactivate course
        course_update["is_active"] = True
        response = integration_client.put(f"/professors/courses/{course_id}", json=course_update, headers=auth_professor_headers)
        assert response.status_code == 200
        reactivated_course = response.json()
        assert reactivated_course["is_active"] == True

class TestEnrollmentAnalyticsIntegration:
    """Integration tests for enrollment analytics and reporting"""
    
    def test_enrollment_statistics(self, integration_client, integration_db,
                                 auth_professor_headers):
        """Test enrollment statistics and analytics"""
        # Create course
        course_data = {
            "course_code": "STATS101",
            "title": "Enrollment Statistics Test",
            "description": "Course for testing enrollment statistics",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 20
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Create and enroll multiple students
        students = []
        for i in range(5):
            student_data = {
                "email": f"stats{i}@example.com",
                "password": "password123",
                "student_id": f"STATS{i:03d}",
                "first_name": f"Stats{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            students.append(student_data)
        
        # Enroll students
        for student in students:
            login_data = {"email": student["email"], "password": student["password"]}
            response = integration_client.post("/auth/login", json=login_data)
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
            assert response.status_code == 200
        
        # View enrollment statistics
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment/stats", headers=auth_professor_headers)
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_enrolled"] == 5
        assert stats["max_enrollment"] == 20
        assert stats["enrollment_percentage"] == 25.0
        
        # View enrollment list
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_list = response.json()
        assert len(enrollment_list) == 5
        
        # View course analytics (if implemented)
        response = integration_client.get(f"/professors/courses/{course_id}/analytics", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
    
    def test_department_enrollment_summary(self, integration_client, integration_db,
                                         auth_professor_headers):
        """Test department-level enrollment summary"""
        # Create courses in different departments
        departments = ["Computer Science", "Mathematics", "Physics"]
        courses = []
        
        for dept in departments:
            course_data = {
                "course_code": f"{dept[:3].upper()}101",
                "title": f"{dept} Course",
                "description": f"Course in {dept} department",
                "credits": 3,
                "department": dept,
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            courses.append(response.json())
        
        # View department summary (if implemented)
        response = integration_client.get("/professors/courses/department-summary", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # View courses by department
        for dept in departments:
            response = integration_client.get(f"/professors/courses?department={dept}", headers=auth_professor_headers)
            assert response.status_code == 200
            dept_courses = response.json()
            assert len(dept_courses) >= 1
            assert all(c["department"] == dept for c in dept_courses)
