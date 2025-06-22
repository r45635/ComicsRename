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

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the ComicsRename application"""
    try:
        # Import the main application class
        from comicsFileRenamer_v3 import ComicRenamer
        
        # Create the QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("ComicsRename")
        app.setApplicationVersion("3.0")
        app.setOrganizationName("ComicsRename")
        app.setOrganizationDomain("github.com")
        
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