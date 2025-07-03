#!/usr/bin/env python3
"""
ComicsRename - Main Entry Point

A powerful GUI application for organizing and renaming comic book files
using metadata from BDGest and ComicVine.

Usage:
    python main.py

Requirements:
    See requirements.txt for dependencies.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Dynamically set the Qt plugin path
if hasattr(sys, '_MEIPASS'):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'Qt', 'plugins')
else:
    import PySide6
    plugin_path = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins")

QCoreApplication.addLibraryPath(plugin_path)

def main():
    """Main entry point for the ComicsRename application"""
    try:
        # Import the main application class
        from comicsFileRenamer_v3 import ComicRenamer
        
        # Initialize i18n system
        from i18n import get_current_language
        
        # Create the QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("ComicsRename")
        app.setApplicationVersion("3.4.0")
        app.setOrganizationName("ComicsRename")
        app.setOrganizationDomain("github.com")
        
        # Set application icon
        try:
            from utils.icons import get_app_icon
            app_icon = get_app_icon()
            if not app_icon.isNull():
                app.setWindowIcon(app_icon)
        except ImportError:
            # Fallback if utils.icons is not available
            icon_paths = [
                os.path.join(os.path.dirname(__file__), 'icons', 'comicsrename.ico'),
                os.path.join(os.path.dirname(__file__), 'icons', 'comicsrename_64x64.png'),
                os.path.join(os.path.dirname(__file__), 'icons', 'comicsrename_32x32.png'),
                os.path.join(os.path.dirname(__file__), 'icons', 'icon.ico')
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    app.setWindowIcon(QIcon(icon_path))
                    break
        
        # Create and show the main window
        window = ComicRenamer()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error: Missing dependencies. Please install requirements:")
        print("pip install -r requirements.txt")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()