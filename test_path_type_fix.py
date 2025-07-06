#!/usr/bin/env python3
"""
Test script for the path type fix in SafeRenameManager.

This verifies that the _is_pdf_file method handles both PosixPath and string paths correctly.
"""

import os
import sys
import tempfile
import pathlib

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_path_type_fix():
    """Test the path type fix in SafeRenameManager."""
    print("🧪 Testing Path Type Fix in SafeRenameManager")
    print("=" * 50)
    
    try:
        # Import required modules
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.image_manager import ImageManager
        from core.safe_rename_manager import SafeRenameManager
        
        # Create required dependencies
        settings_manager = SettingsManager()
        error_handler = ErrorHandler()
        image_manager = ImageManager(debug=True)  # Use correct parameters
        
        # Create SafeRenameManager instance
        safe_rename_manager = SafeRenameManager(settings_manager, error_handler, image_manager)
        
        print("✅ SafeRenameManager instantiated successfully")
        
        # Test with PosixPath (the problematic case)
        test_path_obj = pathlib.PosixPath("/test/file.pdf")
        file_info_path_obj = {
            'path': test_path_obj,
            'ext': 'pdf',
            'name': 'file',
            'folder': '/test'
        }
        
        result1 = safe_rename_manager._is_pdf_file(file_info_path_obj)
        print(f"✅ _is_pdf_file with PosixPath: {result1}")
        
        # Test with string path
        file_info_string = {
            'path': "/test/file.pdf",
            'ext': 'pdf',
            'name': 'file',
            'folder': '/test'
        }
        
        result2 = safe_rename_manager._is_pdf_file(file_info_string)
        print(f"✅ _is_pdf_file with string: {result2}")
        
        # Test with non-PDF file
        file_info_cbz = {
            'path': pathlib.PosixPath("/test/file.cbz"),
            'ext': 'cbz',
            'name': 'file',
            'folder': '/test'
        }
        
        result3 = safe_rename_manager._is_pdf_file(file_info_cbz)
        print(f"✅ _is_pdf_file with CBZ file: {result3}")
        
        # Test edge cases
        file_info_empty = {
            'path': '',
            'ext': '',
            'name': '',
            'folder': ''
        }
        
        result4 = safe_rename_manager._is_pdf_file(file_info_empty)
        print(f"✅ _is_pdf_file with empty data: {result4}")
        
        # Verify all results
        expected_results = [True, True, False, False]
        actual_results = [result1, result2, result3, result4]
        
        if actual_results == expected_results:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Path type bug is fixed")
            print(f"✅ SafeRename will work correctly with drag & drop")
            return True
        else:
            print(f"\n❌ Test results mismatch:")
            print(f"   Expected: {expected_results}")
            print(f"   Actual: {actual_results}")
            return False
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Path Type Fix Test")
    print("=" * 60)
    
    success = test_path_type_fix()
    
    if success:
        print(f"\n📋 Test Summary: SUCCESS")
        print(f"🔧 The AttributeError: 'PosixPath' object has no attribute 'lower' is FIXED")
    else:
        print(f"\n📋 Test Summary: FAILURE")
