"""
ComicsRename - Requirements

This script requires the following Python packages:
    - PySide6
    - requests
    - beautifulsoup4
    - lxml

To install all dependencies in your (virtual) environment, run:
    pip install PySide6 requests beautifulsoup4 lxml

All other modules used are from the Python standard library.
"""

import sys
import os
import pathlib
import requests
from collections import defaultdict
import subprocess
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QSplitter, QPushButton, QLineEdit,
    QLabel, QFileDialog, QMessageBox, QComboBox, QTextEdit, QTextBrowser, QCheckBox,
    QAbstractItemView, QHeaderView, QMenu, QDialog, QFormLayout, QDialogButtonBox, QMenuBar,
    QScrollArea
)
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSettings, QThread, Signal as pyqtSignal
from PySide6.QtGui import QPixmap, QDrag, QAction, QIcon

from utils import scan_comic_files, load_bdgest_credentials, extract_year, open_file_cross_platform, reveal_file_cross_platform, get_system_info
from utils.icons import get_app_icon
from bdgest_scraper_api import get_bdgest_series

# Import internationalization system
from i18n import tr, set_language, get_current_language, get_supported_languages

# ---------- Providers (API abstraction layer) ----------
class MetadataProvider:
    def search_series(self, query):
        raise NotImplementedError

    def search_albums(self, series_id_or_name):
        raise NotImplementedError

class BDGestProvider(MetadataProvider):
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

class ComicVineProvider(MetadataProvider):
    def search_series(self, query, debug=False):
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        if api_key:
            return search_comicvine_series(query, api_key=api_key, debug=debug)
        else:
            return search_comicvine_series(query, debug=debug)

    def search_albums(self, volume_id, debug=False):
        from comicVine_scraper_api import get_comicvine_volume_issues, get_comicvine_issue_details, get_comicvine_volume_details
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        
        # First, get volume details to extract concepts (genres/styles)
        volume_details = get_comicvine_volume_details(volume_id, api_key=api_key, debug=debug) if api_key else get_comicvine_volume_details(volume_id, debug=debug)
        volume_concepts = []
        volume_style = ""
        
        if volume_details and volume_details.get('concepts'):
            concepts = volume_details.get('concepts', [])
            volume_concepts = [concept.get('name') for concept in concepts if concept.get('name')]
            # Use the first concept as the main style, or join multiple concepts
            if volume_concepts:
                volume_style = volume_concepts[0] if len(volume_concepts) == 1 else ', '.join(volume_concepts[:3])
                if debug:
                    print(f"[DEBUG] Volume style from concepts: {volume_style}")
        
        # Get basic volume and issues data
        issues_list = get_comicvine_volume_issues(volume_id, api_key=api_key, debug=debug) if api_key else get_comicvine_volume_issues(volume_id, debug=debug)
        
        if not issues_list:
            return []
        
        # Use the data we already have without additional API calls for speed
        enriched_issues = []
        for issue in issues_list:  # Process all issues, not just first 20
            issue_id = issue.get('id')
            if issue_id:
                # Use the data we already have from the volume issues call
                # This is much faster than making individual API calls
                # Determine publication date with fallback logic
                publication_date = issue.get('cover_date')
                if not publication_date or publication_date == 'Date inconnue':
                    # Use volume start year as fallback
                    if volume_details and volume_details.get('start_year'):
                        publication_date = str(volume_details.get('start_year'))
                    else:
                        publication_date = 'Date inconnue'
                
                enriched_issue = {
                    'id': issue.get('id'),
                    'issue_number': issue.get('issue_number', 'N/A'),
                    'name': issue.get('name', 'Sans titre'),
                    'cover_date': publication_date,
                    'store_date': issue.get('store_date', ''),
                    'description': issue.get('description', ''),
                    'image': volume_details.get('image', {}) if volume_details else issue.get('image', {}),  # Use volume image if available
                    'volume': volume_details,  # Use volume details we already fetched
                    'api_detail_url': issue.get('api_detail_url', ''),
                    # Add computed fields for consistency with BDGest
                    'title': issue.get('name', 'Sans titre'),
                    # Use volume image since individual issues don't have detailed image data
                    'cover_url': volume_details.get('image', {}).get('original_url', '') if volume_details and volume_details.get('image') else '',
                    'album_url': f"https://comicvine.gamespot.com/issue/4000-{issue_id}/",
                }
                
                # Create details section like BDGest with automatic structure detection
                details_dict = {}
                
                # Helper function to format any complex data structure
                def format_complex_data(key, value, label):
                    """Format complex data (arrays, objects) into structured display format"""
                    if isinstance(value, list) and value:
                        if isinstance(value[0], dict):
                            # Array of objects - extract meaningful info
                            if key == 'character_credits':
                                items = [char.get('name', 'Unknown') for char in value[:10]]
                            elif key == 'person_credits':
                                items = [f"{person.get('name', 'Unknown')} ({person.get('role', 'N/A')})" for person in value]
                            elif key == 'location_credits':
                                items = [loc.get('name', 'Unknown') for loc in value]
                            else:
                                # Generic handling for any array of objects
                                items = []
                                for item in value[:10]:  # Limit to 10 items
                                    if isinstance(item, dict):
                                        # Try to find a meaningful display value
                                        display_value = (item.get('name') or 
                                                       item.get('title') or 
                                                       item.get('id') or 
                                                       str(item)[:50] + '...' if len(str(item)) > 50 else str(item))
                                        items.append(str(display_value))
                                    else:
                                        items.append(str(item))
                            
                            if items:
                                details_dict[label] = {'type': 'list', 'items': items}
                        else:
                            # Array of simple values
                            details_dict[label] = {'type': 'list', 'items': [str(item) for item in value[:10]]}
                    
                    elif isinstance(value, dict) and value:
                        # Single object - show key-value pairs
                        items = []
                        for k, v in value.items():
                            if isinstance(v, (str, int, float)) and v:
                                # Format key names nicely
                                display_key = k.replace('_', ' ').title()
                                items.append(f"{display_key}: {v}")
                        
                        if items:
                            details_dict[label] = {'type': 'list', 'items': items[:10]}  # Limit to 10 items
                
                # Add basic fields with date fallback logic
                publication_date = None
                if enriched_issue.get('cover_date'):
                    publication_date = enriched_issue.get('cover_date')
                    details_dict['Date de publication'] = publication_date
                elif volume_details and volume_details.get('start_year'):
                    # Use volume start year as fallback when cover_date is not available
                    publication_date = str(volume_details.get('start_year'))
                    details_dict['Date de publication'] = f"{publication_date} (Année du volume)"
                else:
                    details_dict['Date de publication'] = "Date inconnue"
                
                # Store the resolved date for use in issue data
                if publication_date:
                    enriched_issue['cover_date'] = publication_date if enriched_issue.get('cover_date') else publication_date
                
                if enriched_issue.get('store_date'):
                    details_dict['Date en magasin'] = enriched_issue.get('store_date')
                if enriched_issue.get('description'):
                    # Clean HTML from description
                    import re
                    clean_desc = re.sub('<[^<]+?>', '', enriched_issue.get('description', ''))
                    details_dict['Description'] = clean_desc[:500] + ('...' if len(clean_desc) > 500 else '')
                
                # Add volume style/genre information
                if volume_style:
                    details_dict['Style/Genre'] = volume_style
                
                # For now, skip the complex field processing since we don't have detailed issue data
                # This makes the loading much faster while still providing essential information
                
                # Add volume information if available
                if volume_details:
                    vol_info = []
                    if volume_details.get('name'):
                        vol_info.append(f"Nom: {volume_details.get('name')}")
                    if volume_details.get('start_year'):
                        vol_info.append(f"Année: {volume_details.get('start_year')}")
                    if volume_details.get('publisher', {}).get('name'):
                        vol_info.append(f"Éditeur: {volume_details.get('publisher', {}).get('name')}")
                    if vol_info:
                        details_dict['Volume'] = {'type': 'list', 'items': vol_info}
                
                enriched_issue['details'] = details_dict
                
                # Add volume style/genre information for folder renaming
                if volume_style:
                    enriched_issue['style'] = volume_style
                    # Also add to details for consistency with BDGest
                    enriched_issue['details']['Style'] = volume_style
                
                enriched_issues.append(enriched_issue)
            else:
                # Fallback for issues without ID
                fallback_issue = issue.copy()
                if volume_style:
                    fallback_issue['style'] = volume_style
                enriched_issues.append(fallback_issue)
        
        if debug:
            print(f"[DEBUG] Enriched {len(enriched_issues)} issues with detailed information")
        return enriched_issues

    def search_series_only(self, query, debug=False, verbose=False):
        """Search only for series names without fetching detailed album data"""
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        
        try:
            if api_key:
                results = search_comicvine_series(query, api_key=api_key, debug=debug)
            else:
                results = search_comicvine_series(query, debug=debug)
            
            # Transform results to match expected format
            series_list = []
            for volume in results:
                series_data = {
                    'serie_name': volume.get('name', 'Unknown'),
                    'volume_id': str(volume.get('id', '')),
                    'start_year': volume.get('start_year'),
                    'publisher': volume.get('publisher', {}).get('name', 'Unknown') if volume.get('publisher') else 'Unknown',
                    'image': volume.get('image'),
                    'api_detail_url': volume.get('api_detail_url'),
                    'raw_data': volume  # Store original data for later use
                }
                series_list.append(series_data)
            
            if debug:
                print(f"[DEBUG][ComicVine] search_series_only returned {len(series_list)} series")
            
            return series_list
        except Exception as e:
            if debug:
                print(f"[ERROR][ComicVine] Error in search_series_only: {e}")
            return []

PROVIDERS = {
    'ComicVine': ComicVineProvider(),
    'BDGest': BDGestProvider(),
}

# ---------- Worker Thread for Search Operations ----------
class SearchWorker(QThread):
    # Signals for communication with the main thread
    progress_update = pyqtSignal(str)  # Progress message
    search_completed = pyqtSignal(dict)  # Search results
    search_error = pyqtSignal(str)  # Error message
    
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

