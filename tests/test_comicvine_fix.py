#!/usr/bin/env python3
"""
Test rapide pour vérifier le fix de la recherche ComicVine
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from comicsFileRenamer_v3 import ComicRenamer

def test_comicvine_search():
    """Test simple de la recherche ComicVine"""
    
    app = QApplication([])
    
    # Créer l'interface
    window = ComicRenamer()
    
    # Activer le debug
    settings = QSettings('ComicsRename', 'App')
    settings.setValue('debug', 'true')
    
    # Configurer pour ComicVine
    window.source_combo.setCurrentText('ComicVine')
    window.search_bar.setText('Grémillet')
    
    print("🔍 Test de recherche ComicVine pour 'Grémillet'")
    print("📋 Debug activé, recherche en cours...")
    
    # Simuler un clic sur recherche
    try:
        window._search()
        
        # Vérifier les résultats
        if window.issues_by_series:
            print(f"✅ SUCCESS: {len(window.issues_by_series)} séries trouvées")
            for series_name in window.issues_by_series:
                album_count = len(window.issues_by_series[series_name])
                print(f"  📚 {series_name}: {album_count} albums")
        else:
            print("❌ PROBLEM: Aucune série trouvée dans l'interface")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comicvine_search()
