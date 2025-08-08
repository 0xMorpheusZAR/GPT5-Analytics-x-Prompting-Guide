@echo off
title SuperClaude Crypto Dashboard Launcher
echo ===============================================
echo   SuperClaude Crypto Analysis Dashboard
echo ===============================================
echo.
echo Launching dashboard options...
echo.
echo 1. Starting local server...
start "SuperClaude Server" cmd /k start_crypto_server.bat
echo.
echo 2. Waiting for server startup...
timeout /t 5 /nobreak > nul
echo.
echo 3. Opening live dashboard in browser...
start "" "http://localhost:8080"
echo.
echo 4. Opening static dashboard as backup...
start "" crypto_dashboard.html
echo.
echo Dashboard launched successfully!
echo - Live version: http://localhost:8080
echo - Static version: crypto_dashboard.html
echo.
echo Press any key to exit...
pause > nul