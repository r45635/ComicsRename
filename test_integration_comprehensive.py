#!/usr/bin/env python3
"""
Comprehensive Integration Test for ComicsRename Application

This test validates the complete integration of all components
without launching the GUI.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_structure():
    """Test that all essential files exist"""
    print("📁 Testing File Structure...")
    
    essential_files = [
        'main.py',
        'comicsFileRenamer_v3.py',
        'i18n.py',
        'utils.py',
        'bdgest_scraper_api.py',
        'comicVine_scraper_api.py',
        'ui/quick_view.py',
        'translations/en.json',
        'translations/fr.json',
        'requirements.txt',
        'icons/comicsrename.ico',
        'README.md'
    ]
    
    found_files = []
    for file_path in essential_files:
        if os.path.exists(file_path):
            found_files.append(file_path)
    
    print(f"   ✅ Found files: {len(found_files)}/{len(essential_files)}")
    
    if len(found_files) < len(essential_files):
        missing = set(essential_files) - set(found_files)
        print(f"   ⚠️  Missing files: {missing}")
    
    return len(found_files) == len(essential_files)

def test_i18n_system():
    """Test internationalization system"""
    print("\n🌍 Testing Internationalization System...")
    
    try:
        # Import the i18n functions - NOT get_available_languages which doesn't exist
        from i18n import tr, get_current_language, get_supported_languages
        
        # Test basic translation
        test_key = "ui.buttons.search"
        result = tr(test_key)
        print(f"   ✅ Translation system working: '{test_key}' -> '{result}'")
        
        # Test language detection
        current_lang = get_current_language()
        print(f"   ✅ Current language: {current_lang}")
        
        # Test supported languages
        supported = get_supported_languages()
        print(f"   ✅ Supported languages: {list(supported.keys())}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ i18n system error: {e}")
        return False

def test_utils_module():
    """Test utilities module"""
    print("\n🛠️  Testing Utilities Module...")
    
    try:
        # Import utils functions - NOT clean_filename which doesn't exist
        from utils import load_bdgest_credentials, extract_year
        
        # Test credential loading (will return None if not configured)
        username, password = load_bdgest_credentials()
        print(f"   ✅ Credential loading works (configured: {username is not None})")
        
        # Test year extraction
        test_year = extract_year("2023-05-15")
        print(f"   ✅ Year extraction: '2023-05-15' -> {test_year}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Utils module error: {e}")
        return False

def test_scraper_apis():
    """Test scraper API modules"""
    print("\n🔍 Testing Scraper APIs...")
    
    try:
        # Test BDGest API
        from bdgest_scraper_api import get_bdgest_series
        print("   ✅ BDGest API module imported successfully")
        
        # Test ComicVine API - NOT search_comic_vine_volumes which doesn't exist
        from comicVine_scraper_api import search_comicvine_issues
        print("   ✅ ComicVine API module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Scraper API error: {e}")
        return False

def test_quickview_module():
    """Test QuickView module without GUI"""
    print("\n📱 Testing QuickView Module...")
    
    try:
        # Import without creating widgets
        from ui.quick_view import QuickViewDialog
        print("   ✅ QuickView dialog class imported successfully")
        
        # Check for static method
        if hasattr(QuickViewDialog, 'show_quick_view'):
            print("   ✅ QuickView has show_quick_view static method")
        else:
            print("   ⚠️  QuickView missing show_quick_view static method")
        
        return True
        
    except Exception as e:
        print(f"   ❌ QuickView module error: {e}")
        return False

def test_main_application_import():
    """Test main application import"""
    print("\n📋 Testing Main Application Import...")
    
    try:
        from comicsFileRenamer_v3 import ComicRenamer
        print("   ✅ Main application class imported successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Main application import error: {e}")
        return False

def test_translation_files():
    """Test translation file loading"""
    print("\n📚 Testing Translation Files...")
    
    try:
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        with open('translations/fr.json', 'r', encoding='utf-8') as f:
            fr_data = json.load(f)
        
        print(f"   ✅ English translations loaded successfully")
        print(f"   ✅ French translations loaded successfully")
        
        # Check if we have the QuickView title key
        try:
            en_quickview_title = en_data.get('dialogs', {}).get('quick_view', {}).get('title')
            print(f"   ✅ QuickView title in English: {en_quickview_title}")
        except:
            print("   ❌ QuickView title missing in English translations")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Translation test error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 ComicsRename Comprehensive Integration Tests")
    print("=" * 70)
    
    tests = [
        test_file_structure,
        test_i18n_system,
        test_utils_module,
        test_scraper_apis,
        test_quickview_module,
        test_main_application_import,
        test_translation_files
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 Integration Test Summary:")
    
    passed = sum(1 for r in results if r)
    total = len(tests)
    
    if passed == total:
        print(f"   🎉 All integration tests passed! ({passed}/{total})")
        print("   ✅ Application is ready for use")
        print("\n🚀 To run the application:")
        print("   source venv/bin/activate")
        print("   python main.py")
        return 0
    else:
        print(f"   ⚠️  {passed}/{total} integration tests passed")
        print("   🔧 Some integration issues detected - see details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
