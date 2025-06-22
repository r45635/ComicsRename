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
    QLabel, QFileDialog, QMessageBox, QComboBox, QTextEdit, QCheckBox,
    QAbstractItemView, QHeaderView, QMenu, QDialog, QFormLayout, QDialogButtonBox, QMenuBar
)
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSettings
from PySide6.QtGui import QPixmap, QDrag, QAction

from utils import scan_comic_files, load_bdgest_credentials, extract_year
from bdgest_scraper_api import get_bdgest_series

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
        import requests
        
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
    def search_series(self, query):
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        return search_comicvine_series(query, api_key=api_key) if api_key else search_comicvine_series(query)

    def search_albums(self, volume_id):
        from comicVine_scraper_api import get_comicvine_volume_issues, get_comicvine_issue_details
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        
        # Get basic volume and issues data
        issues_list = get_comicvine_volume_issues(volume_id, api_key=api_key, debug=True) if api_key else get_comicvine_volume_issues(volume_id, debug=True)
        
        if not issues_list:
            return []
        
        # Enrich each issue with detailed information
        enriched_issues = []
        for issue in issues_list[:20]:  # Limit to first 20 issues to avoid too many API calls
            issue_id = issue.get('id')
            if issue_id:
                print(f"[DEBUG] Fetching details for issue {issue_id}...")
                # Get detailed information for this issue
                details = get_comicvine_issue_details(issue_id, api_key=api_key, debug=False) if api_key else get_comicvine_issue_details(issue_id, debug=False)
                
                # Merge basic issue data with detailed data
                enriched_issue = {
                    'id': issue.get('id'),
                    'issue_number': issue.get('issue_number') or details.get('issue_number', 'N/A'),
                    'name': issue.get('name') or details.get('name', 'Sans titre'),
                    'cover_date': details.get('cover_date', 'Date inconnue'),
                    'store_date': details.get('store_date', ''),
                    'description': details.get('description', ''),
                    'image': details.get('image', {}),
                    'volume': details.get('volume', {}),
                    'character_credits': details.get('character_credits', []),
                    'person_credits': details.get('person_credits', []),
                    'location_credits': details.get('location_credits', []),
                    # Add computed fields for consistency with BDGest
                    'title': issue.get('name') or details.get('name', 'Sans titre'),
                    'cover_url': details.get('image', {}).get('original_url', ''),
                    'album_url': f"https://comicvine.gamespot.com/issue/4000-{issue_id}/",
                }
                
                # Create details section like BDGest
                details_dict = {}
                if details.get('cover_date'):
                    details_dict['Date de publication'] = details.get('cover_date')
                if details.get('store_date'):
                    details_dict['Date en magasin'] = details.get('store_date')
                if details.get('description'):
                    # Clean HTML from description
                    import re
                    clean_desc = re.sub('<[^<]+?>', '', details.get('description', ''))
                    details_dict['Description'] = clean_desc[:500] + ('...' if len(clean_desc) > 500 else '')
                
                # Add character credits
                if details.get('character_credits'):
                    char_names = [char.get('name', '') for char in details.get('character_credits', [])[:5]]
                    if char_names:
                        details_dict['Personnages'] = ', '.join(char_names)
                
                # Add person credits (writers, artists, etc.)
                if details.get('person_credits'):
                    person_names = [f"{person.get('name', '')} ({person.get('role', 'N/A')})" for person in details.get('person_credits', [])[:5]]
                    if person_names:
                        details_dict['Équipe créative'] = ', '.join(person_names)
                
                enriched_issue['details'] = details_dict
                enriched_issues.append(enriched_issue)
            else:
                # Fallback for issues without ID
                enriched_issues.append(issue)
        
        print(f"[DEBUG] Enriched {len(enriched_issues)} issues with detailed information")
        return enriched_issues

