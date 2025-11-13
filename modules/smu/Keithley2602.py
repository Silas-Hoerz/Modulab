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

# Die Verbindung läuft über einen seriellen Port RS232 
# Mann kann wahrscheinlich auch über den USB Port der neuen SMU ein Virtuellen Com Port nutzen.
# Am besten einfach mal auspobieren 
import serial
from serial.tools import list_ports

class Keithley2602:
    """
    Low-Level-Treiber des Keithley2602
    """

    def __init__(self,log_manager):
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
            self.log_mgr.error(f"Serial connection error: {e}")
            return False, str(e)
        except Exception as e:
            self.log_mgr.error(f"Unexpected connection error: {e}")
            return False, str(e)

    def disconnect(self):
        """ Schließt die serielle Verbindung """
        if self.is_open:
            try:
                self.set_output_off('a')
                self.set_output_off('b')
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

    def set_source_current(self, channel: str):
        """Stellt die Source-Funktion auf Strom für einen Kanal"""
        self.send_command(f"smu{channel}.source.func = smu{channel}.OUTPUT_DCAMPS")

    def set_source_voltage(self, channel: str):
        """Stellt die Source-Funktion auf Spannung für einen Kanal"""
        self.send_command(f"smu{channel}.source.func = smu{channel}.OUTPUT_DCVOLTS")

    def set_sense_mode_local(self, channel: str):
        """Stellt den Sense_Modus (2-Draht) für einen Kanal ein."""
        self.send_command(f"smu{channel}.sense = smu{channel}.SENSE_LOCAL")
    
    def set_sense_mode_remote(self, channel: str):
        """Stellt den Sense_Modus (4-Draht) für einen Kanal ein."""
        self.send_command(f"smu{channel}.sense = smu{channel}.SENSE_REMOTE")

    def set_source_voltage_level(self, channel: str, level: float):
        """Stellt das Source-Level (Spannungswert) für einen Kanal ein."""
        self.send_command(f"smu{channel}.source.levelv = {level}")

    def set_source_current_level(self, channel: str, level: float):
        """Stellt das Source-Level (Stromwert) für einen Kanal ein."""
        self.send_command(f"smu{channel}.source.leveli = {level}")

    def set_source_voltage_limit(self, channel: str, limit: float):
        """Stellt den Source-Limit (Spannungslimit) für einen Kanal ein."""
        self.send_command(f"smu{channel}.source.limitv = {limit}")
                          
    def set_source_current_limit(self, channel: str, limit: float):
        """Stellt den Source-Limit (Stomlimit) für einen Kanal ein."""
        self.send_command(f"smu{channel}.source.limiti = {limit}")

    def set_output_on(self, channel: str):
        """Schaltet den Ausgang eines Kanals ein."""
        self.send_command(f"smu{channel}.source.output = smu{channel}.OUTPUT_ON")
    
    def set_output_off(self, channel: str):
        """Schaltet den Ausgang eines Kanals aus."""
        self.send_command(f"smu{channel}.source.output = smu{channel}.OUTPUT_OFF")

    def measure_iv(self, channel: str) -> tuple[float, float]:
        """Misst Strom und Spannung für einen Kanal und gibt sie zurück."""
        response = self.query(f"print(smu{channel}.measure.iv())")
        try:
            parts = response.split('\t')
            return float(parts[0]), float(parts[1])
        except (ValueError, IndexError, TypeError):
            self.log_mgr.error(f"Invalid response from SMU during measurement: '{response}'")
            raise ValueError(f"Invalid SMU response: '{response}'")

# ==========================================================================================
#  Dummy Treiber
# ==========================================================================================

