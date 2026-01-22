@echo off
REM Bank Teller Chatbot - Unified Launcher
REM Starts both backend server and Flutter frontend
REM Usage: run_app.bat [device]
REM        run_app.bat windows (default)
REM        run_app.bat web

setlocal enabledelayedexpansion

set DEVICE=%1
if "%DEVICE%"=="" set DEVICE=windows

set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend\app
set FRONTEND_DIR=%PROJECT_ROOT%frontend\bank_teller_bot_frontend
set PYTHON_EXE=C:\Users\talha\AppData\Local\Programs\Python\Python310\python.exe

cls
echo.
echo ============================================================
echo    Bank Teller Chatbot - Unified Launcher
echo ============================================================
echo.

REM ============================================================
REM STEP 1: Clear all caches for fresh start
REM ============================================================
echo [*] Cleaning up caches for fresh start...

REM Kill any running Python/Node processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Clear backend Python cache
echo [*] Clearing backend Python cache...
if exist "%PROJECT_ROOT%backend\app\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\__pycache__" >nul 2>&1
)
if exist "%PROJECT_ROOT%backend\app\auth\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\auth\__pycache__" >nul 2>&1
)
if exist "%PROJECT_ROOT%backend\app\database\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\database\__pycache__" >nul 2>&1
)
if exist "%PROJECT_ROOT%backend\app\ml\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\ml\__pycache__" >nul 2>&1
)
if exist "%PROJECT_ROOT%backend\app\ml\dialogue\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\ml\dialogue\__pycache__" >nul 2>&1
)
if exist "%PROJECT_ROOT%backend\app\utils\__pycache__" (
    rmdir /S /Q "%PROJECT_ROOT%backend\app\utils\__pycache__" >nul 2>&1
)
echo [OK] Backend cache cleared

REM Clear frontend cache
echo [*] Clearing frontend cache...
if exist "%FRONTEND_DIR%\node_modules" (
    rmdir /S /Q "%FRONTEND_DIR%\node_modules" >nul 2>&1
    echo [OK] Frontend node_modules deleted
)
if exist "%FRONTEND_DIR%\.next" (
    rmdir /S /Q "%FRONTEND_DIR%\.next" >nul 2>&1
    echo [OK] Frontend .next cache deleted
)
if exist "%FRONTEND_DIR%\.dart_tool" (
    rmdir /S /Q "%FRONTEND_DIR%\.dart_tool" >nul 2>&1
    echo [OK] Frontend .dart_tool deleted
)
if exist "%FRONTEND_DIR%\build" (
    rmdir /S /Q "%FRONTEND_DIR%\build" >nul 2>&1
    echo [OK] Frontend build cache deleted
)

REM Clear session state by setting environment variable
set FORCE_FRESH_SESSIONS=1

echo [OK] All caches cleared - fresh start enabled
echo.

REM ============================================================
REM STEP 2: Start backend and frontend
REM ============================================================

REM Check if backend is already running
echo [*] Checking if backend is already running on port 8000...
netstat -ano | find ":8000" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend already running on port 8000
) else (
    echo [*] Starting backend server...
    start "Bank Teller Backend" cmd /c "cd /d %BACKEND_DIR%& %PYTHON_EXE% -m uvicorn main:app --host 127.0.0.1 --port 8000"
    
    echo [*] Waiting for backend to initialize ^(8 seconds^)...
    timeout /t 8 /nobreak
    
    echo [OK] Backend server started!
    echo Backend window will stay open. Keep it running while using the app.
)

echo.
echo [*] Launching Flutter app (%DEVICE%)...
echo.

REM Launch Flutter app
cd /d %FRONTEND_DIR%
call flutter run -d %DEVICE%

endlocal
