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
import json
import shutil
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

# Import core components
from core.providers import PROVIDERS
from core.workers import SearchWorker
from core.widgets import DroppableLineEdit, EditableFolderLineEdit
from core import FolderRenamer

# Import UI components  
from ui.tables import FileTable, AlbumTable
from ui.dialogs import SettingsDialog

# Import internationalization system
from i18n import tr, set_language, get_current_language, get_supported_languages

# ---------- Providers (API abstraction layer) ----------

# ---------- Custom UI Components ----------
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
        
        # Initialize folder renamer
        self.folder_renamer = FolderRenamer(debug=self.debug)
        
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
            
            # Process normal results (moved outside of the error check block)
            if series_list and not error_handled:
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
                            # Show series details using the same formatting as albums
                            html = "<b>Série sélectionnée :</b><br><br>"
                            
                            # Title and main info
                            html += f"<b>Titre :</b> {series_data.get('serie_name', 'N/A')}<br>"
                            html += f"<b>Année de début :</b> {series_data.get('start_year', 'N/A')}<br>"
                            html += f"<b>Éditeur :</b> {series_data.get('publisher', 'N/A')}<br>"
                            
                            # ComicVine links
                            if series_data.get('api_detail_url'):
                                html += f"<b>Page ComicVine :</b> <a href='{series_data['api_detail_url']}'>Voir sur ComicVine</a><br>"
                            
                            # Volume ID
                            html += f"<b>Volume ID :</b> {volume_id}<br>"
                            
                            html += "<br><i>Récupération des albums...</i>"
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
                            # Show series details using clean formatting
                            html = "<b>Série sélectionnée :</b><br><br>"
                            
                            # Title and main info
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
                            html += f"<b>Série ID :</b> {series_id}<br>"
                            
                            html += "<br><i>Récupération des albums...</i>"
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
                                        # Note: Don't set series_cover_url here - each album has its own cover
                                        
                                        # Process UI events every 10 albums for responsiveness
                                        if r % 10 == 0:
                                            QApplication.processEvents()
                                    
                                    # Update the detail text with album count
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
                                    
                                    html += f"<br><b>{len(albums)} album(s) trouvé(s)</b>"
                                    self.detail_text.setHtml(html)
                                else:
                                    # No albums found
                                    self.album_table.setRowCount(0)
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
                                    
                                    html += "<br><i>Aucun album trouvé pour cette série.</i>"
                                    self.detail_text.setHtml(html)
                                    
                            except Exception as e:
                                print(f"[ERROR] Failed to fetch albums for series {series_name}: {e}")
                                self.album_table.setRowCount(0)
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
                                
                                html += f"<br><i>{tr('messages.errors.fetch_albums_error', error=str(e))}</i>"
                                self.detail_text.setHtml(html)
                        else:
                            # Missing series ID or name
                            self.album_table.setRowCount(0)
                            html = "<b>Série sélectionnée :</b><br><br>"
                            html += f"<b>Titre :</b> {series_data.get('serie_name', 'N/A')}<br>"
                            html += "<br><i>ID ou nom de série manquant pour récupérer les albums.</i>"
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
                    # Note: Don't set series_cover_url here - each album has its own cover
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
                                items.append(f"{display_key}: {v}")
                        return {'type': 'list', 'items': items} if items else make_links_clickable(str(value), field_name)
                else:
                    # Convert dict to structured list
                    items = []
                    for k, v in value.items():
                        if isinstance(v, (str, int, float)) and v:
                            display_key = str(k).replace('_', ' ').title()
                            items.append(f"{display_key}: {v}")
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
            # ComicVine order - optimized for better user experience
            field_order = [
                'name',           # Issue title (most important)
                'issue_number',   # Issue number
                'volume',         # Series/Volume info
                'cover_date',     # Cover date (when published)
                'store_date',     # Store date (when released)
                'description',    # Issue description
                'story_arc',      # Story arc information
                'character_credits', # Characters
                'person_credits', # Creators
                'location_credits', # Locations
                'concept_credits', # Concepts/themes
                'team_credits',   # Teams
                'id',             # ComicVine ID
                'album_url',      # ComicVine page URL
                'api_detail_url', # API detail URL
                'cover_url',      # Cover image URL
                'image'           # Image information
            ]
        
        # Display fields in the preferred order
        displayed_fields = set()
        
        # Helper function to get display name for ComicVine fields
        def get_display_name(field_name):
            """Get a user-friendly display name for ComicVine fields"""
            if self._source == 'ComicVine':
                display_names = {
                    'name': 'Title',
                    'issue_number': 'Issue #',
                    'volume': 'Series',
                    'cover_date': 'Cover Date',
                    'store_date': 'Store Date',
                    'description': 'Description',
                    'story_arc': 'Story Arc',
                    'character_credits': 'Characters',
                    'person_credits': 'Creators',
                    'location_credits': 'Locations',
                    'concept_credits': 'Concepts',
                    'team_credits': 'Teams',
                    'id': 'ComicVine ID',
                    'album_url': 'ComicVine Page',
                    'api_detail_url': 'API Details',
                    'cover_url': 'Cover Image',
                    'image': 'Image Info'
                }
                return display_names.get(field_name, field_name.replace('_', ' ').title())
            else:
                return field_name.replace('_', ' ').title()
        
        for field in field_order:
            if field in meta:
                if field == "details":
                    # Handle details specially - will be processed later
                    continue
                    
                v = meta[field]
                formatted_value = format_display_value(v, field)
                display_name = get_display_name(field)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    html += f'<li class="sub-section"><b>{display_name} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    html += f"<li><b>{display_name}</b> : {make_links_clickable(formatted_value, field)}</li>"
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
            # For ComicVine, create a better structured display
            html += "<li><b>Détails ComicVine :</b><ul>"
            
            # Add important links first
            for url_field in ['album_url', 'api_detail_url', 'cover_url']:
                if url_field in meta and meta[url_field]:
                    formatted_value = format_display_value(meta[url_field], url_field)
                    html += f"<li><b>{url_field.replace('_', ' ').title()}</b> : {make_links_clickable(formatted_value, url_field)}</li>"
                    displayed_fields.add(url_field)
            
            # Add credits section if any credits are available
            credit_fields = ['character_credits', 'person_credits', 'location_credits', 'concept_credits', 'team_credits']
            available_credits = [field for field in credit_fields if field in meta and meta[field]]
            
            if available_credits:
                html += "<li><b>Crédits :</b><ul>"
                for credit_field in available_credits:
                    if credit_field in meta and meta[credit_field]:
                        formatted_value = format_display_value(meta[credit_field], credit_field)
                        display_name = credit_field.replace('_credits', '').replace('_', ' ').title() + 's'
                        if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                            html += f'<li class="sub-section"><b>{display_name} :</b><ul class="sub-list">'
                            for item in formatted_value.get('items', []):
                                html += f"<li>{item}</li>"
                            html += "</ul></li>"
                        else:
                            html += f"<li><b>{display_name}</b> : {make_links_clickable(formatted_value, credit_field)}</li>"
                        displayed_fields.add(credit_field)
                html += "</ul></li>"
            
            # Process any details dict if present
            details = meta.get("details")
            if isinstance(details, dict):
                html += "<li><b>Détails supplémentaires :</b><ul>"
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
                        html += f'<li class="sub-section"><b>{k.replace("_", " ").title()} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        html += f"<li><b>{k.replace('_', ' ').title()}</b> : {make_links_clickable(formatted_value, k)}</li>"
            
            html += "</ul></li>"
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
            
        # Check if Safe Rename is enabled and file is PDF
        safe_rename_enabled = self.settings.value('safe_rename', 'false') == 'true'
        file_path = str(f['path'])
        is_pdf = file_path.lower().endswith('.pdf')
        
        if safe_rename_enabled and is_pdf:
            # Perform cover comparison for PDF files
            success = self._perform_safe_rename_check(f, meta)
            if not success:
                return  # User cancelled or comparison failed
                
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

    def _perform_safe_rename_check(self, file_info, meta):
        """
        Perform Safe Rename check by comparing PDF cover with album cover.
        
        Args:
            file_info (dict): File information
            meta (dict): Album metadata
            
        Returns:
            bool: True if rename should proceed, False if cancelled
        """
        try:
            # Try Qt-native version first (no Poppler dependency)
            try:
                from pdf_cover_comparator_qt import PDFCoverComparator
                comparator_type = "Qt-native"
            except ImportError:
                # Fallback to Poppler-based version
                from pdf_cover_comparator import PDFCoverComparator
                comparator_type = "Poppler-based"
            
            from cover_comparison_dialog import CoverComparisonDialog
            
            # Get cover URL from metadata
            cover_url = meta.get('cover_url', '')
            if not cover_url:
                # Try alternative fields
                cover_url = meta.get('image_url', '')
                if not cover_url and meta.get('image'):
                    cover_url = meta.get('image', {}).get('original_url', '')
            
            if not cover_url:
                if self.debug:
                    print("[DEBUG] No cover URL found in metadata, skipping Safe Rename check")
                return True  # No cover to compare, proceed with rename
            
            # Create comparator
            threshold = 0.7  # Could be made configurable in settings later
            comparator = PDFCoverComparator(ssim_threshold=threshold)
            
            # Perform comparison
            if self.debug:
                print(f"[DEBUG] Safe Rename ({comparator_type}): Comparing {file_info['path']} with {cover_url}")
                
            result = comparator.compare(str(file_info['path']), cover_url)
            
            if result['match']:
                if self.debug:
                    print(f"[DEBUG] Safe Rename: Cover match successful (score: {result['ssim_score']:.3f})")
                # Clean up temp files
                comparator.cleanup_temp_files(result.get('temp_files', []))
                return True  # Good match, proceed with rename
            else:
                if self.debug:
                    print(f"[DEBUG] Safe Rename: Cover mismatch detected (score: {result['ssim_score']:.3f})")
                
                # Show comparison dialog
                file_name = os.path.basename(file_info['path'])
                album_name = meta.get('album_name') or meta.get('name') or 'Unknown Album'
                
                dialog = CoverComparisonDialog(
                    parent=self,
                    pdf_image_path=result.get('pdf_image_path'),
                    cover_image_path=result.get('cover_image_path'),
                    ssim_score=result['ssim_score'],
                    threshold=threshold,
                    file_name=file_name,
                    album_name=album_name
                )
                
                dialog.exec()
                user_choice = dialog.get_user_choice()
                
                # Clean up temp files
                comparator.cleanup_temp_files(result.get('temp_files', []))
                
                return user_choice == 'proceed'
                
        except ImportError as e:
            if self.debug:
                print(f"[DEBUG] Safe Rename dependencies not available: {e}")
            QMessageBox.warning(
                self, 
                "Safe Rename Unavailable", 
                "Safe Rename feature requires additional dependencies.\n"
                "Please install: pip install opencv-python scikit-image"
            )
            return True  # Proceed without check if dependencies missing
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Safe Rename error: {e}")
            
            # Check if user wants to skip problematic PDFs
            skip_problematic = self.settings.value('skip_problematic_pdfs', 'false') == 'true'
            
            # Check if this is a PDF loading issue
            error_msg = str(e)
            if "Failed to load PDF" in error_msg or "Failed to extract first page" in error_msg:
                if skip_problematic:
                    if self.debug:
                        print(f"[DEBUG] Skipping Safe Rename for problematic PDF (user setting enabled)")
                    return True  # Skip check and proceed with rename
                
                # This is a PDF-specific issue - show detailed dialog
                reply = QMessageBox.question(
                    self,
                    "PDF Loading Issue",
                    f"Cannot verify PDF cover due to file format issues:\n\n"
                    f"{error_msg}\n\n"
                    f"This can happen with:\n"
                    f"• Password-protected PDFs\n"
                    f"• Corrupted PDF files\n"
                    f"• Unsupported PDF formats\n"
                    f"• Files with special security features\n\n"
                    f"Would you like to proceed with the rename anyway?\n\n"
                    f"💡 Tip: You can disable Safe Rename for problematic PDFs in Settings",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            else:
                # Generic error
                reply = QMessageBox.question(
                    self,
                    "Safe Rename Error",
                    f"Cover comparison failed: {e}\n\nProceed with rename anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            
            return reply == QMessageBox.Yes

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
        
        # Use FolderRenamer to get rename info
        serie_name, style, new_folder_name = self.folder_renamer.get_folder_rename_info(current_folder, meta)
        
        if not serie_name:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.cannot_determine_series"))
            return
        
        # Print debug info
        self.folder_renamer.debug_info(current_folder, serie_name, style, new_folder_name, meta)
        
        # Validate the rename
        is_valid, reason = self.folder_renamer.validate_rename(current_folder, new_folder_name)
        if not is_valid:
            if reason == "Folder name is already the target name":
                QMessageBox.information(self, "Info", "Le dossier porte déjà ce nom.")
                return
            elif "already exists" in reason:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_already_exists", name=new_folder_name))
                return
            else:
                QMessageBox.critical(self, tr("messages.errors.error"), reason)
                return
        
        # Confirm the rename operation
        if QMessageBox.question(
            self,
            tr("messages.errors.rename_folder_title"),
            tr("dialogs.rename_confirmation.folder_message", old_name=current_folder.name, new_name=new_folder_name),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            # Perform the rename
            success, error_msg, new_folder_path = self.folder_renamer.perform_rename(current_folder, new_folder_name)
            
            if success:
                # Reload files from the new location
                self._load_files(str(new_folder_path))
                QMessageBox.information(self, tr("messages.errors.success_title"), tr("messages.errors.folder_renamed", name=new_folder_name))
            else:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_rename_error", error=error_msg))

    def _confirm_and_rename_folder(self, old_name, new_name):
        """Handle folder rename from direct editing of folder name"""
        if not self.files:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.no_files_in_folder"))
            return False
            
        current_folder = pathlib.Path(self.files[0]['folder'])
        
        # Clean up the new name using FolderRenamer
        new_name_clean = self.folder_renamer.clean_folder_name(new_name)
        
        if not new_name_clean:
            QMessageBox.warning(self, tr("messages.errors.error"), "Le nouveau nom de dossier ne peut pas être vide.")
            return False
        
        # Validate the rename
        is_valid, reason = self.folder_renamer.validate_rename(current_folder, new_name_clean)
        if not is_valid:
            if "already exists" in reason:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_already_exists", name=new_name_clean))
                return False
            else:
                QMessageBox.critical(self, tr("messages.errors.error"), reason)
                return False
        
        # Confirm the rename operation
        if QMessageBox.question(
            self,
            tr("messages.errors.rename_folder_title"),
            tr("dialogs.rename_confirmation.folder_message", old_name=old_name, new_name=new_name_clean),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            # Perform the rename
            success, error_msg, new_folder_path = self.folder_renamer.perform_rename(current_folder, new_name_clean)
            
            if success:
                # Reload files from the new location
                self._load_files(str(new_folder_path))
                QMessageBox.information(self, tr("messages.errors.success_title"), tr("messages.errors.folder_renamed", name=new_name_clean))
                return True
            else:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.folder_rename_error", error=error_msg))
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