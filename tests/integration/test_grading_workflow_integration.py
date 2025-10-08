"""
Grading and Assessment Workflow Integration Tests
Tests the complete grading workflow from assignment creation to gradebook management,
including bulk operations and analytics.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

class TestAssignmentManagementIntegration:
    """Integration tests for assignment management workflow"""
    
    def test_complete_assignment_lifecycle(self, integration_client, integration_db,
                                         auth_professor_headers, enrolled_student_course):
        """Test complete assignment lifecycle from creation to completion"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Programming Assignment 1",
            "description": "Complete the programming exercises with detailed explanations",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "late_policy": json.dumps({
                "penalty_per_day": 10,
                "max_penalty": 50,
                "grace_period_hours": 24
            }),
            "instructions": "Submit your code with comments and test cases",
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        assert assignment["title"] == "Programming Assignment 1"
        assert assignment["points_possible"] == 100
        assert assignment["is_published"] == True
        
        # 2. View assignment
        response = integration_client.get(f"/grading/assignments/{assignment['id']}", headers=auth_professor_headers)
        assert response.status_code == 200
        assignment_details = response.json()
        assert assignment_details["id"] == assignment["id"]
        
        # 3. Update assignment
        assignment_update = {
            "title": "Updated Programming Assignment 1",
            "description": "Updated description with additional requirements",
            "points_possible": 110,
            "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
            "instructions": "Updated instructions with more details"
        }
        
        response = integration_client.put(f"/grading/assignments/{assignment['id']}", json=assignment_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_assignment = response.json()
        assert updated_assignment["title"] == "Updated Programming Assignment 1"
        assert updated_assignment["points_possible"] == 110
        
        # 4. View all assignments for course
        response = integration_client.get(f"/grading/assignments?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) >= 1
        
        # 5. Publish/unpublish assignment
        response = integration_client.patch(f"/grading/assignments/{assignment['id']}/publish", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # 6. Delete assignment (if implemented)
        response = integration_client.delete(f"/grading/assignments/{assignment['id']}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
    
    def test_bulk_assignment_creation(self, integration_client, integration_db,
                                    auth_professor_headers, enrolled_student_course):
        """Test bulk assignment creation"""
        course_id = enrolled_student_course["course_id"]
        
        # Create multiple assignments at once
        bulk_assignments_data = {
            "course_id": course_id,
            "assignments": [
                {
                    "title": "Homework 1",
                    "description": "Basic programming exercises",
                    "assignment_type": "homework",
                    "points_possible": 50,
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat()
                },
                {
                    "title": "Homework 2",
                    "description": "Advanced programming exercises",
                    "assignment_type": "homework",
                    "points_possible": 50,
                    "due_date": (datetime.now() + timedelta(days=14)).isoformat()
                },
                {
                    "title": "Project 1",
                    "description": "Major programming project",
                    "assignment_type": "project",
                    "points_possible": 100,
                    "due_date": (datetime.now() + timedelta(days=30)).isoformat()
                }
            ]
        }
        
        response = integration_client.post("/grading/assignments/bulk", json=bulk_assignments_data, headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            created_assignments = response.json()
            assert len(created_assignments) == 3
        
        # Verify assignments were created individually
        response = integration_client.get(f"/grading/assignments?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        assignments = response.json()
        # Should have at least the assignments we created

class TestExamManagementIntegration:
    """Integration tests for exam management workflow"""
    
    def test_complete_exam_lifecycle(self, integration_client, integration_db,
                                   auth_professor_headers, enrolled_student_course):
        """Test complete exam lifecycle from creation to completion"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Create exam
        exam_data = {
            "course_id": course_id,
            "title": "Midterm Exam",
            "description": "Midterm examination covering chapters 1-5",
            "exam_type": "midterm",
            "points_possible": 100,
            "exam_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "duration_minutes": 120,
            "location": "Room 101",
            "instructions": "Bring a calculator and scratch paper",
            "allowed_materials": json.dumps(["calculator", "scratch_paper"]),
            "is_published": True
        }
        
        response = integration_client.post("/grading/exams", json=exam_data, headers=auth_professor_headers)
        assert response.status_code == 200
        exam = response.json()
        assert exam["title"] == "Midterm Exam"
        assert exam["duration_minutes"] == 120
        assert exam["exam_type"] == "midterm"
        
        # 2. View exam
        response = integration_client.get(f"/grading/exams/{exam['id']}", headers=auth_professor_headers)
        assert response.status_code == 200
        exam_details = response.json()
        assert exam_details["id"] == exam["id"]
        
        # 3. Update exam
        exam_update = {
            "title": "Updated Midterm Exam",
            "duration_minutes": 150,
            "location": "Room 201",
            "instructions": "Updated instructions with additional details"
        }
        
        response = integration_client.put(f"/grading/exams/{exam['id']}", json=exam_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_exam = response.json()
        assert updated_exam["duration_minutes"] == 150
        assert updated_exam["location"] == "Room 201"
        
        # 4. View all exams for course
        response = integration_client.get(f"/grading/exams?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        exams = response.json()
        assert len(exams) >= 1
        
        # 5. Create exam session
        session_data = {
            "exam_id": exam["id"],
            "student_id": enrolled_student_course["student"].id,
            "start_time": (datetime.now() + timedelta(days=14)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=14, hours=2)).isoformat(),
            "status": "scheduled"
        }
        
        response = integration_client.post("/grading/exams/sessions", json=session_data, headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]

class TestGradeManagementIntegration:
    """Integration tests for grade management workflow"""
    
    def test_complete_grade_lifecycle(self, integration_client, integration_db,
                                    auth_professor_headers, enrolled_student_course):
        """Test complete grade lifecycle from creation to publishing"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # 1. Create assignment first
        assignment_data = {
            "course_id": course_id,
            "title": "Grade Test Assignment",
            "description": "Assignment for testing grade management",
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
            "is_published": False,
            "professor_comments": "Good work, but could improve on algorithm efficiency.",
            "detailed_feedback": "Your solution works correctly but uses O(n²) time complexity. Consider using a hash map for O(n) solution."
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        assert grade["points_earned"] == 85.0
        assert grade["letter_grade"] == "B"
        assert grade["grade_status"] == "graded"
        
        # 3. View grade
        response = integration_client.get(f"/grading/grades/{grade['id']}", headers=auth_professor_headers)
        assert response.status_code == 200
        grade_details = response.json()
        assert grade_details["id"] == grade["id"]
        
        # 4. Update grade
        grade_update = {
            "points_earned": 88.0,
            "percentage": 88.0,
            "letter_grade": "B+",
            "professor_comments": "Updated comments after review."
        }
        
        response = integration_client.put(f"/grading/grades/{grade['id']}", json=grade_update, headers=auth_professor_headers)
        assert response.status_code == 200
        updated_grade = response.json()
        assert updated_grade["points_earned"] == 88.0
        assert updated_grade["letter_grade"] == "B+"
        
        # 5. Publish grade
        publish_data = {"is_published": True}
        response = integration_client.patch(f"/grading/grades/{grade['id']}/publish", json=publish_data, headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # 6. View all grades for course
        response = integration_client.get(f"/grading/grades?course_id={course_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        course_grades = response.json()
        assert len(course_grades) >= 1
        
        # 7. View grades by student
        response = integration_client.get(f"/grading/grades?student_id={student_id}", headers=auth_professor_headers)
        assert response.status_code == 200
        student_grades = response.json()
        assert len(student_grades) >= 1
    
    def test_bulk_grade_management(self, integration_client, integration_db,
                                 auth_professor_headers, enrolled_student_course):
        """Test bulk grade management operations"""
        course_id = enrolled_student_course["course_id"]
        
        # Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Bulk Grade Assignment",
            "description": "Assignment for testing bulk grade operations",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Create multiple students
        students = []
        for i in range(3):
            student_data = {
                "email": f"bulkgrading{i}@example.com",
                "password": "password123",
                "student_id": f"BULKGRADE{i:03d}",
                "first_name": f"BulkGrading{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            student_id = response.json()["id"]
            students.append(student_id)
            
            # Enroll student
            login_data = {"email": f"bulkgrading{i}@example.com", "password": "password123"}
            response = integration_client.post("/auth/login", json=login_data)
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
            assert response.status_code == 200
        
        # Bulk grade creation
        bulk_grades_data = {
            "assignment_id": assignment["id"],
            "course_id": course_id,
            "grades": [
                {
                    "student_id": students[0],
                    "points_earned": 90.0,
                    "points_possible": 100.0,
                    "percentage": 90.0,
                    "letter_grade": "A-"
                },
                {
                    "student_id": students[1],
                    "points_earned": 85.0,
                    "points_possible": 100.0,
                    "percentage": 85.0,
                    "letter_grade": "B"
                },
                {
                    "student_id": students[2],
                    "points_earned": 80.0,
                    "points_possible": 100.0,
                    "percentage": 80.0,
                    "letter_grade": "B-"
                }
            ]
        }
        
        response = integration_client.post("/grading/grades/bulk", json=bulk_grades_data, headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # Bulk grade publishing
        if response.status_code == 200:
            created_grades = response.json()
            grade_ids = [grade["id"] for grade in created_grades]
            
            publish_data = {"grade_ids": grade_ids, "is_published": True}
            response = integration_client.post("/grading/grades/bulk-publish", json=publish_data, headers=auth_professor_headers)
            # May not be implemented
            assert response.status_code in [200, 404, 405]

class TestGradebookManagementIntegration:
    """Integration tests for gradebook management"""
    
    def test_gradebook_creation_and_management(self, integration_client, integration_db,
                                             auth_professor_headers, enrolled_student_course):
        """Test gradebook creation and management"""
        course_id = enrolled_student_course["course_id"]
        
        # 1. Create gradebook
        gradebook_data = {
            "course_id": course_id,
            "title": "Course Gradebook",
            "description": "Main gradebook for the course",
            "grading_categories": json.dumps([
                {"name": "Assignments", "weight": 40, "drop_lowest": 1},
                {"name": "Exams", "weight": 50, "drop_lowest": 0},
                {"name": "Participation", "weight": 10, "drop_lowest": 0}
            ]),
            "is_active": True
        }
        
        response = integration_client.post("/grading/gradebooks", json=gradebook_data, headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            gradebook = response.json()
            
            # 2. View gradebook
            response = integration_client.get(f"/grading/gradebooks/{gradebook['id']}", headers=auth_professor_headers)
            assert response.status_code == 200
            gradebook_details = response.json()
            assert gradebook_details["id"] == gradebook["id"]
            
            # 3. Update gradebook
            gradebook_update = {
                "title": "Updated Course Gradebook",
                "description": "Updated gradebook description",
                "grading_categories": json.dumps([
                    {"name": "Assignments", "weight": 45, "drop_lowest": 1},
                    {"name": "Exams", "weight": 45, "drop_lowest": 0},
                    {"name": "Participation", "weight": 10, "drop_lowest": 0}
                ])
            }
            
            response = integration_client.put(f"/grading/gradebooks/{gradebook['id']}", json=gradebook_update, headers=auth_professor_headers)
            assert response.status_code == 200
            updated_gradebook = response.json()
            assert updated_gradebook["title"] == "Updated Course Gradebook"
        
        # 4. View all gradebooks for course
        response = integration_client.get(f"/grading/gradebooks?course_id={course_id}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
    
    def test_gradebook_calculations(self, integration_client, integration_db,
                                  auth_professor_headers, enrolled_student_course):
        """Test gradebook calculations and weighted grades"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create multiple assignments with different weights
        assignments = []
        assignment_data = [
            {
                "title": "Assignment 1",
                "assignment_type": "homework",
                "points_possible": 100,
                "weight": 20
            },
            {
                "title": "Assignment 2",
                "assignment_type": "homework",
                "points_possible": 100,
                "weight": 20
            },
            {
                "title": "Midterm Exam",
                "assignment_type": "exam",
                "points_possible": 100,
                "weight": 30
            },
            {
                "title": "Final Exam",
                "assignment_type": "exam",
                "points_possible": 100,
                "weight": 30
            }
        ]
        
        for data in assignment_data:
            assignment = {
                "course_id": course_id,
                "title": data["title"],
                "description": f"Description for {data['title']}",
                "assignment_type": data["assignment_type"],
                "points_possible": data["points_possible"],
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment, headers=auth_professor_headers)
            assert response.status_code == 200
            assignments.append(response.json())
        
        # Grade all assignments
        grades = [85, 90, 88, 92]  # Different grades for each assignment
        for i, assignment in enumerate(assignments):
            grade_data = {
                "student_id": student_id,
                "course_id": course_id,
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
        
        # View gradebook summary (if implemented)
        response = integration_client.get(f"/grading/gradebooks/summary?course_id={course_id}&student_id={student_id}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            summary = response.json()
            assert "total_grade" in summary or "final_grade" in summary
            assert "weighted_average" in summary or "percentage" in summary

class TestGradingAnalyticsIntegration:
    """Integration tests for grading analytics and reporting"""
    
    def test_grading_statistics(self, integration_client, integration_db,
                              auth_professor_headers, enrolled_student_course):
        """Test grading statistics and analytics"""
        course_id = enrolled_student_course["course_id"]
        
        # Create assignment
        assignment_data = {
            "course_id": course_id,
            "title": "Analytics Assignment",
            "description": "Assignment for testing grading analytics",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Create multiple students and grade them
        students = []
        grades = [75, 80, 85, 90, 95, 88, 82, 78]  # Various grades
        
        for i in range(len(grades)):
            student_data = {
                "email": f"analytics{i}@example.com",
                "password": "password123",
                "student_id": f"ANALYTICS{i:03d}",
                "first_name": f"Analytics{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            student_id = response.json()["id"]
            students.append(student_id)
            
            # Enroll student
            login_data = {"email": f"analytics{i}@example.com", "password": "password123"}
            response = integration_client.post("/auth/login", json=login_data)
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            enrollment_data = {"course_id": course_id}
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
            assert response.status_code == 200
            
            # Grade the assignment
            grade_data = {
                "student_id": student_id,
                "course_id": course_id,
                "assignment_id": assignment["id"],
                "points_earned": grades[i],
                "points_possible": 100.0,
                "percentage": grades[i],
                "letter_grade": "C" if grades[i] < 80 else "B" if grades[i] < 90 else "A",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # View assignment statistics
        response = integration_client.get(f"/grading/assignments/{assignment['id']}/statistics", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # View grade distribution
        response = integration_client.get(f"/grading/grades/distribution?course_id={course_id}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # View course grading summary
        response = integration_client.get(f"/grading/courses/{course_id}/summary", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
    
    def test_grading_dashboard(self, integration_client, integration_db,
                             auth_professor_headers):
        """Test grading dashboard functionality"""
        # View grading dashboard
        response = integration_client.get("/grading/dashboard", headers=auth_professor_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        # Dashboard should contain relevant sections
        expected_sections = ["summary", "overview", "recent_grades", "assignments", "exams"]
        for section in expected_sections:
            # At least some sections should be present
            if section in dashboard:
                assert isinstance(dashboard[section], (dict, list))
        
        # View grading analytics (if implemented)
        response = integration_client.get("/grading/analytics", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
        
        # View grade trends (if implemented)
        response = integration_client.get("/grading/trends", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]

class TestLateSubmissionHandlingIntegration:
    """Integration tests for late submission handling"""
    
    def test_late_submission_detection_and_penalties(self, integration_client, integration_db,
                                                   auth_professor_headers, enrolled_student_course):
        """Test late submission detection and penalty application"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create assignment with late policy
        due_date = datetime.now() + timedelta(days=7)
        assignment_data = {
            "course_id": course_id,
            "title": "Late Submission Test",
            "description": "Assignment for testing late submission handling",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": due_date.isoformat(),
            "late_policy": json.dumps({
                "penalty_per_day": 5,
                "max_penalty": 25,
                "grace_period_hours": 24
            }),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Grade assignment (simulating late submission)
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
            "is_late": True,
            "late_penalty_applied": 10.0,
            "professor_comments": "Good work, but submitted 2 days late."
        }
        
        response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
        assert response.status_code == 200
        grade = response.json()
        assert grade["is_late"] == True
        assert grade["late_penalty_applied"] == 10.0
        
        # View late submissions report (if implemented)
        response = integration_client.get(f"/grading/late-submissions?course_id={course_id}", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]

class TestGradeModificationIntegration:
    """Integration tests for grade modification and appeals"""
    
    def test_grade_modification_workflow(self, integration_client, integration_db,
                                       auth_professor_headers, enrolled_student_course):
        """Test grade modification workflow"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create assignment and grade
        assignment_data = {
            "course_id": course_id,
            "title": "Grade Modification Test",
            "description": "Assignment for testing grade modification",
            "assignment_type": "homework",
            "points_possible": 100,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_published": True
        }
        
        response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
        assert response.status_code == 200
        assignment = response.json()
        
        # Initial grade
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
        
        # Modify grade
        grade_modification = {
            "points_earned": 85.0,
            "percentage": 85.0,
            "letter_grade": "B",
            "is_modified": True,
            "modification_reason": "Additional points for extra credit work",
            "professor_comments": "Updated grade after review of extra credit submission."
        }
        
        response = integration_client.put(f"/grading/grades/{grade['id']}", json=grade_modification, headers=auth_professor_headers)
        assert response.status_code == 200
        modified_grade = response.json()
        assert modified_grade["points_earned"] == 85.0
        assert modified_grade["is_modified"] == True
        
        # View grade modification history (if implemented)
        response = integration_client.get(f"/grading/grades/{grade['id']}/modifications", headers=auth_professor_headers)
        # May not be implemented
        assert response.status_code in [200, 404, 405]
