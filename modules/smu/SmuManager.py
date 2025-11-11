
import sys
import time
import serial
from serial.tools import list_ports

from PySide6.QtCore import QObject, Signal
from modules.smu.Keithley2602 import Keithley2602,TSP_DC_VOLTS, TSP_DC_AMPS,TSP_SMU_OFF, TSP_SMU_ON,TSP_SENSE_LOCAL, TSP_SENSE_REMOTE

class SmuManager(QObject):
    """
    Manager zur Steuerung und Verwaltung von SMU-Geräten
    """

    # Signale
    connection_status_changed = Signal(bool, str)   # (bool connecred, str device_name)
    device_list_updated = Signal(list)              # ([list] str port_names)
    new_measurement_acquired = Signal(str, float, float)    # (str channel, float current, float voltage)

    def __init__(self, log_manager, profile_manager):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.smu_device = None  
        self.available_devices = {}
        self.connected_port = ""
        self.idn_message = ""

        self.channel_source_func = {
            'a': TSP_DC_VOLTS,
            'b': TSP_DC_VOLTS
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
        Aktualisiert die Liste der Verfügbaren seriellen Ports
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
                    self.log_mgr.debug(f" - Found: {port.decice} ({port.description})")
        
        except Exception as e:
            self.log_mgr.error(f"Error listing COM-Ports: {e}")
            self.available_devices.clear()

        self.device_list_updated.emit(port_names)
        return port_names
    
    def connect(self, port_name: str) -> bool:
        """
        Verbindet eine SMU an einem bestimmten COM-Port.
        """

        self.disconnect()

        # ================================================================================================================
        # Hier können später auch andere Treiber für andere SMU Geräte eingebunden werden
        
        driver_to_use = Keithley2602(self.log_mgr)

        try:
            is_connectd, idn_msg = driver_to_use(port = port_name)

            if is_connectd:
                #Prüfen ob Keithley:
                if "KEITHLEY" not in idn_msg.upper() or "26" not in idn_msg:
                    self.log_mgr.error(f"Device on {port_name} is not a Keithley SMU. IDN: {idn_msg}")
                    driver_to_use.disconnect()
                    self.connection_status_changed.emit(False,"")
                    return False

                self.smu_device = driver_to_use 
                self.connected_port = port_name
                self.idn_message = idn_msg
                self.LastDevice = port_name
                self.progile_mgr.write("Smu_LastDevice", self.LastDevice)

                active_name = self.get_activeDeviceName()
                self.log_mgr.info(f"Successfully connected to {active_name}")
                self.connection_status_changed.emit(True,active_name)
                return True
            else:
                raise ConnectionError (idn_msg)
        except Exception as e:
            self.log_mgr.error(f"Connection to {port_name} failed: {e}")
            self.smu_device = None
            self.connection_status_changed.emit(False, "")
            return False
        
    def connect_LastDevice(self):
        """
        Versuch Verbindung mit dem zuletzt genutzten Device herzustellen
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
        Trennt Verbindung zum SMU-Gerät
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
        """ Gibt den Namen des aktuell verbundenen Geräts zurück """
        if self.is_connected() and self.idn_message:
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
        """ Prüft, ob SMU verbunden und Port offen ist """
        return self.smu_device is not None and self.smu_device.is_open
    
    # --- Konfiguration - Getter & Setter

    def _check_connection(self, command_name: str) -> bool:
        """ Interne Hilfsfunktion, um Verbindung zu prüfen und zu loggen """
        if not self.is_connected():
            self.log_mgr.warning(f"Cannot {command_name}: No SMU connected.")
            return False
        return True

    def reset_channel(self, channel: str):
        """ Setzt einen SMU-Kanal auf Werkseinstellungen zurück. """
        if not self._check_connection(f"reset channel {channel}"):
            return
        try:
            self.smu_device.reset_channel(channel)
            # Internen Zustand auch zurücksetzen
            self.channel_source_func[channel] = TSP_DC_VOLTS
            self.log_mgr.info(f"SMU Channel {channel} reset.")
        except Exception as e:
            self.log_mgr.error(f"Failed to reset channel {channel}: {e}")

    def set_source(self, channel: str, is_voltage_source: bool):
        """ Legt die Source-Funktion fest (Spannung oder Strom). """
        if not self._check_connection(f"set source for {channel}"):
            return
        
        func_cmd = TSP_DC_VOLTS if is_voltage_source else TSP_DC_AMPS
        try:
            self.smu_device.set_source_function(channel, func_cmd)
            self.channel_source_func[channel] = func_cmd # Wichtig Zustand im Manager merken
            self.log_mgr.info(f"SMU Channel {channel} source set to {func_cmd}.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source for {channel}: {e}")

    def set_sense_mode(self, channel: str, is_remote_sense: bool):
        """ Legt den Sense-Modus fest (Lokal/2-Draht oder Remote/4-Draht). """
        if not self._check_connection(f"set sense mode for {channel}"):
            return
        
        mode_cmd = TSP_SENSE_REMOTE if is_remote_sense else TSP_SENSE_LOCAL
        try:
            self.smu_device.set_sense_mode(channel, mode_cmd)
            self.log_mgr.info(f"SMU Channel {channel} sense mode set to {mode_cmd}.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set sense mode for {channel}: {e}")

    def set_source_level(self, channel: str, level: float):
        """ Setzt das Source-Level (V oder A), basierend auf der aktuellen Source-Funktion. """
        if not self._check_connection(f"set source level for {channel}"):
            return
        
        # Greift auf den im Manager gespeicherten Zustand zurück
        func = self.channel_source_func.get(channel, TSP_DC_VOLTS)
        
        try:
            self.smu_device.set_source_level(channel, func, level)
            self.log_mgr.debug(f"SMU Channel {channel} level set to {level} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source level for {channel}: {e}")

    def set_source_limit(self, channel: str, limit: float):
        """ Setzt das Source-Limit (A oder V), basierend auf der aktuellen Source-Funktion. """
        if not self._check_connection(f"set source limit for {channel}"):
            return
        
        # Greift auf den im Manager gespeicherten Zustand zurück
        func = self.channel_source_func.get(channel, TSP_DC_VOLTS)
        
        try:
            self.smu_device.set_source_limit(channel, func, limit)
            self.log_mgr.debug(f"SMU Channel {channel} limit set to {limit} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source limit for {channel}: {e}")

    def set_output_state(self, channel: str, enable: bool):
        """ Schaltet den Ausgang eines Kanals EIN oder AUS. """
        if not self._check_connection(f"set output state for {channel}"):
            return
        
        state_cmd = TSP_SMU_ON if enable else TSP_SMU_OFF
        try:
            self.smu_device.set_output_state(channel, state_cmd)
            self.log_mgr.info(f"SMU Channel {channel} output set to {state_cmd}.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set output state for {channel}: {e}")

    # --- Daten Erhebung ---

    def measure_iv(self, channel: str) -> tuple[float, float] | None:
        """
        Führt eine einzelne I/V-Messung auf dem Kanal durch.
        Returns: (current, voltage) oder None bei Fehler.
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
            if isinstance(e, (ConnectionError, serial.SerialException, ValueError)):
                self.disconnect()
            return None