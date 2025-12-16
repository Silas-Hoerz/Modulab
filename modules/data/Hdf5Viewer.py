# modules/data/Hdf5Viewer.py
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
        self.placeholder_label = QLabel("Keine HDF5 Datei geladen.")
        self.placeholder_label.setVisible(False)

        if not SILX_AVAILABLE:
            self.layout.addWidget(QLabel("Fehler: 'silx' ist nicht installiert.\nBitte 'pip install silx' ausführen."))
            return

        # --- Das Herzstück: Der HDF5 Tree View ---
        self.tree_view = Hdf5TreeView()
        self.tree_view.setSortingEnabled(True) 
        self.tree_view.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)
        
        self.layout.addWidget(self.tree_view)
        self.layout.addWidget(self.placeholder_label)

    @Slot(str)
    def load_file(self, filepath):
        """
        Öffnet eine HDF5-Datei sicher im Read-Only Modus und zeigt sie an.
        Ignoriert CSV Dateien.
        """
        if not SILX_AVAILABLE: return

        # 1. Alte Datei schließen
        self.close_file()

        if not filepath or not os.path.exists(filepath):
            return

        # --- FIX: Prüfen ob es überhaupt HDF5 ist ---
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in ['.h5', '.hdf5', '.nxs', '.nx']:
            # Es ist eine CSV oder Textdatei -> Viewer leeren, aber keinen Fehler werfen!
            self.tree_view.setVisible(False)
            self.placeholder_label.setText(f"Vorschau für {ext}-Dateien nicht verfügbar.\n(Daten wurden erfolgreich gespeichert)")
            self.placeholder_label.setVisible(True)
            return
        
        # Es ist eine H5 Datei -> Anzeigen
        self.tree_view.setVisible(True)
        self.placeholder_label.setVisible(False)

        try:
            # 2. Datei explizit mit h5py im Read-Only Modus ('r') öffnen
            self.h5_file_handle = h5py.File(filepath, 'r')

            # 3. Dem Model das h5py-Objekt übergeben
            model = self.tree_view.findHdf5TreeModel()
            model.insertH5pyObject(self.h5_file_handle)
            
        except Exception as e:
            # Echte HDF5 Fehler (z.B. kaputte Datei) sollen immer noch gemeldet werden
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
        self.close_file()
        super().closeEvent(event)