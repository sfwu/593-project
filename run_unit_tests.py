#!/usr/bin/env python3
"""
Comprehensive Unit Test Runner for Academic Information Management System

This script runs all unit tests and provides detailed coverage reports.
It includes tests for:
- Authentication system (JWT, password hashing)
- Database models (User, Student, Professor, Course)
- Pydantic schemas validation
- API controllers (auth, student, professor, course, grading, academic records, student info)
- Business logic and error handling
- Grading and assessment management
- Student information management
- Academic record tracking

Usage:
    python run_unit_tests.py              # Run all unit tests
    python run_unit_tests.py --verbose    # Run with verbose output
    python run_unit_tests.py --coverage   # Run with coverage report
    python run_unit_tests.py --module auth # Run specific module tests
    python run_unit_tests.py --module grading_assessment # Run grading tests
    python run_unit_tests.py --module student_information # Run student info tests
    python run_unit_tests.py --module academic_record # Run academic record tests
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(command, capture_output=False):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            return subprocess.run(command, shell=True).returncode
    except Exception as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return 1

def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("🔍 Checking testing dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-mock',
        'httpx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install " + ' '.join(missing_packages))
        return False
    
    print("✅ All testing dependencies are installed")
    return True

def run_unit_tests(verbose=False, coverage=False, module=None):
    """Run unit tests with specified options"""
    print("🧪 Running Unit Tests...")
    print("=" * 60)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    # Add specific module if specified
    if module:
        module_map = {
            'auth': 'tests/unit/test_auth.py',
            'models': 'tests/unit/test_models.py',
            'schemas': 'tests/unit/test_schemas.py',
            'auth_controller': 'tests/unit/test_auth_controller.py',
            'student_controller': 'tests/unit/test_student_controller.py',
            'professor_controller': 'tests/unit/test_professor_controller.py',
            'course_controller': 'tests/unit/test_course_controller.py',
            'grading_assessment_controller': 'tests/unit/test_grading_assessment_controller.py',
            'grading_assessment_service': 'tests/unit/test_grading_assessment_service.py',
            'student_information_controller': 'tests/unit/test_student_information_controller.py',
            'student_information_service': 'tests/unit/test_student_information_service.py',
            'academic_record_controller': 'tests/unit/test_academic_record_controller.py',
            'academic_record_service': 'tests/unit/test_academic_record_service.py',
            'grading_assessment': 'tests/unit/test_grading_assessment_controller.py tests/unit/test_grading_assessment_service.py',
            'student_information': 'tests/unit/test_student_information_controller.py tests/unit/test_student_information_service.py',
            'academic_record': 'tests/unit/test_academic_record_controller.py tests/unit/test_academic_record_service.py'
        }
        
        if module in module_map:
            cmd = ["python", "-m", "pytest", module_map[module]]
        else:
            print(f"❌ Unknown module: {module}")
            print(f"Available modules: {', '.join(module_map.keys())}")
            return 1
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    # Add additional options for better output
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "-ra"  # Show summary for all test results
    ])
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    return run_command(' '.join(cmd))

def run_lint_checks():
    """Run code quality checks"""
    print("\n🔍 Running Code Quality Checks...")
    print("=" * 60)
    
    # Check if flake8 is available
    if run_command("which flake8", capture_output=True)[0] == 0:
        print("📝 Running flake8 linting...")
        flake8_result = run_command("flake8 backend/ tests/ --max-line-length=100 --ignore=E203,W503")
        if flake8_result == 0:
            print("✅ Flake8 checks passed")
        else:
            print("⚠️ Flake8 found issues")
    else:
        print("⚠️ flake8 not found, skipping lint checks")

def display_test_summary():
    """Display a summary of what was tested"""
    print("\n📋 Test Coverage Summary")
    print("=" * 60)
    
    test_categories = [
        ("🔐 Authentication System", [
            "Password hashing and verification",
            "JWT token creation and validation", 
            "User authentication functions",
            "Role-based access control",
            "Token verification and user retrieval"
        ]),
        ("🗄️ Database Models", [
            "User model creation and validation",
            "Student model with profile fields",
            "Professor model with academic info",
            "Course model with enrollment limits",
            "Model relationships and associations"
        ]),
        ("📋 Pydantic Schemas", [
            "Authentication schemas (login, register, token)",
            "Student schemas (create, update, response)",
            "Professor schemas (create, update, response)",
            "Course schemas (create, update, response)",
            "Enrollment schemas and validation",
            "Email and password validation rules"
        ]),
        ("🌐 API Controllers", [
            "Authentication endpoints (login, registration)",
            "Student profile management",
            "Student course search and enrollment",
            "Professor profile management",
            "Professor course administration",
            "Enrollment management and statistics"
        ]),
        ("🛡️ Error Handling", [
            "Invalid credentials handling",
            "Duplicate registration prevention",
            "Course capacity validation",
            "Permission and authorization checks",
            "Database constraint validation"
        ])
    ]
    
    for category, items in test_categories:
        print(f"\n{category}")
        for item in items:
            print(f"  ✓ {item}")

def main():
    """Main function to run tests based on command line arguments"""
    parser = argparse.ArgumentParser(description="Run unit tests for Academic Management System")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--module", "-m", help="Run tests for specific module")
    parser.add_argument("--lint", "-l", action="store_true", help="Run lint checks")
    parser.add_argument("--summary", "-s", action="store_true", help="Show test summary only")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🎓 Academic Information Management System - Unit Tests")
    print("=" * 60)
    
    if args.summary:
        display_test_summary()
        return 0
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Run lint checks if requested
    if args.lint:
        run_lint_checks()
    
    # Run unit tests
    test_result = run_unit_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        module=args.module
    )
    
    # Display summary
    display_test_summary()
    
    # Final results
    print("\n" + "=" * 60)
    if test_result == 0:
        print("🎉 All tests passed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    return test_result

if __name__ == "__main__":
    sys.exit(main())
