#!/usr/bin/env python3
"""
Simple script to run the Streamlit frontend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    app_path = os.path.join(frontend_path, 'app.py')
    
    print("🎓 Starting Academic Information Management System Frontend...")
    print("🌐 Frontend URL: http://localhost:9700")
    print("⚠️  Make sure the backend is running on http://localhost:9600")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "9700"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running frontend: {e}")
        sys.exit(1)
