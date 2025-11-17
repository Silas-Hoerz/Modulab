# This Python file uses the following encoding: utf-8
import os
import logging # Thread sicheres logging
import datetime

from PySide6.QtCore import QObject, Signal # Nötig um Signale später an das Widget Modul zu senden

class LogManager(QObject):
    """
    Verwaltet das Logging für die gesamte Anwendung.

    Diese Klasse ist als zentraler Dienst konzipiert. Sie erfüllt zwei 
    Hauptaufgaben:

    1.  **Datei-Logging:** Schreibt alle Logs (DEBUG, INFO, WARNING, ERROR)
        in eine zeitgestempelte .log-Datei im Benutzerverzeichnis
        (`~/Modulab/Logs`) unter Verwendung des standard `logging`-Moduls.
    2.  **GUI-Benachrichtigung:** Speichert Logs im Speicher (in-memory) und
        löst das `message_logged`-Signal für jeden neuen Eintrag aus, 
        um UIs (wie ein Log-Widget) in Echtzeit zu aktualisieren.

    Sie wird typischerweise einmal erstellt und an alle anderen Manager
    übergeben.

    Signale:
        message_logged (dict):
            Wird für jeden Log-Eintrag (Info, Error, etc.) ausgelöst. 
            Das übergebene Wörterbuch (dict) hat die Struktur:
            `{'timestamp': datetime.datetime, 'type': str, 'message': str}`
    """
    
    # Signale
    message_logged = Signal(dict)
    
    # Definitionen der Massage Types
    INFO = "INFO"
    """str: Konstante für den 'INFO'-Log-Level."""
    WARNING = "WARNING"
    """str: Konstante für den 'WARNING'-Log-Level."""
    ERROR = "ERROR"
    """str: Konstante für den 'ERROR'-Log-Level."""
    DEBUG = "DEBUG"
    """str: Konstante für den 'DEBUG'-Log-Level."""

    def __init__(self):
        """
        Initialisiert den LogManager.

        Erstellt das Log-Verzeichnis (`~/Modulab/Logs`), falls es nicht existiert,
        und konfiguriert den Python `logging`-Handler für das
        zeitgestempelte Sitzungs-Logfile.

        Raises:
            RuntimeError: Wenn das Log-Verzeichnis nicht erstellt oder 
                          beschrieben werden kann.
        """
        super().__init__() # QObject __init__ aufrufen (Für Signale)

        self.messages_list = []
        self.latest_message = None # Speziell für das Status Label

        self.working_dir = os.path.join(os.path.expanduser('~'),'Modulab','Logs')
        self.logger = None
        self.log_file_path = None

        try:
            os.makedirs(self.working_dir, exist_ok = True)

            # Anlegen des Log Files - Jede Sitzung bekommt eigenes Log File
            now = datetime.datetime.now()
            log_filename = f"log_{now.strftime('%Y-%m-%d_%H-%M-%S')}.log"
            self.log_file_path = os.path.join(self.working_dir, log_filename)

            # Logger konfigurieren.
            self.logger = logging.getLogger('ModulabLogger')
            self.logger.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(self.log_file_path, encoding= 'utf-8')
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            if not self.logger.hasHandlers():
                self.logger.addHandler(file_handler)
            self.debug("LogManager initialisiert.") # loggt seine eigene Initialisierung

        except OSError as e:
            print(f"Fehler: Das Log-Verzeichnis konnte nicht erstellt oder gelesen werden: {e}")
            self.working_dir = None
            self.log_file_path = None
            raise RuntimeError(f"LogManager konnte nicht initialisiert werden: {e}") # Fail Fast!
    
    # --- Interne Funktionen ---- #
    def __log(self, msg_type, message):
        """
        Interne Log-Funktion. Nicht für den externen Aufruf gedacht.

        Loggt die Nachricht in die Datei (via self.logger), in die 
        In-Memory-Liste (self.messages_list) und löst das 
        `message_logged`-Signal aus.
        """
        message_str = str(message) # Sicheres einlesen der Nachricht

        log_entry = {
            'timestamp': datetime.datetime.now(),
            'type': msg_type,
            'message': message_str
        }

        self.messages_list.append(log_entry)
        self.latest_message = log_entry

        print(f"{log_entry['timestamp'].strftime('%H:%M:%S')} [{log_entry['type']}] {log_entry['message']}")

        if self.logger:
            if msg_type == self.INFO:
                self.logger.info(message_str)
            elif msg_type == self.WARNING:
                self.logger.warning(message_str)
            elif msg_type == self.ERROR:
                self.logger.error(message_str)
            elif msg_type == self.DEBUG:
                self.logger.debug(message_str)
            else:
                self.logger.info(message_str)
                
        # Signal an die GUI senden
        self.message_logged.emit(log_entry)

    # --- Öffentliche Log-Funktionen ---- #
    def info(self, message):
        """
        Loggt eine Info-Nachricht.

        Args:
            message (str): Die zu loggende Nachricht.

        Examples:
            Eine einfache Statusmeldung loggen:
            
            .. code-block:: python
            
                # Annahme: 'log_mgr' ist eine Instanz von LogManager
                log_mgr.info("Verbindung zum Gerät erfolgreich hergestellt.")
        """
        self.__log(self.INFO, message)

    def warning(self, message):
        """
        Loggt eine Warnung.

        Args:
            message (str): Die zu loggende Warnung.

        Examples:
            Eine Warnung für einen ungültigen Wert loggen:
            
            .. code-block:: python
            
                log_mgr.warning("Integrationszeit auf 0 gesetzt. Ignoriere Befehl.")
        """
        self.__log(self.WARNING, message)

    def error(self, message, exc_info = True):
        """
        Loggt einen Fehler.

        Standardmäßig wird die Ausnahme-Info (Stack Trace) mitgeloggt,
        wenn diese Funktion innerhalb eines `except`-Blocks aufgerufen wird.

        Args:
            message (str): Die zu loggende Fehlermeldung.
            exc_info (bool, optional): Wenn True (Standard), wird der 
                                       Stack Trace automatisch mitgeloggt.
                                       Setzen Sie auf False, um dies zu unterdrücken.

        Examples:
            Einen einfachen Fehler loggen (ohne Stack Trace):
            
            .. code-block:: python
            
                if not manager.is_connected():
                    log_mgr.error("Verbindung fehlgeschlagen. Kein Stack Trace.", exc_info=False)

            Einen Fehler innerhalb einer Ausnahmebehandlung loggen (mit Stack Trace):
            
            .. code-block:: python
            
                try:
                    # Code, der fehlschlagen könnte
                    result = 10 / 0
                except ZeroDivisionError as e:
                    # 'exc_info=True' ist Standard, aber hier zur Verdeutlichung.
                    # 'e' wird automatisch vom Logger erfasst.
                    log_mgr.error(f"Schwerer Rechenfehler: {e}", exc_info=True)
        """
        self.__log(self.ERROR, message)

        # Optional den ganzen Stack-Trace loggen
        if exc_info and self.logger:
            # logger.exception erfasst automatisch den Stack Trace
            self.logger.exception(message)

    def debug(self, message):
        """
        Loggt eine Debug-Nachricht.

        Diese Nachrichten sind oft sehr detailliert und nur für die
        Fehlersuche gedacht.

        Args:
            message (str): Die zu loggende Debug-Nachricht.

        Examples:
            Messwerte oder Zwischenschritte loggen:
            
            .. code-block:: python
            
                log_mgr.debug(f"Spektrum aufgenommen. {len(intensities)} Datenpunkte.")
        """
        self.__log(self.DEBUG, message)

    # --- Öffentliche Get-Funktionen ---- #
    def get_all_messages(self) -> list[dict]:
        """
        Gibt die komplette Liste aller Log-Einträge der aktuellen Sitzung zurück.

        Nützlich, um ein Log-Fenster beim Öffnen zu initialisieren.

        Returns:
            list[dict]: Eine Liste von Log-Einträgen. Jedes dict hat die
                        Struktur: `{'timestamp': datetime, 'type': str, 'message': str}`

        Examples:
            Alle bisherigen Logs beim Start eines Widgets laden:
            
            .. code-block:: python
            
                alle_logs = log_gmr.get_all_messages()
                for eintrag in alle_logs:
                    # z.B. in eine QListWidget einfügen
                    print(f"[{eintrag['type']}] {eintrag['message']}")
        """
        return self.messages_list
    
    def get_latest_message(self) -> dict | None:
        """
        Gibt nur den letzten Log-Eintrag zurück. (Für bspw. Status Label)

        Returns:
            dict | None: Der letzte Log-Eintrag als dict mit der Struktur
                         `{'timestamp': ..., 'type': ..., 'message': ...}`
                         oder `None`, wenn noch keine Logs vorhanden sind.

        Examples:
            Den Text für eine Statusleiste setzen:
            
            .. code-block:: python
            
                letzte_meldung = log_mgr.get_latest_message()
                if letzte_meldung:
                    status_bar.showMessage(letzte_meldung['message'])
        """
        return self.latest_message

