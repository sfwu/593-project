"""
Streamlit frontend for Academic Information Management System
"""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:9600"

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Academic Information Management System",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Academic Information Management System")
    st.markdown("**Hello World** - Student Management Interface")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "View Students", "Add Student", "Update Student", "Delete Student"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "View Students":
        show_students()
    elif page == "Add Student":
        add_student()
    elif page == "Update Student":
        update_student()
    elif page == "Delete Student":
        delete_student()

def check_api_connection():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def show_dashboard():
    """Show dashboard page"""
    st.header("📊 Dashboard")
    
    # Check API connection
    if check_api_connection():
        st.success("✅ Backend API is connected and healthy!")
        st.info("⚠️ Student endpoints need to be implemented in the new backend structure")
        
        # TODO: Uncomment when student endpoints are implemented
        # try:
        #     response = requests.get(f"{API_BASE_URL}/students/")
        #     if response.status_code == 200:
        #         students = response.json()
        #         st.metric("Total Students", len(students))
        #         
        #         if students:
        #             df = pd.DataFrame(students)
        #             st.subheader("Recent Students")
        #             st.dataframe(df.head(5))
        #     else:
        #         st.warning("Could not fetch student data")
        # except requests.exceptions.RequestException as e:
        #     st.error(f"Error fetching data: {e}")
    else:
        st.error("❌ Backend API is not available. Please start the FastAPI server.")
        st.code("python run_backend.py")

def show_students():
    """Show all students"""
    st.header("👥 All Students")
    
    st.info("⚠️ This feature requires implementation of student endpoints in the new backend structure")
    
    # TODO: Uncomment when student endpoints are implemented
    # try:
    #     response = requests.get(f"{API_BASE_URL}/students/")
    #     if response.status_code == 200:
    #         students = response.json()
    #         if students:
    #             df = pd.DataFrame(students)
    #             st.dataframe(df)
    #         else:
    #             st.info("No students found. Add some students to get started!")
    #     else:
    #         st.error("Failed to fetch students")
    # except requests.exceptions.RequestException as e:
    #     st.error(f"Error: {e}")

def add_student():
    """Add a new student"""
    st.header("➕ Add New Student")
    
    st.info("⚠️ This feature requires implementation of student endpoints in the new backend structure")
    
    with st.form("add_student_form"):
        first_name = st.text_input("First Name*")
        last_name = st.text_input("Last Name*")
        email = st.text_input("Email*")
        student_id = st.text_input("Student ID*")
        
        submitted = st.form_submit_button("Add Student (Not Functional Yet)")
        
        if submitted:
            st.warning("⚠️ Student creation is not implemented yet. Backend structure needs to be completed first.")

def update_student():
    """Update an existing student"""
    st.header("✏️ Update Student")
    
    st.info("⚠️ This feature requires implementation of student endpoints in the new backend structure")
    
    st.selectbox("Select a student to update", ["Feature not available yet"])
    
    with st.form("update_student_form"):
        first_name = st.text_input("First Name", disabled=True)
        last_name = st.text_input("Last Name", disabled=True)
        email = st.text_input("Email", disabled=True)
        student_id_field = st.text_input("Student ID", disabled=True)
        
        submitted = st.form_submit_button("Update Student (Not Functional Yet)")
        
        if submitted:
            st.warning("⚠️ Student update is not implemented yet. Backend structure needs to be completed first.")

def delete_student():
    """Delete a student"""
    st.header("🗑️ Delete Student")
    st.warning("⚠️ This action cannot be undone!")
    
    st.info("⚠️ This feature requires implementation of student endpoints in the new backend structure")
    
    st.selectbox("Select a student to delete", ["Feature not available yet"])
    
    if st.button("🗑️ Delete Student (Not Functional Yet)", type="primary", disabled=True):
        st.warning("⚠️ Student deletion is not implemented yet. Backend structure needs to be completed first.")

if __name__ == "__main__":
    main()
