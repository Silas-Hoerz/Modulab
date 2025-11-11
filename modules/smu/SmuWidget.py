# -*- coding: utf-8 -*-


from PySide6.QtWidgets import (
    QWidget, QButtonGroup, QAbstractItemView, QHeaderView
)
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PySide6.QtCore import Slot, QEvent, Qt, QDateTime, QLocale

# Importiere die generierte UI-Klasse
try:
    from .ui_SmuWidget import Ui_Form 
except ImportError:
    print("Error: Could not find 'ui_SmuWidget.py'.")
    # Notfall-Fallback
    from PySide6.QtWidgets import QVBoxLayout, QLabel
    class Ui_Form:
        def setupUi(self, Form):
            self.vLayout = QVBoxLayout(Form)
            self.label_progress = QLabel("UI File 'ui_SmuWidget.py' not loaded", Form)
            self.vLayout.addWidget(self.label_progress)
        def retranslateUi(self, Form): pass


class SmuWidget(QWidget, Ui_Form):
    """
    Diese Klasse verwaltet das SMU-UI-Panel.
    Sie verbindet die UI-Elemente mit dem SmuManager.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Manager aus dem Kontext-Objekt holen
        self.smu_mgr = context.smu_manager
        self.log_mgr = context.log_manager

        self.__setup_ui()
        self.__connect_signals()

        # Event-Filter für die ComboBox
        self.comboBox_port.installEventFilter(self)

        # Beim Start sofort nach Geräten suchen
        self.smu_mgr.get_deviceList()

    def __setup_ui(self):
        """Setzt den anfänglichen Zustand der UI-Elemente."""
        
        # 1. ButtonGroups erstellen (fehlt in der .ui-Datei)
        self.channel_group = QButtonGroup(self)
        self.channel_group.addButton(self.radioButton_channelA)
        self.channel_group.addButton(self.radioButton_channelB)
        self.radioButton_channelA.setChecked(True)

        self.source_group = QButtonGroup(self)
        self.source_group.addButton(self.radioButton_voltage)
        self.source_group.addButton(self.radioButton_current)
        self.radioButton_voltage.setChecked(True)

        self.sense_group = QButtonGroup(self)
        self.sense_group.addButton(self.radioButton_local)
        self.sense_group.addButton(self.radioButton_remote)
        self.radioButton_local.setChecked(True)

        # 2. Validatoren für LineEdits
        double_validator = QDoubleValidator()
        double_validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Punkte statt Kommas
        self.lineEdit_level.setValidator(double_validator)
        self.lineEdit_limit.setValidator(double_validator) # Achtung: Tippfehler (doppelter __) aus .ui-Datei
        
        # 3. Standardwerte
        self.lineEdit_level.setText("0.0")
        self.lineEdit_limit.setText("0.1") # 100mA als sicherer Standard

        # 4. Setup für die Mess-Tabelle (NEU)
        self.measurement_model = QStandardItemModel(0, 4, self) # 0 Zeilen, 4 Spalten
        self.measurement_model.setHorizontalHeaderLabels(["Timestamp", "Kanal", "Spannung (V)", "Strom (A)"])
        self.tableView_measurements.setModel(self.measurement_model)
        
        # UI-Verhalten für die Tabelle einstellen
        self.tableView_measurements.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Nicht editierbar
        self.tableView_measurements.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # Ganze Zeilen markieren
        
        # Spaltenbreiten anpassen (NEU)
        header = self.tableView_measurements.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Timestamp
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Kanal
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Spannung
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Strom

        # 5. Initialen (getrennten) Zustand setzen
        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        """Verbindet alle Signale und Slots."""
        
        # 1. Manager-Signale an UI-Slots (diese Klasse)
        self.smu_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.smu_mgr.device_list_updated.connect(self.on_device_list_updated)
        self.smu_mgr.new_measurement_acquired.connect(self.on_new_measurement_acquired)

        # 2. UI-Elemente an lokale Slots oder direkt an Manager
        self.pushButton_connect.clicked.connect(self.on_connect_clicked)
        self.pushButton_measure.clicked.connect(self.on_measure_clicked)
        self.pushButton_reset.clicked.connect(self.on_reset_clicked)

        # UI-Aktionen, die sofort gesendet werden
        self.pushButton_output.toggled.connect(self.on_output_toggled)
        self.radioButton_voltage.toggled.connect(self.on_source_changed) # Wenn V getoggled wird
        self.radioButton_remote.toggled.connect(self.on_sense_changed) # Wenn Remote getoggled wird
        self.radioButton_local.toggled.connect(self.on_sense_changed) # Auch wenn Local getoggled wird
        
        self.lineEdit_level.editingFinished.connect(self.on_level_changed)
        self.lineEdit_limit.editingFinished.connect(self.on_limit_changed)
        
        # Stelle sicher, dass Einstellungsänderungen den richtigen Kanal verwenden
        self.radioButton_channelA.toggled.connect(self.on_settings_changed)
        self.radioButton_channelB.toggled.connect(self.on_settings_changed)

    # --- Hilfsfunktion ---
    
    def _get_active_channel(self) -> str:
        """Gibt den aktuell im UI ausgewählten Kanal ('a' oder 'b') zurück."""
        return 'a' if self.radioButton_channelA.isChecked() else 'b'

    # --- Slots für Signale vom SmuManager ---

    @Slot(list)
    def on_device_list_updated(self, port_names):
        """Aktualisiert die ComboBox, wenn der Manager Ports gefunden hat."""
        current_selection = self.comboBox_port.currentText()
        self.comboBox_port.clear()
        self.comboBox_port.addItems(port_names)
        
        # Versuche, das zuletzt verbundene Gerät auszuwählen
        last_device = self.smu_mgr.LastDevice
        if last_device in port_names:
            self.comboBox_port.setCurrentText(last_device)
        elif current_selection in port_names:
            self.comboBox_port.setCurrentText(current_selection)

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        """
        Schaltet die UI-Zustände um, wenn die Verbindung aufgebaut oder getrennt wird.
        """
        if connected:
            self.label_status.setText(f"Verbunden: {device_name.split('@')[0]}")
            self.label_status.setStyleSheet("color: green;")
            self.pushButton_connect.setText("Trennen")
            self.comboBox_port.setEnabled(False) # Auswahl sperren
            
            # Alle Steuerelemente aktivieren
            for child in self.gridLayout.parentWidget().findChildren(QWidget):
                if child != self.label_status: # Status-Label nicht überschreiben
                    child.setEnabled(True)
            self.pushButton_measure.setEnabled(True)
            self.tableView_measurements.setEnabled(True)
        
        else: # Nicht verbunden
            self.label_status.setText("Nicht verbunden")
            self.label_status.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Verbinden")
            self.comboBox_port.setEnabled(True) # Auswahl freigeben
            
            # Alle Steuerelemente (außer Verbindung) deaktivieren
            for child in self.gridLayout.parentWidget().findChildren(QWidget):
                # Deaktiviere alles im Grid und im Hauptlayout
                if child not in [self.label, self.comboBox_port, self.pushButton_connect, self.label_status]:
                    child.setEnabled(False)
            self.pushButton_measure.setEnabled(False)
            self.tableView_measurements.setEnabled(False)
        
            # Labels zurücksetzen
            self.label_voltage.setText("--- V")
            self.label_current.setText("--- A")
            self.pushButton_output.setChecked(False)


    @Slot(str, float, float)
    def on_new_measurement_acquired(self, channel, current, voltage):
        """
        Aktualisiert die Readout-Labels UND fügt die Messung zur Tabelle hinzu. (MODIFIZIERT)
        """
        
        # 1. Labels aktualisieren, falls die Messung vom aktiven Kanal kommt
        if channel == self._get_active_channel():
            self.label_voltage.setText(f"{voltage:.4e} V")
            self.label_current.setText(f"{current:.4e} A")

        # 2. Messung zur Tabelle hinzufügen (immer, da dies von measure_iv getriggert wird) (NEU)
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        # Erstelle die QStandardItems für jede Zelle
        item_time = QStandardItem(timestamp)
        item_ch = QStandardItem(channel.upper())
        item_volt = QStandardItem(f"{voltage:.4e}")
        item_curr = QStandardItem(f"{current:.4e}")
        
        # Zellen-Ausrichtung für bessere Lesbarkeit
        item_ch.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        item_volt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_curr.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
     
        # Füge die Zeile GANZ OBEN in das Modell ein
        self.measurement_model.insertRow(0, [item_time, item_ch, item_volt, item_curr])

    # --- Slots für UI-Aktionen ---

    @Slot()
    def on_connect_clicked(self):
        """Wird aufgerufen, wenn der Verbinden/Trennen-Button geklickt wird."""
        if self.smu_mgr.is_connected():
            self.smu_mgr.disconnect()
        else:
            selected_port = self.comboBox_port.currentText()
            if not selected_port:
                self.log_mgr.warning("Kein SMU-Port zur Verbindung ausgewählt.")
                return
            self.smu_mgr.connect(selected_port)

    @Slot()
    def on_measure_clicked(self):
        """Führt eine einzelne Messung auf dem aktiven Kanal durch."""
        # Dieser Aufruf triggert den Manager, der dann das
        # 'new_measurement_acquired'-Signal sendet, welches
        # 'on_new_measurement_acquired' (oben) aufruft.
        self.smu_mgr.measure_iv(self._get_active_channel())

    @Slot()
    def on_reset_clicked(self):
        """Setzt den aktiven Kanal zurück."""
        self.smu_mgr.reset_channel(self._get_active_channel())
        # Optional: Tabelle leeren
        # self.measurement_model.clear()
        # self.__setup_ui() # Setzt Header etc. neu

    @Slot(bool)
    def on_output_toggled(self, is_on):
        """Schaltet den Output des aktiven Kanals ein oder aus."""
        self.smu_mgr.set_output_state(self._get_active_channel(), is_on)
        self.pushButton_output.setText("Output ON" if is_on else "Output OFF")

    @Slot()
    def on_settings_changed(self):
        """
        Wird aufgerufen, wenn eine Einstellung (Kanal, Source, Sense, Level, Limit)
        geändert wird, um die SMU sofort zu aktualisieren.
        """
        self.on_source_changed()
        self.on_sense_changed()
        self.on_level_changed()
        self.on_limit_changed()
    
    @Slot()
    def on_source_changed(self):
        is_voltage = self.radioButton_voltage.isChecked()
        self.smu_mgr.set_source(self._get_active_channel(), is_voltage)

    @Slot()
    def on_sense_changed(self):
        is_remote = self.radioButton_remote.isChecked()
        self.smu_mgr.set_sense_mode(self._get_active_channel(), is_remote)
    
    @Slot()
    def on_level_changed(self):
        try:
            level = float(self.lineEdit_level.text())
            self.smu_mgr.set_source_level(self._get_active_channel(), level)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Level-Eingabe: '{self.lineEdit_level.text()}'")

    @Slot()
    def on_limit_changed(self):
        try:
            # Achtung: Tippfehler (doppelter __) aus .ui-Datei
            limit = float(self.lineEdit_limit.text()) 
            self.smu_mgr.set_source_limit(self._get_active_channel(), limit)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Limit-Eingabe: '{self.lineEdit_limit.text()}'")

    # --- Event Filter für ComboBox ---
    
    def eventFilter(self, watched_object, event):
        """
        Fängt Events ab, um das Öffnen der ComboBox zu erkennen.       
        """
        if watched_object == self.comboBox_port:
            # Wir verwenden popupAboutToShow, da es sauberer ist als MouseButtonPress
            if event.type() == QEvent.Type.MouseButtonPress:
                if not self.comboBox_port.view().isVisible():
                    # ComboBox wird gerade geöffnet -> Liste aktualisieren
                    self.smu_mgr.get_deviceList()

        # Event an die Basisklasse weiterleiten
        return super().eventFilter(watched_object, event)