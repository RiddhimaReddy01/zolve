@echo off
REM Zolve Backend & Frontend Startup Script for Windows

echo.
echo 🚀 Starting Zolve Backend ^& Frontend...
echo.

REM Check if backend is running by trying to connect
timeout /t 1 /nobreak > nul
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend already running on http://localhost:8000
    goto frontend_start
)

REM Start backend in a new window
echo Starting backend server on port 8000...
cd backend
start "Zolve Backend" cmd /k python main.py
cd ..
timeout /t 3 /nobreak > nul
echo ✅ Backend started
echo.

:frontend_start
REM Start frontend
echo Starting Streamlit frontend on port 8501...
echo 📱 Frontend will open at http://localhost:8501
echo.
timeout /t 1 /nobreak > nul
streamlit run frontend/app.py

pause
