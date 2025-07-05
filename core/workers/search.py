"""
Background worker for metadata search operations.
"""
from PySide6.QtCore import QThread, Signal


class SearchWorker(QThread):
    """Background worker for searching comic metadata."""
    
    # Signals for communication with the main thread
    progress_update = Signal(str)  # Progress message
    search_completed = Signal(dict)  # Search results
    search_error = Signal(str)  # Error message
    
    def __init__(self, source, query, provider, debug=False, verbose=False, series_name_mode=False):
        super().__init__()
        self.source = source
        self.query = query
        self.provider = provider
        self.debug = debug
        self.verbose = verbose
        self.series_name_mode = series_name_mode
        self._cancelled = False
        
    def cancel(self):
        """Cancel the search operation"""
        self._cancelled = True
        
    def run(self):
        """Run the search operation in the background"""
        try:
            if self._cancelled:
                return
                
            if self.source == 'ComicVine':
                self._search_comicvine()
            elif self.source == 'BDGest':
                self._search_bdgest()
                
        except Exception as e:
            if not self._cancelled:
                self.search_error.emit(f"Search error: {str(e)}")
                
    def _search_comicvine(self):
        """Search ComicVine in background thread"""
        from comicVine_scraper_api import search_comicvine_series, search_comicvine_issues
        
        self.progress_update.emit("Searching ComicVine series...")
        
        if self._cancelled:
            return
            
        volumes = search_comicvine_series(self.query, debug=self.debug)
        if not volumes:
            if self.debug:
                print(f"[DEBUG][Worker] No ComicVine volumes found for '{self.query}', trying issues search")
            issues = search_comicvine_issues(self.query)
            issues_by_series = {}
            for it in issues:
                s = (it.get('volume') or {}).get('name', 'Sans série')
                issues_by_series.setdefault(s, []).append(it)
            
            if not self._cancelled:
                self.search_completed.emit({
                    'type': 'comicvine_issues',
                    'issues_by_series': issues_by_series
                })
            return
            
        if self._cancelled:
            return
            
        self.progress_update.emit(f"Loading albums from {len(volumes)} series...")
        
        issues_by_series = {}
        total_volumes = len(volumes)
        
        for vol_idx, series in enumerate(volumes, 1):
            if self._cancelled:
                return
                
            series_name = series.get('name', 'Unknown')
            volume_id = str(series.get('id', ''))
            
            self.progress_update.emit(f"Loading albums from series {vol_idx}/{total_volumes}: {series_name}")
            
            # Fetch issues for this series
            issues = self.provider.search_albums(volume_id, debug=self.debug)
            for issue in issues:
                issue['volume'] = {'name': series_name}
                issues_by_series.setdefault(series_name, []).append(issue)
                
        if not self._cancelled:
            self.search_completed.emit({
                'type': 'comicvine_series',
                'issues_by_series': issues_by_series
            })
            
    def _search_bdgest(self):
        """Search BDGest in background thread"""
        if self.series_name_mode:
            self.progress_update.emit("Searching BDGest series...")
            
            if self._cancelled:
                return
                
            series_results = self.provider.search_series_only(self.query, debug=self.debug, verbose=self.verbose) \
                if hasattr(self.provider, 'search_series_only') \
                else []
                
            if not self._cancelled:
                self.search_completed.emit({
                    'type': 'bdgest_series',
                    'series_results': series_results
                })
        else:
            self.progress_update.emit("Searching BDGest albums...")
            
            if self._cancelled:
                return
                
            # Use regular album search
            series_list = self.provider.search_series(self.query, debug=self.debug, verbose=self.verbose) \
                if hasattr(self.provider, 'search_series') and self.provider.search_series.__code__.co_argcount > 2 \
                else self.provider.search_series(self.query)
                
            if self._cancelled:
                return
                
            self.progress_update.emit("Processing album results...")
            
            albums = []
            for album in series_list:
                if self._cancelled:
                    return
                s = album.get('serie_name', '')
                if s:
                    albums.append(album)
                    
            if not self._cancelled:
                self.search_completed.emit({
                    'type': 'bdgest_albums',
                    'albums': albums
                })
