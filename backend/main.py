"""
FastAPI backend for Academic Information Management System
Complete authentication and user management system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import init_db

# Import all routers
from controllers.auth_controller import router as auth_router
from controllers.student_controller import router as student_router
from controllers.professor_controller import router as professor_router
from controllers.course_controller import router as course_router
from controllers.academic_record_controller import router as academic_record_router
from controllers.student_information_controller import router as student_information_router
from controllers.grading_assessment_controller import router as grading_assessment_router

app = FastAPI(
    title="Academic Information Management System", 
    version="1.0.0",
    description="A comprehensive system for academic information management with role-based authentication"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()

@app.get("/")
async def root():
    """Root endpoint - API Information"""
    return {
        "message": "Academic Information Management System API",
        "version": "1.0.0",
        "features": [
            "JWT Authentication",
            "Role-based Access Control (Student/Professor)",
            "Student Profile Management",
            "Course Search and Registration",
            "Professor Course Administration",
            "Enrollment Management",
            "Academic Record Access",
            "Grade Management",
            "Transcript Generation",
            "GPA Calculation",
            "Academic Progress Tracking",
            "Student Information Management",
            "Student Directory Access",
            "Attendance Tracking",
            "Student Communication",
            "Performance Monitoring",
            "Grading and Assessment",
            "Grade Management",
            "Gradebook Management",
            "Assignment Creation",
            "Exam Scheduling"
        ],
        "auth_endpoints": [
            "POST /auth/login - User login",
            "POST /auth/register/student - Student registration",
            "POST /auth/register/professor - Professor registration",
            "GET /auth/me - Get current user profile"
        ],
        "course_endpoints": [
            "GET /courses - Browse all courses (role-based filtering)",
            "GET /courses/{id} - Get course details",
            "GET /courses/{id}/enrollment - Get enrollment info",
            "GET /courses/departments/list - List all departments",
            "GET /courses/semesters/list - List all semesters"
        ],
        "academic_record_endpoints": [
            "GET /academic-records/grades - View student grades",
            "GET /academic-records/gpa - Get GPA calculation",
            "GET /academic-records/transcripts - List transcripts",
            "POST /academic-records/transcripts/generate - Generate transcript",
            "GET /academic-records/progress - View academic progress",
            "GET /academic-records/dashboard - Academic dashboard"
        ],
        "student_information_endpoints": [
            "GET /student-information/directory - Access student directory",
            "GET /student-information/academic-records - View student academic history",
            "POST /student-information/attendance - Record attendance",
            "GET /student-information/attendance - View attendance records",
            "POST /student-information/messages - Send messages to students",
            "GET /student-information/messages - View sent messages",
            "GET /student-information/dashboard - Professor dashboard"
        ],
        "grading_assessment_endpoints": [
            "POST /grading/assignments - Create assignments",
            "GET /grading/assignments - View assignments",
            "POST /grading/exams - Schedule exams",
            "GET /grading/exams - View exams",
            "POST /grading/grades - Create grades",
            "GET /grading/grades - View grades",
            "POST /grading/gradebooks - Create gradebooks",
            "GET /grading/gradebooks - View gradebooks",
            "GET /grading/dashboard - Grading dashboard"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "academic-management-api"}

# Include routers with prefixes and tags
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(student_router, prefix="/students", tags=["Students"])
app.include_router(professor_router, prefix="/professors", tags=["Professors"])
app.include_router(course_router, prefix="/courses", tags=["Courses"])
app.include_router(academic_record_router, prefix="/academic-records", tags=["Academic Records"])
app.include_router(student_information_router, prefix="/student-information", tags=["Student Information Management"])
app.include_router(grading_assessment_router, prefix="/grading", tags=["Grading and Assessment"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9600)
