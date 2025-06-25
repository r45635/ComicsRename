#!/usr/bin/env python3
"""
ComicsRename Installation Validator

This script validates that all dependencies and components are properly installed
and configured for the ComicsRename application.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    dependencies = [
        ("PySide6", "PySide6"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("python-dotenv", "dotenv")
    ]
    
    all_ok = True
    for package_name, import_name in dependencies:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'installed')
            print(f"   ✅ {package_name}: {version}")
        except ImportError:
            print(f"   ❌ {package_name}: Not installed")
            all_ok = False
    
    return all_ok

def check_project_files():
    """Check if essential project files exist"""
    print("\n📁 Checking project files...")
    
    essential_files = [
        "main.py",
        "comicsFileRenamer_v3.py",
        "bdgest_scraper_api.py",
        "comicVine_scraper_api.py",
        "utils.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_ok = True
    for file_name in essential_files:
        if Path(file_name).exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name}: Missing")
            all_ok = False
    
    return all_ok

def check_imports():
    """Test importing main application modules"""
    print("\n🔧 Testing module imports...")
    
    modules = [
        ("utils", "Utility functions"),
        ("bdgest_scraper_api", "BDGest API"),
        ("comicVine_scraper_api", "ComicVine API"),
        ("comicsFileRenamer_v3", "Main application")
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"   ✅ {module_name}: {description}")
            
            # Special check for main application class
            if module_name == "comicsFileRenamer_v3":
                if hasattr(module, 'ComicRenamer'):
                    print(f"   ✅ ComicRenamer class found")
                else:
                    print(f"   ❌ ComicRenamer class not found")
                    all_ok = False
                    
        except ImportError as e:
            print(f"   ❌ {module_name}: {description} - {e}")
            all_ok = False
    
    return all_ok

def check_configuration():
    """Check configuration files and environment"""
    print("\n⚙️  Checking configuration...")
    
    all_ok = True
    
    # Check .env file
    if Path(".env").exists():
        print("   ✅ .env file exists")
        
        # Check if it has content
        try:
            with open(".env", "r") as f:
                content = f.read().strip()
                if content:
                    print("   ✅ .env file has content")
                else:
                    print("   ⚠️  .env file is empty")
        except Exception as e:
            print(f"   ❌ Error reading .env file: {e}")
            all_ok = False
    else:
        print("   ⚠️  .env file not found (optional)")
    
    # Check .env.example
    if Path(".env.example").exists():
        print("   ✅ .env.example template exists")
    else:
        print("   ❌ .env.example template missing")
        all_ok = False
    
    # Check setup_credentials.py
    if Path("setup_credentials.py").exists():
        print("   ✅ setup_credentials.py exists")
    else:
        print("   ❌ setup_credentials.py missing")
        all_ok = False
    
    return all_ok

def check_gui_availability():
    """Check if GUI components can be loaded"""
    print("\n🖥️  Checking GUI availability...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap
        
        # Test creating a QApplication (don't show anything)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        print("   ✅ PySide6 GUI components available")
        return True
        
    except Exception as e:
        print(f"   ❌ GUI components unavailable: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 ComicsRename Installation Validator")
    print("=" * 40)
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project files", check_project_files),
        ("Module imports", check_imports),
        ("Configuration", check_configuration),
        ("GUI availability", check_gui_availability)
    ]
    
    all_passed = True
    failed_checks = []
    
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            failed_checks.append(check_name)
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! ComicsRename is ready to use.")
        print("\nTo start the application, run:")
        print("   python main.py")
        print("\nOr use the launcher scripts:")
        print("   ./launch.sh       (macOS/Linux)")
        print("   launch.bat        (Windows)")
    else:
        print(f"❌ {len(failed_checks)} check(s) failed:")
        for failed in failed_checks:
            print(f"   • {failed}")
        print("\nPlease fix the issues above.")
        print("\nFor installation help, see:")
        print("   README.md")
        print("   DEVELOPMENT.md")
        
        if not Path("requirements.txt").exists():
            print("\n💡 If dependencies are missing, try:")
            print("   pip install PySide6 requests beautifulsoup4 lxml python-dotenv")
        else:
            print("\n💡 If dependencies are missing, try:")
            print("   pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
