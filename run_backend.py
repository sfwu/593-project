#!/usr/bin/env python3
"""
Simple script to run the FastAPI backend
"""
import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 Starting Academic Information Management System API...")
    print("📊 API Documentation: http://localhost:9100/docs")
    print("🏥 Health Check: http://localhost:9100/health")
    print("👋 Hello World: http://localhost:9100/")
    print("⏹️  Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=9100, reload=True)
