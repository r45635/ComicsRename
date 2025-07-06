#!/usr/bin/env python3
"""
Test script for the enhanced rename confirmation dialog.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, '/Users/vincentcruvellier/Documents/GitHub/ComicsRename')

def test_enhanced_dialog():
    """Test the enhanced rename confirmation dialog."""
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from enhanced_rename_confirmation_dialog import show_enhanced_rename_confirmation
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        print("Testing Enhanced Rename Confirmation Dialog...")
        
        # Test 1: SafeRename passed case
        print("\n=== Test 1: SafeRename Passed ===")
        result1 = show_enhanced_rename_confirmation(
            parent=None,
            new_name="Blacksad - 01 - Quelque part entre les ombres (2000).pdf",
            safe_rename_passed=True,
            safe_rename_score=0.865,
            is_folder=False
        )
        print(f"User choice for SafeRename passed: {result1}")
        
        # Test 2: SafeRename not applicable (non-PDF)
        print("\n=== Test 2: SafeRename Not Applicable ===")
        result2 = show_enhanced_rename_confirmation(
            parent=None,
            new_name="Some Comic.cbz",
            safe_rename_passed=False,
            safe_rename_score=0.0,
            is_folder=False
        )
        print(f"User choice for non-PDF: {result2}")
        
        # Test 3: Folder rename (no SafeRename)
        print("\n=== Test 3: Folder Rename ===")
        result3 = show_enhanced_rename_confirmation(
            parent=None,
            new_name="Blacksad",
            safe_rename_passed=False,
            safe_rename_score=0.0,
            is_folder=True,
            old_name="Old Folder Name"
        )
        print(f"User choice for folder: {result3}")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_import():
    """Test that the dialog can be imported without errors."""
    
    try:
        from enhanced_rename_confirmation_dialog import EnhancedRenameConfirmationDialog, show_enhanced_rename_confirmation
        print("✓ Enhanced rename confirmation dialog imported successfully")
        
        # Test that it can be imported with main application
        import comicsFileRenamer_v3
        print("✓ Main application imports successfully with enhanced dialog")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Enhanced Rename Confirmation Dialog...")
    print("=" * 50)
    
    # Test import first
    import_success = test_import()
    
    if import_success:
        print("\n✅ Import tests passed!")
        
        # Ask user if they want to see the visual test
        response = input("\nDo you want to see the visual dialog test? (y/n): ")
        if response.lower() in ['y', 'yes']:
            dialog_success = test_enhanced_dialog()
            if dialog_success:
                print("\n✅ Dialog tests completed!")
            else:
                print("\n❌ Dialog tests failed!")
        else:
            print("Skipping visual tests.")
    else:
        print("\n❌ Import tests failed!")
        sys.exit(1)
