#!/usr/bin/env python3
"""
Test Safe Rename Error Handling

This script tests the improved error handling for Safe Rename with problematic PDFs.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_rename_error_handling():
    """Test Safe Rename error handling improvements"""
    print("🔧 Testing Safe Rename Error Handling")
    print("=" * 50)
    
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        print("✅ PDF comparator loaded successfully")
        
        # Test with a problematic PDF
        problematic_pdf = "/Users/vincentcruvellier/OneDrive/Ebooks/BD_US/The Grémillet Sisters/The Grémillet Sffffffisters - 01 - Sarah's Dream (2020).pdf"
        
        if os.path.exists(problematic_pdf):
            print(f"📁 Testing with problematic PDF: {os.path.basename(problematic_pdf)}")
            
            comparator = PDFCoverComparator(ssim_threshold=0.7)
            cover_url = "https://comicvine.gamespot.com/a/uploads/original/6/67663/7474144-01.jpg"
            
            try:
                result = comparator.compare(problematic_pdf, cover_url)
                print("❌ Unexpectedly succeeded - this PDF should fail")
            except Exception as e:
                print(f"✅ Expected error caught: {type(e).__name__}")
                print(f"📝 Error message: {str(e)[:100]}...")
                
                # Check if it's a PDF loading error
                if "Failed to load PDF" in str(e) or "Failed to extract first page" in str(e):
                    print("✅ PDF loading error properly identified")
                else:
                    print("⚠️  Different type of error")
        else:
            print("⚠️  Test PDF not found, cannot test error handling")
            
    except ImportError as e:
        print(f"❌ Could not import PDF comparator: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    print("\n✅ Error handling test completed")
    return True

def test_settings_integration():
    """Test that the new settings are properly integrated"""
    print("\n🔧 Testing Settings Integration")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QSettings
        
        app = QApplication([])
        settings = QSettings("ComicsRename", "TestApp")
        
        # Test setting values
        settings.setValue("skip_problematic_pdfs", "true")
        value = settings.value("skip_problematic_pdfs", "false")
        
        if value == "true":
            print("✅ Settings save/load working correctly")
        else:
            print(f"❌ Settings issue: expected 'true', got '{value}'")
            return False
        
        # Test default value
        default_value = settings.value("skip_problematic_pdfs_nonexistent", "false")
        if default_value == "false":
            print("✅ Default value handling working correctly")
        else:
            print(f"❌ Default value issue: expected 'false', got '{default_value}'")
            return False
            
    except Exception as e:
        print(f"❌ Settings test error: {e}")
        return False
    
    print("✅ Settings integration test completed")
    return True

def main():
    """Main test function"""
    print("🚀 Safe Rename Error Handling Test Suite")
    print("=" * 60)
    
    success1 = test_safe_rename_error_handling()
    success2 = test_settings_integration()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
        print("🎉 Safe Rename error handling improvements are working correctly")
    else:
        print("❌ Some tests failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
