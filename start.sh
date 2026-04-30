#!/bin/bash

# Zolve Backend & Frontend Startup Script

echo "🚀 Starting Zolve Backend & Frontend..."
echo ""

# Check if backend is running
echo "Checking backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend already running on http://localhost:8000"
else
    echo "Starting backend server..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
    cd ..
fi

# Small delay to ensure backend is ready
sleep 2

# Start frontend
echo ""
echo "Starting frontend..."
echo "📱 Streamlit app will open at http://localhost:8501"
echo ""
streamlit run frontend/app.py

# Cleanup
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
fi
