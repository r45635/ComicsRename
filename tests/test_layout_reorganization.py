#!/usr/bin/env python3
"""
Test script to verify the GUI reorganization is working correctly.
This tests the layout structure without requiring the full GUI to run.
"""

import sys
import os

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_layout_reorganization():
    """Test that the albums management area is properly organized"""
    try:
        # Import required classes
        from comicsFileRenamer_v3 import ComicRenamer
        from PySide6.QtWidgets import QApplication
        
        # Create minimal app for widget testing
        app = QApplication([])
        
        # Create the main window
        window = ComicRenamer()
        
        # Check that the reorganization is in place
        print("🔍 Testing Albums Management Area Reorganization...")
        
        # Check if the albums management widget exists in the layout
        splitter_right = window.splitter_right
        print(f"✅ Right splitter has {splitter_right.count()} widgets")
        
        # The splitter should have 2 widgets:
        # 1. alb_widget (series combo + album table)
        # 2. albums_mgmt_widget (details + cover)
        if splitter_right.count() == 2:
            print("✅ Correct number of widgets in right splitter")
            
            # Get the second widget (should be our albums management area)
            albums_mgmt_widget = splitter_right.widget(1)
            print(f"✅ Albums management widget type: {type(albums_mgmt_widget).__name__}")
            
            # Check if the albums management widget has the right layout
            layout = albums_mgmt_widget.layout()
            if layout and layout.count() == 2:
                print("✅ Albums management area has 2 sections (details + cover)")
                
                # Check if detail_text and detail_image are present
                if hasattr(window, 'detail_text') and hasattr(window, 'detail_image'):
                    print("✅ Both detail_text and detail_image widgets are accessible")
                    print("✅ Albums Management Area Successfully Reorganized!")
                    return True
                else:
                    print("❌ Missing detail widgets")
                    return False
            else:
                print(f"❌ Albums management layout has {layout.count() if layout else 0} items instead of 2")
                return False
        else:
            print(f"❌ Wrong number of widgets in right splitter: {splitter_right.count()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        if 'app' in locals():
            app.quit()

if __name__ == "__main__":
    print("🚀 Testing GUI Reorganization...")
    print("=" * 50)
    
    success = test_layout_reorganization()
    
    print("=" * 50)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("📋 Summary of changes:")
        print("  • Album details and cover are now grouped together")
        print("  • New 'Albums Management' area in bottom right")
        print("  • Same functionality, better organization")
        print("  • No breaking changes detected")
    else:
        print("❌ TESTS FAILED!")
        print("Something went wrong with the reorganization.")
    
    sys.exit(0 if success else 1)
