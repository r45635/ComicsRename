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
    (str(spec_dir / 'qt.conf'), '.'),
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
    'python_dotenv',
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
        icon=str(spec_dir / 'icons' / 'comicsrename.ico'),
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
        icon=str(spec_dir / 'icons' / 'comicsrename.ico'),
        bundle_identifier='com.comicsrename.app',
        version='3.2.0',
        info_plist={
            'CFBundleName': 'ComicsRename',
            'CFBundleDisplayName': 'ComicsRename',
            'CFBundleIdentifier': 'com.comicsrename.app',
            'CFBundleVersion': '3.2.0',
            'CFBundleShortVersionString': '3.2.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
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
