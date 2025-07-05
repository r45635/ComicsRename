"""
Album Population Logic Module

This module handles the population of album tables based on series selection
and provider-specific data formats.
"""

import requests
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from core.providers import PROVIDERS
from utils import extract_year
from i18n import tr


class AlbumPopulator:
    """Handles album population for different providers and modes."""
    
    def __init__(self, main_window, debug: bool = False):
        """
        Initialize the AlbumPopulator.
        
        Args:
            main_window: Reference to the main ComicRenamer window
            debug (bool): Enable debug output
        """
        self.main_window = main_window
        self.debug = debug
    
    def populate_albums(self, series_text: str):
        """
        Populate the album table based on the selected series and current provider.
        
        Args:
            series_text (str): The selected series text from the combo box
        """
        if not series_text:
            return
            
        # Check for cancellation at the start
        if hasattr(self.main_window, '_search_cancelled') and self.main_window._search_cancelled:
            return
            
        # Debug output
        debug = bool(self._get_debug_setting())
        if debug:
            print(f"[DEBUG][UI] _populate_albums called with series: '{series_text}' (provider: {self.main_window._source})")
            
        # Clear existing data
        self.main_window.album_table.clearContents()
        self.main_window.album_table.setRowCount(0)
        self.main_window.series_cover_url = ''

        provider = PROVIDERS[self.main_window._source]
        
        # Populate based on provider
        if self.main_window._source == 'ComicVine':
            self._populate_comicvine_albums(series_text, provider, debug)
        else:  # BDGest
            self._populate_bdgest_albums(series_text, provider, debug)
        
        # Update UI state
        if self.main_window.folder_rename_btn is not None:
            self.main_window.folder_rename_btn.setEnabled(False)  # Disable when repopulating albums
        
        # Adjust album table column after populating
        self.main_window.album_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    
    def _populate_comicvine_albums(self, series_text: str, provider, debug: bool):
        """Handle ComicVine album population."""
        if self.main_window.series_name_cb.isChecked() and self.main_window._comicvine_series_results:
            # Series mode - fetch and display albums for the selected series
            self._populate_comicvine_series_mode(series_text, provider, debug)
        else:
            # Normal mode - use existing issues_by_series data
            self._populate_comicvine_normal_mode(series_text, debug)
    
    def _populate_comicvine_series_mode(self, series_text: str, provider, debug: bool):
        """Handle ComicVine series mode album population."""
        # Find the index of the series by name
        series_index = -1
        for i in range(self.main_window.series_combo.count()):
            if self.main_window.series_combo.itemText(i) == series_text:
                series_index = i
                break
        
        if debug:
            print(f"[DEBUG][UI] Looking for series '{series_text}' in dropdown - found at index {series_index}")
        
        if series_index >= 0:
            series_data = self.main_window.series_combo.itemData(series_index, Qt.ItemDataRole.UserRole)
            if debug:
                print(f"[DEBUG][UI] Found series data: {series_data is not None}")
            
            if series_data:
                volume_id = series_data.get('volume_id') or str(series_data.get('id', ''))
                series_name = series_data.get('serie_name', 'Unknown')
                
                if volume_id and series_name:
                    self._fetch_comicvine_issues(series_data, volume_id, series_name, provider, debug)
    
    def _fetch_comicvine_issues(self, series_data, volume_id: str, series_name: str, provider, debug: bool):
        """Fetch and display ComicVine issues for a series."""
        # Show series details using the same formatting as albums
        html = "<b>Série sélectionnée :</b><br><br>"
        html += f"<b>Titre :</b> {series_data.get('serie_name', 'N/A')}<br>"
        html += f"<b>Année de début :</b> {series_data.get('start_year', 'N/A')}<br>"
        html += f"<b>Éditeur :</b> {series_data.get('publisher', 'N/A')}<br>"
        
        # ComicVine links
        if series_data.get('api_detail_url'):
            html += f"<b>Page ComicVine :</b> <a href='{series_data['api_detail_url']}'>Voir sur ComicVine</a><br>"
        
        # Volume ID
        html += f"<b>Volume ID :</b> {volume_id}<br>"
        html += "<br><i>Récupération des albums...</i>"
        
        self.main_window.detail_text.setHtml(html)
        
        # Set cover image if available
        self._load_comicvine_cover_image(series_data)
        
        # Fetch issues for this volume
        try:
            # Check for cancellation
            if self.main_window._search_cancelled:
                return
            
            # Show progress message
            self.main_window.detail_text.setHtml(html.replace("<i>Récupération des albums...</i>", "<i>Récupération des albums en cours...</i>"))
            QApplication.processEvents()  # Allow UI update and cancellation
            
            # Get issues
            issues = provider.search_albums(volume_id, debug=debug)
            
            # Check for cancellation after fetching
            if self.main_window._search_cancelled:
                return
            
            # Clear and populate album table
            self.main_window.album_table.clearContents()
            self.main_window.album_table.setRowCount(len(issues))
            
            for r, issue in enumerate(issues):
                t = issue.get('name') or 'Untitled'
                n = issue.get('issue_number') or '?'
                n_fmt = self._format_number(n)
                y = (issue.get('cover_date') or '')[:4]
                val = f"{series_name} - {n_fmt} - {t} ({y})"
                itm = QTableWidgetItem(val)
                itm.setData(Qt.ItemDataRole.UserRole, issue)
                self.main_window.album_table.setItem(r, 0, itm)
            
            # Update details with success message
            html = html.replace("<i>Récupération des albums en cours...</i>", f"<i>✅ {len(issues)} issue(s) trouvée(s)</i>")
            self.main_window.detail_text.setHtml(html)
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch ComicVine issues: {e}")
            error_html = html.replace("<i>Récupération des albums...</i>", f"<i>❌ Erreur lors du chargement des issues: {e}</i>")
            self.main_window.detail_text.setHtml(error_html)
    
    def _load_comicvine_cover_image(self, series_data):
        """Load ComicVine cover image."""
        if series_data.get('image'):
            cover_url = series_data.get('image', {}).get('medium_url', '')
            if cover_url:
                try:
                    data = requests.get(cover_url, timeout=10).content
                    pm = QPixmap()
                    pm.loadFromData(data)
                    # Store original for future rescaling
                    self.main_window._original_cover_pixmap = pm
                    # Scale to fit available space while maintaining aspect ratio
                    scaled_pm = self.main_window._scale_image_to_fit(pm)
                    self.main_window.detail_image.setPixmap(scaled_pm)
                except Exception as e:
                    print("[ERROR] ComicVine image load failed:", e)
                    self.main_window.detail_image.clear()
            else:
                self.main_window.detail_image.clear()
    
    def _populate_comicvine_normal_mode(self, series_text: str, debug: bool):
        """Handle ComicVine normal mode album population."""
        series = series_text.rsplit(' (', 1)[0]
        if series in self.main_window.issues_by_series:
            lst = sorted(self.main_window.issues_by_series[series], 
                        key=lambda x: ((x.get('cover_date') or ''), x.get('issue_number') or ''))
            self.main_window.album_table.setRowCount(len(lst))
            for r, it in enumerate(lst):
                t = it.get('name') or 'Untitled'
                n = it.get('issue_number') or '?'
                n_fmt = self._format_number(n)
                y = (it.get('cover_date') or '')[:4]
                val = f"{series} - {n_fmt} - {t} ({y})"
                itm = QTableWidgetItem(val)
                itm.setData(Qt.ItemDataRole.UserRole, it)
                self.main_window.album_table.setItem(r, 0, itm)
    
    def _populate_bdgest_albums(self, series_text: str, provider, debug: bool):
        """Handle BDGest album population."""
        if self.main_window.series_name_cb.isChecked() and self.main_window._bdgest_series_results:
            # Series mode - fetch and display albums for the selected series
            self._populate_bdgest_series_mode(series_text, provider, debug)
        else:
            # Normal mode - use existing _bdgest_album_results data
            self._populate_bdgest_normal_mode(series_text, debug)
    
    def _populate_bdgest_series_mode(self, series_text: str, provider, debug: bool):
        """Handle BDGest series mode album population."""
        current_index = self.main_window.series_combo.currentIndex()
        if current_index >= 0:
            series_data = self.main_window.series_combo.itemData(current_index, Qt.ItemDataRole.UserRole)
            if series_data:
                series_id = series_data.get('serie_id') or series_data.get('id')
                series_name = series_data.get('serie_name') or series_data.get('label') or series_data.get('value')
                
                if series_id and series_name:
                    self._fetch_bdgest_albums(series_data, series_id, series_name, provider, debug)
                else:
                    self._show_bdgest_missing_info_error(series_data)
    
    def _fetch_bdgest_albums(self, series_data, series_id: str, series_name: str, provider, debug: bool):
        """Fetch and display BDGest albums for a series."""
        # Show series details using clean formatting
        html = self._create_bdgest_series_html(series_data, series_id, "Récupération des albums...")
        self.main_window.detail_text.setHtml(html)
        
        # Set cover image if available
        self._load_bdgest_cover_image(series_data)
        
        # Fetch albums for this series
        try:
            # Check for cancellation
            if self.main_window._search_cancelled:
                return
            
            # Show progress message
            self.main_window.detail_text.setHtml(html.replace("<i>Récupération des albums...</i>", "<i>Récupération des albums en cours...</i>"))
            QApplication.processEvents()  # Allow UI update and cancellation
            
            # Get albums
            albums = provider.search_albums_by_series_id(series_id, series_name, debug=debug, verbose=False)
            
            # Check for cancellation after fetching
            if self.main_window._search_cancelled:
                return
            
            # Check for authentication failed error
            if albums and len(albums) == 1 and albums[0].get('error') == 'authentication_failed':
                self._show_bdgest_auth_error(series_data)
                return
            
            if albums:
                self._populate_bdgest_albums_table(albums, series_name, series_data)
            else:
                self._show_bdgest_no_albums_found(series_data)
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch albums for series {series_name}: {e}")
            self._show_bdgest_fetch_error(series_data, e)
    
    def _populate_bdgest_albums_table(self, albums, series_name: str, series_data):
        """Populate BDGest albums table."""
        self.main_window.album_table.setRowCount(len(albums))
        for r, alb in enumerate(albums):
            # Check for cancellation during album table population
            if self.main_window._search_cancelled:
                return
            
            s = alb.get('serie_name', series_name)
            t = alb.get('album_name', alb.get('nomAlbum', ''))
            n = alb.get('album_number', alb.get('numeroAlbum', ''))
            n_fmt = self._format_number(n)
            y = extract_year(alb.get('date', '') or alb.get('dateAlbum', ''))
            val = f"{s} - {n_fmt} - {t} ({y})"
            itm = QTableWidgetItem(val)
            itm.setData(Qt.ItemDataRole.UserRole, alb)
            self.main_window.album_table.setItem(r, 0, itm)
            
            # Process UI events every 10 albums for responsiveness
            if r % 10 == 0:
                QApplication.processEvents()
        
        # Update the detail text with album count
        html = self._create_bdgest_series_html(series_data, series_data.get('serie_id') or series_data.get('id'), f"<b>{len(albums)} album(s) trouvé(s)</b>")
        self.main_window.detail_text.setHtml(html)
    
    def _show_bdgest_auth_error(self, series_data):
        """Show BDGest authentication error."""
        title = tr("messages.errors.authentication_failed_title")
        message = tr("messages.errors.authentication_failed_message")
        hint = tr("messages.errors.authentication_failed_hint")
        full_message = f"{message}\n\n{hint}"
        
        QMessageBox.critical(self.main_window, title, full_message)
        
        # Clear album table and show error in details
        self.main_window.album_table.setRowCount(0)
        html = "<b>Série sélectionnée :</b><br><ul>"
        for k, v in series_data.items():
            if v and str(v).strip():
                html += f"<li><b>{k}</b> : {v}</li>"
        html += "</ul><br><i>Erreur d'authentification BDGest. Vérifiez vos identifiants.</i>"
        self.main_window.detail_text.setHtml(html)
    
    def _show_bdgest_no_albums_found(self, series_data):
        """Show BDGest no albums found message."""
        self.main_window.album_table.setRowCount(0)
        html = self._create_bdgest_series_html(series_data, series_data.get('serie_id') or series_data.get('id'), "Aucun album trouvé pour cette série.")
        self.main_window.detail_text.setHtml(html)
    
    def _show_bdgest_fetch_error(self, series_data, error):
        """Show BDGest fetch error."""
        self.main_window.album_table.setRowCount(0)
        html = self._create_bdgest_series_html(series_data, series_data.get('serie_id') or series_data.get('id'), f"{tr('messages.errors.fetch_albums_error', error=str(error))}")
        self.main_window.detail_text.setHtml(html)
    
    def _show_bdgest_missing_info_error(self, series_data):
        """Show BDGest missing info error."""
        self.main_window.album_table.setRowCount(0)
        html = "<b>Série sélectionnée :</b><br><br>"
        html += f"<b>Titre :</b> {series_data.get('serie_name', 'N/A')}<br>"
        html += "<br><i>ID ou nom de série manquant pour récupérer les albums.</i>"
        self.main_window.detail_text.setHtml(html)
    
    def _create_bdgest_series_html(self, series_data, series_id: str, status_message: str):
        """Create HTML for BDGest series display."""
        html = "<b>Série sélectionnée :</b><br><br>"
        html += f"<b>Titre :</b> {series_data.get('serie_name', 'N/A')}<br>"
        
        # Try to get year information
        year_info = series_data.get('year', '') or series_data.get('start_year', '') or series_data.get('date_debut', '')
        if year_info:
            html += f"<b>Année :</b> {year_info}<br>"
        
        # Try to get publisher information
        publisher_info = series_data.get('publisher', '') or series_data.get('editeur', '')
        if publisher_info:
            html += f"<b>Éditeur :</b> {publisher_info}<br>"
        
        # BDGest links
        if series_data.get('album_url'):
            html += f"<b>Page BDGest :</b> <a href='{series_data['album_url']}'>Voir sur BDGest</a><br>"
        
        # Series ID
        if series_id:
            html += f"<b>Série ID :</b> {series_id}<br>"
        
        html += f"<br><i>{status_message}</i>"
        return html
    
    def _load_bdgest_cover_image(self, series_data):
        """Load BDGest cover image."""
        if series_data.get('cover_url'):
            self.main_window.series_cover_url = series_data.get('cover_url')
            # Load and display the image
            img_url = self.main_window.series_cover_url
            if img_url and img_url.startswith('/'):
                img_url = 'https://www.bedetheque.com' + img_url
            if img_url:
                try:
                    data = requests.get(img_url, timeout=10).content
                    pm = QPixmap()
                    pm.loadFromData(data)
                    # Store original for future rescaling
                    self.main_window._original_cover_pixmap = pm
                    # Scale to fit available space while maintaining aspect ratio
                    scaled_pm = self.main_window._scale_image_to_fit(pm)
                    self.main_window.detail_image.setPixmap(scaled_pm)
                except Exception as e:
                    print("[ERROR] Image load failed:", e)
                    self.main_window.detail_image.clear()
            else:
                self.main_window.detail_image.clear()
    
    def _populate_bdgest_normal_mode(self, series_text: str, debug: bool):
        """Handle BDGest normal mode album population."""
        series = self.main_window.series_combo.currentText()
        alb_list = [a for a in self.main_window._bdgest_album_results if a.get('serie_name', '') == series]
        self.main_window.album_table.setRowCount(len(alb_list))
        for r, alb in enumerate(alb_list):
            s = alb.get('serie_name', '')
            t = alb.get('album_name', alb.get('nomAlbum', ''))
            n = alb.get('album_number', alb.get('numeroAlbum', ''))
            n_fmt = self._format_number(n)
            y = extract_year(alb.get('date', '') or alb.get('dateAlbum', ''))
            val = f"{s} - {n_fmt} - {t} ({y})"
            itm = QTableWidgetItem(val)
            itm.setData(Qt.ItemDataRole.UserRole, alb)
            self.main_window.album_table.setItem(r, 0, itm)
    
    def _format_number(self, n):
        """Format album/issue number to two digits."""
        try:
            n_int = int(n)
            return f"{n_int:02d}"
        except Exception:
            return str(n)
    
    def _get_debug_setting(self):
        """Get debug setting from main window."""
        return getattr(self.main_window, 'debug_cb', None) and self.main_window.debug_cb.isChecked() if hasattr(self.main_window, 'debug_cb') else False
