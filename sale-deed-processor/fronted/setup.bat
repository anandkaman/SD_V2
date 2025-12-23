@echo off
echo ================================
echo SaleDeed Processor - Frontend Setup
echo ================================
echo.

echo Installing dependencies...
call npm install

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To run the application:
echo 1. Make sure backend is running on http://localhost:8000
echo 2. Run: npm run electron-dev
echo.
echo For production build:
echo - npm run build
echo - npm run dist
echo.
pause
