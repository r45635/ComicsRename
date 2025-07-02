"""
UI components for ComicsRename application.

This package contains custom widgets, tables, and dialogs used in the
ComicsRename application.
"""

from .widgets import DroppableLineEdit, EditableFolderLineEdit
from .tables import FileTable, AlbumTable
from .dialogs import SettingsDialog, QuickViewDialog

__all__ = [
    'DroppableLineEdit', 
    'EditableFolderLineEdit',
    'FileTable', 
    'AlbumTable',
    'SettingsDialog',
    'QuickViewDialog'
]
