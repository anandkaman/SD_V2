@echo off
REM Production Build Script for SaleDeed Processor
REM Builds Electron installer for Windows

echo ========================================
echo SaleDeed Processor - Production Build
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check Node version
echo Checking Node.js version...
node --version
npm --version
echo.

REM Navigate to frontend directory
cd sale-deed-processor\fronted

echo Step 1/4: Installing dependencies...
echo This may take a few minutes...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 2/4: Building React application...
echo This may take 2-3 minutes...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: React build failed
    pause
    exit /b 1
)
echo React build complete!
echo.

echo Step 3/4: Creating Electron installer...
echo This may take 5-10 minutes...
echo.
call npm run dist
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Electron build failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Installer location:
echo   dist\SaleDeed Processor Setup 1.0.0.exe
echo.
echo Build artifacts:
dir dist\*.exe 2>nul
echo.

echo Step 4/4: Moving installer to release directory...
cd ..\..

REM Create release directory if it doesn't exist
if not exist "release" mkdir release

REM Copy installer to release directory with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set mytime=%mytime: =0%

copy "sale-deed-processor\fronted\dist\SaleDeed Processor Setup 1.0.0.exe" "release\SaleDeed-Processor-v1.0.0-%mydate%-%mytime%.exe"

if exist "release\SaleDeed-Processor-v1.0.0-%mydate%-%mytime%.exe" (
    echo.
    echo Installer copied to: release\SaleDeed-Processor-v1.0.0-%mydate%-%mytime%.exe
    echo.
    echo Production build complete and ready for distribution!
) else (
    echo.
    echo WARNING: Could not copy installer to release directory
    echo Installer is available at: sale-deed-processor\fronted\dist\
)

echo.
echo ========================================
echo Build Information
echo ========================================
echo Version: 1.0.0
echo Platform: Windows x64
echo Type: NSIS Installer
echo Estimated Size: ~100 MB
echo.
echo Next Steps:
echo 1. Test the installer on a clean Windows machine
echo 2. Verify all features work correctly
echo 3. Distribute to users
echo.
pause
