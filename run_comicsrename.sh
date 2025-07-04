#!/bin/bash
"""
ComicsRename Launcher Script

This script ensures ComicsRename runs with the correct virtual environment
and all dependencies (including Safe Rename) are available.
"""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if virtual environment exists
if [ ! -d "$DIR/.venv" ]; then
    echo "❌ Virtual environment not found at $DIR/.venv"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run the application
echo "🚀 Starting ComicsRename with virtual environment..."
echo "📁 Project directory: $DIR"
echo "🐍 Virtual environment: $DIR/.venv"

cd "$DIR"
source .venv/bin/activate

# Check if dependencies are available
echo "🔍 Checking dependencies..."
python -c "
import sys
sys.path.insert(0, '.')

try:
    import cv2
    print('✅ OpenCV available')
except ImportError:
    print('❌ OpenCV not available - Safe Rename will be disabled')

try:
    from skimage.metrics import structural_similarity as ssim
    print('✅ scikit-image available')
except ImportError:
    print('❌ scikit-image not available - Safe Rename will be disabled')

try:
    from pdf_cover_comparator_qt import PDFCoverComparator
    print('✅ Safe Rename feature available')
except ImportError:
    print('❌ Safe Rename feature not available')
"

echo ""
echo "🎉 Starting ComicsRename..."
echo "💡 Close this terminal window to exit the application"
echo ""

# Run the application
python main.py

echo ""
echo "👋 ComicsRename has been closed"
