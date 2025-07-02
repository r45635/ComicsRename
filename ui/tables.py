"""
Custom table widgets for ComicsRename application.
"""

import os
import re
import pathlib
import shutil
from PySide6.QtWidgets import (
    QTableWidget, QAbstractItemView, QHeaderView, QMenu, QMessageBox, QDialog, QVBoxLayout
)
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSettings
from PySide6.QtGui import QDrag

# Import internationalization system
from i18n import tr
from utils import get_system_info, open_file_cross_platform, reveal_file_cross_platform


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
            # Try to parse the payload as "Series - Num - Title (Year)"
            parts = payload.split(' - ', 2)
            if len(parts) < 3:
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
            msg = f"Voulez-vous {op} les fichiers suivants dans le dossier actif ?\\n\\n" + "\\n".join(os.path.basename(f) for f in files_to_add)
            if QMessageBox.question(self, "Ajouter des fichiers", msg, QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                return
            
            dest_folder = self.main.files[0]['folder'] if self.main.files else self.main.settings.value('last_folder', '')
            if not dest_folder:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.no_active_folder"))
                return
            
            for src in files_to_add:
                # Check that the file exists
                if not os.path.exists(src):
                    QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.file_not_exists", path=src))
                    continue
                # Clean the filename (remove forbidden characters)
                base_name = os.path.basename(src).replace('/', '_')
                # Truncate name if too long (255 chars max on most filesystems)
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
                    # Check if destination file exists despite the exception
                    if os.path.exists(dest):
                        QMessageBox.warning(
                            self,
                            "Avertissement",
                            f"Le fichier a été copié, mais une exception a été levée :\\n{e}\\n\\nSource: {src}\\nDestination: {dest}"
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
        system_info = get_system_info()
        # Adaptive menu labels based on OS
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
        
        action = menu.exec(self.viewport().mapToGlobal(pos))
        f = self.main.files[row]
        file_path = str(f['path'])
        
        # Handle actions
        if action == open_action:
            open_file_cross_platform(file_path)
        elif action == reveal_action:
            reveal_file_cross_platform(file_path)
        elif action == refresh_action:
            folder = self.main.settings.value('last_folder', '')
            if folder:
                # First try the exact path as stored
                if pathlib.Path(folder).exists():
                    self.main._load_files(folder)
                else:
                    # Only if exact path doesn't exist, use fallback logic
                    best_folder = self.main._get_fallback_folder_path(folder)
                    self.main._load_files(best_folder)
        elif action == quick_view_action:
            # Use the new independent QuickViewDialog
            from .dialogs import QuickViewDialog
            QuickViewDialog.show_quick_view(file_path, self)

    def _show_quick_view(self, file_path):
        """Show quick view dialog for PDF files"""
        # Only for PDF files
        ext = os.path.splitext(file_path)[1].lower()
        if ext != '.pdf':
            QMessageBox.warning(self, tr("messages.warnings.unsupported_format"), tr("messages.errors.unsupported_format"))
            return
        
        # Try to import Qt PDF modules
        try:
            from PySide6.QtPdf import QPdfDocument
            from PySide6.QtPdfWidgets import QPdfView
        except ImportError:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.could_not_load_pdf_viewer"))
            return
        
        # Create dialog to display first page
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("dialogs.settings.quick_view.title", title=os.path.basename(file_path)))
        dialog.setModal(False)  # Allow window to be resized and moved freely
        
        # Restore window geometry from settings
        settings = QSettings("ComicsRename", "App")
        saved_geometry = settings.value('quick_view_geometry')
        if saved_geometry:
            dialog.restoreGeometry(saved_geometry)
        else:
            dialog.resize(700, 900)  # Default size, slightly larger
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(5, 5, 5, 5)  # Small margins
        
        # Create PDF document and view
        pdf_doc = QPdfDocument(dialog)
        load_err = pdf_doc.load(file_path)
        if load_err != QPdfDocument.Error.None_:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.pdf_load_error", file=file_path))
            return
        
        view = QPdfView(dialog)
        view.setDocument(pdf_doc)
        view.setPageMode(QPdfView.PageMode.SinglePage)
        
        # Create custom pannbale PDF view (this would need the PannableQPdfView class)
        # For now, using standard view
        layout.addWidget(view)
        dialog.show()


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
