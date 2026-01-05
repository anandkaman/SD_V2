@echo off
title SaleDeed Processor - Setup

echo.
echo ========================================
echo  SaleDeed Processor - First Time Setup
echo ========================================
echo.
echo This will install all required dependencies GLOBALLY
echo (No virtual environment needed)
echo Please wait, this may take 5-10 minutes...
echo.
pause

REM Setup Backend Dependencies (Global Python)
echo.
echo [1/2] Installing Backend Dependencies...
echo ========================================
cd sale-deed-processor\sale_deed_processor\backend

echo Installing Python packages globally...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install backend dependencies
    echo Make sure Python and pip are installed
    pause
    exit /b 1
)

echo Backend dependencies installed!
cd ..\..\..

REM Setup Frontend
echo.
echo [2/2] Installing Frontend Dependencies...
echo ========================================
cd sale-deed-processor\fronted

echo Installing Node packages...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install frontend dependencies
    echo Make sure Node.js and npm are installed
    pause
    exit /b 1
)

echo Frontend dependencies installed!
cd ..\..\

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo All dependencies installed globally.
echo You can now run START.bat to launch the application
echo.
pause
