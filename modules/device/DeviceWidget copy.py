# modules/device/DeviceWidget.py
# This Python file uses the following encoding: utf-8

import math

try:
    from .ui_DeviceWidget import Ui_Dialog
except ImportError:
    print("Fehler: Konnte 'ui_DeviceWidget.py' nicht finden.")
    from PySide6.QtWidgets import QWidget
    class Ui_Dialog:
        def setupUi(self, Form):
            Form.setObjectName("Device")

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Slot, QLocale
from PySide6.QtGui import QDoubleValidator


from modules.log.LogManager import LogManager
from modules.device.DeviceManager import DeviceManager, Device


class DeviceWidget(QWidget, Ui_Dialog):
    """
    Steuerklasse (View/Controller) für das Device-Management.
    Verbindet die UI (ui_DeviceWidget) mit der Logik (DeviceManager).
    """

    # 1 Meter = 1_000_000_000 Nanometer
    M_TO_NM = 1_000_000_000.0

    def __init__(self,context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.dev_mgr = context.device_manager
        self.log_mgr = context.log_manager

        # Locale für Komma-Eingabe ("123,45")
        self.locale = QLocale(QLocale.German, QLocale.Germany)
        self._block_signals = False  # Zur Vermeidung von Signal-Schleifen

        self.__setup_ui()
        self.__connect_signals()

    def __setup_ui(self):
        """Initialisiert die UI-Elemente (Validatoren, ComboBox-Einträge)."""
        
        # Validatoren für Fließkommazahlen (mit Komma)
        # Erlaube Zahlen von 0 bis 1 Milliarde (nm) mit 6 Nachkommastellen
        validator = QDoubleValidator(0.0, 1e9, 6, self)
        validator.setLocale(self.locale)
        validator.setNotation(QDoubleValidator.StandardNotation)

        self.lineEdit_length.setValidator(validator)
        self.lineEdit_width.setValidator(validator)
        self.lineEdit_radius.setValidator(validator)

        # Geometrie-Auswahl füllen
        self.comboBox_geometry.addItems(["rectangle", "circle"])

        # Editor initial deaktivieren, bis ein Device gewählt wird
        self.groupBox_editor.setEnabled(False)
        self.label_area.setText("Fläche: -")

    def __connect_signals(self):
        """Verbindet alle UI-Signale mit den Slots."""
        # --- Auswahl & Verwaltung ---
        self.comboBox_activeDevice.currentIndexChanged.connect(self.on_active_device_changed)
        self.pushButton_newDevice.clicked.connect(self.on_new_device)
        self.pushButton_deleteDevice.clicked.connect(self.on_delete_device)

        # --- Editor ---
        self.pushButton_saveDevice.clicked.connect(self.on_save_device)
        self.comboBox_geometry.currentIndexChanged.connect(self.on_geometry_changed)
        
        # Live-Aktualisierung der Fläche
        live_update_inputs = [
            self.lineEdit_length,
            self.lineEdit_width,
            self.lineEdit_radius,
            self.comboBox_geometry
        ]
        for widget in live_update_inputs:
            # textChanged für QLineEdit, currentIndexChanged für QComboBox
            if hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self.update_area_display)
            else:
                widget.currentIndexChanged.connect(self.update_area_display)

    # --- DATEN-KONVERTIERUNG (nm <-> m) ---

    def __nm_str_to_m(self, nm_str: str) -> float:
        """Liest einen 'nm'-String (z.B. "123,45") und wandelt ihn in Meter um."""
        if not nm_str:
            return 0.0
        
        value, ok = self.locale.toDouble(nm_str)
        if not ok:
            return 0.0
        
        return value / self.M_TO_NM

    def __m_to_nm_str(self, m_float: float | None) -> str:
        """Wandelt einen Meter-Wert in einen 'nm'-String um (z.B. "123,45")."""
        if m_float is None:
            m_float = 0.0
            
        nm_value = m_float * self.M_TO_NM
        # 'f' für Standard-Notation, 3 Nachkommastellen
        return self.locale.toString(nm_value, 'f', 3)

    # --- ÖFFENTLICHE FUNKTION (Vom MainWindow aufgerufen) ---

    def load_devices_from_profile(self):
        """
        Aktualisiert die ComboBox mit den Devices aus dem Manager.
        MUSS aufgerufen werden, nachdem der DeviceManager sein Profil geladen hat.
        """
        self._block_signals = True  # Verhindert, dass on_active_device_changed feuert
        
        self.comboBox_activeDevice.clear()
        
        device_names = self.dev_mgr.list_device_names()
        if device_names:
            self.comboBox_activeDevice.addItems(device_names)
            
            # Aktives Device aus dem Manager setzen
            active_name = self.dev_mgr.active_device_name
            if active_name:
                self.comboBox_activeDevice.setCurrentText(active_name)
        
        self._block_signals = False
        
        # Manuelles Auslösen, um den Editor zu füllen
        if device_names:
            self.on_active_device_changed()
        else:
            self.__clear_editor() # Wenn keine Devices da sind, Editor leeren

    # --- SLOTS (Reaktionen auf UI-Aktionen) ---

    @Slot()
    def on_active_device_changed(self):
        """Wird aufgerufen, wenn ein anderes Device in der ComboBox gewählt wird."""
        if self._block_signals:
            return

        name = self.comboBox_activeDevice.currentText()
        if not name:
            self.__clear_editor()
            return

        # 1. Dem Manager sagen, welches Device jetzt aktiv ist
        self.dev_mgr.set_active_device(name)

        # 2. Editor mit den Daten des aktiven Devices füllen
        device = self.dev_mgr.get_active_device()
        if device:
            self.__populate_editor(device)
            self.groupBox_editor.setEnabled(True)
        else:
            # Sollte nicht passieren, wenn set_active_device erfolgreich war
            self.__clear_editor()

    @Slot()
    def on_geometry_changed(self):
        """Wechselt das QStackedWidget basierend auf der Geometrie."""
        geo = self.comboBox_geometry.currentText()
        if geo == 'rectangle':
            self.stackedWidget_dims.setCurrentIndex(1)
        elif geo == 'circle':
            self.stackedWidget_dims.setCurrentIndex(0)

    @Slot()
    def on_new_device(self):
        """Erstellt ein neues Standard-Device."""
        # Finde einen einzigartigen Namen
        new_name = "Neues Device"
        i = 1
        while self.dev_mgr.get_device_by_name(new_name):
            new_name = f"Neues Device {i}"
            i += 1
        
        # Erstelle das Device im Manager (mit 0-Dimensionen in Metern)
        success = self.dev_mgr.create_device(
            name=new_name,
            geometry="rectangle",
            tags=[],
            length=0.0,
            width=0.0
        )
        
        if success:
            self.log_mgr.info(f"Device '{new_name}' erstellt.")
            # UI neu laden
            self.load_devices_from_profile()
            # Neues Device auswählen
            self.comboBox_activeDevice.setCurrentText(new_name)
        else:
            self.log_mgr.error("Device konnte nicht erstellt werden.")

    @Slot()
    def on_delete_device(self):
        """Löscht das aktuell ausgewählte Device."""
        name = self.comboBox_activeDevice.currentText()
        if not name:
            return

        # Sicherheitsabfrage
        reply = QMessageBox.question(self, "Device löschen",
                                     f"Möchten Sie das Device '{name}' wirklich löschen?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success = self.dev_mgr.delete_device(name)
            if success:
                self.log_mgr.info(f"Device '{name}' gelöscht.")
                self.load_devices_from_profile() # UI neu laden
            else:
                self.log_mgr.error(f"Device '{name}' konnte nicht gelöscht werden.")

    @Slot()
    def on_save_device(self):
        """Speichert die Änderungen aus dem Editor im DeviceManager."""
        original_name = self.dev_mgr.active_device_name
        if not original_name:
            self.log_mgr.warning("Kein aktives Device zum Speichern ausgewählt.")
            return

        # --- 1. Daten aus der UI auslesen ---
        new_name = self.lineEdit_name.text().strip()
        new_geo = self.comboBox_geometry.currentText()
        new_tags_str = self.lineEdit_tags.text()
        # Erzeugt eine saubere Liste: ["Tag1", "Tag2"]
        new_tags = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]

        new_dims = {}
        if new_geo == 'rectangle':
            new_dims['length'] = self.__nm_str_to_m(self.lineEdit_length.text())
            new_dims['width'] = self.__nm_str_to_m(self.lineEdit_width.text())
        elif new_geo == 'circle':
            new_dims['radius'] = self.__nm_str_to_m(self.lineEdit_radius.text())

        if not new_name:
            self.log_mgr.error("Device-Name darf nicht leer sein.")
            return

        # --- 2. Logik: Name geändert? ---
        if original_name != new_name:
            # Prüfen, ob der neue Name bereits existiert
            if self.dev_mgr.get_device_by_name(new_name):
                self.log_mgr.error(f"Ein Device mit dem Namen '{new_name}' existiert bereits.")
                self.lineEdit_name.setText(original_name) # Namen zurücksetzen
                return
            
            # Da der Name die ID ist, müssen wir es "neu erstellen" und das alte löschen
            self.log_mgr.debug(f"Device wird umbenannt: '{original_name}' -> '{new_name}'")
            self.dev_mgr.create_device(new_name, new_geo, new_tags, **new_dims)
            self.dev_mgr.delete_device(original_name)
            self.dev_mgr.set_active_device(new_name) # Das neue als aktiv setzen
            
            # UI komplett neu laden, um ComboBox zu aktualisieren
            self.load_devices_from_profile()
            self.comboBox_activeDevice.setCurrentText(new_name)

        else:
            # Nur die Attribute des bestehenden Devices bearbeiten
            self.dev_mgr.edit_device(original_name, new_geo, new_tags, new_dims)

        self.log_mgr.info(f"Device '{new_name}' gespeichert.")
        self.update_area_display() # Fläche aktualisieren

    @Slot()
    def update_area_display(self):
        """Berechnet die Fläche LIVE aus den UI-Feldern."""
        if self._block_signals:
            return

        area_m2 = 0.0
        geo = self.comboBox_geometry.currentText()

        try:
            if geo == 'rectangle':
                l = self.__nm_str_to_m(self.lineEdit_length.text())
                w = self.__nm_str_to_m(self.lineEdit_width.text())
                area_m2 = l * w
            elif geo == 'circle':
                r = self.__nm_str_to_m(self.lineEdit_radius.text())
                area_m2 = math.pi * (r ** 2)
        except Exception:
            area_m2 = 0.0 # Bei ungültiger Eingabe

        # Sinnvolle Einheit wählen, z.B. Quadratmikrometer (µm²)
        # 1 m² = (1_000_000 µm)² = 1e12 µm²
        area_um2 = area_m2 * 1e12 
        
        self.label_area.setText(f"Fläche: {self.locale.toString(area_um2, 'f', 3)} µm²")


    # --- PRIVATE HELPER (UI-Steuerung) ---

    def __populate_editor(self, device: Device):
        """Füllt die Editor-Felder mit den Daten eines Device-Objekts."""
        self._block_signals = True # Verhindert, dass Signale beim Befüllen feuern
        
        self.lineEdit_name.setText(device.name)
        self.comboBox_geometry.setCurrentText(device.geometry)
        self.lineEdit_tags.setText(", ".join(device.tags))

        # Dimensionen (in nm umrechnen)
        length_m = device.dimensions.get('length')
        width_m = device.dimensions.get('width')
        radius_m = device.dimensions.get('radius')
        
        self.lineEdit_length.setText(self.__m_to_nm_str(length_m))
        self.lineEdit_width.setText(self.__m_to_nm_str(width_m))
        self.lineEdit_radius.setText(self.__m_to_nm_str(radius_m))
        
        self._block_signals = False
        
        # Manuell das StackedWidget und die Fläche aktualisieren
        self.on_geometry_changed() 
        self.update_area_display()

    def __clear_editor(self):
        """Leert alle Editor-Felder und deaktiviert sie."""
        self._block_signals = True
        
        self.lineEdit_name.clear()
        self.lineEdit_tags.clear()
        self.lineEdit_length.clear()
        self.lineEdit_width.clear()
        self.lineEdit_radius.clear()
        self.label_area.setText("Fläche: -")
        
        self.groupBox_editor.setEnabled(False) # Editor sperren
        
        self._block_signals = False