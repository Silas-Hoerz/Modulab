# modules/profile/ProfileManager.py
# This Python file uses the following encoding: utf-8

import os # Für Zugriff auf Dateisystem
import json # Für ach was ist ja irgendwie selbst erklärend
from PySide6.QtCore import QObject, Signal

class ProfileManager(QObject):
        """
        Erstellt, speichert und bearbeitet Profile
        """
        #Signal
        profile_loaded = Signal(str)

        CONFIG_FILE_NAME = "config.json"
        KEY_LAST_PROFILE = "last_profile_name"

        def __init__(self, log_manager):
                super().__init__()  # Initialize QObject base class
                
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
                return os.path.join(self.working_dir, f"{profile_name}.json")
        
        def __read_from_file(self, profile_name):
                # Liest alle Daten von JSON File
                if not self.working_dir:
                        # Kein Zugriff auf working_dir
                        return {}
                profile_path = self.__get_profile_path(profile_name)
                try:
                        with open(profile_path, 'r', encoding= 'utf-8') as f:
                                data = json.load(f)
                        return data
                except FileNotFoundError:
                        # File nicht gefunden
                        return {}
                except (IOError, json.JSONDecodeError) as e:
                        self.log_mgr.error(f"Error reading file '{profile_name}': {e}")
                        return {}
        
        def __write_to_file(self, profile_name, data):
                # Speicher Daten in JSON
                if not self.working_dir:
                        # Kein Zugriff auf working_dir
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
                """ Lädt die separate Konfigurationsdatei des Managers. """
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
                """ Speichert die separate Konfigurationsdatei des Managers. """
                try:
                        with open(self.config_file_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=4, ensure_ascii=False)
                        return True
                except (IOError, OSError) as e:
                        self.log_mgr.error(f"Error writing manager config file: {e}")
                        return False



        # --- Öffentliche Funktionen ---- #

        def create_profile(self, profile_name, data = None):
                """
                Erstellt ein neues Profil
                """
                if not self.working_dir:
                        self.log_mgr.error("create_profile failed: no working_dir.")
                        return False

                profile_path = self.__get_profile_path(profile_name)
                if os.path.exists(profile_path):
                        self.log_mgr.warning(f"Profile '{profile_name}' already exists.")
                        return False

                # data = {"year": 2020, "sales": 12345678, "currency": "€"} Beispiel für data

                try:
                        with open(profile_path, 'w', encoding='utf-8') as f:
                                json.dump(data if data is not None else {}, f, indent=4, ensure_ascii=False)
                        self.log_mgr.info(f"Profile '{profile_name}' was created successfully.")
                        return True

                except (IOError, OSError) as e:
                        self.log_mgr.error(f"Error creating profile '{profile_name}': {e}")
                        return False

        def load_profile(self, profile_name):
                """
                Lädt ein Profil
                """
                if not self.working_dir:
                        # Kein Zugriff auf working_dir
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
        
        def delete_profile(self, profile_name):
                """
                Löscht ein Profil
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
                        config_data = self.__load_manager_config()
                        if config_data.get(self.KEY_LAST_PROFILE) == profile_name:
                                config_data[self.KEY_LAST_PROFILE] = None
                                self.__save_manager_config(config_data)
                                self.log_mgr.debug(f"Cleared last used profile (was '{profile_name}').")
                        return True

                except OSError as e:
                        self.log_mgr.error(f"Error deleting profile '{profile_name}': {e}")
                        return False

        def list_profiles(self):
                """
                Stellt Liste verfügbarer Profile zur Verfügung
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

        def write(self, key, value):
                """
                Schreibt Attribut (Key-Value-Paar) ind das akutell geladene Profil.
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
                Liest einen Wert anhand des 'key' aus dem akutellen Profil
                """
                if not self.current_profile_name:
                        self.log_mgr.error("read failed: no current_profile_name.")
                        return None
                return self.current_profile_data.get(key, None)
        
        def get_current_profile_name(self):
                """ Gibt den Namen des aktuell geladenen Profils zurück. """
                return self.current_profile_name

        def get_last_profile_name(self) -> str | None:
                """
                Gibt den Namen des zuletzt geladenen Profils zurück.
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