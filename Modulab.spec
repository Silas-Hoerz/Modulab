# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

# This file generates a SINGLE ONE-FILE EXE.
# No scientific libraries are bundled (as per your request).

# --- FIX FÜR SILX FEHLER ---
# Silx benötigt Icons und interne Daten (z.B. 'process-working'), die PyInstaller
# standardmäßig übersieht. Wir sammeln diese hier manuell ein.
silx_datas = collect_data_files('silx')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    
    # Data files required by the core application + SILX Data
    datas=[
        ('resources', 'resources'), 
        ('docs', 'docs')
    ] + silx_datas,

    # Hidden imports for libraries that are bundled with the app
    # h5py und silx benötigen oft explizite hiddenimports
    hiddenimports=[
        'seabreeze.backends.cseabreeze',
        'silx',
        'silx.gui.qt',
        'h5py',
        'h5py.defs',
        'h5py.utils',
        'h5py.h5ac',
        'h5py._proxy',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Wir schließen PyQt5/6 aus, da du im Code PySide6 nutzt.
    # Stelle sicher, dass PySide6 installiert ist.
    excludes=['PyQt5', 'tkinter'], 
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- EXE (One-File Build) ---
# Um eine einzelne Datei zu erhalten, müssen a.binaries, a.zipfiles und a.datas
# hier übergeben werden und exclude_binaries darf NICHT True sein.

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,   # WICHTIG: Binaries müssen hier rein für One-File
    a.zipfiles,   # WICHTIG: Zipfiles müssen hier rein für One-File
    a.datas,      # WICHTIG: Daten müssen hier rein für One-File
    [],
    name='Modulab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Setze dies auf True, falls du Fehler beim Start sehen willst
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/logo.ico',
)