"""
BDGest provider for fetching comic metadata.
"""
import requests
from PySide6.QtCore import QSettings

from .base import MetadataProvider


class BDGestProvider(MetadataProvider):
    """Provider for BDGest metadata fetching."""
    
    def __init__(self):
        self._session = None
        self._authenticated = False
        self._last_credentials = None
    
    def _get_credentials(self):
        """Get current credentials from settings"""
        settings = QSettings("ComicsRename", "App")
        user = settings.value('bdgest_user', '')
        pwd = settings.value('bdgest_pass', '')
        return user, pwd
    
    def _ensure_authenticated_session(self, debug=False, verbose=False):
        """Ensure we have an authenticated session, create/authenticate if needed"""
        from bdgest_scraper_api import login_bdgest, get_csrf_token
        
        user, pwd = self._get_credentials()
        current_credentials = (user, pwd)
        
        # Check if we need to create a new session or re-authenticate
        need_new_session = (
            self._session is None or 
            not self._authenticated or
            self._last_credentials != current_credentials
        )
        
        if need_new_session:
            if debug:
                print("[DEBUG][BDGest] Creating new session or re-authenticating")
            
            # Create new session
            self._session = requests.Session()
            self._authenticated = False
            
            # Get CSRF token
            if not get_csrf_token(self._session, debug=debug, verbose=verbose):
                if debug:
                    print("[ERROR][BDGest] Failed to get CSRF token")
                return False
            
            # Authenticate
            if not login_bdgest(self._session, user, pwd, debug=debug, verbose=verbose):
                if debug:
                    print("[ERROR][BDGest] Authentication failed")
                self._authenticated = False
                return False
            
            self._authenticated = True
            self._last_credentials = current_credentials
            if debug:
                print("[DEBUG][BDGest] Session authenticated successfully")
        else:
            if debug:
                print("[DEBUG][BDGest] Using existing authenticated session")
        
        return True
    
    def _invalidate_session(self):
        """Invalidate the current session (called when authentication fails)"""
        self._session = None
        self._authenticated = False
        self._last_credentials = None

    def search_series(self, query, debug=False, verbose=False):
        from bdgest_scraper_api import fetch_albums
        
        if not self._ensure_authenticated_session(debug=debug, verbose=verbose):
            return []
        
        try:
            return fetch_albums(self._session, query, debug=debug, verbose=verbose)
        except Exception as e:
            if debug:
                print(f"[ERROR][BDGest] Error in search_series: {e}")
            # Invalidate session on error (might be authentication issue)
            self._invalidate_session()
            return []

    def search_series_only(self, query, debug=False, verbose=False):
        """Search only in series names using the new fetch_series function"""
        from bdgest_scraper_api import fetch_series
        
        if not self._ensure_authenticated_session(debug=debug, verbose=verbose):
            return []
        
        try:
            return fetch_series(self._session, query, debug=debug, verbose=verbose)
        except Exception as e:
            if debug:
                print(f"[ERROR][BDGest] Error in search_series_only: {e}")
            # Invalidate session on error (might be authentication issue)
            self._invalidate_session()
            return []

    def search_albums(self, serie_name):
        from bdgest_scraper_api import fetch_albums
        
        if not self._ensure_authenticated_session():
            return []
        
        try:
            return fetch_albums(self._session, serie_name)
        except Exception as e:
            print(f"[ERROR][BDGest] Error in search_albums: {e}")
            # Invalidate session on error (might be authentication issue)
            self._invalidate_session()
            return []

    def search_albums_by_series_id(self, series_id, series_name, debug=False, verbose=False, fetch_details=True):
        """Search albums for a specific series using series ID"""
        from bdgest_scraper_api import fetch_albums_by_series_id
        
        if not self._ensure_authenticated_session(debug=debug, verbose=verbose):
            return []
        
        try:
            return fetch_albums_by_series_id(self._session, series_id, series_name, debug=debug, verbose=verbose, fetch_details=fetch_details)
        except Exception as e:
            if debug:
                print(f"[ERROR][BDGest] Error in search_albums_by_series_id: {e}")
            # Invalidate session on error (might be authentication issue)
            self._invalidate_session()
            return []
