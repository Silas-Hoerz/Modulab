# modules/device/DeviceManager.py
# This Python file uses the following encoding: utf-8
# Atrributes of Device:
# - name: str
# - tags: custom strings tags for potential filtering 
# - geometry:   rectangle
#               circle
# - dimensions: length [m] if geometry = rectangle
#               width [m] if geometry = rectangle
#               radius [m] if geometry = circle
#               area [m^2]

import math 
from PySide6.QtCore import QObject, Signal

class Device:
    """
    Repräsentiert ein einzelnes physisches Device (z.B. Pixel, Teststruktur).

    Dies ist eine Daten-Container-Klasse, die alle geometrischen und
    metadatenbezogenen Eigenschaften eines Devices speichert.
    """

    def __init__(self, name: str, geometry: str, tags: list = None, **dimensions):
        """
        Initialisiert ein neues Device-Objekt.

        Args:
            name (str): Der eindeutige Name des Devices (z.B. "Pixel_R1C1").
            geometry (str): Der Geometrie-Typ. Muss 'rectangle' oder 'circle' sein.
            tags (list, optional): Eine Liste von String-Tags zur Filterung.
            **dimensions (float): Dynamische Schlüsselwortargumente für die Maße 
                                  des Devices in Metern [m].
                                  
                                  - Für 'rectangle': `length`, `width`
                                  - Für 'circle': `radius`
                                  - Optionale Cutouts: `cutout_length`, `cutout_width`,
                                    `cutout_radius`.

        Examples:
            Ein rechteckiges Device (1mm x 0.5mm) erstellen:
            
            .. code-block:: python
            
                dev1 = Device(
                    name="Pixel_1", 
                    geometry="rectangle", 
                    tags=["OLED", "Red"], 
                    length=1e-3, 
                    width=0.5e-3
                )

            Ein kreisförmiges Device (Radius 80µm) mit einem kreisförmigen 
            Ausschnitt (Radius 10µm) erstellen:
            
            .. code-block:: python
            
                dev2 = Device(
                    name="Ring_Struktur", 
                    geometry="circle", 
                    radius=80e-6, 
                    cutout_radius=10e-6
                )
        """
        self.name: str = name
        self.geometry: str = geometry # 'rectangle' or 'circle'
        self.tags: list = tags if tags is not None else []
        self.dimensions: dict = dimensions

    def get_area(self) -> float:
        """
        Berechnet die aktive Fläche [m²] des Devices.

        Die Fläche wird als `Hauptfläche - Ausschnittfläche` berechnet,
        basierend auf der Geometrie und den `dimensions`.

        Hinweis:
            - Wenn die Maße ungültig (nicht numerisch) sind, wird 0.0 zurückgegeben.
            - Wenn die Ausschnittfläche größer als die Hauptfläche ist, 
              wird 0.0 zurückgegeben.

        Returns:
            float: Die berechnete aktive Fläche in Quadratmetern [m²].
        """

        main_area = 0.0
        cutout_area = 0.0

        try:
            if self.geometry == 'rectangle':
                length = self.dimensions.get('length',0)
                width = self.dimensions.get('width', 0)
                main_area = float(length) * float(width)

                cutout_length = self.dimensions.get('cutout_length',0)
                cutout_width = self.dimensions.get('cutout_width', 0)
                cutout_area = float(cutout_length) * float(cutout_width)

            elif self.geometry == 'circle':
                radius = self.dimensions.get('radius', 0)
                main_area = math.pi * (float(radius)**2)

                cutout_radius = self.dimensions.get('cutout_radius', 0)
                cutout_area = math.pi * (float(cutout_radius)**2)
            else:
                print(f"get_area error: unknown geometry type '{self.geometry}' for device '{self.name}'.")
                return 0.0

            # Sicherstellen, dass Cutout-Maße nicht negativ waren
            if cutout_area < 0:
                 print(f"get_area warning: negative cutout dimensions detected for device '{self.name}'. Cutout area set to 0.")
                 cutout_area = 0.0

            # Constraint: Cutout darf nicht größer als Device sein
            if cutout_area > main_area:
                print(f"get_area error: cutout area ({cutout_area}) is larger than main area ({main_area}) for device '{self.name}'. Returning 0.0")
                return 0.0  
            
            return main_area - cutout_area
        
        except (ValueError, TypeError):
            # Fehler bei Umwandlung (z.B. length="abc")
            print(f"get_area error: invalid (non-numeric) dimension values for device '{self.name}'.")
            return 0.0
        
    def to_dict(self) -> dict:
        """
        Konvertiert das Device-Objekt in ein serialisierbares Diktat.

        Wird verwendet, um das Device im ProfileManager zu speichern.

        Returns:
            dict: Eine Diktat-Repräsentation des Devices.
        """
        return {
            'name': self.name,
            'geometry': self.geometry,
            'tags': self.tags,
            'dimensions': self.dimensions
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Erstellt eine Device-Instanz aus einem Diktat.

        Wird verwendet, um das Device aus dem ProfileManager zu laden.

        Args:
            data (dict): Das Diktat, das `to_dict()` erzeugt hat.

        Returns:
            Device: Eine neue Instanz der Device-Klasse.
        """
        if not data:
            return None
        return cls(
            name=data.get('name', 'Unnamed Device'),
            geometry=data.get('geometry', 'rectangle'),
            tags=data.get('tags', []),
            **data.get('dimensions', {})
        )

    def __repr__(self):
        """Stellt eine formale String-Repräsentation des Objekts bereit."""
        return f"Device(name={self.name}, geometry={self.geometry}, tags={self.tags}, dimensions={self.dimensions})"


class DeviceManager (QObject):
    """
    Erstellt, bearbeitet, löscht und verwaltet `Device`-Objekte.

    Diese Klasse dient als zentraler Service für die Verwaltung einer 
    Liste von Devices. Sie ist verantwortlich für:
    - Das Erstellen, Bearbeiten und Löschen von `Device`-Objekten.
    - Das Speichern und Laden der Device-Liste im/aus dem `ProfileManager`.
    - Die Verwaltung, welches Device das "aktive" ist.

    Args:
        log_manager (LogManager): Eine Instanz des LogManagers.
        profile_manager (ProfileManager): Eine Instanz des ProfileManagers.
        parent (QObject, optional): Ein übergeordnetes QObject für das Speichermanagement.

    Signale:
        device_loaded (str):
            Wird ausgelöst, wenn ein Device mit `set_active_device`
            als aktiv ausgewählt wurde.
            Args: (str: Der Name des geladenen Devices).
    """
    KEY_DEVICE_LIST = "devices" 
    """str: Der Profil-Schlüssel zum Speichern der Liste aller Device-Diktate."""
    KEY_ACTIVE_DEVICE = "active_device_name"
    """str: Der Profil-Schlüssel zum Speichern des Namens des aktiven Devices."""

    device_loaded = Signal(str)  # Signal, wenn ein Device geladen wurde

    def __init__(self, log_manager = None, profile_manager = None, parent=None):
        """
        Initialisiert den DeviceManager.

        Args:
            log_manager (LogManager, optional): Die LogManager-Instanz.
            profile_manager (ProfileManager, optional): Die ProfileManager-Instanz.
            parent (QObject, optional): Ein übergeordnetes QObject.
        """
        # Initialize QObject base to ensure signals/ownership are managed by Qt
        super().__init__(parent)

        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.devices: list[Device] = []
        self.active_device_name: str = None

 
    
    def __save_to_profile(self):
        """
        Interne Hilfsmethode: Speichert die aktuelle Device-Liste und 
        das aktive Device im geladenen Profil.
        """
        if not self.profile_mgr or not self.profile_mgr.current_profile_name:
            self.log_mgr.warning("__save_to_profile error: no current profile loaded.")
            return False
        
        device_data_list = [dev.to_dict() for dev in self.devices]

        self.profile_mgr.write(self.KEY_DEVICE_LIST, device_data_list)
        self.profile_mgr.write(self.KEY_ACTIVE_DEVICE, self.active_device_name)
        self.log_mgr.debug("DeviceManager: Device data saved to profile.")

    def load_from_profile(self):
        """
        Lädt die Device-Liste und das aktive Device aus dem geladenen Profil.

        Diese Funktion wird typischerweise aufgerufen, nachdem der 
        ProfileManager das `profile_loaded`-Signal gesendet hat.
        """
        if not self.profile_mgr or not self.profile_mgr.current_profile_name:
            self.log_mgr.warning("load_from_profile error: no current profile loaded.")
            self.devices = []
            self.active_device_name = None
            return
        
        self.log_mgr.debug(f"DeviceManager: Loading device data from profile '{self.profile_mgr.current_profile_name}'...")
        device_data_list = self.profile_mgr.read(self.KEY_DEVICE_LIST)
        self.devices = []
        if device_data_list:
            try:
                for dev_data in device_data_list:
                    device_obj = Device.from_dict(dev_data)
                    if device_obj:
                        self.devices.append(device_obj)
            except Exception as e:
                self.log_mgr.error(f"load_from_profile error: failed to load devices: {e}")
                self.devices = []
        
        self.active_device_name = self.profile_mgr.read(self.KEY_ACTIVE_DEVICE)
        
        # Sicherstellen, dass das geladene "aktive" Device auch existiert
        if self.active_device_name and not self.get_device_by_name(self.active_device_name):
            self.log_mgr.warning(f"load_from_profile warning: active device '{self.active_device_name}' not found in device list.")
            self.active_device_name = None
            self.__save_to_profile() # Bereinige ungültigen Eintrag

        self.log_mgr.debug(f"DeviceManager: Loaded {len(self.devices)} devices from profile.")
    
    def create_device(self, name: str, geometry: str, tags: list = None, **dimensions) -> bool:
        """
        Erstellt ein neues Device, fügt es zur Liste hinzu und speichert es im Profil.

        Args:
            name (str): Der eindeutige Name des Devices (z.B. "Pixel_R1C1").
            geometry (str): Der Geometrie-Typ ('rectangle' oder 'circle').
            tags (list, optional): Eine Liste von String-Tags.
            **dimensions (float): Dynamische Schlüsselwortargumente für die Maße 
                                  des Devices in Metern [m] (z.B. `length=1e-3`).

        Returns:
            bool: True bei Erfolg, False, wenn der Name bereits existiert.

        Examples:
            Ein rechteckiges Device (1mm x 0.5mm) erstellen:
            
            .. code-block:: python
            
                # Annahme: 'device_mgr' ist eine Instanz von DeviceManager
                device_mgr.create_device(
                    "OLED_Pixel_1", 
                    "rectangle", 
                    length=1e-3, 
                    width=0.5e-3
                )
                                         
            Ein kreisförmiges Device (Radius 80µm) mit Tags erstellen:
            
            .. code-block:: python
            
                device_mgr.create_device(
                    "Pin80", 
                    "circle", 
                    tags=["Test_Struktur", "Rund"], 
                    radius=80e-6
                )
        """
        if not name:
            self.log_mgr.error("Name is required.")
            return False
        if self.get_device_by_name(name):
            self.log_mgr.error(f"Device with name '{name}' already exists.")
            return False
        try:
            new_device = Device(name, geometry, tags, **dimensions)
            self.devices.append(new_device)

            if len(self.devices) == 1: # Erstes erstelltes Device = aktiv
                self.active_device_name = name

            self.__save_to_profile()
            self.log_mgr.info(f"Device '{name}' created successfully.")
            return True
        except Exception as e:
            self.log_mgr.error(f"create_device error: {e}")
            return False
        
    def delete_device(self, name: str) -> bool:
        """
        Löscht ein Device anhand seines Namens aus der Liste.

        Args:
            name (str): Der Name des zu löschenden Devices.

        Returns:
            bool: True bei Erfolg, False, wenn das Device nicht gefunden wurde.
        """
        device = self.get_device_by_name(name)
        if not device:
            self.log_mgr.error(f"delete_device error: Device '{name}' not found.")
            return False
        
        self.devices.remove(device)
        
        # Fallback für aktives Device, falls das gelöschte aktiv war
        if self.active_device_name == name:
            self.active_device_name = self.devices[0].name if self.devices else None
            
        self.__save_to_profile()
        self.log_mgr.info(f"Device '{name}' deleted successfully.")
        return True

    def edit_device(self, name: str, new_geometry: str = None, new_tags: list = None, new_dimensions: dict = None) -> bool:
        """
        Bearbeitet ein existierendes Device.

        Der Name kann nicht geändert werden. Nur die übergebenen (nicht-None)
        Parameter werden aktualisiert.

        Args:
            name (str): Der Name des zu bearbeitenden Devices.
            new_geometry (str, optional): Die neue Geometrie ('rectangle'/'circle').
            new_tags (list, optional): Die *komplett neue* Liste von Tags.
            new_dimensions (dict, optional): Das *komplett neue* Diktat 
                                             für Dimensionen.

        Returns:
            bool: True bei Erfolg, False, wenn das Device nicht gefunden wurde.

        Examples:
            Die Dimensionen eines Devices ändern:
            
            .. code-block:: python
            
                neue_maße = {'length': 1.1e-3, 'width': 0.6e-3}
                device_mgr.edit_device("OLED_Pixel_1", new_dimensions=neue_maße)
                
            Nur die Tags eines Devices ändern:
            
            .. code-block:: python
            
                device_mgr.edit_device("Pin80", new_tags=["Test_Struktur", "Wichtig"])
        """
        device_to_edit = self.get_device_by_name(name)
        if not device_to_edit:
            self.log_mgr.warning(f"DeviceManager: Kann '{name}' nicht bearbeiten (nicht gefunden).")
            return False

        # Nur die Werte aktualisieren, die übergeben wurden
        if new_geometry is not None:
            device_to_edit.geometry = new_geometry
        if new_tags is not None:
            device_to_edit.tags = new_tags
        if new_dimensions is not None:
            # Ersetzt alle Dimensionen
            device_to_edit.dimensions = new_dimensions
            
        self.__save_to_profile()
        self.log_mgr.info(f"DeviceManager: Device '{name}' bearbeitet.")
        return True

    def get_device_by_name(self, name: str) -> Device | None:
        """
        Sucht und retourniert das Device-Objekt anhand des Namens.

        Args:
            name (str): Der Name des gesuchten Devices.

        Returns:
            Device | None: Das `Device`-Objekt oder `None`, wenn nicht gefunden.
        """
        for dev in self.devices:
            if dev.name == name:
                return dev
        return None

    def list_device_names(self) -> list[str]:
        """
        Gibt eine Liste aller Device-Namen zurück.

        Nützlich für die Anzeige in einer Combobox oder Liste in der GUI.

        Returns:
            list[str]: Eine Liste der Namen aller geladenen Devices.
        
        Examples:
            Eine QComboBox mit allen Device-Namen füllen:
            
            .. code-block:: python
            
                namen = device_mgr.list_device_names()
                ui.device_combobox.clear()
                ui.device_combobox.addItems(namen)
        """
        self.load_from_profile() # Stellt sicher, dass die Liste aktuell ist
        return [dev.name for dev in self.devices]

    # --- Active-Device-Funktionen ---

    def set_active_device(self, name: str) -> bool:
        """
        Setzt das aktive Device für die Anwendung.

        Löst das `device_loaded`-Signal aus.

        Args:
            name (str): Der Name des Devices, das aktiv werden soll.

        Returns:
            bool: True bei Erfolg, False, wenn das Device nicht gefunden wurde.
        """
        if not self.get_device_by_name(name):
            self.log_mgr.warning(f"DeviceManager: Kann '{name}' nicht aktivieren (nicht gefunden).")
            return False
            
        self.active_device_name = name
        self.__save_to_profile()
        self.device_loaded.emit(name)
        self.log_mgr.info(f"Device '{name}' loaded successfully.")
        return True

    def get_active_device(self) -> Device | None:
        """
        Gibt das *gesamte Objekt* des aktiven Devices zurück.

        Die UI kann dann `device.get_area()` oder `device.dimensions` 
        selbst aufrufen.

        Returns:
            Device | None: Das aktuell aktive `Device`-Objekt oder `None`.
        
        Examples:
            Informationen des aktiven Devices abrufen:
            
            .. code-block:: python
            
                aktives_gerät = device_mgr.get_active_device()
                if aktives_gerät:
                    print(f"Aktuell: {aktives_gerät.name}")
                    print(f"Fläche: {aktives_gerät.get_area()} m²")
                else:
                    print("Kein Device aktiv.")
        """
        if not self.active_device_name:
            # Lade Fallback, falls noch nicht geladen
            self.load_from_profile()
            if not self.active_device_name:
                return None
        return self.get_device_by_name(self.active_device_name)

    # --- "Getter"-Funktionen (Shortcuts für die View) ---

    def get_active_device_area(self) -> float | None:
        """
        Bequemlichkeitsfunktion: Gibt die Fläche [m²] des aktiven Devices zurück.

        Returns:
            float | None: Die Fläche in m² oder `None`, wenn kein Device aktiv ist.
        """
        active_dev = self.get_active_device()
        if active_dev:
            return active_dev.get_area()
        return None

    def get_active_device_dimensions(self) -> dict:
        """
        Bequemlichkeitsfunktion: Gibt die Maße des aktiven Devices zurück.

        Returns:
            dict: Das Dimensions-Wörterbuch (z.B. `{'length': 0.1, ...}`) 
                  oder ein leeres dict.
        """
        active_dev = self.get_active_device()
        if active_dev:
            return active_dev.dimensions
        return {} # Leeres dict statt None ist oft einfacher zu handhaben