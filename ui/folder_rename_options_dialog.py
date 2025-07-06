"""
Folder Rename Options Dialog

This module provides a dialog for selecting folder rename/move options when working with single files.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QRadioButton, QButtonGroup, QComboBox,
    QGroupBox, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pathlib import Path
from utils.icons import get_app_icon
from i18n import tr


class FolderRenameOptionsDialog(QDialog):
    """
    Dialog for selecting folder rename/move options for single file operations.
    """
    
    def __init__(self, parent=None, current_folder=None, series_name="", 
                 parent_folder=None, root_folder=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialogs.folder_rename_options.title"))
        self.setModal(True)
        self.resize(500, 400)
        
        # Set dialog icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.current_folder = Path(current_folder) if current_folder else None
        self.series_name = series_name
        self.parent_folder = Path(parent_folder) if parent_folder else None
        self.root_folder = Path(root_folder) if root_folder else None
        
        # Result variables
        self.selected_option = None
        self.target_location = None
        self.create_new_folder = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(tr("dialogs.folder_rename_options.subtitle"))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Current info
        info_label = QLabel(tr("dialogs.folder_rename_options.current_info", 
                              current_folder=self.current_folder.name if self.current_folder else "N/A",
                              series_name=self.series_name))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Options group
        options_group = QGroupBox(tr("dialogs.folder_rename_options.options_title"))
        options_layout = QVBoxLayout(options_group)
        
        # Radio button group
        self.button_group = QButtonGroup(self)
        
        # Option 1: Rename current folder
        self.rename_current_radio = QRadioButton(
            tr("dialogs.folder_rename_options.rename_current", 
               folder_name=self.current_folder.name if self.current_folder else "N/A",
               series_name=self.series_name)
        )
        self.rename_current_radio.setChecked(True)  # Default option
        self.button_group.addButton(self.rename_current_radio, 1)
        options_layout.addWidget(self.rename_current_radio)
        
        # Option 2: Create new folder at same level
        self.create_same_level_radio = QRadioButton(
            tr("dialogs.folder_rename_options.create_same_level", series_name=self.series_name)
        )
        self.button_group.addButton(self.create_same_level_radio, 2)
        options_layout.addWidget(self.create_same_level_radio)
        
        # Option 3: Create new subfolder inside current folder
        self.create_subfolder_radio = QRadioButton(
            tr("dialogs.folder_rename_options.create_subfolder", series_name=self.series_name)
        )
        self.button_group.addButton(self.create_subfolder_radio, 3)
        options_layout.addWidget(self.create_subfolder_radio)
        
        # Option 4: Create new folder at parent level
        if (self.parent_folder and self.current_folder and 
            self.parent_folder != self.current_folder.parent):
            self.create_parent_level_radio = QRadioButton(
                tr("dialogs.folder_rename_options.create_parent_level", 
                   series_name=self.series_name,
                   parent_folder=self.parent_folder.name)
            )
            self.button_group.addButton(self.create_parent_level_radio, 4)
            options_layout.addWidget(self.create_parent_level_radio)
        else:
            self.create_parent_level_radio = None
        
        # Option 5: Create new folder at root level
        if (self.root_folder and self.current_folder and 
            self.root_folder != self.current_folder.parent and self.root_folder != self.parent_folder):
            self.create_root_level_radio = QRadioButton(
                tr("dialogs.folder_rename_options.create_root_level", 
                   series_name=self.series_name,
                   root_folder=self.root_folder.name)
            )
            self.button_group.addButton(self.create_root_level_radio, 5)
            options_layout.addWidget(self.create_root_level_radio)
        else:
            self.create_root_level_radio = None
        
        layout.addWidget(options_group)
        
        # Preview section
        preview_group = QGroupBox(tr("dialogs.folder_rename_options.preview_title"))
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # Connect radio buttons to preview update
        self.button_group.buttonClicked.connect(self._update_preview)
        
        # Options section
        options_section = QGroupBox(tr("dialogs.folder_rename_options.additional_options"))
        options_section_layout = QVBoxLayout(options_section)
        
        self.cleanup_empty_checkbox = QCheckBox(tr("dialogs.folder_rename_options.cleanup_empty"))
        self.cleanup_empty_checkbox.setChecked(True)
        options_section_layout.addWidget(self.cleanup_empty_checkbox)
        
        layout.addWidget(options_section)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton(tr("ui.buttons.ok"))
        self.ok_btn.clicked.connect(self._accept_dialog)
        self.ok_btn.setDefault(True)
        
        self.cancel_btn = QPushButton(tr("ui.buttons.cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize preview
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview based on selected option."""
        selected_id = self.button_group.checkedId()
        
        if selected_id == 1:  # Rename current folder
            preview_text = tr("dialogs.folder_rename_options.preview_rename_current",
                             old_name=self.current_folder.name if self.current_folder else "N/A",
                             new_name=self.series_name)
        elif selected_id == 2:  # Create at same level
            if self.current_folder:
                target_path = self.current_folder.parent / self.series_name
                preview_text = tr("dialogs.folder_rename_options.preview_create_same",
                                 new_path=str(target_path))
            else:
                preview_text = tr("dialogs.folder_rename_options.preview_none")
        elif selected_id == 3:  # Create subfolder inside current folder
            if self.current_folder:
                target_path = self.current_folder / self.series_name
                preview_text = tr("dialogs.folder_rename_options.preview_create_subfolder",
                                 new_path=str(target_path))
            else:
                preview_text = tr("dialogs.folder_rename_options.preview_none")
        elif selected_id == 4:  # Create at parent level
            if self.parent_folder:
                target_path = self.parent_folder / self.series_name
                preview_text = tr("dialogs.folder_rename_options.preview_create_parent",
                                 new_path=str(target_path))
            else:
                preview_text = tr("dialogs.folder_rename_options.preview_none")
        elif selected_id == 5:  # Create at root level
            if self.root_folder:
                target_path = self.root_folder / self.series_name
                preview_text = tr("dialogs.folder_rename_options.preview_create_root",
                                 new_path=str(target_path))
            else:
                preview_text = tr("dialogs.folder_rename_options.preview_none")
        else:
            preview_text = tr("dialogs.folder_rename_options.preview_none")
        
        self.preview_label.setText(preview_text)
    
    def _accept_dialog(self):
        """Accept the dialog and set result variables."""
        selected_id = self.button_group.checkedId()
        
        if selected_id == 1:  # Rename current folder
            self.selected_option = "rename_current"
            self.target_location = self.current_folder.parent if self.current_folder else None
            self.create_new_folder = False
        elif selected_id == 2:  # Create at same level
            self.selected_option = "create_same_level"
            self.target_location = self.current_folder.parent if self.current_folder else None
            self.create_new_folder = True
        elif selected_id == 3:  # Create subfolder inside current folder
            self.selected_option = "create_subfolder"
            self.target_location = self.current_folder
            self.create_new_folder = True
        elif selected_id == 4:  # Create at parent level
            self.selected_option = "create_parent_level"
            self.target_location = self.parent_folder
            self.create_new_folder = True
        elif selected_id == 5:  # Create at root level
            self.selected_option = "create_root_level"
            self.target_location = self.root_folder
            self.create_new_folder = True
        else:
            QMessageBox.warning(self, tr("messages.errors.error"), 
                              tr("dialogs.folder_rename_options.no_option_selected"))
            return
        
        self.accept()
    
    def get_result(self):
        """Get the selected options."""
        return {
            'option': self.selected_option,
            'target_location': self.target_location,
            'create_new_folder': self.create_new_folder,
            'cleanup_empty': self.cleanup_empty_checkbox.isChecked(),
            'series_name': self.series_name
        }


def show_folder_rename_options(parent=None, current_folder=None, series_name="", 
                              parent_folder=None, root_folder=None):
    """
    Show folder rename options dialog.
    
    Args:
        parent: Parent widget
        current_folder: Current folder path
        series_name: Series name for the new folder
        parent_folder: Parent folder path
        root_folder: Root folder path
        
    Returns:
        dict or None: Selected options or None if cancelled
    """
    dialog = FolderRenameOptionsDialog(
        parent=parent,
        current_folder=current_folder,
        series_name=series_name,
        parent_folder=parent_folder,
        root_folder=root_folder
    )
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_result()
    else:
        return None
