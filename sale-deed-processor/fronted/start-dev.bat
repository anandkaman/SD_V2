@echo off
echo Starting SaleDeed Processor Frontend...
echo.
echo Make sure the backend is running on http://localhost:8000
echo.
set NODE_ENV=development
call npm run electron-dev