class DummyKeithley2602:
    """
    Simuliert einen Keithley2602-Treiber für Tests ohne angeschlossene Hardware.
    Verhält sich nach außen hin (API) identisch zum echten Treiber.
    """
    def __init__(self, log_manager):
        self.log_mgr = log_manager
        self._is_open = False
        self.idn_message = "DUMMY INC., MODEL 2602 (SIMULATED), 1.0, 1.0"
        self.simulated_resistance = 100.0 # 100 Ohm, wie gewünscht
        
        # Interner Zustand der simulierten Kanäle
        self._channel_states = {}
        self.reset_channel('a')
        self.reset_channel('b')

    @property
    def is_open(self) -> bool:
        return self._is_open

    def connect(self, port: str, baudrate: int = 115200) -> tuple[bool, str]:
        self.log_mgr.info(f"Connected to DUMMY SMU (Port: {port})...")
        self._is_open = True
        time.sleep(0.1) # Simuliere Verbindungszeit
        return True, self.idn_message

    def disconnect(self):
        if self._is_open:
            self.set_output_off('a')
            self.set_output_off('b')
            self._is_open = False
            self.log_mgr.info("Disconnected from DUMMY SMU.")

    def query(self, command: str) -> str:
        self.log_mgr.debug(f"[DUMMY_TX] {command}")
        if command == "*IDN?":
            return self.idn_message
        return ""

    def reset_channel(self, channel: str):
        self.log_mgr.debug(f"[DUMMY] Resetting channel {channel}")
        self._channel_states[channel] = {
            'func': 'V', # 'V' (Spannung) oder 'I' (Strom)
            'level': 0.0,
            'v_limit': 20.0, # Standard 20V Limit
            'i_limit': 0.1,  # Standard 100mA Limit
            'output': False # ON/OFF
        }

    def set_source_current(self, channel: str):
        self._channel_states[channel]['func'] = 'I'
        self.log_mgr.debug(f"[DUMMY] Channel {channel} set to CURRENT source")

    def set_source_voltage(self, channel: str):
        self._channel_states[channel]['func'] = 'V'
        self.log_mgr.debug(f"[DUMMY] Channel {channel} set to VOLTAGE source")

    def set_sense_mode_local(self, channel: str):
        self.log_mgr.debug(f"[DUMMY] Channel {channel} set to LOCAL sense")

    def set_sense_mode_remote(self, channel: str):
        self.log_mgr.debug(f"[DUMMY] Channel {channel} set to REMOTE sense")

    def set_source_voltage_level(self, channel: str, level: float):
        self._channel_states[channel]['level'] = level

    def set_source_current_level(self, channel: str, level: float):
        self._channel_states[channel]['level'] = level

    def set_source_voltage_limit(self, channel: str, limit: float):
        self._channel_states[channel]['v_limit'] = limit

    def set_source_current_limit(self, channel: str, limit: float):
        self._channel_states[channel]['i_limit'] = limit

    def set_output_on(self, channel: str):
        self._channel_states[channel]['output'] = True
        self.log_mgr.debug(f"[DUMMY] Channel {channel} output ON")

    def set_output_off(self, channel: str):
        self._channel_states[channel]['output'] = False
        self.log_mgr.debug(f"[DUMMY] Channel {channel} output OFF")

    def measure_iv(self, channel: str) -> tuple[float, float]:
        if not self._is_open:
            raise ConnectionError("DUMMY SMU is not connected.")
        
        state = self._channel_states[channel]
        
        if not state['output']:
            # Wenn Output aus ist, messe 0V / 0A (mit etwas Rauschen)
            return 0.0, 0.0 

        # --- Simulation 100 Ohm ---
        voltage = 0.0
        current = 0.0
        
        if state['func'] == 'V':
            # Spannungsquelle: Spannung ist fix, Strom wird berechnet
            voltage = state['level']
            current = voltage / self.simulated_resistance
            
            # Strom-Limit (Compliance) prüfen
            if abs(current) > abs(state['i_limit']):
                current = state['i_limit'] * (1 if current > 0 else -1)
                # Spannung bricht in der Realität auch ein, aber das ist eine Vereinfachung
                self.log_mgr.warning(f"[DUMMY] Channel {channel} current limit reached!")

        else: # state['func'] == 'I'
            # Stromquelle: Strom ist fix, Spannung wird berechnet
            current = state['level']
            voltage = current * self.simulated_resistance
            
            # Spannungs-Limit (Compliance) prüfen
            if abs(voltage) > abs(state['v_limit']):
                voltage = state['v_limit'] * (1 if voltage > 0 else -1)
                self.log_mgr.warning(f"[DUMMY] Channel {channel} voltage limit reached!")

        self.log_mgr.debug(f"[DUMMY] Measured: C={current}, V={voltage}")
        return current, voltage  
