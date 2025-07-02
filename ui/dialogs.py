"""
Dialog windows for ComicsRename application.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QCheckBox, QLineEdit, QDialogButtonBox, QMessageBox,
    QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton, QSlider, QFileDialog
)
from PySide6.QtCore import QSettings, Qt, QPoint, QPointF, QSizeF
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QIcon, QImage, QPainter

# Import internationalization system  
from i18n import tr, get_supported_languages, get_current_language, set_language

# Import the extracted QuickView components
from .quick_view import QuickViewDialog


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
