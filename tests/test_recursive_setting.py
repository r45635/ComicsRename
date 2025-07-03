#!/usr/bin/env python3
"""
Test script to verify the recursive setting works correctly.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_recursive_setting():
    """Test that the recursive setting can be saved and loaded correctly"""
    
    # Create QApplication for QSettings to work
    app = QApplication(sys.argv)
    app.setApplicationName("ComicsRename")
    app.setOrganizationName("ComicsRename")
    
    # Test settings
    settings = QSettings("ComicsRename", "App")
    
    print("Testing recursive setting functionality...")
    
    # Test 1: Set recursive to True and verify
    settings.setValue("recursive", "true")
    value = settings.value("recursive", "false")
    print(f"Test 1 - Set to 'true': {value == 'true'}")
    
    # Test 2: Set recursive to False and verify
    settings.setValue("recursive", "false")
    value = settings.value("recursive", "false")
    print(f"Test 2 - Set to 'false': {value == 'false'}")
    
    # Test 3: Test default value when not set
    settings.remove("recursive")  # Remove the setting
    value = settings.value("recursive", "false") == "true"
    print(f"Test 3 - Default value is False: {not value}")
    
    # Test 4: Import and test dialogs
    try:
        from ui.dialogs import SettingsDialog
        print("Test 4 - SettingsDialog import: True")
        
        # Create dialog instance to check it works
        dialog = SettingsDialog(settings=settings)
        print("Test 5 - SettingsDialog creation: True")
        
        # Test that the recursive checkbox exists
        has_recursive_cb = hasattr(dialog, 'recursive_cb')
        print(f"Test 6 - Has recursive checkbox: {has_recursive_cb}")
        
        if has_recursive_cb:
            # Test that it can be set
            dialog.recursive_cb.setChecked(True)
            is_checked = dialog.recursive_cb.isChecked()
            print(f"Test 7 - Recursive checkbox can be set: {is_checked}")
        else:
            print("Test 7 - Recursive checkbox can be set: False")
            
    except ImportError as e:
        print(f"Test 4 - SettingsDialog import: False ({e})")
        print("Test 5 - SettingsDialog creation: False")
        print("Test 6 - Has recursive checkbox: False")
        print("Test 7 - Recursive checkbox can be set: False")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_recursive_setting()
