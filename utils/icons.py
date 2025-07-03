"""
Centralized icon management for ComicsRename application.
"""
import os
from PySide6.QtGui import QIcon


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


def get_icon_path(icon_name):
    """Get full path to a specific icon file"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, 'icons', icon_name)
