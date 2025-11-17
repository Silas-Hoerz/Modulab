# -*- coding: utf-8 -*-
"""
============================================================================
 File:          SmuWidget.py
 Author:        (Dein Name)
 Creation date: 2025-11-17
 Last modified: 2025-11-17 (Bugfix: findChildren entfernt, manuelle Widget-Liste)
============================================================================
 Description:
     Diese Klasse verwaltet das SMU-UI-Panel.
     Sie verbindet die UI-Elemente (aus ui_SmuWidget.py)
    mit dem SmuManager und dessen neuer, intuitiver API.
    Sie steuert Kanal A und B komplett getrennt.
============================================================================
"""

# import re # <-- ENTFERNT, da fehlerhaft
from PySide6.QtWidgets import (
    QWidget, QButtonGroup, QAbstractItemView, QHeaderView, QWidget
)
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PySide6.QtCore import Slot, QEvent, Qt, QDateTime, QLocale

# Importiere die generierte UI-Klasse (Name aus deinem UI-File)
try:
    # Annahme: Deine neue Datei heißt 'ui_SmuWidget.py'
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
        
        # 1. ButtonGroups für die neuen PushButtons erstellen
        self.source_group_A = QButtonGroup(self)
        self.source_group_A.addButton(self.pushButton_voltageA)
        self.source_group_A.addButton(self.pushButton_currentA)
        # Standard-Auswahl ist bereits in .ui gesetzt (voltageA.checked = True)

        self.sense_group_A = QButtonGroup(self)
        self.sense_group_A.addButton(self.pushButton_localA)
        self.sense_group_A.addButton(self.pushButton_remoteA)
        # Standard-Auswahl ist bereits in .ui gesetzt (localA.checked = True)
        
        self.source_group_B = QButtonGroup(self)
        self.source_group_B.addButton(self.pushButton_voltageB)
        self.source_group_B.addButton(self.pushButton_currentB)
        # Standard-Auswahl ist bereits in .ui gesetzt (voltageB.checked = True)

        self.sense_group_B = QButtonGroup(self)
        self.sense_group_B.addButton(self.pushButton_localB)
        self.sense_group_B.addButton(self.pushButton_remoteB)
        # Standard-Auswahl ist bereits in .ui gesetzt (localB.checked = True)

        # 2. Validatoren für LineEdits (für alle 4 Felder)
        double_validator = QDoubleValidator()
        # Verwende englisches Locale für Punkte statt Kommas
        double_validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) 
        self.lineEdit_levelA.setValidator(double_validator)
        self.lineEdit_limitA.setValidator(double_validator)
        self.lineEdit_levelB.setValidator(double_validator)
        self.lineEdit_limitB.setValidator(double_validator)
        
        # 3. Standardwerte
        self.lineEdit_levelA.setText("0.0")
        self.lineEdit_limitA.setText("0.1") # 100mA als sicherer Standard
        self.lineEdit_levelB.setText("0.0")
        self.lineEdit_limitB.setText("0.1")

        # 4. Setup für die Mess-Tabellen (Modell A und B)
        self.modelA = QStandardItemModel(0, 3, self) # 0 Zeilen, 3 Spalten (Zeit, V, I)
        self.modelA.setHorizontalHeaderLabels(["Timestamp", "Spannung (V)", "Strom (A)"])
        self.tableView_measurementsA.setModel(self.modelA)
        
        self.modelB = QStandardItemModel(0, 3, self) # 0 Zeilen, 3 Spalten
        self.modelB.setHorizontalHeaderLabels(["Timestamp", "Spannung (V)", "Strom (A)"])
        self.tableView_measurementsB.setModel(self.modelB)
        
        # UI-Verhalten für die Tabellen einstellen
        self._setup_table_behavior(self.tableView_measurementsA)
        self._setup_table_behavior(self.tableView_measurementsB)

        # 5. Dynamische Labels initial setzen (basierend auf .ui-Standard)
        self._update_channel_labels('a')
        self._update_channel_labels('b')

        # 6. Initialen (getrennten) Zustand setzen
        self.on_connection_status_changed(False, "")

    def _setup_table_behavior(self, table_view):
        """Hilfsfunktion zum Konfigurieren der Tabellen-Ansicht."""
        table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Timestamp
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Spannung
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Strom

    def __connect_signals(self):
        """Verbindet alle Signale und Slots."""
        
        # 1. Manager-Signale an UI-Slots (diese Klasse)
        self.smu_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.smu_mgr.device_list_updated.connect(self.on_device_list_updated)
        self.smu_mgr.new_measurement_acquired.connect(self.on_new_measurement_acquired)

        # 2. UI-Elemente (Verbindung)
        self.pushButton_connect.clicked.connect(self.on_connect_clicked)

        # 3. UI-Elemente (Kanal A) - Verwende die neuen PushButtons
        self.pushButton_resetA.clicked.connect(self.on_reset_A_clicked)
        self.pushButton_measureA.clicked.connect(self.on_measure_A_clicked)
        self.pushButton_outputA.toggled.connect(self.on_output_A_toggled)
        # Source-Buttons (V/I)
        self.pushButton_voltageA.toggled.connect(self.on_source_A_changed)
        self.pushButton_currentA.toggled.connect(self.on_source_A_changed)
        # Sense-Buttons (Local/Remote)
        self.pushButton_localA.toggled.connect(self.on_sense_A_changed)
        self.pushButton_remoteA.toggled.connect(self.on_sense_A_changed)
        # LineEdits
        self.lineEdit_levelA.editingFinished.connect(self.on_level_A_changed)
        self.lineEdit_limitA.editingFinished.connect(self.on_limit_A_changed)

        # 4. UI-Elemente (Kanal B) - Verwende die neuen PushButtons
        self.pushButton_resetB.clicked.connect(self.on_reset_B_clicked)
        self.pushButton_measureB.clicked.connect(self.on_measure_B_clicked)
        self.pushButton_outputB.toggled.connect(self.on_output_B_toggled)
        # Source-Buttons (V/I)
        self.pushButton_voltageB.toggled.connect(self.on_source_B_changed)
        self.pushButton_currentB.toggled.connect(self.on_source_B_changed)
        # Sense-Buttons (Local/Remote)
        self.pushButton_localB.toggled.connect(self.on_sense_B_changed)
        self.pushButton_remoteB.toggled.connect(self.on_sense_B_changed)
        # LineEdits
        self.lineEdit_levelB.editingFinished.connect(self.on_level_B_changed)
        self.lineEdit_limitB.editingFinished.connect(self.on_limit_B_changed)

    # --- Hilfsfunktionen ---
    
    def _set_channel_controls_enabled(self, channel_char: str, enabled: bool):
        """
        Aktiviert oder deaktiviert alle Steuerelemente für einen Kanal.
        (KORRIGIERTE VERSION - manuelle Auflistung)
        """
        widgets_to_toggle = []
        if channel_char == 'a':
            widgets_to_toggle = [
                self.label_2, self.line_3, self.pushButton_measureA,
                self.lineEdit_levelA, self.label_limitA, self.lineEdit_limitA,
                self.pushButton_currentA, self.label_levelA, self.pushButton_outputA,
                self.label_voltageA, self.pushButton_remoteA, self.pushButton_voltageA,
                self.label_currentA, self.line_2, self.pushButton_localA,
                self.label_6, self.pushButton_resetA, self.tableView_measurementsA
            ]
        elif channel_char == 'b':
            widgets_to_toggle = [
                self.label_channel, self.line_4, self.label_currentB,
                self.pushButton_measureB, self.pushButton_remoteB, self.line,
                self.pushButton_currentB, self.label_limitB, self.label_voltageB,
                self.label_levelB, self.pushButton_voltageB, self.pushButton_localB,
                self.pushButton_resetB, self.pushButton_outputB, self.label_3,
                self.lineEdit_levelB, self.lineEdit_limitB, self.tableView_measurementsB
            ]
        else:
            return

        for widget in widgets_to_toggle:
            # Stelle sicher, dass das Widget existiert (ist bei QFrame/line der Fall)
            if isinstance(widget, QWidget): 
                widget.setEnabled(enabled)

    def _update_channel_labels(self, channel: str):
        """
        NEU: Aktualisiert die [V]/[A] Labels basierend auf dem Source-Modus.
        """
        if channel == 'a':
            is_voltage_source = self.pushButton_voltageA.isChecked()
            if is_voltage_source:
                self.label_levelA.setText("Level [V]")
                self.label_limitA.setText("Limit [A]")
            else:
                self.label_levelA.setText("Level [A]")
                self.label_limitA.setText("Limit [V]")
        
        elif channel == 'b':
            is_voltage_source = self.pushButton_voltageB.isChecked()
            if is_voltage_source:
                self.label_levelB.setText("Level [V]")
                self.label_limitB.setText("Limit [A]")
            else:
                self.label_levelB.setText("Level [A]")
                self.label_limitB.setText("Limit [V]")

    def _format_si(self, value: float, unit: str) -> str:
        """
        Formatiert einen Float-Wert mit SI-Präfixen (z.B. m, µ, k).
        """
        if value == 0:
            return f"0.00 {unit}"
        
        abs_val = abs(value)
        
        if abs_val >= 1e9:
            return f"{value / 1e9:.2f} G{unit}"
        if abs_val >= 1e6:
            return f"{value / 1e6:.2f} M{unit}"
        if abs_val >= 1e3:
            return f"{value / 1e3:.2f} k{unit}"
        if abs_val >= 1:
            return f"{value:.3f} {unit}"
        if abs_val >= 1e-3:
            return f"{value * 1e3:.2f} m{unit}"
        if abs_val >= 1e-6:
            return f"{value * 1e6:.2f} µ{unit}"
        if abs_val >= 1e-9:
            return f"{value * 1e9:.2f} n{unit}"
        if abs_val >= 1e-12:
            return f"{value * 1e12:.2f} p{unit}"
        
        # Fallback für sehr kleine Zahlen
        return f"{value:.2e} {unit}"

    # --- Slots für Signale vom SmuManager ---

    @Slot(list)
    def on_device_list_updated(self, port_names):
        """Aktualisiert die ComboBox, wenn der Manager Ports gefunden hat."""
        current_selection = self.comboBox_port.currentText()
        self.comboBox_port.clear()
        self.comboBox_port.addItems(port_names)
        
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
            self.label_status.setText(f"Connected")
            self.label_status.setStyleSheet("color: green;")
            self.pushButton_connect.setText("Disconnect")
            self.comboBox_port.setEnabled(False)
            
            # Beide Kanäle aktivieren
            self._set_channel_controls_enabled('a', True)
            self._set_channel_controls_enabled('b', True)
        
        else: # Nicht verbunden
            self.label_status.setText("Not Connected")
            self.label_status.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect")
            self.comboBox_port.setEnabled(True)
            
            # Beide Kanäle deaktivieren
            self._set_channel_controls_enabled('a', False)
            self._set_channel_controls_enabled('b', False)
        
            # Labels und Buttons auf Default zurücksetzen
            self._sync_ui_to_reset_state('a')
            self._sync_ui_to_reset_state('b')
            # Tabellen leeren
            self.modelA.setRowCount(0)
            self.modelB.setRowCount(0)


    @Slot(str, float, float)
    def on_new_measurement_acquired(self, channel, current, voltage):
        """
        Aktualisiert die Readout-Labels UND fügt die Messung zur richtigen Tabelle hinzu.
        """
        # --- NEU: Werte mit SI-Präfix formatieren ---
        formatted_voltage = self._format_si(voltage, "V")
        formatted_current = self._format_si(current, "A")
        
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        item_time = QStandardItem(timestamp)
        # --- NEU: Formatierte Werte für die Tabelle verwenden ---
        item_volt = QStandardItem(formatted_voltage)
        item_curr = QStandardItem(formatted_current)
        
        # Zellen-Ausrichtung
        item_volt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_curr.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        if channel == 'a':
            # --- NEU: Formatierte Werte für Labels verwenden ---
            self.label_voltageA.setText(formatted_voltage)
            self.label_currentA.setText(formatted_current)
            self.modelA.insertRow(0, [item_time, item_volt, item_curr])
        
        elif channel == 'b':
            # --- NEU: Formatierte Werte für Labels verwenden ---
            self.label_voltageB.setText(formatted_voltage)
            self.label_currentB.setText(formatted_current)
            self.modelB.insertRow(0, [item_time, item_volt, item_curr])

    # --- Slots für UI-Aktionen (Verbindung) ---

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

    # --- Hilfsfunktion für Reset (aktualisiert) ---
    
    def _sync_ui_to_reset_state(self, channel: str):
        """
        Setzt alle UI-Elemente eines Kanals auf den bekannten
        Geräte-Default-Zustand (nach Reset) zurück.
        """
        if channel == 'a':
            # Blockiere Signale, um Endlosschleifen (toggled -> changed) zu verhindern
            self.pushButton_voltageA.blockSignals(True)
            self.pushButton_localA.blockSignals(True)
            
            self.pushButton_voltageA.setChecked(True) # Default ist Voltage
            self.pushButton_localA.setChecked(True) # Default ist Local
            
            self.pushButton_voltageA.blockSignals(False)
            self.pushButton_localA.blockSignals(False)
            
            self.lineEdit_levelA.setText("0.0") # Default ist 0V
            self.lineEdit_limitA.setText("10e-6") # 10µA (Geräte-Default)
            self.pushButton_outputA.setChecked(False) 
            self.pushButton_outputA.setText("OFF")
            self.label_voltageA.setText("--- V")
            self.label_currentA.setText("--- A")
            self._update_channel_labels('a') # Wichtig: Labels [V]/[A] aktualisieren
        
        elif channel == 'b':
            self.pushButton_voltageB.blockSignals(True)
            self.pushButton_localB.blockSignals(True)
            
            self.pushButton_voltageB.setChecked(True) # Default ist Voltage
            self.pushButton_localB.setChecked(True) # Default ist Local
            
            self.pushButton_voltageB.blockSignals(False)
            self.pushButton_localB.blockSignals(False)
            
            self.lineEdit_levelB.setText("0.0") # Default ist 0V
            self.lineEdit_limitB.setText("10e-6") # 10µA (Geräte-Default)
            self.pushButton_outputB.setChecked(False) 
            self.pushButton_outputB.setText("OFF")
            self.label_voltageB.setText("--- V")
            self.label_currentB.setText("--- A")
            self._update_channel_labels('b') # Wichtig: Labels [V]/[A] aktualisieren

    # --- Slots für UI-Aktionen (KANAL A) ---

    @Slot()
    def on_measure_A_clicked(self):
        self.smu_mgr.measure_iv('a')

    @Slot()
    def on_reset_A_clicked(self):
        self.smu_mgr.reset_channel('a')
        self.modelA.setRowCount(0) # Tabelle leeren
        self._sync_ui_to_reset_state('a') # UI auf Default setzen

    @Slot(bool)
    def on_output_A_toggled(self, is_on):
        self.smu_mgr.set_output_state('a', is_on)
        self.pushButton_outputA.setText("ON" if is_on else "OFF")

    @Slot()
    def on_source_A_changed(self):
        # Wird getriggert, wenn V ODER C gecheckt wird
        # Nur senden, wenn der Button auch wirklich 'checked' ist
        if self.pushButton_voltageA.isChecked():
            self.smu_mgr.set_source_voltage('a')
        elif self.pushButton_currentA.isChecked():
            self.smu_mgr.set_source_current('a')
        # IMMER die Labels aktualisieren
        self._update_channel_labels('a')

    @Slot()
    def on_sense_A_changed(self):
        # Wird getriggert, wenn Local ODER Remote gecheckt wird
        if self.pushButton_remoteA.isChecked():
            self.smu_mgr.set_sense_remote('a')
        elif self.pushButton_localA.isChecked():
            self.smu_mgr.set_sense_local('a')
    
    @Slot()
    def on_level_A_changed(self):
        try:
            level = float(self.lineEdit_levelA.text())
            self.smu_mgr.set_source_level('a', level)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Level-Eingabe (A): '{self.lineEdit_levelA.text()}'")

    @Slot()
    def on_limit_A_changed(self):
        try:
            limit = float(self.lineEdit_limitA.text()) 
            self.smu_mgr.set_source_limit('a', limit)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Limit-Eingabe (A): '{self.lineEdit_limitA.text()}'")

    # --- Slots für UI-Aktionen (KANAL B) ---

    @Slot()
    def on_measure_B_clicked(self):
        self.smu_mgr.measure_iv('b')

    @Slot()
    def on_reset_B_clicked(self):
        self.smu_mgr.reset_channel('b')
        self.modelB.setRowCount(0) # Tabelle leeren
        self._sync_ui_to_reset_state('b') # UI auf Default setzen

    @Slot(bool)
    def on_output_B_toggled(self, is_on):
        # HINWEIS: Dies funktioniert, da du outputB 'checkable' gemacht hast.
        self.smu_mgr.set_output_state('b', is_on)
        self.pushButton_outputB.setText("ON" if is_on else "OFF")

    @Slot()
    def on_source_B_changed(self):
        if self.pushButton_voltageB.isChecked():
            self.smu_mgr.set_source_voltage('b')
        elif self.pushButton_currentB.isChecked():
            self.smu_mgr.set_source_current('b')
        # IMMER die Labels aktualisieren
        self._update_channel_labels('b')

    @Slot()
    def on_sense_B_changed(self):
        if self.pushButton_remoteB.isChecked():
            self.smu_mgr.set_sense_remote('b')
        elif self.pushButton_localB.isChecked():
            self.smu_mgr.set_sense_local('b')
    
    @Slot()
    def on_level_B_changed(self):
        try:
            level = float(self.lineEdit_levelB.text())
            self.smu_mgr.set_source_level('b', level)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Level-Eingabe (B): '{self.lineEdit_levelB.text()}'")

    @Slot()
    def on_limit_B_changed(self):
        try:
            limit = float(self.lineEdit_limitB.text()) 
            self.smu_mgr.set_source_limit('b', limit)
        except ValueError:
            self.log_mgr.warning(f"Ungültige Limit-Eingabe (B): '{self.lineEdit_limitB.text()}'")

    # --- Event Filter für ComboBox ---
    
    def eventFilter(self, watched_object, event):
        """
        Fängt Events ab, um das Öffnen der ComboBox zu erkennen.       
        """
        if watched_object == self.comboBox_port:
            if event.type() == QEvent.Type.MouseButtonPress:
                if not self.comboBox_port.view().isVisible():
                    # ComboBox wird gerade geöffnet -> Liste aktualisieren
                    self.smu_mgr.get_deviceList()

        # Event an die Basisklasse weiterleiten
        return super().eventFilter(watched_object, event)