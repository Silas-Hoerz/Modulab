"""
================================================================================
SMU (Source Measure Unit) Befehlsübersicht (Cheatsheet)
================================================================================

Hierbei ist 'smuX' als Platzhalter für die jeweilige SMU-Instanz zu 
verstehen (z.B. smua, smub).

--------------------------------------------------------------------------------
1. MESSFUNKTIONEN (smuX.measure)
--------------------------------------------------------------------------------

# --- Autorange (Messung) ---
smuX.measure.autorangei = smuX.AUTORANGE_ON     # Strommessung Autorange EIN
smuX.measure.autorangev = smuX.AUTORANGE_ON     # Spannungsmessung Autorange EIN
smuX.measure.autorangei = smuX.AUTORANGE_OFF    # Strommessung Autorange AUS
smuX.measure.autorangev = smuX.AUTORANGE_OFF    # Spannungsmessung Autorange AUS

# --- Manueller Messbereich (Range) ---
smuX.measure.rangei = rangeval                  # Strommessbereich setzen (z.B. 1e-3 für 1mA)
smuX.measure.rangev = rangeval                  # Spannungsmessbereich setzen (z.B. 10 für 10V)

# --- Messwerte abfragen (Readings) ---
reading = smuX.measure.i()                      # Aktuellen Strommesswert abfragen
reading = smuX.measure.v()                      # Aktuellen Spannungsmesswert abfragen
iReading, vReading = smuX.measure.iv()          # Strom- UND Spannungsmesswert abfragen
reading = smuX.measure.r()                      # Widerstandsmesswert abfragen
reading = smuX.measure.p()                      # Leistungsmesswert abfragen

--------------------------------------------------------------------------------
2. QUELLFUNKTIONEN (smuX.source)
--------------------------------------------------------------------------------

# --- Quellen-Funktion (Modus) ---
smuX.source.func = smuX.OUTPUT_DCVOLTS          # Quelle als Spannungsquelle (V-Source) konfigurieren
smuX.source.func = smuX.OUTPUT_DCAMPS           # Quelle als Stromquelle (I-Source) konfigurieren

# --- Pegel (Level) ---
smuX.source.levelv = sourceval                  # Spannungs-Quellwert setzen (wenn func=VOLTS)
smuX.source.leveli = sourceval                  # Strom-Quellwert setzen (wenn func=AMPS)

# --- Limits (Begrenzungen) ---
smuX.source.limitv = level                      # Spannungslimit setzen (Schutz)
smuX.source.limiti = level                      # Stromlimit setzen (Schutz)
smuX.source.limitp = level                      # Leistungslimit setzen (Schutz)

# --- Autorange (Quelle) ---
smuX.source.autorangev = smuX.AUTORANGE_ON      # Spannungsquelle Autorange EIN
smuX.source.autorangei = smuX.AUTORANGE_ON      # Stromquelle Autorange EIN
smuX.source.autorangev = smuX.AUTORANGE_OFF     # Spannungsquelle Autorange AUS
smuX.source.autorangei = smuX.AUTORANGE_OFF     # Stromquelle Autorange AUS

# --- Manueller Quellbereich (Range) ---
smuX.source.rangev = rangeval                   # Spannungs-Quellbereich setzen
smuX.source.rangei = rangeval                   # Strom-Quellbereich setzen

# --- Ausgang (Output) ---
smuX.source.output = smuX.OUTPUT_ON             # Quelle (Ausgang) einschalten
smuX.source.output = smuX.OUTPUT_OFF            # Quelle (Ausgang) ausschalten

--------------------------------------------------------------------------------
3. MESSEINSTELLUNGEN (smuX.sense)
--------------------------------------------------------------------------------

smuX.sense = smuX.SENSE_LOCAL                   # Lokale Messung (2-Leiter-Messung)
smuX.sense = smuX.SENSE_REMOTE                  # Fernmessung (4-Leiter-Messung / Kelvin-Messung)

"""

# ==========================================================================================
# Treiber Keithley2602
# ==========================================================================================
# https://download.tek.com/manual/2600AS-901-01--E-Aug2011--Ref.pdf

import time
import serial
from serial.tools import list_ports

# Konstanten für die TSP-Commands
#state
TSP_SMU_OFF = 'OUTPUT_OFF'
TSP_SMU_ON = 'OUTPUT_ON'

#func
TSP_DC_VOLTS = 'OUTPUT_DCVOLTS'
TSP_DC_AMPS = 'OUTPUT_DCAMPS'

