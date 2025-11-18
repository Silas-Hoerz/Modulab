# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- 1. Silx Ressourcen sammeln ---
silx_datas = collect_data_files('silx')
silx_hidden = collect_submodules('silx')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    
    # --- 2. Daten ---
    # WICHTIG: Wir nutzen das '+' Zeichen, um die Listen zu verbinden
    datas=[
        ('resources', 'resources'), 
        ('docs', 'docs')
    ] + silx_datas,  

    # --- 3. Versteckte Imports ---
    # Auch hier: '+' zum Verbinden der Listen
    hiddenimports=[
        'seabreeze.backends.cseabreeze',
        'scipy.special._ufuncs_cxx',
        'scipy.linalg.cython_blas',
        'scipy.linalg.cython_lapack',
        'pandas._libs.tslibs.base', 
        'pandas._libs.tslibs.np_datetime',
        'matplotlib.backends.backend_qtagg',
        'sklearn.neighbors._partition_nodes',
    ] + silx_hidden,

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# --- 4. EXE (Starter) ---
exe = EXE(
    pyz,
    a.scripts,
    [], 
    exclude_binaries=True,
    name='Modulab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Setze auf True für Debugging (Fehlermeldungen sehen)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\logo.ico'],
)

# --- 5. COLLECT (Ordner-Modus) ---
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Modulab',
)