# This Python file uses the following encoding: utf-8

import os # Für Zugriff auf Dateisystem
import json # Für ach was ist ja irgendwie selbst erklärend
from PySide6.QtCore import QObject, Signal

class ProfileManager(QObject):
    """
    Erstellt, speichert und verwaltet Benutzerprofile (Key-Value-Speicher).

    Diese Klasse verwaltet app-weite Einstellungen, indem sie diese in
    `.json`-Dateien im Benutzerverzeichnis (`~/Modulab/Profiles`) speichert.
    Jede `.json`-Datei repräsentiert ein "Profil" (z.B. "Experiment_A", "Default").

    Sie dient als zentraler Key-Value-Speicher für alle anderen Manager
    (z.B. zum Speichern der letzten Integrationszeit oder des letzten
    verbundenen Geräts).

    Args:
        log_manager (LogManager): Eine Instanz des LogManagers für das Logging.

    Signale:
        profile_loaded (str):
            Wird ausgelöst, nachdem `load_profile` erfolgreich war.
            Args: (str: Der Name des geladenen Profils).
    """
    #Signal
    profile_loaded = Signal(str)

    CONFIG_FILE_NAME = "config.json"
    """str: Interner Dateiname für die Manager-Konfiguration (z.B. letztes Profil)."""
    KEY_LAST_PROFILE = "last_profile_name"
    """str: Interner Schlüssel zum Speichern des Namens des zuletzt geladenen Profils."""

    def __init__(self, log_manager):
        """
        Initialisiert den ProfileManager.

        Erstellt das Profil-Verzeichnis (`~/Modulab/Profiles`), falls es 
        nicht existiert.

        Args:
            log_manager (LogManager): Die LogManager-Instanz.
        """
        super().__init__() # Initialize QObject base class
        
        self.log_mgr = log_manager # Log_Manager übernehmen

        self.working_dir = os.path.join(os.path.expanduser('~'),'Modulab','Profiles')

        self.current_profile_name = None
        self.current_profile_data = {}

        self.config_file_path = ""

        try:
            os.makedirs(self.working_dir, exist_ok = True)
            self.config_file_path = os.path.join(self.working_dir, self.CONFIG_FILE_NAME)
            self.log_mgr.debug(f"Working Dir: '{self.working_dir}'")
            self.log_mgr.debug(f"Manager Config: '{self.config_file_path}'")

        except OSError as e:
            self.log_mgr.error(f"Directory could not be created: {e}")
            self.working_dir = None


    # --- Interne Funktionen ---- #

    def __get_profile_path(self, profile_name):
        """Erstellt den vollständigen Dateipfad für einen Profilnamen."""
        return os.path.join(self.working_dir, f"{profile_name}.json")
    
    def __read_from_file(self, profile_name):
        """Liest alle Daten aus einer JSON-Profildatei."""
        if not self.working_dir:
            return {}
        profile_path = self.__get_profile_path(profile_name)
        try:
            with open(profile_path, 'r', encoding= 'utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return {}
        except (IOError, json.JSONDecodeError) as e:
            self.log_mgr.error(f"Error reading file '{profile_name}': {e}")
            return {}
    
    def __write_to_file(self, profile_name, data):
        """Speichert Daten in eine JSON-Profildatei."""
        if not self.working_dir:
            return False
        profile_path = self.__get_profile_path(profile_name)
        try:
            with open(profile_path, 'w', encoding= 'utf-8') as f:
                json.dump (data, f, indent = 4, ensure_ascii=False)
            return True

        except (IOError, OSError) as e:
            self.log_mgr.error(f"Error writing file '{profile_name}': {e}")
            return False
            
    def __load_manager_config(self) -> dict:
        """ Lädt die separate Konfigurationsdatei des Managers (config.json)."""
        if not os.path.exists(self.config_file_path):
            return {}
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (IOError, json.JSONDecodeError) as e:
            self.log_mgr.error(f"Error reading manager config file: {e}")
            return {}

    def __save_manager_config(self, data: dict) -> bool:
        """ Speichert die separate Konfigurationsdatei des Managers (config.json). """
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            self.log_mgr.error(f"Error writing manager config file: {e}")
            return False



    # --- Öffentliche Funktionen ---- #

    def create_profile(self, profile_name: str, data: dict = None) -> bool:
        """
        Erstellt eine neue, leere Profildatei (.json).

        Wenn `data` angegeben wird, wird das Profil mit diesen 
        Anfangswerten erstellt.

        Args:
            profile_name (str): Der Name für das neue Profil (ohne .json).
            data (dict, optional): Ein Wörterbuch mit Anfangsdaten 
                                   für das Profil.

        Returns:
            bool: True bei Erfolg, False, wenn das Profil bereits existiert
                  oder ein Fehler auftritt.

        Examples:
            Ein neues, leeres Profil "Experiment_A" erstellen:
            
            .. code-block:: python
            
                profile_mgr.create_profile("Experiment_A")

            Ein Profil mit Standard-Einstellungen für ein Spektrometer erstellen:
            
            .. code-block:: python
            
                default_settings = {
                    "Spec_integration_time_us": 10000,
                    "Spec_correct_dark_counts": False
                }
                profile_mgr.create_profile("Default_Spektrometer", data=default_settings)
        """
        if not self.working_dir:
            self.log_mgr.error("create_profile failed: no working_dir.")
            return False

        profile_path = self.__get_profile_path(profile_name)
        if os.path.exists(profile_path):
            self.log_mgr.warning(f"Profile '{profile_name}' already exists.")
            return False

        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(data if data is not None else {}, f, indent=4, ensure_ascii=False)
            self.log_mgr.info(f"Profile '{profile_name}' was created successfully.")
            return True

        except (IOError, OSError) as e:
            self.log_mgr.error(f"Error creating profile '{profile_name}': {e}")
            return False

    def load_profile(self, profile_name: str) -> bool:
        """
        Lädt ein Profil in den Speicher und macht es zum "aktuellen" Profil.

        Alle zukünftigen `read()`- und `write()`-Operationen beziehen sich
        auf dieses Profil. Setzt auch dieses Profil als "zuletzt verwendet".

        Args:
            profile_name (str): Der Name des zu ladenden Profils.

        Returns:
            bool: True bei Erfolg, False, wenn das Profil nicht gefunden wurde.

        Examples:
            Das "Default" Profil beim Start laden:
            
            .. code-block:: python
            
                if not profile_mgr.load_profile("Default"):
                    profile_mgr.create_profile("Default")
                    profile_mgr.load_profile("Default")
        """
        if not self.working_dir:
            return False
        profile_path = self.__get_profile_path(profile_name)
        if not os.path.exists(profile_path):
            self.log_mgr.error(f"load_profile failed: Profile '{profile_name}' not found.")
            return False
        
        self.current_profile_name = profile_name
        self.current_profile_data = self.__read_from_file(profile_name)
        self.profile_loaded.emit(profile_name)
        self.log_mgr.info(f"Profile '{profile_name}' loaded successfully.")

        try:
            config_data = self.__load_manager_config()
            config_data[self.KEY_LAST_PROFILE] = profile_name
            self.__save_manager_config(config_data)
            self.log_mgr.debug(f"Set '{profile_name}' as last used profile.")
        except Exception as e:
            self.log_mgr.warning(f"Could not set last used profile: {e}")

        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Löscht eine Profildatei (.json) vom Datenträger.

        Args:
            profile_name (str): Der Name des zu löschenden Profils.

        Returns:
            bool: True bei Erfolg, False, wenn die Datei nicht existiert
                  oder ein Fehler auftritt.
        """
        if not self.working_dir:
            self.log_mgr.error("delete_profile failed: no working_dir.")
            return False

        profile_path = self.__get_profile_path(profile_name)
        if not os.path.exists(profile_path):
            self.log_mgr.warning(f"Profile '{profile_name}' does not exist.")
            return False

        try:
            os.remove(profile_path)
            self.log_mgr.info(f"Profile '{profile_name}' was deleted successfully.")
            
            # Prüfen, ob dies das "zuletzt geladene" Profil war
            config_data = self.__load_manager_config()
            if config_data.get(self.KEY_LAST_PROFILE) == profile_name:
                config_data[self.KEY_LAST_PROFILE] = None
                self.__save_manager_config(config_data)
                self.log_mgr.debug(f"Cleared last used profile (was '{profile_name}').")
            return True

        except OSError as e:
            self.log_mgr.error(f"Error deleting profile '{profile_name}': {e}")
            return False

    def list_profiles(self) -> list[str]:
        """
        Listet alle verfügbaren Profile (alle .json-Dateien) im Profilordner auf.

        Returns:
            list[str]: Eine alphabetisch sortierte Liste aller Profilnamen.

        Examples:
            Eine QComboBox mit allen Profilen füllen:
            
            .. code-block:: python
            
                profil_liste = profile_mgr.list_profiles()
                ui.profile_combobox.clear()
                ui.profile_combobox.addItems(profil_liste)
        """
        if not self.working_dir:
            self.log_mgr.error("list_profiles failed: no working_dir.")
            return []

        try:
            all_files = os.listdir(self.working_dir)
            profile_names = []
            for f in all_files:
                if f.endswith('.json') and f != self.CONFIG_FILE_NAME:
                    profile_name = os.path.splitext(f)[0]
                    profile_names.append(profile_name)
            return sorted(profile_names)

        except OSError as e:
            self.log_mgr.error(f"Error listing profiles: {e}")
            return []

    def write(self, key: str, value) -> bool:
        """
        Schreibt ein Key-Value-Paar in das *aktuell geladene* Profil.

        Dies ist die Hauptmethode für andere Manager, um ihre
        Einstellungen zu speichern.

        Args:
            key (str): Der Einstellungs-Schlüssel (z.B. "Spec_integration_time_us").
            value (any): Der zugehörige Wert (muss JSON-serialisierbar sein).

        Returns:
            bool: True bei Erfolg, False, wenn kein Profil geladen ist.

        Examples:
            Einstellungen von anderen Managern speichern:
            
            .. code-block:: python
            
                # Im SpectrometerManager (nach Änderung der Integrationszeit)
                time_us = 100000
                profile_mgr.write("Spec_integration_time_us", time_us)
                
                # Im SmuManager (nach Verbindung)
                port = "COM3"
                profile_mgr.write("Smu_LastDevice", port)
        """
        if not self.current_profile_name:
            self.log_mgr.error("write failed: no current_profile_name.")
            return False
        if not self.working_dir:
            self.log_mgr.error("write failed: no working_dir.")
            return False

        # Daten im RAM aktualisieren
        self.current_profile_data[key] = value

        # Daten in Datei sichern
        success = self.__write_to_file(self.current_profile_name, self.current_profile_data)
        if success:
            self.log_mgr.debug(f"Attribute '{key}' updated successfully.")
        return success

    def read(self, key):
        """
        Liest einen Wert anhand des 'key' aus dem *aktuell geladenen* Profil.

        Dies ist die Hauptmethode für andere Manager, um ihre
        Einstellungen zu laden.

        Args:
            key (str): Der Einstellungs-Schlüssel (z.B. "Spec_integration_time_us").

        Returns:
            any | None: Der gespeicherte Wert, oder `None`, wenn der Schlüssel
                        nicht existiert oder kein Profil geladen ist.

        Examples:
            Einstellungen in anderen Managern laden:
            
            .. code-block:: python
            
                # Im SpectrometerManager (während __init__)
                # Lade gespeicherte Zeit, oder nutze 100ms als Standard
                default_time = 100 * 1000
                time_us = profile_mgr.read("Spec_integration_time_us")
                
                if time_us is None:
                    time_us = default_time
                
                self.set_integrationtime(time_us)
        """
        if not self.current_profile_name:
                self.log_mgr.error("read failed: no current_profile_name.")
                return None
        return self.current_profile_data.get(key, None)
    
    def get_current_profile_name(self) -> str | None:
        """
        Gibt den Namen des aktuell geladenen Profils zurück.

        Returns:
            str | None: Der Name des Profils, oder `None`.
        """
        return self.current_profile_name

    def get_last_profile_name(self) -> str | None:
        """
        Liest aus der `config.json`, welches Profil zuletzt geladen wurde.

        Prüft gleichzeitig, ob dieses Profil noch existiert.

        Returns:
            str | None: Der Name des letzten Profils, oder `None`.

        Examples:
            Beim App-Start das letzte Profil automatisch laden:
            
            .. code-block:: python
            
                last_profile = profile_mgr.get_last_profile_name()
                if last_profile:
                    profile_mgr.load_profile(last_profile)
                else:
                    # Lade Fallback oder zeige Profil-Auswahl
                    profile_mgr.load_profile("Default")
        """
        config_data = self.__load_manager_config()
        last_name = config_data.get(self.KEY_LAST_PROFILE, None)

        if not last_name:
            return None

        # Sicherheitscheck: Existiert dieses Profil überhaupt noch?
        profile_path = self.__get_profile_path(last_name)
        if not os.path.exists(profile_path):
            self.log_mgr.warning(f"Last used profile '{last_name}' no longer exists.")
            # Bereinige die ungültige Einstellung
            config_data[self.KEY_LAST_PROFILE] = None
            self.__save_manager_config(config_data)
            return None
        
        self.log_mgr.debug(f"Found last used profile: '{last_name}'")
        return last_name

# --- Selbsttest ---- #

if __name__ == "__main__":

    print("--- Starte ProfileManager Test ---")

    # 1. Initialisierung
    pm = ProfileManager()

    # 2. Profile erstellen
    print("\n--- Test: create_profile ---")
    pm.create_profile("Test_Profil_A")
    pm.create_profile("Test_Profil_B")

    # 3. Profile auflisten
    print("\n--- Test: list_profiles ---")
    alle_profile = pm.list_profiles()
    print(f"Gefundene Profile: {alle_profile}")

    # 4. Test Profil A laden und beschreiben
    print("\n--- Test: load_profile & write (Test_Profil_A) ---")
    pm.load_profile("Test_Profil_A")
    pm.write("Value1", 150)
    pm.write("Value2", 42)
    pm.write("Data1", {"x": 1.1, "y": -0.5})

    # 5. Test Profil B laden und beschreiben
    print("\n--- Test: load_profile & write (Test_Profil_B) ---")
    pm.load_profile("Test_Profil_B")
    pm.write("Sting1", "22")
    pm.write("String2", "Ein ganzer Satz!")

    # 6. Test Profil A erneut laden und Daten lesen
    print("\n--- Test: load_profile & read (Profil A) ---")
    pm.load_profile("Test_Profil_A")

    # 7. Daten aus Test Profil A lesen
    Value1 = pm.read("Value1")
    Value2 = pm.read("Value2")

    # 8. Nicht existierenden Wert lesen (sollte None sein)
    print("Lese nicht-existenten Key:")
    missing = pm.read("gibt_es_nicht")

    print("\n===== Test abgeschlossen =====")