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
            "Enrollment Management"
        ],
        "auth_endpoints": [
            "POST /auth/login - User login",
            "POST /auth/register/student - Student registration",
            "POST /auth/register/professor - Professor registration",
            "GET /auth/me - Get current user profile"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9100)
