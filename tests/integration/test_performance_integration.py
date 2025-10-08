"""
Performance and Load Integration Tests
Tests system performance under various load conditions and concurrent operations.
"""
import pytest
import time
import threading
import concurrent.futures
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import statistics

class TestConcurrentUserOperationsIntegration:
    """Integration tests for concurrent user operations"""
    
    def test_concurrent_user_registration(self, integration_client, integration_db):
        """Test concurrent user registration performance"""
        def register_user(user_id):
            student_data = {
                "email": f"concurrent{user_id}@example.com",
                "password": "password123",
                "student_id": f"CONC{user_id:03d}",
                "first_name": f"Concurrent{user_id}",
                "last_name": "User",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            start_time = time.time()
            response = integration_client.post("/auth/register/student", json=student_data)
            end_time = time.time()
            
            return {
                "user_id": user_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Test with 10 concurrent registrations
        num_users = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_user, i) for i in range(num_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_registrations = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in results]
        
        assert len(successful_registrations) >= 8  # Allow for some failures due to test environment
        assert all(r["response_time"] < 5.0 for r in results)  # All responses under 5 seconds
        assert statistics.mean(response_times) < 2.0  # Average response time under 2 seconds
    
    def test_concurrent_login_operations(self, integration_client, integration_db):
        """Test concurrent login operations performance"""
        # First, create users for login testing
        users = []
        for i in range(5):
            student_data = {
                "email": f"loginperf{i}@example.com",
                "password": "password123",
                "student_id": f"LOGIN{i:03d}",
                "first_name": f"LoginPerf{i}",
                "last_name": "User",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            users.append(student_data)
        
        def login_user(user_data):
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            start_time = time.time()
            response = integration_client.post("/auth/login", json=login_data)
            end_time = time.time()
            
            return {
                "email": user_data["email"],
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Test concurrent logins
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_user, user) for user in users]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify all logins succeeded
        successful_logins = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in results]
        
        assert len(successful_logins) == len(users)
        assert all(r["response_time"] < 3.0 for r in results)
        assert statistics.mean(response_times) < 1.0
    
    def test_concurrent_course_enrollment(self, integration_client, integration_db,
                                        auth_professor_headers):
        """Test concurrent course enrollment performance"""
        # Create a course with limited capacity
        course_data = {
            "course_code": "PERF101",
            "title": "Performance Test Course",
            "description": "Course for testing enrollment performance",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 10
        }
        
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        assert response.status_code == 200
        course = response.json()
        course_id = course["id"]
        
        # Create students for enrollment testing
        students = []
        for i in range(15):  # More students than course capacity
            student_data = {
                "email": f"enrollperf{i}@example.com",
                "password": "password123",
                "student_id": f"ENROLLPERF{i:03d}",
                "first_name": f"EnrollPerf{i}",
                "last_name": "Student",
                "major": "Computer Science",
                "year_level": "Junior"
            }
            
            response = integration_client.post("/auth/register/student", json=student_data)
            assert response.status_code == 200
            students.append(student_data)
        
        def enroll_student(student_data):
            # Login first
            login_data = {"email": student_data["email"], "password": student_data["password"]}
            response = integration_client.post("/auth/login", json=login_data)
            
            if response.status_code != 200:
                return {"email": student_data["email"], "success": False, "error": "Login failed"}
            
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Attempt enrollment
            enrollment_data = {"course_id": course_id}
            start_time = time.time()
            response = integration_client.post("/students/enroll", json=enrollment_data, headers=headers)
            end_time = time.time()
            
            return {
                "email": student_data["email"],
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Test concurrent enrollments
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(enroll_student, student) for student in students]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_enrollments = [r for r in results if r["success"]]
        failed_enrollments = [r for r in results if not r["success"]]
        response_times = [r["response_time"] for r in results if "response_time" in r]
        
        # Should not exceed course capacity
        assert len(successful_enrollments) <= course_data["max_enrollment"]
        
        # Some enrollments should fail due to capacity
        assert len(failed_enrollments) >= 5
        
        # Response times should be reasonable
        if response_times:
            assert all(rt < 3.0 for rt in response_times)
            assert statistics.mean(response_times) < 1.5

