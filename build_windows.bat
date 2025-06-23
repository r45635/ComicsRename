@echo off
REM Build script for ComicsRename Windows executable

echo ====================================
echo Building ComicsRename for Windows
echo ====================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

REM Build the executable
echo Building executable...
python -m PyInstaller ComicsRename.spec

REM Check if build was successful
if exist "dist\ComicsRename.exe" (
    echo.
    echo ====================================
    echo Build completed successfully!
    echo ====================================
    echo Executable location: dist\ComicsRename.exe
    echo File size: 
    dir dist\ComicsRename.exe
    echo.
    echo You can now distribute the ComicsRename.exe file
    echo It includes all dependencies and can run on any Windows system
) else (
    echo.
    echo ====================================
    echo Build failed!
    echo ====================================
    echo Please check the error messages above
)

pause
