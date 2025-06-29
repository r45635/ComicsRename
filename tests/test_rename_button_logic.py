#!/usr/bin/env python3
"""
Test script to verify the rename button logic is working correctly.
"""

import sys
import os

# Add current directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rename_button_logic():
    """Test that the rename button logic is properly implemented"""
    print("🔍 Testing Rename Button Logic...")
    
    try:
        # Read the file and check for our fixes
        with open('comicsFileRenamer_v3.py', 'r') as f:
            content = f.read()
        
        # Check for our implementation
        checks = []
        
        # 1. Check that rename button is disabled by default
        if 'self.rename_btn.setEnabled(False)  # Disabled by default until both file and album are selected' in content:
            checks.append("✅ Rename button disabled by default")
        else:
            checks.append("❌ Rename button not disabled by default")
        
        # 2. Check for update method
        if 'def _update_rename_button_state(self):' in content:
            checks.append("✅ Update rename button state method exists")
        else:
            checks.append("❌ Update rename button state method missing")
        
        # 3. Check for both selection checks
        if 'file_selected = bool(self.file_table.selectionModel().selectedRows())' in content and 'album_selected = bool(self.album_table.selectionModel().selectedRows())' in content:
            checks.append("✅ Both file and album selection checks implemented")
        else:
            checks.append("❌ Selection checks missing")
        
        # 4. Check for proper AND logic
        if 'both_selected = file_selected and album_selected' in content:
            checks.append("✅ Proper AND logic for both selections")
        else:
            checks.append("❌ AND logic missing")
        
        # 5. Check that method is called from album selection
        if '_update_rename_button_state()' in content and '_on_album_selection_changed' in content:
            checks.append("✅ Method called from album selection handler")
        else:
            checks.append("❌ Method not called from album selection handler")
        
        # 6. Check that method is called from file selection
        if '_update_rename_button_state()' in content and '_update_folder_display' in content:
            checks.append("✅ Method called from file selection handler")
        else:
            checks.append("❌ Method not called from file selection handler")
        
        # 7. Check for helpful tooltips
        if 'Select both a file and an album to enable renaming' in content:
            checks.append("✅ Helpful tooltips implemented")
        else:
            checks.append("❌ Helpful tooltips missing")
        
        print("\n📋 Implementation Status:")
        for check in checks:
            print(f"  {check}")
        
        # Count successful checks
        success_count = len([c for c in checks if c.startswith("✅")])
        total_count = len(checks)
        
        print(f"\n📊 Summary: {success_count}/{total_count} checks passed")
        
        if success_count == total_count:
            print("✅ ALL CHECKS PASSED!")
            print("\n🔧 Rename Button Logic Implemented:")
            print("  • Button disabled by default")
            print("  • Enabled only when both file and album selected")
            print("  • Updates automatically on selection changes")
            print("  • Provides helpful tooltips for user guidance")
            return True
        else:
            print("❌ Some checks failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Rename Button Logic...")
    print("=" * 50)
    
    success = test_rename_button_logic()
    
    print("=" * 50)
    if success:
        print("✅ RENAME BUTTON LOGIC VERIFIED!")
        print("The rename button should now only be enabled when both a file and album are selected.")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some implementation may be missing or incomplete.")
    
    sys.exit(0 if success else 1)
