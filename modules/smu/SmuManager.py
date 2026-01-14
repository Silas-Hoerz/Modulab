# modules/smu/SmuManager.py
import sys
import time
import serial
from serial.tools import list_ports

from PySide6.QtCore import QObject, Signal, Slot

# Importiere Treiber
from .Keithley2602 import Keithley2602, DummyKeithley2602

class SmuManager(QObject):
    """
    Manager zur Steuerung und Verwaltung von SMU-Geräten (Source Measure Units).

    Diese Klasse kapselt die Gerätetreiber (z.B. Keithley2602) und verwaltet den
    gesamten Status der Kanäle (Spannung, Strom, Limits). Sie dient als
    "Single Source of Truth": Das UI holt sich den Status von hier.
    Zudem kümmert sie sich um das Speichern und Laden der Einstellungen im Profil.

    Args:
        log_manager (LogManager): Instanz für das Logging von Ereignissen.
        profile_manager (ProfileManager): Instanz zum Speichern von Einstellungen.

    Signale:
        connection_status_changed (bool, str):
            Wird bei Verbindungsänderung ausgelöst.
            Args: (Ist_Verbunden [bool], Gerätename [str])
        
        device_list_updated (list):
            Wird nach dem Scannen nach Ports ausgelöst.
            Args: (Liste der Portnamen [list[str]])
            
        new_measurement_acquired (str, float, float):
            Wird ausgelöst, wenn eine Messung erfolgreich war.
            Args: (Kanal [str], Strom [A], Spannung [V])
    """

    # Signale Definitionen
    connection_status_changed = Signal(bool, str)
    device_list_updated = Signal(list)
    new_measurement_acquired = Signal(str, float, float)

    def __init__(self, log_manager, profile_manager):
        """
        Initialisiert den SmuManager.

        Bereitet die interne Datenstruktur vor, verbindet sich mit dem ProfileManager,
        lädt aber noch keine hardware-spezifischen Einstellungen (das passiert erst
        bei `on_profile_loaded`).
        """
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.smu_device = None
        self.available_devices = {}
        self.connected_port = ""
        self.idn_message = ""
        self.LastDevice = None

        self.active_channels = ['a', 'b']

        # Speichert, ob der Kanal als Spannungs- ('V') oder Stromquelle ('I') dient
        self.channel_source_func = {
            'a': 'V',
            'b': 'V'
        }

        # Interner State für UI-Synchronisation (Level, Limit, Sense, Output)
        # Dies ist der Cache, den das Widget abfragt.
        self.channel_state = {
            'a': {'level': 0.0, 'limit': 0.1, 'sense': 'local', 'output': False},
            'b': {'level': 0.0, 'limit': 0.1, 'sense': 'local', 'output': False}
        }

        # Warten auf das Profil-Laden-Signal
        self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

        # Initialer Hardware-Scan
        self.get_deviceList()

    @Slot(str)
    def on_profile_loaded(self, profile_name: str):
        """
        Slot: Wird aufgerufen, sobald der User ein Profil ausgewählt hat.

        Versucht, die letzte Verbindung wiederherzustellen.

        Args:
            profile_name (str): Name des geladenen Profils.
        """
        self.log_mgr.info(f"SmuManager: Loading settings from profile '{profile_name}'...")
        
        self.LastDevice = self.profile_mgr.read("Smu_LastDevice")

        if self.LastDevice:
            self.log_mgr.info(f"Last connected SMU (Port): {self.LastDevice}. Attempting re-connect...")
            if not self.connect_LastDevice():
                self.log_mgr.info("Could not reconnect to last SMU.")
        else:
            self.log_mgr.info("No last SMU saved in this profile.")

    def _disable_channel(self, channel, reason):
        """Markiert einen Kanal als defekt/nicht vorhanden."""
        if channel in self.active_channels:
            self.active_channels.remove(channel)
            self.log_mgr.warning(f"Channel '{channel}' disabled permanently for this session. Reason: {reason}")
            # Signal senden, damit das UI (Widget) den Kanal ausgraut
            self.channel_disabled.emit(channel)
    
    def _check_connection(self, action_name="", channel=None) -> bool:
        """
        Helper: Prüft Verbindung UND ob der Kanal aktiv ist.
        """
        if not self.is_connected():
            return False
        
        # WICHTIG: Hier wird geprüft, ob der Kanal (z.B. 'b') überhaupt noch erlaubt ist
        if channel is not None and channel not in self.active_channels:
            # Still und leise abbrechen -> Kein Log Spam
            return False
            
        return True
    
    def apply_channel_settings(self):
        """Wendet die gespeicherten/internen Settings auf das Gerät an."""
        if not self.is_connected(): return
        
        self.log_mgr.info("Applying channel settings...")
        
        # --- ÄNDERUNG: Reset active list bei neuem Connect ---
        self.active_channels = ['a', 'b']

        # Über Kopie der Liste iterieren, falls einer währenddessen rausfliegt
        for ch in list(self.active_channels):
            try:
                state = self.channel_state[ch]
                
                if state['func'] == 'V': self.set_source_voltage(ch)
                else: self.set_source_current(ch)
                
                self.set_source_level(ch, state['level'])
                self.set_source_limit(ch, state['limit'])
                self.set_sense_mode(ch, state['sense'])
                self.set_output_state(ch, False)
                
            except Exception as e:
                # Falls schon beim Setup ein Fehler kommt (z.B. Timeout auf Ch B)
                if isinstance(e, ValueError):
                    self._disable_channel(ch, "Setup failed (Device rejected command)")
                else:
                    self.log_mgr.error(f"Error applying settings to {ch}: {e}")

    def _load_channel_settings_from_profile(self):
        """
        Lädt alle Kanal-Einstellungen (Level, Limit, Mode) aus dem Profil und wendet sie an.
        
        Wird automatisch nach einer erfolgreichen Verbindung aufgerufen.
        """
        if not self.is_connected():
            return

        self.log_mgr.info("Applying channel settings from profile...")
        for ch in ['a', 'b']:
            ch_upper = ch.upper()
            
            # 1. Source Function (V/I)
            source_func = self.profile_mgr.read(f"Smu_Ch{ch_upper}_SourceFunc")
            if source_func == 'I':
                self.set_source_current(ch)
            else:
                self.set_source_voltage(ch) # Default
            
            # 2. Level
            level = self.profile_mgr.read(f"Smu_Ch{ch_upper}_Level")
            if level is not None:
                self.set_source_level(ch, float(level))

            # 3. Limit
            limit = self.profile_mgr.read(f"Smu_Ch{ch_upper}_Limit")
            if limit is not None:
                self.set_source_limit(ch, float(limit))
            
            # 4. Sense Mode
            sense_mode = self.profile_mgr.read(f"Smu_Ch{ch_upper}_Sense")
            if sense_mode == 'remote':
                self.set_sense_remote(ch)
            else:
                self.set_sense_local(ch) # Default

            # 5. SICHERHEITSREGEL: Output beim Start immer AUS
            self.set_output_state(ch, False)
        
        self.log_mgr.info("Channel settings applied.")

    def get_channel_state(self, channel: str) -> dict:
        """
        Gibt den aktuellen internen Status eines Kanals zurück.
        
        Wird vom Widget genutzt, um die UI zu aktualisieren (`sync_ui_from_manager`).

        Args:
            channel (str): 'a' oder 'b'.

        Returns:
            dict: Dictionary mit Keys 'source_func', 'level', 'limit', 'sense', 'output'.
        """
        return {
            'source_func': self.channel_source_func.get(channel, 'V'),
            'level': self.channel_state[channel]['level'],
            'limit': self.channel_state[channel]['limit'],
            'sense': self.channel_state[channel]['sense'],
            'output': self.channel_state[channel]['output']
        }

    # --- Verbindungs- und Geräte-Verwaltung ---

    def get_deviceList(self) -> list:
        """
        Scannt nach verfügbaren seriellen Ports (COM-Ports).

        Returns:
            list: Liste der Port-Namen (z.B. ['COM3', 'DUMMY']).
        
        Example:
            >>> ports = manager.get_deviceList()
            >>> print(ports)
            ['COM1', 'DUMMY']
        """
        port_names = []
        try:
            ports = list_ports.comports()
            self.available_devices.clear()

            if not ports:
                self.log_mgr.warning("No COM-Ports found.")
            else:
                for port in ports:
                    name = port.device
                    port_names.append(name)
                    self.available_devices[name] = port
        except Exception as e:
            self.log_mgr.error(f"Error listing COM-Ports: {e}")
            self.available_devices.clear()

        # Dummy Port hinzufügen
        port_names.append("DUMMY")
        self.available_devices["DUMMY"] = None

        self.device_list_updated.emit(port_names)
        return port_names
    
    def connect(self, port_name: str) -> bool:
        """
        Verbindet eine SMU an einem bestimmten Port.

        Lädt bei Erfolg automatisch die letzten Einstellungen aus dem Profil.

        Args:
            port_name (str): Der Name des Ports (z.B. "COM1" oder "DUMMY").

        Returns:
            bool: True bei Erfolg.

        Example:
            >>> manager.connect("COM3")
        """
        self.disconnect()

        driver_to_use = None
        if port_name.upper() == "DUMMY":
            self.log_mgr.info("Connecting to DUMMY driver...")
            driver_to_use = DummyKeithley2602(self.log_mgr)
        elif port_name in self.available_devices:
            self.log_mgr.info(f"Connecting to real Keithley driver on {port_name}...")
            driver_to_use = Keithley2602(self.log_mgr)
        else:
            self.log_mgr.error(f"Cannot connect: Port '{port_name}' not found.")
            return False

        try:
            is_connected, idn_msg = driver_to_use.connect(port=port_name) 

            if is_connected:
                if "KEITHLEY" not in idn_msg.upper() and "DUMMY" not in idn_msg.upper():
                    self.log_mgr.error(f"Device is not a Keithley SMU. IDN: {idn_msg}")
                    driver_to_use.disconnect()
                    self.connection_status_changed.emit(False, "")
                    return False

                self.smu_device = driver_to_use
                self.connected_port = port_name
                self.idn_message = idn_msg
                
                # Port merken
                self.LastDevice = port_name
                if self.profile_mgr.get_current_profile_name():
                    self.profile_mgr.write("Smu_LastDevice", self.LastDevice)

                # Settings wiederherstellen
                self._load_channel_settings_from_profile()

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
        
    def connect_LastDevice(self) -> bool:
        """Versucht, das zuletzt genutzte Gerät zu verbinden."""
        self.get_deviceList()
        if self.LastDevice and (self.LastDevice in self.available_devices):
            return self.connect(self.LastDevice)
        return False

    def disconnect(self):
        """Trennt die Verbindung."""
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
        """Gibt den Namen des verbundenen Geräts zurück."""
        if self.is_connected() and self.idn_message:
            if self.connected_port.upper() == "DUMMY":
                return "DUMMY (Simuliert)"
            try:
                parts = self.idn_message.split(',')
                model = parts[1].strip()
                serial = parts[2].strip()
                return f"{model} (SN: {serial}) @ {self.connected_port}"
            except Exception:
                return f"Keithley SMU @ {self.connected_port}"
        return ""
    
    def is_connected(self) -> bool:
        """Prüft, ob eine Verbindung besteht."""
        return self.smu_device is not None and self.smu_device.is_open
    
    # --- Interne Helper ---


    # --- API Methoden (Hardware Steuerung) ---

    def reset_channel(self, channel: str):
        """
        Setzt einen Kanal auf Werkseinstellungen zurück.
        
        Args:
            channel (str): 'a' oder 'b'.
        """
        if not self._check_connection(f"reset channel {channel}"):
            return
        try:
            self.smu_device.reset_channel(channel)
            # Internen State Reset
            self.channel_source_func[channel] = 'V'
            self.channel_state[channel] = {'level': 0.0, 'limit': 0.1, 'sense': 'local', 'output': False}
            self.log_mgr.info(f"SMU Channel {channel} reset.")
        except Exception as e:
            self.log_mgr.error(f"Failed to reset channel {channel}: {e}")

    def set_source_voltage(self, channel: str):
        """
        Konfiguriert den Kanal als Spannungsquelle.
        Speichert die Einstellung im Profil.

        Args:
            channel (str): 'a' oder 'b'.
        """
        if not self._check_connection(f"set source voltage for {channel}"): return
        try:
            self.smu_device.set_source_voltage(channel)
            self.channel_source_func[channel] = 'V'
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_SourceFunc", "V")
            self.log_mgr.info(f"SMU Channel {channel} source set to VOLTAGE.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source voltage for {channel}: {e}")

    def set_source_current(self, channel: str):
        """
        Konfiguriert den Kanal als Stromquelle.
        Speichert die Einstellung im Profil.

        Args:
            channel (str): 'a' oder 'b'.
        """
        if not self._check_connection(f"set source current for {channel}"): return
        try:
            self.smu_device.set_source_current(channel)
            self.channel_source_func[channel] = 'I'
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_SourceFunc", "I")
            self.log_mgr.info(f"SMU Channel {channel} source set to CURRENT.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source current for {channel}: {e}")

    def set_source_level(self, channel: str, level: float):
        """
        Setzt das Level (Spannung oder Strom, je nach Modus).
        Speichert den Wert im Profil.

        Args:
            channel (str): 'a' oder 'b'.
            level (float): Wert in V oder A.
        """
        if not self._check_connection(f"set source level for {channel}"): return
        
        func = self.channel_source_func.get(channel, 'V') 
        try:
            if func == 'V':
                self.smu_device.set_source_voltage_level(channel, level)
            else:
                self.smu_device.set_source_current_level(channel, level)

            # State Update & Save
            self.channel_state[channel]['level'] = level
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_Level", level)

            self.log_mgr.debug(f"SMU Channel {channel} level set to {level} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source level for {channel}: {e}")

    def set_source_limit(self, channel: str, limit: float):
        """
        Setzt das Compliance-Limit (Strom bei V-Source, Spannung bei I-Source).
        Speichert den Wert im Profil.

        Args:
            channel (str): 'a' oder 'b'.
            limit (float): Limit in A oder V.
        """
        if not self._check_connection(f"set source limit for {channel}"): return
        
        func = self.channel_source_func.get(channel, 'V')
        try:
            if func == 'V':
                self.smu_device.set_source_current_limit(channel, limit)
            else:
                self.smu_device.set_source_voltage_limit(channel, limit)

            # State Update & Save
            self.channel_state[channel]['limit'] = limit
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_Limit", limit)

            self.log_mgr.debug(f"SMU Channel {channel} limit set to {limit} (using {func}).")
        except Exception as e:
            self.log_mgr.error(f"Failed to set source limit for {channel}: {e}")

    def set_sense_local(self, channel: str):
        """Aktiviert Local Sense (2-Wire). Speichert Einstellung."""
        if not self._check_connection(f"set sense local for {channel}"): return
        try:
            self.smu_device.set_sense_mode_local(channel)
            self.channel_state[channel]['sense'] = 'local'
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_Sense", "local")
            self.log_mgr.info(f"SMU Channel {channel} sense mode set to LOCAL.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set sense local for {channel}: {e}")

    def set_sense_remote(self, channel: str):
        """Aktiviert Remote Sense (4-Wire). Speichert Einstellung."""
        if not self._check_connection(f"set sense remote for {channel}"): return
        try:
            self.smu_device.set_sense_mode_remote(channel)
            self.channel_state[channel]['sense'] = 'remote'
            if self.profile_mgr.get_current_profile_name():
                self.profile_mgr.write(f"Smu_Ch{channel.upper()}_Sense", "remote")
            self.log_mgr.info(f"SMU Channel {channel} sense mode set to REMOTE.")
        except Exception as e:
            self.log_mgr.error(f"Failed to set sense remote for {channel}: {e}")

    def set_output_state(self, channel: str, enable: bool):
        """
        Schaltet den Output AN oder AUS.
        Dieser Zustand wird NICHT im Profil gespeichert (Safety First).

        Args:
            channel (str): 'a' oder 'b'.
            enable (bool): True = ON, False = OFF.
        """
        if not self._check_connection(f"set output state for {channel}"): return
        try:
            if enable:
                self.smu_device.set_output_on(channel)
                self.log_mgr.info(f"SMU Channel {channel} output set to ON.")
            else:
                self.smu_device.set_output_off(channel)
                self.log_mgr.info(f"SMU Channel {channel} output set to OFF.")
            
            # State Update
            self.channel_state[channel]['output'] = enable
        except Exception as e:
            self.log_mgr.error(f"Failed to set output state for {channel}: {e}")

    def measure_iv(self, channel: str) -> tuple[float, float] | None:
        """
        Führt eine Messung durch. Deaktiviert Kanal bei 'Invalid Response'.
        """
        if not self._check_connection(f"measure IV", channel): return None
        
        try:
            current, voltage = self.smu_device.measure_iv(channel)
            self.new_measurement_acquired.emit(channel, current, voltage)
            return current, voltage
        
        except Exception as e:
            # --- ÄNDERUNG: Fehlererkennung ---
            # Wenn ValueError (z.B. leere Antwort), dann existiert der Kanal wohl nicht
            if isinstance(e, ValueError):
                self._disable_channel(channel, f"Invalid Response ({e})")
                return None
            
            elif isinstance(e, (ConnectionError, serial.SerialException)):
                self.log_mgr.error(f"Critical connection error: {e}. Disconnecting.")
                self.disconnect()
                return None
            
            else:
                self.log_mgr.error(f"Error on {channel}: {e}")
                return None