PROVIDERS = {
    'ComicVine': ComicVineProvider(),
    'BDGest': BDGestProvider(),
}

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
            print(f"[DEBUG][DnD] Payload: {payload}")
            # Try to parse the payload as "Series - Num - Title (Year)"
            # Use similar cleaning as in _rename_selected
            parts = payload.split(' - ', 2)
            if len(parts) < 3:
                print("[DEBUG][DnD] Split failed, parts:", parts)
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
                'Rename',
                f"Rename file to:\n{new_name}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    if not os.path.exists(f['path']):
                        QMessageBox.critical(self, "Erreur", f"Le fichier source n'existe pas:\n{f['path']}")
                        return
                    if new_path.exists():
                        QMessageBox.critical(self, "Erreur", f"Un fichier nommé '{new_name}' existe déjà dans ce dossier.")
                        return
                    os.rename(f['path'], new_path)
                    self.main._load_files(f['folder'])
                except Exception as e:
                    QMessageBox.critical(self, "Rename Error", str(e))
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
                QMessageBox.warning(self, "Format non supporté", "Seuls les fichiers PDF, EPUB, CBZ ou CBR sont acceptés.")
                return
            op = "déplacer" if (event.dropAction() == Qt.MoveAction or (event.keyboardModifiers() & Qt.ShiftModifier)) else "copier"
            msg = f"Voulez-vous {op} les fichiers suivants dans le dossier actif ?\n\n" + "\n".join(os.path.basename(f) for f in files_to_add)
            if QMessageBox.question(self, "Ajouter des fichiers", msg, QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                return
            dest_folder = self.main.files[0]['folder'] if self.main.files else self.main.settings.value('last_folder', '')
            if not dest_folder:
                QMessageBox.critical(self, "Erreur", "Aucun dossier actif pour l'import.")
                return
            import shutil
            for src in files_to_add:
                # Vérifie que le fichier existe
                if not os.path.exists(src):
                    QMessageBox.critical(self, "Erreur", f"Le fichier source n'existe pas :\n{src}")
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
                            "Erreur",
                            f"Erreur lors de l'ajout de {base_name} :\n{e}\n\nSource: {src}\nDestination: {dest}"
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
            'Rename',
            f"Rename file to:\n{new_path.name}?",
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
        open_action = menu.addAction("Open File")
        reveal_action = menu.addAction("Reveal in Finder")
        menu.addSeparator()
        refresh_action = menu.addAction("Rafraîchir les fichiers du dossier")
        action = menu.exec(self.viewport().mapToGlobal(pos))
        f = self.main.files[row]
        file_path = str(f['path'])
        if action == open_action:
            try:
                subprocess.Popen(['open', file_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
        elif action == reveal_action:
            try:
                subprocess.Popen(['open', '-R', file_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not reveal file:\n{e}")
        elif action == refresh_action:
            folder = self.main.settings.value('last_folder', '')
            if folder and pathlib.Path(folder).exists():
                self.main._load_files(folder)

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
        print(f"[DEBUG][DnD] Drag value: {it.text()}")
        mime = QMimeData()
        mime.setData('application/x-comic-meta', QByteArray(it.text().encode()))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

    def _show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu(self)
        # Aucune action spéciale pour le moment - peut être étendu plus tard
        # Exemple : menu.addAction("Voir détails de l'album")
        # Pour l'instant, le menu contextuel reste vide mais peut être développé
        # action = menu.exec(self.viewport().mapToGlobal(pos))

# ---------- Settings Dialog ----------
class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.layout = QFormLayout(self)

        self.settings = settings or QSettings("ComicsRename", "App")

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["BDGest", "ComicVine"])
        default_provider = self.settings.value("default_provider", "BDGest")
        idx = self.provider_combo.findText(default_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.layout.addRow("Provider par défaut :", self.provider_combo)

        self.debug_cb = QCheckBox()
        self.debug_cb.setChecked(self.settings.value('debug', 'false') == 'true')
        self.layout.addRow("Debug mode", self.debug_cb)

        self.verbose_cb = QCheckBox()
        self.verbose_cb.setChecked(self.settings.value('verbose', 'false') == 'true')
        self.layout.addRow("Verbose mode", self.verbose_cb)

        self.bdgest_user = QLineEdit(self.settings.value('bdgest_user', ''))
        self.layout.addRow("BDGest Username", self.bdgest_user)
        self.bdgest_pass = QLineEdit(self.settings.value('bdgest_pass', ''))
        self.bdgest_pass.setEchoMode(QLineEdit.Password)
        self.layout.addRow("BDGest Password", self.bdgest_pass)

        self.comicvine_api = QLineEdit(self.settings.value('comicvine_api', ''))
        self.layout.addRow("ComicVine API Key", self.comicvine_api)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

    def accept(self):
        self.settings.setValue("default_provider", self.provider_combo.currentText())
        self.settings.setValue("debug", 'true' if self.debug_cb.isChecked() else 'false')
        self.settings.setValue("verbose", 'true' if self.verbose_cb.isChecked() else 'false')
        self.settings.setValue("bdgest_user", self.bdgest_user.text())
        self.settings.setValue("bdgest_pass", self.bdgest_pass.text())
        self.settings.setValue("comicvine_api", self.comicvine_api.text())
        super().accept()

# ---------- Main GUI ----------
class ComicRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comic Renamer - Multi-Source")
        self.resize(1400, 800)
        self.settings = QSettings("ComicsRename", "App")
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
        if self._source == 'BDGest':
            self.series_name_cb.setVisible(True)
        else:
            self.series_name_cb.setVisible(False)

        # Recharge automatiquement le dernier dossier utilisé
        last_folder = self.settings.value("last_folder", "")
        if last_folder:
            self._load_files(last_folder)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        ctrl = QHBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems(['ComicVine', 'BDGest'])
        self.search_bar = DroppableLineEdit()
        self.search_btn = QPushButton('Search')
        self.dir_btn = QPushButton('Change Folder')
        self.recursive_cb = QCheckBox('Recursive')
        self.series_name_cb = QCheckBox('SeriesName')  # New checkbox for BDGest series search
        self.series_name_cb.setToolTip("Rechercher uniquement dans les noms de séries (BDGest uniquement)")
        self.series_name_cb.setVisible(False)  # Hidden by default, shown only for BDGest
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedWidth(30)
        self.settings_btn.setToolTip("Application Settings")
        self.rename_btn = QPushButton('Rename Selected')
        for w in (self.source_combo, self.search_bar, self.search_btn, self.dir_btn, self.recursive_cb, self.series_name_cb, self.settings_btn):
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
        self.folder_rename_btn.setToolTip("Renommer le dossier avec le nom de la série sélectionnée")
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

        det_widget = QWidget()
        det_layout = QHBoxLayout(det_widget)
        self.detail_text = QTextEdit(readOnly=True)
        self.detail_image = QLabel()
        # Configure image label to be responsive and centered
        self.detail_image.setScaledContents(False)  # Don't force scaling to fill
        self.detail_image.setAlignment(Qt.AlignCenter)  # Center the image
        self.detail_image.setMinimumSize(50, 50)  # Small minimum size
        self.detail_image.setMaximumSize(300, 400)  # Reasonable maximum
        self.detail_image.setSizePolicy(self.detail_image.sizePolicy().horizontalPolicy(), 
                                       self.detail_image.sizePolicy().verticalPolicy())
        det_layout.addWidget(self.detail_text,2)
        det_layout.addWidget(self.detail_image,1)
        splitter_right.addWidget(det_widget)

        splitter_main.addWidget(splitter_right)
        layout.addWidget(splitter_main)
        layout.addWidget(self.rename_btn)

        # Store splitter reference for image resize handling
        self.splitter_right = splitter_right

        self.source_combo.currentTextChanged.connect(self._change_source)
        self.dir_btn.clicked.connect(self._choose_folder)
        self.search_btn.clicked.connect(self._search)
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
        rec = self.settings.value('recursive','false') == 'true'
        self.recursive_cb.setChecked(rec)
        fc = self.settings.value('file_cols')
        if fc:
            for i,w in enumerate(map(int,fc.split(','))):
                self.file_table.setColumnWidth(i,w)
        ac = self.settings.value('album_cols')
        if ac:
            self.album_table.setColumnWidth(0,int(ac))
        # Restore debug/verbose for next dialog open
        self.debug = self.settings.value('debug', 'false') == 'true'
        self.verbose = self.settings.value('verbose', 'false') == 'true'
        if folder and pathlib.Path(folder).exists():
            self._load_files(folder)

    def closeEvent(self,ev):
        self.settings.setValue('last_folder', self.settings.value('last_folder'))
        self.settings.setValue('recursive','true' if self.recursive_cb.isChecked() else 'false')
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
        if src == 'BDGest':
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
        elif msg.clickedButton() == btn_last and current_folder:
            start_dir = current_folder
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
        self._populating = True
        self.file_table.blockSignals(True)
        # Filter out files whose name starts with '.'
        all_files = scan_comic_files(folder, self.recursive_cb.isChecked())
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

    def _search(self):
        q = self.search_bar.text().strip()
        if not q:
            return
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
        
        # Only call search_series for ComicVine or BDGest in non-SeriesName mode
        if self._source == 'ComicVine' or (self._source == 'BDGest' and not self.series_name_cb.isChecked()):
            series_list = provider.search_series(q, debug=debug, verbose=verbose) \
                if hasattr(provider, 'search_series') and provider.search_series.__code__.co_argcount > 2 \
                else provider.search_series(q)
        else:
            # For BDGest in SeriesName mode, we'll call search_series_only later
            series_list = []

        self.issues_by_series.clear()
        self._bdgest_album_results = []

        if self._source == 'ComicVine':
            from comicVine_scraper_api import search_comicvine_series, search_comicvine_issues
            volumes = search_comicvine_series(q)
            if volumes:
                print(f"[DEBUG][UI] {len(volumes)} volumes found for '{q}'")
                for series in volumes:
                    series_name = series.get('name', 'Unknown')
                    volume_id = str(series.get('id', ''))
                    issues = provider.search_albums(volume_id)
                    for issue in issues:
                        issue['volume'] = {'name': series_name}
                        self.issues_by_series[series_name].append(issue)
                if not self.issues_by_series:
                    QMessageBox.warning(self, 'No Results', 'No albums found for this search.')
                    return
                for s in sorted(self.issues_by_series):
                    self.series_combo.addItem(f"{s} ({len(self.issues_by_series[s])})")
            else:
                print(f"[DEBUG][UI] No volumes found for '{q}', fallback to issues search")
                issues = search_comicvine_issues(q)
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
        else:  # BDGest
            # Check if SeriesName checkbox is checked
            if self.series_name_cb.isChecked():
                # Use series-only search
                series_results = provider.search_series_only(q, debug=debug, verbose=verbose) \
                    if hasattr(provider, 'search_series_only') \
                    else []
                
                self._bdgest_series_results = series_results
                self._bdgest_album_results = []  # Clear album results when searching series
                
                # Populate series dropdown with series results
                for series in series_results:
                    series_name = series.get('serie_name', 'Unknown Series')
                    if series_name and series_name != 'Unknown Series':
                        self.series_combo.addItem(series_name)
                        idx = self.series_combo.count() - 1
                        # Store the full series data for later use
                        self.series_combo.setItemData(idx, series, Qt.UserRole)
                
                # Inform user if no series results
                if not series_results:
                    QMessageBox.information(self, "Aucun résultat", "Aucune série trouvée pour cette recherche sur BDGest.")
                else:
                    # Clear album table since we're in series mode
                    self.album_table.clearContents()
                    self.album_table.setRowCount(0)
                    
                    # Automatically populate albums for the first (default selected) series
                    if self.series_combo.count() > 0:
                        # The first series is automatically selected by default
                        # Trigger album population for the first series
                        first_series_name = self.series_combo.itemText(0)
                        self._populate_albums(first_series_name)
            else:
                # Use default album search
                albums = []
                for album in series_list:
                    s = album.get('serie_name', '')
                    if s:
                        albums.append(album)
                self._bdgest_album_results = albums
                self._bdgest_series_results = []  # Clear series results when searching albums
                
                series_seen = set()
                for album in albums:
                    s = album.get('serie_name', '')
                    serie_id = album.get('series_id', '')
                    if s and s not in series_seen:
                        self.series_combo.addItem(s)
                        idx = self.series_combo.count() - 1
                        self.series_combo.setItemData(idx, serie_id, Qt.UserRole)
                        series_seen.add(s)
                # Inform user if no BDGest results
                if not albums:
                    QMessageBox.information(self, "Aucun résultat", "Aucun album trouvé pour cette recherche sur BDGest.")

    def _enable_folder_rename_btn(self, *args):
        self.folder_rename_btn.setEnabled(True)

    def _on_album_selection_changed(self, selected, deselected):
        # Enable if any row is selected, else disable
        selected_rows = self.album_table.selectionModel().selectedRows()
        self.folder_rename_btn.setEnabled(bool(selected_rows))

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
            series = txt.rsplit(' (', 1)[0]
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
                                debug = self.debug_cb.isChecked() if hasattr(self, 'debug_cb') else False
                                verbose = self.verbose_cb.isChecked() if hasattr(self, 'verbose_cb') else False
                                albums = provider.search_albums_by_series_id(series_id, series_name, debug=debug, verbose=verbose)
                                
                                if albums:
                                    # Populate album table with series albums
                                    self.album_table.setRowCount(len(albums))
                                    for r, alb in enumerate(albums):
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
                                html += f"</ul><br><i>Erreur lors de la récupération des albums: {e}</i>"
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
        itm = self.album_table.item(r, 0)
        meta = itm.data(Qt.UserRole) if itm else None
        if not meta:
            return
        html = "<b>Détails complets :</b><br><ul>"
        # Affiche tous les champs principaux sauf 'details'
        for k, v in meta.items():
            if k != "details":
                html += f"<li><b>{k}</b> : {v}</li>"
        # Ajoute les détails à la fin, bien mis en forme
        details = meta.get("details")
        if isinstance(details, dict):
            html += "<li><b>Détails :</b><ul>"
            for label, value in details.items():
                html += f"<li><b>{label}</b> : {value}</li>"
            html += "</ul></li>"
        html += "</ul>"
        self.detail_text.setHtml(html)
        img_url = meta.get('cover_url') or meta.get('image', {}).get('original_url')
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
            print(f"[DEBUG] clean() input: {repr(s)}")
            cleaned = re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
            print(f"[DEBUG] clean() output: {repr(cleaned)}")
            return cleaned
        print(f"[DEBUG] series before clean: {repr(series)}")
        print(f"[DEBUG] num before clean: {repr(num)}")
        print(f"[DEBUG] title before clean: {repr(title)}")
        base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
        if y:
            base += f" ({y})"
        print(f"[DEBUG] base filename after clean: {repr(base)}")
        # Ensure extension does not have a leading dot
        ext = f['ext'].lstrip('.')
        new_name = f"{base}.{ext}"
        new_path = pathlib.Path(f['folder']) / new_name
        msg = f"Rename file to:\n{new_name}?"
        if new_path.exists():
            QMessageBox.critical(self, "Erreur", f"Un fichier nommé '{new_name}' existe déjà dans ce dossier.")
            return
        if QMessageBox.question(self, 'Rename', msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                if not os.path.exists(str(f['path'])):
                    QMessageBox.critical(self, "Erreur", f"Le fichier source n'existe pas:\n{f['path']}")
                    return
                os.rename(str(f['path']), str(new_path))
                self._load_files(f['folder'])
            except Exception as e:
                QMessageBox.critical(self, 'Rename Error', str(e))

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

    def _rename_folder_to_serie(self):
        # Get current folder path
        if not self.files:
            QMessageBox.warning(self, "Erreur", "Aucun fichier dans le dossier.")
            return
        current_folder = pathlib.Path(self.files[0]['folder'])
        # Get selected album
        ar = self.album_table.currentRow()
        if ar < 0:
            QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un album dans la liste.")
            return
        itm = self.album_table.item(ar, 0)
        meta = itm.data(Qt.UserRole) if itm else None
        if not meta:
            QMessageBox.critical(self, "Erreur", "Métadonnées de l'album manquantes.")
            return
        # Extract serie_name
        serie_name = meta.get('serie_name') or (meta.get('volume') or {}).get('name', '')
        # Extract style from details['Détails'] if present
        style = ''
        details = meta.get('details', {})
        # Some BDGest scrapers put all details in a subkey 'Détails'
        if isinstance(details, dict):
            # Try both 'Style' and 'Détails'->'Style'
            if 'Style' in details:
                style = details['Style']
            elif 'Détails' in details and isinstance(details['Détails'], dict):
                style = details['Détails'].get('Style', '')
        if not style:
            style = meta.get('style', '')
        if not serie_name:
            QMessageBox.warning(self, "Erreur", "Impossible de déterminer le nom de la série.")
            return
        # Clean up names
        clean = lambda s: ''.join(c for c in str(s) if c.isalnum() or c in "-_(),' ").strip()
        style_clean = clean(style)
        serie_clean = clean(serie_name)
        new_folder_name = f"[{style_clean}] {serie_clean}" if style_clean else serie_clean
        parent_dir = current_folder.parent

        # DEBUG: Print current and new folder names and paths
        print(f"[DEBUG] current_folder: {current_folder}")
        print(f"[DEBUG] current_folder.name: {current_folder.name}")
        print(f"[DEBUG] new_folder_name: {new_folder_name}")
        print(f"[DEBUG] new_folder_path: {parent_dir / new_folder_name}")
        print(f"[DEBUG] details: {details}")

        if current_folder.name == new_folder_name:
            print("[DEBUG] Folder name is already the target name, aborting rename.")
            QMessageBox.information(self, "Info", "Le dossier porte déjà ce nom.")
            return

        if style_clean and current_folder.name == serie_clean and new_folder_name != current_folder.name:
            print("[DEBUG] Folder is only serie name, will rename to [Style] SerieName.")

        new_folder_path = parent_dir / new_folder_name
        if new_folder_path.exists():
            print("[DEBUG] Target folder already exists, aborting rename.")
            QMessageBox.critical(self, "Erreur", f"Un dossier nommé '{new_folder_name}' existe déjà dans ce répertoire.")
            return

        if QMessageBox.question(
            self,
            "Renommer le dossier",
            f"Renommer le dossier en :\n{new_folder_name} ?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                print(f"[DEBUG] Renaming {current_folder} -> {new_folder_path}")
                os.rename(str(current_folder), str(new_folder_path))
                self.settings.setValue('last_folder', str(new_folder_path))
                self._load_files(str(new_folder_path))
                QMessageBox.information(self, "Succès", f"Dossier renommé en :\n{new_folder_name}")
            except Exception as e:
                print(f"[DEBUG] Exception during rename: {e}")
                QMessageBox.critical(self, "Erreur", f"Erreur lors du renommage du dossier :\n{e}")

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

class DraggableLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)

    def mouseMoveEvent(self, event):
        if not self.text():
            return
        mime = QMimeData()
        mime.setText(self.text())
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

class DroppableLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        raw_text = event.mimeData().text()
        # Remove all text within () or []
        text = re.sub(r'\(.*?\)|\[.*?\]', '', raw_text)
        # Keep unicode letters, numbers, spaces, apostrophes, hyphens, and underscores
        # Use regex with re.UNICODE and add explicit ' to the allowed set
        text = re.sub(r"[^\w\s'\-_]", '', text, flags=re.UNICODE)
        # Collapse multiple spaces and strip
        text = re.sub(r'\s+', ' ', text).strip()
        self.setText(text)
        event.acceptProposedAction()

class EditableFolderLineEdit(QLineEdit):
    def __init__(self, main_window=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.main_window = main_window
        self._original_folder_path = None
        self._drag_start_position = None

    def mousePressEvent(self, event):
        """Store the position where mouse was pressed for drag detection"""
        if event.button() == Qt.LeftButton:
            self._drag_start_position = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle dragging functionality only when mouse is pressed and moved sufficiently"""
        # Only drag if we have text and mouse button is pressed
        if (not self.text() or 
            not (event.buttons() & Qt.LeftButton) or 
            self._drag_start_position is None):
            return
        
        # Calculate distance moved
        distance = (event.position() - self._drag_start_position).manhattanLength()
        
        # Only start drag if moved far enough (avoid accidental drags)
        if distance < QApplication.startDragDistance():
            return
        
        # Start drag operation
        mime = QMimeData()
        mime.setText(self.text())
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to enable folder renaming"""
        if not self.main_window or not self.main_window.files:
            return
        
        # Get current folder path
        current_folder = pathlib.Path(self.main_window.files[0]['folder'])
        self._original_folder_path = current_folder
        
        # Switch to editable mode
        self.setReadOnly(False)
        self.setStyleSheet("background-color: #ffffcc; border: 2px solid #0078d4;")  # Light yellow background
        self.selectAll()
        self.setFocus()
        
        # Connect to handle when editing is finished
        self.editingFinished.connect(self._on_editing_finished)
        self.returnPressed.connect(self._on_return_pressed)

    def _on_return_pressed(self):
        """Handle Enter key press"""
        self._on_editing_finished()

    def _on_editing_finished(self):
        """Handle when editing is finished (Enter pressed or focus lost)"""
        # Disconnect signals to avoid multiple calls
        self.editingFinished.disconnect()
        if hasattr(self, '_return_connection'):
            self.returnPressed.disconnect()
        
        new_name = self.text().strip()
        if not new_name:
            self._cancel_editing()
            return
        
        # Check if name changed
        if new_name == self._original_folder_path.name:
            self._cancel_editing()
            return
        
        # Validate new name (remove invalid characters)
        import string
        valid_chars = string.ascii_letters + string.digits + ' -_()[]'
        cleaned_name = ''.join(c for c in new_name if c in valid_chars or ord(c) > 127)  # Allow unicode
        cleaned_name = cleaned_name.strip()
        
        if not cleaned_name:
            QMessageBox.warning(self.main_window, "Nom invalide", "Le nom du dossier ne peut pas être vide.")
            self._cancel_editing()
            return
        
        # Check if folder with new name already exists
        new_folder_path = self._original_folder_path.parent / cleaned_name
        if new_folder_path.exists():
            QMessageBox.critical(self.main_window, "Erreur", f"Un dossier nommé '{cleaned_name}' existe déjà dans ce répertoire.")
            self._cancel_editing()
            return
        
        # Confirm rename
        reply = QMessageBox.question(
            self.main_window,
            "Renommer le dossier",
            f"Renommer le dossier de :\n'{self._original_folder_path.name}'\nà :\n'{cleaned_name}' ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Perform the rename
                os.rename(str(self._original_folder_path), str(new_folder_path))
                
                # Update the settings and reload files
                self.main_window.settings.setValue('last_folder', str(new_folder_path))
                self.main_window._load_files(str(new_folder_path))
                
                # Success message
                QMessageBox.information(self.main_window, "Succès", f"Dossier renommé en '{cleaned_name}'")
                
            except Exception as e:
                QMessageBox.critical(self.main_window, "Erreur", f"Erreur lors du renommage :\n{e}")
                self._cancel_editing()
                return
        
        # Reset to read-only mode
        self._reset_to_readonly()

    def _cancel_editing(self):
        """Cancel editing and restore original name"""
        if self._original_folder_path:
            self.setText(self._original_folder_path.name)
        self._reset_to_readonly()

    def _reset_to_readonly(self):
        """Reset the widget to read-only mode"""
        self.setReadOnly(True)
        self.setStyleSheet("")  # Clear custom styling
        self.clearFocus()
        self._original_folder_path = None

    def keyPressEvent(self, event):
        """Handle key presses during editing"""
        if event.key() == Qt.Key_Escape:
            # Cancel editing on Escape
            self._cancel_editing()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ComicRenamer()
    win.show()
    sys.exit(app.exec())