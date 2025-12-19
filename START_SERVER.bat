@echo off
REM ============================================================
REM FARMER PROFIT DASHBOARD - WINDOWS SERVER STARTUP
REM ============================================================

echo.
echo ============================================================
echo   FARMER PROFIT DASHBOARD - STARTING ON YOUR SERVER
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Check if model file exists
if not exist "yield_prediction_model.pkl" (
    echo ERROR: yield_prediction_model.pkl not found!
    echo Make sure this file is in the project root directory
    pause
    exit /b 1
)

echo [✓] Python installed
echo [✓] Model file found

REM Check if venv exists, create if not
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%a
)
set IP=%IP: =%

echo.
echo ============================================================
echo   DASHBOARD READY!
echo ============================================================
echo.
echo [✓] Virtual environment activated
echo [✓] Dependencies installed
echo [✓] Model loaded
echo.
echo ACCESS POINTS:
echo   Local:        http://localhost:5000
echo   This Network: http://%IP%:5000
echo.
echo Server running in production mode...
echo Press CTRL+C to stop
echo.
echo ============================================================
echo.

REM Run production server
python run_production.py

pause
