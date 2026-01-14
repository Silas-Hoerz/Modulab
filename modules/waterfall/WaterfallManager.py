import numpy as np 
from PySide6.QtCore import QObject, Signal, Slot 
from collections import deque # Wichtig für Speicher-Management

class WaterfallManager(QObject):
    """
    Verwaltet den historischen Datenbestand für Waterfall- (Spektrogramm-) Diagramme.

    

    Diese Klasse dient als Zwischenspeicher (Buffer) zwischen der schnellen Datenerfassung
    und der oft langsameren GUI-Darstellung. Sie speichert eine definierte Anzahl
    vergangener Spektren (History), um einen zeitlichen Verlauf der Intensität 
    darstellen zu können.

    **Speicher-Management:**
    Da Spektraldaten sehr groß werden können, nutzt diese Klasse eine `collections.deque`
    mit definierter Maximallänge (`maxlen`). Wenn der Puffer voll ist, wird beim Hinzufügen
    eines neuen Spektrums das älteste automatisch verworfen (FIFO - First In, First Out).

    

    Args:
        log_manager (LogManager): Instanz für das Logging.
        profile_manager (ProfileManager): Instanz zum Laden/Speichern der Buffer-Größe.

    Signals:
        new_spectrum_available (np.ndarray, np.ndarray): 
            Wird emittiert, sobald ein Spektrum dem Buffer hinzugefügt wurde.
            Args: (Wellenlängen, Intensitäten)
        
        waterfall_cleared (): 
            Wird emittiert, wenn der Buffer geleert wurde.
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
        """
        Lädt die gespeicherte Buffer-Größe (History Depth) aus dem Profil.
        """
        saved_limit = self.profile_mgr.read("Waterfall_MaxHistory")
        if saved_limit:
            self.set_history_limit(int(saved_limit))
            self.log_mgr.debug(f"Waterfall history limit set to {saved_limit} from profile.")

    @Slot(object, object)
    def add_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray):
        """
        Fügt ein neues Spektrum zum Verlauf hinzu.

        Schiebt die Intensitäten in den Ring-Puffer. Die Wellenlängen werden
        beim ersten Aufruf gecached (da sie sich meist nicht ändern).

        Args:
            wavelengths (np.ndarray): 1D-Array der Wellenlängen (X-Achse).
            intensities (np.ndarray): 1D-Array der Intensitäten (Z-Achse / Farbe).

        Example:
            >>> # In der Acquisition-Schleife:
            >>> waterfall_mgr.add_spectrum(wl_array, inten_array)
        """
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
        Ändert die maximale Anzahl der gespeicherten Zeilen (Lines).

        Achtung: Dies ist eine "teure" Operation, da die interne `deque` 
        komplett neu erstellt und kopiert werden muss.

        Args:
            limit (int): Neue maximale Anzahl an Spektren (z.B. 2000).
        """
        # Nur ändern, wenn nötig (deque neu erstellen ist teuer)
        if limit != self.history_buffer.maxlen:
            self.log_mgr.info(f"Expanding waterfall buffer to {limit} lines.")
            # Neue Deque mit Daten kopieren
            new_deque = deque(self.history_buffer, maxlen=limit)
            self.history_buffer = new_deque
            self.limit = limit
            
            # Speichern
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write("Waterfall_MaxHistory", limit)

    @Slot()
    def clear_data(self):
        """Löscht alle Daten aus dem Buffer und setzt den Zähler zurück."""
        self.history_buffer.clear()
        self.counter = 0
        self.log_mgr.info("Waterfall history cleared.")
        self.waterfall_cleared.emit()

    def save_raw_data(self, filepath: str, format: str = 'csv') -> bool:
        """
        Exportiert den aktuellen Inhalt des Waterfall-Buffers.

        Stapelt die gesammelten Spektren zu einer 2D-Matrix und speichert sie.

        Args:
            filepath (str): Zielpfad der Datei.
            format (str, optional): 'csv' oder 'npy'. Defaults to 'csv'.

        Returns:
            bool: True bei Erfolg, False bei Fehler.
        """
        if not self.history_buffer:
            self.log_mgr.warning("No data to save.")
            return False
            
        try:
            # Deque zu Numpy Array konvertieren (Liste von 1D Arrays -> 2D Matrix)
            data_matrix = np.vstack(list(self.history_buffer))
            
            if format == 'csv':
                # Header bauen: Index, WL_1, WL_2, ...
                header = ["Index"] + [f"{w:.2f}" for w in self.wavelengths]
                
                # Indizes generieren (0 bis N)
                indices = np.arange(len(data_matrix)).reshape(-1, 1)
                
                # Zusammenfügen: [Index_Spalte | Daten_Matrix]
                full_data = np.hstack((indices, data_matrix))
                
                np.savetxt(filepath, full_data, delimiter=",", header=",".join(header), comments='')
                
            elif format == 'npy':
                # Binär speichern: Tupel aus (Wellenlängen, DatenMatrix)
                np.save(filepath, (self.wavelengths, data_matrix))
                
            self.log_mgr.info(f"Saved {len(data_matrix)} lines to {filepath}")
            return True
        except Exception as e:
            self.log_mgr.error(f"Save failed: {e}")
            return False