@echo off
echo ================================================
echo  Sale Deed Processor - Starting Application
echo ================================================
echo.

REM ================= START BACKEND ===================
echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "cd /d E:\salesdeed\sale-deed-processor\sale_deed_processor\backend && call venv_test\Scripts\activate && uvicorn app.main:app --reload"

REM Wait for backend to initialize
echo Waiting for backend to start (5 seconds)...
timeout /t 5 /nobreak >nul

REM ================= START FRONTEND ===================
echo [2/2] Starting Frontend...
start "Frontend App" cmd /k "cd /d E:\salesdeed\sale-deed-processor\fronted && call start-dev.bat"

REM Wait for applications to fully start
echo.
echo Waiting for applications to initialize (8 seconds)...
timeout /t 8 /nobreak >nul

echo.
echo ================================================
echo  Application Started Successfully!
echo ================================================
echo  Backend:  http://localhost:8000
echo  Frontend: Check the Frontend window for URL
echo ================================================
echo.
echo Press any key to close this launcher window...
echo (Backend and Frontend will continue running)
pause >nul
exit