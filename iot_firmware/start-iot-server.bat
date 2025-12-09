@echo off
echo ============================================
echo  Starting IoT Smart Garden Server
echo ============================================
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [SETUP] Installing dependencies...
    call npm install
    echo.
)

echo [START] Launching IoT server...
echo.

node server.js

pause
