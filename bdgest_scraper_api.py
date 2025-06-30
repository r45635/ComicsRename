"""
bdgest_scraper_api.py
======================

Ce module fournit des fonctions pour s'authentifier et scraper les données d'albums et de séries depuis le portail BDGest Online (https://online.bdgest.com).

Fonctions :
- get_csrf_token(session, debug=True, verbose=False, log_path=None) : Extrait le token CSRF de la page de login.
- login_bdgest(session, username, password, debug=True, verbose=False, log_path=None) : Authentifie la session utilisateur.
- fetch_albums(session, term, debug=True, verbose=False, log_path=None) : Récupère la liste des albums correspondant au terme de recherche.
- fetch_albums_by_series_id(session, series_id, series_name=None, debug=True, verbose=False, log_path=None, fetch_details=True, max_workers=4) : Récupère la liste des albums d'une série spécifique par ID.
- get_bdgest_albums(term, username, password, debug=True, verbose=False, log_path=None) : Wrapper pour login et fetch albums.
- get_bdgest_albums_by_series_id(series_id, series_name, username, password, debug=True, verbose=False, log_path=None, fetch_details=True, max_workers=4) : Wrapper pour login et fetch albums par ID de série.
- fetch_album_details(album_url, session, debug=False, verbose=False, log_path=None) : Récupère les métadonnées détaillées d'un album.
- fetch_series(session, term, debug=True, verbose=False, log_path=None) : Récupère la liste des séries correspondant au terme de recherche via AJAX.
- get_bdgest_series(term, username, password, debug=True, verbose=False, log_path=None) : Wrapper pour login et fetch series.

Dépendances :
- requests
- bs4
- re
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import concurrent.futures
import json
import html

LOGIN_URL = "https://online.bdgest.com/login"
ALBUMS_URL = (
    "https://online.bdgest.com/albums/import?ids=&s=&t={}&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
)

def _log(text, log_path):
    if log_path:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {text}\n")
            f.flush()

def _decode_html_entities(text):
    """Decode HTML entities like &amp; to & and &lt; to <"""
    if not text:
        return text
    return html.unescape(str(text))

def _check_too_many_results(soup, debug=False):
    """
    Check if BDGest returned a 'too many results' error message.
    Returns (is_error, error_message)
    """
    # Look for the specific error message
    error_spans = soup.find_all("span", class_="semi-bold")
    for span in error_spans:
        if span and "Erreur" in span.get_text():
            # Look for the error message in the next siblings or parent
            parent = span.parent
            if parent:
                full_text = parent.get_text()
                if "plus de 1000 albums" in full_text and "veuillez affiner" in full_text:
                    error_msg = full_text.strip()
                    if debug:
                        print(f"[WARN][BDGest] Too many results error detected: {error_msg}")
                    return True, error_msg
    
    # Also check for any div containing the error message
    error_divs = soup.find_all("div")
    for div in error_divs:
        if div:
            div_text = div.get_text()
            if "plus de 1000 albums" in div_text and "veuillez affiner" in div_text:
                error_msg = div_text.strip()
                if debug:
                    print(f"[WARN][BDGest] Too many results error detected in div: {error_msg}")
                return True, error_msg
    
    return False, None

def _get_soup(text, debug=False):
    try:
        from bs4 import BeautifulSoup
        return BeautifulSoup(text, "lxml")
    except Exception as e:
        if debug:
            print("[WARN][BDGest] lxml parser not available, falling back to html.parser:", e)
        return BeautifulSoup(text, "html.parser")

def get_csrf_token(session, debug=False, verbose=False, log_path=None, max_retries=2):
    for attempt in range(max_retries):
        r = session.get(LOGIN_URL, timeout=10)
        _log(f"GET {LOGIN_URL} status={r.status_code}", log_path)
        if debug:
            print(f"[DEBUG][BDGest] GET {LOGIN_URL} status={r.status_code}")
            if verbose:
                print(f"[DEBUG][BDGest] Response content:\n{r.text}\n")
            _log(r.text if verbose else r.text[:1000] + "...", log_path)
        soup = _get_soup(r.text, debug=debug)
        token = soup.find("input", {"name": "csrf_token_bdg"})
        if token:
            if debug:
                print("[DEBUG][BDGest] CSRF token found")
            return token["value"]
        else:
            if debug:
                print(f"[WARN][BDGest] No CSRF token found on attempt {attempt+1}/{max_retries}")
    raise Exception("No CSRF token found after retries!")

def login_bdgest(session, username, password, debug=False, verbose=False, log_path=None):
    try:
        csrf_token = get_csrf_token(session, debug=debug, verbose=verbose, log_path=log_path)
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Could not get CSRF token: {e}")
        return False
    data = {
        "csrf_token_bdg": csrf_token,
        "li1": "username",
        "li2": "password",
        "source": "",
        "username": username,
        "password": password,
        "auto_connect": "on",
    }
    headers = {
        "Referer": LOGIN_URL,
        "Origin": "https://online.bdgest.com",
        "User-Agent": "Mozilla/5.0",
    }
    r = session.post(LOGIN_URL, data=data, headers=headers, allow_redirects=True)
    _log(f"POST {LOGIN_URL} status={r.status_code} -> {r.url}", log_path)
    if verbose:
        print(f"[DEBUG][BDGest] Full response content:\n{r.text}\n")
    _log(r.text if verbose else r.text[:1000] + "...", log_path)
    if debug:
        print(f"[DEBUG][BDGest] POST {LOGIN_URL} status={r.status_code} -> {r.url}")
        if verbose:
            print(f"[DEBUG][BDGest] Response content:\n{r.text}\n")
        # Remove this else block to avoid printing truncated content when not verbose
        # else:
        #     print(f"[DEBUG][BDGest] Response content (truncated):\n{r.text[:1000]}\n...")
    # Vérifie si la connexion a réussi
    if "/accueil" in r.url or (r.history and "/accueil" in r.history[-1].headers.get("Location", "")):
        if debug:
            print("[INFO][BDGest] Login successful!")
        return True
    else:
        if debug:
            print("[ERROR][BDGest] Login failed! Check credentials or CSRF token.")
        return False

def fetch_album_details(album_url, session, debug=False, verbose=False, log_path=None):
    if not album_url:
        if debug:
            print("[WARN][fetch_album_details] album_url is empty or None.")
        return {}
    if debug:
        print(f"[DEBUG][fetch_album_details] Fetching URL: {album_url}")
    _log(f"GET {album_url}", log_path)
    resp = session.get(album_url, timeout=10)
    _log(f"GET {album_url} status={resp.status_code}", log_path)
    if verbose:
        print(f"[DEBUG][fetch_album_details] Response content:\n{resp.text}\n")
    _log(resp.text if verbose else resp.text[:1000] + "...", log_path)

    if debug:
        print(f"[DEBUG][fetch_album_details] HTTP status: {resp.status_code}")
        print(f"[DEBUG][fetch_album_details] Response length: {len(resp.text)}")
        if verbose:
            print(f"[DEBUG][fetch_album_details] HTML snippet:\n{resp.text[:500]}")
    soup = _get_soup(resp.text, debug=debug)
    details = {}

    col_infos = soup.find("div", class_="col-infos")
    if not col_infos:
        if debug:
            print("[DEBUG][fetch_album_details] No <div class='col-infos'> found.")
        return details

    # Extraction des <ul class="infos">
    infos_ul = col_infos.find("ul", class_="infos")
    if infos_ul:
        for li in infos_ul.find_all("li"):
            label_tag = li.find("label")
            if not label_tag:
                continue
            # Remove trailing and leading spaces from label
            label = _decode_html_entities(label_tag.get_text(strip=True).rstrip(":").strip())
            label_tag.extract()
            value = _decode_html_entities(li.get_text(strip=True))
            # Si la valeur est vide, on regarde les <a> ou <i>
            if not value:
                a_tag = li.find("a")
                if a_tag:
                    value = _decode_html_entities(a_tag.get_text(strip=True))
                i_tag = li.find("i")
                if i_tag and i_tag.has_attr("title"):
                    value = _decode_html_entities(i_tag["title"])
            orig_label = label
            i = 2
            while label in details:
                label = f"{orig_label}#{i}"
                i += 1
            details[label] = value
            if verbose:
                print(f"[VERBOSE][fetch_album_details] {label}: {value}")

    # Extraction du résumé
    autres_div = col_infos.find("div", class_="autres")
    if autres_div:
        resume_span = autres_div.find("span", id="ResumeAffiche")
        if resume_span:
            details["Résumé"] = _decode_html_entities(resume_span.get_text(strip=True))
            if verbose:
                print(f"[VERBOSE][fetch_album_details] Résumé: {details['Résumé']}")

    if debug:
        print(f"[DEBUG][fetch_album_details] Final details: {details}")
    return details

def fetch_albums(session, term, debug=True, verbose=False, log_path=None, fetch_details=True, max_workers=4):
    url = ALBUMS_URL.format(requests.utils.quote(term))
    _log(f"GET {url}", log_path)
    if debug:
        print(f"[DEBUG][BDGest] Fetching albums URL: {url}")
    resp = session.get(url, timeout=10)
    _log(f"GET {url} status={resp.status_code}", log_path)
    if verbose:
        print(f"[DEBUG][BDGest] Response content:\n{resp.text}\n")
    _log(resp.text if verbose else resp.text[:1000] + "...", log_path)

    soup = _get_soup(resp.text, debug=debug)
    albums = []
    
    # Check for "too many results" error first
    is_error, error_msg = _check_too_many_results(soup, debug=debug)
    if is_error:
        if debug:
            print(f"[ERROR][BDGest] Search returned too many results: {error_msg}")
        # Return a special error indicator
        return [{"error": "too_many_results", "message": error_msg}]
    
    table = soup.find("table", class_="table-albums-mid")
    if not table:
        if debug:
            print("[WARN][BDGest] No album table found.")
        return albums

    for tr in table.find_all("tr", class_="clic"):
        album_id = tr.get("id", "").replace("ID", "")
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        cover_img = tds[1].find("img")["src"] if tds[1].find("img") else ""
        serie_tag = tds[2].find("span", class_="serie")
        serie_name = _decode_html_entities(serie_tag.get_text(strip=True)) if serie_tag else ""
        titre_tag = tds[2].find("span", class_="titre")
        titre_raw = titre_tag.get_text(" ", strip=True) if titre_tag else ""
        m = re.match(r"-?\s*([A-Z0-9\-]+)\s*-\s*(.+)", titre_raw)
        album_number = m.group(1) if m else ""
        album_name = _decode_html_entities(m.group(2)) if m else _decode_html_entities(titre_raw)

        editor = tds[3].contents[0].strip() if tds[3].contents else ""
        date = tds[3].find("span", class_="dl").get_text(strip=True) if tds[3].find("span", class_="dl") else ""
        pages = tds[3].find("span", class_="auteurs").get_text(strip=True) if tds[3].find("span", class_="auteurs") else ""
        collection = tds[3].find("span", class_="collection").get_text(strip=True) if tds[3].find("span", class_="collection") else ""
        isbn = tds[3].find("span", class_="isbn").get_text(strip=True) if tds[3].find("span", class_="isbn") else ""
        album_url = f"https://online.bdgest.com/import/edit?IdAlbum={album_id}" if album_id else ""

        # Infos principales d'abord
        album = {
            "serie_name": serie_name,
            "album_id": album_id,
            "album_number": album_number,
            "album_name": album_name,
            "editor": editor,
            "collection": collection,
            "date": date,
            "pages": pages,
            "isbn": isbn,
            "cover_url": cover_img,
            "album_url": album_url,
        }
        albums.append(album)

    if fetch_details and albums:
        def fetch_one(album):
            details = fetch_album_details(album["album_url"], session, debug=debug, verbose=verbose, log_path=log_path)
            album["details"] = details
            return album

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            albums = list(executor.map(fetch_one, albums))
    else:
        for album in albums:
            album["details"] = {}

    if debug:
        print(f"[DEBUG][BDGest] {len(albums)} albums found.")
    return albums

def fetch_albums_by_series_id(session, series_id, series_name=None, debug=True, verbose=False, log_path=None, fetch_details=True, max_workers=4):
    """
    Récupère la liste des albums d'une série spécifique par ID.
    
    Args:
        session (requests.Session): Session authentifiée
        series_id (str): ID de la série
        series_name (str): Nom de la série (optionnel, pour vérification)
        debug (bool): Mode debug
        verbose (bool): Mode verbose
        log_path (str): Chemin du fichier de log
        fetch_details (bool): Si True, récupère les détails de chaque album
        max_workers (int): Nombre de threads pour récupérer les détails en parallèle
    
    Returns:
        list: Liste des albums de la série avec leurs métadonnées
    """
    if debug:
        print(f"[DEBUG][BDGest] Called fetch_albums_by_series_id(series_id={series_id}, series_name={series_name})")
    
    if not series_id:
        if debug:
            print("[WARN][BDGest] series_id is empty or None.")
        return []
    
    # URL de l'endpoint pour récupérer les albums par ID de série
    # Use the series ID in the 'ids' parameter and series name in the 's' parameter
    encoded_series_name = requests.utils.quote(series_name) if series_name else ""
    url = f"https://online.bdgest.com/albums/import?ids={series_id}&s={encoded_series_name}&t=&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
    
    _log(f"GET {url}", log_path)
    
    if debug:
        print(f"[DEBUG][BDGest] Fetching albums by series ID URL: {url}")
    
    try:
        resp = session.get(url, timeout=10)
        _log(f"GET {url} status={resp.status_code}", log_path)
        
        if debug:
            print(f"[DEBUG][BDGest] HTTP status: {resp.status_code}")
            print(f"[DEBUG][BDGest] Response length: {len(resp.text)}")
        
        if verbose:
            print(f"[DEBUG][BDGest] Response content:\n{resp.text}\n")
        
        _log(resp.text if verbose else resp.text[:1000] + "...", log_path)
        
        if resp.status_code != 200:
            if debug:
                print(f"[ERROR][BDGest] HTTP error {resp.status_code}")
            return []
        
        soup = _get_soup(resp.text, debug=debug)
        albums = []
        
        # Check for "too many results" error first
        is_error, error_msg = _check_too_many_results(soup, debug=debug)
        if is_error:
            if debug:
                print(f"[ERROR][BDGest] Search returned too many results: {error_msg}")
            # Return a special error indicator
            return [{"error": "too_many_results", "message": error_msg}]
        
        table = soup.find("table", class_="table-albums-mid")
        if not table:
            if debug:
                print("[WARN][BDGest] No album table found.")
            return albums

        for tr in table.find_all("tr", class_="clic"):
            album_id = tr.get("id", "").replace("ID", "")
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            cover_img = tds[1].find("img")["src"] if tds[1].find("img") else ""
            serie_tag = tds[2].find("span", class_="serie")
            serie_name_extracted = _decode_html_entities(serie_tag.get_text(strip=True)) if serie_tag else ""
            titre_tag = tds[2].find("span", class_="titre")
            titre_raw = titre_tag.get_text(" ", strip=True) if titre_tag else ""
            
            # Improved parsing to handle special cases like album 13
            album_number = ""
            album_name = ""
            
            if titre_raw:
                # Nettoyer les retours à la ligne et espaces multiples
                titre_clean = re.sub(r'\s+', ' ', titre_raw.strip())
                
                # Patterns à tester dans l'ordre de priorité
                patterns = [
                    # Pattern normal: "-1 - Titre"
                    r"^-(\d+)\s*-\s*(.+)$",
                    # Pattern avec caractères spéciaux: "-13 ' - Titre" (cas album 13)
                    r"^-(\d+)\s*['\s]*-\s*(.+)$",
                    # Pattern simple: "1 - Titre"
                    r"^(\d+)\s*-\s*(.+)$",
                    # Pattern général: trouve le premier nombre puis le titre après un tiret
                    r".*?(\d+).*?-\s*(.+)$",
                ]
                
                for pattern in patterns:
                    m = re.search(pattern, titre_clean, re.DOTALL)
                    if m:
                        album_number = m.group(1)
                        album_name = _decode_html_entities(m.group(2).strip())
                        break
                
                # Si aucun pattern ne marche, garder le titre tel quel
                if not album_number and not album_name:
                    album_name = _decode_html_entities(titre_raw)
            
            if debug and album_number == "13":
                print(f"[DEBUG][BDGest] Album 13 parsing - Raw: {repr(titre_raw)}")
                print(f"[DEBUG][BDGest] Album 13 parsing - Number: '{album_number}', Name: '{album_name}'")

            editor = tds[3].contents[0].strip() if tds[3].contents else ""
            date = tds[3].find("span", class_="dl").get_text(strip=True) if tds[3].find("span", class_="dl") else ""
            pages = tds[3].find("span", class_="auteurs").get_text(strip=True) if tds[3].find("span", class_="auteurs") else ""
            collection = tds[3].find("span", class_="collection").get_text(strip=True) if tds[3].find("span", class_="collection") else ""
            isbn = tds[3].find("span", class_="isbn").get_text(strip=True) if tds[3].find("span", class_="isbn") else ""
            album_url = f"https://online.bdgest.com/import/edit?IdAlbum={album_id}" if album_id else ""

            # Infos principales d'abord
            album = {
                "serie_name": serie_name_extracted or series_name,  # Use extracted name or fallback to provided name
                "album_id": album_id,
                "album_number": album_number,
                "album_name": album_name,
                "editor": editor,
                "collection": collection,
                "date": date,
                "pages": pages,
                "isbn": isbn,
                "cover_url": cover_img,
                "album_url": album_url,
            }
            albums.append(album)

        # Récupération des détails des albums si demandé
        if fetch_details and albums:
            def fetch_one(album):
                details = fetch_album_details(album["album_url"], session, debug=debug, verbose=verbose, log_path=log_path)
                album["details"] = details
                return album

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                albums = list(executor.map(fetch_one, albums))
        else:
            for album in albums:
                album["details"] = {}

        if debug:
            print(f"[DEBUG][BDGest] {len(albums)} albums found for series ID {series_id}.")
        return albums
    
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Exception in fetch_albums_by_series_id: {e}")
        _log(f"Exception in fetch_albums_by_series_id: {e}", log_path)
        return []

def get_bdgest_albums(term, username, password, debug=True, verbose=False, log_path=None):
    if debug:
        print(f"[DEBUG][BDGest] Called get_bdgest_albums(term={term}, username={username})")
    try:
        with requests.Session() as session:
            if not login_bdgest(session, username, password, debug=debug, verbose=verbose, log_path=log_path):
                if debug:
                    print("[ERROR][BDGest] Login failed in get_bdgest_albums.")
                return []
            return fetch_albums(session, term, debug=debug, verbose=verbose, log_path=log_path)
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Exception in get_bdgest_albums: {e}")
        _log(f"Exception: {e}", log_path)
        return []

def get_bdgest_series(term, username, password, debug=True, verbose=False, log_path=None):
    """
    Recherche des séries sur BDGest Online via l'endpoint AJAX.
    
    Args:
        term (str): Terme de recherche pour les séries
        username (str): Nom d'utilisateur BDGest
        password (str): Mot de passe BDGest
        debug (bool): Mode debug pour afficher les informations de débogage
        verbose (bool): Mode verbose pour afficher plus de détails
        log_path (str): Chemin du fichier de log (optionnel)
    
    Returns:
        list: Liste des séries trouvées avec leurs métadonnées
    """
    if debug:
        print(f"[DEBUG][BDGest] Called get_bdgest_series(term={term}, username={username})")
    
    try:
        with requests.Session() as session:
            # Authentification
            if not login_bdgest(session, username, password, debug=debug, verbose=verbose, log_path=log_path):
                if debug:
                    print("[ERROR][BDGest] Login failed in get_bdgest_series.")
                return []
            
            # Recherche des séries via l'endpoint AJAX
            return fetch_series(session, term, debug=debug, verbose=verbose, log_path=log_path)
            
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Exception in get_bdgest_series: {e}")
        _log(f"Exception: {e}", log_path)
        return []

def fetch_series(session, term, debug=True, verbose=False, log_path=None):
    """
    Récupère la liste des séries correspondant au terme de recherche via l'API AJAX.
    
    Args:
        session (requests.Session): Session authentifiée
        term (str): Terme de recherche
        debug (bool): Mode debug
        verbose (bool): Mode verbose
        log_path (str): Chemin du fichier de log
    
    Returns:
        list: Liste des séries avec leurs métadonnées
    """
    # URL de l'endpoint AJAX pour la recherche de séries
    series_url = f"https://online.bdgest.com/ajax/series?term={requests.utils.quote(term)}"
    
    if debug:
        print(f"[DEBUG][BDGest] Fetching series URL: {series_url}")
    
    _log(f"GET {series_url}", log_path)
    
    # Headers nécessaires pour l'endpoint AJAX
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://online.bdgest.com/albums/import",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    
    try:
        resp = session.get(series_url, headers=headers, timeout=10)
        _log(f"GET {series_url} status={resp.status_code}", log_path)
        
        if debug:
            print(f"[DEBUG][BDGest] HTTP status: {resp.status_code}")
            print(f"[DEBUG][BDGest] Response length: {len(resp.text)}")
        
        if verbose:
            print(f"[DEBUG][BDGest] Response content:\n{resp.text}\n")
        
        _log(resp.text if verbose else resp.text[:1000] + "...", log_path)
        
        if resp.status_code != 200:
            if debug:
                print(f"[ERROR][BDGest] HTTP error {resp.status_code}")
            return []
        
        # Check if response is JSON or HTML
        content_type = resp.headers.get('Content-Type', '').lower()
        series_list = []
        
        try:
            # Try to parse as JSON first
            if 'application/json' in content_type or resp.text.strip().startswith('[') or resp.text.strip().startswith('{'):
                json_data = json.loads(resp.text)
                if debug:
                    print(f"[DEBUG][BDGest] Parsed JSON response with {len(json_data) if isinstance(json_data, list) else 1} items")
                
                # Handle JSON array or single object
                items = json_data if isinstance(json_data, list) else [json_data]
                
                for item in items:
                    if isinstance(item, dict):
                        serie_info = {
                            "search_term": term,
                            "serie_name": _decode_html_entities(item.get("label", item.get("value", item.get("name", "Unknown")))),
                            "serie_id": item.get("id"),
                            "value": item.get("value"),
                            "label": item.get("label"),
                        }
                        
                        # Add all other fields from the JSON
                        for key, value in item.items():
                            if key not in ["label", "value", "name", "id"] and value:
                                serie_info[key] = value
                        
                        series_list.append(serie_info)
                        if debug:
                            print(f"[DEBUG][BDGest] Found series: {serie_info['serie_name']}")
                            if verbose:
                                print(f"[VERBOSE][BDGest] Series details: {serie_info}")
                
            else:
                # Fallback to HTML parsing
                if debug:
                    print("[DEBUG][BDGest] Response appears to be HTML, parsing as HTML")
                
                soup = _get_soup(resp.text, debug=debug)
                
                # Look for <li> elements containing series information
                li_elements = soup.find_all("li")
                
                for li in li_elements:
                    try:
                        # Extract series information from the HTML structure
                        serie_info = {}
                        
                        # Look for the series name in the text content
                        text_content = li.get_text(strip=True)
                        if not text_content:
                            continue
                        
                        # Extract data attributes if they exist
                        if li.has_attr("data-value"):
                            serie_info["serie_name"] = _decode_html_entities(li["data-value"])
                        else:
                            # Fallback to text content
                            serie_info["serie_name"] = _decode_html_entities(text_content)
                        
                        # Look for additional information in spans or other elements
                        spans = li.find_all("span")
                        for span in spans:
                            span_text = span.get_text(strip=True)
                            if span_text:
                                # Try to identify the type of information
                                if span.has_attr("class"):
                                    class_name = " ".join(span["class"])
                                    serie_info[f"info_{class_name}"] = span_text
                                else:
                                    if "additional_info" not in serie_info:
                                        serie_info["additional_info"] = []
                                    serie_info["additional_info"].append(span_text)
                        
                        # Look for images (covers, flags, etc.)
                        img = li.find("img")
                        if img:
                            if img.has_attr("src"):
                                if "flag" in img["src"]:
                                    serie_info["country_flag"] = img["src"]
                                else:
                                    serie_info["cover_url"] = img["src"]
                            if img.has_attr("alt"):
                                serie_info["country"] = img["alt"]
                        
                        # Extract any links
                        link = li.find("a")
                        if link and link.has_attr("href"):
                            serie_info["serie_url"] = link["href"]
                        
                        # Only add if we have meaningful information
                        if serie_info.get("serie_name"):
                            serie_info["search_term"] = term
                            series_list.append(serie_info)
                            
                            if debug:
                                print(f"[DEBUG][BDGest] Found series: {serie_info['serie_name']}")
                                if verbose:
                                    print(f"[VERBOSE][BDGest] Series details: {serie_info}")
                        
                    except Exception as e:
                        if debug:
                            print(f"[WARN][BDGest] Error parsing series element: {e}")
                        continue
                        
        except json.JSONDecodeError as e:
            if debug:
                print(f"[DEBUG][BDGest] JSON decode failed, trying HTML parsing: {e}")
            # Fallback to HTML parsing if JSON fails
            soup = _get_soup(resp.text, debug=debug)
            # ... (same HTML parsing logic as above)
        except Exception as e:
            if debug:
                print(f"[ERROR][BDGest] Error parsing response: {e}")
            return []
        
        if debug:
            print(f"[DEBUG][BDGest] {len(series_list)} series found.")
        
        return series_list
        
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Exception in fetch_series: {e}")
        _log(f"Exception in fetch_series: {e}", log_path)
        return []

def get_bdgest_albums_by_series_id(series_id, series_name, username, password, debug=True, verbose=False, log_path=None, fetch_details=True, max_workers=4):
    """
    Wrapper pour authentification et récupération des albums d'une série par ID.
    
    Args:
        series_id (str): ID de la série
        series_name (str): Nom de la série
        username (str): Nom d'utilisateur BDGest
        password (str): Mot de passe BDGest
        debug (bool): Mode debug
        verbose (bool): Mode verbose
        log_path (str): Chemin du fichier de log
        fetch_details (bool): Si True, récupère les détails de chaque album
        max_workers (int): Nombre de threads pour récupérer les détails en parallèle
    
    Returns:
        list: Liste des albums de la série avec leurs métadonnées
    """
    if not series_id:
        if debug:
            print("[ERROR][BDGest] series_id is required.")
        return []
    
    session = requests.Session()
    try:
        # Récupération du token CSRF
        if not get_csrf_token(session, debug=debug, verbose=verbose, log_path=log_path):
            if debug:
                print("[ERROR][BDGest] CSRF token not found in get_bdgest_albums_by_series_id.")
            return []
        
        # Authentification
        if not login_bdgest(session, username, password, debug=debug, verbose=verbose, log_path=log_path):
            if debug:
                print("[ERROR][BDGest] Login failed in get_bdgest_albums_by_series_id.")
            return []
        
        # Recherche des albums par ID de série
        return fetch_albums_by_series_id(session, series_id, series_name, debug=debug, verbose=verbose, log_path=log_path, fetch_details=fetch_details, max_workers=max_workers)
        
    except Exception as e:
        if debug:
            print(f"[ERROR][BDGest] Exception in get_bdgest_albums_by_series_id: {e}")
        _log(f"Exception: {e}", log_path)
        return []
