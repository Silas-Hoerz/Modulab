from PySide6.QtCore import QObject, Signal, Slot

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

    Diese Klasse dient als "Dolmetscher" zwischen der Hardware (Seabreeze Bibliothek)
    und der Benutzeroberfläche. Sie kümmert sich um Verbindung, Einstellungen und
    die korrekte mathematische Verrechnung von Dunkelspektren.

    Args:
        log_manager (LogManager): Eine Klasse zum Schreiben von Log-Nachrichten (Info/Error).
        profile_manager (ProfileManager): Eine Klasse zum Speichern/Laden von Einstellungen.

    Signale (Events für die GUI):
        connection_status_changed (bool, str): 
            Wird gefeuert, wenn sich die Verbindung ändert. 
            Gibt (IstVerbunden, Gerätename) zurück.
        
        device_list_updated (list): 
            Wird gefeuert, wenn nach Geräten gesucht wurde. 
            Gibt eine Liste mit Namen zurück (z.B. ["FLAME (SN123)", ...]).
            
        new_spectrum_acquired (numpy.ndarray, numpy.ndarray): 
            Wird gefeuert, wenn eine *rohe* Messung abgeschlossen ist.
            Gibt (Wellenlängen, Intensitäten) zurück.

        dark_measurement_progress (object, object, int): 
            Wird während der Dunkel-Messung laufend gefeuert.
            Gibt (Wellenlängen, Aktueller Durchschnitt, Fortschritt in %) zurück.
    """

    # Definition der Signale
    connection_status_changed = Signal(bool, str)
    device_list_updated = Signal(list)
    new_spectrum_acquired = Signal(object, object) 
    dark_measurement_progress = Signal(object, object, int) 

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager 
        self.profile_mgr = profile_manager

        self.log_mgr.debug("Initializing SpectrometerManager...")

        self.spectrometer = None
        self.available_devices = []
        self.device_name_map = {}

        # WICHTIG: Hier NICHT mehr laden!
        # Sondern auf das Signal warten.
        self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

        # Standardwerte initialisieren (damit der Code nicht crasht, bevor Profil da ist)
        self.correct_dark_counts = False
        self.correct_non_linearity = False
        self.current_integration_time_us = 100000 
        self.current_temperature_C = -15
        self.LastDevice = None
        
        # Initialer Scan (Hardware suchen darf man immer)
        self.get_deviceList()

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        """Wird aufgerufen, sobald ein Profil erfolgreich geladen wurde."""
        self.log_mgr.info(f"SpectrometerManager loading settings from '{profile_name}'...")

        # Jetzt erst laden!
        self.correct_dark_counts = self.profile_mgr.read("Spec_correct_dark_counts")
        self.correct_non_linearity = self.profile_mgr.read("Spec_non_linearity")
        self.current_integration_time_us = self.profile_mgr.read("Spec_integration_time_us")
        self.current_temperature_C = self.profile_mgr.read("Spec_temperature_C")
        self.LastDevice = self.profile_mgr.read("Spec_LastDevice")

        # Fallbacks (falls im Profil noch nichts steht)
        if self.correct_dark_counts is None: self.set_correction_dark_count(False)
        if self.correct_non_linearity is None: self.set_correction_non_linearity(False)
        if self.current_integration_time_us is None: self.set_integrationtime(100000)
        if self.current_temperature_C is None: self.set_temperature(-15)

        # Auto-Connect Versuch (erst jetzt, wo wir LastDevice kennen)
        if self.LastDevice:
            self.log_mgr.info(f"Last connected spectrometer (SN): {self.LastDevice}. Attempting re-connect...")
            self.connect_LastDevice()
        else:
            self.log_mgr.info("No last spectrometer saved in this profile.")

    # --- Verbindungs- und Geräte-Verwaltung ---

    def get_deviceList(self) -> list:
        """
        Sucht nach angeschlossenen Spektrometern (via USB).

        Diese Funktion aktualisiert die interne Liste und sendet das Signal
        `device_list_updated`, damit z.B. eine ComboBox in der GUI gefüllt werden kann.

        Returns:
            list: Eine Liste von Namen, z.B. ["FLAME (SN123)", "USB2000 (SN999)"].

        Example:
            >>> devices = manager.get_deviceList()
            >>> print(devices)
            ['FLAME (SN12345)']
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
        Verbindet den Manager mit einem konkreten Spektrometer.

        Wenn erfolgreich, werden gespeicherte Einstellungen (Integrationszeit, Temperatur)
        direkt auf das Gerät angewendet.

        Args:
            device_name_or_serial (str): Der Name aus der Liste (z.B. "FLAME (SN...)") 
                                         oder direkt die Seriennummer.

        Returns:
            bool: True, wenn die Verbindung geklappt hat, sonst False.

        Example:
            >>> manager.connect("FLAME (SN12345)")
            True
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
            if self.profile_mgr.get_current_profile_name():
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
        Verbindet automatisch das zuletzt genutzte Gerät.

        Returns:
            bool: True bei Erfolg.
        """
        if self.LastDevice:
            return self.connect(self.LastDevice)
        else:
            self.log_mgr.warning("No 'LastDevice' found to connect to.")
            return False
        
    def disconnect(self):
        """
        Trennt die Verbindung und gibt das Gerät frei.
        
        Wichtig: Das gespeicherte Dunkelspektrum wird hierbei gelöscht, da es
        für ein neues Gerät (oder nach Neustart) nicht mehr gültig wäre.
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
        Gibt den Namen des aktuell verbundenen Geräts zurück.

        Returns:
            str: Name (z.B. "FLAME (SN123)") oder leerer String "", wenn nicht verbunden.
        """
        if self.spectrometer:
            return f"{self.spectrometer.model} ({self.spectrometer.serial_number})"
        return ""
    
    def is_connected(self) -> bool: 
        """
        Prüft, ob aktuell eine Verbindung besteht.

        Returns:
            bool: True = Verbunden, False = Getrennt.
        """
        return self.spectrometer is not None
    
    # --- Konfiguration - Getter & Setter ---

    def set_correction_dark_count(self, enable: bool):
        """ 
        Schaltet die hardwareseitige 'Electric Dark Correction' an oder aus.
        
        Info: Dies nutzt abgedunkelte Pixel am Rand des Sensors, um elektrisches
        Rauschen abzuziehen. Das ist NICHT das gleiche wie der Abzug eines
        kompletten Dunkelspektrums (welches Streulicht korrigiert).

        Wichtig: Eine Änderung macht das gespeicherte Dunkelspektrum ungültig!

        Args:
            enable (bool): True = An, False = Aus.
        
        Example:
            >>> manager.set_correction_dark_count(True)
        """
        if self.correct_dark_counts != enable:
            self.correct_dark_counts = enable
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write("Spec_correct_dark_counts", enable)
            self.log_mgr.info(f"Dark count correction set to: {enable}")
            self._invalidate_dark_spectrum()
    
    def get_correction_dark_count(self) -> bool:
        """Gibt zurück, ob Electric Dark Correction aktiv ist."""
        return self.correct_dark_counts
    
    def set_correction_non_linearity(self, enable: bool):
        """ 
        Schaltet die Linearitäts-Korrektur an oder aus.
        
        Info: Sensoren sind bei hoher Intensität oft nicht perfekt linear.
        Diese Funktion nutzt Kalibrierdaten im Gerät, um das auszugleichen.

        Wichtig: Eine Änderung macht das gespeicherte Dunkelspektrum ungültig!

        Args:
            enable (bool): True = An, False = Aus.
        """
        if self.correct_non_linearity != enable:
            self.correct_non_linearity = enable
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write("Spec_non_linearity", enable)
            self.log_mgr.info(f"Non-linearity correction set to: {enable}")
            self._invalidate_dark_spectrum()
    
    def get_correction_non_linearity(self) -> bool:
        """Gibt zurück, ob Linearitäts-Korrektur aktiv ist."""
        return self.correct_non_linearity

    def set_integrationtime(self, time_us: int) -> bool:
        """
        Setzt die Belichtungszeit (Integrationszeit) in Mikrosekunden.

        Die Zeit bestimmt, wie lange der Sensor Licht sammelt.
        - Längere Zeit = Mehr Signal (heller), aber langsamer.
        - Kürzere Zeit = Weniger Signal (dunkler), aber schneller.

        Die Funktion begrenzt den Wert automatisch auf das, was das Gerät kann (z.B. min 1000us).
        Eine Änderung löscht das gespeicherte Dunkelspektrum, da sich das Rauschen ändert.

        Args:
            time_us (int): Zeit in Mikrosekunden (1 ms = 1000 us).

        Returns:
            bool: True, wenn erfolgreich gesetzt.

        Example:
            >>> # Setze auf 100 Millisekunden
            >>> manager.set_integrationtime(100000)
        """
        if not self.is_connected():
            self.log_mgr.info(f"Storing integration time ({time_us} us) for next connect.")
            self.current_integration_time_us = time_us
            if self.profile_mgr.get_current_profile_name():
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
                if self.profile_mgr.get_current_profile_name():
                    self.profile_mgr.write("Spec_integration_time_us", clamped_us)
                self.log_mgr.info(f"Integration time set to {self.current_integration_time_us} us.")
                self._invalidate_dark_spectrum()
            return True

        except Exception as e:
            self.log_mgr.error(f"Error setting integration time: {e}")
            return False
    
    def get_integrationtime(self) -> int:
        """Gibt die aktuelle Integrationszeit in Mikrosekunden (µs) zurück."""
        return self.current_integration_time_us

    def get_integrationtime_limits_us(self) -> tuple[int, int]:
        """
        Fragt die Hardware, welche Zeiten minimal und maximal möglich sind.

        Returns:
            tuple: (Minimum_us, Maximum_us). Gibt (0,0) zurück bei Fehler.
        
        Example:
            >>> min_t, max_t = manager.get_integrationtime_limits_us()
            >>> print(f"Bereich: {min_t} bis {max_t}")
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
        Gibt zurück, bei welchem Wert der Sensor "voll" ist (Sättigung).
        Meistens 65535 (16-bit) oder ca. 4000 (12-bit).

        Returns:
            float: Maximaler Intensitätswert.
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
        Setzt die Ziel-Temperatur für die Kühlung (TEC).
        KORRIGIERT: Greift jetzt korrekt auf das erste Element der Feature-Liste zu.
        """
        self.current_temperature_C = temperature_degC
        if self.profile_mgr.get_current_profile_name():
            self.profile_mgr.write("Spec_temperature_C", temperature_degC)
        self._invalidate_dark_spectrum()
        
        if self.is_connected():
            try:
                # Prüfen auf TEC Feature
                if hasattr(self.spectrometer, 'features') and 'thermo_electric' in self.spectrometer.features:
                    # WICHTIG: Das Dictionary gibt eine LISTE zurück. Wir brauchen das erste Element [0].
                    tec_features = self.spectrometer.features['thermo_electric']
                    
                    if tec_features:
                        tec = tec_features[0] # <--- HIER WAR DER FEHLER
                        
                        # 1. Setpoint setzen
                        tec.set_temperature_setpoint_degrees_celsius(temperature_degC)
                        
                        # 2. TEC aktivieren
                        tec.enable_tec(True)
                        
                        self.log_mgr.info(f"TEC Temperature setpoint set to {temperature_degC}°C")
                    else:
                        self.log_mgr.warning("Thermo-electric feature found, but list is empty.")

                else:
                    self.log_mgr.info(f"Temperature value {temperature_degC}°C stored (Hardware control not available).")
            except Exception as e:
                self.log_mgr.error(f"Error setting temperature: {e}")

    def get_temperature(self) -> float:
        """
        Liest die aktuelle Temperatur des Sensors aus.
        KORRIGIERT: Greift jetzt korrekt auf das erste Element der Feature-Liste zu.
        """
        if self.is_connected():
            try:
                # 1. Versuch: TEC Temperatur (Detektor)
                if hasattr(self.spectrometer, 'features') and 'thermo_electric' in self.spectrometer.features:
                    tec_features = self.spectrometer.features['thermo_electric']
                    if tec_features:
                        # HIER WAR DER FEHLER: Zugriff auf [0] nötig
                        return tec_features[0].read_temperature_degrees_celsius()
                
                # 2. Versuch: PCB Temperatur (Fallback)
                elif hasattr(self.spectrometer, 'features') and 'temperature' in self.spectrometer.features:
                     # Das 'temperature' Feature gibt oft direkt eine Liste von Floats zurück
                     temps = self.spectrometer.features['temperature'].get_temperatures_degrees_celsius()
                     if temps: 
                         return temps[0]
                     
            except Exception as e:
                # Wir loggen das nur als Debug, um den Log nicht vollzuspammen, wenn es jede Sekunde passiert
                self.log_mgr.debug(f"Could not read HW temperature: {e}")
        
        # Fallback auf gespeicherten Wert
        return self.current_temperature_C if self.current_temperature_C is not None else 0.0
    
    def _invalidate_dark_spectrum(self):
        """
        Interne Hilfsfunktion: 
        Löscht das Dunkelspektrum automatisch, wenn sich Parameter ändern 
        (z.B. Integrationszeit geändert -> Altes Dunkelbild passt nicht mehr).
        """
        if self._dark_spectrum_avg is not None:
            self.clear_dark_spectrum()
            self.log_mgr.warning("Dark spectrum invalidated due to parameter change.")

    def clear_dark_spectrum(self):
        """
        Löscht das gespeicherte Dunkelspektrum manuell.
        Nach Aufruf dieser Funktion wird keine Subtraktion mehr durchgeführt,
        bis ein neues Dunkelspektrum aufgenommen wird.
        
        Example:
            >>> manager.clear_dark_spectrum()
        """
        if self._dark_spectrum_avg is not None:
            self._dark_spectrum_avg = None
            self._dark_spectrum_raw_list = []
            self.log_mgr.info("Dark spectrum cleared.")
    
    # --- Daten Erhebung & Dark Spectrum ---

    def get_dark_spectrum_average(self) -> np.ndarray | None:
        """
        Gibt das aktuell gespeicherte Dunkelspektrum (Durchschnitt) zurück.
        
        Nützlich, um es in Dateien abzuspeichern oder anzuzeigen.

        Returns:
            np.ndarray: Array der Intensitäten (oder None, wenn keins existiert).
        """
        return self._dark_spectrum_avg

    def get_dark_spectrum_raw(self) -> list[np.ndarray]:
        """
        Gibt ALLE Einzelmessungen zurück, aus denen der Durchschnitt berechnet wurde.
        Nützlich für statistische Auswertungen (Standardabweichung etc.).

        Returns:
            list: Eine Liste von Numpy-Arrays.
        """
        return self._dark_spectrum_raw_list

    def acquire_spectrum(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Nimmt ein Spektrum auf und zieht automatisch das Dark Spectrum ab.

        Returns:
            tuple: (Wellenlängen, Korrigierte Intensitäten).
        """
        if self._dark_spectrum_avg is None:
            self.log_mgr.warning("Cannot acquire corrected spectrum: No valid dark spectrum available.")
            return None, None

        wl, inten = self.acquire_spectrum_raw(emit_signal=False) 
        
        if wl is None:
            return None, None

        try:
            if inten.shape != self._dark_spectrum_avg.shape:
                self.log_mgr.error("Shape mismatch between measurement and dark spectrum. Invalidating dark.")
                self._invalidate_dark_spectrum()
                return None, None

            corrected_intensities = inten - self._dark_spectrum_avg
            
            self.new_spectrum_acquired.emit(wl, corrected_intensities)
            
            return wl, corrected_intensities

        except Exception as e:
            self.log_mgr.error(f"Error calculating dark-corrected spectrum: {e}")
            return None, None

    def acquire_spectrum_raw(self, emit_signal: bool = True) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Führt eine rohe Messung durch, OHNE etwas abzuziehen.
        
        Args:
            emit_signal (bool): Wenn True, wird das 'new_spectrum_acquired' Signal gesendet.
                                Wenn False, geschieht das nicht (wichtig für interne Aufrufe).

        Returns:
            tuple: (Wellenlängen, Rohe Intensitäten).
        """
        if not self.is_connected():
            self.log_mgr.warning("Cannot acquire spectrum: No spectrometer connected.")
            return None, None
        
        try:
            wavelengths, intensities = self.spectrometer.spectrum(
                correct_dark_counts=self.correct_dark_counts,
                correct_nonlinearity=self.correct_non_linearity
            )
            
            if emit_signal:
                self.new_spectrum_acquired.emit(wavelengths, intensities)

            return wavelengths, intensities
        
        except Exception as e:
            self.log_mgr.error(f"Error during spectrum acquisition: {e}")
            return None, None
        

    def acquire_dark_spectrum(self, n_scans: int) -> bool:
        """
        Startet den Prozess zur Aufnahme eines Dunkelspektrums.
        
        Dabei wird der Shutter (falls vorhanden) meist manuell geschlossen oder
        die Lichtquelle ausgeschaltet (muss der User machen!).
        Die Funktion misst `n_scans` mal, mittelt alle Messungen und speichert
        das Ergebnis als Referenz für `acquire_spectrum`.

        Args:
            n_scans (int): Wie viele Messungen sollen gemittelt werden? (z.B. 10).
                           Mehr Scans = Weniger Rauschen im Dunkelbild.

        Returns:
            bool: True bei Erfolg.

        Example:
            >>> # Lichtquelle aus!
            >>> manager.acquire_dark_spectrum(10)
            >>> # Jetzt ist das Dunkelbild gespeichert.
        """
        if not self.is_connected():
            self.log_mgr.error("Cannot measure dark spectrum: No connection.")
            return False

        if n_scans < 1:
            self.log_mgr.error("n_scans must be >= 1")
            return False

        self.log_mgr.info(f"Starting dark spectrum measurement ({n_scans} scans)...")
        
        # Reset Speicher
        self._dark_spectrum_raw_list = []
        self._dark_spectrum_avg = None
        
        try:
            wavelengths = None
            
            for i in range(n_scans):
                # Messung (direkt vom Device)
                wl, inten = self.spectrometer.spectrum(
                    correct_dark_counts=self.correct_dark_counts,
                    correct_nonlinearity=self.correct_non_linearity
                )
                wavelengths = wl
                
                # Speichern
                self._dark_spectrum_raw_list.append(inten)
                
                # Live-Durchschnitt berechnen für die Anzeige
                current_stack = np.vstack(self._dark_spectrum_raw_list)
                current_avg = np.mean(current_stack, axis=0)
                
                # Signal senden (für Fortschrittsbalken/Plot)
                progress_pct = int(((i + 1) / n_scans) * 100)
                self.dark_measurement_progress.emit(wl, current_avg, progress_pct)
                
            # Endergebnis berechnen und speichern
            self._dark_spectrum_avg = np.mean(np.vstack(self._dark_spectrum_raw_list), axis=0)
            self.log_mgr.info("Dark spectrum measurement completed.")
            return True

        except Exception as e:
            self.log_mgr.error(f"Error measuring dark spectrum: {e}")
            self._invalidate_dark_spectrum()
            return False