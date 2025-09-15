#!/bin/bash

# Academic Information Management System - Start Script
# Starts both backend and frontend in background (non-blocking)

echo "🚀 Starting Academic Information Management System..."
echo "=" * 50

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if services are already running
if [ -f ".backend.pid" ] && kill -0 $(cat .backend.pid) 2>/dev/null; then
    echo "⚠️  Backend is already running (PID: $(cat .backend.pid))"
else
    # Start Backend (FastAPI)
    echo "🔧 Starting Backend (FastAPI)..."
    python run_backend.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
    echo "   ✅ Backend started (PID: $BACKEND_PID)"
    echo "   📊 API: http://localhost:9600"
    echo "   📚 Docs: http://localhost:9600/docs"
    echo "   📋 Logs: logs/backend.log"
fi

# Wait a moment for backend to start
sleep 2

if [ -f ".frontend.pid" ] && kill -0 $(cat .frontend.pid) 2>/dev/null; then
    echo "⚠️  Frontend is already running (PID: $(cat .frontend.pid))"
else
    # Start Frontend (Streamlit)
    echo "🎨 Starting Frontend (Streamlit)..."
    python run_frontend.py > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend.pid
    echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
    echo "   🌐 Web UI: http://localhost:9700"
    echo "   📋 Logs: logs/frontend.log"
fi

echo ""
echo "🎉 Academic Management System is running!"
echo ""
echo "📱 Quick Links:"
echo "   • Frontend: http://localhost:9700"
echo "   • Backend API: http://localhost:9600"
echo "   • API Documentation: http://localhost:9600/docs"
echo ""
echo "📋 Management:"
echo "   • View logs: tail -f logs/backend.log"
echo "   • View logs: tail -f logs/frontend.log"
echo "   • Stop services: ./stop.sh"
echo ""
echo "💡 The services are running in the background."
echo "   Your terminal is free to use for other commands!"
echo ""
