#!/usr/bin/env python3
"""
Test script to verify drag & drop SafeRename functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import QSettings, QMimeData, QByteArray, Qt, QPoint
from PySide6.QtGui import QDropEvent
import json

# Mock the main application
class MockComicRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('ComicsRename', 'Test')
        self.settings.setValue('safe_rename', 'true')  # Enable SafeRename
        self.debug = True
        self.files = [
            {
                'path': '/path/to/test.pdf',
                'folder': '/path/to/',
                'name': 'test.pdf',
                'ext': 'pdf'
            }
        ]
    
    def _perform_safe_rename_check(self, file_info, meta):
        """Mock SafeRename check"""
        print(f"[TEST] _perform_safe_rename_check called!")
        print(f"[TEST] File: {file_info['path']}")
        print(f"[TEST] Meta: {meta}")
        
        # Simulate the dialog - for testing, we'll just return True
        return True
    
    def _load_files(self, folder):
        """Mock file loading"""
        print(f"[TEST] _load_files called for folder: {folder}")


def test_drag_drop_safe_rename():
    """Test if drag & drop triggers SafeRename"""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    print("=== Testing Drag & Drop SafeRename ===")
    
    # Create mock objects
    mock_main = MockComicRenamer()
    
    # Import the actual FileTable
    from ui.tables import FileTable
    
    # Create a FileTable with our mock main
    table = FileTable(parent=mock_main)
    table.main = mock_main
    
    # Add a row to the table so drop target is valid
    table.setRowCount(1)
    table.setColumnCount(4)
    
    # Create test metadata (like what would come from drag)
    test_meta = {
        'serie_name': 'Test Series',
        'album_number': '1',
        'album_name': 'Test Album',
        'date': '2023',
        'cover_url': 'https://example.com/cover.jpg'
    }
    
    # Create mime data
    mime_data = QMimeData()
    json_data = json.dumps(test_meta)
    mime_data.setData('application/x-comic-meta', QByteArray(json_data.encode()))
    
    # Create a mock drop event
    drop_event = QDropEvent(
        QPoint(10, 10),  # Position
        Qt.DropAction.CopyAction,  # Action
        mime_data,  # Mime data
        Qt.MouseButton.LeftButton,  # Buttons
        Qt.KeyboardModifier.NoModifier  # Modifiers
    )
    
    print("Simulating drop event...")
    
    # Test if the drop event would trigger SafeRename
    try:
        # This should trigger the SafeRename check
        table.dropEvent(drop_event)
        print("✅ Drop event processed successfully")
    except Exception as e:
        print(f"❌ Drop event failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_drag_drop_safe_rename()
