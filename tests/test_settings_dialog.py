#!/usr/bin/env python3
"""
Test script to verify the settings dialog shows the recursive checkbox.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QSettings

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_settings_dialog():
    """Test that the settings dialog shows the recursive checkbox"""
    
    app = QApplication(sys.argv)
    app.setApplicationName("ComicsRename")
    app.setOrganizationName("ComicsRename")
    
    # Import the dialogs
    from ui.dialogs import SettingsDialog
    from i18n import tr
    
    # Create settings
    settings = QSettings("ComicsRename", "App")
    
    # Create and show the settings dialog
    dialog = SettingsDialog(settings=settings)
    
    print("=== Settings Dialog Debug Info ===")
    print(f"Dialog has recursive_cb: {hasattr(dialog, 'recursive_cb')}")
    
    if hasattr(dialog, 'recursive_cb'):
        print(f"Recursive checkbox exists: True")
        print(f"Recursive checkbox text: {repr(tr('ui.labels.recursive_search'))}")
        print(f"Recursive checkbox is checked: {dialog.recursive_cb.isChecked()}")
        print(f"Current recursive setting: {settings.value('recursive', 'false')}")
    
    # Count form rows to see where recursive checkbox should appear
    layout = dialog.layout
    print(f"\nForm layout row count: {layout.rowCount()}")
    
    from PySide6.QtWidgets import QFormLayout
    
    for i in range(layout.rowCount()):
        label_item = layout.itemAt(i, QFormLayout.LabelRole)
        field_item = layout.itemAt(i, QFormLayout.FieldRole)
        
        label_text = ""
        field_type = ""
        
        if label_item and label_item.widget():
            label_text = label_item.widget().text()
        
        if field_item and field_item.widget():
            field_type = type(field_item.widget()).__name__
            
        print(f"Row {i}: Label='{label_text}' Field={field_type}")
    
    print("\n=== Opening Settings Dialog ===")
    print("Please check if you can see the 'Recherche récursive' checkbox in the dialog.")
    
    # Show the dialog
    dialog.exec()
    
    print("Dialog closed.")

if __name__ == "__main__":
    test_settings_dialog()
