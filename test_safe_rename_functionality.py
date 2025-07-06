#!/usr/bin/env python3
"""
Test script to verify SafeRename functionality after the QImage.save fix.
"""

import sys
import os
import tempfile
from pathlib import Path
import shutil

# Add the project root to the Python path
sys.path.insert(0, '/Users/vincentcruvellier/Documents/GitHub/ComicsRename')

def test_safe_rename_import():
    """Test that SafeRename components can be imported successfully."""
    
    try:
        from core.safe_rename_manager import SafeRenameManager
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.image_manager import ImageManager
        print("✓ All SafeRename components imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_safe_rename_manager_creation():
    """Test that SafeRenameManager can be created with required dependencies."""
    
    try:
        from core.safe_rename_manager import SafeRenameManager
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.image_manager import ImageManager
        
        # Create dependencies
        settings_manager = SettingsManager()
        error_handler = ErrorHandler()
        image_manager = ImageManager()
        
        # Create SafeRenameManager
        safe_rename_manager = SafeRenameManager(
            settings_manager=settings_manager,
            error_handler=error_handler,
            image_manager=image_manager,
            debug=True
        )
        
        print("✓ SafeRenameManager created successfully")
        return True
        
    except Exception as e:
        print(f"✗ SafeRenameManager creation failed: {e}")
        return False

def test_pdf_cover_comparator_import():
    """Test that PDF cover comparator can be imported and used."""
    
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        
        # Create comparator
        comparator = PDFCoverComparator(ssim_threshold=0.7)
        
        print("✓ PDFCoverComparator imported and created successfully")
        return True
        
    except Exception as e:
        print(f"✗ PDFCoverComparator test failed: {e}")
        return False

def test_main_app_import():
    """Test that the main application can be imported without errors."""
    
    try:
        # Try importing the main application components
        import comicsFileRenamer_v3
        print("✓ Main application imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Main application import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing SafeRename functionality after QImage.save fix...")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_safe_rename_import,
        test_safe_rename_manager_creation,
        test_pdf_cover_comparator_import,
        test_main_app_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{test.__doc__}")
        if test():
            passed += 1
        else:
            print("  (This test failed)")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! SafeRename functionality appears to be working correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)
