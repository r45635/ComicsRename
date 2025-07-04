#!/usr/bin/env python3
"""
Test script for Quick View pan functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
    from ui.dialogs import QuickViewDialog
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test Quick View Pan Feature")
            self.setGeometry(300, 300, 400, 200)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout
            layout = QVBoxLayout(central_widget)
            
            # Button to open Quick View
            self.open_btn = QPushButton("Open PDF for Quick View")
            self.open_btn.clicked.connect(self.open_quick_view)
            layout.addWidget(self.open_btn)
            
            # Instructions
            instructions = """
            Test Instructions for Enhanced Quick View:
            
            🎯 CORE FEATURES:
            1. Click 'Open PDF for Quick View'
            2. Select any PDF file
            
            📄 NAVIGATION:
            - First/Previous/Next/Last buttons for page navigation
            - Page counter shows "Page X of Y"
            
            🔍 ZOOM & PAN:
            - Use Ctrl + mouse wheel to zoom in/out
            - Zoom In/Out buttons for manual control
            - Fit Width/Fit Page buttons for auto-sizing
            - Left-click and drag to pan around (only when zoomed)
            
            💾 EXPORT:
            - "Export PNG" button saves current page as high-quality PNG
            - Suggested filename includes page number
            - 300 DPI resolution for print quality
            
            ✨ PAN CONTROL (UPDATED):
            - Left-click + drag panning (more standard)
            - Pan only works when image is larger than window
            - Visual cursor feedback during panning
            - Cross-platform compatible (macOS/Windows)
            """
            
            from PySide6.QtWidgets import QTextEdit
            info_text = QTextEdit()
            info_text.setPlainText(instructions)
            info_text.setReadOnly(True)
            layout.addWidget(info_text)
        
        def open_quick_view(self):
            """Open file dialog and show Quick View"""
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select PDF file for Quick View",
                "",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                QuickViewDialog.show_quick_view(file_path, self)
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        sys.exit(app.exec())

except ImportError as e:
    print(f"Import error: {e}")
    print("PySide6 modules may not be installed.")
    print("Please install with: pip install PySide6")
    sys.exit(1)
