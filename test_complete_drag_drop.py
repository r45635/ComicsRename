#!/usr/bin/env python3
"""
Test complet du workflow drag & drop avec SafeRename
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_pdf():
    """Crée un PDF de test simple"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Créer un fichier PDF temporaire
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "test_comic.pdf")
        
        # Créer un PDF simple
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "Test Comic PDF")
        c.drawString(100, 700, "This is a test PDF for SafeRename")
        c.save()
        
        return pdf_path, temp_dir
    except ImportError:
        print("❌ reportlab not installed, creating empty PDF")
        # Créer un fichier vide avec extension .pdf
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "test_comic.pdf")
        with open(pdf_path, 'w') as f:
            f.write("fake pdf content")
        return pdf_path, temp_dir

def test_complete_workflow():
    """Test complet du workflow drag & drop"""
    
    print("=== Test Complet Drag & Drop SafeRename ===")
    
    # Créer un PDF de test
    pdf_path, temp_dir = create_test_pdf()
    print(f"PDF test créé: {pdf_path}")
    
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
        
        # Vérifier les paramètres SafeRename
        safe_rename_enabled = main_window.settings.value('safe_rename', 'false') == 'true'
        print(f"SafeRename enabled: {safe_rename_enabled}")
        
        # Simuler les métadonnées du drag & drop
        meta = {
            'serie_name': 'Test Series',
            'album_number': '1',
            'album_name': 'Test Album',
            'date': '2023',
            'cover_url': 'https://example.com/cover.jpg'
        }
        
        # Tester la logique SafeRename
        file_info = main_window.files[0]
        is_pdf = file_info['ext'].lower() == 'pdf'
        
        print(f"File: {file_info['path']}")
        print(f"Is PDF: {is_pdf}")
        print(f"SafeRename enabled: {safe_rename_enabled}")
        
        if safe_rename_enabled and is_pdf:
            print("✅ SafeRename should be called for this file")
            
            # Tester l'appel réel
            try:
                result = main_window._perform_safe_rename_check(file_info, meta)
                print(f"SafeRename result: {result}")
                
                if result:
                    print("✅ SafeRename passed, rename would proceed")
                else:
                    print("❌ SafeRename failed, rename would be cancelled")
                    
            except Exception as e:
                print(f"SafeRename error: {e}")
                
        else:
            print("❌ SafeRename would NOT be called")
            
    finally:
        # Nettoyer
        shutil.rmtree(temp_dir)
        print(f"Nettoyage terminé: {temp_dir}")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_complete_workflow()
