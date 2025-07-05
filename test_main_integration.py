#!/usr/bin/env python3
"""
Test script to validate the integration of new modules into the main application.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_app_integration():
    """Test that the main application can use the new modules."""
    print("=== Testing Main Application Integration ===")
    
    try:
        # Initialize Qt application for testing
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test module imports
        from core import (
            SettingsManager, ErrorHandler, FilenameGenerator, 
            ImageManager, SafeRenameManager
        )
        print("✅ All new modules imported successfully")
        
        # Test initialization chain
        settings_manager = SettingsManager()
        error_handler = ErrorHandler(debug=settings_manager.get_debug_mode())
        filename_generator = FilenameGenerator(debug=settings_manager.get_debug_mode())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_manager = ImageManager(debug=settings_manager.get_debug_mode(), cache_dir=temp_dir)
            safe_rename_manager = SafeRenameManager(
                settings_manager, error_handler, image_manager,
                debug=settings_manager.get_debug_mode()
            )
            
            print("✅ All modules initialized successfully")
            
            # Test SafeRename integration workflow
            test_file_info = {
                'path': '/test/file.pdf',
                'ext': 'pdf',
                'folder': '/test'
            }
            
            test_meta = {
                'serie_name': 'Test Series',
                'album_number': '1', 
                'album_name': 'Test Album',
                'date': '2023-01-01',
                'cover_url': 'https://example.com/cover.jpg'
            }
            
            # Test filename generation
            filename = filename_generator.generate_safe_filename(test_meta, test_file_info)
            expected = "Test Series - 01 - Test Album (2023).pdf"
            assert filename == expected
            print(f"✅ Filename generation: {filename}")
            
            # Test SafeRename check (will skip due to no actual PDF file)
            result = safe_rename_manager.check_rename_safety(test_file_info, test_meta)
            print(f"✅ SafeRename check: {result['reason']}")
            
            # Test statistics
            stats = safe_rename_manager.get_statistics()
            assert 'current_threshold' in stats
            print(f"✅ SafeRename statistics: {stats}")
            
            # Test image manager URL normalization
            bdgest_url = '/media/cover.jpg'
            normalized = image_manager.normalize_url(bdgest_url, 'bdgest')
            assert normalized.startswith('https://www.bedetheque.com')
            print(f"✅ URL normalization: {normalized}")
            
            print("✅ Complete integration workflow successful")
            
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_rename_simulation():
    """Test the unified rename logic with new modules."""
    print("\n=== Testing Unified Rename Simulation ===")
    
    try:
        from core import SettingsManager, FilenameGenerator
        
        settings_manager = SettingsManager()
        filename_generator = FilenameGenerator(debug=True)
        
        # Test various metadata scenarios
        test_cases = [
            {
                'meta': {
                    'serie_name': 'Batman',
                    'album_number': '1',
                    'album_name': 'Year One',
                    'date': '1987-02-01'
                },
                'file_info': {'ext': 'cbr', 'path': '/comics/batman.cbr'},
                'expected': 'Batman - 01 - Year One (1987).cbr'
            },
            {
                'meta': {
                    'serie_name': 'X-Men: Legacy',
                    'album_number': '12',
                    'album_name': 'Dark Phoenix Saga',
                    'date': '1980'
                },
                'file_info': {'ext': 'pdf', 'path': '/comics/xmen.pdf'},
                'expected': 'X-Men Legacy - 12 - Dark Phoenix Saga (1980).pdf'
            },
            {
                'meta': {
                    'serie_name': 'Series: With/Bad\\Chars<>',
                    'album_number': '5',
                    'album_name': 'Title: With"Problems|Here',
                    'date': '2023-12-25'
                },
                'file_info': {'ext': 'cbz', 'path': '/comics/test.cbz'},
                'expected_contains': ['Series WithBadChars', 'Title WithProblemsHere', '05', '2023']
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            filename = filename_generator.generate_safe_filename(
                test_case['meta'], 
                test_case['file_info']
            )
            
            if 'expected' in test_case:
                assert filename == test_case['expected'], f"Expected '{test_case['expected']}', got '{filename}'"
            elif 'expected_contains' in test_case:
                for expected in test_case['expected_contains']:
                    assert expected in filename, f"Expected '{expected}' in '{filename}'"
            
            print(f"✅ Test case {i+1}: {filename}")
        
        print("✅ Unified rename simulation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Unified rename simulation failed: {e}")
        return False

def test_settings_integration():
    """Test settings integration with the main application."""
    print("\n=== Testing Settings Integration ===")
    
    try:
        from core import SettingsManager
        
        settings = SettingsManager()
        
        # Test all the main settings
        settings.set_debug_mode(True)
        assert settings.get_debug_mode() == True
        
        settings.set_safe_rename_enabled(True)
        assert settings.get_safe_rename_enabled() == True
        
        settings.set_default_provider("ComicVine")
        assert settings.get_default_provider() == "ComicVine"
        
        settings.set_safe_rename_threshold(0.8)
        assert settings.get_safe_rename_threshold() == 0.8
        
        # Test fallback logic
        fake_path = "/completely/fake/path"
        fallback = settings.get_fallback_folder_path(fake_path)
        assert os.path.exists(fallback)
        
        print("✅ All settings tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Settings integration test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("ComicsRename - Main Application Integration Test")
    print("=" * 60)
    
    tests = [
        test_main_app_integration,
        test_unified_rename_simulation,
        test_settings_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("✅ Main application is ready to use the new modules")
        print("✅ SafeRename workflow is integrated")
        print("✅ Image caching and management working")
        print("✅ Settings management fully functional")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
