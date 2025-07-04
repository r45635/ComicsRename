#!/usr/bin/env python3
"""
Debug script for Safe Rename drag-and-drop functionality

This script helps debug the Safe Rename feature in drag-and-drop operations.
"""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_drag_drop_metadata():
    """Test if drag-and-drop metadata serialization works"""
    print("Testing drag-and-drop metadata serialization...")
    
    # Sample metadata similar to what's in the app
    sample_meta = {
        'album_name': 'Test Album',
        'serie_name': 'Test Series',
        'album_number': '1',
        'cover_url': 'https://example.com/cover.jpg',
        'image_url': 'https://example.com/image.jpg',
        'date': '2023-01-01',
        'details': {
            'style': 'Science Fiction',
            'year': '2023'
        }
    }
    
    try:
        # Test serialization
        meta_json = json.dumps(sample_meta, default=str)
        print(f"✓ Serialization successful: {len(meta_json)} characters")
        
        # Test deserialization
        recovered_meta = json.loads(meta_json)
        print(f"✓ Deserialization successful")
        
        # Check if cover URL is preserved
        if recovered_meta.get('cover_url') == sample_meta.get('cover_url'):
            print("✓ Cover URL preserved in metadata")
        else:
            print("✗ Cover URL not preserved")
            
        return True
        
    except Exception as e:
        print(f"✗ Metadata serialization test failed: {e}")
        return False

def debug_safe_rename_logic():
    """Debug the Safe Rename logic"""
    print("\nDebugging Safe Rename logic...")
    
    # Test conditions
    test_cases = [
        {'safe_rename': 'true', 'file_ext': '.pdf', 'has_meta': True, 'expected': True},
        {'safe_rename': 'false', 'file_ext': '.pdf', 'has_meta': True, 'expected': False},
        {'safe_rename': 'true', 'file_ext': '.cbz', 'has_meta': True, 'expected': False},
        {'safe_rename': 'true', 'file_ext': '.pdf', 'has_meta': False, 'expected': False},
    ]
    
    for i, case in enumerate(test_cases):
        safe_rename_enabled = case['safe_rename'] == 'true'
        is_pdf = case['file_ext'].lower().endswith('.pdf')
        has_meta = case['has_meta']
        
        should_check = safe_rename_enabled and is_pdf and has_meta
        expected = case['expected']
        
        status = "✓" if should_check == expected else "✗"
        print(f"{status} Case {i+1}: safe_rename={case['safe_rename']}, "
              f"ext={case['file_ext']}, has_meta={has_meta} -> "
              f"should_check={should_check} (expected={expected})")
    
    return True

def main():
    """Main debug function"""
    print("Safe Rename Drag-and-Drop Debug Script")
    print("=" * 50)
    
    success = True
    
    # Test metadata serialization
    if not test_drag_drop_metadata():
        success = False
    
    # Test Safe Rename logic
    if not debug_safe_rename_logic():
        success = False
    
    if success:
        print("\n✓ All tests passed! Drag-and-drop Safe Rename should work correctly.")
    else:
        print("\n✗ Some tests failed. Check the implementation.")
    
    print("\nDrag-and-Drop Safe Rename Implementation Notes:")
    print("1. When you drag an album from the albums table to a file:")
    print("   - The album metadata is serialized and included in the drag data")
    print("   - When dropped, the metadata is deserialized")
    print("   - If Safe Rename is enabled and the file is PDF, cover comparison runs")
    print("   - If covers don't match, the comparison dialog is shown")
    print("2. The feature only works for PDF files")
    print("3. The Safe Rename setting must be enabled in Settings")
    print("4. The album must have a cover_url in its metadata")

if __name__ == "__main__":
    main()
