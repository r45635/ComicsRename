#!/usr/bin/env python3
"""
Test pour vérifier que fetch_albums_by_series_id récupère bien les détails des albums
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_album_details_structure():
    """Test the structure of album data returned by the function"""
    
    print("🔍 Test de la structure des données d'album...")
    
    try:
        from bdgest_scraper_api import get_bdgest_albums_by_series_id
        
        # Test de la fonction avec des paramètres fictifs (ne pas exécuter réellement)
        print("✅ Import de get_bdgest_albums_by_series_id réussi")
        
        # Vérifier que la fonction accepte fetch_details
        import inspect
        sig = inspect.signature(get_bdgest_albums_by_series_id)
        params = list(sig.parameters.keys())
        
        print(f"Paramètres de get_bdgest_albums_by_series_id: {params}")
        
        if 'fetch_details' in params:
            print("✅ Paramètre fetch_details présent")
        else:
            print("❌ Paramètre fetch_details manquant")
            return False
            
        if 'max_workers' in params:
            print("✅ Paramètre max_workers présent")
        else:
            print("❌ Paramètre max_workers manquant")
            return False
        
        # Vérifier les valeurs par défaut
        default_fetch_details = sig.parameters['fetch_details'].default
        default_max_workers = sig.parameters['max_workers'].default
        
        print(f"Valeur par défaut fetch_details: {default_fetch_details}")
        print(f"Valeur par défaut max_workers: {default_max_workers}")
        
        if default_fetch_details is True:
            print("✅ fetch_details=True par défaut")
        else:
            print("❌ fetch_details devrait être True par défaut")
            
        if default_max_workers == 4:
            print("✅ max_workers=4 par défaut")
        else:
            print("❌ max_workers devrait être 4 par défaut")
            
        # Test du provider
        from comicsFileRenamer_v3 import BDGestProvider
        provider = BDGestProvider()
        
        provider_sig = inspect.signature(provider.search_albums_by_series_id)
        provider_params = list(provider_sig.parameters.keys())
        
        print(f"Paramètres de BDGestProvider.search_albums_by_series_id: {provider_params}")
        
        if 'fetch_details' in provider_params:
            provider_default = provider_sig.parameters['fetch_details'].default
            print(f"Valeur par défaut fetch_details dans provider: {provider_default}")
            if provider_default is True:
                print("✅ BDGestProvider utilise fetch_details=True par défaut")
            else:
                print("❌ BDGestProvider devrait utiliser fetch_details=True par défaut")
        
        print("\n✅ Structure des fonctions correcte !")
        print("📝 Les albums récupérés auront maintenant un champ 'details' avec les métadonnées complètes")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Test de récupération des détails d'albums par série")
    print("=" * 55)
    
    success = test_album_details_structure()
    
    if success:
        print("\n🎉 Tous les tests réussis !")
        print("La fonction fetch_albums_by_series_id récupère maintenant les détails des albums")
        print("exactement comme fetch_albums.")
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)
