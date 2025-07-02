"""
Dialog windows for ComicsRename application.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QCheckBox, QLineEdit, QDialogButtonBox, QMessageBox,
    QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton, QSlider
)
from PySide6.QtCore import QSettings, Qt, QPoint
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QIcon

# Import internationalization system  
from i18n import tr, get_supported_languages, get_current_language, set_language


def get_app_icon():
    """Get the application icon, with fallback options"""
    icon_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'comicsrename.ico'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'comicsrename_64x64.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'comicsrename_32x32.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'icon.ico')
    ]
    
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            return QIcon(icon_path)
    
    return QIcon()  # Return empty icon if none found


class PannableLabel(QLabel):
    """A QLabel that supports mouse panning and zooming"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setScaledContents(False)
        
        # Panning variables
        self.panning = False
        self.pan_start_pos = QPoint()
        self.last_pan_pos = QPoint()
        
        # Zoom variables
        self.zoom_factor = 1.0
        self.original_pixmap = None
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def setPixmap(self, pixmap):
        """Set the pixmap and store the original for zooming"""
        self.original_pixmap = pixmap
        self.updatePixmap()
    
    def updatePixmap(self):
        """Update the displayed pixmap based on zoom factor"""
        if self.original_pixmap:
            if self.zoom_factor != 1.0:
                scaled_pixmap = self.original_pixmap.scaled(
                    int(self.original_pixmap.width() * self.zoom_factor),
                    int(self.original_pixmap.height() * self.zoom_factor),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                super().setPixmap(scaled_pixmap)
            else:
                super().setPixmap(self.original_pixmap)
    
    def mousePressEvent(self, event):
        """Start panning when middle mouse button is pressed"""
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            self.panning = True
            self.pan_start_pos = event.position().toPoint()
            self.last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle panning during mouse movement"""
        if self.panning:
            # Calculate the delta movement
            delta = event.position().toPoint() - self.last_pan_pos
            
            # Get the scroll area parent
            scroll_area = self.parent()
            while scroll_area and not isinstance(scroll_area, QScrollArea):
                scroll_area = scroll_area.parent()
            
            if scroll_area:
                # Move the scroll bars
                h_scroll = scroll_area.horizontalScrollBar()
                v_scroll = scroll_area.verticalScrollBar()
                
                h_scroll.setValue(h_scroll.value() - delta.x())
                v_scroll.setValue(v_scroll.value() - delta.y())
            
            self.last_pan_pos = event.position().toPoint()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Stop panning when mouse button is released"""
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom in/out
            zoom_in = event.angleDelta().y() > 0
            zoom_change = 1.1 if zoom_in else 1/1.1
            
            new_zoom = self.zoom_factor * zoom_change
            # Limit zoom between 0.1x and 10x
            if 0.1 <= new_zoom <= 10.0:
                self.zoom_factor = new_zoom
                self.updatePixmap()
        else:
            super().wheelEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialogs.settings.title"))
        
        # Set dialog icon
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
        self.settings.setValue("bdgest_user", self.bdgest_user.text())
        self.settings.setValue("bdgest_pass", self.bdgest_pass.text())
        self.settings.setValue("comicvine_api", self.comicvine_api.text())
        super().accept()


class QuickViewDialog(QDialog):
    """
    Independent Quick View dialog for PDF files.
    
    This class encapsulates all Quick View functionality and is designed to be
    completely independent from the main application. It only needs a PDF file path.
    """
    
    def __init__(self, parent=None, file_path=None):
        """
        Initialize Quick View dialog.
        
        Args:
            parent: Parent widget (can be None for standalone use)
            file_path: Path to the PDF file to display
        """
        super().__init__(parent)
        self.file_path = file_path
        self.settings = QSettings("ComicsRename", "App")
        
        # Validate file
        if not self._validate_file():
            return
        
        self._setup_ui()
        self._setup_pdf_viewer()
        self._restore_geometry()
    
    def _validate_file(self):
        """Validate that the file exists and is a PDF"""
        if not self.file_path:
            QMessageBox.warning(self, tr("messages.warnings.invalid_file"), "No file path provided")
            return False
        
        if not os.path.exists(self.file_path):
            QMessageBox.warning(self, tr("messages.warnings.file_not_found"), f"File not found: {self.file_path}")
            return False
        
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext != '.pdf':
            QMessageBox.warning(self, tr("messages.warnings.unsupported_format"), tr("messages.errors.unsupported_format"))
            return False
        
        return True
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Window properties
        self.setWindowTitle(tr("ui.dialogs.quick_view.title").format(title=os.path.basename(self.file_path)))
        self.setModal(False)  # Allow window to be resized and moved freely
        
        # Set application icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)  # Small margins
        
        # Create toolbar
        self._create_toolbar()
    
    def _create_toolbar(self):
        """Create the toolbar with zoom and navigation controls"""
        toolbar_layout = QHBoxLayout()
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_in_btn = QPushButton("Zoom In")
        self.fit_width_btn = QPushButton("Fit Width")
        self.fit_page_btn = QPushButton("Fit Page")
        
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.fit_width_btn)
        toolbar_layout.addWidget(self.fit_page_btn)
        toolbar_layout.addStretch()
        
        # Instructions label
        instructions = QLabel("Drag to pan • Mouse wheel to zoom • Right-click for context menu")
        instructions.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        toolbar_layout.addWidget(instructions)
        
        self.main_layout.addLayout(toolbar_layout)
    
    def _setup_pdf_viewer(self):
        """Setup the PDF viewer component"""
        # Try to import Qt PDF modules
        try:
            from PySide6.QtPdf import QPdfDocument
            from PySide6.QtPdfWidgets import QPdfView
        except ImportError:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.could_not_load_pdf_viewer"))
            return False
        
        # Create PDF document and view
        self.pdf_doc = QPdfDocument(self)
        load_err = self.pdf_doc.load(self.file_path)
        if load_err != QPdfDocument.Error.None_:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.pdf_load_error").format(file=self.file_path))
            return False
        
        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_doc)
        self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)
        
        # Connect zoom controls
        self.zoom_out_btn.clicked.connect(lambda: self.pdf_view.setZoomFactor(self.pdf_view.zoomFactor() * 0.8))
        self.zoom_in_btn.clicked.connect(lambda: self.pdf_view.setZoomFactor(self.pdf_view.zoomFactor() * 1.25))
        self.fit_width_btn.clicked.connect(lambda: self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth))
        self.fit_page_btn.clicked.connect(lambda: self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView))
        
        self.main_layout.addWidget(self.pdf_view)
        return True
    
    def _restore_geometry(self):
        """Restore window geometry from settings"""
        saved_geometry = self.settings.value('quick_view_geometry')
        if saved_geometry:
            self.restoreGeometry(saved_geometry)
        else:
            self.resize(800, 900)  # Default size
    
    def _save_geometry(self):
        """Save window geometry to settings"""
        self.settings.setValue('quick_view_geometry', self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self._save_geometry()
        super().closeEvent(event)
    
    @staticmethod
    def show_quick_view(file_path, parent=None):
        """
        Static method to show Quick View dialog.
        
        This is the main entry point for using Quick View from other parts of the application.
        
        Args:
            file_path: Path to the PDF file to display
            parent: Parent widget (optional)
        
        Returns:
            QuickViewDialog instance or None if creation failed
        """
        dialog = QuickViewDialog(parent, file_path)
        if dialog.file_path:  # Only show if file validation passed
            dialog.show()
            return dialog
        return None
