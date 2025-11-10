from PySide6.QtCore import QObject, Signal

# https://python-seabreeze.readthedocs.io/en/latest/api.html#seabreeze.spectrometers.Spectrometer
import seabreeze
seabreeze.use('cseabreeze')
from seabreeze.spectrometers import Spectrometer, list_devices

class SpectrometerManager(QObject):
    """
    Manager zu Steuerung und Verwaltung von Ocean Optics Spektrometern über seabreeze
    """

    # Signale
    connection_status_changed = Signal(bool,str)    # (bool connected, str device_name)
    device_list_updated = Signal(list)              # ([list]str device_names)
    new_spectrum_acquired = Signal(object, object)  # (np.ndarray wavelengths, np.ndarray intensities)
    # log_message = Signal(str, str)                # (str level, str message)
    
    def __init__(self, log_manager, profile_manager):
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

    def get_deviceList(self):
        """
        Aktualisiert die Liste der verfügbaren Geräte
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
    
    def connect(self, device_name_or_serial):
        """
        Verbindet ein Spektrometer
        """
        self.disconnect()
        dev_to_connect = None
        try:
            if device_name_or_serial in self.device_name_map:
                # Name
                dev_to_connect = self.device_name_map[device_name_or_serial]
                self.spectrometer = Spectrometer(dev_to_connect)
            else:
                # Seriennummer
                self.spectrometer = Spectrometer.from_serial_number(device_name_or_serial)
            
            active_name = self.get_activeDeviceName()
            self.LastDevice = self.spectrometer.serial_number
            self.profile_mgr.write("Spec_LastDevice",self.LastDevice)
            self.log_mgr.info(f"Successfully connected to {active_name}")
            self.set_integrationtime(self.current_integration_time_us)
            self.connection_status_changed.emit(True,active_name)
            return True

        except Exception as e:
            self.log_mgr.error(f"Connection failed: {e}")
            self.spectrometer= None
            self.connection_status_changed.emit (False, "")
            return False
        
    def connect_LastDevice(self):
        """
        Versucht Verbindung mit dem zuletzt genutzten Device herzustellen
        """
        if self.LastDevice:
            return self.connect(self.LastDevice)
        else:
            self.log_mgr.warning("No 'LastDevice' found to connect to.")
            return False
        
    def disconnect(self):
        """
        Trennt Verbindung zu Spektrometer
        """
        if self.spectrometer:
            try:
                self.spectrometer.close()
            except Exception as e:
                self.log_mgr.error(f"Error closing spectrometer: {e}")
            self.spectrometer = None
            self.connection_status_changed.emit(False,"")

    def get_activeDeviceName(self):
        """ Gibt den Namen des aktuell verbundenen Geräts zurück """
        if self.spectrometer:
            return f"{self.spectrometer.model} ({self.spectrometer.serial_number})"
        return ""
    
    def is_connected(self): 
        """ Prüft, ob Spektrometer verbunden """
        return self.spectrometer is not None
    
    # --- Konfiguration - Getter & Setter ---

    def set_correction_dark_count(self, enable: bool):
        """ 
        Aktiviere/ Deaktive die Dark Count Korrektur 

        If requested and supported the average value of electric dark
        pixels on the ccd of the spectrometer is subtracted from the
        measurements to remove the noise floor in the measurements
        caused by non optical noise sources.
        
        """
        self.correct_dark_counts = enable
        self.log_mgr.info(f"Dark count correction set to: {enable}")
    
    def get_correction_dark_count(self) -> bool:
        """ Gibt Status der Dark Count Korrektur zurück """
        return self.correct_dark_counts
    
    def set_correction_non_linearity(self, enable: bool):
        """ 
        Aktiviere/ Deaktive die Dark Count Korrektur 

        Some spectrometers store non linearity correction coefficients
        in their eeprom. If requested and supported by the spectrometer
        the readings returned by the spectrometer will be linearized
        using the stored coefficients.
        
        """
        self.correct_non_linearity = enable
        self.log_mgr.info(f"Non-linearity correction set to: {enable}")
    
    def get_correction_non_linearity(self) -> bool:
        """ Gibt Status der Non Linearity zurück """
        return self.correct_non_linearity

    def set_integrationtime(self, time_us: int):
        """
        Stellt die Integrationszeit ein
        """

        if not self.is_connected():
            # Eine validierung nicht nötig.. bei einem connect wird diese funktion neu aufgerufen und die validierung findet dann beim setzen statt
            self.log_mgr.info( "Cannot set integration time: No spectrometer connected.")
            self.current_integration_time_us = time_us
            return False
        
        try:
            min_us, max_us = self.spectrometer.integration_time_micros_limits 
            
            # Zeit auf min max begrenzen
            clamped_us =max(min_us, min(time_us, max_us)) # Elegent, oder!? :P

            if clamped_us != time_us:
                self.log_mgr.warning(   f"Desired time {time_us} us is outside limits. "
                                        f"Setting to {clamped_us} us.")
            
            self.spectrometer.integration_time_micros(clamped_us)
            self.current_integration_time_us = clamped_us

            self.log_mgr.info(  f"Integration time set to {self.current_integration_time_us} us.")
            return True

        except Exception as e:
            self.log_mgr.error(f"Error setting integration time: {e}")
            return False
    
    def get_integrationtime(self) -> int:
        """ Gibt die zuletzt gesetzte Integrationszeit in us zurück. """
        return self.current_integration_time_us

    def get_integrationtime_limits_us(self):
        """Gibt die Hardware-Limits (min, max) in Mikrosekunden zurück."""
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
        Gibt die maximal mögliche Intensität (ADC-Wert) des Spektrometers zurück.
        """
        if not self.is_connected():
            self.log_mgr.warning("Cannot read max intensity: No spectrometer connected. Returning default 65535.0.")
            return 65535.0 
        
        try:
            return self.spectrometer.max_intensity
        except Exception as e:
            self.log_mgr.error(f"Error reading max intensity: {e}")
            return 65535.0

    # --- Daten Erhebung ---

    def acquire_spectrum(self):
        """
        Nimmt ein einzelnes Spektrum auf
        Returns: (np.ndarray, np.ndarray): (wavelengths, intensities) oder (None, None) bei Fehler.
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

            self.new_spectrum_acquired.emit(wavelengths, intensities)

            return wavelengths, intensities
        
        except Exception as e:
            self.log_mgr.error(f"Error during spectrum acquisition: {e}")
            # self.disconnect() 
            return None, None