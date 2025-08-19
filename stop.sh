#!/bin/bash

# Academic Information Management System - Stop Script
# Stops both backend and frontend services

echo "🛑 Stopping Academic Information Management System..."
echo "=" * 50

STOPPED_ANY=false

# Stop Backend
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 $BACKEND_PID 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "   ⚠️  Force killing backend..."
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        
        echo "   ✅ Backend stopped"
        STOPPED_ANY=true
    else
        echo "⚠️  Backend PID file exists but process not running"
    fi
    rm -f .backend.pid
else
    echo "ℹ️  Backend PID file not found (not running)"
fi

# Stop Frontend
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 $FRONTEND_PID 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "   ⚠️  Force killing frontend..."
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
        
        echo "   ✅ Frontend stopped"
        STOPPED_ANY=true
    else
        echo "⚠️  Frontend PID file exists but process not running"
    fi
    rm -f .frontend.pid
else
    echo "ℹ️  Frontend PID file not found (not running)"
fi

# Clean up any orphaned processes (backup method)
echo "🧹 Cleaning up any orphaned processes..."
pkill -f "run_backend.py" 2>/dev/null && echo "   🔧 Killed orphaned backend processes"
pkill -f "run_frontend.py" 2>/dev/null && echo "   🎨 Killed orphaned frontend processes"
pkill -f "streamlit run" 2>/dev/null && echo "   🎨 Killed orphaned streamlit processes"

echo ""
if [ "$STOPPED_ANY" = true ]; then
    echo "✅ Academic Management System stopped successfully!"
else
    echo "ℹ️  No running services found to stop"
fi

echo ""
echo "📋 Log files preserved:"
echo "   • Backend: logs/backend.log"
echo "   • Frontend: logs/frontend.log"
echo ""
echo "🚀 To start again: ./start.sh"
echo ""
