import numpy as np
from collections import deque
from PySide6.QtCore import QObject, Signal, Slot

class LivePlotManager(QObject):
    """
    Backend für Multi-Plot Sessions.
    """
    # Signale Monitor
    monitor_updated = Signal(dict)
    spectrum_updated = Signal(object, object)
    
    # Signale Experiment-Sessions
    session_started = Signal(str) # Nur Name
    # session, plot_key, title, x_lbl, y_lbl, log_x, log_y
    plot_defined = Signal(str, str, str, str, str, bool, bool) 
    # session, plot_key, x, y (Append Mode)
    data_appended = Signal(str, str, float, float)
    # session, plot_key, x_array, y_array (Replace Mode für Spektren)
    data_set = Signal(str, str, object, object)
    
    session_finished = Signal(str)

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
        # Struktur: self.sessions['SessionName']['PlotKey'] = {'x': [], 'y': []}
        self.active_sessions = {}

        self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        size = self.profile_mgr.read("LivePlot_MonitorHistory")
        if size: self.set_monitor_buffer_size(int(size))

    def set_monitor_buffer_size(self, new_len: int):
        self.monitor_maxlen = new_len
        for ch in ['a', 'b']:
            self.monitor_data[ch]['v'] = deque(list(self.monitor_data[ch]['v']), maxlen=new_len)
            self.monitor_data[ch]['i'] = deque(list(self.monitor_data[ch]['i']), maxlen=new_len)

    # --- Monitor Slots (Pull) ---
    @Slot(str, float, float)
    def on_smu_measurement(self, channel, current, voltage):
        ch = channel.lower()
        if ch in self.monitor_data:
            self.monitor_data[ch]['v'].append(voltage)
            self.monitor_data[ch]['i'].append(current)
            self.monitor_updated.emit(self.monitor_data)

    @Slot(object, object)
    def on_spectrum_acquired(self, wavelengths, intensities):
        self.spectrum_updated.emit(wavelengths, intensities)

    # --- Session API (Push) ---

    def start_session(self, name: str, metadata: dict = None):
        """
        Startet Session mit optionalen Metadaten (Device, User, Config).
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
        if session not in self.active_sessions: return
        # Struktur update: Wir speichern unter ['plots'][key]
        if 'plots' not in self.active_sessions[session]:
             self.active_sessions[session]['plots'] = {}
             
        self.active_sessions[session]['plots'][key] = {
            'x': [], 'y': [], 'is_array': False,
            'title': title, 'log_y': log_y
        }
        self.plot_defined.emit(session, key, title, xl, yl, log_x, log_y)

    def append_data(self, session, key, x, y):
        # Zugriff angepasst auf ['plots']
        if session not in self.active_sessions: return
        plots = self.active_sessions[session].get('plots', {})
        if key not in plots: return
        
        plots[key]['x'].append(x)
        plots[key]['y'].append(y)
        self.data_appended.emit(session, key, x, y)
        
    # set_data analog anpassen...

    def set_data(self, session: str, key: str, x_arr, y_arr):
        """Ersetzt die Daten komplett (für Spektren)."""
        if session not in self.active_sessions or key not in self.active_sessions[session]: return
        
        # Wir speichern hier keine History im RAM, nur das letzte Frame
        self.active_sessions[session][key]['x'] = x_arr
        self.active_sessions[session][key]['y'] = y_arr
        self.active_sessions[session][key]['is_array'] = True
        
        self.data_set.emit(session, key, x_arr, y_arr)

    def stop_session(self, name: str):
        if name in self.active_sessions:
            self.session_finished.emit(name)

    def remove_session(self, name: str):
        if name in self.active_sessions:
            del self.active_sessions[name]