@echo off
echo Building Compact Gantt executable...
echo.

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo .venv not found. Please create it and install dependencies first.
    pause
    exit /b 1
)

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Running PyInstaller...
.venv\Scripts\python -m PyInstaller compactgantt.spec

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: dist\CompactGantt.exe
echo.
pause
