"""
FastAPI backend for Academic Information Management System
Clean structured architecture ready for implementation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Academic Information Management System", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - Hello World"""
    return {"message": "Hello World! Academic Information Management System API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "academic-management-api"}

# TODO: Import and include routers from controllers
# Example:
# from controllers.student_controller import router as student_router
# app.include_router(student_router, prefix="/students", tags=["students"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9100)
