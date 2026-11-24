# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for compiling FurryPersonaStudio3D.exe with bundled assets."""

block_cipher = None

a = Analysis(
    ['src/furry_persona_studio.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets/audio/*.wav', 'assets/audio'),
        ('assets/icons/*', 'assets/icons'),
        ('assets/palettes/*.json', 'assets/palettes'),
        ('assets/presets/*.json', 'assets/presets'),
    ],
    hiddenimports=['persona_engine', 'style_renderer', 'audio_chaos'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FurryPersonaStudio3D',
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
    icon='assets/icons/app_icon.ico',
)
