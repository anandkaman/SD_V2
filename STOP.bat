@echo off
title SaleDeed Processor - Stopping...

echo.
echo ========================================
echo  Stopping SaleDeed Processor
echo ========================================
echo.

REM Kill Electron processes first
echo Stopping Electron app...
taskkill /F /IM electron.exe 2>nul

REM Kill Node.js processes
echo Stopping Node.js processes...
taskkill /F /IM node.exe 2>nul

REM Kill Python processes
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

REM Kill processes by port
echo Stopping processes on ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":4000" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Kill all cmd.exe windows with SaleDeed in title
echo Closing terminal windows...
for /f "tokens=2" %%a in ('tasklist /v /fo list ^| findstr /i "SaleDeed"') do taskkill /F /PID %%a 2>nul

REM Alternative: Kill cmd windows by window title
powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -like '*SaleDeed*'} | Stop-Process -Force" 2>nul

echo.
echo ========================================
echo  All Services Stopped!
echo ========================================
echo.
echo All processes and terminals closed.
echo.
timeout /t 2 /nobreak >nul
exit
