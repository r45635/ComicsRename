#!/usr/bin/env python3
"""
Test de la correction pour le drag & drop SafeRename
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_corrected_drag_drop():
    """Test de la correction pour le drag & drop SafeRename"""
    
    print("=== Test Correction Drag & Drop SafeRename ===")
    
    # Créer un fichier PDF temporaire
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "test_comic.pdf")
    
    # Créer un PDF minimal
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
    
    try:
        # Importer les modules nécessaires
        from comicsFileRenamer_v3 import ComicRenamer
        from PySide6.QtWidgets import QApplication
        
        # Créer l'application
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Créer l'instance principale
        main_window = ComicRenamer()
        
        # Simuler les fichiers chargés
        file_info = {
            'path': pdf_path,
            'folder': temp_dir,
            'name': os.path.basename(pdf_path),
            'ext': 'pdf'
        }
        
        # Métadonnées pour le test
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023',
            'cover_url': 'https://www.bdgest.com/covers/cover_123.jpg'
        }
        
        print("\n=== Test Nouvelle Méthode SafeRename ===")
        
        # Tester la nouvelle méthode SafeRename
        safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
        is_pdf = file_info['ext'].lower() == 'pdf'
        
        print(f"SafeRename activé: {safe_rename_enabled}")
        print(f"Fichier PDF: {is_pdf}")
        
        if safe_rename_enabled and is_pdf:
            print("\n✅ SafeRename sera appelé")
            
            try:
                # Appel de la nouvelle méthode
                result = main_window._perform_safe_rename_check(file_info, meta)
                print(f"Résultat SafeRename: {result}")
                
                # Analyse du résultat
                if result['proceed']:
                    print("✅ Renommage autorisé")
                    print(f"   Raison: {result['reason']}")
                else:
                    print("❌ Renommage bloqué")
                    print(f"   Raison: {result['reason']}")
                    if result['user_cancelled']:
                        print("   → Utilisateur a explicitement annulé")
                    else:
                        print("   → Erreur technique")
                        
            except Exception as e:
                print(f"❌ Erreur SafeRename: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ SafeRename ne sera pas appelé")
            
        print("\n=== Test Simulation Drag & Drop ===")
        
        # Simuler le nouveau code de drag & drop
        if safe_rename_enabled and is_pdf:
            print("Code drag & drop:")
            print("result = self.main._perform_safe_rename_check(f, meta)")
            print("if not result['proceed']:")
            print("    print(f'Rename cancelled: {result[\"reason\"]}')")
            print("    if result['user_cancelled']:")
            print("        print('User explicitly cancelled')")
            print("    return")
            
            # Simulation
            result = main_window._perform_safe_rename_check(file_info, meta)
            if not result['proceed']:
                print(f"✅ Drag & drop détectera: Rename cancelled: {result['reason']}")
                if result['user_cancelled']:
                    print("✅ Drag & drop détectera: User explicitly cancelled")
                else:
                    print("✅ Drag & drop détectera: Technical error")
                print("✅ Drag & drop s'arrêtera proprement")
            else:
                print("✅ Drag & drop continuerait avec le renommage")
        else:
            print("❌ Drag & drop ne déclencherait pas SafeRename")
            
    except Exception as e:
        print(f"Erreur générale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Nettoyer
        shutil.rmtree(temp_dir)
        print(f"\nNettoyage terminé: {temp_dir}")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_corrected_drag_drop()
