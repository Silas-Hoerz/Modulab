import h5py
import numpy as np
from datetime import datetime
import os

# WICHTIG: Imports für Threading und GUI
from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread, QMetaObject
from PySide6.QtWidgets import QFileDialog, QApplication

# Falls du keine core.constants hast, ersetze dies durch Strings
try:
    from core.constants import APP_TITLE, APP_VERSION
except ImportError:
    APP_TITLE = "Modulab"
    APP_VERSION = "0.1.1"

class ExportManager(QObject):
    """
    Verwaltet den Daten-Export in HDF5-Dateien und fungiert als Datenquelle für Live-Plots.

    Dieser Manager abstrahiert die Komplexität von `h5py`. Er implementiert ein
    Zeilen-basiertes Schreibmodell: Daten werden mit `add()` gesammelt (gestaged)
    und mit `commit()` synchron in die HDF5-Datei geschrieben und gleichzeitig
    an die GUI (z.B. PlotManager) gesendet.

    Funktionsweise:
        1. **Setup:** Zielordner wählen (`select_directory_dialog`).
        2. **Start:** Neue Datei/Gruppe erstellen (`new`).
        3. **Metadaten:** Statische Infos speichern (`add_static`).
        4. **Loop:**
            - Werte hinzufügen (`add('Voltage', 5.0)`).
            - Werte hinzufügen (`add('Current', 0.001)`).
            - Schreiben & Senden (`commit()`).
        5. **Ende:** Datei schließen (`stop`).

    Args:
        log_manager (LogManager): Instanz für das Logging.
        profile_manager (ProfileManager): Instanz zum Speichern des letzten Pfades.

    Signale:
        data_committed (dict):
            Wird bei jedem `commit()` ausgelöst. Enthält die neuen Datenpunkte für
            Live-Plots.
            
            **Payload-Struktur:**
            
            .. code-block:: python
            
                {
                    'Voltage': {'value': 5.0, 'unit': 'V'},
                    'Current': {'value': 1.2e-3, 'unit': 'A'},
                    'Spectrum': {'value': numpy.array([...]), 'unit': 'cnt'}
                }

        export_started (str):
            Wird ausgelöst, wenn eine neue Datei erstellt wurde.
            Args: (str: Voller Pfad zur Datei).

        export_finished (str):
            Wird ausgelöst, wenn der Export beendet wurde.
            Args: (str: Dateiname).

        export_error (str):
            Wird bei Schreib-/IO-Fehlern ausgelöst.
            Args: (str: Fehlermeldung).
    """
    
    # Signal für GUI / Plotter
    data_committed = Signal(dict)
    
    # Status-Signale
    export_started = Signal(str)   # Filename
    export_finished = Signal(str)  # Filename
    export_error = Signal(str)

    def __init__(self, log_manager, profile_manager):
        """
        Initialisiert den ExportManager.
        """
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.file = None
        self.current_group = None
        
        # Interner Buffer für den aktuellen Datenpunkt (Row)
        self._buffer = {} 
        
        # Tracking
        self._row_counter = 0 
        self._known_columns = set()
        
        # Temporärer Speicher für Thread-übergreifende Dialog-Rückgabe
        self._temp_selected_path = None

    # --- Directory Management (Thread-Safe Fix) ---

    def select_directory_dialog(self) -> str:
        """
        Öffnet einen System-Dialog zur Auswahl des Speicherordners.

        **Thread-Safety:**
        Diese Funktion erkennt automatisch, ob sie aus einem Worker-Thread (Experiment)
        oder dem Haupt-Thread aufgerufen wird. Wenn sie aus einem Worker-Thread kommt,
        pausiert sie diesen und führt den GUI-Dialog sicher im Haupt-Thread aus.

        Der gewählte Pfad wird automatisch im Profil gespeichert (`Export_LastDir`).

        Returns:
            str: Der ausgewählte (oder vorherige) Pfad.

        Examples:
            Button-Click Handler in der GUI:
            
            .. code-block:: python
            
                def on_btn_browse_clicked():
                    new_path = export_mgr.select_directory_dialog()
                    ui.line_edit_path.setText(new_path)
        """
        # Prüfen, ob wir im Main-Thread sind
        if QThread.currentThread() == QApplication.instance().thread():
            # Wir sind im GUI Thread -> Direkt ausführen
            self._show_directory_dialog_slot()
            return self._temp_selected_path
        else:
            # Wir sind im Worker Thread -> Anfrage an Main Thread senden und WARTEN (Blocking)
            # Dies verhindert den Freeze/Crash.
            QMetaObject.invokeMethod(self, "_show_directory_dialog_slot", Qt.BlockingQueuedConnection)
            return self._temp_selected_path

    @Slot()
    def _show_directory_dialog_slot(self):
        """
        Interne Slot-Methode, die den Dialog tatsächlich anzeigt.
        Muss zwingend im Main-Thread laufen.
        """
        current_dir = self.get_export_directory()
        
        # Parent holen (damit der Dialog modal über dem Fenster erscheint)
        parent = QApplication.activeWindow()
        
        new_dir = QFileDialog.getExistingDirectory(
            parent, 
            "Choose storage location for dataset",
            current_dir
        )
        
        if new_dir:
            self.set_export_directory(new_dir)
            self._temp_selected_path = new_dir
        else:
            self._temp_selected_path = current_dir

    def set_export_directory(self, path: str):
        """
        Setzt den Export-Pfad manuell und speichert ihn im Profil.

        Args:
            path (str): Der absolute Pfad zum Zielordner.
        """
        if os.path.isdir(path):
            self.profile_mgr.write("Export_LastDir", path)
            self.log_mgr.info(f"Export directory set to: {path}")
        else:
            self.log_mgr.warning(f"Invalid directory path ignored: {path}")

    def get_export_directory(self) -> str:
        """
        Liest den aktuell konfigurierten Export-Pfad aus dem Profil.

        Returns:
            str: Der Pfad oder das Benutzer-Home-Verzeichnis als Fallback.
        """
        path = self.profile_mgr.read("Export_LastDir")
        if path and os.path.isdir(path):
            return path
        return os.path.expanduser("~") # Fallback: User Home

    # --- Dataset Control ---

    def new(self, filename_base: str, dataset_name: str = "Measurement") -> bool:
        """
        Erstellt eine neue HDF5-Datei und bereitet die Messung vor.

        Der Dateiname wird automatisch mit einem Zeitstempel versehen 
        (`Name_YYYYMMDD_HHMMSS.h5`). Schließt eine evtl. offene Datei zuvor.

        Args:
            filename_base (str): Der Basisname der Datei (z.B. "Experiment_A").
            dataset_name (str): Der Name der HDF5-Gruppe für die Daten 
                                (Standard: "Measurement").

        Returns:
            bool: True bei Erfolg, False bei IO-Fehlern.

        Examples:
            Eine neue Messdatei starten:
            
            .. code-block:: python
            
                if export_mgr.new("OLED_IV_Curve"):
                    print("Datei erstellt, bereit für Daten.")
        """
        save_dir = self.get_export_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        full_name = f"{filename_base}_{timestamp}.h5"
        filepath = os.path.join(save_dir, full_name)
        
        try:
            if self.file: self.stop()

            self.file = h5py.File(filepath, 'w')
            self.file.attrs['Date'] = datetime.now().isoformat()
            self.file.attrs['Software'] = f"{APP_TITLE} {APP_VERSION}"
            
            self.current_group = self.file.create_group(dataset_name)
            self.current_group.attrs['Start_Time'] = timestamp
            
            # Reset
            self._row_counter = 0
            self._buffer = {}
            self._known_columns = set()
            
            self.log_mgr.info(f"Export started: {full_name}")
            self.export_started.emit(filepath)
            return True
            
        except Exception as e:
            self.log_mgr.error(f"Failed to create HDF5 file: {e}")
            self.export_error.emit(str(e))
            return False

    def add(self, name: str, data, unit: str = ""):
        """
        Fügt dynamische Messdaten zum internen Puffer hinzu.

        Diese Daten werden **noch nicht** auf die Festplatte geschrieben.
        Erst der Aufruf von `commit()` schreibt alle mit `add()` gesammelten
        Werte als eine Zeile in die HDF5-Datasets.

        Args:
            name (str): Der Name des Datasets (Spaltenname), z.B. "Voltage".
            data (float | numpy.ndarray): Der Messwert (Skalar) oder ein Array 
                                          (z.B. ganzes Spektrum).
            unit (str, optional): Die physikalische Einheit (z.B. "V", "nm"), 
                                  wird als HDF5-Attribut gespeichert.

        Examples:
            Werte für den nächsten Zeitschritt sammeln:
            
            .. code-block:: python
            
                # Skalar hinzufügen
                export_mgr.add("Time", 1.5, "s")
                export_mgr.add("Current", 1e-6, "A")
                
                # Array hinzufügen (z.B. Spektrum)
                spectrum_data = np.array([1, 2, 3, ...])
                export_mgr.add("Spectrum", spectrum_data, "counts")
                
                # WICHTIG: Jetzt commit aufrufen!
                export_mgr.commit()
        """
        if self.file is None: return
        
        self._buffer[name] = {
            'value': data,
            'unit': unit
        }

    def add_static(self, name: str, data, unit: str = ""):
        """
        Speichert einmalige, statische Daten (Metadaten/Konstanten).

        Im Gegensatz zu `add()` wird hier **sofort** geschrieben.
        Das Dataset hat die Länge 1 und wird nicht erweitert.

        Args:
            name (str): Name des Datasets.
            data: Der Wert (String, Zahl, Array).
            unit (str, optional): Einheit.

        Examples:
            Geräte-Infos speichern:
            
            .. code-block:: python
            
                export_mgr.add_static("User", "Max Mustermann")
                export_mgr.add_static("IntegrationTime", 100, "ms")
        """
        if self.current_group is None: return
        try:
            dset = self.current_group.create_dataset(name, data=data)
            dset.attrs['units'] = unit
            dset.attrs['long_name'] = name
            dset.attrs['type'] = 'static'
            self.file.flush()
        except Exception as e:
            self.log_mgr.error(f"Error saving static '{name}': {e}")

    def add_group_attribute(self, key: str, value):
        """
        Fügt Metadaten als Attribute zur HDF5-Hauptgruppe hinzu.
        
        Args:
            key (str): Attribut-Name.
            value: Attribut-Wert.
        """
        if self.current_group:
            self.current_group.attrs[key] = value

    def commit(self):
        """
        Schließt den aktuellen Datenpunkt ab (Synchronisation).

        Führt folgende Schritte aus:
        1. Erstellt HDF5-Datasets für neue Spalten (falls nötig).
        2. Erweitert alle Datasets um eine Zeile.
        3. Schreibt die gepufferten Werte aus `add()` in die neue Zeile.
        4. Füllt fehlende Werte (falls `add` für eine Spalte vergessen wurde) mit NaN.
        5. Sendet das `data_committed`-Signal für Live-Plots.
        6. Leert den Puffer für den nächsten Punkt.

        Examples:
            Am Ende einer Messschleife aufrufen:
            
            .. code-block:: python
            
                while measuring:
                    val = instrument.read()
                    export_mgr.add("Reading", val)
                    export_mgr.commit() # Schreibt auf Disk & updated Plot
        """
        if self.file is None or self.current_group is None: return

        try:
            # 1. Datasets anlegen falls neu
            for name, content in self._buffer.items():
                if name not in self._known_columns:
                    self._create_dataset_for(name, content['value'], content['unit'])
                    self._known_columns.add(name)

            # 2. Schreiben & Datenpaket für Plotter schnüren
            plot_payload = {} # Das Paket für den PlotManager

            for col_name in self._known_columns:
                dset = self.current_group[col_name]
                
                # Wert holen oder NaN
                if col_name in self._buffer:
                    val = self._buffer[col_name]['value']
                    unit = self._buffer[col_name]['unit']
                else:
                    val = self._get_nan_value_for_dataset(dset)
                    unit = dset.attrs.get('units', '')
                
                # HDF5 Resize & Write
                dset.resize((dset.shape[0] + 1), axis=0)
                dset[-1] = val
                
                # Daten für Signal vorbereiten
                # Wir schicken value UND unit, damit der Plotter Achsen beschriften kann
                plot_payload[col_name] = {
                    'value': val,
                    'unit': unit
                }

            # 3. Flush und Signal
            self.file.flush()
            self._row_counter += 1
            self._buffer.clear()
            
            self.data_committed.emit(plot_payload)

        except Exception as e:
            self.log_mgr.error(f"Error during commit: {e}")
            self.export_error.emit(str(e))

    def stop(self):
        """
        Beendet den Export und schließt die HDF5-Datei sauber.
        
        Sendet das `export_finished`-Signal.
        """
        if self.file:
            fname = self.file.filename
            try:
                self.file.close()
            except: pass
            
            self.file = None
            self.current_group = None
            self.log_mgr.info("Export stopped.")
            self.export_finished.emit(fname)

    # --- Helpers ---
    def _create_dataset_for(self, name, data, unit):
        """
        Interne Hilfsfunktion: Erstellt ein erweiterbares (chunked) Dataset.
        Erkennt automatisch, ob es sich um Skalare oder Arrays handelt.
        """
        arr = np.asanyarray(data)
        if arr.ndim == 0: # Skalar
            shape, maxshape, chunks = (0,), (None,), True
        else: # Array
            shape = (0,) + arr.shape
            maxshape = (None,) + arr.shape
            chunks = (1,) + arr.shape
        
        dset = self.current_group.create_dataset(name, shape=shape, maxshape=maxshape, chunks=chunks, dtype=arr.dtype)
        dset.attrs['units'] = unit
        dset.attrs['long_name'] = name

    def _get_nan_value_for_dataset(self, dset):
        """
        Interne Hilfsfunktion: Generiert einen NaN-Wert passend zum Datentyp
        (für fehlende Werte beim Commit).
        """
        dtype = dset.dtype
        shape = dset.shape[1:]
        if np.issubdtype(dtype, np.floating): return np.full(shape, np.nan, dtype=dtype)
        return np.full(shape, 0, dtype=dtype)