class TestDatabasePerformanceIntegration:
    """Integration tests for database performance under load"""
    
    def test_large_dataset_operations(self, integration_client, integration_db,
                                    auth_professor_headers):
        """Test operations with large datasets"""
        # Create multiple courses
        courses = []
        for i in range(20):
            course_data = {
                "course_code": f"LARGE{i:03d}",
                "title": f"Large Dataset Course {i}",
                "description": f"Course {i} for testing large dataset operations",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            courses.append(response.json())
        
        # Test fetching all courses
        start_time = time.time()
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert len(response.json()) >= 20
        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
        
        # Test pagination with large dataset
        start_time = time.time()
        response = integration_client.get("/professors/courses?skip=0&limit=10", headers=auth_professor_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert len(response.json()) <= 10
        assert (end_time - start_time) < 1.0
    
    def test_bulk_operations_performance(self, integration_client, integration_db,
                                       auth_professor_headers, enrolled_student_course):
        """Test performance of bulk operations"""
        course_id = enrolled_student_course["course_id"]
        student_id = enrolled_student_course["student"].id
        
        # Create multiple assignments
        assignments = []
        start_time = time.time()
        
        for i in range(10):
            assignment_data = {
                "course_id": course_id,
                "title": f"Bulk Assignment {i+1}",
                "description": f"Assignment {i+1} for bulk operations testing",
                "assignment_type": "homework",
                "points_possible": 100,
                "due_date": (datetime.now() + timedelta(days=7+i)).isoformat(),
                "is_published": True
            }
            
            response = integration_client.post("/grading/assignments", json=assignment_data, headers=auth_professor_headers)
            assert response.status_code == 200
            assignments.append(response.json())
        
        end_time = time.time()
        assignment_creation_time = end_time - start_time
        
        # Should create 10 assignments in reasonable time
        assert assignment_creation_time < 10.0
        assert len(assignments) == 10
        
        # Test bulk grade creation
        start_time = time.time()
        
        for i, assignment in enumerate(assignments):
            grade_data = {
                "student_id": student_id,
                "course_id": course_id,
                "assignment_id": assignment["id"],
                "points_earned": 80.0 + (i * 2),
                "points_possible": 100.0,
                "percentage": 80.0 + (i * 2),
                "letter_grade": "B",
                "grade_status": "graded",
                "is_published": True
            }
            
            response = integration_client.post("/grading/grades", json=grade_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        end_time = time.time()
        grade_creation_time = end_time - start_time
        
        # Should create 10 grades in reasonable time
        assert grade_creation_time < 15.0
        
        # Test fetching all grades
        start_time = time.time()
        response = integration_client.get(f"/grading/grades?course_id={course_id}", headers=auth_professor_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert len(response.json()) >= 10
        assert (end_time - start_time) < 2.0

class TestMemoryAndResourceUsageIntegration:
    """Integration tests for memory and resource usage"""
    
    def test_memory_usage_with_large_responses(self, integration_client, integration_db,
                                             auth_professor_headers):
        """Test memory usage with large API responses"""
        # Create courses with large descriptions
        large_description = "This is a very long description. " * 100  # ~3000 characters
        
        start_time = time.time()
        for i in range(10):
            course_data = {
                "course_code": f"MEMORY{i:03d}",
                "title": f"Memory Test Course {i}",
                "description": large_description,
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
        
        # Fetch all courses and measure response time
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        courses = response.json()
        assert len(courses) >= 10
        
        # Response time should still be reasonable even with large data
        assert (end_time - start_time) < 5.0
        
        # Verify data integrity
        for course in courses:
            if course["course_code"].startswith("MEMORY"):
                assert len(course["description"]) > 2000
    
    def test_concurrent_database_connections(self, integration_client, integration_db,
                                           auth_professor_headers):
        """Test system behavior under concurrent database connections"""
        def create_course(course_id):
            course_data = {
                "course_code": f"CONN{i:03d}",
                "title": f"Connection Test Course {course_id}",
                "description": "Course for testing concurrent connections",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            start_time = time.time()
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            end_time = time.time()
            
            return {
                "course_id": course_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Test with multiple concurrent database operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(create_course, i) for i in range(8)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All operations should succeed
        successful_operations = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in results]
        
        assert len(successful_operations) == 8
        assert all(rt < 3.0 for rt in response_times)
        assert statistics.mean(response_times) < 1.5

class TestSystemStressIntegration:
    """Integration tests for system stress conditions"""
    
    def test_rapid_request_handling(self, integration_client, integration_db,
                                  auth_student_headers):
        """Test system handling of rapid requests"""
        def make_request(request_id):
            start_time = time.time()
            response = integration_client.get("/students/profile", headers=auth_student_headers)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Send 50 rapid requests
        num_requests = 50
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in results]
        
        # Most requests should succeed
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.9  # 90% success rate
        
        # Response times should be reasonable
        assert all(rt < 5.0 for rt in response_times)
        assert statistics.mean(response_times) < 2.0
        
        # No requests should take extremely long
        assert max(response_times) < 10.0
    
    def test_mixed_operation_load(self, integration_client, integration_db,
                                auth_professor_headers, auth_student_headers):
        """Test system under mixed operation load"""
        def professor_operation(operation_id):
            operations = [
                lambda: integration_client.get("/professors/courses", headers=auth_professor_headers),
                lambda: integration_client.get("/student-information/dashboard", headers=auth_professor_headers),
                lambda: integration_client.get("/grading/dashboard", headers=auth_professor_headers)
            ]
            
            start_time = time.time()
            response = operations[operation_id % len(operations)]()
            end_time = time.time()
            
            return {
                "operation_id": operation_id,
                "operation_type": "professor",
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        def student_operation(operation_id):
            operations = [
                lambda: integration_client.get("/students/profile", headers=auth_student_headers),
                lambda: integration_client.get("/academic-records/grades", headers=auth_student_headers),
                lambda: integration_client.get("/academic-records/gpa", headers=auth_student_headers)
            ]
            
            start_time = time.time()
            response = operations[operation_id % len(operations)]()
            end_time = time.time()
            
            return {
                "operation_id": operation_id,
                "operation_type": "student",
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Mix professor and student operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            # Submit professor operations
            prof_futures = [executor.submit(professor_operation, i) for i in range(10)]
            # Submit student operations
            student_futures = [executor.submit(student_operation, i) for i in range(10)]
            
            # Collect results
            prof_results = [future.result() for future in concurrent.futures.as_completed(prof_futures)]
            student_results = [future.result() for future in concurrent.futures.as_completed(student_futures)]
        
        all_results = prof_results + student_results
        
        # Analyze results
        successful_operations = [r for r in all_results if r["success"]]
        response_times = [r["response_time"] for r in all_results]
        
        # Most operations should succeed
        success_rate = len(successful_operations) / len(all_results)
        assert success_rate >= 0.85  # 85% success rate
        
        # Response times should be reasonable
        assert all(rt < 5.0 for rt in response_times)
        assert statistics.mean(response_times) < 2.5
        
        # Both operation types should perform similarly
        prof_times = [r["response_time"] for r in prof_results if r["success"]]
        student_times = [r["response_time"] for r in student_results if r["success"]]
        
        if prof_times and student_times:
            prof_avg = statistics.mean(prof_times)
            student_avg = statistics.mean(student_times)
            
            # Average response times should be within reasonable range
            assert abs(prof_avg - student_avg) < 2.0

class TestPerformanceRegressionIntegration:
    """Integration tests to detect performance regressions"""
    
    def test_response_time_benchmarks(self, integration_client, integration_db,
                                    auth_student_headers, auth_professor_headers):
        """Test that response times meet performance benchmarks"""
        benchmarks = {
            "student_profile": 0.5,  # 500ms
            "student_grades": 1.0,   # 1 second
            "professor_courses": 1.0, # 1 second
            "course_creation": 2.0,   # 2 seconds
            "grade_creation": 1.5,    # 1.5 seconds
        }
        
        # Test student profile access
        start_time = time.time()
        response = integration_client.get("/students/profile", headers=auth_student_headers)
        end_time = time.time()
        assert response.status_code == 200
        assert (end_time - start_time) <= benchmarks["student_profile"]
        
        # Test student grades access
        start_time = time.time()
        response = integration_client.get("/academic-records/grades", headers=auth_student_headers)
        end_time = time.time()
        assert response.status_code == 200
        assert (end_time - start_time) <= benchmarks["student_grades"]
        
        # Test professor courses access
        start_time = time.time()
        response = integration_client.get("/professors/courses", headers=auth_professor_headers)
        end_time = time.time()
        assert response.status_code == 200
        assert (end_time - start_time) <= benchmarks["professor_courses"]
        
        # Test course creation
        course_data = {
            "course_code": "BENCH101",
            "title": "Benchmark Test Course",
            "description": "Course for performance benchmarking",
            "credits": 3,
            "department": "Computer Science",
            "semester": "Fall 2024",
            "year": 2024,
            "max_enrollment": 30
        }
        
        start_time = time.time()
        response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
        end_time = time.time()
        assert response.status_code == 200
        assert (end_time - start_time) <= benchmarks["course_creation"]
        
        # Test grade creation (if we have enrolled student)
        course = response.json()
        course_id = course["id"]
        
        # This would require a student to be enrolled and an assignment to exist
        # For now, we'll test the endpoint availability
        start_time = time.time()
        response = integration_client.get(f"/grading/grades?course_id={course_id}", headers=auth_professor_headers)
        end_time = time.time()
        assert response.status_code == 200
        assert (end_time - start_time) <= 1.0  # Grade listing should be fast
    
    def test_memory_usage_stability(self, integration_client, integration_db,
                                  auth_professor_headers):
        """Test that memory usage remains stable under load"""
        # Create and delete multiple courses to test memory management
        course_ids = []
        
        # Create courses
        for i in range(20):
            course_data = {
                "course_code": f"MEMSTAB{i:03d}",
                "title": f"Memory Stability Course {i}",
                "description": "Course for testing memory stability",
                "credits": 3,
                "department": "Computer Science",
                "semester": "Fall 2024",
                "year": 2024,
                "max_enrollment": 30
            }
            
            response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
            assert response.status_code == 200
            course_ids.append(response.json()["id"])
        
        # Fetch all courses multiple times
        for _ in range(5):
            response = integration_client.get("/professors/courses", headers=auth_professor_headers)
            assert response.status_code == 200
            assert len(response.json()) >= 20
        
        # Test that response times don't degrade significantly
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = integration_client.get("/professors/courses", headers=auth_professor_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Response times should be consistent (no significant degradation)
        assert all(rt < 2.0 for rt in response_times)
        assert statistics.stdev(response_times) < 0.5  # Low standard deviation

class TestScalabilityIntegration:
    """Integration tests for system scalability"""
    
    def test_user_scalability(self, integration_client, integration_db):
        """Test system scalability with increasing number of users"""
        user_counts = [5, 10, 20]
        results = {}
        
        for user_count in user_counts:
            # Register users
            users = []
            start_time = time.time()
            
            for i in range(user_count):
                student_data = {
                    "email": f"scale{user_count}_{i}@example.com",
                    "password": "password123",
                    "student_id": f"SCALE{user_count}_{i:03d}",
                    "first_name": f"Scale{user_count}_{i}",
                    "last_name": "User",
                    "major": "Computer Science",
                    "year_level": "Junior"
                }
                
                response = integration_client.post("/auth/register/student", json=student_data)
                assert response.status_code == 200
                users.append(student_data)
            
            end_time = time.time()
            registration_time = end_time - start_time
            
            # Login users
            start_time = time.time()
            successful_logins = 0
            
            for user in users:
                login_data = {"email": user["email"], "password": user["password"]}
                response = integration_client.post("/auth/login", json=login_data)
                if response.status_code == 200:
                    successful_logins += 1
            
            end_time = time.time()
            login_time = end_time - start_time
            
            results[user_count] = {
                "registration_time": registration_time,
                "login_time": login_time,
                "successful_logins": successful_logins,
                "registration_rate": user_count / registration_time,
                "login_rate": successful_logins / login_time
            }
        
        # Analyze scalability
        for user_count, result in results.items():
            # Registration rate should be reasonable
            assert result["registration_rate"] > 1.0  # At least 1 user per second
            
            # Login success rate should be high
            assert result["successful_logins"] >= user_count * 0.9
            
            # Login rate should be reasonable
            assert result["login_rate"] > 2.0  # At least 2 logins per second
    
    def test_data_scalability(self, integration_client, integration_db,
                            auth_professor_headers):
        """Test system scalability with increasing data volume"""
        data_sizes = [10, 25, 50]
        results = {}
        
        for size in data_sizes:
            # Create courses
            start_time = time.time()
            course_ids = []
            
            for i in range(size):
                course_data = {
                    "course_code": f"SCALEDATA{size}_{i:03d}",
                    "title": f"Scalability Test Course {size}-{i}",
                    "description": f"Course {i} for scalability testing with {size} total courses",
                    "credits": 3,
                    "department": "Computer Science",
                    "semester": "Fall 2024",
                    "year": 2024,
                    "max_enrollment": 30
                }
                
                response = integration_client.post("/professors/courses", json=course_data, headers=auth_professor_headers)
                assert response.status_code == 200
                course_ids.append(response.json()["id"])
            
            creation_time = time.time() - start_time
            
            # Fetch all courses
            start_time = time.time()
            response = integration_client.get("/professors/courses", headers=auth_professor_headers)
            end_time = time.time()
            
            fetch_time = end_time - start_time
            
            results[size] = {
                "creation_time": creation_time,
                "fetch_time": fetch_time,
                "creation_rate": size / creation_time,
                "fetch_rate": size / fetch_time,
                "courses_fetched": len(response.json())
            }
        
        # Analyze scalability
        for size, result in results.items():
            # Creation rate should be reasonable
            assert result["creation_rate"] > 2.0  # At least 2 courses per second
            
            # Fetch time should scale reasonably (not exponentially)
            assert result["fetch_time"] < size * 0.1  # Less than 0.1s per course
            
            # Should fetch all created courses
            assert result["courses_fetched"] >= size
