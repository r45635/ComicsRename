"""
Custom input widgets with drag and drop functionality.
"""
import re
from PySide6.QtWidgets import QLineEdit, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QDrag
from PySide6.QtCore import QMimeData


class DroppableLineEdit(QLineEdit):
    """A QLineEdit that accepts drag and drop of text/files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text().strip()
            # Remove file:// prefix if present
            if text.startswith('file://'):
                text = text[7:]
            self.setText(text)
            event.acceptProposedAction()
        else:
            event.ignore()


class EditableFolderLineEdit(QLineEdit):
    """A QLineEdit for displaying folder names (not full paths) with drag support for search"""
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(False)  # Disable drop to avoid conflicts
        self.setReadOnly(True)  # Read-only by default, editable on double-click
        self.original_text = ""  # Store original text for comparison
        self.editing_finished = False  # Flag to prevent double processing
        
    def mouseDoubleClickEvent(self, event):
        """Enable editing on double-click"""
        if event.button() == Qt.LeftButton:
            self.original_text = self.text()  # Store original text
            self.editing_finished = False  # Reset flag
            self.setReadOnly(False)
            self.selectAll()
            self.setFocus()
        super().mouseDoubleClickEvent(event)
    
    def keyPressEvent(self, event):
        """Handle Enter/Return and Escape keys during editing"""
        if not self.isReadOnly():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._finish_editing(save=True)
                return
            elif event.key() == Qt.Key_Escape:
                self._finish_editing(save=False)
                return
        super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Finish editing when focus is lost"""
        if not self.isReadOnly():
            self._finish_editing(save=True)
        super().focusOutEvent(event)
    
    def _finish_editing(self, save=True):
        """Finish editing and optionally save changes"""
        if self.isReadOnly() or self.editing_finished:
            return
            
        self.editing_finished = True  # Set flag to prevent double processing
        new_text = self.text().strip()
        
        if save and new_text != self.original_text and new_text:
            # Confirm rename operation
            if self.main_window and hasattr(self.main_window, '_confirm_and_rename_folder'):
                success = self.main_window._confirm_and_rename_folder(self.original_text, new_text)
                if not success:
                    # Revert to original text if rename failed
                    self.setText(self.original_text)
            else:
                # Fallback: just revert to original text
                self.setText(self.original_text)
        elif not save:
            # Restore original text on cancel
            self.setText(self.original_text)
        
        self.setReadOnly(True)
        self.clearFocus()
        
    def mousePressEvent(self, event):
        """Handle mouse press to start drag operation"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to start drag if conditions are met"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if not hasattr(self, 'drag_start_position'):
            return
            
        if ((event.pos() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # Start drag operation with folder name
        folder_name = self.text()
        if folder_name:
            # Clean the folder name by removing bracketed and parenthetical content
            cleaned_name = self._clean_folder_name(folder_name)
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(cleaned_name)
            drag.setMimeData(mime_data)
            drag.exec(Qt.CopyAction)
    
    def _clean_folder_name(self, folder_name):
        """Clean folder name by removing bracketed and parenthetical content"""
        # Remove content in square brackets like [Fantastique]
        cleaned = re.sub(r'\[.*?\]', '', folder_name)
        
        # Remove content in parentheses like (PeruMartino)
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        
        # Remove extra whitespace and strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