# ---------- Metadata Providers ----------
# ---------- Custom UI Components ----------
class DroppableLineEdit(QLineEdit):
    """A QLineEdit that accepts drag and drop of text/files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text().strip()
            # Remove file:// prefix if present
            if text.startswith('file://'):
                text = text[7:]
            self.setText(text)
            event.acceptProposedAction()
        else:
            event.ignore()


class EditableFolderLineEdit(QLineEdit):
    """A QLineEdit for displaying folder names (not full paths) with drag support for search"""
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(False)  # Disable drop to avoid conflicts
        self.setReadOnly(True)  # Read-only by default, editable on double-click
        self.original_text = ""  # Store original text for comparison
        self.editing_finished = False  # Flag to prevent double processing
        
    def mouseDoubleClickEvent(self, event):
        """Enable editing on double-click"""
        if event.button() == Qt.LeftButton:
            self.original_text = self.text()  # Store original text
            self.editing_finished = False  # Reset flag
            self.setReadOnly(False)
            self.selectAll()
            self.setFocus()
        super().mouseDoubleClickEvent(event)
    
    def keyPressEvent(self, event):
        """Handle Enter/Return and Escape keys during editing"""
        if not self.isReadOnly():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._finish_editing(save=True)
                return
            elif event.key() == Qt.Key_Escape:
                self._finish_editing(save=False)
                return
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Finish editing when focus is lost"""
        if not self.isReadOnly():
            self._finish_editing(save=True)
        super().focusOutEvent(event)
    
    def _finish_editing(self, save=True):
        """Finish editing and optionally save changes"""
        if self.isReadOnly() or self.editing_finished:
            return
            
        self.editing_finished = True  # Set flag to prevent double processing
        new_text = self.text().strip()
        
        if save and new_text != self.original_text and new_text:
            # Confirm rename operation
            if self.main_window and hasattr(self.main_window, '_confirm_and_rename_folder'):
                success = self.main_window._confirm_and_rename_folder(self.original_text, new_text)
                if not success:
                    # Revert to original text if rename failed
                    self.setText(self.original_text)
            else:
                # Fallback: just revert to original text
                self.setText(self.original_text)
        elif not save:
            # Restore original text on cancel
            self.setText(self.original_text)
        
        self.setReadOnly(True)
        self.clearFocus()
        
    def mousePressEvent(self, event):
        """Handle mouse press to start drag operation"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to start drag if conditions are met"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if not hasattr(self, 'drag_start_position'):
            return
            
        if ((event.pos() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # Start drag operation with folder name
        folder_name = self.text()
        if folder_name:
            # Clean the folder name by removing bracketed and parenthetical content
            cleaned_name = self._clean_folder_name(folder_name)
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(cleaned_name)
            drag.setMimeData(mime_data)
            drag.exec(Qt.CopyAction)
    
    def _clean_folder_name(self, folder_name):
        """Clean folder name by removing bracketed and parenthetical content"""
        import re
        
        # Remove content in square brackets like [Fantastique]
        cleaned = re.sub(r'\[.*?\]', '', folder_name)
        
        # Remove content in parentheses like (PeruMartino)
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        
        # Remove extra whitespace and strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

# ---------- Custom Tables ----------
class FileTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDropIndicatorShown(True)
        self.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
        )
        self.setColumnCount(4)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemChanged.connect(self._cell_changed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def dragEnterEvent(self, event):
        # Accept internal app drag or external files with supported extensions
        if event.mimeData().hasFormat('application/x-comic-meta'):
            event.acceptProposedAction()
        elif event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    ext = os.path.splitext(url.toLocalFile())[1].lower()
                    if ext in ('.pdf', '.epub', '.cbz', '.cbr'):
                        event.acceptProposedAction()
                        return
            event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # Internal drag & drop (DnD rename)
        if event.mimeData().hasFormat('application/x-comic-meta'):
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            row = self.rowAt(pos.y())
            if row < 0:
                return
            payload = event.mimeData().data('application/x-comic-meta').data().decode()
            # print(f"[DEBUG][DnD] Payload: {payload}")  # Debug disabled by default
            # Try to parse the payload as "Series - Num - Title (Year)"
            # Use similar cleaning as in _rename_selected
            parts = payload.split(' - ', 2)
            if len(parts) < 3:
                # print("[DEBUG][DnD] Split failed, parts:", parts)  # Debug disabled by default
                return
            series, num, rest = parts
            # Extract title and year if present
            title = rest
            y = ''
            m = re.match(r"^(.*)\s+\((\d{4})\)$", rest)
            if m:
                title = m.group(1)
                y = m.group(2)
            def format_num(n):
                try:
                    n_int = int(n)
                    return f"{n_int:02d}"
                except Exception:
                    return str(n)
            def clean(s):
                return re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
            base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
            if y:
                base += f" ({y})"
            f = self.main.files[row]
            ext = f['ext'].lstrip('.')
            new_name = f"{base}.{ext}"
            new_path = pathlib.Path(f['folder']) / new_name
            confirm = QMessageBox.question(
                self,
                tr("dialogs.rename_confirmation.title"),
                tr("dialogs.rename_confirmation.file_message", new_name=new_name),
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    if not os.path.exists(f['path']):
                        QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_not_exists", path=f['path']))
                        return
                    if new_path.exists():
                        QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_already_exists", name=new_name))
                        return
                    os.rename(f['path'], new_path)
                    self.main._load_files(f['folder'])
                except Exception as e:
                    QMessageBox.critical(self, tr("messages.errors.rename_error"), str(e))
            return

        # External file drop (from Finder, etc.)
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            supported_exts = ('.pdf', '.epub', '.cbz', '.cbr')
            files_to_add = []
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in supported_exts:
                        files_to_add.append(file_path)
            if not files_to_add:
                QMessageBox.warning(self, tr("messages.warnings.unsupported_format"), tr("messages.errors.unsupported_format"))
                return
            op = "déplacer" if (event.dropAction() == Qt.MoveAction or (event.keyboardModifiers() & Qt.ShiftModifier)) else "copier"
            msg = f"Voulez-vous {op} les fichiers suivants dans le dossier actif ?\n\n" + "\n".join(os.path.basename(f) for f in files_to_add)
            if QMessageBox.question(self, "Ajouter des fichiers", msg, QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                return
            dest_folder = self.main.files[0]['folder'] if self.main.files else self.main.settings.value('last_folder', '')
            if not dest_folder:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.no_active_folder"))
                return
            import shutil
            for src in files_to_add:
                # Vérifie que le fichier existe
                if not os.path.exists(src):
                    QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_not_exists", path=src))
                    continue
                # Nettoie le nom du fichier (enlève les caractères interdits)
                base_name = os.path.basename(src).replace('/', '_')
                # Coupe le nom si trop long (255 caractères max sur la plupart des FS)
                if len(base_name) > 255:
                    name, ext = os.path.splitext(base_name)
                    base_name = name[:250-len(ext)] + ext
                dest = os.path.join(dest_folder, base_name)
                try:
                    if op == "déplacer":
                        shutil.move(src, dest)
                    else:
                        shutil.copy2(src, dest)
                except Exception as e:
                    # Vérifie si le fichier destination existe malgré l'exception
                    if os.path.exists(dest):
                        QMessageBox.warning(
                            self,
                            "Avertissement",
                            f"Le fichier a été copié, mais une exception a été levée :\n{e}\n\nSource: {src}\nDestination: {dest}"
                        )
                    else:
                        QMessageBox.critical(
                            self,
                            tr("messages.errors.error"),
                            tr("messages.errors.add_file_error", file=base_name, error=str(e), source=src, dest=dest)
                        )
            self.main._load_files(dest_folder)
            return

    def _cell_changed(self, item):
        if getattr(self.main, '_populating', False) or item.column() != 0:
            return
        row = item.row()
        f = self.main.files[row]
        new_name = item.text()
        if new_name == f['name']:
            return
        new_path = pathlib.Path(f['folder']) / f"{new_name}.{f['ext']}"
        confirm = QMessageBox.question(
            self,
            tr("dialogs.rename_confirmation.title"),
            tr("dialogs.rename_confirmation.file_message", new_name=new_path.name),
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                os.rename(f['path'], new_path)
                self.main._load_files(f['folder'])
            except Exception as e:
                QMessageBox.critical(self, "Rename Error", str(e))

    def _show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu(self)
        
        # Get system info for appropriate menu labels
        system_info = get_system_info()        # Adaptive menu labels based on OS
        if system_info['is_windows']:
            open_label = tr("ui.menus.open_file")  # "Open File"
            reveal_label = tr("ui.menus.show_in_explorer")  # "Show in Explorer"
        elif system_info['is_macos']:
            open_label = tr("ui.menus.open_file")  # "Open File" 
            reveal_label = tr("ui.menus.reveal_in_finder")  # "Reveal in Finder"
        else:  # Linux
            open_label = tr("ui.menus.open_file")  # "Open File"
            reveal_label = tr("ui.menus.show_in_file_manager")  # "Show in File Manager"
            
        open_action = menu.addAction(open_label)
        reveal_action = menu.addAction(reveal_label)
        # Quick View option for PDF files
        quick_view_action = menu.addAction(tr("ui.menus.quick_view"))  # "Quick View"
        menu.addSeparator()
        refresh_action = menu.addAction(tr("ui.menus.refresh_folder_files"))
        menu.addSeparator()
        # Delete file option
        delete_action = menu.addAction(tr("ui.menus.delete_file"))  # "Delete File"
        
        action = menu.exec(self.viewport().mapToGlobal(pos))
        f = self.main.files[row]
        file_path = str(f['path'])
        # Handle Quick View action
        if action == quick_view_action:
            # Only for PDF files
            ext = os.path.splitext(file_path)[1].lower()
            if ext != '.pdf':
                QMessageBox.warning(self, tr("messages.warnings.unsupported_format"), tr("messages.errors.unsupported_format"))
                return
            
            # Use the standalone QuickView class
            try:
                from ui.quick_view import QuickViewDialog
                dialog = QuickViewDialog.show_quick_view(file_path, self)
                return
            except ImportError:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.could_not_load_pdf_viewer"))
                return
        # Existing code...
        elif action == open_action:
            result = open_file_cross_platform(file_path)
            if result is not True:
                success, error_msg = result
                if not success:
                    QMessageBox.critical(self, tr("messages.errors.error"), 
                                       tr("messages.errors.could_not_open_file", error=error_msg))
        elif action == reveal_action:
            result = reveal_file_cross_platform(file_path)
            if result is not True:
                success, error_msg = result
                if not success:
                    QMessageBox.critical(self, tr("messages.errors.error"), 
                                       tr("messages.errors.could_not_reveal_file", error=error_msg))
        elif action == refresh_action:
            folder = self.main.settings.value('last_folder', '')
            if folder:
                # D'abord essayer le chemin exact tel qu'il est stocké
                if pathlib.Path(folder).exists():
                    self.main._load_files(folder)
                else:
                    # Seulement si le chemin exact n'existe pas, utiliser la logique de fallback
                    best_folder = self.main._get_fallback_folder_path(folder)
                    self.main._load_files(best_folder)
        elif action == delete_action:
            # Ask for confirmation before deleting
            from utils import delete_file_cross_platform
            
            # Get file name for the confirmation message
            file_name = os.path.basename(file_path)
            confirm_msg = tr("messages.confirmations.delete_file", file=file_name)
            confirm_title = tr("messages.confirmations.confirm_delete")
            
            # Show confirmation dialog
            reply = QMessageBox.question(self, confirm_title, confirm_msg,
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                result = delete_file_cross_platform(file_path)
                if result is True:
                    # Refresh file list to reflect the deletion
                    current_folder = self.main.settings.value('last_folder', '')
                    if current_folder and pathlib.Path(current_folder).exists():
                        self.main._load_files(current_folder)
                    # Show success message
                    success_msg = tr("messages.success.file_deleted", file=file_name)
                    QMessageBox.information(self, tr("messages.success.success"), success_msg)
                else:
                    # Show error message
                    _, error_msg = result
                    error_dialog_msg = tr("messages.errors.could_not_delete_file", file=file_name, error=error_msg)
                    QMessageBox.critical(self, tr("messages.errors.error"), error_dialog_msg)

class AlbumTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def mouseMoveEvent(self, event):
        it = self.itemAt(event.pos())
        if not it:
            return
        # print(f"[DEBUG][DnD] Drag value: {it.text()}")  # Debug disabled by default
        mime = QMimeData()
        mime.setData('application/x-comic-meta', QByteArray(it.text().encode()))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

    def _show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row < 0:
            return
        
        # Get the album metadata for the selected row
        item = self.item(row, 0)
        if not item:
            return
        
        meta = item.data(Qt.UserRole)
        if not meta:
            return
        
        menu = QMenu(self)
        
        # Add Amazon search action
        amazon_action = menu.addAction(tr("ui.menus.search_on_amazon"))
        
        # Execute menu and handle action
        action = menu.exec(self.viewport().mapToGlobal(pos))
        
        if action == amazon_action:
            # Use main window's Amazon search functionality
            if hasattr(self.main, '_search_amazon_for_album'):
                self.main._search_amazon_for_album(meta)

# ---------- Settings Dialog ----------
class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialogs.settings.title"))        # Set dialog icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.layout = QFormLayout(self)

        self.settings = settings or QSettings("ComicsRename", "App")
        
        # Language selection
        self.language_combo = QComboBox()
        supported_langs = get_supported_languages()
        current_lang = get_current_language()
        
        for code, name in supported_langs.items():
            self.language_combo.addItem(name, code)
            if code == current_lang:
                self.language_combo.setCurrentText(name)
        
        self.layout.addRow(tr("dialogs.settings.language_label"), self.language_combo)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["BDGest", "ComicVine"])
        default_provider = self.settings.value("default_provider", "BDGest")
        idx = self.provider_combo.findText(default_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.layout.addRow(tr("ui.labels.provider") + " :", self.provider_combo)

        self.debug_cb = QCheckBox()
        self.debug_cb.setChecked(self.settings.value('debug', 'false') == 'true')
        self.layout.addRow("Debug mode", self.debug_cb)

        self.verbose_cb = QCheckBox()
        self.verbose_cb.setChecked(self.settings.value('verbose', 'false') == 'true')
        self.layout.addRow("Verbose mode", self.verbose_cb)

        self.recursive_cb = QCheckBox()
        self.recursive_cb.setChecked(self.settings.value('recursive', 'false') == 'true')
        self.recursive_cb.setToolTip(tr("ui.tooltips.recursive_folder_scan"))
        self.layout.addRow(tr("ui.labels.recursive_folder_scan"), self.recursive_cb)

        self.bdgest_user = QLineEdit(self.settings.value('bdgest_user', ''))
        self.layout.addRow(tr("dialogs.settings.username"), self.bdgest_user)
        self.bdgest_pass = QLineEdit(self.settings.value('bdgest_pass', ''))
        self.bdgest_pass.setEchoMode(QLineEdit.Password)
        self.layout.addRow(tr("dialogs.settings.password"), self.bdgest_pass)

        self.comicvine_api = QLineEdit(self.settings.value('comicvine_api', ''))
        self.layout.addRow(tr("dialogs.settings.api_key"), self.comicvine_api)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)
        
        # Connect language change
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
    
    def _on_language_changed(self):
        """Handle language change"""
        selected_code = self.language_combo.currentData()
        if selected_code and selected_code != get_current_language():
            set_language(selected_code)
            # Show message about restart requirement
            QMessageBox.information(
                self, 
                "Language Change", 
                "Language will be applied after restarting the application."
            )

    def accept(self):
        # Save language first
        selected_code = self.language_combo.currentData()
        if selected_code:
            set_language(selected_code)
            
        self.settings.setValue("default_provider", self.provider_combo.currentText())
        self.settings.setValue("debug", 'true' if self.debug_cb.isChecked() else 'false')
        self.settings.setValue("verbose", 'true' if self.verbose_cb.isChecked() else 'false')
        self.settings.setValue("recursive", 'true' if self.recursive_cb.isChecked() else 'false')
        self.settings.setValue("bdgest_user", self.bdgest_user.text())
        self.settings.setValue("bdgest_pass", self.bdgest_pass.text())
        self.settings.setValue("comicvine_api", self.comicvine_api.text())
        super().accept()

# ---------- Main GUI ----------
class ComicRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app.title"))
        self.resize(1400, 800)        # Set application icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.settings = QSettings("ComicsRename", "App")
        
        # Initialize debug/verbose early to avoid AttributeError
        self.debug = self.settings.value('debug', 'false') == 'true'
        self.verbose = self.settings.value('verbose', 'false') == 'true'
        
        self.default_provider = self.settings.value("default_provider", "BDGest")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["BDGest", "ComicVine"])
        idx = self.provider_combo.findText(self.default_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.provider_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self.files = []
        self._source = self.provider_combo.currentText()
        self.issues_by_series = defaultdict(list)
        self._populating = False
        self._bdgest_album_results = []
        self._bdgest_series_results = []  # New: store series search results
        self._comicvine_series_results = []  # New: store Comic Vine series search results
        self._original_cover_pixmap = None  # Store original pixmap for rescaling
        self._build_ui()
        self.series_cover_url = ''

        # Synchronize source_combo with user preference
        default_provider = self.settings.value("default_provider", "BDGest")
        idx = self.source_combo.findText(default_provider)
        if idx >= 0:
            self.source_combo.setCurrentIndex(idx)
        self._source = self.source_combo.currentText()
        
        # Show/hide SeriesName checkbox based on initial provider
        if self._source in ['BDGest', 'ComicVine']:
            self.series_name_cb.setVisible(True)
        else:
            self.series_name_cb.setVisible(False)

        # Recharge automatiquement le dernier dossier utilisé
        last_folder = self.settings.value("last_folder", "")
        if last_folder:
            # D'abord essayer le chemin exact tel qu'il est stocké
            if pathlib.Path(last_folder).exists():
                self._load_files(last_folder)
            else:
                # Seulement si le chemin exact n'existe pas, utiliser la logique de fallback
                best_folder = self._get_fallback_folder_path(last_folder)
                self._load_files(best_folder)

    def keyPressEvent(self, event):
        """Handle key press events - Escape cancels search"""
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_Escape and self._search_in_progress:
            # Cancel search with Escape key
            self._search_cancelled = True
            self._restore_search_ui()
            self.detail_text.setHtml("<i>Search cancelled by user (Escape key)</i>")
            print("[INFO] Search operation cancelled by user (Escape key)")
        else:
            # Pass other events to parent
            super().keyPressEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        ctrl = QHBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems(['ComicVine', 'BDGest'])
        self.search_bar = DroppableLineEdit()
        self.search_btn = QPushButton(tr("ui.buttons.search"))
        self.dir_btn = QPushButton(tr("ui.buttons.browse"))
        self.series_name_cb = QCheckBox(tr("ui.labels.series_name_mode"))  # New checkbox for BDGest and ComicVine series search
        self.series_name_cb.setToolTip(tr("ui.tooltips.series_name_mode"))
        self.series_name_cb.setVisible(False)  # Hidden by default, shown only for BDGest and ComicVine
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedWidth(30)
        self.settings_btn.setToolTip(tr("ui.tooltips.settings"))
        self.rename_btn = QPushButton(tr("ui.buttons.rename"))
        self.rename_btn.setEnabled(False)  # Disabled by default until both file and album are selected
        
        # Add search cancellation support
        self._search_cancelled = False
        self._search_in_progress = False
        
        for w in (self.source_combo, self.search_bar, self.search_btn, self.dir_btn, self.series_name_cb, self.settings_btn):
            ctrl.addWidget(w)
        layout.addLayout(ctrl)

        splitter_main = QSplitter(Qt.Horizontal)

        # --- Folder display ---
        file_panel = QWidget()
        file_panel_layout = QVBoxLayout(file_panel)
        file_panel_layout.setContentsMargins(0, 0, 0, 0)
        folder_display_layout = QHBoxLayout()
        self.folder_display = EditableFolderLineEdit(main_window=self)
        # Add the rename folder button
        self.folder_rename_btn = QPushButton("✎")
        self.folder_rename_btn.setToolTip(tr("ui.tooltips.rename_folder"))
        self.folder_rename_btn.setFixedWidth(30)
        self.folder_rename_btn.setEnabled(False)  # Disabled by default
        self.folder_rename_btn.clicked.connect(self._rename_folder_to_serie)
        folder_display_layout.addWidget(self.folder_display)
        folder_display_layout.addWidget(self.folder_rename_btn)
        file_panel_layout.addLayout(folder_display_layout)
        self.file_table = FileTable(self)
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(['Name','Ext','Size','Folder'])
        self.file_table.setSortingEnabled(True)
        file_panel_layout.addWidget(self.file_table)
        splitter_main.addWidget(file_panel)
        # --- End block ---

        splitter_right = QSplitter(Qt.Vertical)
        alb_widget = QWidget()
        alb_layout = QVBoxLayout(alb_widget)
        self.series_combo = QComboBox()
        self.album_table = AlbumTable(self)
        self.album_table.setColumnCount(1)
        self.album_table.setHorizontalHeaderLabels(['Albums'])
        self.album_table.setSortingEnabled(True)
        alb_layout.addWidget(self.series_combo)
        alb_layout.addWidget(self.album_table)
        splitter_right.addWidget(alb_widget)

        # Albums Management Area (regrouped album details + cover)
        albums_mgmt_widget = QWidget()
        albums_mgmt_widget.setWindowTitle("Albums Management")  # For potential future groupbox styling
        albums_mgmt_layout = QHBoxLayout(albums_mgmt_widget)
        
        # Album Details Section
        self.detail_text = QTextBrowser()  # Use QTextBrowser instead of QTextEdit for better link support
        
        # Configure QTextBrowser for better link handling and styling
        self.detail_text.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse
        )
        # QTextBrowser has built-in support for opening external links
        self.detail_text.setOpenExternalLinks(True)
        
        # Album Cover Section
        self.detail_image = QLabel()
        # Configure image label to be responsive and centered
        self.detail_image.setScaledContents(False)  # Don't force scaling to fill
        self.detail_image.setAlignment(Qt.AlignCenter)  # Center the image
        self.detail_image.setMinimumSize(50, 50)  # Small minimum size
        self.detail_image.setMaximumSize(300, 400)  # Reasonable maximum
        self.detail_image.setSizePolicy(self.detail_image.sizePolicy().horizontalPolicy(), 
                                       self.detail_image.sizePolicy().verticalPolicy())
        # Make cover image clickable for Amazon search
        self.detail_image.setCursor(Qt.PointingHandCursor)
        self.detail_image.mousePressEvent = self._on_cover_image_clicked
        
        # Add both sections to the albums management area
        albums_mgmt_layout.addWidget(self.detail_text, 2)  # Album details take 2/3 of space
        albums_mgmt_layout.addWidget(self.detail_image, 1)  # Album cover takes 1/3 of space
        
        # Add the albums management area to the right splitter
        splitter_right.addWidget(albums_mgmt_widget)

        splitter_main.addWidget(splitter_right)
        layout.addWidget(splitter_main)
        layout.addWidget(self.rename_btn)

        # Store splitter reference for image resize handling
        self.splitter_right = splitter_right

        self.source_combo.currentTextChanged.connect(self._change_source)
        self.dir_btn.clicked.connect(self._choose_folder)
        self.search_btn.clicked.connect(self._search_or_cancel)
        self.search_bar.returnPressed.connect(self._search)
        self.series_combo.currentTextChanged.connect(self._on_series_selection_changed)
        self.album_table.cellClicked.connect(self._show_details)
        self.album_table.cellClicked.connect(self._enable_folder_rename_btn)
        self.album_table.selectionModel().selectionChanged.connect(self._on_album_selection_changed)
        self.rename_btn.clicked.connect(self._rename_selected)
        self.settings_btn.clicked.connect(self._open_settings)
        
        # Connect splitter movement to image resize
        splitter_right.splitterMoved.connect(self._update_cover_image_size)

        # Connect selection change to update folder display
        self.file_table.selectionModel().selectionChanged.connect(self._update_folder_display)

        # Adjust column widths after UI is built
        self._adjust_table_columns()

    def _adjust_table_columns(self):
        # Adjust file_table: set 'Name' column to fit contents, others to reasonable defaults
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        # Optionally, set minimum width for 'Name' column
        self.file_table.setColumnWidth(0, max(200, self.file_table.sizeHintForColumn(0)))

        # Adjust album_table: single column stretches to fill available space
        self.album_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def _restore_session(self):
        folder = self.settings.value('last_folder','')
        fc = self.settings.value('file_cols')
        if fc:
            for i,w in enumerate(map(int,fc.split(','))):
                self.file_table.setColumnWidth(i,w)
        ac = self.settings.value('album_cols')
        if ac:
            self.album_table.setColumnWidth(0,int(ac))
        # Note: debug/verbose are now initialized earlier in __init__
        if folder:
            # D'abord essayer le chemin exact tel qu'il est stocké
            if pathlib.Path(folder).exists():
                self._load_files(folder)
            else:
                # Seulement si le chemin exact n'existe pas, utiliser la logique de fallback
                best_folder = self._get_fallback_folder_path(folder)
                self._load_files(best_folder)

    def closeEvent(self,ev):
        self.settings.setValue('last_folder', self.settings.value('last_folder'))
        widths=[self.file_table.columnWidth(i) for i in range(self.file_table.columnCount())]
        self.settings.setValue('file_cols',','.join(map(str,widths)))
        self.settings.setValue('album_cols',str(self.album_table.columnWidth(0)))
        super().closeEvent(ev)

    def _scale_image_to_fit(self, pixmap):
        """Scale the image to fit the available space while maintaining aspect ratio and centering"""
        if not pixmap or pixmap.isNull():
            return pixmap
        
        # Get available size (with some margin)
        available_width = max(100, self.detail_image.width() - 20)
        available_height = max(100, self.detail_image.height() - 20)
        
        # If the label is too small (not yet properly sized), use reasonable defaults
        if available_width < 50 or available_height < 50:
            available_width = 250
            available_height = 300
        
        # Get original image dimensions
        original_width = pixmap.width()
        original_height = pixmap.height()
        
        # Calculate scaling factors to fit within available space
        scale_x = available_width / original_width
        scale_y = available_height / original_height
        
        # Use the smaller scale factor to maintain aspect ratio
        scale_factor = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Scale the image maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            new_width, new_height, 
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        return scaled_pixmap

    def _change_source(self,src):
        self._source=src
        self.series_combo.clear()
        self.album_table.clearContents();self.album_table.setRowCount(0); self.series_cover_url = ''
        self.detail_text.clear();self.detail_image.clear();self._original_cover_pixmap = None
        if self.folder_rename_btn is not None:
            self.folder_rename_btn.setEnabled(False)
        
        # Show/hide SeriesName checkbox based on provider
        if src in ['BDGest', 'ComicVine']:
            self.series_name_cb.setVisible(True)
        else:
            self.series_name_cb.setVisible(False)
            self.series_name_cb.setChecked(False)  # Reset checkbox when hiding

    def _choose_folder(self):
        current_folder = self.settings.value('last_folder', '')
        # Ajout d'une boîte de dialogue personnalisée pour proposer /Volumes
        msg = QMessageBox(self)
        msg.setWindowTitle("Sélection du dossier")
        msg.setText("Où souhaitez-vous commencer la navigation ?")
        btn_volumes = msg.addButton("Disques externes (/Volumes)", QMessageBox.ActionRole)
        btn_last = msg.addButton("Dernier dossier utilisé", QMessageBox.ActionRole)
        btn_home = msg.addButton("Dossier personnel", QMessageBox.ActionRole)
        btn_cancel = msg.addButton(QMessageBox.Cancel)
        msg.exec()
        if msg.clickedButton() == btn_volumes:
            start_dir = "/Volumes"
        elif msg.clickedButton() == btn_last:
            if current_folder:
                start_dir = self._get_fallback_folder_path(current_folder)
            else:
                QMessageBox.information(self, "Information", "Aucun dossier précédent enregistré. Utilisation du dossier personnel.")
                start_dir = str(pathlib.Path.home())
        elif msg.clickedButton() == btn_home:
            start_dir = str(pathlib.Path.home())
        else:
            return  # Cancelled

        dialog = QFileDialog(self, 'Select Folder', start_dir)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # <-- This enables the "Up" button
        if dialog.exec():
            folders = dialog.selectedFiles()
            if folders:
                d = folders[0]
                self.settings.setValue('last_folder', d)
                self._load_files(d)

    def _load_files(self, folder):
        """
        Load comic files from the specified folder.
        
        The recursive setting controls whether to scan only the current folder
        or to recursively scan all subfolders and their subdirectories.
        
        Args:
            folder (str): Path to the folder to scan
        """
        self._populating = True
        self.file_table.blockSignals(True)
        # Filter out files whose name starts with '.'
        # Get recursive folder scan setting from user preferences
        # When True: recursively scans all subfolders and their subdirectories
        # When False: only scans files in the current folder
        recursive = self.settings.value('recursive', 'false') == 'true'
        all_files = scan_comic_files(folder, recursive)
        self.files = [f for f in all_files if not f['name'].startswith('.')]
        self.file_table.clearContents()
        self.file_table.setRowCount(len(self.files))
        for r, f in enumerate(self.files):
            self.file_table.setItem(r, 0, QTableWidgetItem(f['name']))
            self.file_table.setItem(r, 1, QTableWidgetItem(f['ext']))
            self.file_table.setItem(r, 2, QTableWidgetItem(f['size']))
            self.file_table.setItem(r, 3, QTableWidgetItem(f['folder']))
        self.file_table.blockSignals(False)
        self._populating = False
        # Update folder display to root (show only folder name)
        self.folder_display.setText(os.path.basename(folder.rstrip('/\\')))
        # Adjust columns after loading files
        self._adjust_table_columns()

    def _search_or_cancel(self):
        """Handle search button click - either start search or cancel current search"""
        if self._search_in_progress:
            # Cancel current search
            self._search_cancelled = True
            self._restore_search_ui()
            self.detail_text.setHtml("<i>Search cancelled by user</i>")
            print("[INFO] Search operation cancelled by user")
        else:
            # Start new search
            self._search()

    def _search(self):
        q = self.search_bar.text().strip()
        if not q:
            return
            
        # Set search in progress and update button
        self._search_cancelled = False
        self._search_in_progress = True
        self.search_btn.setText("⏹️ Cancel Search")
        self.search_btn.setToolTip("Cancel current search operation")
        
        # Clear previous results
        self.series_combo.clear()
        self.album_table.clearContents()
        self.album_table.setRowCount(0)
        self.series_cover_url = ''
        self.detail_text.clear()
        self.detail_image.clear()
        self._original_cover_pixmap = None

        provider = PROVIDERS[self._source]
        # Pass debug/verbose to provider if supported
        debug = self.settings.value('debug', 'false') == 'true'
        verbose = self.settings.value('verbose', 'false') == 'true'
        
        # Only call search_series for providers in non-SeriesName mode
        if (self._source == 'ComicVine' and not self.series_name_cb.isChecked()) or (self._source == 'BDGest' and not self.series_name_cb.isChecked()):
            try:
                # Try with debug parameter first
                series_list = provider.search_series(q, debug=debug)
            except TypeError:
                # Fallback to old interface if debug parameter not supported
                series_list = provider.search_series(q)
            
            # Check for "too many results" error early (BDGest specific)
            if self._source == 'BDGest' and series_list and len(series_list) == 1 and series_list[0].get('error') == 'too_many_results':
                # Use internationalized error messages
                title = tr("messages.errors.too_many_results_title")
                message = tr("messages.errors.too_many_results_message")
                hint = tr("messages.errors.too_many_results_hint")
                full_message = f"{message}\n\n{hint}"
                
                QMessageBox.warning(self, title, full_message)
                # Restore UI and exit early
                self._restore_search_ui()
                return
            
            # Check for "authentication failed" error early (BDGest specific)
            if self._source == 'BDGest' and series_list and len(series_list) == 1 and series_list[0].get('error') == 'authentication_failed':
                # Use internationalized error messages
                title = tr("messages.errors.authentication_failed_title")
                message = tr("messages.errors.authentication_failed_message")
                hint = tr("messages.errors.authentication_failed_hint")
                full_message = f"{message}\n\n{hint}"
                
                QMessageBox.critical(self, title, full_message)
                # Restore UI and exit early
                self._restore_search_ui()
                return
        else:
            # For BDGest or ComicVine in SeriesName mode, we'll call search_series_only later
            series_list = []

        self.issues_by_series.clear()
        self._bdgest_album_results = []

        # First check if SeriesName mode is enabled for either provider
        if self.series_name_cb.isChecked():
            # SERIES MODE: Use series-only search for both providers
            if debug:
                print(f"[DEBUG][UI] Using series-only mode for {self._source}")
                
            # Check for cancellation before starting series operations
            if self._search_cancelled:
                return
                
            # Use series-only search
            series_results = provider.search_series_only(q, debug=debug, verbose=verbose) \
                if hasattr(provider, 'search_series_only') \
                else []
            
            # Check for "too many results" error in series search
            series_error_handled = False  # Track if we handled an error for series
            if series_results and len(series_results) == 1 and series_results[0].get('error') == 'too_many_results':
                # Use internationalized error messages
                title = tr("messages.errors.too_many_results_title")
                message = tr("messages.errors.too_many_results_message")
                hint = tr("messages.errors.too_many_results_hint")
                full_message = f"{message}\n\n{hint}"
                
                QMessageBox.warning(self, title, full_message)
                # Don't populate any results
                series_results = []
                series_error_handled = True
            
            # Check for "authentication failed" error in series search
            if series_results and len(series_results) == 1 and series_results[0].get('error') == 'authentication_failed':
                # Use internationalized error messages
                title = tr("messages.errors.authentication_failed_title")
                message = tr("messages.errors.authentication_failed_message")
                hint = tr("messages.errors.authentication_failed_hint")
                full_message = f"{message}\n\n{hint}"
                
                QMessageBox.critical(self, title, full_message)
                # Don't populate any results and restore UI
                series_results = []
                series_error_handled = True
                self._restore_search_ui()
                return
            
            # Store series results based on provider
            if self._source == 'BDGest':
                self._bdgest_series_results = series_results
                self._bdgest_album_results = []  # Clear album results when searching series
            else:  # ComicVine
                self._comicvine_series_results = series_results
                self.issues_by_series.clear()  # Clear ComicVine issues
            
            # Populate series dropdown with series results
            for series in series_results:
                # Check for cancellation during series population
                if self._search_cancelled:
                    if debug:
                        print(f"[DEBUG][UI] Search cancelled during {self._source} series population")
                    return
                    
                # Get series name based on provider
                if self._source == 'BDGest':
                    series_name = series.get('serie_name', 'Unknown Series')
                else:  # ComicVine
                    series_name = series.get('serie_name', 'Unknown Series')  # ComicVineProvider normalizes this field
                    
                if series_name and series_name != 'Unknown Series':
                    self.series_combo.addItem(series_name)
                    idx = self.series_combo.count() - 1
                    # Store the full series data for later use
                    self.series_combo.setItemData(idx, series, Qt.UserRole)
                    
                # Process UI events to allow cancellation
                QApplication.processEvents()
            
            # Inform user if no series results (but only if we didn't handle an error)
            if not series_results and not series_error_handled:
                title = tr("messages.info.no_result")
                message = tr("messages.errors.no_series_found")
                QMessageBox.information(self, title, message)
            else:
                # Clear album table since we're in series mode
                self.album_table.clearContents()
                self.album_table.setRowCount(0)
                
                # Show user how many series were found and instruction to select one
                if self.series_combo.count() > 0:
                    series_count = self.series_combo.count()
                    instruction_html = f"<b>🔍 Recherche terminée</b><br><br>"
                    instruction_html += f"<b>{series_count} série(s) trouvée(s)</b><br><br>"
                    if series_count == 1:
                        instruction_html += f"<i>� Chargement des albums de la série unique...</i>"
                    else:
                        instruction_html += f"<i>📚 Chargement des albums de la première série...</i>"
                    self.detail_text.setHtml(instruction_html)
                    self.detail_image.clear()
                    
                    # Auto-load albums for the first series (optimal UX)
                    # The first series is automatically selected by default in the dropdown
                    first_series_name = self.series_combo.itemText(0)
                    if debug:
                        print(f"[DEBUG][UI] Auto-loading albums for first series: '{first_series_name}' ({self._source} series mode)")
                    
                    # Trigger album population for the first series
                    self._populate_albums(first_series_name)
                    
                    if debug:
                        print(f"[DEBUG][UI] Series mode completed: {series_count} series found, first series albums auto-loaded")
        
        elif self._source == 'ComicVine' and not self.series_name_cb.isChecked():
            # COMICVINE NORMAL MODE: Use full search (only when NOT in series mode)
            from comicVine_scraper_api import search_comicvine_issues
            # Use the series_list already fetched by provider.search_series()
            volumes = series_list
            if volumes:
                if debug:
                    print(f"[DEBUG][UI] {len(volumes)} volumes found for '{q}' - loading all albums immediately")
                
                # Fetch albums for all series immediately - optimized for speed
                total_volumes = len(volumes)
                
                # Show initial loading message
                self.detail_text.setHtml(f"<i>Loading albums from {total_volumes} series...</i>")
                QApplication.processEvents()  # Single UI update at start
                
                for vol_idx, series in enumerate(volumes, 1):
                    # Check for cancellation
                    if self._search_cancelled:
                        if debug:
                            print("[DEBUG][UI] Search cancelled during ComicVine album fetching")
                        return
                    
                    series_name = series.get('name', 'Unknown')
                    volume_id = str(series.get('id', ''))
                    
                    if debug:
                        print(f"[DEBUG][UI] Fetching albums for volume {vol_idx}/{total_volumes}: {series_name}")
                    
                    # Update progress in UI
                    self.detail_text.setHtml(f"<i>Loading albums from {total_volumes} series... ({vol_idx}/{total_volumes})</i>")
                    QApplication.processEvents()  # Allow UI updates and cancellation
                    
                    # Fetch issues for this series without UI updates in the loop for maximum speed
                    issues = provider.search_albums(volume_id, debug=debug)
                    for issue in issues:
                        issue['volume'] = {'name': series_name}
                        self.issues_by_series.setdefault(series_name, []).append(issue)
                
                # Clear loading message after all fetching is complete
                self.detail_text.clear()
                
                if not self.issues_by_series:
                    QMessageBox.warning(self, tr("messages.info.no_result"), tr("messages.errors.no_results"))
                    return
                
                # Populate series dropdown with album counts
                for s in sorted(self.issues_by_series):
                    self.series_combo.addItem(f"{s} ({len(self.issues_by_series[s])})")
                
                # Auto-select the first series to show albums immediately
                if self.series_combo.count() > 0:
                    self.series_combo.setCurrentIndex(0)
                    # Trigger the selection manually to populate albums
                    first_series_text = self.series_combo.currentText()
                    self._populate_albums(first_series_text)
                
                if debug:
                    total_albums = sum(len(albums) for albums in self.issues_by_series.values())
                    print(f"[DEBUG][UI] Loaded {total_albums} total albums across {len(self.issues_by_series)} series")
                    print(f"[DEBUG][UI] Auto-selected first series: {first_series_text if self.series_combo.count() > 0 else 'None'}")
            else:
                if debug:
                    print(f"[DEBUG][UI] No volumes found for '{q}', fallback to issues search")
                issues = search_comicvine_issues(q)
                if debug:
                    print(f"[DEBUG][UI] {len(issues)} issues found for '{q}'")
                issues_by_series = {}
                for it in issues:
                    s = (it.get('volume') or {}).get('name', 'Sans série')
                    issues_by_series.setdefault(s, []).append(it)
                for s in sorted(issues_by_series):
                    self.series_combo.addItem(f"{s} ({len(issues_by_series[s])})")
                self.issues_by_series = issues_by_series
                if not issues_by_series:
                    QMessageBox.warning(self, 'Résultat', 'Aucun album trouvé pour cette recherche.')
        
        else:  # BDGest NORMAL MODE
            # Check for cancellation before starting BDGest operations
            if self._search_cancelled:
                return
                
            # Use default album search (normal mode)
            albums = []
            error_handled = False  # Track if we handled an error
            
            # First check for errors in series_list before filtering
            if series_list and len(series_list) == 1:
                error_item = series_list[0]
                if error_item.get('error') == 'authentication_failed':
                    # Use internationalized error messages
                    title = tr("messages.errors.authentication_failed_title")
                    message = tr("messages.errors.authentication_failed_message")
                    hint = tr("messages.errors.authentication_failed_hint")
                    full_message = f"{message}\n\n{hint}"
                    
                    QMessageBox.critical(self, title, full_message)
                    # Don't populate any results and restore UI
                    error_handled = True
                    self._restore_search_ui()
                    return
                elif error_item.get('error') == 'too_many_results':
                    # Use internationalized error messages
                    title = tr("messages.errors.too_many_results_title")
                    message = tr("messages.errors.too_many_results_message")
                    hint = tr("messages.errors.too_many_results_hint")
                    full_message = f"{message}\n\n{hint}"
                    
                    QMessageBox.warning(self, title, full_message)
                    # Don't populate any results
                    error_handled = True
                    self._restore_search_ui()
                    return
                
                for album in series_list:
                    s = album.get('serie_name', '')
                    if s:
                        albums.append(album)
                
                # Check for "too many results" error (legacy fallback)
                if albums and len(albums) == 1 and albums[0].get('error') == 'too_many_results':
                    # Use internationalized error messages
                    title = tr("messages.errors.too_many_results_title")
                    message = tr("messages.errors.too_many_results_message")
                    hint = tr("messages.errors.too_many_results_hint")
                    full_message = f"{message}\n\n{hint}"
                    
                    QMessageBox.warning(self, title, full_message)
                    # Don't populate any results
                    albums = []
                    error_handled = True
                
                self._bdgest_album_results = albums
                if self._source == 'BDGest':
                    self._bdgest_series_results = []  # Clear series results when searching albums
                else:  # ComicVine
                    self._comicvine_series_results = []  # Clear ComicVine series results when searching albums
                
                series_seen = set()
                for album in albums:
                    # Check for cancellation during album processing
                    if self._search_cancelled:
                        if debug:
                            print("[DEBUG][UI] Search cancelled during BDGest album processing")
                        return
                        
                    s = album.get('serie_name', '')
                    serie_id = album.get('series_id', '')
                    if s and s not in series_seen:
                        self.series_combo.addItem(s)
                        idx = self.series_combo.count() - 1
                        self.series_combo.setItemData(idx, serie_id, Qt.UserRole)
                        series_seen.add(s)
                        
                    # Process UI events periodically
                    if len(series_seen) % 5 == 0:  # Every 5 items
                        QApplication.processEvents()
                # Inform user if no BDGest results (but only if we didn't handle an error)
                if not albums and not error_handled:
                    title = tr("messages.info.no_result")
                    message = tr("messages.errors.no_albums_found")
                    QMessageBox.information(self, title, message)
        
        # Restore UI state after search completion
        self._restore_search_ui()

    def _restore_search_ui(self):
        """Restore UI elements after search completion or cancellation"""
        self._search_in_progress = False
        self.search_btn.setText(tr("ui.buttons.search"))
        self.search_btn.setToolTip("")  # Clear tooltip or set default

    def _enable_folder_rename_btn(self, *args):
        self.folder_rename_btn.setEnabled(True)

    def _on_album_selection_changed(self, selected, deselected):
        # Enable if any row is selected, else disable
        selected_rows = self.album_table.selectionModel().selectedRows()
        self.folder_rename_btn.setEnabled(bool(selected_rows))
        
        # Update rename button state based on both file and album selections
        self._update_rename_button_state()

    def _update_rename_button_state(self):
        """Update rename button state - enabled only when both file and album are selected"""
        # Check if file is selected
        file_selected = bool(self.file_table.selectionModel().selectedRows())
        
        # Check if album is selected
        album_selected = bool(self.album_table.selectionModel().selectedRows())
        
        # Enable rename button only when both are selected
        both_selected = file_selected and album_selected
        self.rename_btn.setEnabled(both_selected)
        
        # Optional: Update button tooltip to provide user feedback
        if not file_selected and not album_selected:
            self.rename_btn.setToolTip("Select both a file and an album to enable renaming")
        elif not file_selected:
            self.rename_btn.setToolTip("Select a file to rename")
        elif not album_selected:
            self.rename_btn.setToolTip("Select an album for renaming")
        else:
            self.rename_btn.setToolTip("Rename selected file using album metadata")

    def _on_series_selection_changed(self, txt):
        """Handle series selection change - close dropdown and populate albums"""
        if not txt:
            return
            
        # Close the dropdown to provide immediate visual feedback
        self.series_combo.hidePopup()
        
        # Force UI update to show dropdown is closed
        QApplication.processEvents()
        
        # Now populate albums for the selected series
        self._populate_albums(txt)

    def _populate_albums(self, txt):
        if not txt:
            return
            
        # Check for cancellation at the start
        if hasattr(self, '_search_cancelled') and self._search_cancelled:
            return
            
        # Debug output
        debug = self.debug_cb.isChecked() if hasattr(self, 'debug_cb') else False
        if debug:
            print(f"[DEBUG][UI] _populate_albums called with series: '{txt}' (provider: {self._source})")
            
        self.album_table.clearContents()
        self.album_table.setRowCount(0)
        self.series_cover_url = ''

        provider = PROVIDERS[self._source]

        def format_num(n):
            try:
                n_int = int(n)
                return f"{n_int:02d}"
            except Exception:
                return str(n)

        if self._source == 'ComicVine':
            # Check if we're in series mode (SeriesName checkbox checked)
            if self.series_name_cb.isChecked() and self._comicvine_series_results:
                # In series mode - fetch and display albums for the selected series
                # Find the index of the series by name (txt parameter)
                series_index = -1
                for i in range(self.series_combo.count()):
                    if self.series_combo.itemText(i) == txt:
                        series_index = i
                        break
                
                if debug:
                    print(f"[DEBUG][UI] Looking for series '{txt}' in dropdown - found at index {series_index}")
                
                if series_index >= 0:
                    series_data = self.series_combo.itemData(series_index, Qt.UserRole)
                    if debug:
                        print(f"[DEBUG][UI] Found series data: {series_data is not None}")
                    if series_data:
                        volume_id = series_data.get('volume_id') or str(series_data.get('id', ''))
                        series_name = series_data.get('serie_name', 'Unknown')
                        
                        if volume_id and series_name:
                            # Show series details
                            html = "<b>Volume sélectionné :</b><br><ul>"
                            for k, v in series_data.items():
                                if v and str(v).strip():
                                    html += f"<li><b>{k}</b> : {v}</li>"
                            html += "</ul><br><i>Récupération des issues...</i>"
                            self.detail_text.setHtml(html)
                            
                            # Set cover image if available
                            if series_data.get('image'):
                                cover_url = series_data.get('image', {}).get('medium_url', '')
                                if cover_url:
                                    try:
                                        data = requests.get(cover_url, timeout=10).content
                                        pm = QPixmap()
                                        pm.loadFromData(data)
                                        # Store original for future rescaling
                                        self._original_cover_pixmap = pm
                                        # Scale to fit available space while maintaining aspect ratio
                                        scaled_pm = self._scale_image_to_fit(pm)
                                        self.detail_image.setPixmap(scaled_pm)
                                    except Exception as e:
                                        print("[ERROR] ComicVine image load failed:", e)
                                        self.detail_image.clear()
                                else:
                                    self.detail_image.clear()
                            
                            # Fetch issues for this volume
                            try:
                                # Check for cancellation
                                if self._search_cancelled:
                                    return
                                
                                # Show progress message
                                self.detail_text.setHtml(html.replace("<i>Récupération des issues...</i>", "<i>Récupération des issues en cours...</i>"))
                                QApplication.processEvents()  # Allow UI update and cancellation
                                
                                debug = self.debug_cb.isChecked() if hasattr(self, 'debug_cb') else False
                                verbose = self.verbose_cb.isChecked() if hasattr(self, 'verbose_cb') else False
                                
                                # Use ComicVine provider to get volume issues
                                provider = PROVIDERS[self._source]
                                issues = provider.search_albums(volume_id, debug=debug)
                                
                                # Check for cancellation after fetching
                                if self._search_cancelled:
                                    return
                                    
                                # Clear and populate album table
                                self.album_table.clearContents()
                                self.album_table.setRowCount(len(issues))
                                
                                for r, issue in enumerate(issues):
                                    t = issue.get('name') or 'Untitled'
                                    n = issue.get('issue_number') or '?'
                                    n_fmt = format_num(n)
                                    y = (issue.get('cover_date') or '')[:4]
                                    val = f"{series_name} - {n_fmt} - {t} ({y})"
                                    itm = QTableWidgetItem(val)
                                    itm.setData(Qt.UserRole, issue)
                                    self.album_table.setItem(r, 0, itm)
                                
                                # Update details with success message
                                html = html.replace("<i>Récupération des issues en cours...</i>", f"<i>✅ {len(issues)} issue(s) trouvée(s)</i>")
                                self.detail_text.setHtml(html)
                                
                            except Exception as e:
                                print(f"[ERROR] Failed to fetch ComicVine issues: {e}")
                                error_html = html.replace("<i>Récupération des issues en cours...</i>", f"<i>❌ Erreur lors du chargement des issues: {e}</i>")
                                self.detail_text.setHtml(error_html)
            else:
                # Original ComicVine logic for non-series mode
                series = txt.rsplit(' (', 1)[0]
                if series in self.issues_by_series:
                    lst = sorted(self.issues_by_series[series], key=lambda x: ((x.get('cover_date') or ''), x.get('issue_number') or ''))
                    self.album_table.setRowCount(len(lst))
                    for r, it in enumerate(lst):
                        t = it.get('name') or 'Untitled'
                        n = it.get('issue_number') or '?'
                        n_fmt = format_num(n)
                        y = (it.get('cover_date') or '')[:4]
                        val = f"{series} - {n_fmt} - {t} ({y})"
                        itm = QTableWidgetItem(val)
                        itm.setData(Qt.UserRole, it)
                        self.album_table.setItem(r, 0, itm)
        else:  # BDGest
            # Check if we're in series mode (SeriesName checkbox checked)
            if self.series_name_cb.isChecked() and self._bdgest_series_results:
                # In series mode - fetch and display albums for the selected series
                current_index = self.series_combo.currentIndex()
                if current_index >= 0:
                    series_data = self.series_combo.itemData(current_index, Qt.UserRole)
                    if series_data:
                        series_id = series_data.get('serie_id') or series_data.get('id')
                        series_name = series_data.get('serie_name') or series_data.get('label') or series_data.get('value')
                        
                        if series_id and series_name:
                            # Show series details
                            html = "<b>Série sélectionnée :</b><br><ul>"
                            for k, v in series_data.items():
                                if v and str(v).strip():
                                    html += f"<li><b>{k}</b> : {v}</li>"
                            html += "</ul><br><i>Récupération des albums...</i>"
                            self.detail_text.setHtml(html)
                            
                            # Set cover image if available
                            if series_data.get('cover_url'):
                                self.series_cover_url = series_data.get('cover_url')
                                # Load and display the image
                                img_url = self.series_cover_url
                                if img_url and img_url.startswith('/'):
                                    img_url = 'https://www.bedetheque.com' + img_url
                                if img_url:
                                    try:
                                        data = requests.get(img_url, timeout=10).content
                                        pm = QPixmap()
                                        pm.loadFromData(data)
                                        # Store original for future rescaling
                                        self._original_cover_pixmap = pm
                                        # Scale to fit available space while maintaining aspect ratio
                                        scaled_pm = self._scale_image_to_fit(pm)
                                        self.detail_image.setPixmap(scaled_pm)
                                    except Exception as e:
                                        print("[ERROR] Image load failed:", e)
                                        self.detail_image.clear()
                                else:
                                    self.detail_image.clear()
                            
                            # Fetch albums for this series
                            try:
                                # Check for cancellation

                                if self._search_cancelled:
                                    return
                                
                                # Show progress message
                                self.detail_text.setHtml(html.replace("<i>Récupération des albums...</i>", "<i>Récupération des albums en cours...</i>"))
                                QApplication.processEvents()  # Allow UI update and cancellation
                                
                                debug = self.debug_cb.isChecked() if hasattr(self, 'debug_cb') else False
                                verbose = self.verbose_cb.isChecked() if hasattr(self, 'verbose_cb') else False
                                albums = provider.search_albums_by_series_id(series_id, series_name, debug=debug, verbose=verbose)
                                
                                # Check for cancellation after fetching
                                if self._search_cancelled:
                                    return
                                
                                # Check for authentication failed error
                                if albums and len(albums) == 1 and albums[0].get('error') == 'authentication_failed':
                                    # Use internationalized error messages
                                    title = tr("messages.errors.authentication_failed_title")
                                    message = tr("messages.errors.authentication_failed_message")
                                    hint = tr("messages.errors.authentication_failed_hint")
                                    full_message = f"{message}\n\n{hint}"
                                    
                                    QMessageBox.critical(self, title, full_message)
                                    # Clear album table and show error in details
                                    self.album_table.setRowCount(0)
                                    html = "<b>Série sélectionnée :</b><br><ul>"
                                    for k, v in series_data.items():
                                        if v and str(v).strip():
                                            html += f"<li><b>{k}</b> : {v}</li>"
                                    html += "</ul><br><i>Erreur d'authentification BDGest. Vérifiez vos identifiants.</i>"
                                    self.detail_text.setHtml(html)
                                    return
                                
                                if albums:
                                    # Populate album table with series albums
                                    self.album_table.setRowCount(len(albums))
                                    for r, alb in enumerate(albums):
                                        # Check for cancellation during album table population
                                        if self._search_cancelled:
                                            return
                                            
                                        s = alb.get('serie_name', series_name)
                                        t = alb.get('album_name', alb.get('nomAlbum', ''))
                                        n = alb.get('album_number', alb.get('numeroAlbum', ''))
                                        n_fmt = format_num(n)
                                        y = extract_year(alb.get('date', '') or alb.get('dateAlbum', ''))
                                        val = f"{s} - {n_fmt} - {t} ({y})"
                                        itm = QTableWidgetItem(val)
                                        itm.setData(Qt.UserRole, alb)
                                        self.album_table.setItem(r, 0, itm)
                                        if r == 0 and alb.get('cover_url'):
                                            self.series_cover_url = alb.get('cover_url')
                                            
                                        # Process UI events every 10 albums for responsiveness
                                        if r % 10 == 0:
                                            QApplication.processEvents()
                                    
                                    # Update the detail text with album count
                                    html = "<b>Série sélectionnée :</b><br><ul>"
                                    for k, v in series_data.items():
                                        if v and str(v).strip():
                                            html += f"<li><b>{k}</b> : {v}</li>"
                                    html += f"</ul><br><b>{len(albums)} album(s) trouvé(s)</b>"
                                    self.detail_text.setHtml(html)
                                else:
                                    # No albums found
                                    self.album_table.setRowCount(0)
                                    html = "<b>Série sélectionnée :</b><br><ul>"
                                    for k, v in series_data.items():
                                        if v and str(v).strip():
                                            html += f"<li><b>{k}</b> : {v}</li>"
                                    html += "</ul><br><i>Aucun album trouvé pour cette série.</i>"
                                    self.detail_text.setHtml(html)
                                    
                            except Exception as e:
                                print(f"[ERROR] Failed to fetch albums for series {series_name}: {e}")
                                self.album_table.setRowCount(0)
                                html = "<b>Série sélectionnée :</b><br><ul>"
                                for k, v in series_data.items():
                                    if v and str(v).strip():
                                        html += f"<li><b>{k}</b> : {v}</li>"
                                html += f"</ul><br><i>{tr('messages.errors.fetch_albums_error', error=str(e))}</i>"
                                self.detail_text.setHtml(html)
                        else:
                            # Missing series ID or name
                            self.album_table.setRowCount(0)
                            html = "<b>Série sélectionnée :</b><br><ul>"
                            for k, v in series_data.items():
                                if v and str(v).strip():
                                    html += f"<li><b>{k}</b> : {v}</li>"
                            html += "</ul><br><i>ID ou nom de série manquant pour récupérer les albums.</i>"
                            self.detail_text.setHtml(html)
                return
            else:
                # Normal album mode
                series = self.series_combo.currentText()
                alb_list = [a for a in self._bdgest_album_results if a.get('serie_name', '') == series]
                self.album_table.setRowCount(len(alb_list))
                for r, alb in enumerate(alb_list):
                    s = alb.get('serie_name', '')
                    t = alb.get('album_name', alb.get('nomAlbum', ''))
                    n = alb.get('album_number', alb.get('numeroAlbum', ''))
                    n_fmt = format_num(n)
                    y = extract_year(alb.get('date', '') or alb.get('dateAlbum', ''))
                    val = f"{s} - {n_fmt} - {t} ({y})"
                    itm = QTableWidgetItem(val)
                    itm.setData(Qt.UserRole, alb)
                    self.album_table.setItem(r, 0, itm)
                    if r == 0 and alb.get('cover_url'):
                        self.series_cover_url = alb.get('cover_url')
                    self.series_cover_url = alb.get('cover_url')
        if self.folder_rename_btn is not None:
            self.folder_rename_btn.setEnabled(False)  # Disable when repopulating albums
        # Adjust album table column after populating
        self.album_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def _show_details(self, r, c):
        if self.debug:
            print(f"[DEBUG] _show_details called for row {r}, col {c}")
        itm = self.album_table.item(r, 0)
        meta = itm.data(Qt.UserRole) if itm else None
        if not meta:
            # Clear the details and image when no metadata
            self.detail_text.setHtml("<p>No details available.</p>")
            self.detail_image.clear()
            self._original_cover_pixmap = None
            return
        
        if self.debug:
            print(f"[DEBUG] Clearing existing image before loading new one")
        # Clear the existing image before loading new one
        self.detail_image.clear()
        self.detail_image.setPixmap(QPixmap())  # Set empty pixmap explicitly
        self._original_cover_pixmap = None
        # Force UI update to ensure image is cleared
        self.detail_image.repaint()
        self.detail_image.update()
        QApplication.processEvents()
        html = """
        <style>
        body, div, ul, li, p { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            background: transparent !important; 
            margin: 0; 
            padding: 0; 
        }
        .details-container { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            background: transparent !important;
            color: #333;
            line-height: 1.4;
        }
        .details-container ul { 
            margin: 5px 0; 
            padding-left: 20px; 
            background: transparent !important;
        }
        .details-container li { 
            margin: 2px 0; 
            background: transparent !important;
            list-style-type: disc;
            line-height: 1.3;
        }
        .sub-section { 
            background-color: #f8f9fa !important; 
            padding: 6px 8px; 
            margin: 4px 0; 
            border-radius: 4px; 
            border: 1px solid #e9ecef;
        }
        .sub-section > b { 
            color: #495057; 
            background: transparent !important;
        }
        .sub-list { 
            margin: 5px 0 5px 15px; 
            background: transparent !important;
        }
        .sub-list li { 
            margin: 1px 0; 
            color: #6c757d; 
            font-size: 0.95em; 
            background: transparent !important;
            list-style-type: circle;
        }
        .complex-data { 
            background-color: #e9ecef !important; 
            padding: 4px 6px; 
            border-radius: 3px; 
            margin: 2px 0;
        }
        a { 
            color: #007bff !important; 
            text-decoration: underline;
            background: transparent !important;
        }
        a:hover { 
            color: #0056b3 !important; 
            background: transparent !important;
            text-decoration: underline;
        }
        b, strong { 
            background: transparent !important; 
            font-weight: 600;
        }
        /* Ensure no unwanted backgrounds appear */
        * { 
            background-attachment: scroll !important;
        }
        </style>
        <div class="details-container">"""
        
        # For BDGest, we'll handle the structure differently
        if self._source == 'BDGest':
            html += "<ul>"
        else:
            html += "<b>Détails complets :</b><br><ul>"
        
        # Helper function to detect and make URLs clickable
        def make_links_clickable(text, field_name=None):
            """Convert URLs in text to clickable HTML links with clean display text"""
            import re
            
            # If the text already contains HTML links, return as-is
            if '<a href=' in str(text):
                return str(text)
            
            # URL pattern to match http/https URLs
            url_pattern = r'(https?://[^\s<>"]{2,})'
            
            # If this is a URL field and the entire text is just a URL, make a clean link
            if field_name in ['album_url', 'cover_url', 'api_detail_url', 'image_url'] and re.match(r'^https?://', str(text).strip()):
                url = str(text).strip()
                if field_name == 'album_url':
                    if 'comicvine.gamespot.com' in url:
                        return f'<a href="{url}">ComicVine Page</a>'
                    elif 'bedetheque.com' in url:
                        return f'<a href="{url}">BDGest Page</a>'
                    else:
                        return f'<a href="{url}">View Page</a>'
                elif field_name == 'api_detail_url':
                    return f'<a href="{url}">API Details</a>'
                elif field_name == 'cover_url':
                    return f'<a href="{url}">View Cover</a>'
                elif field_name == 'image_url':
                    return f'<a href="{url}">View Image</a>'
                else:
                    return f'<a href="{url}">Link</a>'
            
            # Replace URLs with HTML links
            def replace_url(match):
                url = match.group(1)
                
                # For other fields, show a shortened URL
                if len(url) <= 50:
                    return f'<a href="{url}">{url}</a>'
                else:
                    display_url = url[:47] + '...'
                    return f'<a href="{url}">{display_url}</a>'
            
            return re.sub(url_pattern, replace_url, str(text))
        
        # Helper function to format any data type for display
        def format_display_value(value, field_name=None):
            """Format any value for HTML display"""
            if isinstance(value, dict):
                if value.get('type') == 'list':
                    # Already structured list data
                    return value
                elif field_name == 'volume':
                    # Special handling for volume field - show just the name
                    if value.get('name'):
                        return f"Name: {value.get('name')}"
                    else:
                        # Convert dict to structured list for other volume info
                        items = []
                        for k, v in value.items():
                            if isinstance(v, (str, int, float)) and v:
                                display_key = str(k).replace('_', ' ').title()
                                items.append(f"{display_key}: {make_links_clickable(v, k)}")
                        return {'type': 'list', 'items': items} if items else make_links_clickable(str(value), field_name)
                else:
                    # Convert dict to structured list
                    items = []
                    for k, v in value.items():
                        if isinstance(v, (str, int, float)) and v:
                            display_key = str(k).replace('_', ' ').title()
                            items.append(f"{display_key}: {make_links_clickable(v, k)}")
                    return {'type': 'list', 'items': items} if items else make_links_clickable(str(value), field_name)
            elif isinstance(value, list):
                # Convert list to structured format
                items = []
                for item in value[:10]:  # Limit display
                    if isinstance(item, dict):
                        # Try to extract meaningful info from dict
                        display_val = (item.get('name') or 
                                     item.get('title') or 
                                     item.get('id') or 
                                     str(item)[:60] + '...' if len(str(item)) > 60 else str(item))
                        items.append(str(display_val))
                    else:
                        items.append(str(item))
                return {'type': 'list', 'items': items} if items else str(value)
            else:
                # For URL fields, don't process with make_links_clickable here
                # Let the main display logic handle it
                return str(value)
        
        # Display all main fields except 'details'
        # Define the preferred order - different for BDGest vs ComicVine
        if self._source == 'BDGest':
            # BDGest-specific order: show most important info first
            field_order = [
                'serie_name',
                'style', 
                'album_name',
                'album_number',
                'ISBN',
                'date',
                'details'  # This will be handled specially
            ]
        else:
            # ComicVine order (original)
            field_order = [
                'issue_number',
                'name', 
                'store_date',
                'title',
                'details',  # This will be handled specially
                'volume',
                'description',
                'album_url',
                'id',
                'image',
                'api_detail_url',
                'cover_url',
                'cover_date'
            ]
        
        # Display fields in the preferred order
        displayed_fields = set()
        
        for field in field_order:
            if field in meta:
                if field == "details":
                    # Handle details specially - will be processed later
                    continue
                    
                v = meta[field]
                formatted_value = format_display_value(v, field)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    html += f'<li class="sub-section"><b>{field} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    html += f"<li><b>{field}</b> : {make_links_clickable(formatted_value, field)}</li>"
                displayed_fields.add(field)
        
        # Add the details section
        if self._source == 'BDGest':
            # For BDGest, show "Détails complets" with album_url, cover_url, then details, then remaining fields
            html += "<li><b>Détails complets :</b><ul>"
            
            # First add album_url and cover_url if they exist
            for url_field in ['album_url', 'cover_url']:
                if url_field in meta and meta[url_field]:
                    formatted_value = format_display_value(meta[url_field], url_field)
                    html += f"<li><b>{url_field}</b> : {make_links_clickable(formatted_value, url_field)}</li>"
                    displayed_fields.add(url_field)
            
            # Then add the details dict content
            details = meta.get("details")
            if isinstance(details, dict):
                html += "<li><b>Détails :</b><ul>"
                for label, value in details.items():
                    formatted_value = format_display_value(value, label)
                    if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                        # Handle structured list data as styled sub-sections
                        html += f'<li class="sub-section"><b>{label} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        # Handle regular string/simple data
                        html += f"<li><b>{label}</b> : {make_links_clickable(formatted_value, label)}</li>"
                html += "</ul></li>"
            
            # Then add any remaining fields
            for k, v in meta.items():
                if k not in displayed_fields and k != "details":
                    formatted_value = format_display_value(v, k)
                    if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                        html += f'<li class="sub-section"><b>{k} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        html += f"<li><b>{k}</b> : {make_links_clickable(formatted_value, k)}</li>"
            
            html += "</ul></li>"
        else:
            # For ComicVine, use the original logic
            details = meta.get("details")
            if isinstance(details, dict):
                html += "<li><b>Détails complets :</b><ul>"
                for label, value in details.items():
                    formatted_value = format_display_value(value, label)
                    if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                        # Handle structured list data as styled sub-sections
                        html += f'<li class="sub-section"><b>{label} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        # Handle regular string/simple data
                        html += f"<li><b>{label}</b> : {make_links_clickable(formatted_value, label)}</li>"
                html += "</ul></li>"
            
            # Display any remaining fields that weren't in our preferred order
            for k, v in meta.items():
                if k not in displayed_fields and k != "details":
                    formatted_value = format_display_value(v, k)
                    if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                        html += f'<li class="sub-section"><b>{k} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        html += f"<li><b>{k}</b> : {make_links_clickable(formatted_value, k)}</li>"
        html += "</ul></div>"
        self.detail_text.setHtml(html)
        img_url = meta.get('cover_url') or meta.get('image', {}).get('original_url')
        
        # Handle different URL formats for different providers
        if img_url:
            # BDGest URLs start with '/' and need domain prepended
            if img_url.startswith('/'):
                img_url = 'https://www.bedetheque.com' + img_url
            # Comic Vine URLs are already complete URLs (start with http)
            # No modification needed for Comic Vine URLs
        
        if img_url:
            try:
                if self.debug:
                    print(f"[DEBUG] Loading cover image from: {img_url}")
                # Add headers to prevent caching issues
                headers = {
                    'User-Agent': 'ComicsRename/3.2',
                    'Cache-Control': 'no-cache'
                }
                data = requests.get(img_url, timeout=10, headers=headers).content
                pm = QPixmap()
                pm.loadFromData(data)
                
                # Ensure we have a valid image
                if pm.isNull():
                    if self.debug:
                        print(f"[DEBUG] Failed to create QPixmap from data")
                    self.detail_image.clear()
                    return
                    
                # Store original for future rescaling
                self._original_cover_pixmap = pm
                # Scale to fit available space while maintaining aspect ratio
                scaled_pm = self._scale_image_to_fit(pm)
                self.detail_image.setPixmap(scaled_pm)
                # Force update to ensure the new image is displayed
                self.detail_image.update()
                self.detail_image.repaint()
                QApplication.processEvents()
                if self.debug:
                    print(f"[DEBUG] Cover image loaded successfully, size: {pm.width()}x{pm.height()}")
            except Exception as e:
                print(f"[ERROR] Image load failed for URL {img_url}: {e}")
                self.detail_image.clear()
        else:
            if self.debug:
                print("[DEBUG] No cover image URL found")
            self.detail_image.clear()

    def _rename_selected(self):
        fr = self.file_table.currentRow()
        ar = self.album_table.currentRow()
        if fr < 0 or ar < 0:
            QMessageBox.warning(self, 'Selection', 'Please select one file and one album')
            return
        f = self.files[fr]
        itm = self.album_table.item(ar, 0)
        meta = itm.data(Qt.UserRole) if itm else None
        if not meta:
            QMessageBox.critical(self, 'Error', 'Album metadata missing')
            return
        # Build new filename
        series = meta.get('serie_name') or (meta.get('volume') or {}).get('name', '')
        num = meta.get('album_number') or meta.get('issue_number') or ''
        title = meta.get('album_name') or meta.get('name') or ''
        y = extract_year(meta.get('date') or meta.get('cover_date') or '')
        # Format number on two digits if it's a number
        def format_num(n):
            try:
                n_int = int(n)
                return f"{n_int:02d}"
            except Exception:
                return str(n)
        # Only keep allowed characters: unicode letters, numbers, spaces, apostrophes, hyphens, underscores, parentheses
        def clean(s):
            if self.debug:
                print(f"[DEBUG] clean() input: {repr(s)}")
            cleaned = re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
            if self.debug:
                print(f"[DEBUG] clean() output: {repr(cleaned)}")
            return cleaned
        if self.debug:
            print(f"[DEBUG] series before clean: {repr(series)}")
            print(f"[DEBUG] num before clean: {repr(num)}")
            print(f"[DEBUG] title before clean: {repr(title)}")
        base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
        if y:
            base += f" ({y})"
        if self.debug:
            print(f"[DEBUG] base filename after clean: {repr(base)}")
        # Ensure extension does not have a leading dot
        ext = f['ext'].lstrip('.')
        new_name = f"{base}.{ext}"
        new_path = pathlib.Path(f['folder']) / new_name
        if new_path.exists():
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_already_exists", name=new_name))
            return
        if QMessageBox.question(self, tr("dialogs.rename_confirmation.title"), tr("dialogs.rename_confirmation.file_message", new_name=new_name), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                if not os.path.exists(str(f['path'])):
                    QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_not_exists", path=f['path']))
                    return
                os.rename(str(f['path']), str(new_path))
                self._load_files(f['folder'])
            except Exception as e:
                QMessageBox.critical(self, tr("messages.errors.rename_error"), str(e))

    def _open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec():
            # Invalidate BDGest session when settings change (credentials might have changed)
            bdgest_provider = PROVIDERS.get('BDGest')
            if bdgest_provider and hasattr(bdgest_provider, '_invalidate_session'):
                bdgest_provider._invalidate_session()
            
            # Met à jour le selector après modification des paramètres
            new_provider = self.settings.value("default_provider", "BDGest")
            idx = self.provider_combo.findText(new_provider)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)
            # Update the search source selector as well
            idx2 = self.source_combo.findText(new_provider)
            if idx2 >= 0:
                self.source_combo.setCurrentIndex(idx2)
            self.default_provider = new_provider

    def _update_folder_display(self, selected, deselected):
        rows = self.file_table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            folder = self.files[row]['folder']
            self.folder_display.setText(os.path.basename(folder.rstrip('/\\')))
        else:
            # If nothing selected, show root folder name
            self.folder_display.setText(os.path.basename(self.settings.value('last_folder', '').rstrip('/\\')))
        
        # Update rename button state based on both file and album selections
        self._update_rename_button_state()

    def _rename_folder_to_serie(self):
        # Get current folder path
        if not self.files:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.no_files_in_folder"))
            return
        current_folder = pathlib.Path(self.files[0]['folder'])
        # Get selected album
        ar = self.album_table.currentRow()
        if ar < 0:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.no_album_selected"))
            return
        itm = self.album_table.item(ar, 0)
        meta = itm.data(Qt.UserRole) if itm else None
        if not meta:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.album_metadata_missing"))
            return
        # Extract serie_name
        serie_name = meta.get('serie_name') or (meta.get('volume') or {}).get('name', '')
        # Extract style from various possible locations
        style = ''
        details = meta.get('details', {})
        
        # Try multiple field names and locations for style information
        style_fields = ['Style', 'Genre', 'Style/Genre', 'Styles', 'Genres']
        
        # First try top-level meta
        for field in style_fields:
            if meta.get(field):
                style = meta.get(field)
                break
        
        # Then try details dict
        if not style and isinstance(details, dict):
            for field in style_fields:
                if field in details and details[field]:
                    style = details[field]
                    break
            
            # Try nested 'Détails' structure
            if not style and 'Détails' in details and isinstance(details['Détails'], dict):
                for field in style_fields:
                    if field in details['Détails'] and details['Détails'][field]:
                        style = details['Détails'][field]
                        break
        
        # Finally try the original 'style' field
        if not style:
            style = meta.get('style', '')
        
        # If no style found in metadata, try to extract from current folder name
        if not style:
            import re
            current_name = current_folder.name
            
            # Try to extract style from patterns like "[Style] Series" or "Style Series"
            # First try bracketed style: [Style] Series
            bracket_match = re.match(r'^\[([^\]]+)\]\s*(.+)$', current_name)
            if bracket_match:
                potential_style = bracket_match.group(1).strip()
                potential_series = bracket_match.group(2).strip()
                # Check if the series part matches our serie_name
                if potential_series.lower() == serie_name.lower():
                    style = potential_style
                    if self.debug:
                        print(f"[DEBUG] Extracted style from bracketed folder name: '{style}'")
            
            # If not bracketed, try "Style Series" pattern
            if not style and serie_name:
                # Check if folder name starts with a style followed by the series name
                if current_name.lower().endswith(serie_name.lower()):
                    potential_style = current_name[:-len(serie_name)].strip()
                    # Only consider it a style if it's a reasonable length and not empty
                    if potential_style and len(potential_style) <= 30 and not potential_style.isdigit():
                        style = potential_style
                        if self.debug:
                            print(f"[DEBUG] Extracted style from folder name pattern: '{style}'")
        if not serie_name:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.cannot_determine_series"))
            return
        # Clean up names
        clean = lambda s: ''.join(c for c in str(s) if c.isalnum() or c in "-_(),' ").strip()
        style_clean = clean(style)
        serie_clean = clean(serie_name)
        new_folder_name = f"[{style_clean}] {serie_clean}" if style_clean else serie_clean
        parent_dir = current_folder.parent

        # DEBUG: Print current and new folder names and paths
        if self.debug:
            print(f"[DEBUG] current_folder: {current_folder}")
            print(f"[DEBUG] current_folder.name: {current_folder.name}")
            print(f"[DEBUG] serie_name: '{serie_name}'")
            print(f"[DEBUG] extracted style: '{style}'")
            print(f"[DEBUG] style_clean: '{style_clean}'")
            print(f"[DEBUG] serie_clean: '{serie_clean}'")
            print(f"[DEBUG] new_folder_name: {new_folder_name}")
            print(f"[DEBUG] new_folder_path: {parent_dir / new_folder_name}")
            print(f"[DEBUG] meta keys: {list(meta.keys())}")
            print(f"[DEBUG] details keys: {list(details.keys()) if isinstance(details, dict) else 'Not a dict'}")
            if isinstance(details, dict) and 'Détails' in details:
                print(f"[DEBUG] nested Détails keys: {list(details['Détails'].keys()) if isinstance(details['Détails'], dict) else 'Not a dict'}")

        if current_folder.name == new_folder_name:
            if self.debug:
                print("[DEBUG] Folder name is already the target name, aborting rename.")
            QMessageBox.information(self, "Info", "Le dossier porte déjà ce nom.")
            return

        if style_clean and current_folder.name == serie_clean and new_folder_name != current_folder.name:
            if self.debug:
                print("[DEBUG] Folder is only serie name, will rename to [Style] SerieName.")

        new_folder_path = parent_dir / new_folder_name
        if new_folder_path.exists():
            if self.debug:
                print("[DEBUG] Target folder already exists, aborting rename.")
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_already_exists", name=new_folder_name))
            return

        if QMessageBox.question(
            self,
            tr("messages.errors.rename_folder_title"),
            tr("dialogs.rename_confirmation.folder_message", old_name=current_folder.name, new_name=new_folder_name),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                if self.debug:
                    print(f"[DEBUG] Renaming {current_folder} -> {new_folder_path}")
                os.rename(str(current_folder), str(new_folder_path))
                # NE PAS mettre à jour last_folder - garder l'ancien chemin pour la logique de fallback
                # self.settings.setValue('last_folder', str(new_folder_path))  # Supprimé
                self._load_files(str(new_folder_path))
                QMessageBox.information(self, tr("messages.errors.success_title"), tr("messages.errors.folder_renamed", name=new_folder_name))
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Exception during rename: {e}")
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_rename_error", error=str(e)))

    def _confirm_and_rename_folder(self, old_name, new_name):
        """Handle folder rename from direct editing of folder name"""
        if not self.files:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.no_files_in_folder"))
            return False
            
        current_folder = pathlib.Path(self.files[0]['folder'])
        parent_dir = current_folder.parent
        
        # Clean up the new name to prevent filesystem issues but allow brackets for style formatting
        clean = lambda s: ''.join(c for c in str(s) if c.isalnum() or c in "-_(),' []").strip()
        new_name_clean = clean(new_name)
        
        if not new_name_clean:
            QMessageBox.warning(self, tr("messages.errors.error"), "Le nouveau nom de dossier ne peut pas être vide.")
            return False
            
        new_folder_path = parent_dir / new_name_clean
        
        # Check if target folder already exists
        if new_folder_path.exists():
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_already_exists", name=new_name_clean))
            return False
            
        # Confirm the rename operation
        if QMessageBox.question(
            self,
            tr("messages.errors.rename_folder_title"),
            tr("dialogs.rename_confirmation.folder_message", old_name=old_name, new_name=new_name_clean),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                if self.debug:
                    print(f"[DEBUG] Direct rename: {current_folder} -> {new_folder_path}")
                os.rename(str(current_folder), str(new_folder_path))
                # NE PAS mettre à jour last_folder - garder l'ancien chemin pour la logique de fallback
                self._load_files(str(new_folder_path))
                QMessageBox.information(self, tr("messages.errors.success_title"), tr("messages.errors.folder_renamed", name=new_name_clean))
                return True
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Exception during direct rename: {e}")
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_rename_error", error=str(e)))
                return False
        else:
            return False  # User cancelled

    def resizeEvent(self, event):
        """Handle window resize to update cover image scaling"""
        super().resizeEvent(event)
        # Re-scale the image if there's one displayed
        self._update_cover_image_size()

    def _update_cover_image_size(self):
        """Update cover image scaling when detail panel size changes"""
        if self._original_cover_pixmap and not self._original_cover_pixmap.isNull():
            # Wait a bit for the layout to settle
            from PySide6.QtCore import QTimer
            QTimer.singleShot(50, self._rescale_cover_image)
    
    def _rescale_cover_image(self):
        """Rescale the cover image to fit current space"""
        if self._original_cover_pixmap and not self._original_cover_pixmap.isNull():
            scaled_pixmap = self._scale_image_to_fit(self._original_cover_pixmap)
            self.detail_image.setPixmap(scaled_pixmap)

    def _get_fallback_folder_path(self, stored_folder_path):
        """
        Get the best available folder path when the stored path might not exist.
        
        Strategy:
        1. If the exact stored path exists, use it
        2. EXHAUSTIVE search for exact folder name in common locations
        3. Fall back to renamed folders only as last resort
        
        Args:
            stored_folder_path (str): The folder path stored in settings
            
        Returns:
            str: The best available folder path to use
        """
        if not stored_folder_path:
            return str(pathlib.Path.home())
        
        stored_path = pathlib.Path(stored_folder_path)
        
        # First, try the exact stored path
        if stored_path.exists():
            return str(stored_path)
        
        # If the folder doesn't exist, search for exact folder name in multiple locations
        try:
            parent_dir = stored_path.parent
            original_folder_name = stored_path.name
            
            # Force debug for this critical function
            force_debug = False  # Respect user's debug setting
            
            # Debug info
            if force_debug or (hasattr(self, 'debug') and self.debug):
                print(f"[DEBUG] Original folder '{original_folder_name}' not found at '{stored_path}'")
                print(f"[DEBUG] Searching for exact folder name in common locations...")
            
            # EXHAUSTIVE search in parent directory and common locations
            search_locations = []
            
            # 1. Parent directory of the original path
            if parent_dir.exists():
                search_locations.append(parent_dir)
            
            # 2. Common folder locations
            home = pathlib.Path.home()
            common_locations = [
                home / "Downloads",
                home / "Documents", 
                home / "Desktop",
                home,  # Home directory itself
                pathlib.Path("/Users") / "Shared",  # macOS shared folder
                pathlib.Path("/Volumes")  # macOS external drives
            ]
            
            # Add existing locations to search
            for loc in common_locations:
                if loc.exists() and loc not in search_locations:
                    search_locations.append(loc)
            
            # Search each location for exact folder name match
            for search_dir in search_locations:
                try:
                    if force_debug or self.debug:
                        print(f"[DEBUG] Searching in: {search_dir}")
                    
                    for item in search_dir.iterdir():
                        if item.is_dir() and item.name == original_folder_name:
                            if force_debug or self.debug:
                                print(f"[DEBUG] FOUND exact match: {item}")
                            return str(item)
                except (PermissionError, OSError) as e:
                    if force_debug or self.debug:
                        print(f"[DEBUG] Cannot search {search_dir}: {e}")
                    continue
            
            # If we still haven't found it, do a broader search for similar names
            if force_debug or self.debug:
                print(f"[DEBUG] Exact match not found, searching for similar folder names...")
            
            for search_dir in search_locations:
                try:
                    for item in search_dir.iterdir():
                        if item.is_dir():
                            # Check if folder name contains the original name (case-insensitive)
                            if original_folder_name.lower() in item.name.lower():
                                if force_debug or self.debug:
                                    print(f"[DEBUG] Found similar folder: {item}")
                                return str(item)
                except (PermissionError, OSError):
                    continue
            
            # Last resort: return home directory
            if force_debug or self.debug:
                print(f"[DEBUG] No matches found, falling back to home directory")
            return str(home)
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Exception in _get_fallback_folder_path: {e}")
            return str(pathlib.Path.home())

    def _get_amazon_domain_for_provider(self, provider):
        """Get the appropriate Amazon domain based on the provider"""
        if provider == 'BDGest':
            return 'amazon.fr'  # French provider -> French Amazon
        else:  # ComicVine or other international providers
            return 'amazon.com'  # International provider -> US Amazon

    def _construct_amazon_search_url(self, album_title, series_name=None, provider=None):
        """Construct Amazon search URL with partner ID"""
        # Use current provider if not specified
        if provider is None:
            provider = self._source
        
        # Get appropriate Amazon domain
        domain = self._get_amazon_domain_for_provider(provider)
        
        # Construct search query
        search_terms = []
        if series_name:
            search_terms.append(series_name)
        if album_title:
            search_terms.append(album_title)
        
        # Add "comic" or "BD" to help Amazon find the right products
        if provider == 'BDGest':
            search_terms.append('BD')
        else:
            search_terms.append('comic')
        
        query = ' '.join(search_terms)
        
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(query)
        
        # Construct Amazon URL with partner ID
        amazon_url = f"https://www.{domain}/s?k={encoded_query}&tag=bdma-21"
        
        return amazon_url

    def _on_cover_image_clicked(self, event):
        """Handle click on cover image to search Amazon"""
        if event.button() == Qt.LeftButton:
            # Get current album metadata
            selected_rows = self.album_table.selectionModel().selectedRows()
            if not selected_rows:
                return
            
            row = selected_rows[0].row()
            item = self.album_table.item(row, 0)
            if not item:
                return
            
            meta = item.data(Qt.UserRole)
            if not meta:
                return
            
            # Extract album info for Amazon search
            album_title = meta.get('title', '') or meta.get('issue_title', '') or meta.get('name', '')
            series_name = meta.get('serie_name', '') or meta.get('volume', {}).get('name', '')
            
            if not album_title and not series_name:
                QMessageBox.information(self, tr("messages.info.amazon_search_title"), tr("messages.info.amazon_no_info"))
                return
            
            # Construct and open Amazon URL
            amazon_url = self._construct_amazon_search_url(album_title, series_name, self._source)
            
            # Open URL in default browser
            import webbrowser
            webbrowser.open(amazon_url)

    def _search_amazon_for_album(self, album_meta):
        """Search Amazon for a specific album"""
        if not album_meta:
            return
        
        # Extract album info
        album_title = album_meta.get('title', '') or album_meta.get('issue_title', '') or album_meta.get('name', '')
        series_name = album_meta.get('serie_name', '') or album_meta.get('volume', {}).get('name', '')
        
        if not album_title and not series_name:
            QMessageBox.information(self, tr("messages.info.amazon_search_title"), tr("messages.info.amazon_no_info"))
            return
        
        # Construct and open Amazon URL
        amazon_url = self._construct_amazon_search_url(album_title, series_name, self._source)
        
        # Open URL in default browser
        import webbrowser
        webbrowser.open(amazon_url)