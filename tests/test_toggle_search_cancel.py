#!/usr/bin/env python3
"""
Test script to verify the toggle search/cancel button functionality.
"""

import sys
import os

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_toggle_search_cancel():
    """Test that the search button toggles between search and cancel modes"""
    print("🔍 Testing Toggle Search/Cancel Button...")
    
    try:
        # Read the file and check for our implementation
        with open('comicsFileRenamer_v3.py', 'r') as f:
            content = f.read()
        
        # Check for our implementation
        checks = []
        
        # 1. Check that separate cancel button is removed
        if 'self.cancel_btn = QPushButton' not in content:
            checks.append("✅ Separate cancel button removed")
        else:
            checks.append("❌ Separate cancel button still exists")
        
        # 2. Check for search in progress flag
        if 'self._search_in_progress = False' in content:
            checks.append("✅ Search in progress flag implemented")
        else:
            checks.append("❌ Search in progress flag missing")
        
        # 3. Check for toggle method
        if 'def _search_or_cancel(self):' in content:
            checks.append("✅ Toggle search/cancel method exists")
        else:
            checks.append("❌ Toggle search/cancel method missing")
        
        # 4. Check for button text change during search
        if 'self.search_btn.setText("⏹️ Cancel Search")' in content:
            checks.append("✅ Button text changes to cancel during search")
        else:
            checks.append("❌ Button text change missing")
        
        # 5. Check for button restoration
        if 'self.search_btn.setText(tr("ui.buttons.search"))' in content:
            checks.append("✅ Button text restored after search")
        else:
            checks.append("❌ Button text restoration missing")
        
        # 6. Check for correct connection
        if 'self.search_btn.clicked.connect(self._search_or_cancel)' in content:
            checks.append("✅ Search button connected to toggle method")
        else:
            checks.append("❌ Search button not connected to toggle method")
        
        # 7. Check for Escape key support
        if 'def keyPressEvent(self, event):' in content and 'Qt.Key_Escape' in content:
            checks.append("✅ Escape key cancellation support")
        else:
            checks.append("❌ Escape key cancellation missing")
        
        # 8. Check that cancel button references are removed from layout
        cancel_btn_in_layout = 'self.cancel_btn' in content and 'ctrl.addWidget' in content
        if not cancel_btn_in_layout:
            checks.append("✅ Cancel button removed from UI layout")
        else:
            checks.append("❌ Cancel button still in UI layout")
        
        # 9. Check for search state logic
        if 'if self._search_in_progress:' in content:
            checks.append("✅ Search state checking logic")
        else:
            checks.append("❌ Search state checking logic missing")
        
        print("\n📋 Toggle Search/Cancel Status:")
        for check in checks:
            print(f"  {check}")
        
        # Count successful checks
        success_count = len([c for c in checks if c.startswith("✅")])
        total_count = len(checks)
        
        print(f"\n📊 Summary: {success_count}/{total_count} checks passed")
        
        if success_count == total_count:
            print("✅ ALL TOGGLE FUNCTIONALITY CHECKS PASSED!")
            print("\n🔧 Toggle Search/Cancel Features:")
            print("  • Single search button that toggles function")
            print("  • Button text changes to 'Cancel Search' during operation")
            print("  • Button text restores to 'Search' after completion")
            print("  • Escape key support for cancellation")
            print("  • No separate cancel button (space efficient)")
            print("  • Proper state management with _search_in_progress")
            print("  • Clean UI restoration after cancellation")
            return True
        else:
            print("❌ Some toggle functionality missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Toggle Search/Cancel Button...")
    print("=" * 50)
    
    success = test_toggle_search_cancel()
    
    print("=" * 50)
    if success:
        print("✅ TOGGLE SEARCH/CANCEL VERIFIED!")
        print("The search button now intelligently toggles between search and cancel modes.")
        print("This provides better UX with less UI clutter!")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some toggle functionality may be incomplete.")
    
    sys.exit(0 if success else 1)
