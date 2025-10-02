"""
Streamlit frontend for Academic Information Management System
Complete authentication system with role-based access
"""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import numpy as np

# Configuration
API_BASE_URL = "http://localhost:9600"

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="Academic Information Management System",
    page_icon="🎓",
    layout="wide"
)
    
# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def main():
    """Main Streamlit application with authentication"""
    # Check if user is authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_application()

def show_login_page():
    """Display login page with authentication options"""
    st.title("🎓 Academic Information Management System")
    st.markdown("### Welcome! Please sign in to continue")
    
    # Create tabs for different authentication options
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "🔑 Change Password", "📧 Forgot Password"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        if st.session_state.authenticated:
            show_change_password_form()
        else:
            st.info("Please login first to change your password.")
    
    with tab3:
        show_forgot_password_form()

def show_login_form():
    """Display login form"""
    st.markdown("#### Sign In")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("🔐 Login", type="primary")
        with col2:
            register_button = st.form_submit_button("📝 Register")
        
        if login_button:
            if email and password:
                login_user(email, password)
            else:
                st.error("Please enter both email and password.")
        
        if register_button:
            st.session_state.show_registration = True
            st.rerun()

def show_change_password_form():
    """Display change password form"""
    st.markdown("#### Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password", help="Password must be at least 6 characters long")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        # Password validation warning
        if new_password and len(new_password) < 6:
            st.warning("⚠️ New password must be at least 6 characters long")
        
        change_button = st.form_submit_button("🔑 Change Password", type="primary")
        
        if change_button:
            if current_password and new_password and confirm_password:
                if len(new_password) < 6:
                    st.error("❌ New password must be at least 6 characters long.")
                elif new_password == confirm_password:
                    change_password(current_password, new_password)
                else:
                    st.error("❌ New passwords do not match.")
            else:
                st.error("❌ Please fill in all fields.")

def show_forgot_password_form():
    """Display forgot password form"""
    st.markdown("#### Forgot Password")
    st.info("Enter your email address and we'll send you a password reset link.")
    
    with st.form("forgot_password_form"):
        email = st.text_input("Email", placeholder="Enter your email address")
        
        reset_button = st.form_submit_button("📧 Send Reset Link", type="primary")
        
        if reset_button:
            if email:
                forgot_password(email)
            else:
                st.error("Please enter your email address.")

def show_registration_form():
    """Display registration form"""
    st.markdown("#### Register New Account")
    
    with st.form("registration_form"):
        role = st.selectbox("Account Type", ["Student", "Professor"])
        
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", help="Password must be at least 6 characters long")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Password validation warning
        if password and len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters long")
        
        if role == "Student":
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            student_id = st.text_input("Student ID")
            major = st.text_input("Major")
            year_level = st.selectbox("Year Level", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
        else:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            professor_id = st.text_input("Professor ID")
            department = st.text_input("Department")
            title = st.text_input("Title (e.g., Professor, Assistant Professor)")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_button = st.form_submit_button("📝 Register", type="primary")
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel")
        
        if register_button:
            if email and password and confirm_password:
                if len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                elif password == confirm_password:
                    register_user(role, email, password, locals())
                else:
                    st.error("❌ Passwords do not match.")
            else:
                st.error("❌ Please fill in all required fields.")
        
        if cancel_button:
            st.session_state.show_registration = False
            st.rerun()

def show_main_application():
    """Display main application after authentication"""
    # Header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_name = f"{st.session_state.user_info.get('first_name', '')} {st.session_state.user_info.get('last_name', '')}"
        st.markdown(f"### Welcome, {user_name}!")
        st.markdown(f"**Role:** {st.session_state.user_role.title()}")
    
    with col2:
        if st.button("🔑 Change Password"):
            st.session_state.show_change_password = True
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout"):
            logout_user()
    
    # Role-based navigation
    if st.session_state.user_role == "student":
        show_student_navigation()
    elif st.session_state.user_role == "professor":
        show_professor_navigation()
    else:
        st.error("Unknown user role. Please contact administrator.")

def show_student_navigation():
    """Show navigation options for students"""
    st.sidebar.title("Student Portal")
    
    # Initialize current_page if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Course Browser", "My Courses", "Grades", "Academic Records", "Analytics"],
        index=["Dashboard", "Course Browser", "My Courses", "Grades", "Academic Records", "Analytics"].index(st.session_state.current_page)
    )
    
    # Update current page
    st.session_state.current_page = page
    
    if page == "Dashboard":
        show_student_dashboard()
    elif page == "Course Browser":
        show_course_browser()
    elif page == "My Courses":
        show_my_courses()
    elif page == "Grades":
        show_grades()
    elif page == "Academic Records":
        show_academic_records()
    elif page == "Analytics":
        show_student_analytics()

def show_professor_navigation():
    """Show navigation options for professors"""
    st.sidebar.title("👨‍🏫 Professor Portal")
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "My Courses", "Course Management", "Student Roster", "Grade Entry", "Announcements", "Analytics"]
    )
    
    if page == "Dashboard":
        show_professor_dashboard()
    elif page == "My Courses":
        show_professor_courses()
    elif page == "Course Management":
        show_course_management()
    elif page == "Student Roster":
        show_student_roster()
    elif page == "Grade Entry":
        show_grade_entry()
    elif page == "Announcements":
        show_announcements()
    elif page == "Analytics":
        show_professor_analytics()

# Authentication Functions
def login_user(email: str, password: str):
    """Authenticate user with backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Store authentication data
            st.session_state.authenticated = True
            st.session_state.access_token = data["access_token"]
            st.session_state.user_role = data["user_role"]
            st.session_state.user_id = data["user_id"]
            
            # Get user profile
            get_user_profile()
            
            st.success("✅ Login successful!")
            st.rerun()
            
        elif response.status_code == 401:
            st.error("❌ Invalid email or password.")
        else:
            st.error(f"❌ Login failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def get_user_profile():
    """Get current user profile information"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            profile_data = response.json()
            st.session_state.user_info = profile_data
            return profile_data
        else:
            st.warning("Could not fetch user profile.")
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch user profile: {str(e)}")
        return None

