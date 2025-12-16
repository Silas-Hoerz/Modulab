import h5py
import numpy as np
import pandas as pd
import os
import time
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from core.constants import APP_TITLE, APP_VERSION


class MeasurementSession:
    """
    Hält alle Daten einer einzigen Messung (z.B. eines Sweeps) im RAM.
    """
    def __init__(self, name, metadata=None):
        self.name = name
        self.metadata = metadata if metadata else {}
        self.created_at = datetime.now()
        
        self.timestamps = []
        self.set_values = []
        self.meas_v = []
        self.meas_i = []
        
        self.spectra = []       
        self.wavelengths = None 

    def add_point(self, t, set_val, v, i, spectrum=None, wl=None):
        self.timestamps.append(t)
        self.set_values.append(set_val)
        self.meas_v.append(v)
        self.meas_i.append(i)
        
        if spectrum is not None:
            # Kopie speichern, um Referenz-Probleme zu vermeiden
            self.spectra.append(np.array(spectrum, copy=True))
            if self.wavelengths is None and wl is not None:
                self.wavelengths = np.array(wl, copy=True)

    def is_empty(self):
        return len(self.timestamps) == 0

    def get_spectra_matrix(self):
        if not self.spectra: return None
        try: return np.vstack(self.spectra)
        except ValueError: return None

    def to_dataframe(self):
        """Konvertiert Session zu Pandas DataFrame."""
        data = {
            "Timestamp": self.timestamps,
            "Set_Value": self.set_values,
            "Voltage_Meas": self.meas_v,
            "Current_Meas": self.meas_i
        }
        df = pd.DataFrame(data)
        
        mat = self.get_spectra_matrix()
        if mat is not None and self.wavelengths is not None:
            # Dimension check
            if mat.shape[1] == len(self.wavelengths):
                col_names = [f"Int_{w:.2f}nm" for w in self.wavelengths]
                df_spec = pd.DataFrame(mat, columns=col_names)
                df = pd.concat([df, df_spec], axis=1)
            
        return df

class ExportManager(QObject):
    session_updated = Signal(str, dict) 
    export_finished = Signal(str)
    export_error = Signal(str)

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager
        self.active_sessions = {} 

    def start_session(self, name, metadata=None):
        if name in self.active_sessions:
            self.log_mgr.warning(f"Session '{name}' overwritten.")
        self.active_sessions[name] = MeasurementSession(name, metadata)
        self.log_mgr.info(f"Session started: {name}")

    def add_data_point(self, session_name, set_val, meas_v, meas_i, spectrum=None, wl=None):
        if session_name not in self.active_sessions: return
        session = self.active_sessions[session_name]
        
        # Add to RAM
        session.add_point(datetime.now().timestamp(), set_val, meas_v, meas_i, spectrum, wl)
        
        # Notify GUI
        self.session_updated.emit(session_name, {
            'x': set_val, 'v': meas_v, 'i': meas_i,
            'spectrum': spectrum, 'wl': wl
        })

    def save_session_to_disk(self, session_name, filepath):
        """
        Exportiert ENTWEDER als HDF5 ODER als CSV, basierend auf der Dateiendung.
        Löscht existierende Dateien aggressiv, um Lock-Probleme zu vermeiden.
        """
        if session_name not in self.active_sessions:
            self.log_mgr.error(f"Cannot save unknown session: {session_name}")
            return

        session = self.active_sessions[session_name]
        if session.is_empty():
            self.log_mgr.warning("Session is empty. Export skipped.")
            return

        # Verzeichnis speichern
        self.profile_mgr.write("Export_LastDir", os.path.dirname(filepath))

        # Dateityp erkennen
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        # --- FIX: Datei vorher löschen ---
        # Das verhindert den "Signature not found" Fehler, wenn h5py versucht, 
        # in eine korrupte/gelockte Datei zu schreiben.
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self.log_mgr.debug(f"Existing file removed: {filepath}")
            except OSError as e:
                self.log_mgr.error(f"Cannot overwrite file (locked?): {e}")
                self.export_error.emit(f"File locked by another process: {e}")
                return

        if ext == ".h5" or ext == ".hdf5":
            self._export_hdf5(session, filepath)
        elif ext == ".csv" or ext == ".txt":
            self._export_csv(session, filepath)
        else:
            self.log_mgr.error(f"Unknown file extension: {ext}")
            self.export_error.emit("Unknown file type selected.")

    def _export_hdf5(self, session, filepath):
        """Interner HDF5 Writer."""
        try:
            # Data Prep
            np_timestamps = np.array(session.timestamps)
            np_set_values = np.array(session.set_values)
            np_meas_v = np.array(session.meas_v)
            np_meas_i = np.array(session.meas_i)
            spectra_matrix = session.get_spectra_matrix()
            wavelengths = session.wavelengths

            with h5py.File(filepath, 'w') as f:
                # Metadaten
                f.attrs['Export_Date'] = str(datetime.now().isoformat())
                f.attrs['Software'] = str(f"{APP_TITLE} {APP_VERSION}")
                for k, v in session.metadata.items():
                    f.attrs[str(k)] = str(v) if v is not None else ""
                
                # Datasets
                grp = f.create_group("Data")
                grp.create_dataset("Timestamps", data=np_timestamps)
                grp.create_dataset("Set_Values", data=np_set_values)
                grp.create_dataset("Voltage_Meas", data=np_meas_v)
                grp.create_dataset("Current_Meas", data=np_meas_i)
                
                if spectra_matrix is not None:
                    grp.create_dataset("Spectra_Matrix", data=spectra_matrix)
                if wavelengths is not None:
                    grp.create_dataset("Wavelengths", data=wavelengths)
                
                f.flush() # Buffer auf Platte zwingen
            
            self.log_mgr.info(f"HDF5 Export successful: {filepath}")
            self.export_finished.emit(filepath)

        except Exception as e:
            self.log_mgr.error(f"HDF5 Export failed: {e}")
            self.export_error.emit(str(e))

    def _export_csv(self, session, filepath):
        """Interner CSV Writer (Origin optimiert)."""
        try:
            df = session.to_dataframe()
            with open(filepath, 'w', newline='') as f:
                f.write(f"# Origin Import Info\n")
                f.write(f"# Date: {session.created_at}\n")
                for k, v in session.metadata.items():
                    f.write(f"# {k}: {v}\n")
                # Pandas write
                df.to_csv(f, index=False)
                
            self.log_mgr.info(f"CSV Export successful: {filepath}")
            self.export_finished.emit(filepath)

        except Exception as e:
            self.log_mgr.error(f"CSV Export failed: {e}")
            self.export_error.emit(str(e))