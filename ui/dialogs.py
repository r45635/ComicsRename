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





class PannablePdfView:
    """
    Enhanced PDF viewer with panning functionality.
    
    This class wraps QPdfView and adds mouse panning capabilities
    by intercepting mouse events and manipulating scroll bars.
    Compatible with macOS and Windows.
    """
    
    def __init__(self, parent=None):
        # Try to import Qt PDF modules
        try:
            from PySide6.QtPdf import QPdfDocument
            from PySide6.QtPdfWidgets import QPdfView
            self.QPdfView = QPdfView
            self.QPdfDocument = QPdfDocument
        except ImportError:
            raise ImportError("Qt PDF modules not available")
        
        # Create the actual PDF view
        self.pdf_view = QPdfView(parent)
        
        # Panning state
        self.panning = False
        self.last_pan_pos = QPoint()
        
        # Store original event handlers
        self.original_mouse_press = self.pdf_view.mousePressEvent
        self.original_mouse_move = self.pdf_view.mouseMoveEvent
        self.original_mouse_release = self.pdf_view.mouseReleaseEvent
        self.original_wheel_event = self.pdf_view.wheelEvent
        
        # Install custom event handlers
        self.pdf_view.mousePressEvent = self._mouse_press_event
        self.pdf_view.mouseMoveEvent = self._mouse_move_event
        self.pdf_view.mouseReleaseEvent = self._mouse_release_event
        self.pdf_view.wheelEvent = self._wheel_event
        
        # Enable mouse tracking for smooth panning
        self.pdf_view.setMouseTracking(True)
        
        # Platform-specific settings
        import platform
        self.is_macos = platform.system() == "Darwin"
    
    def _mouse_press_event(self, event):
        """Handle mouse press for panning - Simple right-click method"""
        # Right click for panning (only when image is larger than viewport)
        if event.button() == Qt.RightButton:
            # Check if image is larger than viewport (pan needed)
            if self._is_pan_needed():
                self.panning = True
                if hasattr(event, 'globalPosition'):
                    self.last_pan_pos = event.globalPosition().toPoint()
                else:
                    self.last_pan_pos = event.position().toPoint()
                self.pdf_view.setCursor(Qt.ClosedHandCursor)
                event.accept()
                return
        
        # Call original handler for all other interactions
        self.original_mouse_press(event)
    
    def _is_pan_needed(self):
        """Check if the image is larger than the viewport and panning is useful"""
        try:
            # Get viewport size
            viewport = self.pdf_view.viewport()
            if not viewport:
                return True  # Default to allowing pan
            
            viewport_size = viewport.size()
            
            # Get document size at current zoom
            zoom_factor = self.pdf_view.zoomFactor()
            
            # Simple heuristic: if zoom > 1.0, panning is likely needed
            return zoom_factor > 1.0
            
        except Exception:
            # If we can't determine, allow panning
            return True
    
    def _mouse_move_event(self, event):
        """Handle mouse movement for panning - Simple right-click drag"""
        if self.panning:
            # Calculate movement delta
            if hasattr(event, 'globalPosition'):
                current_pos = event.globalPosition().toPoint()
            else:
                current_pos = event.position().toPoint()
            
            delta = current_pos - self.last_pan_pos
            
            # Get the scroll area from QPdfView
            viewport = self.pdf_view.viewport()
            if viewport:
                # Try to get parent scroll area
                scroll_area = viewport.parent()
                while scroll_area and not hasattr(scroll_area, 'horizontalScrollBar'):
                    scroll_area = scroll_area.parent()
                
                if scroll_area and hasattr(scroll_area, 'horizontalScrollBar'):
                    # Pan by adjusting scroll bars
                    h_scroll = scroll_area.horizontalScrollBar()
                    v_scroll = scroll_area.verticalScrollBar()
                    
                    if h_scroll:
                        new_h_value = h_scroll.value() - delta.x()
                        h_scroll.setValue(max(h_scroll.minimum(), min(h_scroll.maximum(), new_h_value)))
                    
                    if v_scroll:
                        new_v_value = v_scroll.value() - delta.y()
                        v_scroll.setValue(max(v_scroll.minimum(), min(v_scroll.maximum(), new_v_value)))
            
            self.last_pan_pos = current_pos
            event.accept()
            return
        
        # Call original handler if not panning
        self.original_mouse_move(event)
    
    def _mouse_release_event(self, event):
        """Handle mouse release to stop panning - Simple right-click release"""
        if event.button() == Qt.RightButton and self.panning:
            self.panning = False
            self.pdf_view.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        
        # Call original handler for other buttons
        self.original_mouse_release(event)
    
    def _wheel_event(self, event):
        """Handle wheel events for zooming - Cross-platform compatible"""
        # Check for zoom modifier (Ctrl key)
        if event.modifiers() & Qt.ControlModifier:
            # Zoom functionality
            angle_delta = event.angleDelta().y()
            if angle_delta != 0:
                # Calculate zoom factor
                zoom_factor = self.pdf_view.zoomFactor()
                if angle_delta > 0:
                    new_zoom = zoom_factor * 1.2  # Zoom in
                else:
                    new_zoom = zoom_factor / 1.2  # Zoom out
                
                # Limit zoom range
                new_zoom = max(0.1, min(10.0, new_zoom))
                self.pdf_view.setZoomFactor(new_zoom)
            
            event.accept()
            return
        
        # Call original handler for normal scrolling
        self.original_wheel_event(event)
    
    def __getattr__(self, name):
        """Delegate all other attributes and methods to the wrapped QPdfView"""
        return getattr(self.pdf_view, name)


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
        
        # Instructions label with simplified right-click pan control
        instructions = QLabel("Pan: Right-click + Drag (when zoomed) • Zoom: Ctrl + Mouse wheel")
        instructions.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        toolbar_layout.addWidget(instructions)
        
        self.main_layout.addLayout(toolbar_layout)
    
    def _setup_pdf_viewer(self):
        """Setup the PDF viewer component with panning functionality"""
        try:
            # Create enhanced PDF viewer with panning
            self.pdf_view_wrapper = PannablePdfView(self)
            
            # Create PDF document
            pdf_doc = self.pdf_view_wrapper.QPdfDocument(self)
            load_err = pdf_doc.load(self.file_path)
            if load_err != self.pdf_view_wrapper.QPdfDocument.Error.None_:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.pdf_load_error").format(file=self.file_path))
                return False
            
            # Configure the PDF view
            self.pdf_view_wrapper.setDocument(pdf_doc)
            self.pdf_view_wrapper.setPageMode(self.pdf_view_wrapper.QPdfView.PageMode.SinglePage)
            
            # Connect zoom controls to the wrapped PDF view
            self.zoom_out_btn.clicked.connect(lambda: self.pdf_view_wrapper.setZoomFactor(self.pdf_view_wrapper.zoomFactor() * 0.8))
            self.zoom_in_btn.clicked.connect(lambda: self.pdf_view_wrapper.setZoomFactor(self.pdf_view_wrapper.zoomFactor() * 1.25))
            self.fit_width_btn.clicked.connect(lambda: self.pdf_view_wrapper.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitToWidth))
            self.fit_page_btn.clicked.connect(lambda: self.pdf_view_wrapper.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView))
            
            # Add the actual PDF view widget to layout
            self.main_layout.addWidget(self.pdf_view_wrapper.pdf_view)
            return True
            
        except ImportError:
            QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.could_not_load_pdf_viewer"))
            return False
    
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
