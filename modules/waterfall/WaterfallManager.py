import numpy as np 
from PySide6.QtCore import QObject, Signal, Slot 
from collections import deque # Wichtig für Speicher-Management

class WaterfallManager(QObject):
    """
    Verwaltet die Daten für den Waterfall.
    
    Nutzt einen Ring-Puffer (deque), um den Speicherverbrauch zu begrenzen.
    """

    new_spectrum_available = Signal(object, object) 
    waterfall_cleared = Signal()

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.wavelengths = None
        self.limit = 1000 # Standardwert vor Profil-Load
        self.history_buffer = deque(maxlen=self.limit) 
        self.counter = 0
        
        # Signal verbinden
        self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        saved_limit = self.profile_mgr.read("Waterfall_MaxHistory")
        if saved_limit:
            self.set_history_limit(int(saved_limit))
            self.log_mgr.debug(f"Waterfall history limit set to {saved_limit} from profile.")

    @Slot(object, object)
    def add_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray):
        if intensities is None or len(intensities) == 0:
            return
        
        if self.wavelengths is None:
            self.wavelengths = wavelengths
        
        # In den Ring-Puffer schieben (automatisch begrenzt)
        self.history_buffer.append(intensities)
        self.counter += 1
        
        self.new_spectrum_available.emit(wavelengths, intensities)

    @Slot(int)
    def set_history_limit(self, limit: int):
        """
        Ändert die Größe des Ring-Puffers.
        Wird aufgerufen, wenn User die History-Lines massiv erhöht.
        """
        # Nur ändern, wenn nötig (deque neu erstellen ist teuer)
        if limit > self.history_buffer.maxlen:
            self.log_mgr.info(f"Expanding waterfall buffer to {limit} lines.")
            # Neue Deque mit Daten kopieren
            new_deque = deque(self.history_buffer, maxlen=limit)
            self.history_buffer = new_deque
            
            # Speichern
            self.profile_mgr.write("Waterfall_MaxHistory", limit)

    @Slot()
    def clear_data(self):
        self.history_buffer.clear()
        self.counter = 0
        self.log_mgr.info("Waterfall history cleared.")
        self.waterfall_cleared.emit()

    def save_raw_data(self, filepath: str, format: str = 'csv') -> bool:
        if not self.history_buffer:
            self.log_mgr.warning("No data to save.")
            return False
            
        try:
            # Deque zu Numpy Array konvertieren
            data_matrix = np.vstack(list(self.history_buffer))
            
            if format == 'csv':
                header = ["Index"] + [f"{w:.2f}" for w in self.wavelengths]
                # Indizes generieren (Relativ zum Start der Aufnahme oder Puffer?)
                # Hier nehmen wir Puffer-Position (0 bis N)
                indices = np.arange(len(data_matrix)).reshape(-1, 1)
                full_data = np.hstack((indices, data_matrix))
                np.savetxt(filepath, full_data, delimiter=",", header=",".join(header), comments='')
                
            elif format == 'npy':
                np.save(filepath, (self.wavelengths, data_matrix))
                
            self.log_mgr.info(f"Saved {len(data_matrix)} lines to {filepath}")
            return True
        except Exception as e:
            self.log_mgr.error(f"Save failed: {e}")
            return False