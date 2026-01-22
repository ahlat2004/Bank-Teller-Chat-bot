@echo off
REM Start server in background and run test

cd /d "e:\AI Project\bank-teller-chatbot"

REM Set environment variables
set SMTP_EMAIL=talhamughal1805@gmail.com
set SMTP_PASSWORD=rmxqdfcjkmeabwva

REM Start server in a new window
echo Starting FastAPI server...
start "Bank Teller Chatbot Server" cmd /k "C:/Users/talha/AppData/Local/Programs/Python/Python310/python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

REM Wait for server to start
timeout /t 8 /nobreak

REM Run the test in this window
echo.
echo Starting account creation test...
echo.
C:/Users/talha/AppData/Local/Programs/Python/Python310/python.exe test_account_creation_otp.py

pause
