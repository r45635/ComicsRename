#!/usr/bin/env python3
"""
Test script to verify that the threading fix prevents GUI freezing during BDGest searches.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def test_search_responsiveness():
    """Test that BDGest search doesn't freeze the GUI"""
    
    print("Testing search threading implementation...")
    
    # Import main application
    from comicsFileRenamer_v3 import ComicRenamer
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = ComicRenamer()
    window.show()
    
    # Set BDGest as provider
    bdgest_idx = window.source_combo.findText('BDGest')
    if bdgest_idx >= 0:
        window.source_combo.setCurrentIndex(bdgest_idx)
        window._source = 'BDGest'
    
    # Set a search term
    window.search_bar.setText("asterix")
    
    print("1. Starting BDGest search with threading...")
    print("   - The GUI should remain responsive")
    print("   - You should see progress messages")
    print("   - Search should not freeze the interface")
    
    # Trigger search
    window._search()
    
    # Create a timer to test GUI responsiveness
    def check_responsiveness():
        print("   ✓ GUI is responsive - timer is working")
    
    response_timer = QTimer()
    response_timer.timeout.connect(check_responsiveness)
    response_timer.start(1000)  # Check every second
    
    # Show instructions
    print("\nInstructions:")
    print("- Watch for progress messages in the detail area")
    print("- Try clicking the cancel button during search")
    print("- Try pressing Escape to cancel")
    print("- The timer should print messages every second (proving GUI responsiveness)")
    print("- Close the window when done testing")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_search_responsiveness()
