"""
bdgest_scraper_api.py
======================

Ce module fournit des fonctions pour s'authentifier et scraper les données d'albums depuis le portail BDGest Online (https://online.bdgest.com).

Fonctions :
- get_csrf_token(session, debug=True, verbose=False, log_path=None) : Extrait le token CSRF de la page de login.
- login_bdgest(session, username, password, debug=True, verbose=False, log_path=None) : Authentifie la session utilisateur.
- fetch_albums(session, term, debug=True, verbose=False, log_path=None) : Récupère la liste des albums correspondant au terme de recherche.
- get_bdgest_albums(term, username, password, debug=True, verbose=False, log_path=None) : Wrapper pour login et fetch albums.
- fetch_album_details(album_url, session, debug=False, verbose=False, log_path=None) : Récupère les métadonnées détaillées d'un album.

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

LOGIN_URL = "https://online.bdgest.com/login"
ALBUMS_URL = (
    "https://online.bdgest.com/albums/import?ids=&s=&t={}&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
)

def _log(text, log_path):
    if log_path:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {text}\n")
            f.flush()

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
    _log(r.text if verbose else r.text[:1000] + "...", log_path)
    if debug:
        print(f"[DEBUG][BDGest] POST {LOGIN_URL} status={r.status_code} -> {r.url}")
        if verbose:
            print(f"[DEBUG][BDGest] Full response content:\n{r.text}\n")
        else:
            print(f"[DEBUG][BDGest] Response content (truncated):\n{r.text[:1000]}\n...")
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
    _log(resp.text if verbose else resp.text[:1000] + "...", log_path)

    if debug:
        print(f"[DEBUG][fetch_album_details] HTTP status: {resp.status_code}")
        print(f"[DEBUG][fetch_album_details] Response length: {len(resp.text)}")
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
            label = label_tag.get_text(strip=True).rstrip(":").strip()
            label_tag.extract()
            value = li.get_text(strip=True)
            # Si la valeur est vide, on regarde les <a> ou <i>
            if not value:
                a_tag = li.find("a")
                if a_tag:
                    value = a_tag.get_text(strip=True)
                i_tag = li.find("i")
                if i_tag and i_tag.has_attr("title"):
                    value = i_tag["title"]
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
            details["Résumé"] = resume_span.get_text(strip=True)
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
    _log(resp.text if verbose else resp.text[:1000] + "...", log_path)

    soup = _get_soup(resp.text, debug=debug)
    albums = []
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
        serie_name = serie_tag.get_text(strip=True) if serie_tag else ""
        titre_tag = tds[2].find("span", class_="titre")
        titre_raw = titre_tag.get_text(" ", strip=True) if titre_tag else ""
        m = re.match(r"-?\s*([A-Z0-9\-]+)\s*-\s*(.+)", titre_raw)
        album_number = m.group(1) if m else ""
        album_name = m.group(2) if m else titre_raw

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
