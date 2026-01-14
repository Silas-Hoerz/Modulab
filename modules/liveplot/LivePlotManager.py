import numpy as np
from collections import deque
from PySide6.QtCore import QObject, Signal, Slot

class LivePlotManager(QObject):
    """
    Backend-Manager für Echtzeit-Visualisierungen.
    
    Dieser Manager unterscheidet strikt zwischen zwei Modi:
    
    1. **Monitor (Oszilloskop-Modus):**
       Ein rollender Ringpuffer (Deque), der ständig die letzten N Werte der SMU speichert.
       Dient zur schnellen Überprüfung ("Ist Spannung da?"), wird aber nicht dauerhaft gespeichert.
       
    2. **Session (Experiment-Modus):**
       Strukturierte Datencontainer für spezifische Messungen (z.B. Sweeps).
       Hier definiert der User, welche Plots (I-V, Zeit-I, Spektrum) angelegt werden sollen.
       
    Args:
        log_manager (LogManager): Logging-Instanz.
        profile_manager (ProfileManager): Profil-Instanz zum Laden der Buffer-Größe.
    """
    
    # --- Signale Monitor ---
    monitor_updated = Signal(dict)
    """Signal: Neuer Datenpunkt im Monitor-Buffer. Args: (monitor_data_dict)"""
    
    spectrum_updated = Signal(object, object)
    """Signal: Neues Spektrum vom Detektor. Args: (wavelengths, intensities)"""
    
    # --- Signale Experiment-Sessions ---
    session_started = Signal(str) 
    """Signal: Neue Session gestartet. Args: (SessionName)"""
    
    plot_defined = Signal(str, str, str, str, str, bool, bool) 
    """
    Signal: Neuer Plot-Tab soll erstellt werden.
    Args: (session, plot_key, title, x_label, y_label, log_x, log_y)
    """
    
    data_appended = Signal(str, str, float, float)
    """Signal: Einzelner Punkt zu Plot hinzugefügt. Args: (session, plot_key, x, y)"""
    
    data_set = Signal(str, str, object, object)
    """Signal: Kompletter Datensatz ersetzt (für Arrays). Args: (session, plot_key, x_arr, y_arr)"""
    
    session_finished = Signal(str)
    """Signal: Session beendet. Args: (SessionName)"""

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        # Monitor Buffer
        self.monitor_maxlen = 2000 
        self.monitor_data = {
            'a': {'v': deque(maxlen=self.monitor_maxlen), 'i': deque(maxlen=self.monitor_maxlen)},
            'b': {'v': deque(maxlen=self.monitor_maxlen), 'i': deque(maxlen=self.monitor_maxlen)}
        }
        
        # Experiment Data Store (RAM)
        # Struktur: self.active_sessions['SessionName']['plots']['PlotKey'] = {'x': [], 'y': ...}
        self.active_sessions = {}

        self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        """Lädt die Monitor-Buffer-Größe aus dem Profil."""
        size = self.profile_mgr.read("LivePlot_MonitorHistory")
        if size: self.set_monitor_buffer_size(int(size))

    def set_monitor_buffer_size(self, new_len: int):
        """
        Ändert die Länge des rollenden Monitors (Oszilloskop).
        
        Args:
            new_len (int): Anzahl der zu speichernden Punkte (z.B. 2000).
        """
        self.monitor_maxlen = new_len
        for ch in ['a', 'b']:
            self.monitor_data[ch]['v'] = deque(list(self.monitor_data[ch]['v']), maxlen=new_len)
            self.monitor_data[ch]['i'] = deque(list(self.monitor_data[ch]['i']), maxlen=new_len)

    # --- Monitor Slots (Automatischer Data Pull) ---

    @Slot(str, float, float)
    def on_smu_measurement(self, channel, current, voltage):
        """
        Slot: Wird automatisch vom SmuManager aufgerufen, wenn gemessen wurde.
        Schiebt Daten in den Ringpuffer für die Live-Ansicht.
        """
        ch = channel.lower()
        if ch in self.monitor_data:
            self.monitor_data[ch]['v'].append(voltage)
            self.monitor_data[ch]['i'].append(current)
            self.monitor_updated.emit(self.monitor_data)

    @Slot(object, object)
    def on_spectrum_acquired(self, wavelengths, intensities):
        """Slot: Wird vom Spektrometer aufgerufen."""
        self.spectrum_updated.emit(wavelengths, intensities)

    # --- Session API (Manuelle Steuerung durch Skripte) ---

    def start_session(self, name: str, metadata: dict = None):
        """
        Erstellt einen neuen Container für Plot-Daten einer Messung.

        Args:
            name (str): Eindeutiger Name (z.B. "IV_Sweep_A").
            metadata (dict, optional): Infos für den Header. Defaults to None.
        
        Example:
            >>> api.plot_mgr.start_session("MySweep")
        """
        if name in self.active_sessions:
            self.log_mgr.warning(f"Session '{name}' overwritten.")
        
        self.active_sessions[name] = {
            'plots': {},      # Hier landen die Kurven (lin_iv, spec, etc.)
            'metadata': metadata if metadata else {}
        }
        self.log_mgr.info(f"Session started: {name}")
        self.session_started.emit(name)

    def define_plot(self, session, key, title, xl, yl, log_x=False, log_y=False):
        """
        Definiert ein neues Diagramm-Fenster (oder Tab) in der GUI.

        Args:
            session (str): Name der gestarteten Session.
            key (str): Interne ID für den Plot (z.B. "iv_log").
            title (str): Sichtbarer Titel des Plots.
            xl (str): Beschriftung X-Achse.
            yl (str): Beschriftung Y-Achse.
            log_x (bool): Logarithmische X-Achse.
            log_y (bool): Logarithmische Y-Achse.

        Example:
            >>> api.plot_mgr.define_plot("MySweep", "iv_curve", "I-V Curve", "Voltage (V)", "Current (A)", log_y=True)
        """
        if session not in self.active_sessions: return
        
        # Struktur sicherstellen
        if 'plots' not in self.active_sessions[session]:
             self.active_sessions[session]['plots'] = {}
             
        self.active_sessions[session]['plots'][key] = {
            'x': [], 'y': [], 
            'is_array': False,
            'title': title, 'log_y': log_y
        }
        self.plot_defined.emit(session, key, title, xl, yl, log_x, log_y)

    def append_data(self, session, key, x, y):
        """
        Fügt einen einzelnen Punkt (X, Y) zu einem Plot hinzu.
        Ideal für Sweeps, wo Daten Punkt für Punkt kommen.

        Args:
            session (str): Session Name.
            key (str): Plot ID (muss vorher mit `define_plot` erstellt sein).
            x (float): X-Koordinate.
            y (float): Y-Koordinate.

        Example:
            >>> api.plot_mgr.append_data("MySweep", "iv_curve", 1.5, 0.002)
        """
        if session not in self.active_sessions: return
        plots = self.active_sessions[session].get('plots', {})
        
        if key not in plots: return
        
        plots[key]['x'].append(x)
        plots[key]['y'].append(y)
        self.data_appended.emit(session, key, x, y)

    def set_data(self, session: str, key: str, x_arr, y_arr):
        """
        Ersetzt die Daten eines Plots komplett.
        Ideal für Spektren oder schnelle Updates, wo ganze Arrays übertragen werden.

        Args:
            session (str): Session Name.
            key (str): Plot ID.
            x_arr (array-like): Array der X-Werte.
            y_arr (array-like): Array der Y-Werte.

        Example:
            >>> api.plot_mgr.set_data("MySweep", "spec_live", wavelengths, intensities)
        """
        if session not in self.active_sessions: return
        plots = self.active_sessions[session].get('plots', {})
        
        if key not in plots: return
        
        # Wir speichern hier keine History im RAM, nur das letzte Frame
        plots[key]['x'] = x_arr
        plots[key]['y'] = y_arr
        plots[key]['is_array'] = True
        
        self.data_set.emit(session, key, x_arr, y_arr)

    def stop_session(self, name: str):
        """
        Markiert eine Session als beendet. 
        Kann von der GUI genutzt werden, um den "Live"-Status zu entfernen.
        """
        if name in self.active_sessions:
            self.session_finished.emit(name)

    def remove_session(self, name: str):
        """
        Löscht die Session-Daten aus dem RAM, um Speicher freizugeben.
        """
        if name in self.active_sessions:
            del self.active_sessions[name]