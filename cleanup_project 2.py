#!/usr/bin/env python3
"""
Cleanup script for ComicsRename project
Organizes files into proper directories and removes unnecessary files
"""

import os
import shutil
import pathlib

def main():
    """Clean up and reorganize the ComicsRename project"""
    
    project_root = pathlib.Path(__file__).parent
    
    print("🧹 Cleaning up ComicsRename project...")
    
    # Files to keep in root
    keep_in_root = {
        'main.py',
        'comicsFileRenamer_v3.py', 
        'bdgest_scraper_api.py',
        'comicVine_scraper_api.py',
        'utils.py',
        'i18n.py',
        'requirements.txt',
        'pyproject.toml',
        'ComicsRename.spec',
        'LICENSE',
        'README.md',
        'QUICKSTART.md',
        '.gitignore',
        '.env.example'
    }
    
    # Documentation files to move to docs/
    doc_files = [
        'CLEANUP_SUMMARY.md',
        'MODULARIZATION_COMPLETE.md', 
        'PAN_LEFT_CLICK_UPDATE.md',
        'QUICKVIEW_FINAL_SUMMARY.md',
        'QUICKVIEW_FIXES_SUMMARY.md', 
        'QUICKVIEW_INTEGRATION_SUMMARY.md',
        'QUICKVIEW_VERIFICATION_GUIDE.md',
        'QUICK_VIEW_PAN_SUMMARY.md',
        'README_ENHANCEMENT_SUMMARY.md',
        'RELEASE_v3.3.0.md',
        'RELEASE_v3.3.2.md'
    ]
    
    # Test files to move to tests/
    test_files = [
        'test_application_health.py',
        'test_delete_file.py',
        'test_integration_comprehensive.py', 
        'test_quick_view_pan.py',
        'test_quickview_improvements.py',
        'test_quickview_integration.py',
        'test_quickview_title_fixes.py',
        'test_quickview_version.py',
        'verify_quickview_integration.py',
        'debug_quickview.py'
    ]
    
    # Files to remove (temporary/outdated)
    files_to_remove = [
        'comicsrename.egg-info',
        '__pycache__',
        '.venv',
        'venv'
    ]
    
    # 1. Move documentation files
    docs_dir = project_root / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    for doc_file in doc_files:
        src = project_root / doc_file
        if src.exists():
            dst = docs_dir / doc_file
            print(f"📄 Moving {doc_file} to docs/")
            shutil.move(str(src), str(dst))
    
    # 2. Move test files
    tests_dir = project_root / 'tests'
    tests_dir.mkdir(exist_ok=True)
    
    for test_file in test_files:
        src = project_root / test_file
        if src.exists():
            dst = tests_dir / test_file
            print(f"🧪 Moving {test_file} to tests/")
            shutil.move(str(src), str(dst))
    
    # 3. Remove temporary files and directories
    for item in files_to_remove:
        path = project_root / item
        if path.exists():
            if path.is_dir():
                print(f"🗑️  Removing directory {item}/")
                shutil.rmtree(str(path))
            else:
                print(f"🗑️  Removing file {item}")
                path.unlink()
    
    # 4. Create proper src/ structure for future organization
    src_dir = project_root / 'src'
    if not src_dir.exists():
        src_dir.mkdir()
        print("📁 Created src/ directory for future code organization")
    
    # 5. Clean up any remaining __pycache__ directories
    for pycache in project_root.rglob('__pycache__'):
        if pycache.is_dir():
            print(f"🗑️  Removing {pycache}")
            shutil.rmtree(str(pycache))
    
    # 6. Clean up any .pyc files
    for pyc_file in project_root.rglob('*.pyc'):
        print(f"🗑️  Removing {pyc_file}")
        pyc_file.unlink()
    
    print("\n✅ Project cleanup completed!")
    print("\n📁 Current structure:")
    print("├── main.py (entry point)")
    print("├── comicsFileRenamer_v3.py (main application)")
    print("├── *_scraper_api.py (API modules)")
    print("├── utils.py, i18n.py (utilities)")
    print("├── requirements.txt, pyproject.toml (dependencies)")
    print("├── docs/ (documentation)")
    print("├── tests/ (test files)")
    print("├── ui/ (UI components)")
    print("├── translations/ (i18n files)")
    print("├── icons/ (application icons)")
    print("└── dev-tools/ (development utilities)")

if __name__ == "__main__":
    main()
