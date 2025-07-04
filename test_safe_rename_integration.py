#!/usr/bin/env python3
"""
Test script to verify Safe Rename integration works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_rename_import():
    """Test that Safe Rename components can be imported"""
    try:
        from comicsFileRenamer_v3 import ComicRenamer
        print("✅ ComicRenamer imported successfully")
        
        # Test that the Safe Rename method exists
        if hasattr(ComicRenamer, '_perform_safe_rename_check'):
            print("✅ _perform_safe_rename_check method exists")
        else:
            print("❌ _perform_safe_rename_check method missing")
            return False
        
        # Test Safe Rename dependencies
        try:
            from pdf_cover_comparator_qt import PDFCoverComparator
            print("✅ Qt-native PDF comparator available")
        except ImportError:
            print("⚠️  Qt-native PDF comparator not available")
            try:
                from pdf_cover_comparator import PDFCoverComparator
                print("✅ Poppler-based PDF comparator available")
            except ImportError:
                print("❌ No PDF comparator available")
                return False
        
        try:
            from cover_comparison_dialog import CoverComparisonDialog
            print("✅ Cover comparison dialog available")
        except ImportError:
            print("❌ Cover comparison dialog not available")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error importing ComicRenamer: {e}")
        return False

def test_safe_rename_settings():
    """Test that Safe Rename settings are properly integrated"""
    try:
        from PySide6.QtCore import QSettings
        from PySide6.QtWidgets import QApplication
        
        # Create minimal app for settings
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        settings = QSettings("ComicsRename", "ComicsRename")
        
        # Test settings keys
        settings.setValue('enable_safe_rename', True)
        settings.setValue('safe_rename_threshold', 0.7)
        settings.setValue('skip_problematic_pdfs', False)
        
        # Read back
        enable_safe_rename = settings.value('enable_safe_rename', 'false') == 'true'
        threshold = float(settings.value('safe_rename_threshold', 0.7))
        skip_problematic = settings.value('skip_problematic_pdfs', 'false') == 'true'
        
        print(f"✅ Safe Rename settings working: enabled={enable_safe_rename}, threshold={threshold}, skip_problematic={skip_problematic}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Safe Rename settings: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Safe Rename Integration...")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing Safe Rename imports...")
    success &= test_safe_rename_import()
    
    print("\n2. Testing Safe Rename settings...")
    success &= test_safe_rename_settings()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All Safe Rename integration tests passed!")
        return 0
    else:
        print("❌ Some Safe Rename integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