def change_password(current_password: str, new_password: str):
    """Change user password"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Backend expects query parameters, not form data
        params = {
            "current_password": current_password,
            "new_password": new_password
        }
        
        if st.session_state.user_role == "student":
            response = requests.post(
                f"{API_BASE_URL}/students/change-password",
                headers=headers,
                params=params,  # Use params for query parameters
                timeout=10
            )
        else:
            # Professor password change endpoint
            response = requests.post(
                f"{API_BASE_URL}/professors/change-password",
                headers=headers,
                params=params,  # Use params for query parameters
                timeout=10
            )
        
        if response.status_code == 200:
            st.success("✅ Password changed successfully!")
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Password change failed: {response.status_code} - {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def forgot_password(email: str):
    """Handle forgot password request"""
    # Note: This would need backend implementation for email sending
    st.info("📧 Password reset functionality requires email service setup in the backend.")
    st.info("For now, please contact your administrator to reset your password.")

def register_user(role: str, email: str, password: str, form_data: dict):
    """Register new user"""
    try:
        if role == "Student":
            registration_data = {
                "email": email,
                "password": password,
                "student_id": form_data.get("student_id", ""),
                "first_name": form_data.get("first_name", ""),
                "last_name": form_data.get("last_name", ""),
                "major": form_data.get("major", ""),
                "year_level": form_data.get("year_level", "")
            }
            endpoint = f"{API_BASE_URL}/auth/register/student"
        else:
            registration_data = {
                "email": email,
                "password": password,
                "professor_id": form_data.get("professor_id", ""),
                "first_name": form_data.get("first_name", ""),
                "last_name": form_data.get("last_name", ""),
                "department": form_data.get("department", ""),
                "title": form_data.get("title", "")
            }
            endpoint = f"{API_BASE_URL}/auth/register/professor"
        
        response = requests.post(endpoint, json=registration_data, timeout=10)
        
        if response.status_code == 200:
            st.success("✅ Registration successful! Please login with your credentials.")
            st.session_state.show_registration = False
            st.rerun()
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Registration failed: {response.status_code} - {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def logout_user():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.access_token = None
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.rerun()

# Student Features Implementation
def show_student_dashboard():
    """Student dashboard with personal info, schedule overview, and quick actions"""
    st.header("📊 Student Dashboard")
    
    # Get student profile and academic data
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Get user profile
        profile_response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=10)
        if profile_response.status_code == 200:
            user_profile = profile_response.json()
        else:
            st.error("Could not fetch user profile")
            return
        
        # Get academic dashboard data
        dashboard_response = requests.get(f"{API_BASE_URL}/academic-records/dashboard", headers=headers, timeout=10)
        dashboard_data = dashboard_response.json() if dashboard_response.status_code == 200 else None
        
        # Get enrolled courses (schedule)
        courses_response = requests.get(f"{API_BASE_URL}/students/schedule", headers=headers, timeout=10)
        enrolled_courses = courses_response.json() if courses_response.status_code == 200 else []
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return
    
    # Personal Information Section
    st.subheader("👤 Personal Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}")
        st.metric("Student ID", user_profile.get('student_id', 'N/A'))
    
    with col2:
        st.metric("Major", user_profile.get('major', 'N/A'))
        st.metric("Year Level", user_profile.get('year_level', 'N/A'))
    
    with col3:
        if dashboard_data:
            st.metric("Cumulative GPA", f"{dashboard_data.get('overview', {}).get('cumulative_gpa', 'N/A')}")
            st.metric("Credits Earned", dashboard_data.get('overview', {}).get('total_credits_earned', 'N/A'))
        else:
            st.metric("Cumulative GPA", "N/A")
            st.metric("Credits Earned", "N/A")
    
    st.divider()
    
    # Quick Actions Section
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Browse Courses", use_container_width=True):
            st.session_state.current_page = "Course Browser"
            st.rerun()
    
    with col2:
        if st.button("📚 My Courses", use_container_width=True):
            st.session_state.current_page = "My Courses"
            st.rerun()
    
    with col3:
        if st.button("📊 View Grades", use_container_width=True):
            st.session_state.current_page = "Grades"
            st.rerun()
    
    with col4:
        if st.button("📋 Academic Records", use_container_width=True):
            st.session_state.current_page = "Academic Records"
            st.rerun()
    
    st.divider()
    
    # Recent Schedule Overview
    st.subheader("📅 Recent Schedule Overview")
    
    if enrolled_courses and isinstance(enrolled_courses, list) and len(enrolled_courses) > 0:
        # Create a DataFrame for better display
        courses_data = []
        for course in enrolled_courses[:5]:  # Show only recent 5 courses
            if isinstance(course, dict):
                courses_data.append({
                    "Course Code": course.get('course_code', 'N/A'),
                    "Title": course.get('title', 'N/A'),
                    "Credits": course.get('credits', 'N/A'),
                    "Professor": f"{course.get('professor', {}).get('first_name', '')} {course.get('professor', {}).get('last_name', '')}" if course.get('professor') else 'N/A',
                    "Semester": f"{course.get('semester', 'N/A')} {course.get('year', 'N/A')}"
                })
        
        if courses_data:
            df = pd.DataFrame(courses_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No enrolled courses found.")
    else:
        st.info("No enrolled courses found. Browse courses to enroll!")
    
    # Academic Progress Section
    if dashboard_data and dashboard_data.get('overview'):
        st.divider()
        st.subheader("📈 Academic Progress")
        
        overview = dashboard_data['overview']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Semester GPA", f"{overview.get('current_semester_gpa', 'N/A')}")
        
        with col2:
            st.metric("Major GPA", f"{overview.get('major_gpa', 'N/A')}")
        
        with col3:
            status = "✅ On Track" if overview.get('is_on_track', False) else "⚠️ Needs Attention"
            st.metric("Academic Status", status)
        
        # Grade Distribution Chart
        if dashboard_data.get('grade_distribution'):
            st.subheader("📊 Grade Distribution")
            grade_dist = dashboard_data['grade_distribution']
            
            # Create a simple bar chart
            grades = list(grade_dist.keys())
            counts = list(grade_dist.values())
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(grades, counts)
            ax.set_xlabel('Grade')
            ax.set_ylabel('Count')
            ax.set_title('Grade Distribution')
            
            st.pyplot(fig)
    
    # Recent Grades Section
    if dashboard_data and dashboard_data.get('recent_grades'):
        st.divider()
        st.subheader("📊 Recent Grades")
        
        recent_grades = dashboard_data['recent_grades'][:5]  # Show only recent 5 grades
        
        grades_data = []
        for grade in recent_grades:
            grades_data.append({
                "Course": grade.get('course_code', 'N/A'),
                "Title": grade.get('course_title', 'N/A'),
                "Grade": grade.get('letter_grade', 'N/A'),
                "Points": grade.get('points_earned', 'N/A'),
                "Semester": f"{grade.get('semester', 'N/A')} {grade.get('year', 'N/A')}"
            })
        
        if grades_data:
            df_grades = pd.DataFrame(grades_data)
            st.dataframe(df_grades, use_container_width=True)

def show_course_browser():
    """Course browser with filtering and section list functionality"""
    st.header("🔍 Course Browser")
    
    # Get available departments and semesters for filters
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Get departments
        dept_response = requests.get(f"{API_BASE_URL}/courses/departments/list", headers=headers, timeout=10)
        departments = dept_response.json() if dept_response.status_code == 200 else []
        
        # Ensure departments is a list of strings
        if isinstance(departments, list):
            department_list = [str(dept) for dept in departments if dept]
        else:
            department_list = []
        
        # Get semesters
        sem_response = requests.get(f"{API_BASE_URL}/courses/semesters/list", headers=headers, timeout=10)
        semesters = sem_response.json() if sem_response.status_code == 200 else []
        
        # Ensure semesters is a list of strings
        if isinstance(semesters, list):
            semester_list = [str(sem) for sem in semesters if sem]
        else:
            semester_list = []
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return
    
    # Filter Section
    st.subheader("🔍 Search & Filter Courses")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        keyword = st.text_input("Search Keyword", placeholder="Course title, code, or description")
    
    with col2:
        department = st.selectbox("Department", ["All"] + department_list)
        department = None if department == "All" else department
    
    with col3:
        semester = st.selectbox("Semester", ["All"] + semester_list)
        semester = None if semester == "All" else semester
    
    with col4:
        year = st.number_input("Year", min_value=2020, max_value=2030, value=2024)
    
    # Search button
    if st.button("🔍 Search Courses", type="primary"):
        search_courses(keyword, department, semester, year)
    
    st.divider()
    
    # Display search results
    if 'search_results' in st.session_state and st.session_state.search_results:
        st.subheader("📚 Available Courses")
        
        courses = st.session_state.search_results
        
        # Ensure courses is a list
        if not isinstance(courses, list):
            courses = []
        
        for course in courses:
            if isinstance(course, dict):
                with st.expander(f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {course.get('description', 'No description available')}")
                        st.write(f"**Credits:** {course.get('credits', 'N/A')}")
                        st.write(f"**Professor:** {course.get('professor', {}).get('first_name', '')} {course.get('professor', {}).get('last_name', '')}")
                        st.write(f"**Department:** {course.get('department', 'N/A')}")
                        st.write(f"**Semester:** {course.get('semester', 'N/A')} {course.get('year', 'N/A')}")
                        st.write(f"**Schedule:** {course.get('schedule', 'N/A')}")
                        
                        if course.get('prerequisites'):
                            st.write(f"**Prerequisites:** {course.get('prerequisites', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Enrolled:** {course.get('enrolled_count', 0)}/{course.get('max_enrollment', 'N/A')}")
                        
                        # Enrollment button
                        if course.get('enrolled_count', 0) < course.get('max_enrollment', 0):
                            if st.button(f"📝 Enroll", key=f"enroll_{course.get('id')}"):
                                enroll_in_course(course.get('id'))
                        else:
                            st.warning("Course is full")
                        
                        # View details button
                        if st.button(f"👁️ View Details", key=f"details_{course.get('id')}"):
                            view_course_details(course.get('id'))
    
    elif 'search_results' in st.session_state:
        st.info("No courses found matching your criteria. Try adjusting your filters.")
    else:
        st.info("Use the search filters above to find courses.")

def search_courses(keyword=None, department=None, semester=None, year=None):
    """Search for courses with filters"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        params = {}
        if keyword:
            params['keyword'] = keyword
        if department:
            params['department'] = department
        if semester:
            params['semester'] = semester
        if year:
            params['year'] = year
        
        # Use general courses endpoint
        response = requests.get(f"{API_BASE_URL}/courses/", headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list):
                st.session_state.search_results = results
                st.success(f"Found {len(results)} courses")
            else:
                st.session_state.search_results = []
                st.warning("Unexpected response format from server")
        else:
            st.error(f"Search failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def enroll_in_course(course_id):
    """Enroll student in a course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.post(
            f"{API_BASE_URL}/students/courses/enroll",
            headers=headers,
            json={"course_id": course_id},
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Successfully enrolled in course!")
            # Refresh search results to update enrollment counts
            if 'search_results' in st.session_state:
                for course in st.session_state.search_results:
                    if course.get('id') == course_id:
                        course['enrolled_count'] = course.get('enrolled_count', 0) + 1
                        break
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Enrollment failed: {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def view_course_details(course_id):
    """View detailed course information"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.get(f"{API_BASE_URL}/courses/{course_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            course = response.json()
            
            st.subheader(f"📚 {course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Course Code:** {course.get('course_code', 'N/A')}")
                st.write(f"**Title:** {course.get('title', 'N/A')}")
                st.write(f"**Credits:** {course.get('credits', 'N/A')}")
                st.write(f"**Department:** {course.get('department', 'N/A')}")
                st.write(f"**Semester:** {course.get('semester', 'N/A')} {course.get('year', 'N/A')}")
                st.write(f"**Max Enrollment:** {course.get('max_enrollment', 'N/A')}")
            
            with col2:
                st.write(f"**Professor:** {course.get('professor', {}).get('first_name', '')} {course.get('professor', {}).get('last_name', '')}")
                st.write(f"**Office:** {course.get('professor', {}).get('office_location', 'N/A')}")
                st.write(f"**Office Hours:** {course.get('professor', {}).get('office_hours', 'N/A')}")
                st.write(f"**Schedule:** {course.get('schedule', 'N/A')}")
            
            if course.get('description'):
                st.write(f"**Description:** {course.get('description')}")
            
            if course.get('prerequisites'):
                st.write(f"**Prerequisites:** {course.get('prerequisites')}")
            
            if course.get('syllabus'):
                st.write(f"**Syllabus:** {course.get('syllabus')}")
            
            # Enrollment information
            enrollment_response = requests.get(f"{API_BASE_URL}/courses/{course_id}/enrollment", headers=headers, timeout=10)
            if enrollment_response.status_code == 200:
                enrollment_data = enrollment_response.json()
                st.write(f"**Current Enrollment:** {enrollment_data.get('enrolled_count', 0)}/{enrollment_data.get('max_enrollment', 'N/A')}")
                st.write(f"**Available Spots:** {enrollment_data.get('available_spots', 0)}")
            
        else:
            st.error(f"Could not fetch course details: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_my_courses():
    """My courses with enrollment/withdrawal functionality"""
    st.header("📚 My Courses")
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Get enrolled courses
        response = requests.get(f"{API_BASE_URL}/students/schedule", headers=headers, timeout=10)
        
        if response.status_code == 200:
            enrolled_courses = response.json()
            
            if enrolled_courses and isinstance(enrolled_courses, list) and len(enrolled_courses) > 0:
                st.subheader(f"📋 Enrolled Courses ({len(enrolled_courses)})")
                
                # Create a DataFrame for better display
                courses_data = []
                for course in enrolled_courses:
                    if isinstance(course, dict):
                        courses_data.append({
                            "Course Code": course.get('course_code', 'N/A'),
                            "Title": course.get('title', 'N/A'),
                            "Credits": course.get('credits', 'N/A'),
                            "Professor": f"{course.get('professor', {}).get('first_name', '')} {course.get('professor', {}).get('last_name', '')}" if course.get('professor') else 'N/A',
                            "Semester": f"{course.get('semester', 'N/A')} {course.get('year', 'N/A')}",
                            "Schedule": course.get('schedule', 'N/A'),
                            "Status": course.get('status', 'enrolled')
                        })
                
                df = pd.DataFrame(courses_data)
                st.dataframe(df, use_container_width=True)
                
                st.divider()
                
                # Course management section
                st.subheader("📝 Course Management")
                
                # Course selection for withdrawal
                course_options = {}
                for course in enrolled_courses:
                    if isinstance(course, dict):
                        course_key = f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}"
                        course_options[course_key] = course.get('id')
                
                if course_options:
                    selected_course = st.selectbox("Select a course to manage:", list(course_options.keys()))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📤 Withdraw from Course", type="secondary"):
                            course_id = course_options[selected_course]
                            withdraw_from_course(course_id, selected_course)
                    
                    with col2:
                        if st.button("👁️ View Course Details", type="primary"):
                            course_id = course_options[selected_course]
                            view_enrolled_course_details(course_id)
                
                # Quick stats
                st.divider()
                st.subheader("📊 Quick Stats")
                
                col1, col2, col3 = st.columns(3)
                
                total_credits = sum([course.get('credits', 0) for course in enrolled_courses if isinstance(course, dict)])
                
                with col1:
                    st.metric("Total Credits", total_credits)
                
                with col2:
                    st.metric("Courses Enrolled", len(enrolled_courses))
                
                with col3:
                    # Calculate average credits per course
                    avg_credits = total_credits / len(enrolled_courses) if enrolled_courses else 0
                    st.metric("Avg Credits/Course", f"{avg_credits:.1f}")
                
            else:
                st.info("📚 You are not enrolled in any courses yet.")
                st.info("💡 Use the 'Course Browser' to find and enroll in courses!")
                
                # Quick action to browse courses
                if st.button("🔍 Browse Courses", type="primary"):
                    st.session_state.current_page = "Course Browser"
                    st.rerun()
        
        else:
            st.error(f"Could not fetch enrolled courses: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def withdraw_from_course(course_id, course_name):
    """Withdraw student from a course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.post(
            f"{API_BASE_URL}/students/courses/withdraw",
            headers=headers,
            json={"course_id": course_id},
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(f"✅ Successfully withdrew from {course_name}")
            st.rerun()  # Refresh the page to show updated course list
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Withdrawal failed: {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def view_enrolled_course_details(course_id):
    """View detailed information for an enrolled course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.get(f"{API_BASE_URL}/courses/{course_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            course = response.json()
            
            st.subheader(f"📚 {course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Course Code:** {course.get('course_code', 'N/A')}")
                st.write(f"**Title:** {course.get('title', 'N/A')}")
                st.write(f"**Credits:** {course.get('credits', 'N/A')}")
                st.write(f"**Department:** {course.get('department', 'N/A')}")
                st.write(f"**Semester:** {course.get('semester', 'N/A')} {course.get('year', 'N/A')}")
                st.write(f"**Max Enrollment:** {course.get('max_enrollment', 'N/A')}")
            
            with col2:
                st.write(f"**Professor:** {course.get('professor', {}).get('first_name', '')} {course.get('professor', {}).get('last_name', '')}")
                st.write(f"**Office:** {course.get('professor', {}).get('office_location', 'N/A')}")
                st.write(f"**Office Hours:** {course.get('professor', {}).get('office_hours', 'N/A')}")
                st.write(f"**Schedule:** {course.get('schedule', 'N/A')}")
            
            if course.get('description'):
                st.write(f"**Description:** {course.get('description')}")
            
            if course.get('prerequisites'):
                st.write(f"**Prerequisites:** {course.get('prerequisites')}")
            
            if course.get('syllabus'):
                st.write(f"**Syllabus:** {course.get('syllabus')}")
            
            # Get current grades for this course
            st.subheader("📊 Current Grades")
            try:
                grades_response = requests.get(f"{API_BASE_URL}/academic-records/grades", headers=headers, params={"course_id": course_id}, timeout=10)
                if grades_response.status_code == 200:
                    grades = grades_response.json()
                    if grades:
                        grades_data = []
                        for grade in grades:
                            grades_data.append({
                                "Assignment": grade.get('assignment_name', 'N/A'),
                                "Type": grade.get('assignment_type', 'N/A'),
                                "Points Earned": grade.get('points_earned', 'N/A'),
                                "Max Points": grade.get('max_points', 'N/A'),
                                "Grade": grade.get('letter_grade', 'N/A'),
                                "Date": grade.get('graded_date', 'N/A')
                            })
                        
                        if grades_data:
                            df_grades = pd.DataFrame(grades_data)
                            st.dataframe(df_grades, use_container_width=True)
                        else:
                            st.info("No grades available yet.")
                    else:
                        st.info("No grades available yet.")
                else:
                    st.info("Could not fetch grades for this course.")
            except:
                st.info("Could not fetch grades for this course.")
            
        else:
            st.error(f"Could not fetch course details: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_grades():
    """Grades page with table view of final grades per section"""
    st.header("📊 Grades")
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Filter options
        st.subheader("🔍 Filter Grades")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            semester = st.selectbox("Semester", ["All", "Fall 2024", "Spring 2024", "Summer 2024", "Fall 2023", "Spring 2023"])
            semester = None if semester == "All" else semester
        
        with col2:
            year = st.number_input("Year", min_value=2020, max_value=2030, value=2024)
        
        with col3:
            status = st.selectbox("Grade Status", ["All", "Graded", "Pending", "Incomplete"])
            status = None if status == "All" else status.lower()
        
        # Get grades
        params = {}
        if semester:
            params['semester'] = semester
        if year:
            params['year'] = year
        if status:
            params['status'] = status
        
        response = requests.get(f"{API_BASE_URL}/academic-records/grades", headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            grades = response.json()
            
            if grades:
                st.subheader(f"📋 Grade Report ({len(grades)} records)")
                
                # Create a comprehensive grades table
                grades_data = []
                for grade in grades:
                    grades_data.append({
                        "Course Code": grade.get('course_code', 'N/A'),
                        "Course Title": grade.get('course_title', 'N/A'),
                        "Semester": f"{grade.get('semester', 'N/A')} {grade.get('year', 'N/A')}",
                        "Credits": grade.get('credits', 'N/A'),
                        "Final Grade": grade.get('letter_grade', 'N/A'),
                        "Points Earned": grade.get('points_earned', 'N/A'),
                        "Max Points": grade.get('max_points', 'N/A'),
                        "Percentage": f"{grade.get('percentage', 0):.1f}%" if grade.get('percentage') else 'N/A',
                        "Status": grade.get('status', 'N/A'),
                        "Graded Date": grade.get('graded_date', 'N/A')
                    })
                
                df = pd.DataFrame(grades_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                st.divider()
                st.subheader("📊 Grade Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                # Calculate statistics
                total_courses = len(grades)
                graded_courses = len([g for g in grades if g.get('status') == 'graded'])
                total_credits = sum([g.get('credits', 0) for g in grades])
                
                # Calculate GPA
                gpa_response = requests.get(f"{API_BASE_URL}/academic-records/gpa", headers=headers, timeout=10)
                gpa_data = gpa_response.json() if gpa_response.status_code == 200 else {}
                
                with col1:
                    st.metric("Total Courses", total_courses)
                
                with col2:
                    st.metric("Graded Courses", graded_courses)
                
                with col3:
                    st.metric("Total Credits", total_credits)
                
                with col4:
                    cumulative_gpa = gpa_data.get('cumulative_gpa', 'N/A')
                    st.metric("Cumulative GPA", cumulative_gpa)
                
                # Grade distribution
                if graded_courses > 0:
                    st.subheader("📈 Grade Distribution")
                    
                    grade_counts = {}
                    for grade in grades:
                        if grade.get('status') == 'graded' and grade.get('letter_grade'):
                            letter_grade = grade.get('letter_grade')
                            grade_counts[letter_grade] = grade_counts.get(letter_grade, 0) + 1
                    
                    if grade_counts:
                        # Create a simple bar chart
                        grades_list = list(grade_counts.keys())
                        counts_list = list(grade_counts.values())
                        
                        fig, ax = plt.subplots(figsize=(10, 4))
                        ax.bar(grades_list, counts_list)
                        ax.set_xlabel('Grade')
                        ax.set_ylabel('Count')
                        ax.set_title('Grade Distribution')
                        
                        st.pyplot(fig)
                
                # Semester breakdown
                if gpa_data.get('semester_breakdown'):
                    st.subheader("📅 Semester GPA Breakdown")
                    
                    semester_data = []
                    for semester_info in gpa_data['semester_breakdown']:
                        semester_data.append({
                            "Semester": f"{semester_info.get('semester', 'N/A')} {semester_info.get('year', 'N/A')}",
                            "GPA": semester_info.get('gpa', 'N/A'),
                            "Credits": semester_info.get('credits', 'N/A'),
                            "Courses": semester_info.get('courses', 'N/A')
                        })
                    
                    if semester_data:
                        df_semester = pd.DataFrame(semester_data)
                        st.dataframe(df_semester, use_container_width=True)
                
                # Export options
                st.divider()
                st.subheader("📤 Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Generate Transcript", type="primary"):
                        generate_transcript()
                
                with col2:
                    # CSV download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv,
                        file_name=f"grades_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            else:
                st.info("📚 No grades found for the selected criteria.")
                st.info("💡 Grades will appear here once your professors submit them.")
        
        else:
            st.error(f"Could not fetch grades: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def generate_transcript_with_options(transcript_type, include_incomplete, include_withdrawn):
    """Generate transcript with user-specified options"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Create transcript generation request with user options
        transcript_request = {
            "transcript_type": transcript_type,
            "include_incomplete": include_incomplete,
            "include_withdrawn": include_withdrawn
        }
        
        response = requests.post(
            f"{API_BASE_URL}/academic-records/transcripts/generate", 
            headers=headers, 
            json=transcript_request,
            timeout=30
        )
        
        if response.status_code == 200:
            transcript_data = response.json()
            st.success("✅ Transcript generated successfully!")
            
            # Display transcript information
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"📄 **Transcript ID:** {transcript_data.get('transcript_id', 'N/A')}")
                st.info(f"📄 **Status:** {transcript_data.get('status', 'N/A')}")
                st.info(f"📄 **Type:** {transcript_type.title()}")
            
            with col2:
                if transcript_data.get('download_url'):
                    st.info(f"📄 **Download URL:** {transcript_data['download_url']}")
                
                if transcript_data.get('file_path'):
                    st.info(f"📄 **File Path:** {transcript_data['file_path']}")
                
                if transcript_data.get('generated_at'):
                    st.info(f"📄 **Generated:** {transcript_data['generated_at']}")
            
            # Show options used
            st.write("**Options Used:**")
            st.write(f"- Include Incomplete: {'Yes' if include_incomplete else 'No'}")
            st.write(f"- Include Withdrawn: {'Yes' if include_withdrawn else 'No'}")
            
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Transcript generation failed: {response.status_code} - {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def generate_transcript():
    """Generate and download transcript"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Create transcript generation request with proper parameters
        transcript_request = {
            "transcript_type": "official",
            "include_incomplete": False,
            "include_withdrawn": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/academic-records/transcripts/generate", 
            headers=headers, 
            json=transcript_request,
            timeout=30
        )
        
        if response.status_code == 200:
            transcript_data = response.json()
            st.success("✅ Transcript generated successfully!")
            
            # Display transcript information
            st.info(f"📄 Transcript ID: {transcript_data.get('transcript_id', 'N/A')}")
            st.info(f"📄 Status: {transcript_data.get('status', 'N/A')}")
            
            if transcript_data.get('download_url'):
                st.info(f"📄 Download URL: {transcript_data['download_url']}")
            
            if transcript_data.get('file_path'):
                st.info(f"📄 File Path: {transcript_data['file_path']}")
            
        else:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Unknown error")
            except:
                pass
            st.error(f"❌ Transcript generation failed: {response.status_code} - {error_detail}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")

def show_academic_records():
    """Academic records with comprehensive academic information"""
    st.header("📋 Academic Records")
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Get comprehensive academic summary
        response = requests.get(f"{API_BASE_URL}/academic-records/academic-summary", headers=headers, timeout=10)
        
        if response.status_code == 200:
            academic_data = response.json()
            
            # Student Information
            st.subheader("👤 Student Information")
            
            student_info = academic_data.get('student_info', {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Student ID", student_info.get('student_id', 'N/A'))
                st.metric("Name", student_info.get('name', 'N/A'))
            
            with col2:
                st.metric("Major", student_info.get('major', 'N/A'))
                st.metric("Year Level", student_info.get('year_level', 'N/A'))
            
            with col3:
                st.metric("Status", "Active")
            
            st.divider()
            
            # GPA Summary
            st.subheader("📊 GPA Summary")
            
            gpa_summary = academic_data.get('gpa_summary', {})
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Cumulative GPA", f"{gpa_summary.get('cumulative_gpa', 'N/A')}")
            
            with col2:
                st.metric("Major GPA", f"{gpa_summary.get('major_gpa', 'N/A')}")
            
            with col3:
                st.metric("Current Semester GPA", f"{gpa_summary.get('current_semester_gpa', 'N/A')}")
            
            with col4:
                st.metric("Total Credits Earned", gpa_summary.get('total_credits_earned', 'N/A'))
            
            st.divider()
            
            # Academic Progress
            progress_summary = academic_data.get('progress_summary')
            if progress_summary:
                st.subheader("📈 Academic Progress")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Credits Completed", progress_summary.get('credits_completed', 'N/A'))
                
                with col2:
                    st.metric("Credits Required", progress_summary.get('credits_required', 'N/A'))
                
                with col3:
                    completion_percentage = progress_summary.get('completion_percentage', 0)
                    st.metric("Completion %", f"{completion_percentage:.1f}%")
                
                # Progress bar
                progress_bar = completion_percentage / 100 if completion_percentage else 0
                st.progress(progress_bar)
                
                # Academic status
                is_on_track = progress_summary.get('is_on_track', False)
                status_color = "green" if is_on_track else "orange"
                status_text = "✅ On Track" if is_on_track else "⚠️ Needs Attention"
                st.markdown(f"**Academic Status:** :{status_color}[{status_text}]")
            
            st.divider()
            
            # Grade Statistics
            grade_stats = academic_data.get('grade_statistics', {})
            if grade_stats:
                st.subheader("📊 Grade Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Courses", grade_stats.get('total_courses', 'N/A'))
                
                with col2:
                    st.metric("Courses Completed", grade_stats.get('courses_completed', 'N/A'))
                
                with col3:
                    st.metric("Courses Incomplete", grade_stats.get('courses_incomplete', 'N/A'))
                
                with col4:
                    st.metric("Courses Withdrawn", grade_stats.get('courses_withdrawn', 'N/A'))
                
                # Grade distribution
                grade_distribution = grade_stats.get('grade_distribution', {})
                if grade_distribution:
                    st.subheader("📈 Grade Distribution")
                    
                    # Create a pie chart
                    grades = list(grade_distribution.keys())
                    counts = list(grade_distribution.values())
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.pie(counts, labels=grades, autopct='%1.1f%%', startangle=90)
                    ax.set_title('Grade Distribution')
                    
                    st.pyplot(fig)
            
            st.divider()
            
            # Semester Breakdown
            semester_breakdown = academic_data.get('semester_breakdown', [])
            if semester_breakdown:
                st.subheader("📅 Semester Breakdown")
                
                semester_data = []
                for semester in semester_breakdown:
                    semester_data.append({
                        "Semester": f"{semester.get('semester', 'N/A')} {semester.get('year', 'N/A')}",
                        "GPA": semester.get('gpa', 'N/A'),
                        "Credits": semester.get('credits', 'N/A'),
                        "Courses": semester.get('courses', 'N/A'),
                        "Status": semester.get('status', 'N/A')
                    })
                
                if semester_data:
                    df_semester = pd.DataFrame(semester_data)
                    st.dataframe(df_semester, use_container_width=True)
            
            # Export and Actions
            st.divider()
            st.subheader("📤 Export & Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Transcript generation with options
                st.subheader("📄 Transcript Generation")
                
                with st.expander("Generate Official Transcript", expanded=False):
                    st.write("**Transcript Options:**")
                    
                    transcript_type = st.selectbox(
                        "Transcript Type",
                        ["official", "unofficial"],
                        help="Official transcripts are certified and can be used for official purposes"
                    )
                    
                    include_incomplete = st.checkbox(
                        "Include Incomplete Courses",
                        value=False,
                        help="Include courses with incomplete grades"
                    )
                    
                    include_withdrawn = st.checkbox(
                        "Include Withdrawn Courses",
                        value=False,
                        help="Include courses that were withdrawn"
                    )
                    
                    if st.button("📄 Generate Transcript", type="primary"):
                        generate_transcript_with_options(transcript_type, include_incomplete, include_withdrawn)
            
            with col2:
                if st.button("📊 Download Academic Summary", type="secondary"):
                    # Create CSV of academic summary
                    summary_data = {
                        "Student ID": student_info.get('student_id', 'N/A'),
                        "Name": student_info.get('name', 'N/A'),
                        "Major": student_info.get('major', 'N/A'),
                        "Cumulative GPA": gpa_summary.get('cumulative_gpa', 'N/A'),
                        "Major GPA": gpa_summary.get('major_gpa', 'N/A'),
                        "Total Credits": gpa_summary.get('total_credits_earned', 'N/A')
                    }
                    
                    csv_data = pd.DataFrame([summary_data]).to_csv(index=False)
                    st.download_button(
                        label="📊 Download Summary",
                        data=csv_data,
                        file_name=f"academic_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🔄 Refresh Data", type="secondary"):
                    st.rerun()
        
        else:
            st.error(f"Could not fetch academic records: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_professor_dashboard():
    """Professor dashboard with teaching load and course overview"""
    st.header("📊 Professor Dashboard")
    
    # Fetch professor profile
    user_profile = get_user_profile()
    if not user_profile:
        st.error("Could not load professor profile")
        return
    
    # Fetch teaching load
    teaching_load = fetch_teaching_load()
    
    # Display professor info
    st.subheader("👨‍🏫 Professor Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", f"{user_profile.get('first_name', 'N/A')} {user_profile.get('last_name', 'N/A')}")
        st.metric("Department", user_profile.get('department', 'N/A'))
    
    with col2:
        st.metric("Title", user_profile.get('title', 'N/A'))
        st.metric("Email", user_profile.get('email', 'N/A'))
    
    with col3:
        if teaching_load:
            st.metric("Total Courses", teaching_load.get('total_courses', 0))
            st.metric("Total Credits", teaching_load.get('total_credits', 0))
        else:
            st.metric("Total Courses", "N/A")
            st.metric("Total Credits", "N/A")
    
    st.divider()
    
    # Teaching Load Overview
    if teaching_load:
        st.subheader("📚 Teaching Load Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Courses", teaching_load.get('total_courses', 0))
        
        with col2:
            st.metric("Total Students", teaching_load.get('total_students', 0))
        
        with col3:
            st.metric("Total Credits", teaching_load.get('total_credits', 0))
        
        with col4:
            st.metric("Department", teaching_load.get('department', 'N/A'))
        
        # Course List
        courses = teaching_load.get('courses', [])
        if courses:
            st.subheader("📋 Current Courses")
            
            courses_data = []
            for course in courses:
                courses_data.append({
                    "Course Code": course.get('course_code', 'N/A'),
                    "Title": course.get('title', 'N/A'),
                    "Credits": course.get('credits', 'N/A'),
                    "Enrolled": f"{course.get('enrolled_count', 0)}/{course.get('max_enrollment', 'N/A')}",
                    "Schedule": course.get('schedule', 'N/A'),
                    "Semester": f"{course.get('semester', 'N/A')} {course.get('year', 'N/A')}"
                })
            
            if courses_data:
                st.dataframe(courses_data, use_container_width=True)
        else:
            st.info("No courses found for current semester")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📚 Manage Courses", type="primary"):
            st.session_state.current_page = "Course Management"
            st.rerun()
    
    with col2:
        if st.button("👥 View Rosters", type="secondary"):
            st.session_state.current_page = "Roster Management"
            st.rerun()
    
    with col3:
        if st.button("📝 Enter Grades", type="secondary"):
            st.session_state.current_page = "Grade Entry"
            st.rerun()
    
    with col4:
        if st.button("📢 Announcements", type="secondary"):
            st.session_state.current_page = "Announcements"
            st.rerun()

def fetch_teaching_load():
    """Fetch professor's teaching load"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/professors/profile/teaching-load",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch teaching load.")
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch teaching load: {str(e)}")
        return None

def show_professor_courses():
    """Professor courses management page"""
    st.header("📚 My Courses")
    
    # Fetch professor courses
    courses = fetch_professor_courses()
    
    if not courses:
        st.info("No courses found. Create your first course!")
        if st.button("➕ Create New Course", type="primary"):
            st.session_state.current_page = "Course Management"
            st.rerun()
        return
    
    # Course filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        semester_filter = st.selectbox(
            "Filter by Semester",
            ["All"] + list(set([course.get('semester', 'N/A') for course in courses if course.get('semester')])),
            key="prof_course_semester_filter"
        )
    
    with col2:
        year_filter = st.selectbox(
            "Filter by Year",
            ["All"] + list(set([str(course.get('year', 'N/A')) for course in courses if course.get('year')])),
            key="prof_course_year_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive"],
            key="prof_course_status_filter"
        )
    
    # Filter courses
    filtered_courses = courses
    if semester_filter != "All":
        filtered_courses = [c for c in filtered_courses if c.get('semester') == semester_filter]
    if year_filter != "All":
        filtered_courses = [c for c in filtered_courses if str(c.get('year')) == year_filter]
    if status_filter == "Active":
        filtered_courses = [c for c in filtered_courses if c.get('is_active', False)]
    elif status_filter == "Inactive":
        filtered_courses = [c for c in filtered_courses if not c.get('is_active', True)]
    
    st.divider()
    
    # Display courses
    if filtered_courses:
        st.subheader(f"📋 Courses ({len(filtered_courses)} found)")
        
        for course in filtered_courses:
            with st.expander(f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {course.get('description', 'No description')}")
                    st.write(f"**Credits:** {course.get('credits', 'N/A')}")
                    st.write(f"**Department:** {course.get('department', 'N/A')}")
                    st.write(f"**Semester:** {course.get('semester', 'N/A')} {course.get('year', 'N/A')}")
                    st.write(f"**Schedule:** {course.get('schedule', 'N/A')}")
                    st.write(f"**Enrollment:** {course.get('enrolled_count', 0)}/{course.get('max_enrollment', 'N/A')}")
                    st.write(f"**Status:** {'🟢 Active' if course.get('is_active') else '🔴 Inactive'}")
                
                with col2:
                    if st.button(f"👥 View Roster", key=f"roster_{course.get('id')}"):
                        st.session_state.selected_course_id = course.get('id')
                        st.session_state.current_page = "Roster Management"
                        st.rerun()
                    
                    if st.button(f"📝 Enter Grades", key=f"grades_{course.get('id')}"):
                        st.session_state.selected_course_id = course.get('id')
                        st.session_state.current_page = "Grade Entry"
                        st.rerun()
                    
                    if st.button(f"📊 Stats", key=f"stats_{course.get('id')}"):
                        show_course_enrollment_stats(course.get('id'))
                    
                    if st.button(f"✏️ Edit", key=f"edit_{course.get('id')}"):
                        st.session_state.selected_course_id = course.get('id')
                        st.session_state.current_page = "Course Management"
                        st.rerun()
    else:
        st.info("No courses match the selected filters.")
    
    # Add course button
    st.divider()
    if st.button("➕ Create New Course", type="primary"):
        st.session_state.current_page = "Course Management"
        st.rerun()

def fetch_professor_courses():
    """Fetch professor's courses"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/professors/courses",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch courses.")
            return []
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch courses: {str(e)}")
        return []

def show_course_enrollment_stats(course_id):
    """Show enrollment statistics for a course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/professors/courses/{course_id}/enrollment-stats",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            stats = response.json()
            
            st.subheader("📊 Enrollment Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Enrolled", stats.get('total_enrolled', 0))
            
            with col2:
                st.metric("Max Enrollment", stats.get('max_enrollment', 0))
            
            with col3:
                st.metric("Available Spots", stats.get('available_spots', 0))
            
            with col4:
                st.metric("Enrollment %", f"{stats.get('enrollment_percentage', 0):.1f}%")
            
            # Year level distribution
            year_dist = stats.get('year_level_distribution', {})
            if year_dist:
                st.subheader("📈 Year Level Distribution")
                year_data = []
                for year_level, count in year_dist.items():
                    year_data.append({
                        "Year Level": year_level,
                        "Count": count
                    })
                
                if year_data:
                    st.dataframe(year_data, use_container_width=True)
                    
                    # Create a simple bar chart
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.bar(year_dist.keys(), year_dist.values())
                    ax.set_xlabel("Year Level")
                    ax.set_ylabel("Number of Students")
                    ax.set_title("Student Distribution by Year Level")
                    st.pyplot(fig)
        else:
            st.error(f"Could not fetch enrollment stats: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_student_roster():
    """Student roster management page"""
    st.header("👥 Student Roster Management")
    
    # Course selection
    courses = fetch_professor_courses()
    if not courses:
        st.info("No courses found. Create a course first!")
        return
    
    # Course selector
    course_options = {f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}": course.get('id') for course in courses}
    
    if 'selected_course_id' in st.session_state and st.session_state.selected_course_id:
        selected_course_id = st.session_state.selected_course_id
        # Find the course name for display
        selected_course_name = None
        for course in courses:
            if course.get('id') == selected_course_id:
                selected_course_name = f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}"
                break
    else:
        selected_course_name = st.selectbox("Select Course", list(course_options.keys()))
        selected_course_id = course_options[selected_course_name]
    
    if not selected_course_id:
        st.warning("Please select a course to view the roster.")
        return
    
    # Fetch course students
    course_students = fetch_course_students(selected_course_id)
    
    if not course_students:
        st.info("No students enrolled in this course.")
        return
    
    # Display course info
    st.subheader(f"📚 {selected_course_name}")
    
    # Course statistics
    enrolled_count = course_students.get('enrolled_count', 0)
    max_enrollment = course_students.get('max_enrollment', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Enrolled Students", enrolled_count)
    
    with col2:
        st.metric("Max Enrollment", max_enrollment)
    
    with col3:
        st.metric("Available Spots", max(0, max_enrollment - enrolled_count))
    
    with col4:
        enrollment_percentage = (enrolled_count / max_enrollment * 100) if max_enrollment > 0 else 0
        st.metric("Enrollment %", f"{enrollment_percentage:.1f}%")
    
    st.divider()
    
    # Student roster
    students = course_students.get('enrolled_students', [])
    if students:
        st.subheader(f"👥 Enrolled Students ({len(students)})")
        
        # Student data table
        students_data = []
        for student in students:
            students_data.append({
                "Student ID": student.get('student_id', 'N/A'),
                "Name": f"{student.get('first_name', 'N/A')} {student.get('last_name', 'N/A')}",
                "Email": student.get('email', 'N/A'),
                "Major": student.get('major', 'N/A'),
                "Year Level": student.get('year_level', 'N/A'),
                "GPA": student.get('gpa', 'N/A'),
                "Status": student.get('status', 'N/A')
            })
        
        if students_data:
            st.dataframe(students_data, use_container_width=True)
            
            # Student actions
            st.subheader("🔧 Student Actions")
            
            # Remove student functionality
            with st.expander("Remove Student from Course"):
                student_options = {f"{s.get('first_name', 'N/A')} {s.get('last_name', 'N/A')} ({s.get('student_id', 'N/A')})": s.get('id') for s in students}
                
                if student_options:
                    selected_student_name = st.selectbox("Select Student to Remove", list(student_options.keys()))
                    selected_student_id = student_options[selected_student_name]
                    
                    if st.button("🗑️ Remove Student", type="secondary"):
                        if remove_student_from_course(selected_course_id, selected_student_id):
                            st.success("Student removed successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to remove student.")
                else:
                    st.info("No students to remove.")
            
            # Export roster
            if st.button("📥 Export Roster"):
                export_roster_data(students_data, selected_course_name)
    else:
        st.info("No students enrolled in this course.")

def fetch_course_students(course_id):
    """Fetch students enrolled in a specific course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/professors/courses/{course_id}/students",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch course students.")
            return {}
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch course students: {str(e)}")
        return {}

def remove_student_from_course(course_id, student_id):
    """Remove a student from a course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.delete(
            f"{API_BASE_URL}/professors/courses/{course_id}/students/{student_id}",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def export_roster_data(students_data, course_name):
    """Export roster data as CSV"""
    import pandas as pd
    import io
    
    df = pd.DataFrame(students_data)
    
    # Create CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    # Download button
    st.download_button(
        label="📥 Download Roster CSV",
        data=csv_data,
        file_name=f"{course_name.replace(' - ', '_')}_roster.csv",
        mime="text/csv"
    )

def show_grade_entry():
    """Grade entry management page"""
    st.header("📝 Grade Entry Management")
    
    # Course selection
    courses = fetch_professor_courses()
    if not courses:
        st.info("No courses found. Create a course first!")
        return
    
    # Course selector
    course_options = {f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}": course.get('id') for course in courses}
    
    if 'selected_course_id' in st.session_state and st.session_state.selected_course_id:
        selected_course_id = st.session_state.selected_course_id
        # Find the course name for display
        selected_course_name = None
        for course in courses:
            if course.get('id') == selected_course_id:
                selected_course_name = f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}"
                break
    else:
        selected_course_name = st.selectbox("Select Course", list(course_options.keys()))
        selected_course_id = course_options[selected_course_name]
    
    if not selected_course_id:
        st.warning("Please select a course to manage grades.")
        return
    
    # Fetch course students
    course_students = fetch_course_students(selected_course_id)
    
    if not course_students or not course_students.get('enrolled_students'):
        st.info("No students enrolled in this course.")
        return
    
    # Display course info
    st.subheader(f"📚 {selected_course_name}")
    
    # Grade entry tabs
    tab1, tab2, tab3 = st.tabs(["📝 Enter Grades", "📊 View Grades", "📈 Grade Statistics"])
    
    with tab1:
        show_grade_entry_form(selected_course_id, course_students.get('enrolled_students', []))
    
    with tab2:
        show_course_grades(selected_course_id)
    
    with tab3:
        show_grade_statistics(selected_course_id)

def show_grade_entry_form(course_id, students):
    """Show grade entry form for students"""
    st.subheader("📝 Enter Grades")
    
    # Assignment/Exam selection
    col1, col2 = st.columns(2)
    
    with col1:
        grade_type = st.selectbox("Grade Type", ["Assignment", "Exam", "Final Grade"])
    
    with col2:
        if grade_type in ["Assignment", "Exam"]:
            item_name = st.text_input("Assignment/Exam Name", placeholder="e.g., Midterm Exam, Homework 1")
        else:
            item_name = "Final Grade"
    
    st.divider()
    
    # Grade entry for each student
    st.subheader("👥 Student Grades")
    
    grades_data = []
    
    for student in students:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{student.get('first_name', 'N/A')} {student.get('last_name', 'N/A')}** ({student.get('student_id', 'N/A')})")
        
        with col2:
            if grade_type == "Final Grade":
                grade = st.selectbox(
                    "Grade",
                    ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F", "W", "I"],
                    key=f"grade_{student.get('id')}"
                )
            else:
                grade = st.number_input(
                    "Score",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.1,
                    key=f"score_{student.get('id')}"
                )
        
        with col3:
            if grade_type == "Final Grade":
                st.write("Final Grade")
            else:
                max_points = st.number_input(
                    "Max Points",
                    min_value=1.0,
                    max_value=1000.0,
                    value=100.0,
                    step=1.0,
                    key=f"max_{student.get('id')}"
                )
        
        grades_data.append({
            "student_id": student.get('id'),
            "student_name": f"{student.get('first_name', 'N/A')} {student.get('last_name', 'N/A')}",
            "grade": grade,
            "max_points": max_points if grade_type != "Final Grade" else None
        })
    
    st.divider()
    
    # Submit grades
    if st.button("💾 Submit Grades", type="primary"):
        if submit_grades(course_id, grade_type, item_name, grades_data):
            st.success("Grades submitted successfully!")
        else:
            st.error("Failed to submit grades.")

def show_course_grades(course_id):
    """Show existing grades for a course"""
    st.subheader("📊 Course Grades")
    
    # Fetch grades
    grades = fetch_course_grades(course_id)
    
    if not grades:
        st.info("No grades entered for this course yet.")
        return
    
    # Display grades in a table
    grades_data = []
    for grade in grades:
        grades_data.append({
            "Student ID": grade.get('student_id', 'N/A'),
            "Student Name": grade.get('student_name', 'N/A'),
            "Assignment/Exam": grade.get('assignment_name', 'N/A'),
            "Score": grade.get('score', 'N/A'),
            "Max Points": grade.get('max_points', 'N/A'),
            "Grade": grade.get('letter_grade', 'N/A'),
            "Status": grade.get('status', 'N/A'),
            "Date": grade.get('created_at', 'N/A')
        })
    
    if grades_data:
        st.dataframe(grades_data, use_container_width=True)
        
        # Grade summary
        st.subheader("📈 Grade Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Grades", len(grades))
        
        with col2:
            avg_score = sum([g.get('score', 0) for g in grades if g.get('score')]) / len([g for g in grades if g.get('score')]) if grades else 0
            st.metric("Average Score", f"{avg_score:.1f}")
        
        with col3:
            passing_grades = len([g for g in grades if g.get('letter_grade') in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']])
            st.metric("Passing Grades", passing_grades)
        
        with col4:
            failing_grades = len([g for g in grades if g.get('letter_grade') in ['F', 'W', 'I']])
            st.metric("Failing Grades", failing_grades)

def show_grade_statistics(course_id):
    """Show grade statistics and distribution"""
    st.subheader("📈 Grade Statistics")
    
    # Fetch grades
    grades = fetch_course_grades(course_id)
    
    if not grades:
        st.info("No grades available for statistics.")
        return
    
    # Grade distribution
    grade_counts = {}
    for grade in grades:
        letter_grade = grade.get('letter_grade', 'N/A')
        grade_counts[letter_grade] = grade_counts.get(letter_grade, 0) + 1
    
    if grade_counts:
        st.subheader("📊 Grade Distribution")
        
        # Create pie chart
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart
        ax1.pie(grade_counts.values(), labels=grade_counts.keys(), autopct='%1.1f%%')
        ax1.set_title("Grade Distribution")
        
        # Bar chart
        ax2.bar(grade_counts.keys(), grade_counts.values())
        ax2.set_xlabel("Grade")
        ax2.set_ylabel("Count")
        ax2.set_title("Grade Count")
        
        st.pyplot(fig)
        
        # Grade distribution table
        st.subheader("📋 Grade Distribution Table")
        distribution_data = []
        for grade, count in grade_counts.items():
            percentage = (count / len(grades)) * 100
            distribution_data.append({
                "Grade": grade,
                "Count": count,
                "Percentage": f"{percentage:.1f}%"
            })
        
        st.dataframe(distribution_data, use_container_width=True)

def fetch_course_grades(course_id):
    """Fetch grades for a specific course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/grading-assessments/grades",
            headers=headers,
            params={"course_id": course_id},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch course grades.")
            return []
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch course grades: {str(e)}")
        return []

def submit_grades(course_id, grade_type, item_name, grades_data):
    """Submit grades for students"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Prepare grade data
        grade_entries = []
        for grade_info in grades_data:
            if grade_type == "Final Grade":
                grade_entry = {
                    "student_id": grade_info["student_id"],
                    "course_id": course_id,
                    "assignment_name": item_name,
                    "letter_grade": grade_info["grade"],
                    "grade_type": "final"
                }
            else:
                grade_entry = {
                    "student_id": grade_info["student_id"],
                    "course_id": course_id,
                    "assignment_name": item_name,
                    "score": grade_info["grade"],
                    "max_points": grade_info["max_points"],
                    "grade_type": grade_type.lower()
                }
            grade_entries.append(grade_entry)
        
        # Submit grades
        response = requests.post(
            f"{API_BASE_URL}/grading-assessments/grades/bulk",
            headers=headers,
            json={"grades": grade_entries},
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def show_course_management():
    """Course management page for creating and editing courses"""
    st.header("📚 Course Management")
    
    # Check if editing existing course
    if 'selected_course_id' in st.session_state and st.session_state.selected_course_id:
        edit_course_id = st.session_state.selected_course_id
        st.subheader("✏️ Edit Course")
        
        # Fetch course details
        course_details = fetch_course_details(edit_course_id)
        if course_details:
            show_course_edit_form(course_details)
        else:
            st.error("Could not fetch course details.")
            # Clear the selected course
            del st.session_state.selected_course_id
    else:
        st.subheader("➕ Create New Course")
        show_course_create_form()

def show_course_create_form():
    """Show form to create a new course"""
    with st.form("create_course_form"):
        st.write("**Course Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            course_code = st.text_input("Course Code", placeholder="e.g., CS101")
            title = st.text_input("Course Title", placeholder="e.g., Introduction to Computer Science")
            credits = st.number_input("Credits", min_value=1, max_value=6, value=3)
            department = st.text_input("Department", placeholder="e.g., Computer Science")
        
        with col2:
            semester = st.selectbox("Semester", ["Fall", "Spring", "Summer"])
            year = st.number_input("Year", min_value=2020, max_value=2030, value=2024)
            max_enrollment = st.number_input("Max Enrollment", min_value=1, max_value=500, value=30)
            schedule = st.text_input("Schedule", placeholder="e.g., MWF 10:00-10:50")
        
        description = st.text_area("Description", placeholder="Course description...")
        prerequisites = st.text_input("Prerequisites", placeholder="e.g., MATH101, CS100")
        syllabus = st.text_area("Syllabus", placeholder="Course syllabus...")
        
        submitted = st.form_submit_button("💾 Create Course", type="primary")
        
        if submitted:
            if create_course(course_code, title, description, credits, department, semester, year, max_enrollment, prerequisites, schedule, syllabus):
                st.success("Course created successfully!")
                st.rerun()
            else:
                st.error("Failed to create course.")

def show_course_edit_form(course_details):
    """Show form to edit an existing course"""
    with st.form("edit_course_form"):
        st.write("**Edit Course Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            course_code = st.text_input("Course Code", value=course_details.get('course_code', ''))
            title = st.text_input("Course Title", value=course_details.get('title', ''))
            credits = st.number_input("Credits", min_value=1, max_value=6, value=course_details.get('credits', 3))
            department = st.text_input("Department", value=course_details.get('department', ''))
        
        with col2:
            semester = st.selectbox("Semester", ["Fall", "Spring", "Summer"], index=["Fall", "Spring", "Summer"].index(course_details.get('semester', 'Fall')))
            year = st.number_input("Year", min_value=2020, max_value=2030, value=course_details.get('year', 2024))
            max_enrollment = st.number_input("Max Enrollment", min_value=1, max_value=500, value=course_details.get('max_enrollment', 30))
            schedule = st.text_input("Schedule", value=course_details.get('schedule', ''))
        
        description = st.text_area("Description", value=course_details.get('description', ''))
        prerequisites = st.text_input("Prerequisites", value=course_details.get('prerequisites', ''))
        syllabus = st.text_area("Syllabus", value=course_details.get('syllabus', ''))
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Update Course", type="primary")
        
        with col2:
            if st.form_submit_button("🗑️ Deactivate Course", type="secondary"):
                if deactivate_course(course_details.get('id')):
                    st.success("Course deactivated successfully!")
                    del st.session_state.selected_course_id
                    st.rerun()
                else:
                    st.error("Failed to deactivate course.")
        
        if submitted:
            if update_course(course_details.get('id'), course_code, title, description, credits, department, semester, year, max_enrollment, prerequisites, schedule, syllabus):
                st.success("Course updated successfully!")
                del st.session_state.selected_course_id
                st.rerun()
            else:
                st.error("Failed to update course.")

def fetch_course_details(course_id):
    """Fetch details of a specific course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/professors/courses/{course_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch course details.")
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch course details: {str(e)}")
        return None

def create_course(course_code, title, description, credits, department, semester, year, max_enrollment, prerequisites, schedule, syllabus):
    """Create a new course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        course_data = {
            "course_code": course_code,
            "title": title,
            "description": description,
            "credits": credits,
            "department": department,
            "semester": semester,
            "year": year,
            "max_enrollment": max_enrollment,
            "prerequisites": prerequisites,
            "schedule": schedule,
            "syllabus": syllabus
        }
        
        response = requests.post(
            f"{API_BASE_URL}/professors/courses",
            headers=headers,
            json=course_data,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def update_course(course_id, course_code, title, description, credits, department, semester, year, max_enrollment, prerequisites, schedule, syllabus):
    """Update an existing course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        course_data = {
            "course_code": course_code,
            "title": title,
            "description": description,
            "credits": credits,
            "department": department,
            "semester": semester,
            "year": year,
            "max_enrollment": max_enrollment,
            "prerequisites": prerequisites,
            "schedule": schedule,
            "syllabus": syllabus
        }
        
        response = requests.put(
            f"{API_BASE_URL}/professors/courses/{course_id}",
            headers=headers,
            json=course_data,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def deactivate_course(course_id):
    """Deactivate a course"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.delete(
            f"{API_BASE_URL}/professors/courses/{course_id}",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def show_announcements():
    """Announcement management system for teachers"""
    st.header("📢 Announcement Management")
    
    # Course selection
    courses = fetch_professor_courses()
    if not courses:
        st.info("No courses found. Create a course first!")
        return
    
    # Announcement tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Announcement", "📋 View Announcements", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        show_create_announcement_form(courses)
    
    with tab2:
        show_announcement_list(courses)
    
    with tab3:
        show_announcement_analytics()
    
    with tab4:
        show_announcement_settings()

def show_create_announcement_form(courses):
    """Show form to create new announcements"""
    st.subheader("📝 Create New Announcement")
    
    with st.form("create_announcement_form"):
        # Course selection
        course_options = {f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}": course.get('id') for course in courses}
        course_options["All Courses (Broadcast)"] = None
        
        selected_course_name = st.selectbox("Select Course", list(course_options.keys()))
        selected_course_id = course_options[selected_course_name]
        
        # Announcement details
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.text_input("Subject", placeholder="Enter announcement subject")
            message_type = st.selectbox("Message Type", ["announcement", "reminder", "assignment", "grade", "general", "urgent"])
        
        with col2:
            priority = st.selectbox("Priority", ["low", "normal", "high", "urgent"])
            scheduled_at = st.date_input("Schedule Date (Optional)", value=None)
            scheduled_time = st.time_input("Schedule Time (Optional)", value=None)
        
        # Content
        content = st.text_area("Content", placeholder="Enter announcement content...", height=200)
        
        # Recipients
        st.subheader("👥 Recipients")
        
        if selected_course_id:
            # Get course students
            course_students = fetch_course_students(selected_course_id)
            students = course_students.get('enrolled_students', [])
            
            if students:
                recipient_options = {}
                for student in students:
                    recipient_options[f"{student.get('first_name', 'N/A')} {student.get('last_name', 'N/A')} ({student.get('student_id', 'N/A')})"] = student.get('id')
                
                selected_recipients = st.multiselect(
                    "Select Recipients",
                    list(recipient_options.keys()),
                    default=list(recipient_options.keys())  # Select all by default
                )
                
                recipient_ids = [recipient_options[name] for name in selected_recipients]
            else:
                st.info("No students enrolled in this course.")
                recipient_ids = []
        else:
            # Broadcast to all students
            st.info("This will be sent to all students as a broadcast message.")
            recipient_ids = []
        
        # Submit button
        submitted = st.form_submit_button("📤 Create Announcement", type="primary")
        
        if submitted:
            if not subject or not content:
                st.error("Please fill in all required fields.")
            elif selected_course_id and not recipient_ids:
                st.error("Please select at least one recipient.")
            else:
                # Combine date and time for scheduling
                scheduled_datetime = None
                if scheduled_at and scheduled_time:
                    scheduled_datetime = datetime.combine(scheduled_at, scheduled_time)
                
                if create_announcement(selected_course_id, subject, content, message_type, priority, recipient_ids, scheduled_datetime):
                    st.success("✅ Announcement created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create announcement.")

def show_announcement_list(courses):
    """Show list of existing announcements"""
    st.subheader("📋 Announcement History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        course_filter = st.selectbox(
            "Filter by Course",
            ["All"] + [f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}" for course in courses],
            key="announcement_course_filter"
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All", "announcement", "reminder", "assignment", "grade", "general", "urgent"],
            key="announcement_type_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "draft", "sent", "delivered", "read", "archived"],
            key="announcement_status_filter"
        )
    
    # Fetch announcements
    announcements = fetch_announcements()
    
    if not announcements:
        st.info("No announcements found.")
        return
    
    # Filter announcements
    filtered_announcements = announcements
    if course_filter != "All":
        course_id = None
        for course in courses:
            if f"{course.get('course_code', 'N/A')} - {course.get('title', 'N/A')}" == course_filter:
                course_id = course.get('id')
                break
        if course_id:
            filtered_announcements = [a for a in filtered_announcements if a.get('course_id') == course_id]
    
    if type_filter != "All":
        filtered_announcements = [a for a in filtered_announcements if a.get('message_type') == type_filter]
    
    if status_filter != "All":
        filtered_announcements = [a for a in filtered_announcements if a.get('status') == status_filter]
    
    # Display announcements
    if filtered_announcements:
        st.subheader(f"📋 Announcements ({len(filtered_announcements)} found)")
        
        for announcement in filtered_announcements:
            with st.expander(f"📢 {announcement.get('subject', 'N/A')} - {announcement.get('status', 'N/A').title()}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Subject:** {announcement.get('subject', 'N/A')}")
                    st.write(f"**Content:** {announcement.get('content', 'N/A')}")
                    st.write(f"**Type:** {announcement.get('message_type', 'N/A').title()}")
                    st.write(f"**Priority:** {announcement.get('priority', 'N/A').title()}")
                    st.write(f"**Status:** {announcement.get('status', 'N/A').title()}")
                    st.write(f"**Created:** {announcement.get('created_at', 'N/A')}")
                    if announcement.get('sent_at'):
                        st.write(f"**Sent:** {announcement.get('sent_at', 'N/A')}")
                
                with col2:
                    if announcement.get('status') == 'draft':
                        if st.button(f"📤 Send", key=f"send_{announcement.get('id')}"):
                            if send_announcement(announcement.get('id')):
                                st.success("Announcement sent!")
                                st.rerun()
                            else:
                                st.error("Failed to send announcement.")
                    
                    if st.button(f"✏️ Edit", key=f"edit_{announcement.get('id')}"):
                        st.session_state.editing_announcement_id = announcement.get('id')
                        st.rerun()
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{announcement.get('id')}"):
                        if delete_announcement(announcement.get('id')):
                            st.success("Announcement deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete announcement.")
                    
                    if st.button(f"👥 Recipients", key=f"recipients_{announcement.get('id')}"):
                        show_announcement_recipients(announcement.get('id'))
    else:
        st.info("No announcements match the selected filters.")

def show_announcement_analytics():
    """Show announcement analytics and statistics"""
    st.subheader("📊 Announcement Analytics")
    
    # Fetch announcement report
    report = fetch_announcement_report()
    
    if not report:
        st.info("No analytics data available.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Announcements", report.get('total_messages', 0))
    
    with col2:
        st.metric("Sent Messages", report.get('sent_messages', 0))
    
    with col3:
        st.metric("Delivered Messages", report.get('delivered_messages', 0))
    
    with col4:
        st.metric("Read Messages", report.get('read_messages', 0))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Message Types Distribution")
        type_counts = report.get('message_type_distribution', {})
        if type_counts:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
            ax.set_title("Message Types Distribution")
            st.pyplot(fig)
    
    with col2:
        st.subheader("📊 Priority Distribution")
        priority_counts = report.get('priority_distribution', {})
        if priority_counts:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(priority_counts.keys(), priority_counts.values())
            ax.set_xlabel("Priority")
            ax.set_ylabel("Count")
            ax.set_title("Priority Distribution")
            st.pyplot(fig)

def show_announcement_settings():
    """Show announcement settings and preferences"""
    st.subheader("⚙️ Announcement Settings")
    
    st.info("Announcement settings and preferences will be implemented here.")
    
    # Placeholder for future settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Default Settings**")
        default_type = st.selectbox("Default Message Type", ["announcement", "reminder", "assignment", "grade", "general"])
        default_priority = st.selectbox("Default Priority", ["low", "normal", "high", "urgent"])
    
    with col2:
        st.write("**Notification Settings**")
        email_notifications = st.checkbox("Email Notifications", value=True)
        sms_notifications = st.checkbox("SMS Notifications", value=False)
        auto_archive = st.checkbox("Auto-archive after 30 days", value=True)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")

def fetch_announcements():
    """Fetch announcements/messages"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/student-information/messages",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch announcements.")
            return []
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch announcements: {str(e)}")
        return []

def create_announcement(course_id, subject, content, message_type, priority, recipient_ids, scheduled_at):
    """Create a new announcement"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        announcement_data = {
            "course_id": course_id,
            "subject": subject,
            "content": content,
            "message_type": message_type,
            "priority": priority,
            "recipient_ids": recipient_ids,
            "scheduled_at": scheduled_at.isoformat() if scheduled_at else None
        }
        
        response = requests.post(
            f"{API_BASE_URL}/student-information/messages",
            headers=headers,
            json=announcement_data,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def send_announcement(message_id):
    """Send an announcement"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.post(
            f"{API_BASE_URL}/student-information/messages/{message_id}/send",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def delete_announcement(message_id):
    """Delete an announcement"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        response = requests.delete(
            f"{API_BASE_URL}/student-information/messages/{message_id}",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def fetch_announcement_report():
    """Fetch announcement analytics report"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/student-information/messages/report",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Could not fetch announcement report.")
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch announcement report: {str(e)}")
        return None

def show_announcement_recipients(message_id):
    """Show announcement recipients"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(
            f"{API_BASE_URL}/student-information/messages/{message_id}/recipients",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            recipients = response.json()
            
            st.subheader("👥 Message Recipients")
            
            if recipients:
                recipient_data = []
                for recipient in recipients:
                    recipient_data.append({
                        "Student ID": recipient.get('student_id', 'N/A'),
                        "Name": f"{recipient.get('first_name', 'N/A')} {recipient.get('last_name', 'N/A')}",
                        "Email": recipient.get('email', 'N/A'),
                        "Status": recipient.get('status', 'N/A'),
                        "Read At": recipient.get('read_at', 'N/A')
                    })
                
                st.dataframe(recipient_data, use_container_width=True)
            else:
                st.info("No recipients found.")
        else:
            st.error("Could not fetch recipients.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

def show_student_analytics():
    """Advanced analytics dashboard for students"""
    st.header("📊 Student Analytics Dashboard")
    
    # Fetch comprehensive analytics data
    analytics_data = fetch_student_analytics()
    
    if not analytics_data:
        st.info("No analytics data available.")
        return
    
    # Key Performance Indicators
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current GPA",
            f"{analytics_data.get('current_gpa', 0):.2f}",
            delta=f"{analytics_data.get('gpa_change', 0):+.2f}",
            help="GPA change from last semester"
        )
    
    with col2:
        st.metric(
            "Credits Completed",
            analytics_data.get('credits_completed', 0),
            delta=f"{analytics_data.get('credits_this_semester', 0)} this semester",
            help="Total credits completed"
        )
    
    with col3:
        st.metric(
            "Courses Enrolled",
            analytics_data.get('courses_enrolled', 0),
            delta=f"{analytics_data.get('courses_completed', 0)} completed",
            help="Current semester enrollment"
        )
    
    with col4:
        st.metric(
            "Academic Standing",
            analytics_data.get('academic_standing', 'N/A'),
            delta=analytics_data.get('standing_change', ''),
            help="Current academic standing"
        )
    
    # Performance Trends
    st.subheader("📈 Performance Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 GPA Trend Over Time")
        gpa_trend = analytics_data.get('gpa_trend', [])
        if gpa_trend:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            semesters = [point.get('semester', 'N/A') for point in gpa_trend]
            gpas = [point.get('gpa', 0) for point in gpa_trend]
            
            ax.plot(semesters, gpas, marker='o', linewidth=2, markersize=8)
            ax.set_xlabel('Semester')
            ax.set_ylabel('GPA')
            ax.set_title('GPA Trend Over Time')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 4.0)
            
            # Add trend line
            import numpy as np
            if len(gpas) > 1:
                z = np.polyfit(range(len(gpas)), gpas, 1)
                p = np.poly1d(z)
                ax.plot(semesters, p(range(len(gpas))), "r--", alpha=0.8, label='Trend')
                ax.legend()
            
            st.pyplot(fig)
        else:
            st.info("No GPA trend data available.")
    
    with col2:
        st.subheader("📚 Course Performance Distribution")
        course_performance = analytics_data.get('course_performance', {})
        if course_performance:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            grades = list(course_performance.keys())
            counts = list(course_performance.values())
            
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
            ax.pie(counts, labels=grades, autopct='%1.1f%%', colors=colors[:len(grades)])
            ax.set_title('Grade Distribution')
            
            st.pyplot(fig)
        else:
            st.info("No course performance data available.")
    
    # Detailed Analytics
    st.subheader("🔍 Detailed Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Academic Progress", "📚 Course Analysis", "⏰ Time Management", "🎯 Goals & Targets"])
    
    with tab1:
        show_academic_progress_analytics(analytics_data)
    
    with tab2:
        show_course_analysis_analytics(analytics_data)
    
    with tab3:
        show_time_management_analytics(analytics_data)
    
    with tab4:
        show_goals_targets_analytics(analytics_data)

def show_professor_analytics():
    """Advanced analytics dashboard for professors"""
    st.header("📊 Professor Analytics Dashboard")
    
    # Fetch comprehensive analytics data
    analytics_data = fetch_professor_analytics()
    
    if not analytics_data:
        st.info("No analytics data available.")
        return
    
    # Key Performance Indicators
    st.subheader("🎯 Teaching Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Students",
            analytics_data.get('total_students', 0),
            delta=f"{analytics_data.get('new_students', 0)} new",
            help="Students across all courses"
        )
    
    with col2:
        st.metric(
            "Active Courses",
            analytics_data.get('active_courses', 0),
            delta=f"{analytics_data.get('courses_this_semester', 0)} this semester",
            help="Currently teaching courses"
        )
    
    with col3:
        st.metric(
            "Average Grade",
            f"{analytics_data.get('average_grade', 0):.1f}",
            delta=f"{analytics_data.get('grade_change', 0):+.1f}",
            help="Average grade across all courses"
        )
    
    with col4:
        st.metric(
            "Student Satisfaction",
            f"{analytics_data.get('satisfaction_score', 0):.1f}/5.0",
            delta=f"{analytics_data.get('satisfaction_change', 0):+.1f}",
            help="Student satisfaction rating"
        )
    
    # Teaching Analytics
    st.subheader("📈 Teaching Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Grade Distribution")
        grade_distribution = analytics_data.get('grade_distribution', {})
        if grade_distribution:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            grades = list(grade_distribution.keys())
            counts = list(grade_distribution.values())
            
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
            ax.bar(grades, counts, color=colors[:len(grades)])
            ax.set_xlabel('Grade')
            ax.set_ylabel('Number of Students')
            ax.set_title('Grade Distribution Across All Courses')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        else:
            st.info("No grade distribution data available.")
    
    with col2:
        st.subheader("📚 Course Performance Comparison")
        course_performance = analytics_data.get('course_performance', [])
        if course_performance:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            courses = [course.get('course_code', 'N/A') for course in course_performance]
            avg_grades = [course.get('average_grade', 0) for course in course_performance]
            
            ax.barh(courses, avg_grades, color='#45b7d1')
            ax.set_xlabel('Average Grade')
            ax.set_ylabel('Course')
            ax.set_title('Course Performance Comparison')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        else:
            st.info("No course performance data available.")
    
    # Detailed Analytics
    st.subheader("🔍 Detailed Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Student Engagement", "📊 Assessment Analysis", "📈 Teaching Trends", "🎯 Performance Insights"])
    
    with tab1:
        show_student_engagement_analytics(analytics_data)
    
    with tab2:
        show_assessment_analysis_analytics(analytics_data)
    
    with tab3:
        show_teaching_trends_analytics(analytics_data)
    
    with tab4:
        show_performance_insights_analytics(analytics_data)

def show_academic_progress_analytics(analytics_data):
    """Show academic progress analytics"""
    st.subheader("📊 Academic Progress Analysis")
    
    progress_data = analytics_data.get('academic_progress', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Progress Towards Degree**")
        credits_required = progress_data.get('credits_required', 120)
        credits_completed = progress_data.get('credits_completed', 0)
        progress_percentage = (credits_completed / credits_required) * 100 if credits_required > 0 else 0
        
        st.progress(progress_percentage / 100)
        st.write(f"**{credits_completed}/{credits_required} credits** ({progress_percentage:.1f}%)")
        
        # Estimated graduation
        if progress_percentage > 0:
            remaining_credits = credits_required - credits_completed
            avg_credits_per_semester = progress_data.get('avg_credits_per_semester', 15)
            semesters_remaining = remaining_credits / avg_credits_per_semester if avg_credits_per_semester > 0 else 0
            st.write(f"**Estimated graduation:** {semesters_remaining:.1f} semesters")
    
    with col2:
        st.write("**Major Requirements Progress**")
        major_requirements = progress_data.get('major_requirements', [])
        
        if major_requirements:
            requirement_data = []
            for req in major_requirements:
                requirement_data.append({
                    "Requirement": req.get('name', 'N/A'),
                    "Completed": f"{req.get('completed', 0)}/{req.get('required', 0)}",
                    "Progress": f"{(req.get('completed', 0) / req.get('required', 1)) * 100:.1f}%"
                })
            
            st.dataframe(requirement_data, use_container_width=True)
        else:
            st.info("No major requirements data available.")

def show_course_analysis_analytics(analytics_data):
    """Show course analysis analytics"""
    st.subheader("📚 Course Analysis")
    
    course_analysis = analytics_data.get('course_analysis', [])
    
    if course_analysis:
        # Course performance table
        course_data = []
        for course in course_analysis:
            course_data.append({
                "Course Code": course.get('course_code', 'N/A'),
                "Course Name": course.get('title', 'N/A'),
                "Grade": course.get('grade', 'N/A'),
                "Credits": course.get('credits', 0),
                "Semester": course.get('semester', 'N/A'),
                "Status": course.get('status', 'N/A')
            })
        
        st.dataframe(course_data, use_container_width=True)
        
        # Performance insights
        st.subheader("💡 Performance Insights")
        
        insights = analytics_data.get('performance_insights', [])
        for insight in insights:
            st.info(f"💡 {insight}")
    else:
        st.info("No course analysis data available.")

def show_time_management_analytics(analytics_data):
    """Show time management analytics"""
    st.subheader("⏰ Time Management Analysis")
    
    time_data = analytics_data.get('time_management', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Study Time Distribution**")
        study_time = time_data.get('study_time_distribution', {})
        if study_time:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            
            subjects = list(study_time.keys())
            hours = list(study_time.values())
            
            ax.pie(hours, labels=subjects, autopct='%1.1f%%')
            ax.set_title('Study Time Distribution')
            
            st.pyplot(fig)
        else:
            st.info("No study time data available.")
    
    with col2:
        st.write("**Weekly Schedule Analysis**")
        weekly_data = time_data.get('weekly_schedule', {})
        if weekly_data:
            schedule_data = []
            for day, activities in weekly_data.items():
                schedule_data.append({
                    "Day": day,
                    "Classes": activities.get('classes', 0),
                    "Study Hours": activities.get('study_hours', 0),
                    "Free Time": activities.get('free_time', 0)
                })
            
            st.dataframe(schedule_data, use_container_width=True)
        else:
            st.info("No weekly schedule data available.")

def show_goals_targets_analytics(analytics_data):
    """Show goals and targets analytics"""
    st.subheader("🎯 Goals & Targets")
    
    goals_data = analytics_data.get('goals_targets', {})
    
    # Current goals
    st.write("**Current Goals**")
    current_goals = goals_data.get('current_goals', [])
    
    if current_goals:
        for goal in current_goals:
            with st.expander(f"🎯 {goal.get('title', 'N/A')}"):
                st.write(f"**Description:** {goal.get('description', 'N/A')}")
                st.write(f"**Target Date:** {goal.get('target_date', 'N/A')}")
                st.write(f"**Progress:** {goal.get('progress', 0)}%")
                st.progress(goal.get('progress', 0) / 100)
    else:
        st.info("No current goals set.")
    
    # Achievements
    st.write("**Recent Achievements**")
    achievements = goals_data.get('achievements', [])
    
    if achievements:
        achievement_data = []
        for achievement in achievements:
            achievement_data.append({
                "Achievement": achievement.get('title', 'N/A'),
                "Date": achievement.get('date', 'N/A'),
                "Description": achievement.get('description', 'N/A')
            })
        
        st.dataframe(achievement_data, use_container_width=True)
    else:
        st.info("No achievements recorded.")

def show_student_engagement_analytics(analytics_data):
    """Show student engagement analytics"""
    st.subheader("👥 Student Engagement Analysis")
    
    engagement_data = analytics_data.get('student_engagement', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Attendance Rates**")
        attendance_rates = engagement_data.get('attendance_rates', {})
        if attendance_rates:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            
            courses = list(attendance_rates.keys())
            rates = list(attendance_rates.values())
            
            ax.bar(courses, rates, color='#4ecdc4')
            ax.set_xlabel('Course')
            ax.set_ylabel('Attendance Rate (%)')
            ax.set_title('Attendance Rates by Course')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        else:
            st.info("No attendance data available.")
    
    with col2:
        st.write("**Participation Levels**")
        participation = engagement_data.get('participation_levels', {})
        if participation:
            participation_data = []
            for course, level in participation.items():
                participation_data.append({
                    "Course": course,
                    "Participation Level": level,
                    "Status": "High" if level > 80 else "Medium" if level > 60 else "Low"
                })
            
            st.dataframe(participation_data, use_container_width=True)
        else:
            st.info("No participation data available.")

def show_assessment_analysis_analytics(analytics_data):
    """Show assessment analysis analytics"""
    st.subheader("📊 Assessment Analysis")
    
    assessment_data = analytics_data.get('assessment_analysis', {})
    
    # Assessment performance
    st.write("**Assessment Performance**")
    assessment_performance = assessment_data.get('assessment_performance', [])
    
    if assessment_performance:
        perf_data = []
        for assessment in assessment_performance:
            perf_data.append({
                "Assessment": assessment.get('name', 'N/A'),
                "Course": assessment.get('course', 'N/A'),
                "Average Score": f"{assessment.get('average_score', 0):.1f}%",
                "Highest Score": f"{assessment.get('highest_score', 0):.1f}%",
                "Lowest Score": f"{assessment.get('lowest_score', 0):.1f}%",
                "Completion Rate": f"{assessment.get('completion_rate', 0):.1f}%"
            })
        
        st.dataframe(perf_data, use_container_width=True)
    else:
        st.info("No assessment performance data available.")

def show_teaching_trends_analytics(analytics_data):
    """Show teaching trends analytics"""
    st.subheader("📈 Teaching Trends")
    
    trends_data = analytics_data.get('teaching_trends', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Grade Trends Over Time**")
        grade_trends = trends_data.get('grade_trends', [])
        if grade_trends:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            semesters = [trend.get('semester', 'N/A') for trend in grade_trends]
            avg_grades = [trend.get('average_grade', 0) for trend in grade_trends]
            
            ax.plot(semesters, avg_grades, marker='o', linewidth=2, markersize=8)
            ax.set_xlabel('Semester')
            ax.set_ylabel('Average Grade')
            ax.set_title('Grade Trends Over Time')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        else:
            st.info("No grade trend data available.")
    
    with col2:
        st.write("**Course Load Analysis**")
        course_load = trends_data.get('course_load', {})
        if course_load:
            load_data = []
            for semester, load in course_load.items():
                load_data.append({
                    "Semester": semester,
                    "Courses": load.get('courses', 0),
                    "Students": load.get('students', 0),
                    "Credits": load.get('credits', 0)
                })
            
            st.dataframe(load_data, use_container_width=True)
        else:
            st.info("No course load data available.")

def show_performance_insights_analytics(analytics_data):
    """Show performance insights analytics"""
    st.subheader("🎯 Performance Insights")
    
    insights_data = analytics_data.get('performance_insights', {})
    
    # Key insights
    st.write("**Key Insights**")
    insights = insights_data.get('insights', [])
    
    if insights:
        for insight in insights:
            st.info(f"💡 {insight}")
    else:
        st.info("No insights available.")
    
    # Recommendations
    st.write("**Recommendations**")
    recommendations = insights_data.get('recommendations', [])
    
    if recommendations:
        for rec in recommendations:
            st.success(f"✅ {rec}")
    else:
        st.info("No recommendations available.")

def fetch_student_analytics():
    """Fetch comprehensive student analytics data"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Fetch multiple analytics endpoints
        analytics_data = {}
        
        # Academic dashboard data
        dashboard_response = requests.get(
            f"{API_BASE_URL}/academic-records/dashboard",
            headers=headers,
            timeout=10
        )
        if dashboard_response.status_code == 200:
            analytics_data.update(dashboard_response.json())
        
        # Grades data
        grades_response = requests.get(
            f"{API_BASE_URL}/academic-records/grades",
            headers=headers,
            timeout=10
        )
        if grades_response.status_code == 200:
            analytics_data['grades_data'] = grades_response.json()
        
        # Academic summary
        summary_response = requests.get(
            f"{API_BASE_URL}/academic-records/academic-summary",
            headers=headers,
            timeout=10
        )
        if summary_response.status_code == 200:
            analytics_data.update(summary_response.json())
        
        return analytics_data
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch analytics data: {str(e)}")
        return None

def fetch_professor_analytics():
    """Fetch comprehensive professor analytics data"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        
        # Fetch multiple analytics endpoints
        analytics_data = {}
        
        # Professor dashboard data
        dashboard_response = requests.get(
            f"{API_BASE_URL}/student-information/dashboard",
            headers=headers,
            timeout=10
        )
        if dashboard_response.status_code == 200:
            analytics_data.update(dashboard_response.json())
        
        # Teaching load data
        teaching_load = fetch_teaching_load()
        if teaching_load:
            analytics_data.update(teaching_load)
        
        # Course performance data
        courses = fetch_professor_courses()
        if courses:
            analytics_data['course_performance'] = courses
        
        return analytics_data
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch analytics data: {str(e)}")
        return None

# Check for registration form display
if 'show_registration' in st.session_state and st.session_state.show_registration:
    show_registration_form()

# Check for change password form display
if 'show_change_password' in st.session_state and st.session_state.show_change_password:
    show_change_password_form()

if __name__ == "__main__":
    main()