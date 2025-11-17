# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath("../"))

from main import __version__, __title__

project = __title__
copyright = f'{date.today().year}, Silas Hörz'
author = 'Silas Hörz'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # 1. AUTODOC: Holt Dokumentation automatisch aus Docstrings
    'sphinx.ext.autodoc',
    
    # 2. NAPOLEON: Der "Übersetzer" für Google & NumPy Style
    'sphinx.ext.napoleon',
    
    # 3. VIEWCODE: Fügt Links zum Quellcode in der Doku hinzu
    'sphinx.ext.viewcode',

    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False # Setze auf True, wenn du NumPy-Stil verwendest
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_warnings = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
