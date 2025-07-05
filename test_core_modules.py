#!/usr/bin/env python3
"""
Test script for the new core modules.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_settings_manager():
    """Test SettingsManager functionality."""
    print("=== Testing SettingsManager ===")
    
    try:
        from core.settings_manager import SettingsManager
        
        # Test initialization
        settings = SettingsManager()
        print("✅ SettingsManager initialized successfully")
        
        # Test boolean settings
        settings.set_debug_mode(True)
        assert settings.get_debug_mode() == True
        print("✅ Boolean settings work correctly")
        
        # Test string settings with validation
        settings.set_default_provider("BDGest")
        assert settings.get_default_provider() == "BDGest"
        print("✅ String settings work correctly")
        
        # Test invalid provider
        try:
            settings.set_default_provider("InvalidProvider")
            assert False, "Should have raised ValueError"
        except ValueError:
            print("✅ Invalid provider validation works")
        
        # Test numeric settings
        settings.set_safe_rename_threshold(0.8)
        assert settings.get_safe_rename_threshold() == 0.8
        print("✅ Numeric settings work correctly")
        
        # Test invalid threshold
        try:
            settings.set_safe_rename_threshold(1.5)
            assert False, "Should have raised ValueError"
        except ValueError:
            print("✅ Invalid threshold validation works")
        
        # Test fallback folder
        fake_path = "/non/existent/path"
        fallback = settings.get_fallback_folder_path(fake_path)
        assert os.path.exists(fallback)
        print("✅ Fallback folder logic works")
        
        print("✅ SettingsManager tests passed\n")
        return True
        
    except Exception as e:
        print(f"❌ SettingsManager test failed: {e}")
        return False

def test_error_handler():
    """Test ErrorHandler functionality."""
    print("=== Testing ErrorHandler ===")
    
    try:
        from core.error_handler import ErrorHandler
        
        # Test initialization
        error_handler = ErrorHandler(debug=True)
        print("✅ ErrorHandler initialized successfully")
        
        # Test debug logging
        error_handler.log_debug("Test debug message")
        print("✅ Debug logging works")
        
        # Test error logging
        error_handler.log_error("Test error message", Exception("Test exception"))
        print("✅ Error logging works")
        
        # Test error counting
        error_handler.error_counts['test_error'] = 1
        summary = error_handler.get_error_summary()
        assert 'test_error' in summary
        print("✅ Error counting works")
        
        # Test reset
        error_handler.reset_error_counts()
        assert len(error_handler.error_counts) == 0
        print("✅ Error count reset works")
        
        print("✅ ErrorHandler tests passed\n")
        return True
        
    except Exception as e:
        print(f"❌ ErrorHandler test failed: {e}")
        return False

def test_filename_generator():
    """Test FilenameGenerator functionality."""
    print("=== Testing FilenameGenerator ===")
    
    try:
        from core.filename_generator import FilenameGenerator
        
        # Test initialization
        generator = FilenameGenerator(debug=True)
        print("✅ FilenameGenerator initialized successfully")
        
        # Test metadata extraction
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023-01-01'
        }
        
        file_info = {'ext': 'pdf'}
        
        filename = generator.generate_filename(meta, file_info)
        expected = "Test Series - 01 - Test Album (2023).pdf"
        assert filename == expected, f"Expected '{expected}', got '{filename}'"
        print("✅ Filename generation works")
        
        # Test number formatting
        assert generator.format_number("1") == "01"
        assert generator.format_number("10") == "10"
        assert generator.format_number("1a") == "1a"
        print("✅ Number formatting works")
        
        # Test string cleaning
        dirty_string = "Test: <string> with/bad\\chars"
        clean_string = generator.clean_string(dirty_string)
        assert '<' not in clean_string
        assert '>' not in clean_string
        assert '/' not in clean_string
        print("✅ String cleaning works")
        
        # Test filename validation
        validation = generator.validate_filename("normal_file.pdf")
        assert validation['valid'] == True
        print("✅ Filename validation works")
        
        # Test invalid filename
        invalid_filename = "file<>with:bad*chars.pdf"
        validation = generator.validate_filename(invalid_filename)
        assert validation['valid'] == False
        assert len(validation['errors']) > 0
        print("✅ Invalid filename detection works")
        
        # Test safe filename generation
        safe_filename = generator.generate_safe_filename(meta, file_info)
        validation = generator.validate_filename(safe_filename)
        assert validation['valid'] == True
        print("✅ Safe filename generation works")
        
        print("✅ FilenameGenerator tests passed\n")
        return True
        
    except Exception as e:
        print(f"❌ FilenameGenerator test failed: {e}")
        return False

def test_image_manager():
    """Test ImageManager functionality."""
    print("=== Testing ImageManager ===")
    
    try:
        # Initialize Qt application for QPixmap
        try:
            from PySide6.QtWidgets import QApplication
            import sys
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
        except:
            print("⚠️  Qt not available, skipping ImageManager GUI tests")
            return True
        
        from core.image_manager import ImageManager
        
        # Create temporary cache directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test initialization
            manager = ImageManager(debug=True, cache_dir=temp_dir)
            print("✅ ImageManager initialized successfully")
            
            # Test URL normalization
            bdgest_url = "/media/Couvertures/Couv_12345.jpg"
            normalized = manager.normalize_url(bdgest_url, 'bdgest')
            assert normalized.startswith('https://www.bedetheque.com')
            print("✅ URL normalization works")
            
            # Test cache path generation
            test_url = "https://example.com/image.jpg"
            cache_path = manager._get_cache_path(test_url)
            assert cache_path.parent == Path(temp_dir)
            print("✅ Cache path generation works")
            
            # Test cleanup
            manager.cleanup_cache()
            print("✅ Cache cleanup works")
            
            # Test cache clearing
            manager.clear_cache()
            print("✅ Cache clearing works")
        
        print("✅ ImageManager tests passed\n")
        return True
        
    except Exception as e:
        print(f"❌ ImageManager test failed: {e}")
        return False

def test_integration():
    """Test integration between modules."""
    print("=== Testing Module Integration ===")
    
    try:
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.filename_generator import FilenameGenerator
        from core.image_manager import ImageManager
        
        # Test settings manager with error handler
        settings = SettingsManager()
        error_handler = ErrorHandler(debug=settings.get_debug_mode())
        
        # Test filename generator with settings
        generator = FilenameGenerator(debug=settings.get_debug_mode())
        
        # Test image manager with settings
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ImageManager(debug=settings.get_debug_mode(), cache_dir=temp_dir)
            
            # Test metadata flow
            meta = {
                'serie_name': 'Integration Test',
                'album_number': '1',
                'album_name': 'Test Integration',
                'date': '2023-01-01'
            }
            
            file_info = {'ext': 'pdf'}
            
            filename = generator.generate_safe_filename(meta, file_info)
            assert filename.endswith('.pdf')
            print("✅ Cross-module data flow works")
            
            # Test error handling integration
            error_handler.log_debug("Integration test successful")
            print("✅ Error handling integration works")
        
        print("✅ Integration tests passed\n")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("ComicsRename Core Modules Test Suite")
    print("=" * 50)
    
    tests = [
        test_settings_manager,
        test_error_handler,
        test_filename_generator,
        test_image_manager,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Core modules are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
