from PySide6.QtCore import QObject, Signal

# https://python-seabreeze.readthedocs.io/en/latest/api.html#seabreeze.spectrometers.Spectrometer
import seabreeze
seabreeze.use('cseabreeze')
from seabreeze.spectrometers import Spectrometer, list_devices
import numpy as np

# ==========================================================================================
# Manager
# ==========================================================================================

class SpectrometerManager(QObject):
    """
    Manager zur Steuerung und Verwaltung von Ocean Optics Spektrometern.

    Diese Klasse kapselt die `python-seabreeze`-Bibliothek, um eine stabile
    Schnittstelle für die Geräteverbindung, Konfiguration (Integrationszeit, 
    Korrekturen, Temperatur) und Datenaufnahme (Spektren) bereitzustellen.
    Zusätzlich verwaltet sie die Erfassung und Subtraktion von Dunkelspektren.

    Args:
        log_manager (LogManager): Eine Instanz eines Log-Managers (erwartet .info, .error, etc.).
        profile_manager (ProfileManager): Eine Instanz zur Verwaltung von App-Einstellungen.

    Signals:
        connection_status_changed (bool, str): 
            Wird bei Änderung des Verbindungsstatus ausgelöst.
            (Verbunden [bool], Gerätename [str])
        
        device_list_updated (list): 
            Wird nach Aktualisierung der Geräteliste ausgelöst.
            (Liste der Gerätenamen [list[str]])
            
        new_spectrum_acquired (numpy.ndarray, numpy.ndarray): 
            Wird ausgelöst, wenn ein *rohes* Spektrum (acquire_spectrum_raw) gemessen wurde.
            (Wellenlängen [ndarray], Intensitäten [ndarray])

        dark_measurement_progress (object, object, int): 
            Fortschritt der Dunkelspektrum-Messung.
            (Wellenlängen [ndarray], Aktueller Average [ndarray], Fortschritt in % [int])
    """

    # Signale Definitionen
    connection_status_changed = Signal(bool, str)
    device_list_updated = Signal(list)
    new_spectrum_acquired = Signal(object, object) 
    dark_measurement_progress = Signal(object, object, int) 

    def __init__(self, log_manager, profile_manager):
        """
        Initialisiert den SpectrometerManager.

        Lädt die zuletzt verwendete Konfiguration aus dem ProfileManager und 
        versucht automatisch, eine Verbindung zum zuletzt verwendeten Gerät herzustellen.
        """
        super().__init__()
        self.log_mgr = log_manager 
        self.profile_mgr = profile_manager

        self.log_mgr.debug("Initializing SpectrometerManager...")

        self.spectrometer = None
        self.available_devices = []
        self.device_name_map = {}

        # Speicher für Dark-Spektren
        self._dark_spectrum_avg = None      # Das gemittelte Spektrum (numpy array)
        self._dark_spectrum_raw_list = []   # Liste aller Einzelmessungen

        # Zuletzt verwendete Konfiguration laden
        self.correct_dark_counts = self.profile_mgr.read("Spec_correct_dark_counts")
        self.correct_non_linearity = self.profile_mgr.read("Spec_non_linearity")
        self.current_integration_time_us = self.profile_mgr.read("Spec_integration_time_us")
        self.current_temperature_C = self.profile_mgr.read("Spec_temperature_C")
        self.LastDevice = self.profile_mgr.read("Spec_LastDevice")

        # Fallbacks setzen, falls Profile leer sind
        if self.correct_dark_counts is None:
            self.set_correction_dark_count(False)

        if self.correct_non_linearity is None:
            self.set_correction_non_linearity(False)

        if self.current_integration_time_us is None:
            self.set_integrationtime(100 * 1000) # Standard 100ms

        if self.current_temperature_C is None:
            self.set_temperature(-15) # Standard -15°C

        # Auto-Connect Versuch
        if self.LastDevice:
            self.log_mgr.info(f"Last connected spectrometer (SN): {self.LastDevice}. Attempting re-connect...")
            self.connect_LastDevice()
        else:
            self.log_mgr.info("No last spectrometer saved. Please connect manually.")
            self.get_deviceList()

    # --- Interne Hilfsfunktionen ---

    def _invalidate_dark_spectrum(self):
        #"""
        #Interner Helper: Löscht das Dunkelspektrum und loggt eine Warnung.
        #Wird aufgerufen, wenn messrelevante Parameter (Zeit, Temp, etc.) geändert werden.
        #"""
        if self._dark_spectrum_avg is not None:
            self.clear_dark_spectrum()
            self.log_mgr.warning("Dark spectrum invalidated due to parameter change.")

    def clear_dark_spectrum(self):
        """
        Löscht das aktuell gespeicherte Dunkelspektrum manuell.

        Setzt den Durchschnitt und die Rohdaten-Liste zurück.
        """
        if self._dark_spectrum_avg is not None:
            self._dark_spectrum_avg = None
            self._dark_spectrum_raw_list = []
            self.log_mgr.info("Dark spectrum cleared.")

    # --- Verbindungs- und Geräte-Verwaltung ---

    def get_deviceList(self) -> list:
        """
        Scannt nach verfügbaren Spektrometern.

        Aktualisiert die interne Geräteliste und emittiert `device_list_updated`.

        Returns:
            list: Liste formatierter Gerätenamen (z.B. ["FLAME (SN123)", ...]).
        """
        device_names = []
        try:
            self.available_devices = list_devices()
            self.device_name_map.clear()

            if not self.available_devices:
                self.log_mgr.warning("No spectrometer found.")
            else:
                self.log_mgr.debug(f"{len(self.available_devices)} spectrometer(s) found.")
                for dev in self.available_devices:
                    name = f"{dev.model} ({dev.serial_number})"
                    device_names.append(name)
                    self.device_name_map[name] = dev

        except Exception as e:
            self.log_mgr.error(f"Error listing spectrometers: {e}")
            self.available_devices = []
            self.device_name_map.clear()
        
        self.device_list_updated.emit(device_names)
        return device_names
    
    def connect(self, device_name_or_serial: str) -> bool:
        """
        Verbindet zu einem Spektrometer.

        Argument kann der Anzeigename oder die Seriennummer sein.
        Stellt bei Erfolg auch Integrationszeit und Temperatur wieder her.

        Args:
            device_name_or_serial (str): Name aus `get_deviceList` oder Seriennummer.

        Returns:
            bool: True bei Erfolg, sonst False.
        """
        self.disconnect()
        dev_to_connect = None
        try:
            if device_name_or_serial in self.device_name_map:
                dev_to_connect = self.device_name_map[device_name_or_serial]
                self.spectrometer = Spectrometer(dev_to_connect)
            else:
                self.spectrometer = Spectrometer.from_serial_number(device_name_or_serial)
            
            active_name = self.get_activeDeviceName()
            self.LastDevice = self.spectrometer.serial_number
            self.profile_mgr.write("Spec_LastDevice", self.LastDevice)
            self.log_mgr.info(f"Successfully connected to {active_name}")
            
            # Wende Einstellungen an
            self.set_integrationtime(self.current_integration_time_us)

            if self.current_temperature_C is not None:
                self.set_temperature(self.current_temperature_C)
            
            self.connection_status_changed.emit(True, active_name)
            return True

        except Exception as e:
            self.log_mgr.error(f"Connection failed: {e}")
            self.spectrometer = None
            self.connection_status_changed.emit(False, "")
            return False
        
    def connect_LastDevice(self) -> bool:
        """
        Versucht, das zuletzt genutzte Gerät (aus Profile) zu verbinden.

        Returns:
            bool: True bei Erfolg, False wenn kein Gerät gespeichert oder Fehler.
        """
        if self.LastDevice:
            return self.connect(self.LastDevice)
        else:
            self.log_mgr.warning("No 'LastDevice' found to connect to.")
            return False
        
    def disconnect(self):
        """
        Trennt die Verbindung zum aktuellen Spektrometer.

        Schließt die Hardware-Ressource und invalidiert das Dunkelspektrum.
        """
        if self.spectrometer:
            try:
                self.spectrometer.close()
            except Exception as e:
                self.log_mgr.error(f"Error closing spectrometer: {e}")
            self.spectrometer = None
            self._invalidate_dark_spectrum()
            self.connection_status_changed.emit(False, "")

    def get_activeDeviceName(self) -> str:
        """
        Liefert den Namen des aktuell verbundenen Geräts.

        Returns:
            str: "Model (Serial)" oder leerer String.
        """
        if self.spectrometer:
            return f"{self.spectrometer.model} ({self.spectrometer.serial_number})"
        return ""
    
    def is_connected(self) -> bool: 
        """
        Prüft den Verbindungsstatus.

        Returns:
            bool: True wenn verbunden.
        """
        return self.spectrometer is not None
    
    # --- Konfiguration - Getter & Setter ---

    def set_correction_dark_count(self, enable: bool):
        """ 
        Aktiviert/Deaktiviert die hardwareseitige Dunkelstrom-Korrektur (Electric Dark).
        
        Achtung: Dies ist NICHT die Subtraktion des Dunkelspektrums, sondern
        die Korrektur basierend auf verdunkelten Pixeln am Sensorrand.
        Macht das gespeicherte Dunkelspektrum ungültig.

        Args:
            enable (bool): True zum Aktivieren.
        """
        if self.correct_dark_counts != enable:
            self.correct_dark_counts = enable
            self.profile_mgr.write("Spec_correct_dark_counts", enable)
            self.log_mgr.info(f"Dark count correction set to: {enable}")
            self._invalidate_dark_spectrum()
    
    def get_correction_dark_count(self) -> bool:
        """Gibt den Status der hardwareseitigen Dunkelstrom-Korrektur zurück."""
        return self.correct_dark_counts
    
    def set_correction_non_linearity(self, enable: bool):
        """ 
        Aktiviert/Deaktiviert die Linearitäts-Korrektur.
        
        Macht das gespeicherte Dunkelspektrum ungültig.

        Args:
            enable (bool): True zum Aktivieren.
        """
        if self.correct_non_linearity != enable:
            self.correct_non_linearity = enable
            self.profile_mgr.write("Spec_non_linearity", enable)
            self.log_mgr.info(f"Non-linearity correction set to: {enable}")
            self._invalidate_dark_spectrum()
    
    def get_correction_non_linearity(self) -> bool:
        """Gibt den Status der Linearitäts-Korrektur zurück."""
        return self.correct_non_linearity

    def set_integrationtime(self, time_us: int) -> bool:
        """
        Setzt die Integrationszeit in Mikrosekunden.

        Begrenzt den Wert automatisch auf die Hardware-Limits.
        Speichert den Wert auch bei getrennter Verbindung für den nächsten Connect.
        Macht das gespeicherte Dunkelspektrum ungültig.

        Args:
            time_us (int): Zeit in Mikrosekunden.

        Returns:
            bool: True bei Erfolg (oder Speicherung), False bei Fehler.
        """
        if not self.is_connected():
            self.log_mgr.info(f"Storing integration time ({time_us} us) for next connect.")
            self.current_integration_time_us = time_us
            self.profile_mgr.write("Spec_integration_time_us", time_us)
            self._invalidate_dark_spectrum()
            return True
        
        try:
            min_us, max_us = self.spectrometer.integration_time_micros_limits 
            
            # Zeit auf min max begrenzen
            clamped_us = max(min_us, min(time_us, max_us))

            if clamped_us != time_us:
                self.log_mgr.warning(f"Desired time {time_us} us is outside limits ({min_us}-{max_us}). "
                                     f"Setting to {clamped_us} us.")
            
            if self.current_integration_time_us != clamped_us:
                self.spectrometer.integration_time_micros(clamped_us)
                self.current_integration_time_us = clamped_us
                self.profile_mgr.write("Spec_integration_time_us", clamped_us)
                self.log_mgr.info(f"Integration time set to {self.current_integration_time_us} us.")
                self._invalidate_dark_spectrum()
            return True

        except Exception as e:
            self.log_mgr.error(f"Error setting integration time: {e}")
            return False
    
    def get_integrationtime(self) -> int:
        """Gibt die aktuelle Integrationszeit in µs zurück."""
        return self.current_integration_time_us

    def get_integrationtime_limits_us(self) -> tuple[int, int]:
        """
        Liest die Limits für die Integrationszeit aus dem Gerät.

        Returns:
            tuple[int, int]: (min_us, max_us) oder (0,0) bei Fehler/Disconnection.
        """
        if not self.is_connected():
            self.log_mgr.warning(f"Cannot read limits: No spectrometer connected.")
            return (0, 0)
        
        try:
            min_us, max_us = self.spectrometer.integration_time_micros_limits
            return (min_us, max_us)
        except Exception as e:
            self.log_mgr.error(f"Error reading integration time limits: {e}")
            return (0, 0)

    def get_max_intensity(self) -> float:
        """
        Gibt die Sättigungsgrenze des Detektors zurück (z.B. 65535).

        Returns:
            float: Maximale Intensität.
        """
        if not self.is_connected():
            return 65535.0 
        
        try:
            return self.spectrometer.max_intensity
        except Exception as e:
            self.log_mgr.error(f"Error reading max intensity: {e}")
            return 65535.0 
        
    def set_temperature(self, temperature_degC: float):
        """
        Setzt die Soll-Temperatur für TEC-gekühlte Spektrometer.

        Aktiviert automatisch das TEC, falls verfügbar.
        Macht das gespeicherte Dunkelspektrum ungültig.

        Args:
            temperature_degC (float): Temperatur in °C (z.B. -15.0).
        """
        self.current_temperature_C = temperature_degC
        self.profile_mgr.write("Spec_temperature_C", temperature_degC)
        self._invalidate_dark_spectrum()
        
        if self.is_connected():
            try:
                if hasattr(self.spectrometer, 'features') and 'thermo_electric' in self.spectrometer.features:
                    self.spectrometer.features['thermo_electric'].set_temperature_setpoint_degrees_celsius(temperature_degC)
                    self.spectrometer.features['thermo_electric'].enable_tec(True)
                    self.log_mgr.info(f"TEC Temperature setpoint set to {temperature_degC}°C")
                else:
                    self.log_mgr.info(f"Temperature value {temperature_degC}°C stored (Hardware control not available/supported).")
            except Exception as e:
                self.log_mgr.error(f"Error setting temperature: {e}")

    def get_temperature(self) -> float:
        """
        Liest die aktuelle Temperatur des Sensors/PCBs aus.

        Returns:
            float: Gemessene Temperatur in °C oder gesetzter Setpoint als Fallback.
        """
        if self.is_connected():
            try:
                # TEC Temperatur (genauer Sensor am Detektor)
                if hasattr(self.spectrometer, 'features') and 'thermo_electric' in self.spectrometer.features:
                    return self.spectrometer.features['thermo_electric'].get_temperature_degrees_celsius()
                # PCB Temperatur
                elif hasattr(self.spectrometer, 'features') and 'temperature' in self.spectrometer.features:
                     temps = self.spectrometer.features['temperature'].get_temperatures_degrees_celsius()
                     if temps: return temps[0]
            except Exception as e:
                self.log_mgr.debug(f"Could not read HW temperature: {e}")
        
        return self.current_temperature_C if self.current_temperature_C is not None else 0.0
    
    # --- Daten Erhebung & Dark Spectrum ---

    def get_dark_spectrum_average(self) -> np.ndarray | None:
        """
        Gibt das aktuell gültige, gemittelte Dunkelspektrum zurück.
        
        Returns:
            np.ndarray | None: Array der Intensitäten oder None.
        """
        return self._dark_spectrum_avg

    def get_dark_spectrum_raw(self) -> list[np.ndarray]:
        """
        Gibt die Liste aller Einzelmessungen der letzten Dunkelstrom-Erfassung zurück.

        Returns:
            list[np.ndarray]: Liste von Intensitäts-Arrays.
        """
        return self._dark_spectrum_raw_list

    def acquire_spectrum(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Nimmt ein Spektrum auf und zieht automatisch das Dark Spectrum ab.

        Voraussetzung: Ein valides Dark Spectrum muss existieren (via acquire_dark_spectrum).

        Returns:
            tuple: (Wellenlängen, Korrigierte Intensitäten) oder (None, None) bei Fehler.
        """
        if self._dark_spectrum_avg is None:
            self.log_mgr.warning("Cannot acquire corrected spectrum: No valid dark spectrum available.")
            return None, None
            
        wl, inten = self.acquire_spectrum_raw() 
        
        if wl is None:
            return None, None

        try:
            # 2. Subtraktion
            if inten.shape != self._dark_spectrum_avg.shape:
                self.log_mgr.error("Shape mismatch between measurement and dark spectrum. Invalidating dark.")
                self._invalidate_dark_spectrum()
                return None, None

            corrected_intensities = inten - self._dark_spectrum_avg
            
            # Optional: Negative Werte auf 0 setzen
            # corrected_intensities = np.clip(corrected_intensities, 0, None)
            
            return wl, corrected_intensities

        except Exception as e:
            self.log_mgr.error(f"Error calculating dark-corrected spectrum: {e}")
            return None, None

    def acquire_spectrum_raw(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Nimmt ein rohes Spektrum vom Gerät auf (ohne Dark-Abzug).
        
        Berücksichtigt lediglich die Hardware-Settings (Integration Time, Electric Dark, Non-Linearity).
        Emittiert das Signal `new_spectrum_acquired`.

        Returns:
            tuple: (Wellenlängen, Intensitäten) oder (None, None).
        """
        if not self.is_connected():
            self.log_mgr.warning("Cannot acquire spectrum: No spectrometer connected.")
            return None, None
        
        try:
            wavelengths, intensities = self.spectrometer.spectrum(
                correct_dark_counts=self.correct_dark_counts,
                correct_nonlinearity=self.correct_non_linearity
            )
            
            # Sende das Signal mit den neuen Daten
            self.new_spectrum_acquired.emit(wavelengths, intensities)

            return wavelengths, intensities
        
        except Exception as e:
            self.log_mgr.error(f"Error during spectrum acquisition: {e}")
            return None, None
        

    def acquire_dark_spectrum(self, n_scans: int) -> bool:
        """
        Führt eine Dunkelspektrum-Messung durch (Mehrfachmessung mit Mittelung).
        
        Der Fortschritt wird über das Signal `dark_measurement_progress` gemeldet.
        Das Ergebnis wird intern in `_dark_spectrum_avg` gespeichert.

        Args:
            n_scans (int): Anzahl der zu mittelnden Spektren (muss >= 1 sein).

        Returns:
            bool: True bei Erfolg, False bei Abbruch oder Fehler.
        """
        if not self.is_connected():
            self.log_mgr.error("Cannot measure dark spectrum: No connection.")
            return False

        if n_scans < 1:
            self.log_mgr.error("n_scans must be >= 1")
            return False

        self.log_mgr.info(f"Starting dark spectrum measurement ({n_scans} scans)...")
        
        # Reset storage
        self._dark_spectrum_raw_list = []
        self._dark_spectrum_avg = None
        
        try:
            wavelengths = None
            
            for i in range(n_scans):
                # Messung durchführen (direkt vom Device, um Signal-Spam zu vermeiden oder settings zu erzwingen)
                wl, inten = self.spectrometer.spectrum(
                    correct_dark_counts=self.correct_dark_counts,
                    correct_nonlinearity=self.correct_non_linearity
                )
                wavelengths = wl
                
                # Zu Rohdaten hinzufügen
                self._dark_spectrum_raw_list.append(inten)
                
                # Laufenden Durchschnitt berechnen für Live-View
                current_stack = np.vstack(self._dark_spectrum_raw_list)
                current_avg = np.mean(current_stack, axis=0)
                
                # Signal senden für Live-Plot
                progress_pct = int(((i + 1) / n_scans) * 100)
                self.dark_measurement_progress.emit(wl, current_avg, progress_pct)
                
                # Hinweis: Hier könnte 'QCoreApplication.processEvents()' nötig sein, 
                # falls dies im MainThread läuft, damit die GUI updated.

            # Abschluss-Berechnung
            self._dark_spectrum_avg = np.mean(np.vstack(self._dark_spectrum_raw_list), axis=0)
            self.log_mgr.info("Dark spectrum measurement completed.")
            return True

        except Exception as e:
            self.log_mgr.error(f"Error measuring dark spectrum: {e}")
            self._invalidate_dark_spectrum()
            return False