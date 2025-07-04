#!/usr/bin/env python3
"""
Debug ComicVine cover URL issue - inspect actual metadata
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

def debug_comicvine_covers():
    """Debug ComicVine cover metadata to find the real issue"""
    
    print("🔍 Debugging ComicVine Cover URL Issue")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    from comicsFileRenamer_v3 import ComicRenamer
    
    # Enable debug mode
    settings = QSettings('ComicsRename', 'App')
    settings.setValue('debug', 'true')
    
    # Create window
    window = ComicRenamer()
    window.debug = True
    
    # Set ComicVine mode
    window.source_combo.setCurrentText('ComicVine')
    window._source = 'ComicVine'
    
    print(f"Current source: {window._source}")
    print(f"Debug mode: {window.debug}")
    
    # Let's manually create some test albums to see what happens
    print("\n🧪 Creating test albums with different cover URLs...")
    
    test_albums = [
        {
            'name': 'Test Issue #1',
            'issue_number': '1',
            'cover_url': 'https://example.com/cover1.jpg',
            'image': {'original_url': 'https://example.com/cover1.jpg'}
        },
        {
            'name': 'Test Issue #2',
            'issue_number': '2', 
            'cover_url': 'https://example.com/cover2.jpg',
            'image': {'original_url': 'https://example.com/cover2.jpg'}
        },
        {
            'name': 'Test Issue #3',
            'issue_number': '3',
            'cover_url': 'https://example.com/cover3.jpg',
            'image': {'original_url': 'https://example.com/cover3.jpg'}
        }
    ]
    
    # Clear existing albums
    window.album_table.clearContents()
    window.album_table.setRowCount(0)
    
    # Add test albums
    window.album_table.setRowCount(len(test_albums))
    for r, album in enumerate(test_albums):
        from PySide6.QtWidgets import QTableWidgetItem
        from PySide6.QtCore import Qt
        
        val = f"{album['name']}"
        itm = QTableWidgetItem(val)
        itm.setData(Qt.UserRole, album)
        window.album_table.setItem(r, 0, itm)
        
        print(f"   Album {r+1}: {album['name']}")
        print(f"   Cover URL: {album['cover_url']}")
    
    print("\n🔍 Testing album selection...")
    
    # Test selecting each album
    for r in range(len(test_albums)):
        print(f"\n--- Selecting Album {r+1} ---")
        
        # Get the metadata from the table
        itm = window.album_table.item(r, 0)
        if itm:
            meta = itm.data(Qt.UserRole)
            print(f"Raw metadata: {meta}")
            
            # Check what cover URL would be used
            img_url = meta.get('cover_url') or meta.get('image', {}).get('original_url')
            print(f"Extracted cover URL: {img_url}")
            
            # Now simulate _show_details
            try:
                print(f"Calling _show_details({r}, 0)...")
                window._show_details(r, 0)
                print("✅ _show_details completed")
            except Exception as e:
                print(f"❌ _show_details failed: {e}")
                import traceback
                traceback.print_exc()
    
    return True

if __name__ == "__main__":
    debug_comicvine_covers()
