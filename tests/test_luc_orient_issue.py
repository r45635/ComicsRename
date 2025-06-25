#!/usr/bin/env python3
"""
Test spécifique pour analyser le problème avec l'album 13 de Luc Orient
"""

import sys
import os

# Configuration de l'environnement Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bdgest_scraper_api import get_bdgest_series, get_bdgest_albums_by_series_id
from utils import load_bdgest_credentials
import json

def analyze_luc_orient_issue():
    """
    Analyse le problème spécifique avec l'album 13 de Luc Orient
    """
    print("=== Test d'analyse pour l'album Luc Orient #13 ===")
    
    # Charger les credentials
    username, password = load_bdgest_credentials()
    if not username or not password:
        print("Credentials BDGest manquants")
        return
    
    print(f"Authentification avec: {username}")
    
    # 1. Rechercher la série "Luc Orient"
    print("\n1. Recherche de la série 'Luc Orient'...")
    series_results = get_bdgest_series("Luc Orient", username, password, debug=True, verbose=False)
    
    if not series_results:
        print("Aucune série trouvée pour 'Luc Orient'")
        return
    
    print(f"Séries trouvées: {len(series_results)}")
    for i, serie in enumerate(series_results):
        print(f"  {i}: {serie}")  # Afficher toute la structure
        print(f"      Clés disponibles: {list(serie.keys()) if isinstance(serie, dict) else type(serie)}")
        if isinstance(serie, dict):
            print(f"      serie_name: {serie.get('serie_name', 'N/A')}")
            print(f"      serie_id: {serie.get('serie_id', 'N/A')}")
            print(f"      label: {serie.get('label', 'N/A')}")
            print(f"      id: {serie.get('id', 'N/A')}")
        print()
    
    # Prendre la première série trouvée
    luc_orient_series = series_results[0]
    series_id = luc_orient_series.get('serie_id') or luc_orient_series.get('id')
    series_name = luc_orient_series.get('serie_name') or luc_orient_series.get('label')
    
    print(f"\n2. Analyse de la série sélectionnée:")
    print(f"   ID: {series_id}")
    print(f"   Nom: {series_name}")
    
    if not series_id:
        print("ID de série manquant")
        return
    
    # 2. Récupérer tous les albums de la série
    print(f"\n3. Récupération des albums pour la série ID {series_id}...")
    albums = get_bdgest_albums_by_series_id(
        series_id, 
        series_name, 
        username, 
        password, 
        debug=True, 
        verbose=False,
        fetch_details=False  # D'abord sans les détails pour voir la structure de base
    )
    
    if not albums:
        print("Aucun album trouvé")
        return
    
    print(f"Albums trouvés: {len(albums)}")
    
    # 3. Analyser spécifiquement l'album 13
    print("\n4. Analyse des albums, focus sur l'album 13:")
    album_13 = None
    
    for i, album in enumerate(albums):
        album_num = album.get('album_number', 'N/A')
        album_name = album.get('album_name', 'N/A')
        print(f"  Album {i+1}: #{album_num} - {album_name}")
        
        # Chercher l'album 13
        if album_num == "13" or "13" in str(album_num):
            album_13 = album
            print(f"    *** ALBUM 13 TROUVÉ ***")
            print(f"    Structure complète:")
            for key, value in album.items():
                print(f"      {key}: {repr(value)}")
    
    if album_13:
        print(f"\n5. Analyse détaillée de l'album 13:")
        print(f"   Numéro: {album_13.get('album_number')}")
        print(f"   Nom: {album_13.get('album_name')}")
        print(f"   URL: {album_13.get('album_url')}")
        print(f"   ID: {album_13.get('album_id')}")
        
        # Récupérer les détails pour cet album spécifique
        print(f"\n6. Récupération des détails pour l'album 13...")
        albums_with_details = get_bdgest_albums_by_series_id(
            series_id, 
            series_name, 
            username, 
            password, 
            debug=True, 
            verbose=True,  # Mode verbose pour voir le HTML
            fetch_details=True
        )
        
        # Trouver l'album 13 avec détails
        for album in albums_with_details:
            if album.get('album_number') == album_13.get('album_number'):
                print(f"\n7. Détails de l'album 13:")
                details = album.get('details', {})
                print(f"   Détails trouvés: {len(details)} éléments")
                for key, value in details.items():
                    print(f"     {key}: {repr(value)}")
                break
    else:
        print("\n❌ Album 13 non trouvé dans la liste")
        print("Albums disponibles:")
        for album in albums:
            print(f"  - #{album.get('album_number')} - {album.get('album_name')}")
    
    # Sauvegarder les données pour analyse
    print(f"\n8. Sauvegarde des données pour analyse...")
    output_file = "luc_orient_analysis.json"
    analysis_data = {
        "series": luc_orient_series,
        "albums": albums,
        "album_13": album_13
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"Données sauvegardées dans: {output_file}")

if __name__ == "__main__":
    analyze_luc_orient_issue()
