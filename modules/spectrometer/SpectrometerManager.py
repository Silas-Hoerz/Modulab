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
    Korrekturen) und Datenaufnahme (Spektren) bereitzustellen.
    Sie nutzt PySide6-Signale, um die GUI über Statusänderungen zu informieren.

    Args:
        log_manager (LogManager): Eine Instanz eines Log-Managers (erwartet .info, .error, etc.).
        profile_manager (ProfileManager): Eine Instanz zur Verwaltung von 
                                          App-Einstellungen (Lesen/Schreiben).

    Signale:
        connection_status_changed (bool, str):
            Wird ausgelöst, wenn sich der Verbindungsstatus ändert.
            Args: (bool: verbunden, str: Gerätename/IDN).
        
        device_list_updated (list):
            Wird ausgelöst, nachdem die Geräteliste aktualisiert wurde.
            Args: (list: Liste von Gerätenamen [str], z.B. ["FLAME (Q...)", ...]).
            
        new_spectrum_acquired (numpy.ndarray, numpy.ndarray):
            Wird ausgelöst, wenn ein neues Spektrum verfügbar ist.
            Args: (numpy.ndarray: Wellenlängen, numpy.ndarray: Intensitäten).
    """

    # Signale
    connection_status_changed = Signal(bool,str)
    device_list_updated = Signal(list)
    new_spectrum_acquired = Signal(object, object) # Intern als (ndarray, ndarray) behandelt
    
    def __init__(self, log_manager, profile_manager):
        """
        Initialisiert den SpectrometerManager.

        Lädt die zuletzt verwendete Konfiguration (Integrationszeit, Korrekturen)
        aus dem ProfileManager und versucht automatisch, eine Verbindung
        zum zuletzt verwendeten Gerät herzustellen.
        """
        super().__init__()
        self.log_mgr = log_manager 
        self.profile_mgr = profile_manager

        self.log_mgr.debug("Initializing SpectrometerManager...")

        self.spectrometer = None
        self.available_devices = []
        self.device_name_map = {}

        # Zuletzt verwendete Konfiguration laden
        self.correct_dark_counts = self.profile_mgr.read("Spec_correct_dark_counts")
        self.correct_non_linearity = self.profile_mgr.read("Spec_non_linearity")
        self.current_integration_time_us = self.profile_mgr.read("Spec_integration_time_us")
        self.LastDevice = self.profile_mgr.read("Spec_LastDevice") # gibt auf self.profile_mgr.write("Spec_LastDevice", value)

        if self.correct_dark_counts is None:
            self.set_correction_dark_count(False)

        if self.correct_non_linearity is None:
            self.set_correction_non_linearity(False)

        if self.current_integration_time_us is None:
            self.set_integrationtime(100 * 1000) # Standard 100ms

        self.LastDevice = self.profile_mgr.read("Spec_LastDevice") # gibt auf self.profile_mgr.write("Spec_LastDevice", value)

        if self.LastDevice:
            self.log_mgr.info(f"Last connected spectrometer (SN): {self.LastDevice}. Attempting re-connect...")
            self.connect_LastDevice()
        else:
            self.log_mgr.info("No last spectrometer saved. Please connect manually.")
            self.get_deviceList()


    # --- Verbindungs- und Geräte-Verwaltung ---

    def get_deviceList(self) -> list:
        """
        Scannt nach verfügbaren Spektrometern und aktualisiert die interne Liste.

        Verwendet `seabreeze.list_devices()` und erstellt eine Zuordnung (Map)
        von formatierten Gerätenamen zu Geräteinstanzen. Löst das 
        `device_list_updated`-Signal aus.

        Returns:
            list: Eine Liste formatierter Gerätenamen (z.B. ["Oceanoptics (O...)", "USB2000 (...)"]).

        Examples:
            Eine Geräteliste abrufen und in einer Combobox anzeigen:
            
            .. code-block:: python
            
                # Annahme: 'spectrometer_mgr' ist eine Instanz von SpectrometerManager
                # und 'ui.combo_devices' ist eine QComboBox.
                
                # Zuerst das Signal verbinden (z.B. in __init__ der GUI)
                spectrometer_mgr.device_list_updated.connect(
                    lambda devices: ui.combo_devices.addItems(devices)
                )
                
                # Manuell eine Aktualisierung auslösen
                ui.combo_devices.clear()
                spectrometer_mgr.get_deviceList()
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
            self.available_devices =[]
            self.device_name_map.clear()
        
        self.device_list_updated.emit(device_names)
        return device_names
    
    def connect(self, device_name_or_serial: str) -> bool:
        """
        Verbindet ein Spektrometer über seinen Namen oder seine Seriennummer.

        Trennt zuerst eine eventuell bestehende Verbindung.
        Speichert die Seriennummer bei Erfolg für die Wiederverbindung.

        Args:
            device_name_or_serial (str): 
                Kann entweder der formatierte Name aus `get_deviceList()` 
                (z.B. "FLAME (Q...)") oder die reine Seriennummer 
                (z.B. "Q...") sein.

        Returns:
            bool: True bei erfolgreicher Verbindung, sonst False.

        Examples:
            Verbindung über den formatierten Namen (z.B. aus einer Combobox):
            
            .. code-block:: python
            
                name = "FLAME (QEP20488)"
                success = spectrometer_mgr.connect(name)
                if success:
                    print("Verbunden mit", name)

            Verbindung direkt über die Seriennummer:
            
            .. code-block:: python
            
                serial = "QEP20488"
                spectrometer_mgr.connect(serial)
        """
        self.disconnect()
        dev_to_connect = None
        try:
            if device_name_or_serial in self.device_name_map:
                # Name (z.B. "FLAME (Q...)")
                dev_to_connect = self.device_name_map[device_name_or_serial]
                self.spectrometer = Spectrometer(dev_to_connect)
            else:
                # Seriennummer (z.B. "Q...")
                self.spectrometer = Spectrometer.from_serial_number(device_name_or_serial)
            
            active_name = self.get_activeDeviceName()
            self.LastDevice = self.spectrometer.serial_number
            self.profile_mgr.write("Spec_LastDevice",self.LastDevice)
            self.log_mgr.info(f"Successfully connected to {active_name}")
            
            # Wende zuletzt bekannte Einstellungen an
            self.set_integrationtime(self.current_integration_time_us)
            
            self.connection_status_changed.emit(True,active_name)
            return True

        except Exception as e:
            self.log_mgr.error(f"Connection failed: {e}")
            self.spectrometer= None
            self.connection_status_changed.emit (False, "")
            return False
        
    def connect_LastDevice(self) -> bool:
        """
        Versucht, die Verbindung mit dem zuletzt genutzten Gerät wiederherzustellen.

        Verwendet die im Profil gespeicherte Seriennummer (`self.LastDevice`).

        Returns:
            bool: True bei Erfolg, False, wenn kein Gerät gespeichert war 
                  oder die Verbindung fehlschlägt.
        """
        if self.LastDevice:
            return self.connect(self.LastDevice)
        else:
            self.log_mgr.warning("No 'LastDevice' found to connect to.")
            return False
        
    def disconnect(self):
        """
        Trennt die aktive Verbindung zum Spektrometer.
        
        Schließt das Gerät über `spectrometer.close()` und löst 
        `connection_status_changed` aus.
        """
        if self.spectrometer:
            try:
                self.spectrometer.close()
            except Exception as e:
                self.log_mgr.error(f"Error closing spectrometer: {e}")
            self.spectrometer = None
            self.connection_status_changed.emit(False,"")

    def get_activeDeviceName(self) -> str:
        """
        Gibt den formatierten Namen des aktuell verbundenen Geräts zurück.

        Returns:
            str: Der formatierte Gerätename (z.B. "FLAME (Q...)") 
                 oder "" (leer, wenn nicht verbunden).
        """
        if self.spectrometer:
            return f"{self.spectrometer.model} ({self.spectrometer.serial_number})"
        return ""
    
    def is_connected(self) -> bool: 
        """
        Prüft, ob eine aktive Verbindung zum Spektrometer besteht.

        Returns:
            bool: True, wenn verbunden, sonst False.
        """
        return self.spectrometer is not None
    
    # --- Konfiguration - Getter & Setter ---

    def set_correction_dark_count(self, enable: bool):
        """ 
        Aktiviert/Deaktiviert die Korrektur des Dunkelstroms (Dark Counts).

        Wenn aktiviert, wird der Durchschnittswert der elektrisch verdunkelten
        Pixel vom Spektrum abgezogen.

        Args:
            enable (bool): True, um die Korrektur zu aktivieren, False zum Deaktivieren.

        Examples:
            Dunkelstrom-Korrektur aktivieren:
            
            .. code-block:: python
            
                spectrometer_mgr.set_correction_dark_count(True)
        """
        self.correct_dark_counts = enable
        self.profile_mgr.write("Spec_correct_dark_counts", enable)
        self.log_mgr.info(f"Dark count correction set to: {enable}")
    
    def get_correction_dark_count(self) -> bool:
        """
        Gibt den aktuellen Status der Dunkelstrom-Korrektur zurück.

        Returns:
            bool: True, wenn die Korrektur aktiv ist.
        """
        return self.correct_dark_counts
    
    def set_correction_non_linearity(self, enable: bool):
        """ 
        Aktiviert/Deaktiviert die Nichtlinearitäts-Korrektur.

        Wenn aktiviert und vom Gerät unterstützt, werden die Messwerte
        anhand der im EEPROM gespeicherten Koeffizienten linearisiert.

        Args:
            enable (bool): True, um die Korrektur zu aktivieren, False zum Deaktivieren.

        Examples:
            Nichtlinearitäts-Korrektur deaktivieren:
            
            .. code-block:: python
            
                spectrometer_mgr.set_correction_non_linearity(False)
        """
        self.correct_non_linearity = enable
        self.profile_mgr.write("Spec_non_linearity", enable)
        self.log_mgr.info(f"Non-linearity correction set to: {enable}")
    
    def get_correction_non_linearity(self) -> bool:
        """
        Gibt den aktuellen Status der Nichtlinearitäts-Korrektur zurück.

        Returns:
            bool: True, wenn die Korrektur aktiv ist.
        """
        return self.correct_non_linearity

    def set_integrationtime(self, time_us: int) -> bool:
        """
        Stellt die Integrationszeit des Spektrometers in Mikrosekunden (us) ein.

        Die Zeit wird automatisch auf die vom Gerät unterstützten Hardware-Limits
        begrenzt (clamping). Die Einstellung wird auch im Profil gespeichert.

        Args:
            time_us (int): Die gewünschte Integrationszeit in Mikrosekunden.

        Returns:
            bool: True, wenn die Zeit erfolgreich gesetzt (oder zwischengespeichert)
                  wurde, False bei einem Hardware-Fehler.

        Examples:
            Integrationszeit auf 100 Millisekunden (100.000 µs) setzen:
            
            .. code-block:: python
            
                spectrometer_mgr.set_integrationtime(100 * 1000)

            Integrationszeit auf 2 Sekunden (2.000.000 µs) setzen:
            
            .. code-block:: python
            
                spectrometer_mgr.set_integrationtime(2_000_000)
        """
        if not self.is_connected():
            # Speichert die Zeit, auch wenn nicht verbunden.
            # 'set_integrationtime' wird automatisch in 'connect' erneut aufgerufen.
            self.log_mgr.info(f"Storing integration time ({time_us} us) for next connect.")
            self.current_integration_time_us = time_us
            self.profile_mgr.write("Spec_integration_time_us", time_us)
            return True
        
        try:
            min_us, max_us = self.spectrometer.integration_time_micros_limits 
            
            # Zeit auf min max begrenzen
            clamped_us = max(min_us, min(time_us, max_us))

            if clamped_us != time_us:
                self.log_mgr.warning(f"Desired time {time_us} us is outside limits ({min_us}-{max_us}). "
                                     f"Setting to {clamped_us} us.")
            
            self.spectrometer.integration_time_micros(clamped_us)
            self.current_integration_time_us = clamped_us
            self.profile_mgr.write("Spec_integration_time_us", clamped_us)

            self.log_mgr.info(f"Integration time set to {self.current_integration_time_us} us.")
            return True

        except Exception as e:
            self.log_mgr.error(f"Error setting integration time: {e}")
            return False
    
    def get_integrationtime(self) -> int:
        """
        Gibt die zuletzt erfolgreich gesetzte Integrationszeit in Mikrosekunden (us) zurück.

        Returns:
            int: Die Integrationszeit in Mikrosekunden.
        """
        return self.current_integration_time_us

    def get_integrationtime_limits_us(self) -> tuple[int, int]:
        """
        Gibt die Hardware-Limits (min, max) der Integrationszeit in Mikrosekunden zurück.

        Returns:
            tuple[int, int]: (min_integrationszeit_us, max_integrationszeit_us).
                             Gibt (0, 0) zurück, wenn nicht verbunden.

        Examples:
            Minimale und maximale Zeit abfragen:
            
            .. code-block:: python
            
                min_t, max_t = spectrometer_mgr.get_integrationtime_limits_us()
                if max_t > 0:
                    print(f"Unterstützter Bereich: {min_t} µs bis {max_t} µs")
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
        Gibt die maximal mögliche Intensität (ADC-Sättigungswert) des Spektrometers zurück.

        Dies ist typischerweise 65535.0 (für 16-bit ADC) oder 4095.0 (für 12-bit ADC).

        Returns:
            float: Der maximale Sättigungswert. 
                   Gibt 65535.0 als Fallback zurück, wenn nicht verbunden.
        """
        if not self.is_connected():
            self.log_mgr.warning("Cannot read max intensity: No spectrometer connected. Returning default 65535.0.")
            return 65535.0 
        
        try:
            return self.spectrometer.max_intensity
        except Exception as e:
            self.log_mgr.error(f"Error reading max intensity: {e}")
            return 65535.0 # Fallback

    # --- Daten Erhebung ---

    def acquire_spectrum(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Nimmt ein einzelnes Spektrum mit den aktuell gesetzten Korrekturen auf.

        Löst bei Erfolg das `new_spectrum_acquired`-Signal aus.

        Returns:
            tuple[np.ndarray | None, np.ndarray | None]: 
            Ein Tupel aus (wavelengths, intensities) bei Erfolg.
            (None, None) bei einem Messfehler oder wenn nicht verbunden.

        Examples:
            Ein Spektrum aufnehmen und verarbeiten:
            
            .. code-block:: python
            
                # Annahme: 'spectrometer_mgr' ist eine Instanz von SpectrometerManager
                
                wavelengths, intensities = spectrometer_mgr.acquire_spectrum()
                
                if wavelengths is not None:
                    # Finde die Wellenlänge mit der maximalen Intensität
                    peak_index = np.argmax(intensities)
                    peak_wl = wavelengths[peak_index]
                    peak_int = intensities[peak_index]
                    
                    print(f"Stärkstes Signal bei {peak_wl:.2f} nm mit {peak_int:.0f} Counts")
                else:
                    print("Spektrum-Aufnahme fehlgeschlagen.")
        """
        if not self.is_connected():
            self.log_mgr.warning("Cannot acquire spectrum: No spectrometer connected.")
            return None, None
        
        try:
            wavelengths, intensities = self.spectrometer.spectrum(
                correct_dark_counts=self.correct_dark_counts,
                correct_non_linearity=self.correct_non_linearity
            )
            self.log_mgr.debug("Spectrum acquired successfully.")

            # Sende das Signal mit den neuen Daten
            self.new_spectrum_acquired.emit(wavelengths, intensities)

            return wavelengths, intensities
        
        except Exception as e:
            self.log_mgr.error(f"Error during spectrum acquisition: {e}")
            # Bei kritischen Fehlern ggf. Verbindung trennen
            # self.disconnect() 
            return None, None