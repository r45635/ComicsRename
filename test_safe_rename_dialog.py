#!/usr/bin/env python3
"""
Test pour vérifier si la boîte de dialogue SafeRename s'affiche
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_rename_dialog():
    """Test pour vérifier l'affichage de la boîte de dialogue SafeRename"""
    
    print("=== Test Boîte de Dialogue SafeRename ===")
    
    # Créer un fichier PDF temporaire
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "test_comic.pdf")
    
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
        
        # Métadonnées avec une URL d'image valide (locale)
        # Créer une image temporaire
        from PIL import Image
        
        # Créer une image de test
        img = Image.new('RGB', (100, 100), color='red')
        img_path = os.path.join(temp_dir, "test_cover.jpg")
        img.save(img_path)
        
        # Utiliser une URL locale
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023',
            'cover_url': f'file://{img_path}'
        }
        
        print(f"Image cover créée: {img_path}")
        print(f"Cover URL: {meta['cover_url']}")
        
        # Tester le SafeRename
        print("\n=== Test SafeRename avec image locale ===")
        
        safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
        is_pdf = file_info['ext'].lower() == 'pdf'
        
        print(f"SafeRename enabled: {safe_rename_enabled}")
        print(f"File is PDF: {is_pdf}")
        
        if safe_rename_enabled and is_pdf:
            try:
                print("Appel de SafeRename...")
                result = main_window._perform_safe_rename_check(file_info, meta)
                print(f"Résultat SafeRename: {result}")
                
                if result:
                    print("✅ SafeRename: Utilisateur a accepté ou correspondance trouvée")
                else:
                    print("❌ SafeRename: Utilisateur a refusé ou erreur")
                    
            except Exception as e:
                print(f"Erreur SafeRename: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ SafeRename ne sera pas appelé")
            
    except ImportError as e:
        print(f"Erreur d'import: {e}")
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
    test_safe_rename_dialog()
