#!/usr/bin/env python3
"""
Test script to verify the integration of new modules into the main application.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_integration():
    """Test that the new modules can be imported and used by the main application."""
    print("=== Testing Main Application Integration ===")
    
    try:
        # Test core module imports
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.filename_generator import FilenameGenerator
        from core.image_manager import ImageManager
        
        print("✅ All core modules imported successfully")
        
        # Test initialization chain
        settings = SettingsManager()
        error_handler = ErrorHandler(debug=settings.get_debug_mode())
        filename_generator = FilenameGenerator(debug=settings.get_debug_mode())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_manager = ImageManager(debug=settings.get_debug_mode(), cache_dir=temp_dir)
            
            print("✅ All modules initialized successfully")
            
            # Test a complete workflow
            meta = {
                'serie_name': 'Test Series',
                'album_number': '1',
                'album_name': 'Test Album',
                'date': '2023-01-01',
                'cover_url': 'https://example.com/cover.jpg'
            }
            
            file_info = {'ext': 'pdf', 'path': '/test/file.pdf'}
            
            # Generate filename
            filename = filename_generator.generate_safe_filename(meta, file_info)
            print(f"✅ Generated filename: {filename}")
            
            # Test error handling
            error_handler.log_debug("Integration test successful")
            print("✅ Error handling works")
            
            # Test settings
            settings.set_safe_rename_enabled(True)
            assert settings.get_safe_rename_enabled() == True
            print("✅ Settings management works")
            
            # Test image manager URL normalization
            url = '/media/cover.jpg'
            normalized = image_manager.normalize_url(url, 'bdgest')
            assert normalized.startswith('https://www.bedetheque.com')
            print("✅ Image manager integration works")
            
            print("✅ Complete integration workflow successful")
            
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """Test that existing functionality is preserved."""
    print("\n=== Testing Backward Compatibility ===")
    
    try:
        # Test that existing core modules still work
        from core import FolderRenamer, DetailsFormatter, AlbumPopulator
        
        print("✅ Existing core modules still importable")
        
        # Test initialization
        folder_renamer = FolderRenamer(debug=True)
        details_formatter = DetailsFormatter(source='BDGest', debug=True)
        
        print("✅ Existing modules still work")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

def test_file_operations():
    """Test file operations with new modules."""
    print("\n=== Testing File Operations ===")
    
    try:
        from core.filename_generator import FilenameGenerator
        from core.error_handler import ErrorHandler
        
        generator = FilenameGenerator(debug=True)
        error_handler = ErrorHandler(debug=True)
        
        # Test various metadata scenarios
        test_cases = [
            {
                'meta': {'serie_name': 'Batman', 'album_number': '1', 'album_name': 'Year One', 'date': '1987'},
                'file_info': {'ext': 'cbr'},
                'expected_pattern': 'Batman - 01 - Year One (1987).cbr'
            },
            {
                'meta': {'serie_name': 'X-Men', 'album_number': '12', 'album_name': 'Dark Phoenix', 'date': '1980-06-01'},
                'file_info': {'ext': 'pdf'},
                'expected_pattern': 'X-Men - 12 - Dark Phoenix (1980).pdf'
            },
            {
                'meta': {'serie_name': 'Series: With/Bad\\Chars', 'album_number': '1', 'album_name': 'Test<>Title', 'date': '2023'},
                'file_info': {'ext': 'pdf'},
                'expected_contains': ['Series WithBadChars', 'TestTitle']
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            filename = generator.generate_safe_filename(test_case['meta'], test_case['file_info'])
            
            if 'expected_pattern' in test_case:
                assert filename == test_case['expected_pattern'], f"Expected '{test_case['expected_pattern']}', got '{filename}'"
            elif 'expected_contains' in test_case:
                for expected in test_case['expected_contains']:
                    assert expected in filename, f"Expected '{expected}' in '{filename}'"
            
            print(f"✅ Test case {i+1} passed: {filename}")
        
        print("✅ File operations tests passed")
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("ComicsRename Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_main_integration,
        test_backward_compatibility,
        test_file_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed! Ready for main application update.")
        return True
    else:
        print("⚠️  Some integration tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
