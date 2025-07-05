#!/usr/bin/env python3
"""
Script de test pour vérifier le système de métadonnées du drag & drop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from ui.tables import AlbumTable

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Drag & Drop Metadata")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create album table
        self.album_table = AlbumTable(self)
        layout.addWidget(self.album_table)
        
        # Add some test data
        self.add_test_data()
    
    def add_test_data(self):
        """Add test metadata to verify the system works"""
        
        # Test metadata 1 - BDGest style
        meta1 = {
            'series': 'Test Series',
            'num': '1',
            'title': 'Test Album',
            'year': '2023',
            'album_name': 'Test Album',
            'cover_url': 'https://example.com/cover1.jpg',
            'image_url': 'https://example.com/image1.jpg',
            'parution': '2023',
            'auteurs': 'Test Author',
            'editeur': 'Test Publisher'
        }
        
        # Test metadata 2 - ComicVine style
        meta2 = {
            'series': 'Comic Series',
            'issue_number': '2',
            'title': 'Comic Issue',
            'year': '2024',
            'album_name': 'Comic Issue',
            'cover_url': 'https://example.com/cover2.jpg',
            'image_url': 'https://example.com/image2.jpg',
            'description': 'Test comic description',
            'publisher': 'Test Comic Publisher'
        }
        
        # Add items to table
        self.album_table.setRowCount(2)
        
        # Item 1
        from PySide6.QtWidgets import QTableWidgetItem
        item1 = QTableWidgetItem("Test Series - 1 - Test Album (2023)")
        item1.setData(Qt.ItemDataRole.UserRole, meta1)
        self.album_table.setItem(0, 0, item1)
        
        # Item 2
        item2 = QTableWidgetItem("Comic Series - 2 - Comic Issue (2024)")
        item2.setData(Qt.ItemDataRole.UserRole, meta2)
        self.album_table.setItem(1, 0, item2)
        
        print("[DEBUG] Test data added successfully")
        print(f"[DEBUG] Item 1 metadata: {meta1}")
        print(f"[DEBUG] Item 2 metadata: {meta2}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("\n" + "="*50)
    print("TEST DRAG & DROP METADATA")
    print("="*50)
    print("1. Essayez de glisser un des albums")
    print("2. Regardez les messages de debug dans la console")
    print("3. Vérifiez si les métadonnées sont correctement transmises")
    print("="*50 + "\n")
    
    sys.exit(app.exec())
