"""
UI components for ComicsRename application.

This package contains custom widgets, tables, and dialogs used in the
ComicsRename application.
"""

from .tables import FileTable, AlbumTable
from .dialogs import SettingsDialog
from .quick_view import QuickViewDialog

__all__ = [
    'DroppableLineEdit', 
    'EditableFolderLineEdit',
    'FileTable', 
    'AlbumTable',
    'SettingsDialog',
    'QuickViewDialog'
]
