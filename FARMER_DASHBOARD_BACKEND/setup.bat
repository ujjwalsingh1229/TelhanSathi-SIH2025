@echo off
REM Installation and Setup Script for Farmer Dashboard Backend (Windows)

echo.
echo ==========================================
echo Farmer Dashboard Backend - Setup Script
echo ==========================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+
    pause
    exit /b 1
)
echo ^✓ Python found
echo.

REM Step 2: Create virtual environment
echo Step 2: Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo ^✓ Virtual environment created
echo.

REM Step 3: Install dependencies
echo Step 3: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ^✓ Dependencies installed
echo.

REM Step 4: Initialize database
echo Step 4: Initializing database...
if exist farmer_dashboard.db (
    echo Database already exists
) else (
    python -c "import sqlite3; sqlite3.connect('farmer_dashboard.db')"
    echo ^✓ Database file created
)
echo Run this manually: sqlite3 farmer_dashboard.db ^< database_schema.sql
echo.

REM Step 5: Run tests
echo Step 5: Running tests...
python -m pytest test_endpoints.py -v
if errorlevel 1 (
    echo WARNING: Some tests failed. Check the output above.
)
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the server, run:
echo   python app.py
echo.
echo Then access the API at:
echo   http://localhost:5000/api/predict-profit (POST)
echo   http://localhost:5000/api/forecast-arima (POST)
echo   http://localhost:5000/api/recommend-crop (POST)
echo.
pause