# --- Selbsttest ---- #
if __name__ == "__main__":

    print("--- Starte LogManager Test ---")

    # 1. Initialisierung
    log_mgr = LogManager()

    # 2. Einfaches Logging
    log_mgr.info("Info Nachricht")
    log_mgr.debug("Debug Nachricht")
    log_mgr.warning("Warnung Nachricht")

    # 3. Letzte Nachricht abrufen
    print("\n--- Test: Get Latest Message ---")
    latest = log_mgr.get_latest_message()
    if latest:
        print(f"Letzte Meldung: [{latest['type']}] {latest['message']}")

    # 4. Fehler-Logging
    try:
        x = 10 / 0
    except ZeroDivisionError as e:
        # exc_info=True loggt den kompletten Fehler-Stack-Trace
        log_mgr.error(f"Fehler bei Berechnung: {e}", exc_info=True)

    # 5. Alle Nachrichten abrufen (für dein 'Terminal'-Feld)
    print("\n--- Test: Get All Messages ---")
    all_msgs = log_mgr.get_all_messages()

    print(f"Gesamte Historie ({len(all_msgs)} Einträge):")
    for msg in all_msgs:
        # Die GUI würde hier die Typen verwenden, um Farben zu setzen (z.B. Error=Rot)
        print(f"  [{msg['type']}] {msg['message']}")

    print("\n===== Test abgeschlossen =====")
    print(f"Log-Datei zu finden unter: {log_mgr.log_file_path}")
