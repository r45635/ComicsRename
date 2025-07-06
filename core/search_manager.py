"""
Search Manager - Handles all search operations for ComicsRename
"""

from collections import defaultdict
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import Qt, QObject, Signal

from i18n import tr
from core.providers import PROVIDERS


class SearchManager(QObject):
    """Manages all search operations and result handling"""
    
    # Signals for communication with the UI
    search_started = Signal()
    search_completed = Signal(dict)  # Search results
    search_cancelled = Signal()
    search_error = Signal(str, str)  # title, message
    progress_updated = Signal(str)  # progress message
    
    def __init__(self, parent=None, debug=False, verbose=False):
        super().__init__(parent)
        self.debug = debug
        self.verbose = verbose
        self._search_cancelled = False
        self._search_in_progress = False
        
    def cancel_search(self):
        """Cancel the current search operation"""
        self._search_cancelled = True
        self.search_cancelled.emit()
        
    def is_search_in_progress(self):
        """Check if a search is currently in progress"""
        return self._search_in_progress
        
    def search(self, query, source, series_name_mode=False):
        """
        Execute a search operation
        
        Args:
            query: Search query string
            source: Provider source ('BDGest' or 'ComicVine')
            series_name_mode: Whether to search in series-name mode
        """
        if not query.strip():
            return
            
        # Set search state
        self._search_cancelled = False
        self._search_in_progress = True
        self.search_started.emit()
        
        try:
            if series_name_mode:
                self._search_series_mode(query, source)
            else:
                self._search_normal_mode(query, source)
                
        except Exception as e:
            if not self._search_cancelled:
                self.search_error.emit("Search Error", str(e))
        finally:
            self._search_in_progress = False
            
    def _search_series_mode(self, query, source):
        """Handle series-mode search"""
        self.progress_updated.emit(f"Searching {source} series...")
        
        provider = PROVIDERS[source]
        
        # Check for cancellation
        if self._search_cancelled:
            return
            
        # Use series-only search
        series_results = provider.search_series_only(query, debug=self.debug, verbose=self.verbose) \
            if hasattr(provider, 'search_series_only') \
            else []
            
        # Check for errors
        if self._check_for_errors(series_results, source):
            return
            
        # Emit results
        if not self._search_cancelled:
            self.search_completed.emit({
                'type': 'series_results',
                'source': source,
                'series_results': series_results,
                'query': query
            })
            
    def _search_normal_mode(self, query, source):
        """Handle normal-mode search"""
        provider = PROVIDERS[source]
        
        if source == 'ComicVine':
            self._search_comicvine_normal(query, provider)
        else:  # BDGest
            self._search_bdgest_normal(query, provider)
            
    def _search_comicvine_normal(self, query, provider):
        """Handle ComicVine normal mode search"""
        self.progress_updated.emit("Searching ComicVine...")
        
        # Check for cancellation
        if self._search_cancelled:
            return
            
        # First try to get series/volumes
        try:
            series_list = provider.search_series(query, debug=self.debug)
        except TypeError:
            series_list = provider.search_series(query)
            
        if series_list:
            self._fetch_comicvine_albums(query, series_list, provider)
        else:
            self._fallback_comicvine_issues(query)
            
    def _fetch_comicvine_albums(self, query, volumes, provider):
        """Fetch albums from ComicVine volumes"""
        self.progress_updated.emit(f"Loading albums from {len(volumes)} series...")
        
        issues_by_series = {}
        
        for vol_idx, series in enumerate(volumes, 1):
            # Check for cancellation
            if self._search_cancelled:
                return
                
            series_name = series.get('name', 'Unknown')
            volume_id = str(series.get('id', ''))
            
            self.progress_updated.emit(f"Loading albums from series {vol_idx}/{len(volumes)}: {series_name}")
            
            # Fetch issues for this series
            issues = provider.search_albums(volume_id, debug=self.debug)
            for issue in issues:
                issue['volume'] = {'name': series_name}
                issues_by_series.setdefault(series_name, []).append(issue)
                
        if not self._search_cancelled:
            self.search_completed.emit({
                'type': 'comicvine_albums',
                'issues_by_series': issues_by_series,
                'query': query
            })
            
    def _fallback_comicvine_issues(self, query):
        """Fallback to direct ComicVine issues search"""
        from comicVine_scraper_api import search_comicvine_issues
        
        self.progress_updated.emit("Searching ComicVine issues...")
        
        if self._search_cancelled:
            return
            
        issues = search_comicvine_issues(query)
        issues_by_series = {}
        
        for issue in issues:
            s = (issue.get('volume') or {}).get('name', 'Sans série')
            issues_by_series.setdefault(s, []).append(issue)
            
        if not self._search_cancelled:
            self.search_completed.emit({
                'type': 'comicvine_issues',
                'issues_by_series': issues_by_series,
                'query': query
            })
            
    def _search_bdgest_normal(self, query, provider):
        """Handle BDGest normal mode search"""
        self.progress_updated.emit("Searching BDGest albums...")
        
        # Check for cancellation
        if self._search_cancelled:
            return
            
        # Get series list
        try:
            series_list = provider.search_series(query, debug=self.debug)
        except TypeError:
            series_list = provider.search_series(query)
            
        # Check for errors
        if self._check_for_errors(series_list, 'BDGest'):
            return
            
        # Process albums
        albums = []
        if series_list:
            for album in series_list:
                if self._search_cancelled:
                    return
                    
                s = album.get('serie_name', '')
                if s:
                    albums.append(album)
                    
        if not self._search_cancelled:
            self.search_completed.emit({
                'type': 'bdgest_albums',
                'albums': albums,
                'query': query
            })
            
    def _check_for_errors(self, results, source):
        """
        Check for common errors in search results
        
        Returns:
            bool: True if error was found and handled, False otherwise
        """
        if not results or len(results) != 1:
            return False
            
        error_item = results[0]
        
        # Check for authentication failed
        if error_item.get('error') == 'authentication_failed':
            title = tr("messages.errors.authentication_failed_title")
            message = tr("messages.errors.authentication_failed_message")
            hint = tr("messages.errors.authentication_failed_hint")
            full_message = f"{message}\n\n{hint}"
            self.search_error.emit(title, full_message)
            return True
            
        # Check for too many results
        if error_item.get('error') == 'too_many_results':
            title = tr("messages.errors.too_many_results_title")
            message = tr("messages.errors.too_many_results_message")
            hint = tr("messages.errors.too_many_results_hint")
            full_message = f"{message}\n\n{hint}"
            self.search_error.emit(title, full_message)
            return True
            
        return False