# ==========================================================================================
#  Main zum Testen des Treibers
# ==========================================================================================
import sys
# Der LogManager ist teil der gesmaten Software deshalb hier ein kleiner Dummy zum testen
class DummyLogManager:
    """Ein einfacher Logger der auf die Konsole druckt."""
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def debug(self, msg):
        print(f"[DEBUG] {msg}")
    
    def warning(self, msg):
        print(f"[WARN] {msg}")
    
    def error(self, msg):
        print(f"[ERROR] {msg}")

if __name__ == "__main__":
    
    # 1. Dummy-Logger und Treiber-Instanz erstellen
    log_manager = DummyLogManager()
    smu = DummyKeithley2602(log_manager=log_manager)

    # 2. Verfügbare COM-Ports finden
    log_manager.info("Suche nach verfügbaren COM-Ports...")
    ports = list_ports.comports()
    
    if not ports:
        log_manager.error("Keine COM-Ports gefunden. Bitte SMU anschließen und Treiber prüfen.")
        sys.exit(1)

    # Hier den COM Port auswählen - is
    log_manager.info("Verfügbare Ports:")
    for i, port in enumerate(ports):
        print(f"  [{i}] {port.device}: {port.description}")
    
    port_to_use = ""
    while not port_to_use:
        try:
            choice_str = input("Bitte Nummer des zu verwendenden Ports eingeben: ")
            choice_int = int(choice_str)
            if 0 <= choice_int < len(ports):
                port_to_use = ports[choice_int].device
            else:
                log_manager.warning(f"Ungültige Auswahl. Bitte Zahl zwischen 0 und {len(ports)-1} eingeben.")
        except ValueError:
            log_manager.warning("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        except EOFError:
            log_manager.error("Auswahl abgebrochen.")
            sys.exit(1)

    # 3. Test-Sequenz (mit try...finally, um sauberes Trennen zu garantieren)
    try:
        # --- Verbindungstest ---
        connected, idn = smu.connect(port_to_use)
        if not connected:
            log_manager.error(f"Verbindung fehlgeschlagen: {idn}")
            sys.exit(1)
        
        log_manager.info(f"Erfolgreich verbunden. IDN: {idn}")
        
        # --- TEST 1: Kanal A als Spannungsquelle (V-Source) ---
        log_manager.info("--- TEST 1: Kanal A (V-Source) ---")
        smu.reset_channel('a')
        smu.set_source_voltage('a')
        smu.set_sense_mode_local('a') # 2-Draht
        smu.set_source_voltage_level('a', 1.0) # 1.0 Volt
        smu.set_source_current_limit('a', 0.1) # 100 mA Limit
        
        smu.set_output_on('a')
        log_manager.info("Kanal A Output [ON]")
        time.sleep(0.5) # Warte auf Stabilisierung
        
        i_a, v_a = smu.measure_iv('a')
        log_manager.info(f"Messung Kanal A: Spannung={v_a:.4f} V, Strom={i_a:.6f} A")
        
        smu.set_output_off('a')
        log_manager.info("Kanal A Output [OFF]")
        
        # --- TEST 2: Kanal B als Stromquelle (I-Source) ---
        log_manager.info("--- TEST 2: Kanal B (I-Source) ---")
        smu.reset_channel('b')
        smu.set_source_current('b')
        smu.set_sense_mode_local('b') # 2-Draht
        smu.set_source_current_level('b', 0.01) # 10 mA
        smu.set_source_voltage_limit('b', 5.0) # 5 V Limit
        
        smu.set_output_on('b')
        log_manager.info("Kanal B Output [ON]")
        time.sleep(0.5) # Warte auf Stabilisierung
        
        i_b, v_b = smu.measure_iv('b')
        log_manager.info(f"Messung Kanal B: Spannung={v_b:.4f} V, Strom={i_b:.6f} A")
        
        smu.set_output_off('b')
        log_manager.info("Kanal B Output [OFF]")
        
        log_manager.info("--- Test erfolgreich beendet ---")

    except ConnectionError as e:
        log_manager.error(f"Verbindungsfehler während des Betriebs: {e}")
    except ValueError as e:
        log_manager.error(f"Messfehler (ungültige Antwort): {e}")
    except Exception as e:
        log_manager.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    
    finally:
        # 4. Verbindung trennen
        if smu.is_open:
            log_manager.info("Trenne Verbindung zur SMU...")
            smu.disconnect()
        else:
            log_manager.info("Verbindung bereits getrennt.")