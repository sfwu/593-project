#!/usr/bin/env python3
"""
Simple script to run all tests
"""
import subprocess
import sys
import os

def run_unit_tests():
    """Run unit tests only"""
    print("🧪 Running Unit Tests...")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/", 
            "-v", 
            "--cov=backend",
            "--cov-report=term-missing",
            "-m", "not integration"
        ], check=True, capture_output=False)
        
        print("✅ Unit tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Unit tests failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install requirements: pip install -r requirements.txt")
        return False

def run_integration_tests():
    """Run integration tests only"""
    print("\n🔗 Running Integration Tests...")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/integration/", 
            "-v", 
            "--cov=backend",
            "--cov-append",
            "--cov-report=term-missing"
        ], check=True, capture_output=False)
        
        print("✅ Integration tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration tests failed with exit code: {e.returncode}")
        return False

def run_all_tests():
    """Run all tests with coverage"""
    print("🧪 Running Academic Information Management System Tests...")
    print("=" * 60)
    
    # Change to project directory
    project_dir = os.path.dirname(__file__)
    os.chdir(project_dir)
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--cov=backend",
            "--cov-report=term-missing"
        ], check=True, capture_output=False)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install requirements: pip install -r requirements.txt")
        return False

def run_linting():
    """Run code linting"""
    print("\n🔍 Running code linting...")
    
    try:
        # Run flake8
        subprocess.run([sys.executable, "-m", "flake8", "backend/", "tests/"], check=True)
        print("✅ No linting errors found!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Linting errors found")
        return False
    except FileNotFoundError:
        print("⚠️  flake8 not found, skipping linting")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Academic Management System Tests")
    parser.add_argument("--type", choices=["unit", "integration", "all"], default="all",
                       help="Type of tests to run (default: all)")
    parser.add_argument("--no-lint", action="store_true", help="Skip linting")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = os.path.dirname(__file__)
    os.chdir(project_dir)
    
    success = True
    
    # Run tests based on type
    if args.type == "unit":
        success &= run_unit_tests()
    elif args.type == "integration":
        success &= run_integration_tests()
    elif args.type == "all":
        success &= run_unit_tests()
        if success:
            success &= run_integration_tests()
    
    # Run linting unless skipped
    if not args.no_lint:
        success &= run_linting()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All checks passed! Your code is ready!")
        print("\n📊 Test Summary:")
        print("  Unit Tests: Fast, isolated, use mocks")
        print("  Integration Tests: Full stack with real database")
        print("  Both types are important for comprehensive testing!")
        sys.exit(0)
    else:
        print("💥 Some checks failed. Please review the output above.")
        sys.exit(1)
