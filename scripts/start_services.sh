#!/bin/bash

# SecuRizz Service Startup Script
echo "🚀 Starting SecuRizz Services"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Check required ports
echo "🔍 Checking port availability..."
check_port 8000 || exit 1
check_port 3000 || exit 1

# Start Backend API
echo "🔧 Starting Backend API on port 8000..."
cd backend-api
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start Oracle Service
echo "📡 Starting Oracle Service..."
cd oracle-service
npm run dev &
ORACLE_PID=$!
cd ..

# Wait a moment for oracle to start
sleep 3

# Start Frontend
echo "🌐 Starting Frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "📋 Service URLs:"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop all services, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $ORACLE_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop services
wait
