@echo off
title SuperClaude Crypto Analysis Server
echo ===============================================
echo   SuperClaude Crypto Analysis Suite Server
echo ===============================================
echo.
echo Starting Flask development server...
echo Server will be available at: http://localhost:8080
echo.
echo Available endpoints:
echo   GET / - Main dashboard
echo   GET /api/status - API status check
echo   GET /api/risk-analysis - Risk management
echo   GET /api/sector-scout - Sector opportunities  
echo   GET /api/dip-buyer - Leverage reset detection
echo   GET /api/yield-analysis - DeFi yields
echo   GET /api/altcoin-strength - ETH outperformers
echo   GET /api/gem-analysis - Micro-cap deep dive
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

python crypto_server.py

pause