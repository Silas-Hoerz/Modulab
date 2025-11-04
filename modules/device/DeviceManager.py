# modules/device/DeviceManager.py
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
    Repräsentiert ein Device mit verschiedenen Attributen.
    """

    def __init__(self, name: str, geometry: str, tags: list = None, **diemensions):
        self.name: str = name
        self.geometry: str = geometry # 'rectangle' or 'circle'
        self.tags: list = tags if tags is not None else []
        self.dimensions: dict = diemensions

    def get_area(self) -> float:
        """
        Berechnet die Fläche [m²] des Devices
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
        Konvertiert das Device Objekt in ein Dictionary für JSON
        (Muss nicht geändert werden, 'dimensions' enthält bereits alles)
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
        Erstellt ein Device Objekt aus einem Dictionary
        (Muss nicht geändert werden, 'dimensions' wird korrekt übergeben)
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
        return f"Device(name={self.name}, geometry={self.geometry}, tags={self.tags}, dimensions={self.dimensions})"


class DeviceManager (QObject):
    """
    Erstellt, bearbeitet, löscht und verwaltet Device Objekte.
    """
    KEY_DEVICE_LIST = "devices" 
    KEY_ACTIVE_DEVICE = "active_device_name"

    device_loaded = Signal(str)  # Signal, wenn ein Device geladen wurde

    def __init__(self, log_manager = None, profile_manager = None, parent=None):
        # Initialize QObject base to ensure signals/ownership are managed by Qt
        super().__init__(parent)

        self.log_mgr = log_manager
        self.profile_mgr = profile_manager

        self.devices: list[Device] = []
        self.active_device_name: str = None

 
    
    def __save_to_profile(self):
        """
        Specihert die aktuelle Device Liste und das aktive Device im geladenem Profil
        """
        if not self.profile_mgr.current_profile_name:
            self.log_mgr.warning("__save_to_profile error: no current profile loaded.")
            return False
        
        device_data_list = [dev.to_dict() for dev in self.devices]

        self.profile_mgr.write(self.KEY_DEVICE_LIST, device_data_list)
        self.profile_mgr.write(self.KEY_ACTIVE_DEVICE, self.active_device_name)
        self.log_mgr.debug("DeviceManager: Device data saved to profile.")

    def load_from_profile(self):
        """
        Lädt die Device Liste und das aktive Device aus dem geladenem Profil
        """
        if not self.profile_mgr.current_profile_name:
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
        if self.active_device_name and not self.get_device_by_name(self.active_device_name):
            self.log_mgr.warning(f"load_from_profile warning: active device '{self.active_device_name}' not found in device list.")
            self.active_device_name = None
            self.__save_to_profile()

        self.log_mgr.debug(f"DeviceManager: Loaded {len(self.devices)} devices from profile.")
    
    def create_device(self, name: str, geometry: str, tags: list = None, **dimensions) -> bool:
        """
        Erstellt ein neues Device z.B create_device("Pin80", "circle", radius = 80E-6)
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

            if len(self.devices) == 1:
                self.active_device_name = name

            self.__save_to_profile()
            self.log_mgr.info(f"Device '{name}' created successfully.")
            return True
        except Exception as e:
            self.log_mgr.error(f"create_device error: {e}")
            return False
        
    def delete_device(self, name: str) -> bool:
        """
        Löscht ein Device anhand des Namens
        """
        device = self.get_device_by_name(name)
        if not device:
            self.log_mgr.error(f"delete_device error: Device '{name}' not found.")
            return False
        self.devices.remove(device)
        if self.active_device_name == name:
            self.active_device_name = self.devices[0].name if self.devices else None
        self.__save_to_profile()
        self.log_mgr.info(f"Device '{name}' deleted successfully.")
        return True

    def edit_device(self, name: str, new_geometry: str = None, new_tags: list = None, new_dimensions: dict = None) -> bool:
        """
        Bearbeitet ein existierendes Device.
        Der Name kann nicht geändert werden.
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
        """
        for dev in self.devices:
            if dev.name == name:
                return dev
        return None

    def list_device_names(self) -> list[str]:
        """
        Gibt eine Liste aller Device-Namen zurück.
        """
        self.load_from_profile()
        return [dev.name for dev in self.devices]

    # --- Active-Device-Funktionen ---

    def set_active_device(self, name: str) -> bool:
        """
        Setzt das aktive Device.
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
        Die View kann dann device.get_area() etc. selbst aufrufen.
        """
        if not self.active_device_name:
            return None
        return self.get_device_by_name(self.active_device_name)

    # --- "Getter"-Funktionen (Shortcuts für die View) ---

    def get_active_device_area(self) -> float | None:
        """
        Bequemlichkeitsfunktion: Gibt die Fläche des aktiven Devices zurück.
        """
        active_dev = self.get_active_device()
        if active_dev:
            return active_dev.get_area()
        return None

    def get_active_device_dimensions(self) -> dict:
        """
        Bequemlichkeitsfunktion: Gibt die Maße des aktiven Devices zurück.
        """
        active_dev = self.get_active_device()
        if active_dev:
            return active_dev.dimensions
        return {} # Leeres dict statt None ist oft einfacher zu handhaben