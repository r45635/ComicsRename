@echo off
REM ComicsRename Launcher Script for Windows
REM This script helps launch the ComicsRename application with proper environment setup

echo 🚀 ComicsRename Launcher
echo =========================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\PySide6" (
    echo 📋 Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo ✅ Dependencies already installed
)

REM Check for .env file
if not exist ".env" (
    echo ⚠️  No .env file found
    echo You can create one from .env.example for ComicVine API access:
    echo copy .env.example .env
    echo.
)

REM Launch the application
echo 🎮 Launching ComicsRename...
echo.

python main.py

pause
