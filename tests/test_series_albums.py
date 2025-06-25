#!/usr/bin/env python3
"""
Test script to validate the series albums fetching functionality
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_series_albums_fetch():
    """Test the series albums fetching functionality"""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    username = os.getenv('BDGEST_USERNAME')
    password = os.getenv('BDGEST_PASSWORD')
    
    if not username or not password:
        print("❌ Erreur: Nom d'utilisateur et mot de passe requis.")
        print("   Utilisez les variables d'environnement BDGEST_USERNAME et BDGEST_PASSWORD")
        print("   ou créez un fichier .env avec:")
        print("   BDGEST_USERNAME=votre_nom_utilisateur")
        print("   BDGEST_PASSWORD=votre_mot_de_passe")
        return 1
    
    try:
        # Test 1: Search for series
        print("🔍 Test 1: Recherche de séries...")
        from bdgest_scraper_api import get_bdgest_series
        
        series_results = get_bdgest_series("spider-man", username, password, debug=True, verbose=False)
        
        if not series_results:
            print("❌ Aucune série trouvée pour 'spider-man'")
            return 1
        
        print(f"✅ {len(series_results)} série(s) trouvée(s)")
        
        # Test 2: Fetch albums for first series
        first_series = series_results[0]
        series_id = first_series.get('serie_id') or first_series.get('id')
        series_name = first_series.get('serie_name') or first_series.get('label') or first_series.get('value')
        
        if not series_id:
            print("❌ Aucun ID de série trouvé dans les résultats")
            print(f"   Données de la série: {first_series}")
            return 1
        
        print(f"🔍 Test 2: Récupération des albums pour la série '{series_name}' (ID: {series_id})...")
        
        from bdgest_scraper_api import get_bdgest_albums_by_series_id
        
        albums = get_bdgest_albums_by_series_id(series_id, series_name, username, password, debug=True, verbose=False)
        
        if not albums:
            print(f"❌ Aucun album trouvé pour la série '{series_name}' (ID: {series_id})")
            return 1
        
        print(f"✅ {len(albums)} album(s) trouvé(s) pour la série '{series_name}'")
        
        # Display first few albums
        print("\n📚 Albums trouvés:")
        for i, album in enumerate(albums[:3]):  # Show first 3 albums
            album_name = album.get('album_name', 'Nom inconnu')
            album_number = album.get('album_number', '?')
            album_date = album.get('date', 'Date inconnue')
            print(f"   {i+1}. {album_name} (#{album_number}) - {album_date}")
        
        if len(albums) > 3:
            print(f"   ... et {len(albums) - 3} autres albums")
        
        print("\n✅ Tests réussis! La fonctionnalité de récupération d'albums par série fonctionne.")
        return 0
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test de récupération d'albums par série BDGest")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    
    args = parser.parse_args()
    
    print("🧪 Test de récupération d'albums par série BDGest")
    print("=" * 50)
    
    result = test_series_albums_fetch()
    sys.exit(result)
