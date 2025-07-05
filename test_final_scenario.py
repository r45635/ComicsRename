#!/usr/bin/env python3
"""
Test final pour reproduire le problème utilisateur
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_final_scenario():
    """Test final pour reproduire le problème utilisateur"""
    
    print("=== Test Final - Problème Utilisateur ===")
    print("Objectif: Comprendre pourquoi le drag & drop ne déclenche pas SafeRename")
    print()
    
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
        
        # Métadonnées comme celles qui viendraient d'un drag & drop réel
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023',
            'cover_url': 'https://www.bdgest.com/covers/cover_123.jpg'  # URL réaliste
        }
        
        print("=== Analyse du Problème ===")
        
        # Vérifier tous les éléments
        safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
        is_pdf = file_info['ext'].lower() == 'pdf'
        has_cover_url = bool(meta.get('cover_url'))
        
        print(f"1. SafeRename activé dans les paramètres: {safe_rename_enabled}")
        print(f"2. Le fichier est un PDF: {is_pdf}")
        print(f"3. URL de couverture disponible: {has_cover_url}")
        print(f"4. URL de couverture: {meta.get('cover_url', 'None')}")
        
        condition = safe_rename_enabled and is_pdf
        print(f"5. Condition SafeRename (activé ET PDF): {condition}")
        
        if condition:
            print("\n✅ TOUTES LES CONDITIONS SONT REMPLIES")
            print("SafeRename DEVRAIT être appelé!")
            
            # Test réel
            try:
                print("\n=== Exécution SafeRename ===")
                result = main_window._perform_safe_rename_check(file_info, meta)
                print(f"Résultat SafeRename: {result}")
                
                if result:
                    print("✅ SafeRename: Renommage autorisé")
                else:
                    print("❌ SafeRename: Renommage bloqué")
                    
            except Exception as e:
                print(f"❌ Erreur SafeRename: {e}")
                
        else:
            print("\n❌ CONDITIONS NON REMPLIES")
            print("SafeRename ne sera pas appelé")
            if not safe_rename_enabled:
                print("   - SafeRename n'est pas activé")
            if not is_pdf:
                print("   - Le fichier n'est pas un PDF")
        
        # Analyse spécifique du drag & drop
        print("\n=== Analyse Drag & Drop ===")
        print("Code dans ui/tables.py, ligne ~185:")
        print("if safe_rename_enabled and is_pdf:")
        print("    proceed = self.main._perform_safe_rename_check(f, meta)")
        print("    if not proceed:")
        print("        return  # User cancelled")
        
        print(f"\nDans le drag & drop:")
        print(f"- safe_rename_enabled: {safe_rename_enabled}")
        print(f"- is_pdf: {is_pdf}")
        print(f"- Appel SafeRename: {condition}")
        
        # Hypothèses sur le problème
        print("\n=== Hypothèses sur le Problème ===")
        
        if not safe_rename_enabled:
            print("❌ PROBLÈME IDENTIFIÉ: SafeRename n'est pas activé dans les paramètres")
            print("   Solution: Activer SafeRename dans les paramètres")
        elif not has_cover_url:
            print("❌ PROBLÈME IDENTIFIÉ: Pas d'URL de couverture dans les métadonnées")
            print("   Solution: Vérifier que les métadonnées contiennent une URL de couverture")
        else:
            print("✅ Configuration correcte")
            print("   Le problème pourrait être:")
            print("   1. Boîte de dialogue masquée ou ne s'affiche pas")
            print("   2. Erreur réseau lors du téléchargement de l'image")
            print("   3. Erreur lors de la lecture du PDF")
            print("   4. L'utilisateur ne voit pas la boîte de dialogue")
            
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
    test_final_scenario()
