# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the current working directory since __file__ might not be available
spec_dir = Path.cwd()

block_cipher = None

# Define data files to include
datas = [
    (str(spec_dir / 'translations'), 'translations'),
    (str(spec_dir / 'icons'), 'icons'),
]

# Include only existing data files
datas = [(src, dst) for src, dst in datas if os.path.exists(src.split(',')[0] if ',' in src else src)]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'requests',
    'bs4',
    'lxml',
    'lxml.etree',
    'lxml.html',
    'dotenv',
    'json',
    'urllib3',
]

a = Analysis(
    ['main.py'],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific configurations
if sys.platform == 'win32':
    # Windows executable
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
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(spec_dir / 'icons' / 'comicsrename.ico'),
    )

elif sys.platform == 'darwin':
    # macOS app bundle
    # Try to use PNG icon and let Pillow convert it
    icon_path = None
    possible_icons = [
        str(spec_dir / 'icons' / 'comicsrename.icns'),
        str(spec_dir / 'icons' / 'comicsrename_1024x1024.png'),
        str(spec_dir / 'icons' / 'comicsrename_512x512.png'),
        str(spec_dir / 'icons' / 'comicsrename_256x256.png'),
    ]
    for icon in possible_icons:
        if os.path.exists(icon):
            icon_path = icon
            break
    
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='ComicsRename',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='ComicsRename',
    )
    
    app = BUNDLE(
        coll,
        name='ComicsRename.app',
        icon=icon_path,
        bundle_identifier='com.comicsrename.app',
        version='3.4.2',
        info_plist={
            'CFBundleName': 'ComicsRename',
            'CFBundleDisplayName': 'ComicsRename',
            'CFBundleIdentifier': 'com.comicsrename.app',
            'CFBundleVersion': '3.4.2',
            'CFBundleShortVersionString': '3.4.2',
            'CFBundleExecutable': 'ComicsRename',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'NSPrincipalClass': 'NSApplication',
            'NSAppleEventsUsageDescription': 'ComicsRename needs access to system events for file operations.',
            'NSDocumentsFolderUsageDescription': 'ComicsRename needs access to your documents to rename comic files.',
            'NSDesktopFolderUsageDescription': 'ComicsRename needs access to your desktop to rename comic files.',
            'NSDownloadsFolderUsageDescription': 'ComicsRename needs access to your downloads folder to rename comic files.',
            'NSRemovableVolumesUsageDescription': 'ComicsRename needs access to removable volumes to rename comic files.',
            'LSMinimumSystemVersion': '10.14',
            'LSApplicationCategoryType': 'public.app-category.utilities',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeExtensions': ['cbr', 'cbz', 'pdf'],
                    'CFBundleTypeName': 'Comic Book Archive',
                    'CFBundleTypeRole': 'Editor',
                    'LSHandlerRank': 'Alternate',
                }
            ],
        },
    )

else:
    # Linux executable
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
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
