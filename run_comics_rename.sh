#!/bin/bash
"""
ComicsRename - Simple Run Script

This script runs ComicsRename with the system Python installation
where all dependencies are available.
"""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "🚀 Starting ComicsRename..."
echo "📁 Project directory: $DIR"

cd "$DIR"

# Check if dependencies are available
echo "🔍 Checking Safe Rename dependencies..."
python3 -c "
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
echo "💡 Close the application window to exit"
echo ""

# Run the application with system Python
python3 main.py

echo ""
echo "👋 ComicsRename has been closed"
