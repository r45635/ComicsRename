"""
Enhanced Rename Confirmation Dialog

This module provides an enhanced confirmation dialog that includes SafeRename status indication.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from utils.icons import get_app_icon
from i18n import tr


class EnhancedRenameConfirmationDialog(QDialog):
    """
    Enhanced rename confirmation dialog with minimal SafeRename status indication.
    """
    
    def __init__(self, parent=None, new_name="", safe_rename_passed=False, 
                 safe_rename_score=0.0, is_folder=False, old_name=""):
        super().__init__(parent)
        self.setWindowTitle(tr("dialogs.rename_confirmation.title"))
        self.setModal(True)
        self.resize(420, 200)
        
        # Set dialog icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.new_name = new_name
        self.safe_rename_passed = safe_rename_passed
        self.is_folder = is_folder
        self.old_name = old_name
        
        self.user_result = QMessageBox.StandardButton.No  # Default to No
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Main message
        if self.is_folder:
            message = tr("dialogs.rename_confirmation.folder_message", 
                        old_name=self.old_name, new_name=self.new_name)
        else:
            message = tr("dialogs.rename_confirmation.file_message", new_name=self.new_name)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_font = QFont()
        message_font.setPointSize(14)  # Texte plus grand
        message_label.setFont(message_font)
        layout.addWidget(message_label)
        
        # Minimal SafeRename status (only for files, not folders)
        if not self.is_folder and self.safe_rename_passed:
            safe_label = QLabel("✅ SafeRename")
            safe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            safe_label.setStyleSheet("color: #2e7d32; font-weight: bold; font-size: 16px;")  # Plus grand
            layout.addWidget(safe_label)
        
        # Buttons
        button_layout = QHBoxLayout()

        self.yes_btn = QPushButton("&" + tr("ui.buttons.confirm"))
        self.yes_btn.clicked.connect(self._accept_rename)

        self.no_btn = QPushButton("&" + tr("ui.buttons.cancel"))
        self.no_btn.clicked.connect(self._reject_rename)
        self.no_btn.setDefault(True)  # Make Cancel the default
        
        button_layout.addStretch()
        button_layout.addWidget(self.yes_btn)
        button_layout.addWidget(self.no_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _accept_rename(self):
        """Accept the rename operation."""
        self.user_result = QMessageBox.StandardButton.Yes
        self.accept()
    
    def _reject_rename(self):
        """Reject the rename operation."""
        self.user_result = QMessageBox.StandardButton.No
        self.reject()
    
    def get_result(self):
        """Get the user's choice."""
        return self.user_result


def show_enhanced_rename_confirmation(parent=None, new_name="", safe_rename_passed=False, 
                                    safe_rename_score=0.0, is_folder=False, old_name=""):
    """
    Show enhanced rename confirmation dialog.
    
    Args:
        parent: Parent widget
        new_name (str): New filename/folder name
        safe_rename_passed (bool): Whether SafeRename check passed
        safe_rename_score (float): SafeRename similarity score
        is_folder (bool): Whether renaming a folder
        old_name (str): Old name (for folders)
        
    Returns:
        QMessageBox.StandardButton: User's choice (Yes or No)
    """
    dialog = EnhancedRenameConfirmationDialog(
        parent=parent,
        new_name=new_name,
        safe_rename_passed=safe_rename_passed,
        safe_rename_score=safe_rename_score,
        is_folder=is_folder,
        old_name=old_name
    )
    
    dialog.exec()
    return dialog.get_result()
