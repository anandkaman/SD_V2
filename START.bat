@echo off
title SaleDeed Processor - Starting...

echo.
echo ========================================
echo  Starting SaleDeed Processor
echo ========================================
echo.

REM Start Backend (in separate terminal that will auto-exit when process ends)
echo [1/2] Starting Backend Server...
start /MIN "SaleDeed Backend" cmd /c start-backend-helper.bat

REM Wait a bit for backend
timeout /t 3 /nobreak >nul

REM Start Frontend as Electron App (in separate terminal that will auto-exit when process ends)
echo [2/2] Starting Electron Desktop App...
start /MIN "SaleDeed Electron" cmd /c start-frontend-helper.bat

echo.
echo ========================================
echo  Services Started!
echo ========================================
echo.
echo Backend:  Running on http://localhost:8000
echo Frontend: Electron Desktop App will open shortly...
echo.
echo Two command windows opened:
echo  - SaleDeed Backend
echo  - SaleDeed Electron
echo.
echo The desktop application will open automatically.
echo.
echo Close those windows to stop the services
echo Or run STOP.bat
echo.
pause
