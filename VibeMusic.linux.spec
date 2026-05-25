# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

BASE = os.path.abspath('.')

a = Analysis(
    ['app.py'],
    pathex=[BASE],
    binaries=[],
    datas=[
        (os.path.join(BASE, 'ui', 'index.html'), 'ui'),
        (os.path.join(BASE, 'ui', 'fonts'), 'ui/fonts'),
        (os.path.join(BASE, 'musicapi'), 'musicapi'),
    ],
    hiddenimports=[
        'flask',
        'webview',
        'requests',
        'webview.platforms.gtk',
        'musicapi',
        'musicapi.musicapi',
        'musicapi.app',
        'Crypto',
        'Crypto.Cipher',
        'Crypto.Cipher.AES',
        'Crypto.Util',
        'Crypto.Util.Padding',
        'execjs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