#mode
TSP_SENSE_LOCAL = 'SENSE_LOCAL'
TSP_SENSE_REMOTE = 'SENSE_REMOTE'

class Keithley2602:
    """
    Low-Level-Treiber des Keithley2602
    """

    def __init__(self, log_manager):
        self.log_mgr = log_manager
        self._serial = serial.Serial() 
        self._serial.timeout = 2
    
        self.idn_message = ""

    # --- Verbindung ---

    @property
    def is_open(self) -> bool:
        """ Gibt den Status des Serialen Ports zurück """
        return self._serial.is_open
    
    def connect(self, port: str, baudrate: int = 115200) -> tuple[bool,str]:
        """ Versucht Verbindung zum Keithley aufzubauen """
        if self._serial.is_open:
            self.disconnect()

        try:
            self._serial.port = port
            self._serial.baudrate = baudrate
            self._serial.open()
            time.sleep(0.1) # sry for that!
            self._serial.read_all() # Buffer leeren
            self.log_mgr.info(f"Connected to SMU [{port}]...")


            # Befehl zum Auslesen der IDN
            self.idn_message = self.query("*IDN?").strip()

            return True, self.idn_message

        except serial.SerialException as e:
            pass
        except Exception as e:
            pass

    def disconnect(self):
        """ Schließt die serielle Verbindung """
        if self.is_open:
            try:
                self.set_output_state('a', TSP_SMU_OFF)
                self.set_output_state('b', TSP_SMU_OFF)
            except Exception as e:
                self.log_mgr.error(f"Could not turn off SMU ouput during disconntect: {e}")
            self._serial.close()
            self.log_mgr.info("Disconnected from Keithley SMU.") 

    # --- Auf Seriellen Port schreiben und lesen ---

    def send_command(self, command: str):
        """ Sendet einen Command an das Gerät."""
        if not self.is_open:
            raise ConnectionError("No Connection to SMU-Device.")
        cmd_bytes = (command + '\n').encode('ascii')
        self._serial.write(cmd_bytes)
        self.log_mgr.debug(f"[SMU_TX] {command}")
        time.sleep(0.05) # sry again but

    def read_response(self) -> str:
        """ Liest eine Antwort vom Gerät """
        if not self.is_open:
            return ""
        response = self._serial.readline().decode('ascii').strip()
        self.log_mgr.debug(f"[SMU_RX] {response}")
        return response
    
    # --- SMU - Funktionen ---

    def query(self, command : str) -> str:
        """sendet einen Befehl und liest die Antwort."""
        self.send_command(command)
        return self.read_response()
    
    def reset_channel(self, channel: str):
        """Setzt Channel der SMU zurück"""
        self.send_command(f"smu{channel}.reset()")

    def set_source_function(self, channel: str, func: str):
        """Stellt die Source-Funktion (Spannung/Strom für einen Kanal ein.)"""
        self.send_command(f"smu{channel}.source.func = smu{channel}.{func}")

    def set_sense_mode(self, channel: str, mode: str):
        """Stellt den Sense_Modus (2- oder 4-Draht) für einen Kanal ein."""
        self.send_command(f"smu{channel}.sense = smu{channel}.{mode}")

    def set_source_level(self, channel: str, func: str, level: float):
        """Stellt das Source-Level (Spannungs- Stromwert) für einen Kanal ein."""
        level_command = 'levelv' if func == TSP_DC_VOLTS else 'leveli'
        self.send_command(f"smu{channel}.source.{level_command} = {level}")

    def set_source_limit(self, channel: str, func: str, limit: float):
        """Stellt den Source-Limit (Stom- Spannungslimit) für einen Kanal ein."""
        limit_command = 'limiti' if func == TSP_DC_VOLTS else 'limitv'  
        self.send_command(f"smu{channel}.source.{limit_command} = {limit}")

    def set_output_state(self, channel: str, state: str):
        """Schaltet den Ausgang eines Kanals ein oder aus."""
        self.send_command(f"smu{channel}.source.output = smu{channel}.{state}")

    def measure_iv(self, channel: str) -> tuple[float, float]:
        """Misst Strom und Spannung für einen Kanal und gibt sie zurück."""
        response = self.query(f"print(smu{channel}.measure.iv())")
        try:
            parts = response.split('\t')
            return float(parts[0]), float(parts[1])
        except (ValueError, IndexError, TypeError):
            self.log_mgr.error(f"Invalid response from SMU during measurement: '{response}'")
            raise ValueError(f"Invalid SMU response: '{response}'")