"""
comicvine_api.py
================

This module provides access to the ComicVine API to search and retrieve issue metadata.

Functions:
- search_comicvine_issues(query, debug=True): Searches ComicVine for issues matching the query.
- get_comicvine_issue_details(issue_url, debug=True): Fetches full metadata for a specific ComicVine issue.

Constants:
- COMICVINE_API_KEY: Your ComicVine API key.
- COMICVINE_SEARCH_URL: Base URL for issue search.

Requirements:
- requests

Usage Example:
    issues = search_comicvine_issues("Lanfeust", debug=True)
    if issues:
        details = get_comicvine_issue_details(issues[0]['api_detail_url'], debug=True)
        print(details)
"""

import requests
import os
from pathlib import Path
#from comicVine_scraper_api import search_comicvine_series, search_comicvine_issues

# Load .env file if it exists
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env()

# ⚠️ SÉCURITÉ: Ne jamais stocker la clé API en dur dans le code !
# Utilisez plutôt une variable d'environnement ou un fichier .env
COMICVINE_API_KEY = os.getenv('COMICVINE_API_KEY', '').strip()
COMICVINE_SEARCH_URL = "https://comicvine.gamespot.com/api/search/"

def search_comicvine_issues(query, debug=False, api_key=None):
    # Clean and validate API key
    final_api_key = (api_key or COMICVINE_API_KEY).strip()
    if not final_api_key:
        if debug:
            print("[ERROR][ComicVine] No API key provided")
        return []
    
    params = {
        'api_key': final_api_key,
        'format': 'json',
        'query': query,
        'resources': 'issue',
        'field_list': 'id,name,issue_number,cover_date,volume,image,api_detail_url',
        'limit': 100
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(COMICVINE_SEARCH_URL, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') != 1:
                print(f"[WARN][ComicVine] API error: {data.get('error')}")
            else:
                print(f"[DEBUG][ComicVine] Retrieved {len(data.get('results', []))} issues")
        return data.get('results', []) if data.get('status_code') == 1 else []
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] API call failed:", e)
        return []

def get_comicvine_issue_details(issue_url, debug=False, api_key=None):
    params = {
        'api_key': api_key or COMICVINE_API_KEY,
        'format': 'json'
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(issue_url, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') != 1:
                print(f"[WARN][ComicVine] Issue detail fetch error: {data.get('error')}")
            else:
                print("[DEBUG][ComicVine] Issue details successfully retrieved")
        return data.get('results', {}) if data.get('status_code') == 1 else {}
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] Issue details fetch failed:", e)
        return {}


def search_comicvine_series(query, debug=True, api_key=None):
    # Clean and validate API key
    final_api_key = (api_key or COMICVINE_API_KEY).strip()
    if not final_api_key:
        if debug:
            print("[ERROR][ComicVine] No API key provided")
        return []
    
    url = "https://comicvine.gamespot.com/api/search/"
    params = {
        'api_key': final_api_key,
        'format': 'json',
        'query': query,
        'resources': 'volume',  # <-- IMPORTANT: search for volumes/series, not issues
        'field_list': 'id,name,start_year,publisher,image,api_detail_url',
        'limit': 100
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') != 1:
                print(f"[WARN][ComicVine] API error: {data.get('error')}")
            else:
                print(f"[DEBUG][ComicVine] Retrieved {len(data.get('results', []))} series")
                for i, series in enumerate(data.get('results', []), 1):
                    print(f"  [Series {i}] id={series.get('id')} name={series.get('name')}")
        return data.get('results', []) if data.get('status_code') == 1 else []
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] Series search failed:", e)
        return []

def get_comicvine_volume_issues(volume_id, debug=True, api_key=None):
    # Clean and validate API key
    final_api_key = (api_key or COMICVINE_API_KEY).strip()
    if not final_api_key:
        if debug:
            print("[ERROR][ComicVine] No API key provided")
        return []
    
    url = f"https://comicvine.gamespot.com/api/volume/4050-{volume_id}/"
    params = {
        'api_key': final_api_key,
        'format': 'json',
        'field_list': 'issues,name,start_year,publisher,description,image',
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') == 1:
                issues = data['results'].get('issues', [])
                print(f"[DEBUG][ComicVine] Volume {volume_id}: {len(issues)} issues found")
                for i, issue in enumerate(issues, 1):
                    print(f"  [Issue {i}] id={issue.get('id')} name={issue.get('name')} number={issue.get('issue_number')}")
            else:
                print(f"[WARN][ComicVine] Volume issue fetch error: {data.get('error')}")
        return data['results'].get('issues', []) if data.get('status_code') == 1 else []
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] Volume issue fetch failed:", e)
        return []

def get_comicvine_issue_details(issue_id, debug=False, api_key=None):
    """Get detailed information for a specific issue"""
    # Clean and validate API key
    final_api_key = (api_key or COMICVINE_API_KEY).strip()
    if not final_api_key:
        if debug:
            print("[ERROR][ComicVine] No API key provided")
        return {}
    
    url = f"https://comicvine.gamespot.com/api/issue/4000-{issue_id}/"
    params = {
        'api_key': final_api_key,
        'format': 'json',
        'field_list': 'id,name,issue_number,cover_date,store_date,description,image,volume,character_credits,person_credits,location_credits',
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') != 1:
                print(f"[WARN][ComicVine] Issue detail fetch error: {data.get('error')}")
            else:
                print("[DEBUG][ComicVine] Issue details successfully retrieved")
        return data.get('results', {}) if data.get('status_code') == 1 else {}
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] Issue details fetch failed:", e)
        return {}

def get_comicvine_volume_details(volume_id, debug=True, api_key=None):
    """Get detailed information for a specific volume"""
    # Clean and validate API key
    final_api_key = (api_key or COMICVINE_API_KEY).strip()
    if not final_api_key:
        if debug:
            print("[ERROR][ComicVine] No API key provided")
        return {}
    
    url = f"https://comicvine.gamespot.com/api/volume/4050-{volume_id}/"
    params = {
        'api_key': final_api_key,
        'format': 'json',
        'field_list': 'id,name,start_year,publisher,description,image,character_credits,person_credits,location_credits',
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)  # Reduced timeout for speed
        if debug:
            print(f"[DEBUG][ComicVine] GET {r.url} (HTTP {r.status_code})")
        r.raise_for_status()
        data = r.json()
        if debug:
            if data.get('status_code') != 1:
                print(f"[WARN][ComicVine] Volume detail fetch error: {data.get('error')}")
            else:
                volume_data = data.get('results', {})
                print(f"[DEBUG][ComicVine] Volume {volume_id} details retrieved successfully")
        return data.get('results', {}) if data.get('status_code') == 1 else {}
    except Exception as e:
        if debug:
            print("[ERROR][ComicVine] Volume details fetch failed:", e)
        return {}
