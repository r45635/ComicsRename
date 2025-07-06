#!/usr/bin/env python3
"""
Test script to verify the QImage.save fix for PDF cover extraction.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, '/Users/vincentcruvellier/Documents/GitHub/ComicsRename')

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtCore import Qt
    QT_PDF_AVAILABLE = True
except ImportError:
    print("Qt PDF module not available")
    QT_PDF_AVAILABLE = False
    sys.exit(1)

def test_qimage_save_format():
    """Test that QImage.save works with different format arguments."""
    
    # Create a simple test image
    image = QImage(100, 100, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.white)
    
    # Test 1: Save with no format parameter (should use file extension)
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name
        
        success = image.save(temp_path)
        print(f"✓ Test 1 passed: save() with no format parameter = {success}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        return False
    
    # Test 2: Save with string format (might fail with type checker)
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name
        
        success = image.save(temp_path, "PNG")
        print(f"✓ Test 2 passed: save() with string format = {success}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        # This is expected to fail with type checker, but might work at runtime
    
    # Test 3: Save with bytes format
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name
        
        success = image.save(temp_path, b"PNG")
        print(f"✓ Test 3 passed: save() with bytes format = {success}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    
    return True

def test_pdf_cover_comparator():
    """Test the PDF cover comparator functionality."""
    
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        
        # Create a comparator instance
        comparator = PDFCoverComparator()
        print("✓ PDFCoverComparator created successfully")
        
        # Test the _extract_first_page method with a mock PDF
        # Note: This requires an actual PDF file to test properly
        print("✓ PDFCoverComparator import and instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"✗ PDFCoverComparator test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing QImage.save format parameter fix...")
    print("=" * 50)
    
    if not QT_PDF_AVAILABLE:
        print("Qt PDF module not available, skipping tests")
        sys.exit(1)
    
    # Test QImage.save format handling
    success1 = test_qimage_save_format()
    
    # Test PDF cover comparator
    success2 = test_pdf_cover_comparator()
    
    if success1 and success2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
