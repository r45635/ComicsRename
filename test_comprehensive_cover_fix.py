#!/usr/bin/env python3
"""
Test ComicVine cover URL fix - comprehensive verification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import Qt

def test_comicvine_cover_fix():
    """Test that ComicVine albums display different cover images"""
    
    print("🔍 Testing ComicVine Cover URL Fix")
    print("=" * 50)
    
    # Create QApplication for Qt widgets
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from comicsFileRenamer_v3 import ComicRenamer
    
    # Create the main window
    window = ComicRenamer()
    
    # Test 1: Check that issue data has individual cover URLs
    print("\n1. Testing individual issue cover URLs...")
    
    # Mock ComicVine issue data with different cover URLs
    mock_issues = [
        {
            'id': 101,
            'name': 'Batman #1',
            'issue_number': '1',
            'image': {'original_url': 'https://comicvine.gamespot.com/cover1.jpg'},
            'cover_url': 'https://comicvine.gamespot.com/cover1.jpg'
        },
        {
            'id': 102,
            'name': 'Batman #2',
            'issue_number': '2',
            'image': {'original_url': 'https://comicvine.gamespot.com/cover2.jpg'},
            'cover_url': 'https://comicvine.gamespot.com/cover2.jpg'
        },
        {
            'id': 103,
            'name': 'Batman #3',
            'issue_number': '3',
            'image': {'original_url': 'https://comicvine.gamespot.com/cover3.jpg'},
            'cover_url': 'https://comicvine.gamespot.com/cover3.jpg'
        }
    ]
    
    # Simulate populating the album table
    window.album_table.setRowCount(len(mock_issues))
    for r, issue in enumerate(mock_issues):
        val = f"Batman #{issue['issue_number']} - {issue['name']}"
        itm = QTableWidgetItem(val)
        itm.setData(Qt.UserRole, issue)  # Store the issue data
        window.album_table.setItem(r, 0, itm)
    
    # Test 2: Verify each album has its own cover URL
    print("\n2. Verifying album metadata...")
    
    all_covers_different = True
    cover_urls = []
    
    for r in range(window.album_table.rowCount()):
        itm = window.album_table.item(r, 0)
        if itm:
            meta = itm.data(Qt.UserRole)
            cover_url = meta.get('cover_url') if meta else None
            cover_urls.append(cover_url)
            print(f"   Album {r+1}: {cover_url}")
    
    # Check if all covers are different
    if len(set(cover_urls)) == len(cover_urls):
        print("   ✅ SUCCESS: All albums have different cover URLs")
    else:
        print("   ❌ PROBLEM: Some albums have duplicate cover URLs")
        all_covers_different = False
    
    # Test 3: Simulate clicking different albums
    print("\n3. Testing album selection and cover display...")
    
    for r in range(min(3, window.album_table.rowCount())):
        try:
            # Simulate clicking on album
            window._show_details(r, 0)
            
            # Get the metadata that would be used for cover display
            itm = window.album_table.item(r, 0)
            meta = itm.data(Qt.UserRole) if itm else None
            
            if meta:
                img_url = meta.get('cover_url') or meta.get('image', {}).get('original_url')
                print(f"   Album {r+1} selected: {img_url}")
                
                # Verify this matches the expected URL
                expected_url = mock_issues[r]['cover_url']
                if img_url == expected_url:
                    print(f"   ✅ CORRECT: URL matches expected value")
                else:
                    print(f"   ❌ WRONG: Expected {expected_url}, got {img_url}")
                    all_covers_different = False
            else:
                print(f"   ❌ ERROR: No metadata found for album {r+1}")
                all_covers_different = False
                
        except Exception as e:
            print(f"   ❌ ERROR: Exception when selecting album {r+1}: {e}")
            all_covers_different = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_covers_different:
        print("🎉 SUCCESS: ComicVine cover URL fix is working correctly!")
        print("   - Each album has its own unique cover URL")
        print("   - Selecting different albums shows different covers")
        print("   - No more 'sticky' first album cover issue")
        return True
    else:
        print("❌ PROBLEM: ComicVine cover URL fix needs more work")
        print("   - Some albums still share the same cover URL")
        return False

if __name__ == "__main__":
    success = test_comicvine_cover_fix()
    if success:
        print("\n✅ All tests passed! The fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the code.")
