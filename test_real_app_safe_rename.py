#!/usr/bin/env python3
"""
Test interactif du drag & drop avec SafeRename
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_drag_drop_real_app():
    """Test avec la vraie application"""
    
    print("=== Test avec l'application réelle ===")
    
    # Importer les modules nécessaires
    from comicsFileRenamer_v3 import ComicRenamer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings
    
    # Créer l'application
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Créer l'instance principale
    main_window = ComicRenamer()
    
    # Vérifier les paramètres SafeRename
    safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
    print(f"SafeRename enabled in settings: {safe_rename_enabled}")
    
    # Vérifier que la méthode SafeRename existe
    if hasattr(main_window, '_perform_safe_rename_check'):
        print("✅ _perform_safe_rename_check method exists")
    else:
        print("❌ _perform_safe_rename_check method missing")
    
    # Tester la méthode SafeRename avec des données fictives
    if hasattr(main_window, '_perform_safe_rename_check'):
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
        
        print("Testing SafeRename method...")
        try:
            # Cela devrait déclencher le SafeRename
            result = main_window._perform_safe_rename_check(mock_file, mock_meta)
            print(f"SafeRename result: {result}")
        except Exception as e:
            print(f"SafeRename error: {e}")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_drag_drop_real_app()
