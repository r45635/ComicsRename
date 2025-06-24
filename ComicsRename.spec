# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for ComicsRename
"""

import os
import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include translation files
        ('translations/*.json', 'translations'),
        # Include icons
        ('icons/*', 'icons'),
        # Include any config files
        ('*.conf', '.'),
    ],
    hiddenimports=[
        # PySide6 modules that might not be auto-detected
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        # Other modules
        'requests',
        'bs4',
        'lxml',
        # Project modules
        'utils',
        'bdgest_scraper_api',
        'comicVine_scraper_api',
        'i18n',
        'comicsFileRenamer_v3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'pygame',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ComicsRename',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debug mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/comicsrename.ico' if os.path.exists('icons/comicsrename.ico') else None,
)

# macOS app bundle configuration
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='ComicsRename.app',
        icon='icons/comicsrename.ico' if os.path.exists('icons/comicsrename.ico') else None,
        bundle_identifier='com.github.r45635.comicsrename',
        info_plist={
            'CFBundleName': 'ComicsRename',
            'CFBundleDisplayName': 'ComicsRename',
            'CFBundleIdentifier': 'com.github.r45635.comicsrename',
            'CFBundleVersion': '3.1.0',
            'CFBundleShortVersionString': '3.1.0',
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundleExecutable': 'ComicsRename',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSMinimumSystemVersion': '10.14.0',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'PDF Document',
                    'CFBundleTypeExtensions': ['pdf'],
                    'CFBundleTypeRole': 'Viewer',
                    'LSHandlerRank': 'Alternate',
                }
            ],
        },
    )
