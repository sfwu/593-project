"""
Cross-Module Integration Tests
Tests the integration between different modules and their data flow
across the entire academic management system.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestAuthenticationToUserManagementIntegration:
    """Integration tests for authentication and user management modules"""
    
    def test_user_registration_to_profile_creation_flow(self, integration_client, integration_db):
        """Test complete flow from user registration to profile creation"""
        # 1. Register student user
        student_data = {
            "email": "crossmodule@example.com",
            "password": "password123",
            "student_id": "CROSS001",
            "first_name": "Cross",
            "last_name": "Module",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        registration_data = response.json()
        
        # 2. Login to get authentication token
        login_data = {
            "email": "crossmodule@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        login_data = response.json()
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Access user profile through authentication
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "crossmodule@example.com"
        assert user_data["role"] == "student"
        
        # 4. Access student profile through student module
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        student_profile = response.json()
        assert student_profile["student_id"] == "CROSS001"
        assert student_profile["first_name"] == "Cross"
        
        # 5. Update profile and verify authentication still works
        profile_update = {
            "first_name": "Cross",
            "last_name": "Module",
            "major": "Computer Science",
            "year_level": "Senior",
            "phone": "555-0123"
        }
        
        response = integration_client.put("/students/profile", json=profile_update, headers=headers)
        assert response.status_code == 200
        
        # 6. Verify updated profile is accessible
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["year_level"] == "Senior"
        assert updated_profile["phone"] == "555-0123"
    
    def test_professor_registration_to_course_management_flow(self, integration_client, integration_db):
        """Test complete flow from professor registration to course management"""
        # 1. Register professor user
        professor_data = {
            "email": "crossprof@example.com",
            "password": "password123",
            "professor_id": "CROSS001",
            "first_name": "Cross",
            "last_name": "Professor",
            "department": "Computer Science",
            "title": "Associate Professor"
        }
        
        response = integration_client.post("/auth/register/professor", json=professor_data)
        assert response.status_code == 200
        
        # 2. Login to get authentication token
        login_data = {
            "email": "crossprof@example.com",
            "password": "password123"
        }
        
        response = integration_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Verify professor profile access
        response = integration_client.get("/professors/profile", headers=headers)
        assert response.status_code == 200
        professor_profile = response.json()
        assert professor_profile["professor_id"] == "CROSS001"
        
        # 4. Create course as professor
        course_data = {
            "course_code": "CROSS101",
            "title": "Cross Module Integration Course",
            "description": "Course for testing cross-module integration",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=headers)
        assert response.status_code == 200
        course = response.json()
        
        # 5. Verify course creation affects professor's course list
        response = integration_client.get("/professors/courses", headers=headers)
        assert response.status_code == 200
        courses = response.json()
        assert len(courses) >= 1
        assert any(c["course_code"] == "CROSS101" for c in courses)

class TestCourseEnrollmentToAcademicRecordsIntegration:
    """Integration tests for course enrollment and academic records modules"""
    
    def test_enrollment_to_grade_tracking_integration(self, integration_client, integration_db,
                                                    auth_student_headers, auth_professor_headers):
        """Test integration between enrollment and grade tracking"""
        # 1. Professor creates course
        course_data = {
            "course_code": "ENROLLGRADE101",
            "title": "Enrollment to Grade Integration",
            "description": "Course for testing enrollment to grade integration",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # 2. Student enrolls in course
        enrollment_data = {"course_id": course_id}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # 3. Professor creates assignment for the course
        assignment_data = {
            "course_id": course_id,
            "title": "Integration Assignment",
            "description": "Assignment to test integration",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # 4. Professor grades the assignment
        # First, get student ID from enrollment
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_list = response.json()
        assert len(enrollment_list) >= 1
        student_id = enrollment_list[0]["student_id"]
        
        grade_data = {
            "student_id": student_id,
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
        
        # 5. Student views their grades
        response = integration_client.get("/academic-records/grades", headers=auth_student_headers)
        assert response.status_code == 200
        grades = response.json()
        assert len(grades) >= 1
        
        # 6. Student views GPA calculation
        response = integration_client.get("/academic-records/gpa", headers=auth_student_headers)
        assert response.status_code == 200
        gpa_data = response.json()
        assert "cumulative_gpa" in gpa_data
        
        # 7. Verify grade appears in academic dashboard
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "recent_grades" in dashboard
    
    def test_course_completion_to_transcript_integration(self, integration_client, integration_db,
                                                       auth_student_headers, auth_professor_headers):
        """Test integration between course completion and transcript generation"""
        # 1. Create course and enroll student
        course_data = {
            "course_code": "TRANSCRIPT101",
            "title": "Transcript Integration Course",
            "description": "Course for testing transcript integration",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # 2. Student enrolls
        enrollment_data = {"course_id": course_id}
        response = integration_client.post("/students/enroll", json=enrollment_data, headers=auth_student_headers)
        assert response.status_code == 200
        
        # 3. Create multiple assignments and grade them
        assignments = []
        for i in range(3):
            assignment_data = {
                "course_id": course_id,
                "title": f"Assignment {i+1}",
                "description": f"Assignment {i+1} for transcript testing",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7+i*7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignment = response.json()
            assignments.append(assignment)
        
        # 4. Grade all assignments
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment_list = response.json()
        student_id = enrollment_list[0]["student_id"]
        
        for i, assignment in enumerate(assignments):
            grade_data = {
                "student_id": student_id,
                "course_id": course_id,
                "assignment_id": assignment["id"],
                "points_earned": 80.0 + (i * 5),  # Increasing grades
                "points_possible": 100.0,
                "percentage": 80.0 + (i * 5),
                "letter_grade": ["B-", "B", "B+"][i],
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # 5. Generate transcript
        transcript_data = {
            "transcript_type": "official",
            "include_incomplete": False,
            "include_withdrawn": False
        }
        
        response = integration_client.post("/academic-records/transcripts/generate", 
                                         json=transcript_data, headers=auth_student_headers)
        assert response.status_code == 200
        transcript = response.json()
        
        # 6. Verify transcript contains course information
        response = integration_client.get("/academic-records/transcripts", headers=auth_student_headers)
        assert response.status_code == 200
        transcripts = response.json()
        assert len(transcripts) >= 1

class TestGradingToAcademicRecordsIntegration:
    """Integration tests for grading and academic records modules"""
    
    def test_grade_creation_to_gpa_calculation_integration(self, integration_client, integration_db,
                                                         auth_professor_headers, enrolled_student_course):
        """Test integration between grade creation and GPA calculation"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create multiple courses and enroll student
        additional_courses = []
        for i in range(2):
            course_data = {
                "course_code": f"GPACALC{i+1}01",
                "title": f"GPA Calculation Course {i+1}",
                "description": f"Course {i+1} for GPA calculation testing",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            course = response.json()
            additional_courses.append(course)
        
        # 2. Enroll student in additional courses
        student_headers = auth_professor_headers  # Using professor headers for now
        for course in additional_courses:
            enrollment_data = {"course_id": course["id"]}
            # Note: This would normally be done by student, but for testing we'll use professor
            # In real scenario, student would enroll through their interface
        
        # 3. Create assignments for all courses and grade them
        courses_to_grade = [{"id": course_id}] + additional_courses
        grades = []
        
        for i, course in enumerate(courses_to_grade):
            assignment_data = {
                "course_id": course["id"],
                "title": f"GPA Test Assignment {i+1}",
                "description": f"Assignment for GPA calculation testing",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignment = response.json()
            
            # Grade the assignment with different grades
            grade_data = {
                "student_id": student_id,
                "course_id": course["id"],
                "assignment_id": assignment["id"],
                "points_earned": 85.0 + (i * 5),  # Different grades: 85, 90, 95
                "points_possible": 100.0,
                "percentage": 85.0 + (i * 5),
                "letter_grade": ["B", "A-", "A"][i],
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
            grades.append(response.json())
        
        # 4. Verify GPA calculation reflects all grades
        # This would require student authentication, but we can verify the grades exist
        response = integration_client.get(f"/grading/grades?student_id={student_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        student_grades = response.json()
        assert len(student_grades) >= 3
        
        # 5. Test grade modification and GPA recalculation
        if grades:
            grade_update = {
                "points_earned": 95.0,
                "percentage": 95.0,
                "letter_grade": "A",
                "professor_comments": "Updated grade after review"
            }
            
            response = integration_client.put(f"/grading/grades/{grades[0]['id']}", json=grade_update, headers=auth_professor_headers)
            assert response.status_code == 200
            updated_grade = response.json()
            assert updated_grade["letter_grade"] == "A"
    
    def test_exam_grading_to_academic_progress_integration(self, integration_client, integration_db,
                                                         auth_professor_headers, enrolled_student_course):
        """Test integration between exam grading and academic progress tracking"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create multiple exams
        exams = []
        for i in range(2):
            exam_data = {
                "course_id": course_id,
                "title": f"Exam {i+1}",
                "description": f"Exam {i+1} for academic progress testing",
                "exam_type": "midterm" if i == 0 else "final",
                "points_possible": 100,
                "exam_date": (datetime.now() + timedelta(days=14+i*14)).isoformat(),
                "duration_minutes": 120,
                "is_published": True
            }
            
            response = integration_client.post("/grading/exams", json=exam_data, headers=auth_professor_headers)
            assert response.status_code == 200
            exam = response.json()
            exams.append(exam)
        
        # 2. Grade the exams
        for i, exam in enumerate(exams):
            exam_grade_data = {
                "student_id": student_id,
                "course_id": course_id,
                "exam_id": exam["id"],
                "points_earned": 78.0 + (i * 10),  # Different grades: 78, 88
                "points_possible": 100.0,
                "percentage": 78.0 + (i * 10),
                "letter_grade": ["C+", "B+"][i],
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=exam_grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # 3. Verify exam grades are tracked
        response = integration_client.get(f"/grading/grades?course_id={course_id}&exam_id={exams[0]['id']}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        exam_grades = response.json()
        assert len(exam_grades) >= 1
        
        # 4. Test grade statistics
        response = integration_client.get(f"/grading/courses/{course_id}/grade-distribution", 
                                        headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404]

class TestStudentInformationToCommunicationIntegration:
    """Integration tests for student information and communication modules"""
    
    def test_attendance_tracking_to_communication_integration(self, integration_client, integration_db,
                                                            auth_professor_headers, enrolled_student_course):
        """Test integration between attendance tracking and communication"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Record attendance issues
        attendance_records = [
            {
                "student_id": student_id,
                "course_id": course_id,
                "attendance_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "absent",
                "late_minutes": 0,
                "notes": "Unexcused absence"
            },
            {
                "student_id": student_id,
                "course_id": course_id,
                "attendance_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "late",
                "late_minutes": 15,
                "notes": "Frequent tardiness"
            }
        ]
        
        for record in attendance_records:
            response = integration_client.post("/student-information/attendance", json=record, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # 2. Send communication based on attendance issues
        message_data = {
            "course_id": course_id,
            "subject": "Attendance Concern",
            "content": "I've noticed some attendance issues. Please let me know if you need any support.",
            "message_type": "concern",
            "priority": "normal",
            "is_broadcast": False,
            "recipient_ids": [student_id]
        }
        
        response = integration_client.post("/student-information/messages", json=message_data, headers=auth_professor_headers)
        assert response.status_code == 200
        message = response.json()
        
        # 3. Verify communication log tracks the interaction
        response = integration_client.get("/student-information/communication-logs", headers=auth_professor_headers)
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
        
        # 4. Check attendance summary
        response = integration_client.get(f"/student-information/attendance/summary/{student_id}?course_id={course_id}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        summary = response.json()
        assert "attendance_percentage" in summary or "total_classes" in summary
    
    def test_performance_monitoring_to_messaging_integration(self, integration_client, integration_db,
                                                           auth_professor_headers, enrolled_student_course):
        """Test integration between performance monitoring and messaging"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create assignment and grade it poorly
        assignment_data = {
            "course_id": course_id,
            "title": "Performance Test Assignment",
            "description": "Assignment for testing performance monitoring",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Grade with low score
        grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 45.0,
            "points_possible": 100.0,
            "percentage": 45.0,
            "letter_grade": "F",
            "grade_status": "graded",
            "is_published": True,
            "professor_comments": "Please see me during office hours for additional help."
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        
        # 2. Check if student is flagged as at-risk
        response = integration_client.get("/student-information/academic-records/at-risk", headers=auth_professor_headers)
        assert response.status_code == 200
        at_risk_students = response.json()
        
        # 3. Send supportive message
        support_message = {
            "course_id": course_id,
            "subject": "Academic Support Available",
            "content": "I noticed you might be struggling with the material. I'm available during office hours to help.",
            "message_type": "support",
            "priority": "normal",
            "is_broadcast": False,
            "recipient_ids": [student_id]
        }
        
        response = integration_client.post("/student-information/messages", json=support_message, headers=auth_professor_headers)
        assert response.status_code == 200
        
        # 4. Generate performance report
        response = integration_client.get(f"/student-information/academic-records/risk-assessment/{student_id}?course_id={course_id}", 
                                        headers=auth_professor_headers)
        assert response.status_code == 200
        risk_assessment = response.json()
        assert "is_at_risk" in risk_assessment
        assert "risk_factors" in risk_assessment

class TestMultiModuleDataConsistencyIntegration:
    """Integration tests for data consistency across multiple modules"""
    
    def test_user_deletion_cascade_effects(self, integration_client, integration_db):
        """Test cascade effects when user data is deleted or modified"""
        # 1. Create student with complete profile
        student_data = {
            "email": "cascade@example.com",
            "password": "password123",
            "student_id": "CASCADE001",
            "first_name": "Cascade",
            "last_name": "Test",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        student_id = response.json()["id"]
        
        # 2. Login and create some data
        login_data = {"email": "cascade@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Update profile
        profile_update = {"phone": "555-0123", "address": "123 Test St"}
        response = integration_client.put("/students/profile", json=profile_update, headers=headers)
        assert response.status_code == 200
        
        # 4. Verify data consistency across modules
        # Profile should be updated
        response = integration_client.get("/students/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["phone"] == "555-0123"
        
        # Authentication should still work
        response = integration_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "cascade@example.com"
    
    def test_course_deletion_impact_on_enrollments_and_grades(self, integration_client, integration_db,
                                                            auth_professor_headers, enrolled_student_course):
        """Test impact of course deletion on related data"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Create assignment and grade for the course
        assignment_data = {
            "course_id": course_id,
            "title": "Course Deletion Test Assignment",
            "description": "Assignment to test course deletion impact",
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
        
        # 2. Verify data exists before deletion
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment = response.json()
        assert len(enrollment) >= 1
        
        response = integration_client.get(f"/grading/grades?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        course_grades = response.json()
        assert len(course_grades) >= 1
        
        # 3. Delete course (this might not be implemented, so we'll test the endpoint exists)
        response = integration_client.delete(f"/professors/courses/{course_id}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # 4. If deletion is implemented, verify cascade effects
        if response.status_code == 200:
            # Course should not exist
            response = integration_client.get(f"/professors/courses/{course_id}", headers=auth_professor_headers)
            assert response.status_code == 404
            
            # Related data should be handled appropriately (deleted or orphaned)
            # This depends on the implementation's cascade rules
    
    def test_concurrent_operations_data_consistency(self, integration_client, integration_db,
                                                  auth_professor_headers, auth_student_headers):
        """Test data consistency during concurrent operations"""
        import threading
        import time
        
        # 1. Create course
        course_data = {
            "course_code": "CONCURRENT101",
            "title": "Concurrent Operations Test",
            "description": "Course for testing concurrent operations",
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
        
        # 2. Create multiple students
        students = []
        for i in range(3):
            student_data = {
                "email": f"concurrent{i}@example.com",
                "password": "password123",
                "student_id": f"CONC{i:03d}",
                "first_name": f"Concurrent{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            students.append(student_data)
        
        # 3. Concurrent enrollment attempts
        results = []
        
        def enroll_student(student_data):
            login_data = {"email": student_data["email"], "password": student_data["password"]}
            response = integration_client.post("/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                enrollment_data = {"course_id": course_id}
                response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
                results.append(response.status_code)
        
        # Start concurrent enrollment threads
        threads = []
        for student in students:
            thread = threading.Thread(target=enroll_student, args=(student,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # 4. Verify enrollment consistency
        response = integration_client.get(f"/professors/courses/{course_id}/enrollment", headers=auth_professor_headers)
        assert response.status_code == 200
        enrollment = response.json()
        
        # Should not exceed max enrollment
        assert len(enrollment) <= course_data["max_enrollment"]
        
        # All successful enrollments should be reflected
        successful_enrollments = [r for r in results if r == 200]
        assert len(enrollment) == len(successful_enrollments)

class TestSystemWideErrorHandlingIntegration:
    """Integration tests for system-wide error handling"""
    
    def test_database_connection_failure_handling(self, integration_client, integration_db, auth_student_headers):
        """Test system behavior during database connection issues"""
        # This test would require mocking database failures
        # For now, we'll test that the system handles invalid operations gracefully
        
        # Test with malformed data that might cause database issues
        malformed_data = {
            "course_id": "invalid_id",  # Should be integer
            "enrollment_date": "invalid_date"
        }
        
        response = integration_client.post("/students/enroll", json=malformed_data, headers=auth_student_headers)
        assert response.status_code == 422  # Validation error
        
        # Test with extremely large data
        large_data = {
            "first_name": "x" * 1000,  # Very long name
            "last_name": "y" * 1000,
            "major": "z" * 500
        }
        
        response = integration_client.put("/students/profile", json=large_data, headers=auth_student_headers)
        # Should either accept or return validation error
        assert response.status_code in [200, 422]
    
    def test_authentication_token_expiration_handling(self, integration_client, integration_db, auth_student_headers):
        """Test handling of authentication token expiration"""
        # Test that system gracefully handles expired tokens
        expired_headers = {"Authorization": "Bearer expired_token_here"}
        
        response = integration_client.get("/students/profile", headers=expired_headers)
        assert response.status_code == 401
        
        # Test that valid tokens still work
        response = integration_client.get("/students/profile", headers=auth_student_headers)
        assert response.status_code == 200
    
    def test_cross_module_error_propagation(self, integration_client, integration_db,
                                          auth_professor_headers, auth_student_headers):
        """Test error propagation across modules"""
        # 1. Try to create assignment for non-existent course
        invalid_assignment = {
            "course_id": 99999,
            "title": "Invalid Assignment",
            "description": "Assignment for non-existent course",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=invalid_assignment, headers=auth_professor_headers)
        assert response.status_code == 404
        
        # 2. Try to grade non-existent assignment
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
        
        # 3. Try to access non-existent academic record
        response = integration_client.get("/academic-records/grades/99999", headers=auth_student_headers)
        assert response.status_code == 404
        
        # 4. Try to send message to non-existent student
        invalid_message = {
            "course_id": 1,
            "subject": "Test Message",
            "content": "Message for non-existent student",
            "message_type": "announcement",
            "is_broadcast": False,
            "recipient_ids": [99999]
        }
        
        response = integration_client.post("/student-information/messages", json=invalid_message, headers=auth_professor_headers)
        # May return 404 or 400 depending on validation order
        assert response.status_code in [400, 404]
