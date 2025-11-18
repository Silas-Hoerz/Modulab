# modules/smu/SmuManager.py
import sys
import time
import serial
from serial.tools import list_ports

from PySide6.QtCore import QObject, Signal

# Importiere beide Treiber, aber KEINE TSP-Konstanten mehr
from .Keithley2602 import Keithley2602, DummyKeithley2602

class SmuManager(QObject):
    """
    Manager zur Steuerung und Verwaltung von SMU-Geräten (Source Measure Units).

    Diese Klasse kapselt die Gerätetreiber (z.B. Keithley2602), verwaltet die 
    serielle Verbindung, aktualisiert die Geräteliste und stellt High-Level-Methoden
    für die Konfiguration (Source, Sense, Limits) und Messung (IV) bereit.
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
            Wird ausgelöst, nachdem die Liste der seriellen Ports aktualisiert wurde.
            Args: (list: Liste von Port-Namen [str]).
            
        new_measurement_acquired (str, float, float):
            Wird ausgelöst, wenn eine neue Messung verfügbar ist.
            Args: (str: Kanal, float: Strom, float: Spannung).
    """

    # Signale
    connection_status_changed = Signal(bool, str)
    device_list_updated = Signal(list)
    new_measurement_acquired = Signal(str, float, float)

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.smu_device = None
        self.available_devices = {}
        self.connected_port = ""
        self.idn_message = ""

        # Speichert den internen Zustand der Source-Funktion ('V' oder 'I')
        self.channel_source_func = {
            'a': 'V',
            'b': 'V'
        }

        self.LastDevice = self.profile_mgr.read("Smu_LastDevice")

        if self.LastDevice:
            self.log_mgr.info(f"Last connected SMU (Port): {self.LastDevice}. Attempting re-connect...")
            self.connect_LastDevice()
        else:
            self.log_mgr.info("No last SMU saved. Please connect manually")
            self.get_deviceList()

    # --- Verbindungs- und Geräte-Verwaltung

    def get_deviceList(self) -> list:
        """
        Scannt nach verfügbaren seriellen Ports und aktualisiert die interne Liste.

        Sucht nach allen COM-Ports und fügt zusätzlich einen "DUMMY"-Port
        für Testzwecke hinzu. Löst das `device_list_updated`-Signal aus.

        Returns:
            list: Eine Liste der gefundenen Port-Namen (z.B. ['COM1', 'COM3', 'DUMMY']).
        """
        port_names = []
        try:
            ports = list_ports.comports() # Etwas blöd hiermit wird vorausgesetzt das ALLE SMU über Serial Port laufen
            self.available_devices.clear()

            if not ports:
                self.log_mgr.warning("No COM-Ports found.")
            else:
                self.log_mgr.debug(f"{len(ports)} COM-Port(s) found.")
                for port in ports:
                    name = port.device
                    port_names.append(name)
                    self.available_devices[name] = port
                    self.log_mgr.debug(f" - Found: {port.device} ({port.description})")
        
        except Exception as e:
            self.log_mgr.error(f"Error listing COM-Ports: {e}")
            self.available_devices.clear()

        # Dummy Port für Testzwecke
        port_names.append("DUMMY")
        self.available_devices["DUMMY"] = None
        self.log_mgr.debug(" - Found: DUMMY")

        self.device_list_updated.emit(port_names)
        return port_names
    
    def connect(self, port_name: str) -> bool:
        """
        Verbindet eine SMU an einem bestimmten COM-Port.
        ...

        Args:
            port_name (str): Der Name des Ports (z.B. "COM1" oder "DUMMY").

        Returns:
            bool: True bei erfolgreicher Verbindung, sonst False.

        Examples:
            Mit einem echten COM-Port verbinden:
            
            .. code-block:: python
            
                # 'COM3' ist nur ein Beispiel
                success = manager.connect('COM3') 
                if success:
                    print("Verbunden!")

            Mit dem DUMMY-Gerät für Tests verbinden:
            
            .. code-block:: python
            
                manager.connect('DUMMY')
        """
        self.disconnect()

        driver_to_use = None
        if port_name.upper() == "DUMMY":
            self.log_mgr.info("Connecting to DUMMY driver...")
            driver_to_use = DummyKeithley2602(self.log_mgr)
        elif port_name in self.available_devices:
            self.log_mgr.info(f"Connecting to real Keithley driver on {port_name}...")
            # =====================================================================
            # Hier können später auch andere Treiber für andere SMU Geräte eingebunden werden
            # Aktuell hardcoded auf Keithley2602
            driver_to_use = Keithley2602(self.log_mgr)
            # =====================================================================
        else:
            self.log_mgr.error(f"Cannot connect: Port '{port_name}' is not in the available device list.")
            return False

        try:
            is_connected, idn_msg = driver_to_use.connect(port=port_name) 

            if is_connected:
                #Prüfen ob Keithley:
                if "KEITHLEY" not in idn_msg.upper() and "DUMMY" not in idn_msg.upper():
                    self.log_mgr.error(f"Device on {port_name} is not a Keithley SMU. IDN: {idn_msg}")
                    driver_to_use.disconnect()
                    self.connection_status_changed.emit(False,"")
                    return False

                self.smu_device = driver_to_use
                self.connected_port = port_name
                self.idn_message = idn_msg
                self.LastDevice = port_name
                self.profile_mgr.write("Smu_LastDevice", self.LastDevice)

                active_name = self.get_activeDeviceName()
                self.log_mgr.info(f"Successfully connected to {active_name}")
                self.connection_status_changed.emit(True, active_name)
                return True
            else:
                raise ConnectionError(idn_msg)
        
        except Exception as e:
            self.log_mgr.error(f"Connection to {port_name} failed: {e}")
            self.smu_device = None
            self.connection_status_changed.emit(False, "")
            return False
        
    def connect_LastDevice(self):
        """
        Versucht, die Verbindung mit dem zuletzt genutzten Gerät wiederherzustellen.

        Aktualisiert zuerst die Geräteliste und prüft, ob der gespeicherte
        Port (`self.LastDevice`) verfügbar ist.

        Returns:
            bool: True bei Erfolg, False, wenn kein Gerät gespeichert war 
                  oder die Verbindung fehlschlägt.
        """
        self.get_deviceList()
        if self.LastDevice:
            if self.LastDevice in self.available_devices:
                return self.connect(self.LastDevice)
            else:
                self.log_mgr.debug(f"Last used port {self.LastDevice} is not available.")   
                return False
        else:
            self.log_mgr.debug(f"No 'LastDevice' (port) found to connect to.")
            return False

    def disconnect(self):
        """
        Trennt die aktive Verbindung zum SMU-Gerät.
        
        Setzt den internen Zustand zurück und löst `connection_status_changed` aus.
        """
        if self.smu_device:
            try:
                self.smu_device.disconnect()
            except Exception as e:
                self.log_mgr.error(f"Error during SMU disconnect: {e}")
            self.smu_device = None
            self.connected_port = ""
            self.idn_message = ""
            self.connection_status_changed.emit(False, "")

    def get_activeDeviceName(self) -> str:
        """
        Gibt einen formatierten Namen des aktuell verbundenen Geräts zurück.

        Parst die IDN-Nachricht, um Modell und Seriennummer zu extrahieren.

        Returns:
            str: Der formatierte Gerätename 
                 (z.B. "MODEL 2602 (SN: 12345) @ COM1") 
                 oder "DUMMY" oder "" (leer, wenn nicht verbunden).
        """
        if self.is_connected() and self.idn_message:
            if self.connected_port.upper() == "DUMMY":
                return "DUMMY (Simuliert)"
            try:
                # IDN-String parsen, z.B.: "KEITHLEY INSTRUMENTS INC.,MODEL 2602,..."
                parts = self.idn_message.split(',')
                model = parts[1].strip()
                serial = parts[2].strip()
                return f"{model} (SN: {serial}) @ {self.connected_port}"
            except Exception as e:
                return f"Keithley SMU @ {self.connected_port}"
        return ""
    
    def is_connected(self) -> bool:
        """
        Prüft, ob eine aktive und offene Verbindung zur SMU besteht.

        Returns:
            bool: True, wenn verbunden und der Treiber als 'offen' gemeldet ist, sonst False.
        """
        return self.smu_device is not None and self.smu_device.is_open
    
    # --- Konfiguration - Getter & Setter

    def _check_connection(self, command_name: str) -> bool:
        """
        Interne Hilfsfunktion, um Verbindung zu prüfen und zu loggen.

        Args:
            command_name (str): Der Name des Befehls, der versucht wird 
                                (z.B. "reset channel a") für die Log-Meldung.

        Returns:
            bool: True, wenn verbunden, False, wenn nicht verbunden 
                  (und ein Warning-Log geschrieben wurde).
        """
        if not self.is_connected():
            self.log_mgr.warning(f"Cannot {command_name}: No SMU connected.")
            return False
        return True

    def reset_channel(self, channel: str):
        """
        Setzt einen SMU-Kanal auf Werkseinstellungen zurück.

        Args:
            channel (str): Der Kanal, der zurückgesetzt wird (z.B. 'a' or 'b').
        """
        if not self._check_connection(f"reset channel {channel}"):
            return
        try:
            self.smu_device.reset_channel(channel)
            # Internen Zustand auch zurücksetzen
            self.channel_source_func[channel] = 'V'
            self.log_mgr.info(f"SMU Channel {channel} reset.")
        except Exception as e:
            self.log_mgr.error(f"Failed to reset channel {channel}: {e}")

    # --- NEUE, INTUITIVE API-METHODEN (ersetzen die alten 'bool'-Methoden) ---

    def set_source_voltage(self, channel: str):
        """
        Konfiguriert den Kanal als SPANNUNGSQUELLE (V-Source).

        Aktualisiert auch den internen Zustand, damit `set_source_limit`
        und `set_source_level` korrekt funktionieren.

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
        """
        if not self._check_connection(f"set source voltage for {channel}"):
            return
        try:
            self.smu_device.set_source_voltage(channel)
            self.channel_source_func[channel] = 'V' # Zustand im Manager merken
            self.log_mgr.info(f"SMU Channel {channel} source set to VOLTAGE.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source voltage for {channel}: {e}")

    def set_source_current(self, channel: str):
        """
        Konfiguriert den Kanal als STROMQUELLE (I-Source).

        Aktualisiert auch den internen Zustand, damit `set_source_limit`
        und `set_source_level` korrekt funktionieren.

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
        """
        if not self._check_connection(f"set source current for {channel}"):
            return
        try:
            self.smu_device.set_source_current(channel)
            self.channel_source_func[channel] = 'I' # Zustand im Manager merken
            self.log_mgr.info(f"SMU Channel {channel} source set to CURRENT.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source current for {channel}: {e}")

    def set_sense_local(self, channel: str):
        """
        Stellt den Sense-Modus auf LOKAL (2-Draht-Messung).

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
        """
        if not self._check_connection(f"set sense local for {channel}"):
            return
        try:
            self.smu_device.set_sense_mode_local(channel)
            self.log_mgr.info(f"SMU Channel {channel} sense mode set to LOCAL (2-Wire).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set sense local for {channel}: {e}")

    def set_sense_remote(self, channel: str):
        """
        Stellt den Sense-Modus auf REMOTE (4-Draht-Messung).

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
        """
        if not self._check_connection(f"set sense remote for {channel}"):
            return
        try:
            self.smu_device.set_sense_mode_remote(channel)
            self.log_mgr.info(f"SMU Channel {channel} sense mode set to REMOTE (4-Wire).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set sense remote for {channel}: {e}")

    # --- "Intelligente" Methoden  ---

    def set_source_level(self, channel: str, level: float):
        """
        Setzt das Source-Level (V oder A).

        Die Einheit (V oder A) hängt von der zuvor mit `set_source_voltage`
        oder `set_source_current` konfigurierten Source-Funktion ab.

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
            level (float): Das zu setzende Level (in Volt oder Ampere).
        """
        if not self._check_connection(f"set source level for {channel}"):
            return
        
        # Greift auf den im Manager gespeicherten Zustand zurück
        func = self.channel_source_func.get(channel, 'V') 
        
        try:
            if func == 'V':
                self.smu_device.set_source_voltage_level(channel, level)
            else: # func == 'I'
                self.smu_device.set_source_current_level(channel, level)
                self.log_mgr.debug(f"SMU Channel {channel} level set to {level} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source level for {channel}: {e}")

    def set_source_limit(self, channel: str, limit: float):
        """
        Setzt das Source-Limit (A oder V).

        Die Einheit ist *entgegengesetzt* zur Source-Funktion:
        - Wenn Source = Spannung (V), ist dies das Strom-Limit (A).
        - Wenn Source = Strom (I), ist dies das Spannungs-Limit (V).

        Args:
            channel (str): Der zu konfigurierende Kanal (z.B. 'a').
            limit (float): Das zu setzende Limit (in Ampere oder Volt).

        Examples:
            Ein Strom-Limit (100mA) für eine Spannungsquelle setzen:
            
            .. code-block:: python
            
                # 1. Zuerst Kanal 'a' als SPANNUNGSQUELLE definieren
                    manager.set_source_voltage('a') 
                
                # 2. Jetzt das Limit setzen (0.1 = 100mA STROM-Limit)
                manager.set_source_limit('a', 0.1)

            Ein Spannungs-Limit (20V) für eine Stromquelle setzen:
                 
            .. code-block:: python
            
                # 1. Zuerst Kanal 'b' als STROMQUELLE definieren
                manager.set_source_current('b')
                
                # 2. Jetzt das Limit setzen (20.0 = 20V SPANNUNGS-Limit)
                manager.set_source_limit('b', 20.0)
        """
        if not self._check_connection(f"set source limit for {channel}"):
            return
        
        # Greift auf den im Manager gespeicherten Zustand zurück
        func = self.channel_source_func.get(channel, 'V')
        
        try:
            if func == 'V':
                # Spannungs-Quelle braucht Strom-Limit
                self.smu_device.set_source_current_limit(channel, limit)
            else: # func == 'I'
                # Strom-Quelle braucht Spannungs-Limit
                self.smu_device.set_source_voltage_limit(channel, limit)

            self.log_mgr.debug(f"SMU Channel {channel} limit set to {limit} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source limit for {channel}: {e}")

    def set_output_state(self, channel: str, enable: bool):
        """
        Schaltet den Ausgang eines Kanals EIN oder AUS.

        Args:
            channel (str): Der zu schaltende Kanal (z.B. 'a').
            enable (bool): True, um den Ausgang einzuschalten, False, um ihn auszuschalten.
        """
        if not self._check_connection(f"set output state for {channel}"):
            return
        
        try:
            if enable:
                self.smu_device.set_output_on(channel)
                self.log_mgr.info(f"SMU Channel {channel} output set to ON.")
            else:
                self.smu_device.set_output_off(channel)
                self.log_mgr.info(f"SMU Channel {channel} output set to OFF.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set output state for {channel}: {e}")

    # --- Daten Erhebung ---

    def measure_iv(self, channel: str) -> tuple[float, float] | None:
        """
        Führt eine einzelne I/V-Messung auf dem Kanal durch.
        ... (andere Sektionen) ...

        Args:
            channel (str): Der zu messende Kanal (z.B. 'a').

        Returns:
            tuple[float, float] | None: Ein Tupel aus (Strom, Spannung) bei Erfolg.
                                         None bei einem Messfehler.

        Examples:
            Das Auslesen der Messung und Speichern in Variablen:
            
            .. code-block:: python
            
                # Annahme: 'manager' ist eine Instanz von SmuManager
                result = manager.measure_iv('a')

                if result:
                    current, voltage = result
                    print(f"Messung OK: {current} A, {voltage} V")
                else:
                    print("Messung fehlgeschlagen oder keine Verbindung.")
        """

        if not self._check_connection(f"measure IV for {channel}"):
            return None
        
        try:
            current, voltage = self.smu_device.measure_iv(channel)
            self.log_mgr.debug(f"SMU Channel {channel} measured: C={current}, V={voltage}")
            
            self.new_measurement_acquired.emit(channel, current, voltage)
            
            return current, voltage
        
        except Exception as e:
            self.log_mgr.error(f"Error during IV measurement on {channel}: {e}")
            # Bei kritischen Fehlern die Verbindung trennen
            if isinstance(e, (ConnectionError, serial.SerialException, ValueError)):
                self.log_mgr.error("Critical error during measurement. Disconnecting SMU.")
                self.disconnect()
            return None