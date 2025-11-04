# modules/device/DeviceWidget.py
# This Python file uses the following encoding: utf-8

import math

try:
    from .ui_DeviceWidget import Ui_Form
except ImportError:
    print("Fehler: Konnte 'ui_DeviceWidget.py' nicht finden.")
    from PySide6.QtWidgets import QWidget
    class Ui_Form:
        def setupUi(self, Form):
            Form.setObjectName("Device")


from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QCloseEvent, QShowEvent, QDoubleValidator, QPalette, QColor

# --- Device Selection Dialog ---

class DeviceWidget(QDialog, Ui_Form):

    def __init__(self,context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.dev_mgr = context.device_manager
        self.log_mgr = context.log_manager
        self.progile_mgr = context.profile_manager

        self.__connect_signals()

    def __refresh(self):
        # evtl das zuletzt geladene Device  bzw neue oder editierte Device direkt auswählen
        self.device_list = self.dev_mgr.list_device_names()
        self.listWidget_devices.clear()
        self.listWidget_devices.addItems(self.device_list)

    def __connect_signals(self):
        self.pushButton_new.clicked.connect(self.on_new_clicked)
        self.pushButton_edit.clicked.connect(self.on_edit_clicked)
        self.pushButton_delete.clicked.connect(self.on_delete_clicked)
        self.pushButton_done.clicked.connect(self.on_done_clicked)

    @Slot()
    def on_new_clicked(self):
        new_data = DeviceWidgetEdit.get_device(self.dev_mgr, parent=self)
        if new_data:
            try:
                # Das zurückgegebene Dictionary wird direkt verwendet
                self.dev_mgr.create_device(**new_data)
                self.log_mgr.info(f"Device '{new_data['name']}' erfolgreich erstellt.")
                self.__refresh()
                # Optional: Das neue Element direkt auswählen
                items = self.listWidget_devices.findItems(new_data['name'], Qt.MatchExactly)
                if items:
                    self.listWidget_devices.setCurrentItem(items[0])
            except Exception as e:
                self.log_mgr.error(f"Fehler beim Erstellen des Devices: {e}")
                QMessageBox.critical(self, "Fehler", f"Konnte Device nicht erstellen: {e}")
       
        


    @Slot()
    def on_edit_clicked(self):
        selected_items = self.listWidget_devices.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wählen Sie ein Device zum Bearbeiten aus.")
            return
        
        device_name = selected_items[0].text()

        try:

            device_obj = self.dev_mgr.get_device_by_name(device_name) 
            if not device_obj:
                 QMessageBox.critical(self, "Fehler", f"Konnte Daten für '{device_name}' nicht laden.")
                 return
           
            existing_data = device_obj.to_dict()
        except Exception as e:
            self.log_mgr.error(f"Konnte Daten für Edit nicht laden: {e}. Sie müssen 'get_device_data' implementieren.")
            QMessageBox.critical(self, "Fehler", f"Konnte Daten für '{device_name}' nicht laden: {e}")
            return


        # Ruft denselben Dialog auf, übergibt aber die existing_data
        updated_data = DeviceWidgetEdit.get_device(self.dev_mgr, device_data=existing_data, parent=self)
        
        if updated_data:
            try:
              
                self.dev_mgr.delete_device(device_name)
                self.dev_mgr.create_device(**updated_data)
                
                self.log_mgr.info(f"Device '{updated_data['name']}' aktualisiert.")
                self.__refresh()
               
                items = self.listWidget_devices.findItems(updated_data['name'], Qt.MatchExactly)
                if items:
                    self.listWidget_devices.setCurrentItem(items[0])
            except Exception as e:
                self.log_mgr.error(f"Fehler beim Aktualisieren des Devices: {e}")
                QMessageBox.critical(self, "Fehler", f"Konnte Device nicht aktualisieren: {e}")
               

    # --- Delete Device ---        
    @Slot()
    def on_delete_clicked(self):
        selected_items = self.listWidget_devices.selectedItems()
        if not selected_items:
            #QMessageBox.warning(self, "No Selection", "Please select a device to continue.")
            return
        device_name = selected_items[0].text()
        reply = QMessageBox.question(self, "Löschen bestätigen", 
                                     f"Möchten Sie das Device '{device_name}' wirklich löschen?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.dev_mgr.delete_device(device_name)
                self.log_mgr.info(f"Device '{device_name}' gelöscht.")
                self.__refresh()
            except Exception as e:
                self.log_mgr.error(f"Fehler beim Löschen von '{device_name}': {e}")
                QMessageBox.critical(self, "Fehler", f"Konnte Device nicht löschen: {e}")

    # --- Done / Load Device ---
    @Slot()
    def on_done_clicked(self):
            selected_items = self.listWidget_devices.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a device to continue.")
                return
            device_name = selected_items[0].text()
            success = self.dev_mgr.set_active_device(device_name)
            if success:
            
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to load device '{device_name}'.")
    
    def showEvent(self, event: QShowEvent):
        self.__refresh()
        try:
            last_device = self.dev_mgr.get_active_device()
            if last_device:
                items = self.listWidget_devices.findItems(last_device.name, Qt.MatchExactly)
                if items:
                    self.listWidget_devices.setCurrentItem(items[0])
        except Exception as e:
            self.log_mgr.error(f"Error selecting last active device: {e}")
        super().showEvent(event)

    def closeEvent(self, event: QCloseEvent):
        # Verhindert das Schließen über das 'X'-Symbol
        event.ignore()

# --- Device Edit Dialog ---

try:
    from .ui_DeviceWidgetEdit import Ui_Form as Ui_DeviceWidgetEdit
except ImportError:
    print("Fehler: Konnte 'ui_DeviceWidgetEdit.py' nicht finden.")
    from PySide6.QtWidgets import QWidget
    class Ui_DeviceWidgetEdit:
        def setupUi(self, Form):
            Form.setObjectName("DeviceEdit")

class DeviceWidgetEdit(QDialog, Ui_DeviceWidgetEdit):
    """
    Ein Dialog zur Erstellung und Bearbeitung von Device-Daten.
    
    - Nimmt Eingaben in nm entgegen.
    - Validiert Eingaben in Echtzeit.
    - Berechnet die Fläche in Echtzeit.
    - Gibt ein Dictionary mit Werten in Metern (m) zurück.
    """
    
    # Umrechnungsfaktor
    NM_TO_M = 1e-9
    M_TO_NM = 1e9

    def __init__(self, dev_mgr, device_data=None, parent=None):
        """
        Initialisiert den Dialog.
        
        :param dev_mgr: Der DeviceManager (für die Namensvalidierung).
        :param device_data: Ein optionales Dictionary mit bestehenden 
                            Device-Daten (für den "Edit"-Modus).
        :param parent: Das übergeordnete Widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True) # Stellt sicher, dass der Dialog modal ist

        self.dev_mgr = dev_mgr
        self.original_name = device_data.get("name") if device_data else None
        self.device_data = device_data if device_data else {}
        
        self.new_device_data = None # Hier wird das Ergebnis gespeichert

        self.__setup_ui()
        self.__connect_signals()
        self.__populate_form()
        
        # Initiale Validierung beim Öffnen
        self.__validate_and_update()

    # --- Setup-Methoden ---

    def __setup_ui(self):
        """Konfiguriert die UI-Elemente (Validatoren, ComboBox etc.)"""
        
        # Validatoren für nm-Eingaben (z.B. 0 bis 1 km in nm)
        validator = QDoubleValidator(0.0, 1e12, 3, self)
        self.lineEdit_length.setValidator(validator)
        self.lineEdit_width.setValidator(validator)
        self.lineEdit_radius.setValidator(validator)
        self.lineEdit_cutout_length.setValidator(validator)
        self.lineEdit_cutout_width.setValidator(validator)
        self.lineEdit_cutout_radius.setValidator(validator)

        # Geometrie-Optionen
        self.comboBox_geometry.addItems(["Rectangle", "Circle"])
        
        # Standard-Error-Stylesheet (wird für ungültige Felder verwendet)
        self.error_style = "border: 1px solid red;"

    def __connect_signals(self):
        """Verbindet alle Signale mit den entsprechenden Slots."""
        self.pushButton_save.clicked.connect(self.on_save_clicked)
        
        # Echtzeit-Validierung und Berechnung
        self.lineEdit_name.textChanged.connect(self.__validate_and_update)
        self.comboBox_geometry.currentTextChanged.connect(self.__validate_and_update)
        self.lineEdit_length.textChanged.connect(self.__validate_and_update)
        self.lineEdit_width.textChanged.connect(self.__validate_and_update)
        self.lineEdit_radius.textChanged.connect(self.__validate_and_update)
        self.checkBox_cutout.toggled.connect(self.__validate_and_update)
        self.lineEdit_cutout_length.textChanged.connect(self.__validate_and_update)
        self.lineEdit_cutout_width.textChanged.connect(self.__validate_and_update)
        self.lineEdit_cutout_radius.textChanged.connect(self.__validate_and_update)

    def __populate_form(self):
        """Füllt das Formular mit den Daten aus self.device_data (Edit-Modus)."""
        if not self.device_data:
            return # "Neu"-Modus

        self.lineEdit_name.setText(self.device_data.get("name", ""))
        self.comboBox_geometry.setCurrentText(self.device_data.get("geometry", "Rectangle"))

        dims = self.device_data.get("dimensions", {})

        # Umrechnung von Meter (dict) zu Nanometer (Feld)
        def set_nm_field(field_widget, dict_key_m):
            value_m = dims.get(dict_key_m)
            if value_m is not None:
                field_widget.setText(str(value_m * self.M_TO_NM))

        set_nm_field(self.lineEdit_length, "length")
        set_nm_field(self.lineEdit_width, "width")
        set_nm_field(self.lineEdit_radius, "radius")

        # Prüfen, ob Cutout-Daten vorhanden sind
        has_cutout = any(k in dims for k in ["cutout_length", "cutout_width", "cutout_radius"])
        self.checkBox_cutout.setChecked(has_cutout)
        
        if has_cutout:
            set_nm_field(self.lineEdit_cutout_length, "cutout_length")
            set_nm_field(self.lineEdit_cutout_width, "cutout_width")
            set_nm_field(self.lineEdit_cutout_radius, "cutout_radius")

    # --- Echtzeit-Logik ---

    @Slot()
    def __validate_and_update(self):
        """
        Wird bei jeder Änderung aufgerufen.
        Aktualisiert die UI-Sichtbarkeit, berechnet die Fläche und validiert das Formular.
        """
        self.__update_ui_visibility()
        self.__update_area()
        self.__validate_form()

    def __update_ui_visibility(self):
        """Passt die Sichtbarkeit von Feldern basierend auf der Geometrie an."""
        geometry = self.comboBox_geometry.currentText()
        is_rect = (geometry == "Rectangle")
        is_Circle = (geometry == "Circle")

        self.lineEdit_length.setVisible(is_rect)
        self.lineEdit_width.setVisible(is_rect)
        self.lineEdit_radius.setVisible(is_Circle)
        
        # Cutout-Felder
        cutout_enabled = self.checkBox_cutout.isChecked()
        self.lineEdit_cutout_length.setVisible(is_rect and cutout_enabled)
        self.lineEdit_cutout_width.setVisible(is_rect and cutout_enabled)
        self.lineEdit_cutout_radius.setVisible(is_Circle and cutout_enabled)
        
        # Sicherstellen, dass unsichtbare Felder keinen Validierungsfehler auslösen
        if not cutout_enabled:
            self.lineEdit_cutout_length.clear()
            self.lineEdit_cutout_width.clear()
            self.lineEdit_cutout_radius.clear()

    def __get_nm(self, field):
        """
        Liest den Text eines Feldes sicher als float (nm-Wert).
        Gibt 0.0 zurück, wenn unsichtbar, leer oder ungültig.
        """
        if not field.isVisible():
            return 0.0
        try:
            # Ersetze Komma durch Punkt für deutsche/internationale Eingabe
            return float(field.text().replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0

    def __update_area(self):
        """Berechnet die Fläche in Echtzeit und zeigt sie in m² an."""
        geometry = self.comboBox_geometry.currentText()

        area_nm2 = 0.0
        cutout_area_nm2 = 0.0

        if geometry == "Rectangle":
            l, w = self.__get_nm(self.lineEdit_length), self.__get_nm(self.lineEdit_width)
            area_nm2 = l * w
            if self.checkBox_cutout.isChecked():
                cl, cw = self.__get_nm(self.lineEdit_cutout_length), self.__get_nm(self.lineEdit_cutout_width)
                cutout_area_nm2 = cl * cw
        
        elif geometry == "Circle":
            r = self.__get_nm(self.lineEdit_radius)
            area_nm2 = math.pi * (r ** 2)
            if self.checkBox_cutout.isChecked():
                cr = self.__get_nm(self.lineEdit_cutout_radius)
                cutout_area_nm2 = math.pi * (cr ** 2)

        final_area_nm2 = area_nm2 - cutout_area_nm2
        final_area_m2 = final_area_nm2 * (self.NM_TO_M ** 2) # nm² zu m²

        self.lineEdit_area.setText(f"{final_area_nm2:.3e} nm²")

    def __validate_form(self):
        """
        Prüft alle Eingaben auf Gültigkeit und (de)aktiviert den "Save"-Button.
        Markiert ungültige Felder rot.
        """
        is_valid = True
        
        # Standard-Stylesheet (kein Fehler)
        default_style = ""
        
        # 1. Name
        name = self.lineEdit_name.text().strip()
        if not name:
            is_valid = False
            self.lineEdit_name.setStyleSheet(self.error_style)
        # Prüfen, ob der Name bereits vergeben ist, AUSSER es ist der Originalname
        elif name != self.original_name and (self.dev_mgr.get_device_by_name(name) is not None): 
            is_valid = False
            self.lineEdit_name.setStyleSheet(self.error_style)
        else:
            self.lineEdit_name.setStyleSheet(default_style)

        # 2. Geometrie-spezifische Felder
        geometry = self.comboBox_geometry.currentText()
        
        # Helfer zur Validierung von sichtbaren Feldern
        def validate_field(field):
            if not field.isVisible():
                return True # Unsichtbare Felder sind gültig
            if not field.text() or not self.__is_valid_float(field.text()):
                field.setStyleSheet(self.error_style)
                return False
            field.setStyleSheet(default_style)
            return True

        if geometry == "Rectangle":
            is_valid &= validate_field(self.lineEdit_length)
            is_valid &= validate_field(self.lineEdit_width)
        elif geometry == "Circle":
            is_valid &= validate_field(self.lineEdit_radius)
        else:
            is_valid = False # Keine Geometrie gewählt

        # 3. Cutout-Felder (nur wenn aktiv)
        if self.checkBox_cutout.isChecked():
            if geometry == "Rectangle":
                is_valid &= validate_field(self.lineEdit_cutout_length)
                is_valid &= validate_field(self.lineEdit_cutout_width)
            elif geometry == "Circle":
                is_valid &= validate_field(self.lineEdit_cutout_radius)
    
        # 4. Logische Validierung (Cutout darf nicht größer als Hauptgeometrie sein)
        if is_valid: 
            if geometry == "rectangle":
                l = self.__get_nm(self.lineEdit_length)
                w = self.__get_nm(self.lineEdit_width)
                if self.checkBox_cutout.isChecked():
                    cl = self.__get_nm(self.lineEdit_cutout_length)
                    cw = self.__get_nm(self.lineEdit_cutout_width)
                    
                    if cl > l:
                        is_valid = False
                        self.lineEdit_cutout_length.setStyleSheet(self.error_style)
                    if cw > w:
                        is_valid = False
                        self.lineEdit_cutout_width.setStyleSheet(self.error_style)
            
            elif geometry == "circle":
                r = self.__get_nm(self.lineEdit_radius)
                if self.checkBox_cutout.isChecked():
                    cr = self.__get_nm(self.lineEdit_cutout_radius)
                    if cr > r:
                        is_valid = False
                        self.lineEdit_cutout_radius.setStyleSheet(self.error_style)

        self.pushButton_save.setEnabled(bool(is_valid))
        return is_valid

    def __is_valid_float(self, text):
        try:
            float(text.replace(',', '.'))
            return True
        except ValueError:
            return False

    # --- Speichern & Rückgabe ---

    @Slot()
    def on_save_clicked(self):
        """
        Wird beim Klick auf "Save" aufgerufen.
        Erstellt das Dictionary, speichert es und schließt den Dialog.
        """
        if not self.__validate_form():
            return # Sollte nicht passieren, da Button deaktiviert ist

        data = {}
        data["name"] = self.lineEdit_name.text().strip()
        data["geometry"] = self.comboBox_geometry.currentText()
        
        # Helfer, um nm-Wert zu lesen und als Meter zu speichern
        def set_m_from_nm(field, dict_key):
            if field.isVisible() and field.text():
                data[dict_key] = float(field.text()) * self.NM_TO_M

        if data["geometry"] == "Rectangle":
            set_m_from_nm(self.lineEdit_length, "length")
            set_m_from_nm(self.lineEdit_width, "width")
        elif data["geometry"] == "Circle":
            set_m_from_nm(self.lineEdit_radius, "radius")

        if self.checkBox_cutout.isChecked():
            if data["geometry"] == "Rectangle":
                set_m_from_nm(self.lineEdit_cutout_length, "cutout_length")
                set_m_from_nm(self.lineEdit_cutout_width, "cutout_width")
            elif data["geometry"] == "Circle":
                set_m_from_nm(self.lineEdit_cutout_radius, "cutout_radius")

        self.new_device_data = data
        self.accept() # Schließt den Dialog mit "Accepted"-Status

    def get_data(self):
        """Gibt das erstellte Dictionary zurück."""
        return self.new_device_data

    # --- Statische Methode für einfachen Aufruf ---

    @staticmethod
    def get_device(dev_mgr, device_data=None, parent=None):
        """
        Öffnet den Dialog und gibt bei Erfolg das neue/aktualisierte 
        Device-Dictionary zurück, ansonsten None.
        
        :param dev_mgr: Der DeviceManager.
        :param device_data: Bestehende Daten für den Edit-Modus (optional).
        :param parent: Das übergeordnete Widget.
        :return: Ein Dictionary oder None.
        """
        dialog = DeviceWidgetEdit(dev_mgr, device_data, parent)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            return dialog.get_data()
        
        return None