# core/std_includes.py

"""
Diese Datei dient nur dazu, PyInstaller zu zwingen, diese Bibliotheken
in die EXE aufzunehmen. Sie wird importiert, aber nicht aktiv genutzt.
"""

# 1. Stummschalten von Fehlern (optional, falls Libs fehlen)
try:
    import numpy
    import scipy
    import scipy.signal
    import scipy.optimize
    import scipy.constants
    import pandas
    
    import lmfit
    import sympy
    import sklearn
    
    import matplotlib
    import matplotlib.pyplot
    import seaborn
    
    import openpyxl
    import PIL
    
    import requests
    import yaml
    # pyvisa und pyserial sind oft schon durch deine Manager drin
except ImportError as e:
    print(f"WARNUNG: Standard-Library fehlt beim Build: {e}")

def keep_alive():
    """Dummy Funktion, damit IDEs die Imports nicht wegoptimieren."""
    pass