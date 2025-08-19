#!/bin/bash

# Academic Information Management System - Status Script
# Check if services are running

echo "📊 Academic Information Management System Status"
echo "=" * 50

# Check Backend Status
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 Backend: ✅ RUNNING (PID: $BACKEND_PID)"
        echo "   📊 API: http://localhost:9100"
        echo "   📚 Docs: http://localhost:9100/docs"
    else
        echo "🔧 Backend: ❌ STOPPED (stale PID file)"
        rm -f .backend.pid
    fi
else
    echo "🔧 Backend: ❌ STOPPED"
fi

# Check Frontend Status  
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 Frontend: ✅ RUNNING (PID: $FRONTEND_PID)"
        echo "   🌐 Web UI: http://localhost:9200"
    else
        echo "🎨 Frontend: ❌ STOPPED (stale PID file)"
        rm -f .frontend.pid
    fi
else
    echo "🎨 Frontend: ❌ STOPPED"
fi

echo ""

# Check database status
echo "🗄️  Database Status:"
if [ -f "data/academic_management.db" ]; then
    DB_SIZE=$(ls -lh data/academic_management.db | awk '{print $5}')
    echo "   • Main DB: data/academic_management.db ($DB_SIZE)"
else
    echo "   • Main DB: ❌ Not created (run: python init_sample_data.py)"
fi

# Count test databases
TEST_DB_COUNT=$(ls data/test_*.db 2>/dev/null | wc -l)
if [ $TEST_DB_COUNT -gt 0 ]; then
    echo "   • Test DBs: $TEST_DB_COUNT files"
else
    echo "   • Test DBs: None"
fi

echo ""

# Check if log files exist
if [ -d "logs" ]; then
    echo "📋 Log Files:"
    if [ -f "logs/backend.log" ]; then
        BACKEND_LOG_SIZE=$(wc -l < logs/backend.log)
        echo "   • Backend: logs/backend.log ($BACKEND_LOG_SIZE lines)"
    fi
    if [ -f "logs/frontend.log" ]; then
        FRONTEND_LOG_SIZE=$(wc -l < logs/frontend.log)
        echo "   • Frontend: logs/frontend.log ($FRONTEND_LOG_SIZE lines)"
    fi
    echo ""
fi

# Quick actions
echo "🚀 Quick Actions:"
echo "   • Start services: ./start.sh"
echo "   • Stop services: ./stop.sh"
echo "   • Initialize database: python init_sample_data.py"
echo "   • Reset database: python init_sample_data.py --clear"
echo "   • Run tests: python run_tests.py"
echo ""
echo "📋 Logs & Debugging:"
echo "   • View backend logs: tail -f logs/backend.log"
echo "   • View frontend logs: tail -f logs/frontend.log"
echo ""
