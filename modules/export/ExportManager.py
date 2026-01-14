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
    Datencontainer, der alle Daten einer einzigen Messung (z.B. eines Sweeps) im RAM hält.

    Diese Klasse wird vom ExportManager verwaltet. Sie akkumuliert Messpunkte 
    und Spektren, bis sie gespeichert werden.

    Args:
        name (str): Ein eindeutiger Name für diese Session (z.B. "Sweep_001").
        metadata (dict, optional): Zusätzliche Metadaten (User, Settings), die im Header gespeichert werden.
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
        """
        Fügt einen einzelnen Messpunkt zur Session hinzu.

        Args:
            t (float): Unix-Timestamp der Messung.
            set_val (float): Der gesetzte Wert (z.B. Spannung in V).
            v (float): Gemessene Spannung in V.
            i (float): Gemessener Strom in A.
            spectrum (np.array, optional): Intensitäts-Array eines Spektrometers. Defaults to None.
            wl (np.array, optional): Wellenlängen-Array (nur beim ersten Punkt nötig). Defaults to None.
        """
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
        """
        Prüft, ob Daten vorhanden sind.

        Returns:
            bool: True, wenn keine Messpunkte existieren, sonst False.
        """
        return len(self.timestamps) == 0

    def get_spectra_matrix(self):
        """
        Konvertiert die Liste der Spektren in eine 2D NumPy-Matrix.

        Returns:
            np.ndarray | None: Matrix mit Shape (Anzahl_Messpunkte, Anzahl_Pixel) oder None.
        """
        if not self.spectra: return None
        try: return np.vstack(self.spectra)
        except ValueError: return None

    def to_dataframe(self):
        """
        Konvertiert die gesamte Session in einen Pandas DataFrame (für CSV-Export).
        
        Falls Spektraldaten vorhanden sind, werden diese als zusätzliche Spalten 
        (Int_XXX.XXnm) angehängt.

        Returns:
            pd.DataFrame: Der fertige DataFrame mit allen Daten.
        """
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
    """
    Verwaltet Datensessions und steuert den Datei-Export (HDF5 / CSV).

    Dieser Manager dient als zentrale Schnittstelle zum Sammeln von Daten während
    einer Messung. Skripte sollten diesen Manager nutzen, um Messpunkte zu protokollieren,
    anstatt Daten manuell zu sammeln.

    Args:
        log_manager (LogManager): Logger-Instanz für Statusmeldungen.
        profile_manager (ProfileManager): Manager zum Speichern des letzten Export-Pfades.

    Signals:
        session_updated (str, dict): 
            Wird gefeuert, wenn ein neuer Punkt hinzugefügt wurde. 
            Nützlich für Live-Plots.
            Args: (SessionName, DataDict)
        export_finished (str): 
            Signalisiert erfolgreichen Export. Args: (Dateipfad)
        export_error (str): 
            Signalisiert Fehler beim Export. Args: (Fehlermeldung)
    """
    session_updated = Signal(str, dict) 
    export_finished = Signal(str)
    export_error = Signal(str)

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager
        self.active_sessions = {} 

    def start_session(self, name, metadata=None):
        """
        Erstellt eine neue Mess-Session im Arbeitsspeicher.
        
        Überschreibt eine existierende Session mit demselben Namen, falls vorhanden.

        Args:
            name (str): Eindeutiger Name der Messung (z.B. "IV_Curve_01").
            metadata (dict, optional): Metadaten wie User, Probe, Parameter.

        Example:
            >>> api.export_mgr.start_session("Test_Run", metadata={"Probe": "A12"})
        """
        if name in self.active_sessions:
            self.log_mgr.warning(f"Session '{name}' overwritten.")
        self.active_sessions[name] = MeasurementSession(name, metadata)
        self.log_mgr.info(f"Session started: {name}")

    def add_data_point(self, session_name, set_val, meas_v, meas_i, spectrum=None, wl=None):
        """
        Fügt einen Messpunkt zu einer laufenden Session hinzu und aktualisiert die GUI.

        Diese Methode sollte innerhalb der Messschleife aufgerufen werden.

        Args:
            session_name (str): Name der Session, zu der die Daten gehören.
            set_val (float): Der gesetzte Sollwert (X-Achse).
            meas_v (float): Gemessene Spannung.
            meas_i (float): Gemessener Strom.
            spectrum (list/array, optional): Spektrum-Daten (Intensitäten).
            wl (list/array, optional): Wellenlängen (nur nötig, wenn sich Achse ändert oder Init).

        Example:
            >>> # In einer Schleife:
            >>> v_meas, i_meas = smu.measure_iv('a')
            >>> api.export_mgr.add_data_point("Test_Run", set_val=1.0, meas_v=v_meas, meas_i=i_meas)
        """
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
        Speichert eine Session auf die Festplatte.
        
        Das Format wird automatisch anhand der Dateiendung erkannt:
        - **.h5 / .hdf5**: HDF5 Format (empfohlen für große Daten/Spektren).
        - **.csv / .txt**: CSV Format (Textbasiert, gut für Origin/Excel).

        Löscht existierende Dateien aggressiv vor dem Schreiben, um 'File Lock'
        Probleme von h5py zu umgehen.

        Args:
            session_name (str): Name der Session im RAM.
            filepath (str): Voller Zielpfad (z.B. "C:/Data/messung.h5").

        Example:
            >>> export_mgr.save_session_to_disk("Test_Run", "C:/Users/Lab/Data/my_data.h5")
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
        """Interner HDF5 Writer. Speichert Rohdaten und Plot-optimierte Matrizen."""
        try:
            # Data Prep (Bestehender Code)
            np_timestamps = np.array(session.timestamps)
            np_set_values = np.array(session.set_values)
            np_meas_v = np.array(session.meas_v)
            np_meas_i = np.array(session.meas_i)
            spectra_matrix = session.get_spectra_matrix() # Shape: (Zeit, Wellenlänge)
            wavelengths = session.wavelengths

            with h5py.File(filepath, 'w') as f:
                # Metadaten (Bestehender Code)
                f.attrs['Export_Date'] = str(datetime.now().isoformat())
                f.attrs['Software'] = str(f"{APP_TITLE} {APP_VERSION}")
                for k, v in session.metadata.items():
                    f.attrs[str(k)] = str(v) if v is not None else ""
                
                # Datasets Gruppe erstellen
                grp = f.create_group("Data")
                
                # Standard Rohdaten speichern (wie bisher)
                grp.create_dataset("Timestamps", data=np_timestamps)
                grp.create_dataset("Set_Values", data=np_set_values)
                grp.create_dataset("Voltage_Meas", data=np_meas_v)
                grp.create_dataset("Current_Meas", data=np_meas_i)
                
                if wavelengths is not None:
                    grp.create_dataset("Wavelengths", data=wavelengths)

                if spectra_matrix is not None:
                    # 1. Die klassische Matrix (Zeit x Wellenlänge) speichern
                    grp.create_dataset("Spectra_Matrix_Raw", data=spectra_matrix)

                    # --- NEU: Origin-optimiertes Dataset ---
                    if wavelengths is not None and len(wavelengths) == spectra_matrix.shape[1]:
                        # Wir transponieren die Matrix: (Wellenlänge x Zeit)
                        # Damit entspricht jede SPALTE einem Spektrum
                        spectra_T = spectra_matrix.T
                        
                        # [Wellenlänge, Spektrum_t0, Spektrum_t1, ...]
                        plot_ready_data = np.column_stack((wavelengths, spectra_T))
                        
                        dset_plot = grp.create_dataset("Spectra_For_Plotting", data=plot_ready_data)
                        
                        # Optional: Attribute setzen, damit man weiß, was was ist
                        dset_plot.attrs['Info'] = "Col 0: Wavelength (X), Col 1..N: Spectra (Y)"
                        # Versuchen, Spaltennamen als Attribut zu hinterlegen (Origin liest das manchmal)
                        col_names = ["Wavelength_nm"] + [f"Spec_{i}" for i in range(spectra_T.shape[1])]
                        # HDF5 unterstützt keine echten Header, aber wir speichern es als String
                        dset_plot.attrs['Column_Names'] = str(col_names)

                f.flush() 
            
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