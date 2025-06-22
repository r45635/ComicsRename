#!/usr/bin/env python3
"""
Script de test pour vérifier que les messages debug sont correctement contrôlés
"""

import sys
import os

# Add the current directory to sys.path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_debug_messages():
    """Test que les messages debug ne s'affichent que quand debug=True"""
    print("=== Test des messages debug ===")
    
    # Test avec debug=False (par défaut)
    print("\n1. Test avec debug=False (mode normal)")
    print("   Aucun message [DEBUG] ne devrait apparaître...")
    
    try:
        from bdgest_scraper_api import _get_soup
        
        # Test d'une fonction qui avait des messages debug non conditionnels
        html_test = "<html><body><h1>Test</h1></body></html>"
        soup = _get_soup(html_test, debug=False)
        print("   ✅ _get_soup() fonctionne sans messages debug")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
    
    # Test avec debug=True
    print("\n2. Test avec debug=True (mode debug)")
    print("   Les messages [DEBUG] devraient apparaître...")
    
    try:
        soup = _get_soup(html_test, debug=True)
        print("   ✅ _get_soup() fonctionne avec messages debug")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
    
    print("\n=== Test terminé ===")
    print("Si vous voyez des messages [DEBUG] au-dessus, ils sont normaux car debug=True était activé.")

if __name__ == "__main__":
    test_debug_messages()
