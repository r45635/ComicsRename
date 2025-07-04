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
from core import (
    FolderRenamer, DetailsFormatter, AlbumPopulator, 
    SettingsManager, ErrorHandler, FilenameGenerator, 
    ImageManager, SafeRenameManager, SearchManager
)

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
        
        # Initialize new core modules
        self.settings_manager = SettingsManager()
        self.error_handler = ErrorHandler(parent_widget=self, debug=self.settings_manager.get_debug_mode())
        self.filename_generator = FilenameGenerator(debug=self.settings_manager.get_debug_mode())
        self.image_manager = ImageManager(debug=self.settings_manager.get_debug_mode())
        self.safe_rename_manager = SafeRenameManager(
            self.settings_manager, 
            self.error_handler, 
            self.image_manager,
            debug=self.settings_manager.get_debug_mode()
        )
        
        # Initialize search manager
        self.search_manager = SearchManager(
            parent=self,
            debug=self.settings_manager.get_debug_mode(),
            verbose=self.settings_manager.get_verbose_mode()
        )
        
        # Keep legacy settings for backward compatibility
        self.settings = QSettings("ComicsRename", "App")
        
        # Get settings from new manager
        self.debug = self.settings_manager.get_debug_mode()
        self.verbose = self.settings_manager.get_verbose_mode()
        
        # Initialize default provider first
        self.default_provider = self.settings_manager.get_default_provider()
        
        # Initialize folder renamer
        self.folder_renamer = FolderRenamer(debug=self.debug)
        
        # Initialize details formatter (will be updated when source changes)
        self.details_formatter = DetailsFormatter(source=self.default_provider, debug=self.debug)
        
        # Initialize album populator
        self.album_populator = AlbumPopulator(self, debug=self.debug)
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
        default_provider = str(self.settings.value("default_provider", "BDGest"))
        idx = self.source_combo.findText(default_provider)
        if idx >= 0:
            self.source_combo.setCurrentIndex(idx)
        self._source = self.source_combo.currentText()
        
        # Show/hide SeriesName checkbox based on initial provider
        if self._source in ['BDGest', 'ComicVine']:
            self.series_name_cb.setVisible(True)
        else:
            self.series_name_cb.setVisible(False)

        # Chargement robuste du dernier dossier utilisé
        last_folder = self.settings.value("last_folder", "")
        if last_folder and isinstance(last_folder, str) and pathlib.Path(last_folder).exists():
            try:
                # Teste si le dossier est lisible (pas seulement existant)
                test = os.listdir(last_folder)
                self._load_files(last_folder)
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Impossible de charger le dossier au démarrage : {e}")
                self.folder_display.setText("Cliquez sur 'Choisir dossier' pour commencer")
        else:
            self.folder_display.setText("Cliquez sur 'Choisir dossier' pour commencer")

    def keyPressEvent(self, event):
        """Handle key press events - Escape cancels search"""
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key.Key_Escape and self._search_in_progress:
            # Cancel search with Escape key
            self._search_cancelled = True
            self._restore_search_ui()
            self.detail_text.setHtml("<i>Search cancelled by user (Escape key)</i>")
            print("[INFO] Search operation cancelled by user (Escape key)")
        else:
            # Pass other events to parent
            super().keyPressEvent(event)

    def _build_ui(self):
        """Build the main user interface"""
        layout = QVBoxLayout(self)
        
        # Build UI components
        toolbar_layout = self._build_toolbar()
        layout.addLayout(toolbar_layout)
        
        splitter_main = self._build_main_content()
        layout.addWidget(splitter_main)
        layout.addWidget(self.rename_btn)
        
        # Connect signals and finalize
        self._connect_signals()
        self._adjust_table_columns()

    def _build_toolbar(self):
        """Build the top toolbar with search and navigation controls"""
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
        return ctrl

    def _build_main_content(self):
        """Build the main content area with file and album panels"""
        splitter_main = QSplitter(Qt.Orientation.Horizontal)

        # Build file panel
        file_panel = self._build_file_panel()
        splitter_main.addWidget(file_panel)
        
        # Build album panel
        album_panel = self._build_album_panel()
        splitter_main.addWidget(album_panel)
        
        return splitter_main

    def _build_file_panel(self):
        """Build the file management panel"""
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
        return file_panel

    def _build_album_panel(self):
        """Build the album management panel"""
        splitter_right = QSplitter(Qt.Orientation.Vertical)
        
        # Album list section
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

        # Album details section
        albums_mgmt_widget = self._build_album_details_section()
        splitter_right.addWidget(albums_mgmt_widget)

        # Store splitter reference for image resize handling
        self.splitter_right = splitter_right
        return splitter_right

    def _build_album_details_section(self):
        """Build the album details and cover section"""
        # Albums Management Area (regrouped album details + cover)
        albums_mgmt_widget = QWidget()
        albums_mgmt_widget.setWindowTitle("Albums Management")  # For potential future groupbox styling
        albums_mgmt_layout = QHBoxLayout(albums_mgmt_widget)
        
        # Album Details Section
        self.detail_text = QTextBrowser()  # Use QTextBrowser instead of QTextEdit for better link support
        
        # Configure QTextBrowser for better link handling and styling
        self.detail_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        # QTextBrowser has built-in support for opening external links
        self.detail_text.setOpenExternalLinks(True)
        
        # Album Cover Section
        self.detail_image = QLabel()
        # Configure image label to be responsive and centered
        self.detail_image.setScaledContents(False)  # Don't force scaling to fill
        self.detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image
        self.detail_image.setMinimumSize(50, 50)  # Small minimum size
        self.detail_image.setMaximumSize(300, 400)  # Reasonable maximum
        self.detail_image.setSizePolicy(self.detail_image.sizePolicy().horizontalPolicy(), 
                                       self.detail_image.sizePolicy().verticalPolicy())
        # Make cover image clickable for Amazon search
        self.detail_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detail_image.mousePressEvent = self._on_cover_image_clicked
        
        # Add both sections to the albums management area
        albums_mgmt_layout.addWidget(self.detail_text, 2)  # Album details take 2/3 of space
        albums_mgmt_layout.addWidget(self.detail_image, 1)  # Album cover takes 1/3 of space
        
        return albums_mgmt_widget

        splitter_main = QSplitter(Qt.Orientation.Horizontal)

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

        splitter_right = QSplitter(Qt.Orientation.Vertical)
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
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        # QTextBrowser has built-in support for opening external links
        self.detail_text.setOpenExternalLinks(True)
        
        # Album Cover Section
        self.detail_image = QLabel()
        # Configure image label to be responsive and centered
        self.detail_image.setScaledContents(False)  # Don't force scaling to fill
        self.detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image
        self.detail_image.setMinimumSize(50, 50)  # Small minimum size
        self.detail_image.setMaximumSize(300, 400)  # Reasonable maximum
        self.detail_image.setSizePolicy(self.detail_image.sizePolicy().horizontalPolicy(), 
                                       self.detail_image.sizePolicy().verticalPolicy())
        # Make cover image clickable for Amazon search
        self.detail_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detail_image.mousePressEvent = self._on_cover_image_clicked
        
        # Add both sections to the albums management area
        albums_mgmt_layout.addWidget(self.detail_text, 2)  # Album details take 2/3 of space
        albums_mgmt_layout.addWidget(self.detail_image, 1)  # Album cover takes 1/3 of space
        
        return albums_mgmt_widget

    def _connect_signals(self):
        """Connect all UI signals to their handlers"""
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
        self.splitter_right.splitterMoved.connect(self._update_cover_image_size)

        # Connect selection change to update folder display
        self.file_table.selectionModel().selectionChanged.connect(self._update_folder_display)
        
        # Connect search manager signals
        self.search_manager.search_started.connect(self._on_search_started)
        self.search_manager.search_completed.connect(self._on_search_completed)
        self.search_manager.search_cancelled.connect(self._on_search_cancelled)
        self.search_manager.search_error.connect(self._on_search_error)
        self.search_manager.progress_updated.connect(self._on_search_progress)

    def _adjust_table_columns(self):
        # Adjust file_table: set 'Name' column to fit contents, others to reasonable defaults
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        # Optionally, set minimum width for 'Name' column
        self.file_table.setColumnWidth(0, max(200, self.file_table.sizeHintForColumn(0)))

        # Adjust album_table: single column stretches to fill available space
        self.album_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def _restore_session(self):
        # Restore UI settings only - NO automatic folder loading
        fc = self.settings.value('file_cols')
        if fc:
            for i,w in enumerate(map(int,fc.split(','))):
                self.file_table.setColumnWidth(i,w)
        ac = self.settings.value('album_cols')
        if ac:
            self.album_table.setColumnWidth(0,int(ac))
        
        # Show welcome message instead of auto-loading
        self.folder_display.setText("Cliquez sur 'Choisir dossier' pour commencer")
        
        # Note: We intentionally do NOT load the last folder automatically
        # to prevent startup hangs when the folder doesn't exist or is slow to access

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
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        
        return scaled_pixmap

    def _change_source(self,src):
        self._source=src
        # Update details formatter source
        self.details_formatter = DetailsFormatter(source=src, debug=self.debug)
        
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
        btn_volumes = msg.addButton("Disques externes (/Volumes)", QMessageBox.ButtonRole.ActionRole)
        btn_last = msg.addButton("Dernier dossier utilisé", QMessageBox.ButtonRole.ActionRole)
        btn_home = msg.addButton("Dossier personnel", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton(QMessageBox.StandardButton.Cancel)
        
        # Disable "last folder" button if no folder is stored or if it's not accessible
        if not current_folder or not isinstance(current_folder, str) or not pathlib.Path(current_folder).exists():
            btn_last.setEnabled(False)
            btn_last.setText("Dernier dossier utilisé (indisponible)")
        
        msg.exec()
        if msg.clickedButton() == btn_volumes:
            start_dir = "/Volumes"
        elif msg.clickedButton() == btn_last:
            if current_folder and isinstance(current_folder, str) and pathlib.Path(current_folder).exists():
                start_dir = current_folder
            else:
                # Safe fallback - don't use the problematic _get_fallback_folder_path
                QMessageBox.information(self, "Information", "Le dossier précédent n'est plus accessible. Utilisation du dossier personnel.")
                start_dir = str(pathlib.Path.home())
        elif msg.clickedButton() == btn_home:
            start_dir = str(pathlib.Path.home())
        else:
            return  # Cancelled

        dialog = QFileDialog(self, 'Select Folder', start_dir)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)  # <-- This enables the "Up" button
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
        if self.search_manager.is_search_in_progress():
            # Cancel current search
            self.search_manager.cancel_search()
            print("[INFO] Search operation cancelled by user")
        else:
            # Start new search
            self._search()

    def _search(self):
        """Execute search using the SearchManager"""
        q = self.search_bar.text().strip()
        if not q:
            return
            
        # Clear previous results
        self.series_combo.clear()
        self.album_table.clearContents()
        self.album_table.setRowCount(0)
        self.series_cover_url = ''
        self.detail_text.clear()
        self.detail_image.clear()
        self._original_cover_pixmap = None
        self.issues_by_series.clear()
        self._bdgest_album_results = []
        
        # Use SearchManager to execute the search
        series_name_mode = self.series_name_cb.isChecked()
        self.search_manager.search(q, self._source, series_name_mode)
        
    def _on_search_started(self):
        """Handle search started signal"""
        self._search_cancelled = False
        self._search_in_progress = True
        self.search_btn.setText("⏹️ Cancel Search")
        self.search_btn.setToolTip("Cancel current search operation")
        
    def _on_search_completed(self, results):
        """Handle search completed signal"""
        result_type = results.get('type')
        
        if result_type == 'series_results':
            self._handle_series_results(results)
        elif result_type == 'comicvine_albums':
            self._handle_comicvine_albums(results)
        elif result_type == 'comicvine_issues':
            self._handle_comicvine_issues(results)
        elif result_type == 'bdgest_albums':
            self._handle_bdgest_albums(results)
            
        self._restore_search_ui()
        
    def _on_search_cancelled(self):
        """Handle search cancelled signal"""
        self._search_cancelled = True
        self._restore_search_ui()
        self.detail_text.setHtml("<i>Search cancelled by user</i>")
        
    def _on_search_error(self, title, message):
        """Handle search error signal"""
        QMessageBox.critical(self, title, message)
        self._restore_search_ui()
        
    def _on_search_progress(self, message):
        """Handle search progress updates"""
        self.detail_text.setHtml(f"<i>{message}</i>")
        QApplication.processEvents()  # Allow UI updates
        
    def _handle_series_results(self, results):
        """Handle series search results"""
        series_results = results.get('series_results', [])
        source = results.get('source')
        
        # Store series results based on provider
        if source == 'BDGest':
            self._bdgest_series_results = series_results
            self._bdgest_album_results = []
        else:  # ComicVine
            self._comicvine_series_results = series_results
            self.issues_by_series.clear()
            
        # Populate series dropdown
        for series in series_results:
            series_name = series.get('serie_name', 'Unknown Series')
            
            if series_name and series_name != 'Unknown Series':
                self.series_combo.addItem(series_name)
                idx = self.series_combo.count() - 1
                self.series_combo.setItemData(idx, series, Qt.ItemDataRole.UserRole)
                
        # Show results and auto-load first series
        if self.series_combo.count() > 0:
            series_count = self.series_combo.count()
            instruction_html = f"<b>🔍 Recherche terminée</b><br><br>"
            instruction_html += f"<b>{series_count} série(s) trouvée(s)</b><br><br>"
            if series_count == 1:
                instruction_html += f"<i>📖 Chargement des albums de la série unique...</i>"
            else:
                instruction_html += f"<i>📚 Chargement des albums de la première série...</i>"
            self.detail_text.setHtml(instruction_html)
            self.detail_image.clear()
            
            # Auto-load albums for the first series
            first_series_name = self.series_combo.itemText(0)
            self._populate_albums(first_series_name)
        else:
            title = tr("messages.info.no_result")
            message = tr("messages.errors.no_series_found")
            QMessageBox.information(self, title, message)
            
    def _handle_comicvine_albums(self, results):
        """Handle ComicVine albums search results"""
        issues_by_series = results.get('issues_by_series', {})
        self.issues_by_series = issues_by_series
        
        if not issues_by_series:
            QMessageBox.warning(self, tr("messages.info.no_result"), tr("messages.errors.no_results"))
            return
            
        # Populate series dropdown with album counts
        for s in sorted(issues_by_series):
            self.series_combo.addItem(f"{s} ({len(issues_by_series[s])})")
            
        # Auto-select the first series to show albums immediately
        if self.series_combo.count() > 0:
            self.series_combo.setCurrentIndex(0)
            first_series_text = self.series_combo.currentText()
            self._populate_albums(first_series_text)
            
    def _handle_comicvine_issues(self, results):
        """Handle ComicVine issues search results"""
        issues_by_series = results.get('issues_by_series', {})
        self.issues_by_series = issues_by_series
        
        for s in sorted(issues_by_series):
            self.series_combo.addItem(f"{s} ({len(issues_by_series[s])})")
            
        if not issues_by_series:
            QMessageBox.warning(self, 'Résultat', 'Aucun album trouvé pour cette recherche.')
            
    def _handle_bdgest_albums(self, results):
        """Handle BDGest albums search results"""
        albums = results.get('albums', [])
        self._bdgest_album_results = albums
        self._bdgest_series_results = []
        
        # Populate series dropdown
        series_seen = set()
        for album in albums:
            s = album.get('serie_name', '')
            serie_id = album.get('series_id', '')
            if s and s not in series_seen:
                self.series_combo.addItem(s)
                idx = self.series_combo.count() - 1
                self.series_combo.setItemData(idx, serie_id, Qt.ItemDataRole.UserRole)
                series_seen.add(s)
                
        if not albums:
            title = tr("messages.info.no_result")
            message = tr("messages.errors.no_albums_found")
            QMessageBox.information(self, title, message)

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
        debug = self.settings_manager.get_debug_mode()
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
                    series_data = self.series_combo.itemData(series_index, Qt.ItemDataRole.UserRole)
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
                                
                                debug = self.settings_manager.get_debug_mode()
                                verbose = self.settings_manager.get_verbose_mode()
                                
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
                                    itm.setData(Qt.ItemDataRole.UserRole, issue)
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
                        itm.setData(Qt.ItemDataRole.UserRole, it)
                        self.album_table.setItem(r, 0, itm)
        else:  # BDGest
            # Check if we're in series mode (SeriesName checkbox checked)
            if self.series_name_cb.isChecked() and self._bdgest_series_results:
                # In series mode - fetch and display albums for the selected series
                current_index = self.series_combo.currentIndex()
                if current_index >= 0:
                    series_data = self.series_combo.itemData(current_index, Qt.ItemDataRole.UserRole)
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
                                
                                debug = self.settings_manager.get_debug_mode()
                                verbose = self.settings_manager.get_verbose_mode()
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
                                        itm.setData(Qt.ItemDataRole.UserRole, alb)
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
                    itm.setData(Qt.ItemDataRole.UserRole, alb)
                    self.album_table.setItem(r, 0, itm)
                    # Note: Don't set series_cover_url here - each album has its own cover
        if self.folder_rename_btn is not None:
            self.folder_rename_btn.setEnabled(False)  # Disable when repopulating albums
        # Adjust album table column after populating
        self.album_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def _show_details(self, r, c):
        if self.debug:
            print(f"[DEBUG] _show_details called for row {r}, col {c}")
        itm = self.album_table.item(r, 0)
        meta = itm.data(Qt.ItemDataRole.UserRole) if itm else None
        
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
        
        # Use DetailsFormatter to generate HTML
        html = self.details_formatter.format_metadata_to_html(meta)
        self.detail_text.setHtml(html)
        
        # Handle cover image loading
        self._load_cover_image(meta)
    
    def _load_cover_image(self, meta):
        """Load and display cover image from metadata using ImageManager."""
        img_url = meta.get('cover_url') or meta.get('image', {}).get('original_url')
        
        if not img_url:
            if self.debug:
                print("[DEBUG] No cover image URL found")
            self.detail_image.clear()
            return
        
        try:
            # Use ImageManager to load and cache the image
            provider = self.settings_manager.get_default_provider().lower()
            pixmap, cached_path = self.image_manager.load_and_cache_cover(img_url, meta, provider)
            
            if pixmap and not pixmap.isNull():
                # Update album metadata in the table with the cached path
                current_row = self.album_table.currentRow()
                if current_row >= 0:
                    current_item = self.album_table.item(current_row, 0)
                    if current_item:
                        # Use proper Qt enum access
                        from PySide6.QtCore import Qt
                        current_item.setData(Qt.ItemDataRole.UserRole, meta)
                        if self.debug:
                            print(f"[DEBUG] Updated album metadata with cached cover path")
                
                # Store original for future rescaling
                self._original_cover_pixmap = pixmap
                
                # Scale to fit available space while maintaining aspect ratio
                scaled_pm = self.image_manager.scale_image_to_fit(pixmap)
                self.detail_image.setPixmap(scaled_pm)
                
                # Force update to ensure the new image is displayed
                self.detail_image.update()
                self.detail_image.repaint()
                
                if self.debug:
                    print(f"[DEBUG] Cover image loaded successfully, size: {pixmap.width()}x{pixmap.height()}")
                    if cached_path:
                        print(f"[DEBUG] Cover image cached at: {cached_path}")
            else:
                if self.debug:
                    print(f"[DEBUG] Failed to load cover image from: {img_url}")
                self.detail_image.clear()
                
        except Exception as e:
            self.error_handler.log_error(f"Image load failed for URL {img_url}", e)
            self.detail_image.clear()

    def _unified_rename_file(self, file_info, meta, show_confirmation=True):
        """
        Unified method to rename a file with metadata.
        Handles SafeRename, filename generation, and actual renaming.
        
        Args:
            file_info (dict): File information with 'path', 'folder', 'ext' keys
            meta (dict): Album metadata
            show_confirmation (bool): Whether to show confirmation dialog
            
        Returns:
            bool: True if rename was successful, False if cancelled or failed
        """
        if not meta:
            if show_confirmation:
                QMessageBox.critical(self, 'Error', 'Album metadata missing')
            return False
            
        print(f"[DEBUG] Unified rename - Starting for: {file_info['path']}")
        print(f"[DEBUG] Unified rename - Meta keys: {list(meta.keys()) if isinstance(meta, dict) else 'Not a dict'}")
        
        # Check if Safe Rename is enabled and file is PDF
        safe_rename_enabled = self.settings.value('safe_rename', 'false') == 'true'
        file_path = str(file_info['path'])
        is_pdf = file_path.lower().endswith('.pdf') or file_info['ext'].lower() == 'pdf'
        
        print(f"[DEBUG] Unified rename - SafeRename enabled: {safe_rename_enabled}")
        print(f"[DEBUG] Unified rename - File is PDF: {is_pdf}")
        
        # SafeRename status tracking
        safe_rename_passed = False
        safe_rename_score = 0.0
        
        # IMPORTANT: SafeRename BEFORE asking user confirmation
        if safe_rename_enabled and is_pdf:
            print(f"[DEBUG] Unified rename - Performing SafeRename check")
            result = self._perform_safe_rename_check(file_info, meta)
            print(f"[DEBUG] Unified rename - SafeRename result: {result}")
            
            if not result['proceed']:
                print(f"[DEBUG] Unified rename - SafeRename cancelled: {result['reason']}")
                return False  # SafeRename failed or user cancelled
            else:
                # SafeRename passed
                safe_rename_passed = True
                safe_rename_score = result.get('comparison_score', 0.0)
                
        # Build new filename
        series = meta.get('serie_name') or meta.get('series') or (meta.get('volume') or {}).get('name', '')
        num = meta.get('album_number') or meta.get('num') or meta.get('issue_number') or ''
        title = meta.get('album_name') or meta.get('title') or meta.get('name') or ''
        
        # Extract year from various date fields
        y = ''
        date_fields = ['date', 'parution', 'cover_date', 'year']
        for field in date_fields:
            date_str = meta.get(field, '')
            if date_str:
                import re
                year_match = re.search(r'(\d{4})', str(date_str))
                if year_match:
                    y = year_match.group(1)
                    break
        
        # Format number and clean strings
        def format_num(n):
            try:
                n_int = int(n)
                return f"{n_int:02d}"
            except Exception:
                return str(n)
        
        def clean(s):
            if self.debug:
                print(f"[DEBUG] clean() input: {repr(s)}")
            cleaned = re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
            if self.debug:
                print(f"[DEBUG] clean() output: {repr(cleaned)}")
            return cleaned
        
        if self.debug:
            print(f"[DEBUG] Unified rename - series: {repr(series)}")
            print(f"[DEBUG] Unified rename - num: {repr(num)}")
            print(f"[DEBUG] Unified rename - title: {repr(title)}")
            print(f"[DEBUG] Unified rename - year: {repr(y)}")
        
        # Build filename: Serie Name - Album Number - Album Title (Year)
        base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
        if y:
            base += f" ({y})"
            
        # Ensure extension does not have a leading dot
        ext = file_info['ext'].lstrip('.')
        new_name = f"{base}.{ext}"
        new_path = pathlib.Path(file_info['folder']) / new_name
        
        print(f"[DEBUG] Unified rename - New filename: {new_name}")
        print(f"[DEBUG] Unified rename - New path: {new_path}")
        
        # Check if target file already exists
        if new_path.exists():
            if show_confirmation:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_already_exists", name=new_name))
            return False
        
        # Ask for user confirmation if requested
        if show_confirmation:
            # Use enhanced confirmation dialog that shows SafeRename status
            from enhanced_rename_confirmation_dialog import show_enhanced_rename_confirmation
            
            confirm = show_enhanced_rename_confirmation(
                parent=self,
                new_name=new_name,
                safe_rename_passed=safe_rename_passed,
                safe_rename_score=safe_rename_score,
                is_folder=False
            )
            
            if confirm != QMessageBox.StandardButton.Yes:
                print(f"[DEBUG] Unified rename - User cancelled confirmation")
                return False
        
        # Perform the actual rename
        try:
            if not os.path.exists(str(file_info['path'])):
                if show_confirmation:
                    QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_not_exists", path=file_info['path']))
                return False
                
            print(f"[DEBUG] Unified rename - Performing rename")
            os.rename(str(file_info['path']), str(new_path))
            self._load_files(file_info['folder'])
            print(f"[DEBUG] Unified rename - Rename successful")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Unified rename - Error: {e}")
            if show_confirmation:
                QMessageBox.critical(self, tr("messages.errors.rename_error"), str(e))
            return False

    def _rename_selected(self):
        fr = self.file_table.currentRow()
        ar = self.album_table.currentRow()
        if fr < 0 or ar < 0:
            QMessageBox.warning(self, 'Selection', 'Please select one file and one album')
            return
        f = self.files[fr]
        itm = self.album_table.item(ar, 0)
        meta = itm.data(Qt.ItemDataRole.UserRole) if itm else None
        
        # Use unified rename method
        if self._unified_rename_file(f, meta):
            QMessageBox.information(self, "Renaming", "Renaming successful")
        else:
            QMessageBox.warning(self, "Renaming", "Renaming failed or cancelled")

    def _perform_safe_rename_check(self, file_info, meta):
        """
        Perform Safe Rename check by comparing PDF cover with album cover.
        Uses the new SafeRenameManager for all logic.
        
        Args:
            file_info (dict): File information
            meta (dict): Album metadata
            
        Returns:
            dict: {
                'proceed': bool,  # True if rename should proceed
                'reason': str,    # Reason for the result
                'user_cancelled': bool  # True if user explicitly cancelled
            }
        """
        return self.safe_rename_manager.check_rename_safety(file_info, meta)

    def _open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec():
            # Invalidate BDGest session when settings change (credentials might have changed)
            bdgest_provider = PROVIDERS.get('BDGest')
            if bdgest_provider and hasattr(bdgest_provider, '_invalidate_session'):
                bdgest_provider._invalidate_session()
            
            # Met à jour le selector après modification des paramètres
            new_provider = self.settings.value("default_provider", "BDGest")
            if isinstance(new_provider, str):
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
            last_folder = self.settings.value('last_folder', '')
            if isinstance(last_folder, str):
                self.folder_display.setText(os.path.basename(last_folder.rstrip('/\\')))
        
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
        meta = itm.data(Qt.ItemDataRole.UserRole) if itm else None
        if not meta:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.album_metadata_missing"))
            return
        
        # Use FolderRenamer to get rename info
        serie_name, style, new_folder_name = self.folder_renamer.get_folder_rename_info(current_folder, meta)
        
        if not serie_name:
            QMessageBox.warning(self, tr("messages.errors.error"), tr("messages.errors.cannot_determine_series"))
            return
        
        # Check if we have a single file selected (special case for extended options)
        selected_files = self._get_selected_files()
        if len(selected_files) == 1:
            # Show extended folder rename options dialog
            self._show_extended_folder_options(current_folder, new_folder_name, meta)
        else:
            # Use original logic for multiple files or no selection
            self._handle_standard_folder_rename(current_folder, new_folder_name, meta)
    
    def _get_selected_files(self):
        """Get list of selected files from the file table."""
        selected_rows = self.file_table.selectionModel().selectedRows()
        selected_files = []
        for index in selected_rows:
            if index.row() < len(self.files):
                selected_files.append(self.files[index.row()])
        return selected_files
    
    def _show_extended_folder_options(self, current_folder, new_folder_name, meta):
        """
        Show extended folder rename options dialog for single file selection.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            new_folder_name (str): Proposed folder name
            meta (dict): Album metadata
        """
        # Import the dialog
        from ui.folder_rename_options_dialog import show_folder_rename_options
        
        # Determine parent and root folders
        parent_folder = current_folder.parent if current_folder.parent != current_folder else None
        root_folder = pathlib.Path(self.folder_display.text()) if hasattr(self, 'folder_display') else None
        
        # Show the dialog
        options = show_folder_rename_options(
            parent=self,
            current_folder=current_folder,
            series_name=new_folder_name,
            parent_folder=parent_folder,
            root_folder=root_folder
        )
        
        if options:
            # Pour un seul fichier sélectionné, ne traiter QUE ce fichier
            selected_files = self._get_selected_files()
            files_to_process = selected_files if selected_files else self.files
            
            # Execute the selected operation
            result = self.folder_renamer.handle_folder_rename_options(
                files_to_process, current_folder, options
            )
            
            if result['success']:
                # Show success message
                if result.get('operation') == 'rename':
                    success_msg = result['message']
                    new_path = result['new_path']
                else:
                    # Move operation
                    moved = result.get('moved_count', 0)
                    skipped = result.get('skipped_count', 0)
                    failed = result.get('failed_count', 0)
                    
                    success_msg = f"Opération terminée:\n• {moved} fichier(s) déplacé(s)"
                    if skipped > 0:
                        success_msg += f"\n• {skipped} fichier(s) ignoré(s)"
                    if failed > 0:
                        success_msg += f"\n• {failed} fichier(s) en échec"
                    
                    if result.get('cleanup_performed'):
                        success_msg += f"\n• Dossier source vide supprimé"
                    
                    new_path = result.get('target_path')
                
                QMessageBox.information(self, "Succès", success_msg)
                
                # Reload files from new location
                if new_path:
                    self._load_files(str(new_path))
            else:
                # Show error message
                error_msg = result.get('error', 'Unknown error')
                QMessageBox.critical(self, "Erreur", error_msg)
    
    def _handle_standard_folder_rename(self, current_folder, new_folder_name, meta):
        """
        Handle standard folder rename operation (original logic).
        
        Args:
            current_folder (pathlib.Path): Current folder path
            new_folder_name (str): New folder name
            meta (dict): Album metadata
        """
        # Print debug info
        serie_name, style, _ = self.folder_renamer.get_folder_rename_info(current_folder, meta)
        self.folder_renamer.debug_info(current_folder, serie_name, style, new_folder_name, meta)
        
        # Validate the rename with new logic
        status, target_path = self.folder_renamer.validate_rename_with_move_option(current_folder, new_folder_name)
        
        if status == "same_name":
            QMessageBox.information(self, "Info", "Le dossier porte déjà ce nom.")
            return
        elif status == "invalid":
            QMessageBox.critical(self, tr("messages.errors.error"), "Impossible de déterminer le nouveau nom de dossier.")
            return
        elif status == "target_exists":
            # Handle the case where target folder exists - offer to move files
            if not self._handle_existing_folder_case(current_folder, target_path, meta):
                return
        elif status == "valid":
            # Standard rename operation
            self._perform_standard_folder_rename_simple(current_folder, new_folder_name)
        else:
            QMessageBox.critical(self, tr("messages.errors.error"), f"Statut de validation inattendu: {status}")
            return

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
        2. Limited search for exact folder name in safe locations
        3. Fall back to home directory quickly if issues occur
        
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
        
        # If the folder doesn't exist, search for exact folder name in safe locations only
        try:
            import time
            start_time = time.time()
            
            parent_dir = stored_path.parent
            original_folder_name = stored_path.name
            home = pathlib.Path.home()
            
            # Debug info
            if self.debug:
                print(f"[DEBUG] Original folder '{original_folder_name}' not found at '{stored_path}'")
                print(f"[DEBUG] Searching for exact folder name in safe locations...")
            
            # Limited search in SAFE locations only (avoid /Volumes which can hang)
            safe_search_locations = []
            
            # 1. Parent directory of the original path (if it exists and is accessible)
            if parent_dir.exists() and self._is_safe_directory(parent_dir):
                safe_search_locations.append(parent_dir)
            
            # 2. Common safe folder locations
            safe_locations = [
                home / "Downloads",
                home / "Documents", 
                home / "Desktop",
                home,  # Home directory itself
            ]
            
            # Add only existing and safe locations to search
            for loc in safe_locations:
                if loc.exists() and self._is_safe_directory(loc):
                    safe_search_locations.append(loc)
            
            # Search each safe location for exact folder name match
            for search_dir in safe_search_locations:
                # Check if we've spent too much time already
                if time.time() - start_time > 10.0:  # Maximum 10 seconds total
                    if self.debug:
                        print(f"[DEBUG] Search timeout after 10 seconds, falling back to home")
                    break
                    
                try:
                    if self.debug:
                        print(f"[DEBUG] Searching in: {search_dir}")
                    
                    # Use timeout to prevent hanging on slow directories
                    found_match = self._search_directory_with_timeout(search_dir, original_folder_name)
                    if found_match:
                        if self.debug:
                            print(f"[DEBUG] FOUND exact match: {found_match}")
                        return str(found_match)
                        
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Cannot search {search_dir}: {e}")
                    continue
            
            # If we still haven't found it, do a quick broader search in home directory only
            if time.time() - start_time < 8.0:  # Only if we still have time
                if self.debug:
                    print(f"[DEBUG] Exact match not found, searching for similar folder names in home...")
                
                try:
                    for item in home.iterdir():
                        if item.is_dir():
                            # Check if folder name contains the original name (case-insensitive)
                            if original_folder_name.lower() in item.name.lower():
                                if self.debug:
                                    print(f"[DEBUG] Found similar folder: {item}")
                                return str(item)
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Cannot search home directory: {e}")
            
            # Last resort: return home directory
            elapsed = time.time() - start_time
            if self.debug:
                print(f"[DEBUG] No matches found after {elapsed:.2f}s, falling back to home directory")
            return str(home)
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Exception in _get_fallback_folder_path: {e}")
            return str(pathlib.Path.home())
    
    def _is_safe_directory(self, directory):
        """
        Check if a directory is safe to search (avoid network mounts, external drives, etc.)
        
        Args:
            directory (pathlib.Path): Directory to check
            
        Returns:
            bool: True if directory is safe to search
        """
        try:
            path_str = str(directory)
            # Avoid potentially problematic paths
            unsafe_paths = [
                '/Volumes',  # macOS external drives
                '/Network',  # Network mounts
                '/net',      # Network mounts
                '/mnt',      # Mount points
            ]
            
            for unsafe_path in unsafe_paths:
                if path_str.startswith(unsafe_path):
                    if self.debug:
                        print(f"[DEBUG] Skipping unsafe path: {path_str}")
                    return False
            
            # Additional check: try to access the directory quickly
            try:
                # Try to list just one item from the directory
                next(directory.iterdir(), None)
                return True
            except (OSError, PermissionError) as e:
                if self.debug:
                    print(f"[DEBUG] Cannot access directory {directory}: {e}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error checking directory safety {directory}: {e}")
            return False
    
    def _search_directory_with_timeout(self, directory, target_name):
        """
        Search for a folder name in a directory with timeout protection.
        
        Args:
            directory (pathlib.Path): Directory to search in
            target_name (str): Name to search for
            
        Returns:
            pathlib.Path or None: Found directory or None
        """
        try:
            import threading
            import time
            
            result = [None]  # Use list to store result from thread
            
            def search_thread():
                try:
                    for item in directory.iterdir():
                        if item.is_dir() and item.name == target_name:
                            result[0] = item
                            return
                except (OSError, PermissionError):
                    pass
            
            # Start the search in a separate thread
            thread = threading.Thread(target=search_thread)
            thread.daemon = True
            thread.start()
            
            # Wait for up to 3 seconds
            thread.join(timeout=3.0)
            
            if thread.is_alive():
                if self.debug:
                    print(f"[DEBUG] Search timeout in directory: {directory}")
                return None
            
            return result[0]
                
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error searching directory {directory}: {e}")
            return None

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
        if event.button() == Qt.MouseButton.LeftButton:
            # Get current album metadata
            selected_rows = self.album_table.selectionModel().selectedRows()
            if not selected_rows:
                return
            
            row = selected_rows[0].row()
            item = self.album_table.item(row, 0)
            if not item:
                return
            
            meta = item.data(Qt.ItemDataRole.UserRole)
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

    def _handle_existing_folder_case(self, current_folder, target_path, meta):
        reply = QMessageBox.question(self, "Dossier existant", 
            f"Le dossier '{target_path.name}' existe déjà.\nDéplacer les fichiers sélectionnés ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                # Ne déplacer QUE les fichiers sélectionnés
                selected_files = self._get_selected_files()
                if not selected_files:
                    selected_files = self.files  # Fallback si aucune sélection
                
                for file_info in selected_files:
                    src = pathlib.Path(file_info['path'])
                    dst = target_path / src.name
                    if not dst.exists():
                        shutil.move(str(src), str(dst))
                self._load_files(str(target_path))
                return True
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
        return False
    
    def _perform_standard_folder_rename_simple(self, current_folder, new_folder_name):
        try:
            new_path = current_folder.parent / new_folder_name
            os.rename(str(current_folder), str(new_path))
            self._load_files(str(new_path))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _offer_cleanup_empty_folder(self, folder_path):
        try:
            if not any(folder_path.iterdir()):
                reply = QMessageBox.question(self, "Dossier vide", 
                    f"Supprimer '{folder_path.name}' ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    os.rmdir(str(folder_path))
        except: pass