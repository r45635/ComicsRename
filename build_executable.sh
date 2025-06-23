#!/bin/bash
# Build script for ComicsRename executable (cross-platform)

echo "===================================="
echo "Building ComicsRename executable"
echo "===================================="

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS_TYPE="windows"
fi

echo "Detected OS: $OS_TYPE"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OS_TYPE" == "windows" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build the executable
echo "Building executable..."
python -m PyInstaller ComicsRename.spec

# Check if build was successful
if [[ "$OS_TYPE" == "windows" ]]; then
    EXECUTABLE="dist/ComicsRename.exe"
else
    EXECUTABLE="dist/ComicsRename"
fi

if [ -f "$EXECUTABLE" ]; then
    echo ""
    echo "===================================="
    echo "Build completed successfully!"
    echo "===================================="
    echo "Executable location: $EXECUTABLE"
    echo "File size: $(du -h "$EXECUTABLE" | cut -f1)"
    echo ""
    echo "You can now distribute the executable file"
    echo "It includes all dependencies and can run standalone"
else
    echo ""
    echo "===================================="
    echo "Build failed!"
    echo "===================================="
    echo "Please check the error messages above"
    exit 1
fi
