"""
QuickView Dialog for PDF Preview with Pan and Zoom functionality.

This module contains the complete QuickViewDialog implementation with:
- Pan functionality (left-click + drag)
- Advanced zoom controls
- Page navigation
- PNG export
- Cross-platform compatibility
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog, QMenu
)
from PySide6.QtCore import QSettings, Qt, QPoint, QPointF
from PySide6.QtGui import QIcon, QImage, QPainter, QAction

# Import internationalization system  
from i18n import tr
from utils.icons import get_app_icon


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
        
        # Store reference to parent dialog for context menu
        self.parent_dialog = parent
        
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
        """Handle mouse press for panning and context menu"""
        # Right click for context menu
        if event.button() == Qt.RightButton:
            self._show_context_menu(event)
            return
        
        # Left click for panning (only when image is larger than viewport)
        if event.button() == Qt.LeftButton:
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
        """Handle mouse movement for panning - Simple left-click drag"""
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
        """Handle mouse release to stop panning - Simple left-click release"""
        if event.button() == Qt.LeftButton and self.panning:
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
                # Calculate zoom factor with better granularity
                try:
                    zoom_factor = self.pdf_view.zoomFactor()
                        
                    if angle_delta > 0:
                        new_zoom = zoom_factor * 1.15  # Zoom in (smaller increment for smoother)
                    else:
                        new_zoom = zoom_factor / 1.15  # Zoom out
                    
                    # Limit zoom range
                    new_zoom = max(0.1, min(10.0, new_zoom))
                    
                    # Apply zoom - set to custom mode first, then set factor
                    self.pdf_view.setZoomMode(self.QPdfView.ZoomMode.Custom)
                    self.pdf_view.setZoomFactor(new_zoom)
                        
                except Exception as e:
                    print(f"Wheel zoom error: {e}")
            
            event.accept()
            return
        
        # Call original handler for normal scrolling
        self.original_wheel_event(event)
    
    def _show_context_menu(self, event):
        """Show context menu with export option"""
        if self.parent_dialog and hasattr(self.parent_dialog, '_export_current_page'):
            # Create context menu
            context_menu = QMenu(self.pdf_view)
            
            # Add export action
            export_action = QAction("💾 Export Page as PNG", self.pdf_view)
            export_action.triggered.connect(self.parent_dialog._export_current_page)
            context_menu.addAction(export_action)
            
            # Show context menu at cursor position
            if hasattr(event, 'globalPosition'):
                context_menu.exec(event.globalPosition().toPoint())
            else:
                context_menu.exec(event.globalPos())
    
    def __getattr__(self, name):
        """Delegate all other attributes and methods to the wrapped QPdfView"""
        return getattr(self.pdf_view, name)


class QuickViewDialog(QDialog):
    """
    Enhanced Quick View dialog for PDF files with complete functionality.
    
    Features:
    - Pan with left-click + drag when zoomed
    - Full page navigation (First/Previous/Next/Last)
    - Advanced zoom controls (manual + auto-fit)
    - PNG export with high quality
    - Window geometry persistence
    - Cross-platform compatibility
    """
    
    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        
        # Settings for window geometry persistence
        self.settings = QSettings("ComicsRename", "App")
        
        # Store file path and validate
        self.file_path = file_path
        if not self._validate_file():
            self.file_path = None
            return
        
        # Setup UI and PDF viewer
        self._setup_ui()
        if not self._setup_pdf_viewer():
            self.file_path = None
            return
            
        self._restore_geometry()
    
    def _validate_file(self):
        """Validate that the file exists and is a PDF"""
        if not self.file_path:
            try:
                QMessageBox.warning(self, tr("messages.warnings.invalid_file"), "No file path provided")
            except Exception:
                QMessageBox.warning(self, "Invalid File", "No file path provided")
            return False
        
        if not os.path.exists(self.file_path):
            try:
                QMessageBox.warning(self, tr("messages.warnings.file_not_found"), f"File not found: {self.file_path}")
            except Exception:
                QMessageBox.warning(self, "File Not Found", f"File not found: {self.file_path}")
            return False
        
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext != '.pdf':
            try:
                QMessageBox.warning(self, tr("messages.warnings.unsupported_format"), tr("messages.errors.unsupported_format"))
            except Exception:
                QMessageBox.warning(self, "Unsupported Format", "Only PDF files are supported for Quick View")
            return False
        
        return True
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Window properties - Create a descriptive title with filename
        filename = os.path.basename(self.file_path) if self.file_path else "PDF Viewer"
        try:
            # Try to use translation key first
            title = tr("dialogs.quick_view.title", title=filename)
        except Exception:
            # Fallback to simple title if translation fails
            title = f"Quick View - {filename}"
        
        self.setWindowTitle(title)
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
        """Create the toolbar with zoom, navigation, and export controls"""
        toolbar_layout = QHBoxLayout()
        
        # Navigation controls
        self.first_btn = QPushButton("⏮ First")
        self.prev_btn = QPushButton("◀ Previous")
        self.next_btn = QPushButton("Next ▶")
        self.last_btn = QPushButton("Last ⏭")
        
        # Page info label
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(120)
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("🔍- Zoom Out")
        self.zoom_in_btn = QPushButton("🔍+ Zoom In")
        self.fit_width_btn = QPushButton("Fit Width")
        self.fit_page_btn = QPushButton("🔍 Fit Page")
        
        # Set minimum button widths for consistent appearance
        self.first_btn.setMinimumWidth(60)
        self.prev_btn.setMinimumWidth(80)
        self.next_btn.setMinimumWidth(80)
        self.last_btn.setMinimumWidth(60)
        self.zoom_out_btn.setMinimumWidth(80)
        self.zoom_in_btn.setMinimumWidth(80)
        self.fit_width_btn.setMinimumWidth(80)
        self.fit_page_btn.setMinimumWidth(80)
        
        # Add navigation controls
        toolbar_layout.addWidget(self.first_btn)
        toolbar_layout.addWidget(self.prev_btn)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addWidget(self.next_btn)
        toolbar_layout.addWidget(self.last_btn)
        toolbar_layout.addStretch()
        
        # Add zoom controls
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.fit_width_btn)
        toolbar_layout.addWidget(self.fit_page_btn)
        
        self.main_layout.addLayout(toolbar_layout)
    
    def _setup_pdf_viewer(self):
        """Setup the PDF viewer component with panning functionality"""
        try:
            # Create enhanced PDF viewer with panning
            self.pdf_view_wrapper = PannablePdfView(self)
            
            # Create PDF document
            self.pdf_doc = self.pdf_view_wrapper.QPdfDocument(self)
            load_err = self.pdf_doc.load(self.file_path)
            if load_err != self.pdf_view_wrapper.QPdfDocument.Error.None_:
                try:
                    error_msg = tr("messages.errors.pdf_load_error", file=self.file_path)
                    QMessageBox.critical(self, tr("messages.errors.error"), error_msg)
                except Exception:
                    QMessageBox.critical(self, "Error", f"Could not load PDF file: {self.file_path}")
                return False
            
            # Configure the PDF view
            self.pdf_view_wrapper.setDocument(self.pdf_doc)
            self.pdf_view_wrapper.setPageMode(self.pdf_view_wrapper.QPdfView.PageMode.SinglePage)
            
            # Set initial zoom mode to fit page (full page visible by default)
            self.pdf_view_wrapper.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView)
            
            # Connect zoom controls to the wrapped PDF view
            self.zoom_out_btn.clicked.connect(self._zoom_out)
            self.zoom_in_btn.clicked.connect(self._zoom_in)
            self.fit_width_btn.clicked.connect(lambda: self._set_zoom_mode_fit_width())
            self.fit_page_btn.clicked.connect(lambda: self._set_zoom_mode_fit_page())
            
            # Connect navigation controls
            self.first_btn.clicked.connect(self._go_first_page)
            self.prev_btn.clicked.connect(self._go_prev_page)
            self.next_btn.clicked.connect(self._go_next_page)
            self.last_btn.clicked.connect(self._go_last_page)
            
            # Connect page change handler
            navigator = self.pdf_view_wrapper.pageNavigator()
            navigator.currentPageChanged.connect(self._update_page_label)
            
            # Initialize page label
            self._update_page_label()
            
            # Add the actual PDF view widget to layout
            self.main_layout.addWidget(self.pdf_view_wrapper.pdf_view)
            
            # Schedule initial fit after dialog is shown
            self._schedule_initial_fit()
            
            return True
            
        except ImportError:
            try:
                QMessageBox.critical(self, tr("messages.errors.error"), tr("messages.errors.could_not_load_pdf_viewer"))
            except Exception:
                QMessageBox.critical(self, "Error", "Could not load PDF viewer. Please ensure Qt PDF modules are installed.")
            return False
    
    def _zoom_in(self):
        """Zoom in on the PDF"""
        try:
            # Get current zoom factor
            current_zoom = self.pdf_view_wrapper.pdf_view.zoomFactor()
            new_zoom = min(current_zoom * 1.25, 10.0)  # Max 10x zoom
            
            # Set zoom factor and switch to custom zoom mode
            self.pdf_view_wrapper.pdf_view.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.Custom)
            self.pdf_view_wrapper.pdf_view.setZoomFactor(new_zoom)
                
        except Exception as e:
            print(f"Zoom in error: {e}")
    
    def _zoom_out(self):
        """Zoom out on the PDF"""
        try:
            # Get current zoom factor
            current_zoom = self.pdf_view_wrapper.pdf_view.zoomFactor()
            new_zoom = max(current_zoom * 0.8, 0.1)  # Min 0.1x zoom
            
            # Set zoom factor and switch to custom zoom mode
            self.pdf_view_wrapper.pdf_view.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.Custom)
            self.pdf_view_wrapper.pdf_view.setZoomFactor(new_zoom)
                
        except Exception as e:
            print(f"Zoom out error: {e}")
            
    def _set_zoom_mode_fit_width(self):
        """Set zoom mode to fit width"""
        try:
            self.pdf_view_wrapper.pdf_view.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitToWidth)
        except Exception as e:
            print(f"Fit width error: {e}")
            
    def _set_zoom_mode_fit_page(self):
        """Set zoom mode to fit page"""
        try:
            self.pdf_view_wrapper.pdf_view.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView)
        except Exception as e:
            print(f"Fit page error: {e}")
            
    def _schedule_initial_fit(self):
        """Schedule initial fit to page after dialog is fully rendered"""
        try:
            from PySide6.QtCore import QTimer
            # Use a timer to ensure the dialog is fully rendered before fitting
            QTimer.singleShot(100, self._apply_initial_fit)
        except ImportError:
            # Fallback: apply immediately
            self._apply_initial_fit()
            
    def _apply_initial_fit(self):
        """Apply initial fit to page"""
        try:
            # Ensure the PDF view is properly sized and fitted
            self.pdf_view_wrapper.pdf_view.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView)
            # Force a repaint to ensure proper display
            self.pdf_view_wrapper.pdf_view.update()
        except Exception as e:
            print(f"Initial fit error: {e}")
    
    def _go_first_page(self):
        """Go to first page"""
        navigator = self.pdf_view_wrapper.pageNavigator()
        if navigator.currentPage() > 0:
            navigator.jump(0, QPointF(0, 0))
    
    def _go_prev_page(self):
        """Go to previous page"""
        navigator = self.pdf_view_wrapper.pageNavigator()
        if navigator.currentPage() > 0:
            navigator.jump(navigator.currentPage() - 1, QPointF(0, 0))
    
    def _go_next_page(self):
        """Go to next page"""
        navigator = self.pdf_view_wrapper.pageNavigator()
        current = navigator.currentPage()
        if current < self.pdf_doc.pageCount() - 1:
            navigator.jump(current + 1, QPointF(0, 0))
    
    def _go_last_page(self):
        """Go to last page"""
        navigator = self.pdf_view_wrapper.pageNavigator()
        last_page = self.pdf_doc.pageCount() - 1
        if navigator.currentPage() < last_page:
            navigator.jump(last_page, QPointF(0, 0))
    
    def _update_page_label(self):
        """Update the page label and navigation button states"""
        try:
            current = self.pdf_view_wrapper.pageNavigator().currentPage()
            total = self.pdf_doc.pageCount()
            self.page_label.setText(f"Page {current + 1} of {total}")
            
            # Update button states
            self.first_btn.setEnabled(current > 0)
            self.prev_btn.setEnabled(current > 0)
            self.next_btn.setEnabled(current < total - 1)
            self.last_btn.setEnabled(current < total - 1)
        except Exception:
            self.page_label.setText("Page 1 of 1")
    
    def _export_current_page(self):
        """Export the current page as PNG"""
        try:
            # Get current page
            current_page = self.pdf_view_wrapper.pageNavigator().currentPage()
            
            # Create suggested filename
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            suggested_name = f"{base_name}_page_{current_page + 1}.png"
            
            # Get the directory of the original file
            file_dir = os.path.dirname(self.file_path)
            suggested_path = os.path.join(file_dir, suggested_name)
            
            # Show save dialog
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Page as PNG",
                suggested_path,
                "PNG Files (*.png);;All Files (*)"
            )
            
            if save_path:
                print(f"[DEBUG] Exporting page {current_page + 1} to: {save_path}")
                # Render the current page as image
                # Get page size at high resolution
                page_size = self.pdf_doc.pagePointSize(current_page)
                print(f"[DEBUG] Page size: {page_size}")
                # Scale factor for high quality export (300 DPI equivalent)
                scale_factor = 300.0 / 72.0  # PDF points are 72 DPI
                
                # Create high resolution image
                image_size = page_size * scale_factor
                print(f"[DEBUG] Image size: {image_size}")
                image = QImage(int(image_size.width()), int(image_size.height()), QImage.Format_ARGB32)
                image.fill(0xFFFFFFFF)  # White background
                
                # Render PDF page to image
                # Use the correct signature: render(page, imageSize, options)
                from PySide6.QtCore import QSize
                try:
                    from PySide6.QtPdf import QPdfDocumentRenderOptions
                    render_options = QPdfDocumentRenderOptions()
                except ImportError:
                    render_options = None
                
                # Use the correct render method signature
                image_size_qt = QSize(int(image_size.width()), int(image_size.height()))
                
                # Render the page
                try:
                    if render_options:
                        rendered_image = self.pdf_doc.render(current_page, image_size_qt, render_options)
                    else:
                        rendered_image = self.pdf_doc.render(current_page, image_size_qt)
                    
                    # Use the rendered image
                    if not rendered_image.isNull():
                        image = rendered_image
                    else:
                        raise ValueError("Rendered image is null")
                        
                except Exception as render_error:
                    # Fallback: create a white image with error message
                    print(f"[DEBUG] Render error: {render_error}")
                    image = QImage(int(image_size.width()), int(image_size.height()), QImage.Format_ARGB32)
                    image.fill(0xFFFFFFFF)  # White background
                    painter = QPainter(image)
                    try:
                        painter.drawText(image.rect(), Qt.AlignCenter, "Failed to render PDF page")
                    finally:
                        painter.end()  # Ensure painter is properly closed
                
                # Save the image
                print(f"[DEBUG] Saving image to: {save_path}")
                if image.save(save_path, "PNG"):
                    print(f"[DEBUG] Export successful")
                    QMessageBox.information(self, "Export Successful", f"Page exported to:\n{save_path}")
                else:
                    print(f"[DEBUG] Export failed - could not save image")
                    QMessageBox.warning(self, "Export Failed", "Failed to save the image file.")
                    
        except Exception as e:
            print(f"[DEBUG] Export error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Export Error", f"Failed to export page:\n{str(e)}")
    
    def _restore_geometry(self):
        """Restore window geometry from settings"""
        saved_geometry = self.settings.value('quick_view_geometry')
        if saved_geometry:
            self.restoreGeometry(saved_geometry)
        else:
            # Default size: make it larger and more proportional for PDF viewing
            self.resize(900, 1000)  # Wider and taller for better PDF display
            
            # Center the window on screen
            try:
                from PySide6.QtWidgets import QApplication
                screen = QApplication.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.frameGeometry()
                    center_point = screen_geometry.center()
                    window_geometry.moveCenter(center_point)
                    self.move(window_geometry.topLeft())
            except Exception:
                # Fallback: don't center if there's an issue
                pass
    
    def _save_geometry(self):
        """Save window geometry to settings"""
        self.settings.setValue('quick_view_geometry', self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self._save_geometry()
        super().closeEvent(event)
        
    def resizeEvent(self, event):
        """Handle window resize event to maintain proper PDF display"""
        super().resizeEvent(event)
        # If we're in fit mode, reapply the fit after resize
        try:
            if hasattr(self, 'pdf_view_wrapper') and self.pdf_view_wrapper:
                # Small delay to ensure resize is complete
                from PySide6.QtCore import QTimer
                QTimer.singleShot(50, self._maintain_fit_mode)
        except Exception:
            pass
            
    def _maintain_fit_mode(self):
        """Maintain fit mode after window resize"""
        try:
            # Check if we're in a fit mode and reapply it
            if hasattr(self.pdf_view_wrapper, 'zoomMode'):
                current_mode = self.pdf_view_wrapper.zoomMode()
                if current_mode == self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView:
                    self.pdf_view_wrapper.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitInView)
                elif current_mode == self.pdf_view_wrapper.QPdfView.ZoomMode.FitToWidth:
                    self.pdf_view_wrapper.setZoomMode(self.pdf_view_wrapper.QPdfView.ZoomMode.FitToWidth)
        except Exception:
            pass
    
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
