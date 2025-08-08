@echo off
REM SuperClaude Local Server Startup Script
REM Automated server startup with dependency installation and error handling

title SuperClaude Crypto API Server

echo ===============================================
echo SuperClaude Local API Server
echo Unified Cryptocurrency Data APIs
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [INFO] Python detected successfully
echo [INFO] Installing/updating dependencies...
echo.

REM Install required packages
pip install -r requirements_server.txt

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo The server may still work with existing packages
    echo.
    pause
)

echo.
echo [INFO] Dependencies installed successfully
echo [INFO] Starting SuperClaude API Server...
echo.

REM Start the server
python superclaude_local_server.py

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo Check the error messages above for details
    echo.
    pause
)

echo.
echo [INFO] Server has stopped
pause