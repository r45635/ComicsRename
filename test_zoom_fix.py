#!/usr/bin/env python3
"""
Test script for Quick View zoom functionality.
This script will open a PDF in Quick View to test zoom controls.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestQuickView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Quick View Zoom")
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout(self)
        
        # Button to open Quick View
        self.open_btn = QPushButton("Open PDF for Quick View")
        self.open_btn.clicked.connect(self.open_quick_view)
        layout.addWidget(self.open_btn)
        
        # Instructions
        instructions = """
Test Instructions for Quick View Zoom:

1. Click 'Open PDF for Quick View'
2. Select any PDF file
3. Test zoom controls:
   - Ctrl + Mouse Wheel: Zoom in/out
   - Zoom In/Out buttons
   - Fit Width/Fit Page buttons
4. Test panning:
   - Left-click + drag when zoomed in
        """
        
        from PySide6.QtWidgets import QTextEdit
        text_widget = QTextEdit()
        text_widget.setPlainText(instructions)
        text_widget.setReadOnly(True)
        text_widget.setMaximumHeight(200)
        layout.addWidget(text_widget)

    def open_quick_view(self):
        """Open file dialog and show Quick View"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF file for Quick View",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                from ui.quick_view import QuickViewDialog
                dialog = QuickViewDialog(self, file_path)
                dialog.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open Quick View: {e}")


def main():
    app = QApplication(sys.argv)
    window = TestQuickView()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
