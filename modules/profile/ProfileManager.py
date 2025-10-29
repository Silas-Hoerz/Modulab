# This Python file uses the following encoding: utf-8

import os # Für Zugriff auf Dateisystem
import json # Für ach was ist ja irgendwie selbst erklärend

class ProfileManager:
        """
        Erstellt, speichert und bearbeitet Profile
        """

        def __init__(self, log_manager):

                self.log_mgr = log_manager # Log_Manager übernehmen

                self.working_dir = os.path.join(os.path.expanduser('~'),'Modulab','Profiles')

                self.current_profile_name = None
                self.current_profile_data = {}


                try:
                        os.makedirs(self.working_dir, exist_ok = True)
                        self.log_mgr.debug(f"Working Dir: '{self.working_dir}'")
                        # self.list_profiles()

                except OSError as e:
                        self.log_mgr.error(f"Verzeichnis konnte nicht erstellt werden: {e}")
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
                        self.log_mgr.error(f"Fehler beim Lesen der Datei '{profile_name}': {e}")
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
                        self.log_mgr.error(f"Fehler beim Schreiben der Datei '{profile_name}': {e}")
                        return False



        # --- Öffentliche Funktionen ---- #

        def create_profile(self, profile_name, data = None):
                """
                Erstellt ein neues Profil
                """
                if not self.working_dir:
                        self.log_mgr.error("create_profile fehlgeschlagen: Kein working_dir.")
                        return False

                profile_path = self.__get_profile_path(profile_name)
                if os.path.exists(profile_path):
                        self.log_mgr.warning(f"Profil '{profile_name}' existiert bereits.")
                        return False

                # data = {"year": 2020, "sales": 12345678, "currency": "€"} Beispiel für data

                try:
                        with open(profile_path, 'w', encoding='utf-8') as f:
                                json.dump(data if data is not None else {}, f, indent=4, ensure_ascii=False)
                        self.log_mgr.info(" Profil '{profile_name}' wurde erfolgreich erstellt.")
                        return True

                except (IOError, OSError) as e:
                        self.log_mgr.error("Fehler beim Erstellen des Profils '{profile_name}': {e}")
                        return False

        def load_profile(self, profile_name):
                """
                Lädt ein Profil
                """
                if not self.working_dir:
                        # Kein Zugriff auf working_dir
                        return False
                self.current_profile_name = profile_name
                self.current_profile_data = self.__read_from_file(profile_name)
                self.log_mgr.info(" Profil '{profile_name}' wurde erfolgreich geladen.")
                return True

        def list_profiles(self):
                """
                Stellt Liste verfügbarer Profile zur Verfügung
                """
                if not self.working_dir:
                        self.log_mgr.error("list_profiles fehlgeschlagen: Kein working_dir.")
                        return []

                try:

                        all_files = os.listdir(self.working_dir)

                        profile_names = []

                        for f in all_files:
                                if f.endswith('.json'):
                                        profile_name = os.path.splitext(f)[0]
                                        profile_names.append(profile_name)

                        return sorted(profile_names)

                except OSError as e:
                        self.log_mgr.error(f"Fehler eim Auflisten der Profile: {e}")
                        return []

        def write(self, key, value):
                """
                Schreibt Attribut (Key-Value-Paar) ind das akutell geladene Profil.
                """
                if not self.current_profile_name:
                        self.log_mgr.error("write fehlgeschlagen: Kein current_profile_name.")
                        return False
                if not self.working_dir:
                        self.log_mgr.error("write fehlgeschlagen: Kein working_dir.")
                        return False

                # Daten im RAM aktualisieren
                self.current_profile_data[key] = value

                # Daten in Datei sichern
                success = self.__write_to_file(self.current_profile_name, self.current_profile_data)
                if success:
                        self.log_mgr.debug(" Attribut '{key}' wurde erfolgreich aktualisiert.")
                return success

        def read(self, key):
                """
                Liest einen Wert anhand des 'key' aus dem akutellen Profil
                """
                if not self.current_profile_name:
                        self.log_mgr.error("read fehlgeschlagen: Kein current_profile_name.")
                        return None
                return self.current_profile_data.get(key, None)


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
    pm.write("Sting1", "CAFEBABE")
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
