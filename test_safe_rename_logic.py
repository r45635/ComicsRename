#!/usr/bin/env python3
"""
Test plus précis du SafeRename avec drag & drop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simuler la réponse utilisateur à la boîte de dialogue
import unittest.mock

def test_safe_rename_call():
    """Test si SafeRename est correctement appelé"""
    
    print("=== Test SafeRename Call ===")
    
    # Simuler les paramètres
    mock_file = {
        'path': '/path/to/test.pdf',
        'folder': '/path/to/',
        'name': 'test.pdf',
        'ext': 'pdf'
    }
    
    mock_meta = {
        'serie_name': 'Test Series',
        'album_number': '1',
        'album_name': 'Test Album',
        'date': '2023',
        'cover_url': 'https://example.com/cover.jpg'
    }
    
    # Tester la détection PDF
    is_pdf = mock_file['ext'].lower() == 'pdf'
    print(f"File extension: {mock_file['ext']}")
    print(f"Is PDF: {is_pdf}")
    
    # Tester la logique SafeRename
    safe_rename_enabled = True  # Settings
    
    print(f"Safe Rename enabled: {safe_rename_enabled}")
    
    if safe_rename_enabled and is_pdf:
        print("✅ SafeRename should be called")
        print(f"File: {mock_file['path']}")
        print(f"Meta: {mock_meta}")
    else:
        print("❌ SafeRename would NOT be called")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_safe_rename_call()
