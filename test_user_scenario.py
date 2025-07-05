#!/usr/bin/env python3
"""
Test de simulation exacte du problème utilisateur
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_user_scenario():
    """Simule exactement le scénario utilisateur"""
    
    print("=== Simulation du Scénario Utilisateur ===")
    print("1. Renommage manuel: SafeRename fonctionne ✅")
    print("2. Drag & drop: SafeRename ne fonctionne pas ❌")
    print()
    
    # Créer un fichier PDF temporaire
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "test_comic.pdf")
    
    # Créer un PDF simple mais valide
    try:
        # Créer un PDF minimal mais valide
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
188
%%EOF"""
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"PDF créé: {pdf_path}")
        
    except Exception as e:
        print(f"Erreur création PDF: {e}")
        return
    
    try:
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
        
        # Simuler les fichiers chargés
        main_window.files = [{
            'path': pdf_path,
            'folder': temp_dir,
            'name': os.path.basename(pdf_path),
            'ext': 'pdf'
        }]
        
        # Métadonnées pour le test
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023',
            'cover_url': 'https://example.com/cover.jpg'
        }
        
        print("=== Test Renommage Manuel ===")
        
        # Test 1: Renommage manuel (comme dans la fonction rename_selected)
        file_info = main_window.files[0]
        is_pdf = file_info['ext'].lower() == 'pdf'
        safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
        
        print(f"SafeRename enabled: {safe_rename_enabled}")
        print(f"File is PDF: {is_pdf}")
        
        if safe_rename_enabled and is_pdf:
            print("✅ SafeRename sera appelé pour renommage manuel")
            try:
                result = main_window._perform_safe_rename_check(file_info, meta)
                print(f"Résultat SafeRename: {result}")
            except Exception as e:
                print(f"Erreur SafeRename: {e}")
        else:
            print("❌ SafeRename ne sera PAS appelé")
            
        print()
        print("=== Test Drag & Drop ===")
        
        # Test 2: Drag & Drop (comme dans dropEvent)
        # Simuler exactement le même processus
        f = main_window.files[0]
        
        # Mêmes vérifications que dans le drag & drop
        is_pdf_dd = f['ext'].lower() == 'pdf' or f['path'].lower().endswith('.pdf')
        safe_rename_enabled_dd = main_window.settings.value('safe_rename', 'false') == 'true'
        
        print(f"SafeRename enabled (DD): {safe_rename_enabled_dd}")
        print(f"File is PDF (DD): {is_pdf_dd}")
        print(f"File extension: '{f['ext']}'")
        print(f"File path: '{f['path']}'")
        
        if safe_rename_enabled_dd and is_pdf_dd:
            print("✅ SafeRename sera appelé pour drag & drop")
            try:
                result = main_window._perform_safe_rename_check(f, meta)
                print(f"Résultat SafeRename: {result}")
            except Exception as e:
                print(f"Erreur SafeRename: {e}")
        else:
            print("❌ SafeRename ne sera PAS appelé")
            
        # Comparaison des deux approches
        print()
        print("=== Comparaison ===")
        print(f"Manuel - SafeRename: {safe_rename_enabled and is_pdf}")
        print(f"Drag & Drop - SafeRename: {safe_rename_enabled_dd and is_pdf_dd}")
        
        if (safe_rename_enabled and is_pdf) == (safe_rename_enabled_dd and is_pdf_dd):
            print("✅ Les deux approches sont cohérentes")
        else:
            print("❌ INCOHÉRENCE entre les deux approches!")
            
    finally:
        # Nettoyer
        shutil.rmtree(temp_dir)
        print(f"\nNettoyage terminé: {temp_dir}")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_user_scenario()
