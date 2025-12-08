import numpy as np 
import os
from PySide6.QtCore import QObject, Signal, Slot 
from matplotlib.figure import Figure

class WaterfallManager(QObject):
    """
    Manager zu Verwaltung und Pufferung von Spektrendaten für die Waterfall-Darstellung.

    Diese Klasse emfängt Daten vom SpektrometerManager, speichert diese in einen Buffer und stellt Funktionen zum Exportieren der 3D-Daten und zu Steuerung des zugehörigen GUI Widgets bereit.

    Args:
        log_manager (LogManager): Eine Instanz des Log-Managers.
        profile_manager (ProfileManager): Eine Instanz zur Verwaltung von App-Einstellungen und User-Daten.

    Signale:
        waterfall_data_updated (list, object):
            Wird ausgelöst, wenn ein neues Spektrum hinzugefügt wurde.
            Args: (list: Z-Indices [int], object: Datenmatrix [np.ndarray]).
        
        waterfall_cleared ():
            Wird ausgelöst, nachdem der interne Datenpuffer geleert wurde.
    """

    # Signale
    waterfall_data_updated = Signal(list, object) # Intern als (list[int], np.ndarray) behandelt
    waterfall_cleared = Signal()

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.log_mgr.debug("Initializing WaterfallManager...")

        self.wavelengths = np.array([])
        self.data_buffer = []
        self.z_indices = []
        self.z_counter = 0

    def get_waterfall_data(self) -> tuple[np.ndarray, np.ndarray, list[int]]:
        """
        Gibt die gesamten akkumulierten 3D-Daten (Wellenlänge, Intensitäten, Z-Indices) zurück.

        Returns:
            tuple[np.ndarray, np.ndarray, list[int]]: 
            (Wellenlängen, Intensitäts-Datenmatrix (2D), Z-Indices).
            Gibt leere Arrays/Listen zurück, wenn keine Daten vorhanden sind.
        """
        if not self.data_buffer:
            return np.array([]), np.array([]), []
        
        data_matrix = np.vstack(self.data_buffer)

        return self.wavelengths, data_matrix, self.z_indices
    
    @Slot(object, object)
    def add_spectrum(self, wavelengths: np.ndarray, intensities: np.ndarray):
        """
        Slot: Fügt dem Waterfall-Puffer ein neues Spektrum hinzu.

        Diese Methode ist dazu gedacht, mit dem Signal 
        `SpectrometerManager.new_spectrum_acquired` verbunden zu werden.

        Args:
            wavelengths (np.ndarray): Wellenlängen des Spektrums (X-Achse).
            intensities (np.ndarray): Intensitäten des Spektrums (Y-Achse).

        .. note::
            Das Wellenlängen-Array wird nur beim ersten Aufruf gespeichert.
            Bei späteren Aufrufen wird nur die Länge des Intensitäts-Arrays
            überprüft, um Konsistenz sicherzustellen.
        """

        if intensities is None or len(intensities) == 0:
            self.log_mgr.warning("Received empty or invalid spectrum. Skipping addition to Waterfall.")
            return
        
        if self.z_counter == 0:
            self.wavelengths = wavelengths
            self.log_mgr.debug(f"Waterfall initialized with {len(wavelengths)} data points.")
        
        elif len(intensities) != len(self.wavelengths):
            self.log_mgr.error(f"New spectrum size ({len(intensities)}) does not match previous size ({len(self.wavelengths)}). Skipping.")
            return
        
        self.data_buffer.append(intensities)
        self.z_counter += 1
        self.z_indices.append(self.z_counter)
        
        self.log_mgr.debug(f"Spectrum #{self.z_counter} added to Waterfall buffer.")

        data_matrix = np.vstack(self.data_buffer)
        self.waterfall_data_updated.emit(self.z_indices, data_matrix)

    @Slot()
    def clear_data(self):
        """
        Löscht alle akkumulierten Spektrendaten und setzt den Zähler zurück.
        
        Löst das `waterfall_cleared`-Signal aus.
        """
        self.wavelengths = np.array([])
        self.data_buffer = []
        self.z_indices = []
        self.z_counter = 0
        self.log_mgr.info("Waterfall data buffer cleared.")
        self.waterfall_cleared.emit()

    def save_raw_data(self, filepath: str, format: str = 'csv') -> bool:
        """
        Exportiert die gesamten 3D-Rohdaten (Wellenlänge, Intensitäten, Z-Index) in eine Datei.

        Unterstützte Formate: 'csv', 'npy'.

        Args:
            filepath (str): Der vollständige Pfad zur Zieldatei.
            format (str): Das gewünschte Exportformat ('csv' oder 'npy').

        Returns:
            bool: True bei erfolgreichem Export, sonst False.

        Examples:
            Daten als CSV speichern:
            
            .. code-block:: python
            
                success = waterfall_mgr.save_raw_data("/pfad/zu/daten.csv", format="csv")
                
            Daten als NumPy Binärdatei (schnell):
            
            .. code-block:: python
            
                success = waterfall_mgr.save_raw_data("/pfad/zu/daten.npy", format="npy")
        """
        if not self.data_buffer:
            self.log_mgr.warning("No data to export.")
            return False
        
        wl, data_matrix, z = self.get_waterfall_data()
        
        try:
            if format.lower() == 'csv':
                # Speichert in einem lesbaren CSV-Format: 
                # Erste Zeile: Wellenlängen
                # Nachfolgende Zeilen: [Z_Index, Intensität_1, Intensität_2, ...]
                
                # Zuerst Wellenlängen-Header vorbereiten
                header_line = ["Z_Index"] + [f"WL_{w:.2f}" for w in wl]
                
                # Daten mit Z-Index zusammenführen
                z_column = np.array(z).reshape(-1, 1)
                full_data = np.hstack((z_column, data_matrix))
                
                # Speichern
                np.savetxt(filepath, full_data, delimiter=",", header=", ".join(header_line), comments='', fmt='%.5f')
                self.log_mgr.info(f"Waterfall data saved to CSV: {filepath}")
                
            elif format.lower() == 'npy':
                # Speichert die Daten als unkomprimiertes NumPy-Tupel (wl, data_matrix, z_indices)
                np.save(filepath, (wl, data_matrix, np.array(z)))
                self.log_mgr.info(f"Waterfall data saved to NumPy file: {filepath}")
                
            else:
                self.log_mgr.error(f"Unsupported export format: {format}")
                return False
            
            return True
        except Exception as e:
            self.log_mgr.error(f"Error exporting waterfall data: {e}")
            return False
            
    def save_plot_image(self, figure: Figure, filepath: str) -> bool:
        """
        Speichert die aktuelle Matplotlib-Abbildung des Waterfalls in eine Bilddatei.

        Args:
            figure (matplotlib.figure.Figure): Die zu speichernde Matplotlib-Figure-Instanz.
            filepath (str): Der vollständige Pfad zur Zieldatei (unterstützt: .png, .svg, .pdf).

        Returns:
            bool: True bei Erfolg, sonst False.
        """
        try:
            figure.savefig(filepath, bbox_inches='tight', dpi=300)
            self.log_mgr.info(f"Waterfall plot saved to: {filepath}")
            return True
        except Exception as e:
            self.log_mgr.error(f"Error saving plot image: {e}")
            return False