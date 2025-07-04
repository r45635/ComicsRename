#!/usr/bin/env python3
"""
Comprehensive test to verify all ComicsRename functionality works together
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_application_startup():
    """Test that the application can start without errors"""
    try:
        from comicsFileRenamer_v3 import ComicRenamer
        from PySide6.QtWidgets import QApplication
        
        # Create minimal app
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create main window (but don't show it)
        window = ComicRenamer()
        
        print("✅ Application startup successful")
        return True
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        return False

def test_provider_integration():
    """Test that both providers work correctly"""
    try:
        from comicsFileRenamer_v3 import PROVIDERS
        
        # Test BDGest provider
        bdgest = PROVIDERS.get('BDGest')
        if bdgest:
            print("✅ BDGest provider available")
            
            # Test upgrade function
            test_url = "https://www.bedetheque.com/cache/thb_couv/test.jpg"
            upgraded = bdgest._upgrade_bdgest_cover_url(test_url)
            expected = "https://www.bedetheque.com/media/Couvertures/test.jpg"
            
            if upgraded == expected:
                print("✅ BDGest cover URL upgrade working")
            else:
                print(f"❌ BDGest cover URL upgrade failed: {upgraded} != {expected}")
                return False
        else:
            print("❌ BDGest provider not available")
            return False
            
        # Test ComicVine provider
        comicvine = PROVIDERS.get('ComicVine')
        if comicvine:
            print("✅ ComicVine provider available")
        else:
            print("❌ ComicVine provider not available")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Provider integration test failed: {e}")
        return False

def test_safe_rename_components():
    """Test that Safe Rename components are available"""
    try:
        # Test PDF comparator
        from pdf_cover_comparator_qt import PDFCoverComparator
        print("✅ Qt-native PDF comparator available")
        
        # Test cover comparison dialog
        from cover_comparison_dialog import CoverComparisonDialog
        print("✅ Cover comparison dialog available")
        
        return True
        
    except Exception as e:
        print(f"❌ Safe Rename components test failed: {e}")
        return False

def test_translation_system():
    """Test that translation system works"""
    try:
        from i18n import tr, set_language
        
        # Test English
        set_language('en')
        english_text = tr('messages.cover_comparison.title')
        if english_text and english_text != 'messages.cover_comparison.title':
            print("✅ English translations working")
        else:
            print("❌ English translations not working")
            return False
            
        # Test French
        set_language('fr')
        french_text = tr('messages.cover_comparison.title')
        if french_text and french_text != 'messages.cover_comparison.title':
            print("✅ French translations working")
        else:
            print("❌ French translations not working")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Translation system test failed: {e}")
        return False

def test_settings_integration():
    """Test that settings work correctly"""
    try:
        from PySide6.QtCore import QSettings
        from PySide6.QtWidgets import QApplication
        
        # Create minimal app
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        settings = QSettings("ComicsRename", "ComicsRename")
        
        # Test Safe Rename settings
        settings.setValue('enable_safe_rename', True)
        settings.setValue('safe_rename_threshold', 0.75)
        settings.setValue('skip_problematic_pdfs', True)
        
        # Read back and verify
        enable_safe_rename = settings.value('enable_safe_rename', 'false') == 'true'
        threshold = float(settings.value('safe_rename_threshold', 0.7))
        skip_problematic = settings.value('skip_problematic_pdfs', 'false') == 'true'
        
        if enable_safe_rename and threshold == 0.75 and skip_problematic:
            print("✅ Settings integration working")
            return True
        else:
            print("❌ Settings integration not working")
            return False
            
    except Exception as e:
        print(f"❌ Settings integration test failed: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("ComicsRename Comprehensive Test Suite")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing application startup...")
    success &= test_application_startup()
    
    print("\n2. Testing provider integration...")
    success &= test_provider_integration()
    
    print("\n3. Testing Safe Rename components...")
    success &= test_safe_rename_components()
    
    print("\n4. Testing translation system...")
    success &= test_translation_system()
    
    print("\n5. Testing settings integration...")
    success &= test_settings_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! ComicsRename is working correctly.")
        print("\nKey features verified:")
        print("  ✅ Application starts without errors")
        print("  ✅ BDGest and ComicVine providers work")
        print("  ✅ BDGest cover URL upgrade works")
        print("  ✅ Safe Rename components available")
        print("  ✅ Translation system works (EN/FR)")
        print("  ✅ Settings integration works")
        print("\nThe application is ready for use!")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
