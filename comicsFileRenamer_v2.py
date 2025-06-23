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

from utils import scan_comic_files, load_bdgest_credentials, extract_year, open_file_cross_platform, reveal_file_cross_platform, get_system_info
from bdgest_scraper_api import get_bdgest_series

# ---------- Providers (API abstraction layer) ----------
class MetadataProvider:
    def search_series(self, query):
        raise NotImplementedError

    def search_albums(self, series_id_or_name):
        raise NotImplementedError

class BDGestProvider(MetadataProvider):
    def search_series(self, query, debug=False, verbose=False):
        from bdgest_scraper_api import get_bdgest_albums
        # Use QSettings to get credentials
        settings = QSettings("ComicsRename", "App")
        user = settings.value('bdgest_user', '')
        pwd = settings.value('bdgest_pass', '')
        return get_bdgest_albums(query, user, pwd, debug=debug, verbose=verbose)

    def search_albums(self, serie_name):
        from bdgest_scraper_api import get_bdgest_albums
        settings = QSettings("ComicsRename", "App")
        user = settings.value('bdgest_user', '')
        pwd = settings.value('bdgest_pass', '')
        return get_bdgest_albums(serie_name, user, pwd)

class ComicVineProvider(MetadataProvider):
    def search_series(self, query):
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        return search_comicvine_series(query, api_key=api_key) if api_key else search_comicvine_series(query)

    def search_albums(self, volume_id):
        from comicVine_scraper_api import get_comicvine_volume_issues
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        return get_comicvine_volume_issues(volume_id, api_key=api_key) if api_key else get_comicvine_volume_issues(volume_id)

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
        
        # Get system info for appropriate menu labels
        system_info = get_system_info()
        
        # Adaptive menu labels based on OS
        if system_info['is_windows']:
            open_label = "Open File"
            reveal_label = "Show in Explorer"  # Windows-specific
        elif system_info['is_macos']:
            open_label = "Open File"
            reveal_label = "Reveal in Finder"  # macOS-specific
        else:  # Linux
            open_label = "Open File"
            reveal_label = "Show in File Manager"  # Linux-generic
            
        open_action = menu.addAction(open_label)
        reveal_action = menu.addAction(reveal_label)
        
        action = menu.exec(self.viewport().mapToGlobal(pos))
        f = self.main.files[row]
        file_path = str(f['path'])
        
        if action == open_action:
            result = open_file_cross_platform(file_path)
            if result is not True:
                success, error_msg = result
                if not success:
                    QMessageBox.critical(self, "Error", f"Could not open file:\n{error_msg}")
        elif action == reveal_action:
            result = reveal_file_cross_platform(file_path)
            if result is not True:
                success, error_msg = result
                if not success:
                    QMessageBox.critical(self, "Error", f"Could not reveal file:\n{error_msg}")

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
        refresh_action = menu.addAction("Rafraîchir les fichiers du dossier")
        action = menu.exec(self.viewport().mapToGlobal(pos))
        if action == refresh_action:
            folder = self.main.settings.value('last_folder', '')
            if folder and pathlib.Path(folder).exists():
                self.main._load_files(folder)

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
        self._build_ui()
        self.series_cover_url = ''

        # Synchronize source_combo with user preference
        default_provider = self.settings.value("default_provider", "BDGest")
        idx = self.source_combo.findText(default_provider)
        if idx >= 0:
            self.source_combo.setCurrentIndex(idx)
        self._source = self.source_combo.currentText()

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
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedWidth(30)
        self.settings_btn.setToolTip("Application Settings")
        self.rename_btn = QPushButton('Rename Selected')
        for w in (self.source_combo, self.search_bar, self.search_btn, self.dir_btn, self.recursive_cb, self.settings_btn):
            ctrl.addWidget(w)
        layout.addLayout(ctrl)

        splitter_main = QSplitter(Qt.Horizontal)

        # --- Folder display ---
        file_panel = QWidget()
        file_panel_layout = QVBoxLayout(file_panel)
        file_panel_layout.setContentsMargins(0, 0, 0, 0)
        folder_display_layout = QHBoxLayout()
        self.folder_display = DraggableLineEdit()
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
        det_layout.addWidget(self.detail_text,2)
        det_layout.addWidget(self.detail_image,1)
        splitter_right.addWidget(det_widget)

        splitter_main.addWidget(splitter_right)
        layout.addWidget(splitter_main)
        layout.addWidget(self.rename_btn)

        self.source_combo.currentTextChanged.connect(self._change_source)
        self.dir_btn.clicked.connect(self._choose_folder)
        self.search_btn.clicked.connect(self._search)
        self.search_bar.returnPressed.connect(self._search)
        self.series_combo.currentTextChanged.connect(self._populate_albums)
        self.album_table.cellClicked.connect(self._show_details)
        self.album_table.cellClicked.connect(self._enable_folder_rename_btn)
        self.album_table.selectionModel().selectionChanged.connect(self._on_album_selection_changed)
        self.rename_btn.clicked.connect(self._rename_selected)
        self.settings_btn.clicked.connect(self._open_settings)

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

    def _change_source(self,src):
        self._source=src
        self.series_combo.clear()
        self.album_table.clearContents();self.album_table.setRowCount(0); self.series_cover_url = ''
        self.detail_text.clear();self.detail_image.clear()
        if self.folder_rename_btn is not None:
            self.folder_rename_btn.setEnabled(False)

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

        provider = PROVIDERS[self._source]
        # Pass debug/verbose to provider if supported
        debug = self.settings.value('debug', 'false') == 'true'
        verbose = self.settings.value('verbose', 'false') == 'true'
        series_list = provider.search_series(q, debug=debug, verbose=verbose) \
            if hasattr(provider, 'search_series') and provider.search_series.__code__.co_argcount > 2 \
            else provider.search_series(q)

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
        else:
            albums = []
            for album in series_list:
                s = album.get('serie_name', '')
                if s:
                    albums.append(album)
            self._bdgest_album_results = albums
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
        else:
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
                self.detail_image.setPixmap(pm.scaledToWidth(300, Qt.SmoothTransformation))
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
        num_fmt = format_num(num)
        # Only keep allowed characters: unicode letters, numbers, spaces, apostrophes, hyphens, underscores, parentheses
        def clean(s):
            print(f"[DEBUG] clean() input: {repr(s)}")
            cleaned = re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
            print(f"[DEBUG] clean() output: {repr(cleaned)}")
            return cleaned
        print(f"[DEBUG] series before clean: {repr(series)}")
        print(f"[DEBUG] num before clean: {repr(num)}")
        print(f"[DEBUG] title before clean: {repr(title)}")
        base = f"{clean(series)} - {num_fmt} - {clean(title)}"
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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ComicRenamer()
    win.show()
    sys.exit(app.exec())