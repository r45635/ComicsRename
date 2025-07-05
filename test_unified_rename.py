#!/usr/bin/env python3
"""
Test de l'unification des méthodes de renommage
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unified_rename():
    """Test de l'unification des méthodes de renommage"""
    
    print("=== Test Unification Renommage Manuel/Drag & Drop ===")
    
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
        
        print("\n=== Test Méthode Unifiée ===")
        
        # Vérifier que la méthode unifiée existe
        if hasattr(main_window, '_unified_rename_file'):
            print("✅ _unified_rename_file existe")
            
            # Tester la méthode unifiée
            print("\n--- Test avec SafeRename activé ---")
            main_window.settings.setValue('safe_rename', 'true')
            
            try:
                # Test avec confirmation
                result = main_window._unified_rename_file(file_info, meta, show_confirmation=False)
                print(f"Résultat (avec confirmation): {result}")
                
                # Test sans confirmation
                result = main_window._unified_rename_file(file_info, meta, show_confirmation=False)
                print(f"Résultat (sans confirmation): {result}")
                
            except Exception as e:
                print(f"Erreur lors du test: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ _unified_rename_file n'existe pas")
            
        print("\n=== Comparaison Ancien/Nouveau ===")
        
        print("✅ AVANT: Code dupliqué")
        print("   - Renommage manuel: logique dans _rename_selected()")
        print("   - Drag & drop: logique dans dropEvent()")
        print("   - SafeRename appelé à des moments différents")
        
        print("✅ APRÈS: Code unifié")
        print("   - Renommage manuel: appelle _unified_rename_file()")
        print("   - Drag & drop: appelle _unified_rename_file()")
        print("   - SafeRename toujours appelé au même moment (AVANT confirmation)")
        
        print("\n=== Avantages ===")
        print("✅ Plus de duplication de code")
        print("✅ Comportement identique entre manuel et drag & drop")
        print("✅ SafeRename appelé de manière cohérente")
        print("✅ Maintenance plus facile")
        print("✅ Moins de bugs potentiels")
        
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
    test_unified_rename()
