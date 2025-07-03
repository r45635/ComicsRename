#!/usr/bin/env python3
"""
Test script to validate the ComicsRename application health and basic functionality.
"""

import sys
import os
import subprocess

def test_python_version():
    """Test if Python version is compatible"""
    print("🐍 Testing Python Version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        ('PySide6', 'PySide6'),
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('python-dotenv', 'dotenv'),
        ('pillow', 'PIL')
    ]
    
    all_ok = True
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name} - Installed")
        except ImportError:
            print(f"   ❌ {package_name} - Missing")
            all_ok = False
    
    return all_ok

def test_imports():
    """Test if main application modules can be imported"""
    print("\n🔧 Testing Module Imports...")
    
    modules = [
        ('i18n', 'Internationalization'),
        ('utils', 'Utilities'),
        ('bdgest_scraper_api', 'BDGest API'),
        ('comicVine_scraper_api', 'ComicVine API'),
        ('comicsFileRenamer_v3', 'Main Application')
    ]
    
    all_ok = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"   ✅ {description} ({module}) - OK")
        except Exception as e:
            print(f"   ❌ {description} ({module}) - Error: {str(e)}")
            all_ok = False
    
    return all_ok

def test_ui_modules():
    """Test if UI modules can be imported"""
    print("\n🎨 Testing UI Modules...")
    
    try:
        sys.path.insert(0, 'ui')
        from ui.quick_view import QuickViewDialog
        print("   ✅ QuickView Dialog - OK")
        return True
    except Exception as e:
        print(f"   ❌ QuickView Dialog - Error: {str(e)}")
        return False

def test_translations():
    """Test if translation files are accessible"""
    print("\n🌍 Testing Translation Files...")
    
    translation_files = [
        'translations/en.json',
        'translations/fr.json'
    ]
    
    all_ok = True
    for file_path in translation_files:
        if os.path.exists(file_path):
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ {file_path} - Valid JSON ({len(data)} keys)")
            except Exception as e:
                print(f"   ❌ {file_path} - Invalid: {str(e)}")
                all_ok = False
        else:
            print(f"   ❌ {file_path} - Missing")
            all_ok = False
    
    return all_ok

def test_icon_files():
    """Test if icon files exist"""
    print("\n🎭 Testing Icon Files...")
    
    icon_files = [
        'icons/comicsrename.ico',
        'icons/comicsrename_64x64.png',
        'icons/comicsrename_32x32.png'
    ]
    
    found_count = 0
    for icon_path in icon_files:
        if os.path.exists(icon_path):
            print(f"   ✅ {icon_path} - Found")
            found_count += 1
        else:
            print(f"   ⚠️  {icon_path} - Missing")
    
    if found_count > 0:
        print(f"   ✅ Icons - {found_count}/{len(icon_files)} available")
        return True
    else:
        print("   ❌ Icons - None found")
        return False

def main():
    """Run all health checks"""
    print("🔍 ComicsRename Application Health Check")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_imports,
        test_ui_modules,
        test_translations,
        test_icon_files
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"   🎉 All tests passed! ({passed}/{total})")
        print("   ✅ Application appears to be in good health")
        return 0
    else:
        print(f"   ⚠️  {passed}/{total} tests passed")
        print("   🔧 Some issues detected - see details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
