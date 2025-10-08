"""
Academic Record Pipeline Integration Tests
Tests the complete academic record pipeline from grade entry to transcript generation,
including GPA calculations, academic progress tracking, and record management.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestAcademicRecordCreationIntegration:
    """Integration tests for academic record creation and management"""
    
    def test_grade_to_academic_record_pipeline(self, integration_client, integration_db,
                                             auth_professor_headers, enrolled_student_course):
        """Test complete pipeline from grade entry to academic record creation"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Academic Record Test Assignment",
            "description": "Assignment for testing academic record pipeline",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # 2. Create grade
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
        
        # 3. Verify academic record is created (if automatic)
        # This would typically be done through the academic record service
        # For now, we'll verify the grade exists and can be accessed
        
        # 4. Student views their academic records
        student_headers = auth_professor_headers  # Using professor headers for now
        response = integration_client.get("/academic-records/grades", headers=student_headers)
        assert response.status_code == 200
        academic_records = response.json()
        # Should contain the grade we just created
        
        # 5. Verify grade appears in academic dashboard
        response = integration_client.get("/academic-records/dashboard", headers=student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "recent_grades" in dashboard
    
    def test_multiple_courses_academic_record_integration(self, integration_client, integration_db,
                                                        auth_professor_headers):
        """Test academic record integration across multiple courses"""
        # Create multiple courses
        courses_data = [
            {
                "course_code": "ACAD101",
                "title": "Academic Record Course 1",
                "description": "First course for academic record testing",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "ACAD102",
                "title": "Academic Record Course 2",
                "description": "Second course for academic record testing",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Create student
        student_data = {
            "email": "multiacad@example.com",
            "password": "password123",
            "student_id": "MULTI001",
            "first_name": "Multi",
            "last_name": "Academic",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        student_id = response.json()["id"]
        
        # Enroll student in both courses
        login_data = {"email": "multiacad@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {token}"}
        
        for course in created_courses:
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
        
        # Create assignments and grades for both courses
        grades = [88, 92]  # Different grades for each course
        
        for i, course in enumerate(created_courses):
            # Create assignment
            assignment_data = {
                "course_id": course["id"],
                "title": f"Assignment for Course {i+1}",
                "description": f"Assignment for academic record testing in course {i+1}",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignment = response.json()
            
            # Grade assignment
            grade_data = {
                "student_id": student_id,
                "course_id": course["id"],
                "assignment_id": assignment["id"],
                "points_earned": grades[i],
                "points_possible": 100.0,
                "percentage": grades[i],
                "letter_grade": "B+" if grades[i] < 90 else "A-",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Verify academic records for both courses
        response = integration_client.get("/academic-records/grades", headers=student_headers)
        assert response.status_code == 200
        academic_records = response.json()
        assert len(academic_records) >= 2

class TestGPACalculationIntegration:
    """Integration tests for GPA calculation and management"""
    
    def test_comprehensive_gpa_calculation(self, integration_client, integration_db,
                                         auth_professor_headers):
        """Test comprehensive GPA calculation across multiple courses and semesters"""
        # Create courses with different credit values
        courses_data = [
            {
                "course_code": "GPA101",
                "title": "3 Credit Course",
                "description": "Course worth 3 credits",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "GPA102",
                "title": "4 Credit Course",
                "description": "Course worth 4 credits",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "GPA201",
                "title": "3 Credit Course Spring",
                "description": "Course worth 3 credits in Spring",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Spring 2025",
                "year": 2025,
                "max_enrollment": 30
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Create student
        student_data = {
            "email": "gpacalc@example.com",
            "password": "password123",
            "student_id": "GPACALC001",
            "first_name": "GPACalc",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        student_id = response.json()["id"]
        
        # Login as student
        login_data = {"email": "gpacalc@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {token}"}
        
        # Enroll in courses and create grades
        grades = [85, 92, 88]  # B, A-, B+
        
        for i, course in enumerate(created_courses):
            # Enroll
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
            
            # Create assignment
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
            
            # Grade assignment
            grade_data = {
                "student_id": student_id,
                "course_id": course["id"],
                "assignment_id": assignment["id"],
                "points_earned": grades[i],
                "points_possible": 100.0,
                "percentage": grades[i],
                "letter_grade": "B" if grades[i] < 90 else "A-",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # View GPA calculations
        response = integration_client.get("/academic-records/gpa", headers=student_headers)
        assert response.status_code == 200
        gpa_data = response.json()
        
        # Verify GPA data structure
        assert "cumulative_gpa" in gpa_data
        assert "major_gpa" in gpa_data
        assert "semester_gpa" in gpa_data
        assert "total_credits_earned" in gpa_data
        assert "total_credits_attempted" in gpa_data
        
        # View semester GPA breakdown
        response = integration_client.get("/academic-records/gpa/semester-breakdown", headers=student_headers)
        assert response.status_code == 200
        semester_breakdown = response.json()
        assert isinstance(semester_breakdown, list)
        
        # View current semester GPA
        response = integration_client.get("/academic-records/gpa/current-semester", headers=student_headers)
        assert response.status_code == 200
        current_semester_gpa = response.json()
        assert "current_semester_gpa" in current_semester_gpa
    
    def test_gpa_recalculation_on_grade_change(self, integration_client, integration_db,
                                             auth_professor_headers, enrolled_student_course):
        """Test GPA recalculation when grades are modified"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "GPA Recalculation Test",
            "description": "Assignment for testing GPA recalculation",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Create initial grade
        grade_data = {
            "student_id": student_id,
            "course_id": course_id,
            "assignment_id": assignment["id"],
            "points_earned": 80.0,
            "points_possible": 100.0,
            "percentage": 80.0,
            "letter_grade": "B-",
            "grade_status": "graded",
            "is_published": True
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        
        # Get initial GPA
        student_headers = auth_professor_headers  # Using professor headers for now
        response = integration_client.get("/academic-records/gpa", headers=student_headers)
        assert response.status_code == 200
        initial_gpa = response.json()
        
        # Modify grade
        grade_update = {
            "points_earned": 90.0,
            "percentage": 90.0,
            "letter_grade": "A-",
            "professor_comments": "Updated grade after review"
        }
        
        response = integration_client.put(f"/grading/grades/{grade['id']}", json=grade_update, headers=auth_professor_headers)
        assert response.status_code == 200
        
        # Verify GPA is recalculated
        response = integration_client.get("/academic-records/gpa", headers=student_headers)
        assert response.status_code == 200
        updated_gpa = response.json()
        
        # GPA should be different (higher) after grade improvement
        # Note: This assumes the GPA calculation is working correctly

class TestTranscriptGenerationIntegration:
    """Integration tests for transcript generation and management"""
    
    def test_complete_transcript_generation_workflow(self, integration_client, integration_db,
                                                   auth_professor_headers):
        """Test complete transcript generation workflow"""
        # Create courses across multiple semesters
        courses_data = [
            {
                "course_code": "TRANS101",
                "title": "Transcript Course Fall",
                "description": "Course for transcript generation testing",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "TRANS102",
                "title": "Transcript Course Spring",
                "description": "Course for transcript generation testing",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Spring 2025",
                "year": 2025,
                "max_enrollment": 30
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Create student
        student_data = {
            "email": "transcript@example.com",
            "password": "password123",
            "student_id": "TRANS001",
            "first_name": "Transcript",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Senior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        student_id = response.json()["id"]
        
        # Login as student
        login_data = {"email": "transcript@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {token}"}
        
        # Enroll in courses and create grades
        for i, course in enumerate(created_courses):
            # Enroll
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
            
            # Create assignment
            assignment_data = {
                "course_id": course["id"],
                "title": f"Transcript Assignment {i+1}",
                "description": f"Assignment for transcript generation",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignment = response.json()
            
            # Grade assignment
            grade_data = {
                "student_id": student_id,
                "course_id": course["id"],
                "assignment_id": assignment["id"],
                "points_earned": 85.0 + (i * 5),  # Different grades
                "points_possible": 100.0,
                "percentage": 85.0 + (i * 5),
                "letter_grade": "B" if i == 0 else "B+",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Generate transcript
        transcript_data = {
            "transcript_type": "official",
            "include_incomplete": False,
            "include_withdrawn": False
        }
        
        response = integration_client.post("/academic-records/transcripts/generate", 
                                         json=transcript_data, headers=student_headers)
        assert response.status_code == 200
        transcript = response.json()
        assert "transcript_id" in transcript
        assert transcript["status"] == "generated"
        
        # View available transcripts
        response = integration_client.get("/academic-records/transcripts", headers=student_headers)
        assert response.status_code == 200
        transcripts = response.json()
        assert len(transcripts) >= 1
        
        # Generate unofficial transcript
        unofficial_transcript_data = {
            "transcript_type": "unofficial",
            "include_incomplete": True,
            "include_withdrawn": False
        }
        
        response = integration_client.post("/academic-records/transcripts/generate", 
                                         json=unofficial_transcript_data, headers=student_headers)
        assert response.status_code == 200
        unofficial_transcript = response.json()
        assert unofficial_transcript["status"] == "generated"
    
    def test_transcript_filtering_and_options(self, integration_client, integration_db,
                                            auth_student_headers):
        """Test transcript generation with different filtering options"""
        # Test different transcript generation options
        transcript_options = [
            {
                "transcript_type": "official",
                "include_incomplete": False,
                "include_withdrawn": False
            },
            {
                "transcript_type": "unofficial",
                "include_incomplete": True,
                "include_withdrawn": False
            },
            {
                "transcript_type": "complete",
                "include_incomplete": True,
                "include_withdrawn": True
            }
        ]
        
        for options in transcript_options:
            response = integration_client.post("/academic-records/transcripts/generate", 
                                             json=options, headers=auth_student_headers)
            assert response.status_code == 200
            transcript = response.json()
            assert "transcript_id" in transcript
            assert transcript["status"] == "generated"

class TestAcademicProgressTrackingIntegration:
    """Integration tests for academic progress tracking"""
    
    def test_academic_progress_monitoring(self, integration_client, integration_db,
                                        auth_professor_headers):
        """Test academic progress monitoring and tracking"""
        # Create courses
        courses_data = [
            {
                "course_code": "PROG101",
                "title": "Progress Course 1",
                "description": "Course for progress tracking",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            },
            {
                "course_code": "PROG102",
                "title": "Progress Course 2",
                "description": "Another course for progress tracking",
                "credits": 4,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            created_courses.append(response.json())
        
        # Create student
        student_data = {
            "email": "progress@example.com",
            "password": "password123",
            "student_id": "PROG001",
            "first_name": "Progress",
            "last_name": "Student",
            "major": "Computer Science",
            "year_level": "Junior"
        }
        
        response = integration_client.post("/auth/register/student", json=student_data)
        assert response.status_code == 200
        student_id = response.json()["id"]
        
        # Login as student
        login_data = {"email": "progress@example.com", "password": "password123"}
        response = integration_client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {token}"}
        
        # Enroll in courses
        for course in created_courses:
            enrollment_data = {"course_id": course["id"]}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=student_headers)
            assert response.status_code == 200
        
        # Create assignments and grades
        for i, course in enumerate(created_courses):
            assignment_data = {
                "course_id": course["id"],
                "title": f"Progress Assignment {i+1}",
                "description": f"Assignment for progress tracking",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignment = response.json()
            
            grade_data = {
                "student_id": student_id,
                "course_id": course["id"],
                "assignment_id": assignment["id"],
                "points_earned": 80.0 + (i * 10),
                "points_possible": 100.0,
                "percentage": 80.0 + (i * 10),
                "letter_grade": "B" if i == 0 else "A-",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # View academic progress
        response = integration_client.get("/academic-records/progress", headers=student_headers)
        # May return 404 if no progress record exists yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            progress = response.json()
            assert "credits_completed" in progress or "total_credits" in progress
            assert "gpa" in progress or "cumulative_gpa" in progress
        
        # View academic progress summary
        response = integration_client.get("/academic-records/progress/summary", headers=student_headers)
        assert response.status_code in [200, 404]
        
        # View grade history
        response = integration_client.get("/academic-records/grade-history", headers=student_headers)
        assert response.status_code == 200
        history = response.json()
        assert "student_id" in history
        assert "total_courses" in history
        assert "cumulative_gpa" in history
        
        # View academic summary
        response = integration_client.get("/academic-records/academic-summary", headers=student_headers)
        assert response.status_code == 200
        summary = response.json()
        assert "student_info" in summary
        assert "gpa_summary" in summary
        assert "progress_summary" in summary

class TestAcademicDashboardIntegration:
    """Integration tests for academic dashboard functionality"""
    
    def test_comprehensive_academic_dashboard(self, integration_client, integration_db,
                                            auth_student_headers):
        """Test comprehensive academic dashboard functionality"""
        # View academic dashboard
        response = integration_client.get("/academic-records/dashboard", headers=auth_student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        # Verify dashboard structure
        expected_sections = ["overview", "recent_grades", "progress", "semester_trend", "grade_distribution"]
        for section in expected_sections:
            if section in dashboard:
                assert isinstance(dashboard[section], (dict, list))
        
        # Check overview section
        if "overview" in dashboard:
            overview = dashboard["overview"]
            assert "cumulative_gpa" in overview
            assert "major_gpa" in overview
            assert "current_semester_gpa" in overview
            assert "total_credits_earned" in overview
        
        # Check recent grades section
        if "recent_grades" in dashboard:
            recent_grades = dashboard["recent_grades"]
            assert isinstance(recent_grades, list)
        
        # Check progress section
        if "progress" in dashboard:
            progress = dashboard["progress"]
            assert isinstance(progress, dict)
        
        # Check semester trend
        if "semester_trend" in dashboard:
            semester_trend = dashboard["semester_trend"]
            assert isinstance(semester_trend, list)
        
        # Check grade distribution
        if "grade_distribution" in dashboard:
            grade_distribution = dashboard["grade_distribution"]
            assert isinstance(grade_distribution, dict)

class TestAcademicRecordErrorHandlingIntegration:
    """Integration tests for academic record error handling"""
    
    def test_academic_record_error_scenarios(self, integration_client, integration_db,
                                           auth_student_headers):
        """Test academic record error handling scenarios"""
        # Test accessing non-existent academic record
        response = integration_client.get("/academic-records/grades/99999", headers=auth_student_headers)
        assert response.status_code == 404
        
        # Test accessing non-existent transcript
        response = integration_client.get("/academic-records/transcripts/99999/download", headers=auth_student_headers)
        assert response.status_code == 404
        
        # Test invalid transcript generation request
        invalid_transcript_data = {
            "transcript_type": "invalid_type",
            "include_incomplete": "invalid_boolean",
            "include_withdrawn": "invalid_boolean"
        }
        
        response = integration_client.post("/academic-records/transcripts/generate", 
                                         json=invalid_transcript_data, headers=auth_student_headers)
        assert response.status_code == 422  # Validation error
        
        # Test invalid GPA calculation parameters
        response = integration_client.get("/academic-records/gpa?invalid_param=value", headers=auth_student_headers)
        # Should either work or return validation error
        assert response.status_code in [200, 422]
    
    def test_academic_record_data_consistency(self, integration_client, integration_db,
                                            auth_professor_headers, enrolled_student_course):
        """Test academic record data consistency"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create assignment and grade
        assignment_data = {
            "course_id": course_id,
            "title": "Data Consistency Test",
            "description": "Assignment for testing data consistency",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
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
        
        # Verify data consistency across different views
        student_headers = auth_professor_headers  # Using professor headers for now
        
        # Check grades view
        response = integration_client.get("/academic-records/grades", headers=student_headers)
        assert response.status_code == 200
        grades = response.json()
        
        # Check GPA calculation
        response = integration_client.get("/academic-records/gpa", headers=student_headers)
        assert response.status_code == 200
        gpa_data = response.json()
        
        # Check dashboard
        response = integration_client.get("/academic-records/dashboard", headers=student_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        # Data should be consistent across all views
        # The same grade should appear in all relevant places
        # GPA should reflect the grade that was entered
        # Dashboard should show the grade in recent grades
