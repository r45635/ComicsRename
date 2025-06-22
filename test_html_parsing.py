#!/usr/bin/env python3
"""
Test pour analyser le HTML brut de l'album 13 de Luc Orient et améliorer le parsing
"""

import sys
import os
import re

# Configuration de l'environnement Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bdgest_scraper_api import fetch_albums_by_series_id, login_bdgest, get_csrf_token
from utils import load_bdgest_credentials
import requests
from bs4 import BeautifulSoup

def analyze_html_structure():
    """
    Analyse la structure HTML brute pour comprendre le problème avec l'album 13
    """
    print("=== Analyse de la structure HTML de l'album Luc Orient #13 ===")
    
    # Charger les credentials
    username, password = load_bdgest_credentials()
    if not username or not password:
        print("Credentials BDGest manquants")
        return
    
    # Créer une session et se connecter
    session = requests.Session()
    
    # Login
    csrf_token = get_csrf_token(session, debug=True)
    if not csrf_token:
        print("Impossible d'obtenir le token CSRF")
        return
        
    login_success = login_bdgest(session, username, password, debug=True)
    if not login_success:
        print("Échec de l'authentification")
        return
    
    # URL pour la série Luc Orient (ID 195)
    series_id = "195"
    series_name = "Luc Orient"
    encoded_series_name = requests.utils.quote(series_name)
    url = f"https://online.bdgest.com/albums/import?ids={series_id}&s={encoded_series_name}&t=&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
    
    print(f"Récupération de l'URL: {url}")
    
    resp = session.get(url, timeout=10)
    if resp.status_code != 200:
        print(f"Erreur HTTP: {resp.status_code}")
        return
    
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", class_="table-albums-mid")
    
    if not table:
        print("Table des albums non trouvée")
        return
    
    print(f"Table trouvée, analyse des lignes...")
    
    for i, tr in enumerate(table.find_all("tr", class_="clic")):
        album_id = tr.get("id", "").replace("ID", "")
        tds = tr.find_all("td")
        
        if len(tds) < 4:
            continue
        
        # Analyser le contenu de la cellule titre (colonne 2)
        titre_td = tds[2]
        
        print(f"\n--- Album {i+1} (ID: {album_id}) ---")
        print(f"HTML brut de la cellule titre:")
        print(titre_td.prettify())
        
        # Extraire les éléments
        serie_tag = titre_td.find("span", class_="serie")
        titre_tag = titre_td.find("span", class_="titre")
        
        print(f"Span série: {serie_tag}")
        print(f"Span titre: {titre_tag}")
        
        if titre_tag:
            titre_raw = titre_tag.get_text(" ", strip=True)
            print(f"Titre brut: {repr(titre_raw)}")
            
            # Test du regex actuel
            m = re.match(r"-?\s*([A-Z0-9\-]+)\s*-\s*(.+)", titre_raw)
            if m:
                print(f"Regex match - Numéro: '{m.group(1)}', Titre: '{m.group(2)}'")
            else:
                print("Regex ne match pas!")
                
                # Test d'autres patterns
                patterns = [
                    r"(\d+)\s*-\s*(.+)",  # Simple numéro-titre
                    r"-?\s*(\d+)\s*['-]\s*-\s*(.+)",  # Avec quotes ou tirets
                    r".*?(\d+).*?-\s*(.+)",  # Numéro quelque part puis tiret
                ]
                
                for pattern in patterns:
                    m2 = re.search(pattern, titre_raw, re.DOTALL)
                    if m2:
                        print(f"Pattern alternatif '{pattern}' match - Numéro: '{m2.group(1)}', Titre: '{m2.group(2)}'")
                        break
                
                # Analyser character par character
                print(f"Analyse caractère par caractère:")
                for j, char in enumerate(titre_raw):
                    print(f"  {j}: {repr(char)} ({ord(char)})")
                    if j > 20:  # Limiter l'affichage
                        print("  ...")
                        break
        
        # Afficher seulement les premiers albums et l'album suspect (ID 733)
        if i > 5 and album_id != "733":
            continue
        
        # S'arrêter après l'album problématique
        if album_id == "733":
            print("\n*** ALBUM PROBLÉMATIQUE TROUVÉ (ID 733) ***")
            break

def test_improved_parsing():
    """
    Test d'un parsing amélioré pour gérer l'album 13
    """
    print("\n=== Test de parsing amélioré ===")
    
    # Exemples de titres problématiques
    test_cases = [
        "-13 ' -\r\n                                L'enclume de la foudre",
        "1 - Les dragons de feu",
        "2 - Les soleils de glace",
        "13 - L'enclume de la foudre",
        "-13 - L'enclume de la foudre",
    ]
    
    def improved_parse_title(titre_raw):
        """
        Parsing amélioré pour gérer les cas spéciaux
        """
        if not titre_raw:
            return "", ""
        
        # Nettoyer les retours à la ligne et espaces multiples
        titre_clean = re.sub(r'\s+', ' ', titre_raw.strip())
        
        # Patterns à tester dans l'ordre
        patterns = [
            # Pattern normal: "1 - Titre"
            r"^(\d+)\s*-\s*(.+)$",
            # Pattern avec tiret initial: "-13 - Titre"
            r"^-(\d+)\s*-\s*(.+)$",
            # Pattern avec caractères spéciaux: "-13 ' - ... Titre"
            r"^-(\d+)\s*['\s-]+(.+)$",
            # Pattern général: trouve le premier nombre puis le titre après un tiret
            r".*?(\d+).*?-\s*(.+)$",
        ]
        
        for pattern in patterns:
            m = re.search(pattern, titre_clean, re.DOTALL)
            if m:
                number = m.group(1)
                title = m.group(2).strip()
                return number, title
        
        # Si aucun pattern ne marche, retourner tel quel
        return "", titre_raw
    
    for test_case in test_cases:
        number, title = improved_parse_title(test_case)
        print(f"Input: {repr(test_case)}")
        print(f"  -> Numéro: '{number}', Titre: '{title}'")

if __name__ == "__main__":
    analyze_html_structure()
    test_improved_parsing()
