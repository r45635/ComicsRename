#!/usr/bin/env python3
"""
Test script to verify bilingual functionality in ComicsRename
"""

import sys
import os

# Add the current directory to sys.path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n import tr, set_language, get_current_language, get_supported_languages

def test_language_switching():
    """Test the language switching functionality"""
    print("ComicsRename Bilingual Test")
    print("=" * 40)
    
    # Test supported languages
    languages = get_supported_languages()
    print(f"Supported languages: {languages}")
    
    # Test default language
    current = get_current_language()
    print(f"Current language: {current}")
    
    # Test English translations
    print("\n--- Testing English translations ---")
    set_language('en')
    print(f"Language set to: {get_current_language()}")
    print(f"App title: {tr('app.title')}")
    print(f"Browse button: {tr('ui.buttons.browse')}")
    print(f"Error message: {tr('messages.errors.error')}")
    print(f"File not exists: {tr('messages.errors.file_not_exists', path='/test/path')}")
    
    # Test French translations
    print("\n--- Testing French translations ---")
    set_language('fr')
    print(f"Language set to: {get_current_language()}")
    print(f"App title: {tr('app.title')}")
    print(f"Browse button: {tr('ui.buttons.browse')}")
    print(f"Error message: {tr('messages.errors.error')}")
    print(f"File not exists: {tr('messages.errors.file_not_exists', path='/test/path')}")
    
    # Test invalid key
    print("\n--- Testing invalid key ---")
    print(f"Invalid key: {tr('invalid.key.that.does.not.exist')}")
    
    # Test missing parameter
    print("\n--- Testing missing parameter ---")
    print(f"Missing param: {tr('messages.errors.file_not_exists')}")
    
    print("\n✅ Bilingual test completed successfully!")

if __name__ == "__main__":
    test_language_switching()
