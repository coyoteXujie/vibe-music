# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

BASE = os.path.abspath('.')
CONDA = 'D:\\miniconda3\\envs\\vibe-music'
CONDA_BIN = os.path.join(CONDA, 'Library', 'bin')

a = Analysis(
    ['app.py'],
    pathex=[BASE],
    binaries=[
        (os.path.join(CONDA_BIN, 'libssl-3-x64.dll'), '.'),
        (os.path.join(CONDA_BIN, 'libcrypto-3-x64.dll'), '.'),
        (os.path.join(CONDA_BIN, 'liblzma.dll'), '.'),
        (os.path.join(CONDA_BIN, 'libbz2.dll'), '.'),
        (os.path.join(CONDA_BIN, 'ffi.dll'), '.'),
        (os.path.join(CONDA_BIN, 'libexpat.dll'), '.'),
    ],
    datas=[
        (os.path.join(BASE, 'ui', 'index.html'), 'ui'),
        (os.path.join(BASE, 'ui', 'fonts'), 'ui/fonts'),
    ],
    hiddenimports=[
        'flask',
        'webview',
        'requests',
        'webview.platforms.winforms',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VibeMusic',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VibeMusic',
)
