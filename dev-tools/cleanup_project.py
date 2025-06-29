#!/usr/bin/env python3
"""
Project Cleanup Script for ComicsRename

This script removes build artifacts, cache files, and temporary files
to keep the project directory clean.
"""

import os
import shutil
import glob
from pathlib import Path

def clean_python_cache():
    """Remove Python cache files and directories"""
    print("🧹 Cleaning Python cache files...")
    
    # Remove __pycache__ directories
    for pycache_dir in glob.glob("**/__pycache__", recursive=True):
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir)
            print(f"   Removed: {pycache_dir}")
    
    # Remove .pyc files
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"   Removed: {pyc_file}")

def clean_build_artifacts():
    """Remove build and distribution artifacts"""
    print("🏗️  Cleaning build artifacts...")
    
    artifacts = ['build', 'dist', '*.egg-info', '.pytest_cache']
    
    for pattern in artifacts:
        for item in glob.glob(pattern):
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"   Removed directory: {item}")
                else:
                    os.remove(item)
                    print(f"   Removed file: {item}")

def clean_macos_files():
    """Remove macOS specific files"""
    print("🍎 Cleaning macOS files...")
    
    for ds_store in glob.glob("**/.DS_Store", recursive=True):
        if os.path.exists(ds_store):
            os.remove(ds_store)
            print(f"   Removed: {ds_store}")

def clean_editor_files():
    """Remove editor specific files"""
    print("📝 Cleaning editor files...")
    
    editor_patterns = [
        "**/.vscode/settings.json",
        "**/*~",
        "**/*.swp",
        "**/*.swo"
    ]
    
    for pattern in editor_patterns:
        for item in glob.glob(pattern, recursive=True):
            if os.path.exists(item):
                os.remove(item)
                print(f"   Removed: {item}")

def main():
    """Main cleanup function"""
    print("🧹 ComicsRename Project Cleanup")
    print("=" * 40)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"Working in: {os.getcwd()}")
    print()
    
    clean_python_cache()
    clean_build_artifacts()
    clean_macos_files()
    clean_editor_files()
    
    print()
    print("✅ Project cleanup completed!")
    print()
    print("💡 To keep your project clean:")
    print("   • Run this script regularly")
    print("   • Make sure .gitignore is up to date")
    print("   • Avoid committing temporary files")

if __name__ == "__main__":
    main()
