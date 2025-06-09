import sys
import os
import pathlib
import requests
from collections import defaultdict
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QSplitter, QPushButton, QLineEdit,
    QLabel, QFileDialog, QMessageBox, QComboBox, QTextEdit, QCheckBox,
    QAbstractItemView, QHeaderView
)
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSettings
from PySide6.QtGui import QPixmap, QDrag

# ---------- Constants ----------
COMICVINE_API_KEY = "2a483cf8399177d8689c6c58d29699ef01978ae5"
COMICVINE_SEARCH_URL = "https://comicvine.gamespot.com/api/search/"

# ---------- Utility Functions ----------
def scan_comic_files(folder, recursive):
    supported_ext = ['.pdf', '.epub', '.cbz', '.cbr']
    files = []
    iterator = pathlib.Path(folder).rglob("*") if recursive else pathlib.Path(folder).glob("*")
    for path in sorted(iterator):
        if path.suffix.lower() in supported_ext:
            size = round(path.stat().st_size / (1024 * 1024), 2)
            files.append({
                'path': path,
                'name': path.stem,
                'ext': path.suffix.lower()[1:],
                'size': f"{size} MB",
                'folder': str(path.parent)
            })
    return files


def search_comicvine_issues(query):
    params = {
        'api_key': COMICVINE_API_KEY,
        'format': 'json',
        'query': query,
        'resources': 'issue',
        'field_list': 'id,name,issue_number,cover_date,volume,image,api_detail_url',
        'limit': 100
    }
    headers = {'User-Agent': 'ComicRenamerApp/1.0'}
    try:
        resp = requests.get(COMICVINE_SEARCH_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('results', []) if data.get('status_code') == 1 else []
    except Exception as e:
        print('API call failed:', e)
        return []

# ---------- Main GUI ----------
class ComicRenamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Comic Renamer - ComicVine Edition')
        self.resize(1400, 800)
        self.settings = QSettings('ComicRenamer', 'App')
        self.files = []
        self.issues_by_series = defaultdict(list)
        self._populating = False
        self._build_ui()
        self._restore_session()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        # Controls
        ctrl = QHBoxLayout()
        self.search_bar = QLineEdit(); self.search_btn = QPushButton('Search')
        self.dir_btn = QPushButton('Change Folder'); self.recursive_cb = QCheckBox('Recursive')
        self.rename_btn = QPushButton('Rename Selected')
        for w in (self.search_bar, self.search_btn, self.dir_btn, self.recursive_cb):
            ctrl.addWidget(w)
        main_layout.addLayout(ctrl)

        # Splitter layout
        main_split = QSplitter(Qt.Horizontal)
        # Left table
        self.file_table = FileTable(self)
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(['Name', 'Ext', 'Size', 'Folder'])
        self.file_table.setSortingEnabled(True)
        main_split.addWidget(self.file_table)
        # Right panel
        right_split = QSplitter(Qt.Vertical)
        # Album selector + table
        alb_widget = QWidget(); alb_layout = QVBoxLayout(alb_widget)
        self.series_combo = QComboBox()
        self.album_table = AlbumTable(self)
        self.album_table.setColumnCount(1)
        self.album_table.setHorizontalHeaderLabels(['Albums'])
        self.album_table.setSortingEnabled(True)
        alb_layout.addWidget(self.series_combo)
        alb_layout.addWidget(self.album_table)
        right_split.addWidget(alb_widget)
        # Details
        det_widget = QWidget(); det_layout = QHBoxLayout(det_widget)
        self.detail_text = QTextEdit(readOnly=True); self.detail_image = QLabel()
        det_layout.addWidget(self.detail_text, 2); det_layout.addWidget(self.detail_image, 1)
        right_split.addWidget(det_widget)

        main_split.addWidget(right_split)
        main_layout.addWidget(main_split)
        main_layout.addWidget(self.rename_btn)

        # Connections
        self.dir_btn.clicked.connect(self._choose_folder)
        self.search_btn.clicked.connect(self._search)
        self.search_bar.returnPressed.connect(self._search)
        self.series_combo.currentTextChanged.connect(self._populate_albums)
        self.album_table.cellClicked.connect(self._show_details)
        self.rename_btn.clicked.connect(self._rename_selected)

    def _restore_session(self):
        folder = self.settings.value('last_folder', '')
        rec = self.settings.value('recursive', 'false') == 'true'
        self.recursive_cb.setChecked(rec)
        cols = self.settings.value('file_cols')
        if cols:
            for i, w in enumerate(map(int, cols.split(','))):
                self.file_table.setColumnWidth(i, w)
        alb_col = self.settings.value('album_cols')
        if alb_col:
            self.album_table.setColumnWidth(0, int(alb_col))
        if folder and pathlib.Path(folder).exists():
            self._load_files(folder)

    def closeEvent(self, event):
        # Save session
        last = self.settings.value('last_folder')
        self.settings.setValue('last_folder', last)
        self.settings.setValue('recursive', 'true' if self.recursive_cb.isChecked() else 'false')
        file_cols = [self.file_table.columnWidth(i) for i in range(self.file_table.columnCount())]
        self.settings.setValue('file_cols', ','.join(map(str, file_cols)))
        self.settings.setValue('album_cols', str(self.album_table.columnWidth(0)))
        super().closeEvent(event)

    def _choose_folder(self):
        d = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if d:
            self.settings.setValue('last_folder', d)
            self._load_files(d)

    def _load_files(self, folder):
        self._populating = True
        self.file_table.blockSignals(True)
        self.files = scan_comic_files(folder, self.recursive_cb.isChecked())
        self.file_table.setRowCount(len(self.files))
        for r, f in enumerate(self.files):
            for c, val in enumerate((f['name'], f['ext'], f['size'], f['folder'])):
                self.file_table.setItem(r, c, QTableWidgetItem(val))
        self.file_table.blockSignals(False)
        self._populating = False

    def _search(self):
        q = self.search_bar.text().strip()
        if not q:
            return
        self.issues_by_series.clear(); self.series_combo.clear()
        self.album_table.clearContents(); self.album_table.setRowCount(0)
        self.detail_text.clear(); self.detail_image.clear()
        for it in search_comicvine_issues(q):
            s = (it.get('volume') or {}).get('name', 'Unknown')
            self.issues_by_series[s].append(it)
        for s in sorted(self.issues_by_series):
            self.series_combo.addItem(f"{s} ({len(self.issues_by_series[s])})")

    def _populate_albums(self, text):
        if not text:
            return
        series = text.rsplit(' (', 1)[0]
        issues = sorted(self.issues_by_series[series], key=lambda x: ((x.get('cover_date') or ''), x.get('issue_number') or ''))
        self.album_table.setRowCount(len(issues))
        for r, it in enumerate(issues):
            title = it.get('name') or 'Untitled'
            num = it.get('issue_number') or '?'           
            yr = (it.get('cover_date') or '')[:4]
            val = f"{series} - {num} - {title} ({yr})"
            self.album_table.setItem(r, 0, QTableWidgetItem(val))

    def _show_details(self, r, c):
        series = self.series_combo.currentText().rsplit(' (', 1)[0]
        it = self.issues_by_series[series][r]
        title = it.get('name') or 'Untitled'
        num = it.get('issue_number') or '?'
        yr = (it.get('cover_date') or '')[:4]
        self.detail_text.setHtml(f"<b>{title}</b><br/>Issue #{num} ({yr})")
        img_url = (it.get('image') or {}).get('super_url', '')
        if img_url:
            data = requests.get(img_url, timeout=10).content
            pix = QPixmap(); pix.loadFromData(data)
            self.detail_image.setPixmap(pix.scaledToWidth(300, Qt.SmoothTransformation))

    def _rename_selected(self):
        file_row = self.file_table.currentRow()
        album_row = self.album_table.currentRow()
        if file_row < 0 or album_row < 0:
            QMessageBox.warning(self, 'Select', 'Please select one file and one album')
            return
        f = self.files[file_row]
        item = self.album_table.item(album_row, 0)
        if not item:
            return
        text = item.text()
        parts = text.rsplit(' - ', 2)
        if len(parts) != 3:
            QMessageBox.critical(self, 'Error', 'Unexpected album format')
            return
        series, issue_num, title_year = parts
        if title_year.endswith(')') and ' (' in title_year:
            title, year = title_year.rsplit(' (', 1)
            year = year.rstrip(')')
        else:
            title = title_year; year = ''
        clean = lambda s: ''.join(c for c in s if c.isalnum() or c in '-_ ').strip()
        new_base = f"{clean(series)} - {issue_num.zfill(3)} - {clean(title)}"
        if year:
            new_base += f" - {year}"
        new_name = f"{new_base}.{f['ext']}"
        new_path = pathlib.Path(f['folder']) / new_name
        # Confirm
        message = f"Rename file to:\n{new_name}?"
        confirm = QMessageBox.question(self, 'Rename', message, QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                os.rename(f['path'], new_path)
                self._load_files(f['folder'])
            except Exception as e:
                QMessageBox.critical(self, 'Rename Error', str(e))

# ---------- Custom Tables ----------
class FileTable(QTableWidget):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setDropIndicatorShown(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.setColumnCount(4)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.itemChanged.connect(self._cell_changed)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('application/x-comic-meta'):
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position().toPoint() if hasattr(e, 'position') else e.pos()
        row = self.rowAt(pos.y())
        if row < 0:
            return
        payload = e.mimeData().data('application/x-comic-meta').data().decode()
        parts = payload.split(' - ', 2)
        if len(parts) != 3:
            return
        series, num, rest = parts
        title, yr = rest.rsplit(' (', 1)
        yr = yr.rstrip(')')
        f = self.main.files[row]
        clean = lambda s: ''.join(c if c.isalnum() or c in '-_' else ' ' for c in s)
        new = f"{clean(series)} - {num.zfill(3)} - {clean(title)} - {yr}.{f['ext']}"
        np = pathlib.Path(f['folder']) / new
        if QMessageBox.question(self, 'Rename', f"Rename to\n{new}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            os.rename(f['path'], np)
            self.main._load_files(f['folder'])

    def _cell_changed(self, item):
        if getattr(self.main, '_populating', False) or item.column() != 0:
            return
        row = item.row()
        f = self.main.files[row]
        nm = item.text()
        if nm == f['name']:
            return
        np = pathlib.Path(f['folder']) / f"{nm}.{f['ext']}"
        if QMessageBox.question(self, 'Rename', f"Rename to\n{np.name}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            os.rename(f['path'], np)
            self.main._load_files(f['folder'])

class AlbumTable(QTableWidget):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragEnabled(True)
        self.setColumnCount(1)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def mouseMoveEvent(self, e):
        it = self.itemAt(e.pos())
        if not it:
            return
        mime = QMimeData()
        mime.setData('application/x-comic-meta', QByteArray(it.text().encode()))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

# ---------- Run ----------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ComicRenamer()
    w.show()
    sys.exit(app.exec())
