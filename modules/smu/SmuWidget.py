# modules/smu/SmuWidget.py
# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QButtonGroup, QAbstractItemView, QHeaderView, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PySide6.QtCore import Slot, QEvent, Qt, QDateTime, QLocale

# Import UI
try:
    from .ui_SmuWidget import Ui_Form 
except ImportError:
    class Ui_Form:
        def setupUi(self, Form): pass

class SmuWidget(QWidget, Ui_Form):
    """
    Diese Klasse verwaltet das SMU-UI-Panel.
    
    Sie empfängt keine Daten direkt aus dem Profil, sondern synchronisiert sich
    ausschließlich mit dem SmuManager (Single Source of Truth).
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.smu_mgr = context.smu_manager
        self.log_mgr = context.log_manager

        # Wir warten auf das Profil-Laden-Signal
        # Wenn das Profil geladen ist, aktualisieren wir die UI, 
        # falls der Manager bereits verbunden ist.
        if hasattr(self.smu_mgr, 'profile_mgr'):
             self.smu_mgr.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

        self.__setup_ui()
        self.__connect_signals()

        self.comboBox_port.installEventFilter(self)
        self.smu_mgr.get_deviceList()

    def __setup_ui(self):
        """Setzt Initiale UI-Konfiguration (Tabellen, Gruppen)."""
        
        # 1. ButtonGroups
        self.bg_src_a = QButtonGroup(self)
        self.bg_src_a.addButton(self.pushButton_voltageA)
        self.bg_src_a.addButton(self.pushButton_currentA)

        self.bg_sns_a = QButtonGroup(self)
        self.bg_sns_a.addButton(self.pushButton_localA)
        self.bg_sns_a.addButton(self.pushButton_remoteA)
        
        self.bg_src_b = QButtonGroup(self)
        self.bg_src_b.addButton(self.pushButton_voltageB)
        self.bg_src_b.addButton(self.pushButton_currentB)

        self.bg_sns_b = QButtonGroup(self)
        self.bg_sns_b.addButton(self.pushButton_localB)
        self.bg_sns_b.addButton(self.pushButton_remoteB)

        # 2. Validatoren
        double_validator = QDoubleValidator()
        double_validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) 
        for le in [self.lineEdit_levelA, self.lineEdit_limitA, self.lineEdit_levelB, self.lineEdit_limitB]:
            le.setValidator(double_validator)
        
        # 3. Tabellen
        self.modelA = QStandardItemModel(0, 3, self)
        self.modelA.setHorizontalHeaderLabels(["Time", "Volt", "Curr"])
        self.tableView_measurementsA.setModel(self.modelA)
        
        self.modelB = QStandardItemModel(0, 3, self)
        self.modelB.setHorizontalHeaderLabels(["Time", "Volt", "Curr"])
        self.tableView_measurementsB.setModel(self.modelB)
        
        for tv in [self.tableView_measurementsA, self.tableView_measurementsB]:
            tv.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            tv.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 4. Initiale Labels und Zustand
        self._update_channel_labels('a')
        self._update_channel_labels('b')
        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        """Verbindet Signale."""
        self.smu_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.smu_mgr.device_list_updated.connect(self.on_device_list_updated)
        self.smu_mgr.new_measurement_acquired.connect(self.on_new_measurement_acquired)

        self.pushButton_connect.clicked.connect(self.on_connect_clicked)

        # --- Channel A ---
        self.pushButton_resetA.clicked.connect(self.on_reset_A_clicked)
        self.pushButton_measureA.clicked.connect(lambda: self.smu_mgr.measure_iv('a'))
        self.pushButton_outputA.toggled.connect(lambda s: self.smu_mgr.set_output_state('a', s))
        
        self.pushButton_voltageA.toggled.connect(lambda c: self.smu_mgr.set_source_voltage('a') if c else None)
        self.pushButton_currentA.toggled.connect(lambda c: self.smu_mgr.set_source_current('a') if c else None)
        self.bg_src_a.buttonToggled.connect(lambda: self._update_channel_labels('a'))

        self.pushButton_localA.toggled.connect(lambda c: self.smu_mgr.set_sense_local('a') if c else None)
        self.pushButton_remoteA.toggled.connect(lambda c: self.smu_mgr.set_sense_remote('a') if c else None)
        
        self.lineEdit_levelA.editingFinished.connect(self.on_level_A_changed)
        self.lineEdit_limitA.editingFinished.connect(self.on_limit_A_changed)

        # --- Channel B ---
        self.pushButton_resetB.clicked.connect(self.on_reset_B_clicked)
        self.pushButton_measureB.clicked.connect(lambda: self.smu_mgr.measure_iv('b'))
        self.pushButton_outputB.toggled.connect(lambda s: self.smu_mgr.set_output_state('b', s))
        
        self.pushButton_voltageB.toggled.connect(lambda c: self.smu_mgr.set_source_voltage('b') if c else None)
        self.pushButton_currentB.toggled.connect(lambda c: self.smu_mgr.set_source_current('b') if c else None)
        self.bg_src_b.buttonToggled.connect(lambda: self._update_channel_labels('b'))

        self.pushButton_localB.toggled.connect(lambda c: self.smu_mgr.set_sense_local('b') if c else None)
        self.pushButton_remoteB.toggled.connect(lambda c: self.smu_mgr.set_sense_remote('b') if c else None)
        
        self.lineEdit_levelB.editingFinished.connect(self.on_level_B_changed)
        self.lineEdit_limitB.editingFinished.connect(self.on_limit_B_changed)

    # ==========================================================================
    # KERN-LOGIK: Sync UI from Manager
    # ==========================================================================

    def sync_ui_from_manager(self, ch: str):
        """
        Holt den aktuellen Status vom Manager und setzt die UI-Elemente.
        Nutzt blockSignals, damit wir keine endlosen Loops erzeugen.
        """
        state = self.smu_mgr.get_channel_state(ch)
        
        # Elemente auswählen je nach Kanal
        if ch == 'a':
            btn_v, btn_i = self.pushButton_voltageA, self.pushButton_currentA
            btn_loc, btn_rem = self.pushButton_localA, self.pushButton_remoteA
            le_lev, le_lim = self.lineEdit_levelA, self.lineEdit_limitA
            btn_out = self.pushButton_outputA
        else:
            btn_v, btn_i = self.pushButton_voltageB, self.pushButton_currentB
            btn_loc, btn_rem = self.pushButton_localB, self.pushButton_remoteB
            le_lev, le_lim = self.lineEdit_levelB, self.lineEdit_limitB
            btn_out = self.pushButton_outputB

        # Signale blockieren
        widgets = [btn_v, btn_i, btn_loc, btn_rem, le_lev, le_lim, btn_out]
        for w in widgets: w.blockSignals(True)

        # Werte setzen
        if state['source_func'] == 'V': btn_v.setChecked(True)
        else: btn_i.setChecked(True)
        
        if state['sense'] == 'remote': btn_rem.setChecked(True)
        else: btn_loc.setChecked(True)
        
        le_lev.setText(str(state['level']))
        le_lim.setText(str(state['limit']))
        
        # Output State
        btn_out.setChecked(state['output'])
        btn_out.setText("ON" if state['output'] else "OFF")

        # Signale freigeben
        for w in widgets: w.blockSignals(False)
            
        # Labels aktualisieren
        self._update_channel_labels(ch)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        """
        Wird aufgerufen, wenn Profil geladen wurde.
        Falls Manager schon verbunden ist (durch Autoconnect), UI updaten.
        """
        if self.smu_mgr.is_connected():
            self.sync_ui_from_manager('a')
            self.sync_ui_from_manager('b')

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        """Verbindung geändert -> UI aktivieren/deaktivieren und syncen."""
        if connected:
            self.label_status.setText(f"Connected")
            self.label_status.setStyleSheet("color: green;")
            self.pushButton_connect.setText("Disconnect")
            self.comboBox_port.setEnabled(False)
            
            self._set_channel_enabled('a', True)
            self._set_channel_enabled('b', True)
            
            # WICHTIG: UI mit Hardware abgleichen (da Manager Settings geladen hat)
            self.sync_ui_from_manager('a')
            self.sync_ui_from_manager('b')
        
        else:
            self.label_status.setText("Not Connected")
            self.label_status.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect")
            self.comboBox_port.setEnabled(True)
            
            self._set_channel_enabled('a', False)
            self._set_channel_enabled('b', False)
            self.modelA.setRowCount(0)
            self.modelB.setRowCount(0)

    # --- Helpers ---

    def _set_channel_enabled(self, ch: str, en: bool):
        # Alle Widgets im jeweiligen Grid enablen/disablen
        layout = self.gridLayout_channelA if ch == 'a' else self.gridLayout_channelB
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setEnabled(en)

    def _update_channel_labels(self, ch: str):
        if ch == 'a':
            is_v = self.pushButton_voltageA.isChecked()
            self.label_levelA.setText("Level [V]" if is_v else "Level [A]")
            self.label_limitA.setText("Limit [A]" if is_v else "Limit [V]")
        else:
            is_v = self.pushButton_voltageB.isChecked()
            self.label_levelB.setText("Level [V]" if is_v else "Level [A]")
            self.label_limitB.setText("Limit [A]" if is_v else "Limit [V]")

    def _format_si(self, value: float, unit: str) -> str:
        """Formatiert mit SI-Suffix (m, k, u)."""
        if value == 0: return f"0.00 {unit}"
        abs_val = abs(value)
        if abs_val >= 1e3: return f"{value/1e3:.2f} k{unit}"
        if abs_val >= 1: return f"{value:.3f} {unit}"
        if abs_val >= 1e-3: return f"{value*1e3:.2f} m{unit}"
        if abs_val >= 1e-6: return f"{value*1e6:.2f} µ{unit}"
        return f"{value:.2e} {unit}"

    # --- Slots Inputs ---

    def on_level_A_changed(self):
        try: self.smu_mgr.set_source_level('a', float(self.lineEdit_levelA.text()))
        except: pass
    def on_limit_A_changed(self):
        try: self.smu_mgr.set_source_limit('a', float(self.lineEdit_limitA.text()))
        except: pass
    def on_level_B_changed(self):
        try: self.smu_mgr.set_source_level('b', float(self.lineEdit_levelB.text()))
        except: pass
    def on_limit_B_changed(self):
        try: self.smu_mgr.set_source_limit('b', float(self.lineEdit_limitB.text()))
        except: pass

    @Slot()
    def on_reset_A_clicked(self):
        self.smu_mgr.reset_channel('a')
        self.modelA.setRowCount(0)
        self.sync_ui_from_manager('a') # Reset -> State ändert sich -> UI Sync

    @Slot()
    def on_reset_B_clicked(self):
        self.smu_mgr.reset_channel('b')
        self.modelB.setRowCount(0)
        self.sync_ui_from_manager('b')

    @Slot(str, float, float)
    def on_new_measurement_acquired(self, ch, curr, volt):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        # Formatierung
        s_volt = self._format_si(volt, "V")
        s_curr = self._format_si(curr, "A")
        
        row = [QStandardItem(ts), QStandardItem(s_volt), QStandardItem(s_curr)]
        if ch == 'a':
            self.label_voltageA.setText(s_volt); self.label_currentA.setText(s_curr)
            self.modelA.insertRow(0, row)
        else:
            self.label_voltageB.setText(s_volt); self.label_currentB.setText(s_curr)
            self.modelB.insertRow(0, row)

    @Slot(list)
    def on_device_list_updated(self, ports):
        cur = self.comboBox_port.currentText()
        self.comboBox_port.clear()
        self.comboBox_port.addItems(ports)
        if self.smu_mgr.LastDevice in ports:
            self.comboBox_port.setCurrentText(self.smu_mgr.LastDevice)
        elif cur in ports:
            self.comboBox_port.setCurrentText(cur)

    @Slot()
    def on_connect_clicked(self):
        if self.smu_mgr.is_connected():
            self.smu_mgr.disconnect()
        else:
            self.smu_mgr.connect(self.comboBox_port.currentText())

    def eventFilter(self, watched, event):
        if watched == self.comboBox_port and event.type() == QEvent.Type.MouseButtonPress:
            if not self.comboBox_port.view().isVisible():
                self.smu_mgr.get_deviceList()
        return super().eventFilter(watched, event)