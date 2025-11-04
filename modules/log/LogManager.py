# modules/log/LogManager.py
# This Python file uses the following encoding: utf-8
import os
import logging # Thread sicheres logging
import datetime

from PySide6.QtCore import QObject, Signal  # Nötig um Signale später an das Widget Modul zu senden

class LogManager(QObject):
    
    # Signale
    message_logged = Signal(dict)
    
    # Definitionen der Massage Types
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

    def __init__(self):
        
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
        Loggt die Nachricht.
        Schreibt in die Log-Datei UND in die In-Memory-Liste
        """
        message_str =  str(message) # Sicheres einlesen der Nachricht

        log_entry = {
            'timestamp': datetime.datetime.now(),
            'type': msg_type,
            'message': message_str
        }

        self.messages_list.append(log_entry)
        self.latest_message = log_entry

        print(f"{log_entry['timestamp'].strftime('%H:%M:%S')} [{log_entry['type']}] {log_entry['message']}")

        if self.logger:
            if msg_type == self.INFO:           # theoretisch reicht auch der else case xD
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
        """ Loggt eine Info-Nachricht. """
        self.__log(self.INFO, message)

    def warning(self, message):
        """ Loggt eine Warnung. """
        self.__log(self.WARNING, message)

    def error(self, message, exc_info = True):
        """ Loggt einen Fehler. """
        self.__log(self.ERROR, message)

        # Optional den ganzen Stack-Trace loggen
        if exc_info and self.logger:
            self.logger.exception(message)

    def debug(self, message):
        """ Loggt eine Debug-Nachricht. """
        self.__log(self.DEBUG, message)

    # --- Öffentliche Get-Funktionen ---- #
    def get_all_messages(self):
        """
        Gibt die komplette Liste aller Log-Einträge der aktuellen Sitzung zurück.

        Format: [{'timestamp':..., 'type':..., 'message':...}, ...]
        """
        return self.messages_list
    
    def get_latest_message(self):
        """
        Gibt nur den letzten Log-Eintrag zurück. (Für bspw. Status Label)

        Format: {'timestamp':..., 'type':..., 'message':...}
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
