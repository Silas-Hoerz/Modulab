import h5py
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLabel
from PySide6.QtCore import Slot

# Silx Imports
try:
    from silx.gui.hdf5 import Hdf5TreeView
    from silx.gui import qt
    SILX_AVAILABLE = True
except ImportError:
    SILX_AVAILABLE = False

class Hdf5Viewer(QWidget):
    """
    Ein Widget zur Inspektion von HDF5-Dateien nach der Messung.
    Nutzt 'silx', um Struktur, Attribute und Daten (Plot/Table) anzuzeigen.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.h5_file_handle = None # Referenz halten, um später sauber zu schließen

        if not SILX_AVAILABLE:
            self.layout.addWidget(QLabel("Fehler: 'silx' ist nicht installiert.\nBitte 'pip install silx' ausführen."))
            return

        # --- Das Herzstück: Der HDF5 Tree View ---
        self.tree_view = Hdf5TreeView()
        
        # Optionen für bessere Übersicht
        self.tree_view.setSortingEnabled(True) 
        
        # Erlaubt das Kontextmenü (Rechtsklick -> Plot / View Data)
        # Das ist extrem mächtig: Silx bringt eigene Plot-Fenster mit!
        self.tree_view.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)
        
        self.layout.addWidget(self.tree_view)

    @Slot(str)
    def load_file(self, filepath):
        """
        Öffnet eine HDF5-Datei sicher im Read-Only Modus und zeigt sie an.
        Schließt vorherige Dateien automatisch.
        """
        if not SILX_AVAILABLE: return

        # 1. Alte Datei schließen (WICHTIG für File Locking!)
        self.close_file()

        if not filepath or not os.path.exists(filepath):
            # Falls Pfad leer (z.B. Abbruch), nichts tun
            return

        try:
            # 2. Datei explizit mit h5py im Read-Only Modus ('r') öffnen
            # Das verhindert, dass wir versehentlich Daten ändern.
            self.h5_file_handle = h5py.File(filepath, 'r')

            # 3. Dem Model das h5py-Objekt übergeben
            model = self.tree_view.findHdf5TreeModel()
            model.insertH5pyObject(self.h5_file_handle)
            
            # Optional: Alle Knoten aufklappen
            # self.tree_view.expandAll() 
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Öffnen", f"Konnte HDF5 Datei nicht laden:\n{e}")
            self.close_file()

    def close_file(self):
        """
        Entfernt die aktuelle Datei aus der Ansicht und schließt das Handle.
        """
        if not SILX_AVAILABLE: return
        
        # View leeren
        model = self.tree_view.findHdf5TreeModel()
        model.clear()

        # Handle schließen
        if self.h5_file_handle:
            try:
                self.h5_file_handle.close()
            except Exception:
                pass
            self.h5_file_handle = None

    def closeEvent(self, event):
        """
        Wird aufgerufen, wenn das Widget/Fenster zerstört wird.
        Sorgt dafür, dass die Datei freigegeben wird.
        """
        self.close_file()
        super().closeEvent(event)