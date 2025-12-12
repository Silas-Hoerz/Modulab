# modules/smu/SmuWidget.py
# -*- coding: utf-8 -*-
import math
import time
from collections import deque
from PySide6.QtWidgets import (
    QWidget, QButtonGroup, QAbstractItemView, QHeaderView, QLabel
)
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PySide6.QtCore import Slot, QEvent, Qt, QDateTime, QTimer, QLocale

# Import UI
try:
    from .ui_SmuWidget import Ui_Form 
except ImportError:
    class Ui_Form:
        def setupUi(self, Form): pass

class SmuWidget(QWidget, Ui_Form):
    """
    SMU-UI mit Live-Statistiken.
    Styles werden komplett über das UI-File (tempState) gesteuert.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.smu_mgr = context.smu_manager
        self.log_mgr = context.log_manager

        # --- Interne Status-Variablen ---
        self.applied_state = {
            'a': {'func': 'V', 'sense': 'local', 'level': 0.0, 'limit': 0.1},
            'b': {'func': 'V', 'sense': 'local', 'level': 0.0, 'limit': 0.1}
        }

        self.expect_single_a = False
        self.expect_single_b = False
        
        # --- Statistik Variablen ---
        self.charge_A = 0.0
        self.charge_B = 0.0
        self.last_time_A = None
        self.last_time_B = None
        
        self.noise_buffer_A = deque(maxlen=10)
        self.noise_buffer_B = deque(maxlen=10)

        # Timer für Live-Monitoring
        self.monitor_timer = QTimer(self)
        self.monitor_timer.setInterval(250) 
        self.monitor_timer.timeout.connect(self._on_monitor_tick)

        self.__setup_ui()
        self.__connect_signals()
        
        if hasattr(self.smu_mgr, 'profile_mgr'):
             self.smu_mgr.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

        self.comboBox_port.installEventFilter(self)
        self.smu_mgr.get_deviceList()

    def __setup_ui(self):
        # 1. ButtonGroups
        self.bg_src_a = QButtonGroup(self); self.bg_src_a.addButton(self.pushButton_voltageA); self.bg_src_a.addButton(self.pushButton_currentA)
        self.bg_sns_a = QButtonGroup(self); self.bg_sns_a.addButton(self.pushButton_localA); self.bg_sns_a.addButton(self.pushButton_remoteA)
        
        self.bg_src_b = QButtonGroup(self); self.bg_src_b.addButton(self.pushButton_voltageB); self.bg_src_b.addButton(self.pushButton_currentB)
        self.bg_sns_b = QButtonGroup(self); self.bg_sns_b.addButton(self.pushButton_localB); self.bg_sns_b.addButton(self.pushButton_remoteB)

        # 2. Validator
        dval = QDoubleValidator()
        dval.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        for le in [self.lineEdit_levelA, self.lineEdit_limitA, self.lineEdit_levelB, self.lineEdit_limitB]:
            le.setValidator(dval)

        # 3. Tabellen
        self.modelA = QStandardItemModel(0, 3, self); self.modelA.setHorizontalHeaderLabels(["Time", "Volt", "Curr"])
        self.tableView_measurementsA.setModel(self.modelA)
        self.modelB = QStandardItemModel(0, 3, self); self.modelB.setHorizontalHeaderLabels(["Time", "Volt", "Curr"])
        self.tableView_measurementsB.setModel(self.modelB)
        
        for tv in [self.tableView_measurementsA, self.tableView_measurementsB]:
            tv.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            tv.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Initiale Styles
        self._update_output_style('a', False)
        self._update_output_style('b', False)
        self._reset_stats('a')
        self._reset_stats('b')
        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        # Manager -> UI
        self.smu_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.smu_mgr.device_list_updated.connect(self.on_device_list_updated)
        self.smu_mgr.new_measurement_acquired.connect(self.on_new_measurement_acquired)
        self.pushButton_connect.clicked.connect(self.on_connect_clicked)

        # Channel A
        self.bg_src_a.buttonClicked.connect(lambda: self._check_source_mode('a'))
        self.bg_sns_a.buttonClicked.connect(lambda: self._check_sense_mode('a'))
        self.lineEdit_levelA.textChanged.connect(lambda: self._check_value('a', 'level'))
        self.lineEdit_limitA.textChanged.connect(lambda: self._check_value('a', 'limit'))
        
        self.pushButton_applyA.clicked.connect(self.on_apply_A_clicked)
        self.pushButton_resetA.clicked.connect(self.on_reset_A_clicked)
        self.pushButton_outputA.clicked.connect(self.on_output_A_toggled)
        self.pushButton_singleA.clicked.connect(self.on_single_A_clicked)

        # Channel B
        self.bg_src_b.buttonClicked.connect(lambda: self._check_source_mode('b'))
        self.bg_sns_b.buttonClicked.connect(lambda: self._check_sense_mode('b'))
        self.lineEdit_levelB.textChanged.connect(lambda: self._check_value('b', 'level'))
        self.lineEdit_limitB.textChanged.connect(lambda: self._check_value('b', 'limit'))

        self.pushButton_applyB.clicked.connect(self.on_apply_B_clicked)
        self.pushButton_resetB.clicked.connect(self.on_reset_B_clicked)
        self.pushButton_outputB.clicked.connect(self.on_output_B_toggled)
        self.pushButton_singleB.clicked.connect(self.on_single_B_clicked)

    # --- Change Detection Logic ---

    def _set_warning(self, widget, is_warning: bool):
        # Wir nutzen 'tempState', genau wie im UI File definiert
        state = "warning" if is_warning else ""
        if widget.property("tempState") != state:
            widget.setProperty("tempState", state)
            widget.style().unpolish(widget); widget.style().polish(widget)

    def _check_source_mode(self, ch: str):
        btn_v = self.pushButton_voltageA if ch == 'a' else self.pushButton_voltageB
        btn_i = self.pushButton_currentA if ch == 'a' else self.pushButton_currentB
        applied = self.applied_state[ch]['func']
        is_v = btn_v.isChecked()
        
        self._set_warning(btn_v, is_v and applied != 'V')
        self._set_warning(btn_i, (not is_v) and applied != 'I')
        self._update_channel_labels(ch)

    def _check_sense_mode(self, ch: str):
        btn_loc = self.pushButton_localA if ch == 'a' else self.pushButton_localB
        btn_rem = self.pushButton_remoteA if ch == 'a' else self.pushButton_remoteB
        applied = self.applied_state[ch]['sense']
        is_loc = btn_loc.isChecked()

        self._set_warning(btn_loc, is_loc and applied != 'local')
        self._set_warning(btn_rem, (not is_loc) and applied != 'remote')

    def _check_value(self, ch: str, param: str):
        le = (self.lineEdit_levelA if ch == 'a' else self.lineEdit_levelB) if param == 'level' else \
             (self.lineEdit_limitA if ch == 'a' else self.lineEdit_limitB)
        applied = self.applied_state[ch][param]
        try:
            curr = float(le.text().replace(',', '.')) if le.text() else 0.0
            self._set_warning(le, abs(curr - applied) > 1e-6)
        except ValueError:
            self._set_warning(le, True)

    # --- Sync from Manager ---

    def sync_ui_from_manager(self, ch: str):
        state = self.smu_mgr.get_channel_state(ch)
        self.applied_state[ch].update(state) 
        self.applied_state[ch]['func'] = state['source_func'] 

        if ch == 'a':
            w = [self.pushButton_voltageA, self.pushButton_currentA, self.pushButton_localA, self.pushButton_remoteA, 
                 self.lineEdit_levelA, self.lineEdit_limitA, self.pushButton_outputA]
        else:
            w = [self.pushButton_voltageB, self.pushButton_currentB, self.pushButton_localB, self.pushButton_remoteB, 
                 self.lineEdit_levelB, self.lineEdit_limitB, self.pushButton_outputB]

        for x in w: x.blockSignals(True)

        if state['source_func'] == 'V': w[0].setChecked(True)
        else: w[1].setChecked(True)
        
        if state['sense'] == 'remote': w[3].setChecked(True)
        else: w[2].setChecked(True)
        
        w[4].setText(str(state['level']))
        w[5].setText(str(state['limit']))
        
        w[6].setChecked(state['output'])
        w[6].setText("ON" if state['output'] else "OFF")
        self._update_output_style(ch, state['output'])

        for x in w: x.blockSignals(False)

        self._check_source_mode(ch)
        self._check_sense_mode(ch)
        self._check_value(ch, 'level')
        self._check_value(ch, 'limit')
        self._update_channel_labels(ch)

    # --- Apply Logic ---

    def _apply_channel(self, ch, is_v, is_rem, level_text, limit_text):
        try:
            level = float(level_text.replace(',', '.')) if level_text else 0.0
            limit = float(limit_text.replace(',', '.')) if limit_text else 0.1
            
            if is_v: self.smu_mgr.set_source_voltage(ch)
            else: self.smu_mgr.set_source_current(ch)
            
            if is_rem: self.smu_mgr.set_sense_remote(ch)
            else: self.smu_mgr.set_sense_local(ch)
            
            self.smu_mgr.set_source_limit(ch, limit)
            self.smu_mgr.set_source_level(ch, level)
            
            self.sync_ui_from_manager(ch)
        except ValueError:
            self.log_mgr.error(f"Invalid number format in Channel {ch}")

    @Slot()
    def on_apply_A_clicked(self):
        self._apply_channel('a', self.pushButton_voltageA.isChecked(), self.pushButton_remoteA.isChecked(), 
                            self.lineEdit_levelA.text(), self.lineEdit_limitA.text())

    @Slot()
    def on_apply_B_clicked(self):
        self._apply_channel('b', self.pushButton_voltageB.isChecked(), self.pushButton_remoteB.isChecked(), 
                            self.lineEdit_levelB.text(), self.lineEdit_limitB.text())

    @Slot()
    def on_reset_A_clicked(self):
        self.pushButton_voltageA.setChecked(True); self.pushButton_localA.setChecked(True)
        self.lineEdit_levelA.setText("0.0"); self.lineEdit_limitA.setText("0.1")
        self._check_source_mode('a'); self._check_sense_mode('a'); self._check_value('a', 'level'); self._check_value('a', 'limit')

    @Slot()
    def on_reset_B_clicked(self):
        self.pushButton_voltageB.setChecked(True); self.pushButton_localB.setChecked(True)
        self.lineEdit_levelB.setText("0.0"); self.lineEdit_limitB.setText("0.1")
        self._check_source_mode('b'); self._check_sense_mode('b'); self._check_value('b', 'level'); self._check_value('b', 'limit')

    # --- Live Monitoring & Output ---

    @Slot()
    def on_output_A_toggled(self):
        state = self.pushButton_outputA.isChecked()
        self.pushButton_outputA.setText("ON" if state else "OFF")
        self.smu_mgr.set_output_state('a', state)
        self._update_output_style('a', state)
        if not state: self._reset_stats('a')
        self._check_monitor_timer()

    @Slot()
    def on_output_B_toggled(self):
        state = self.pushButton_outputB.isChecked()
        self.pushButton_outputB.setText("ON" if state else "OFF")
        self.smu_mgr.set_output_state('b', state)
        self._update_output_style('b', state)
        if not state: self._reset_stats('b')
        self._check_monitor_timer()

    def _update_output_style(self, ch: str, state: bool):
        """Setzt Style 'on'/'off' (via tempState) für Voltage, Current UND Stats Labels."""
        if ch == 'a':
            lbls = [self.label_voltageA, self.label_currentA, self.label_statsA]
        else:
            lbls = [self.label_voltageB, self.label_currentB, self.label_statsB]
            
        # WICHTIG: Hier nutzen wir jetzt 'tempState', wie im UI-File definiert!
        state_str = "on" if state else "off"
        for l in lbls:
            if l.property("tempState") != state_str:
                l.setProperty("tempState", state_str)
                l.style().unpolish(l); l.style().polish(l)

    def _reset_stats(self, ch):
        """Setzt Statistik-Variablen zurück."""
        placeholder = "P: -  |  R: -  |  Q: -  |  σ: -"
        if ch == 'a':
            self.charge_A = 0.0; self.last_time_A = None; self.noise_buffer_A.clear()
            self.label_statsA.setText(placeholder)
        else:
            self.charge_B = 0.0; self.last_time_B = None; self.noise_buffer_B.clear()
            self.label_statsB.setText(placeholder)

    def _check_monitor_timer(self):
        # Timer läuft immer, wenn verbunden (Always-On Monitoring)
        if self.smu_mgr.is_connected():
            if not self.monitor_timer.isActive(): self.monitor_timer.start()
        else:
            self.monitor_timer.stop()

    def _on_monitor_tick(self):
        if self.smu_mgr.is_connected():
            self.smu_mgr.measure_iv('a')
            self.smu_mgr.measure_iv('b')

    # --- Single Shot & Measurement Signals ---

    def on_single_A_clicked(self):
        self.expect_single_a = True
        self.smu_mgr.measure_iv('a')

    def on_single_B_clicked(self):
        self.expect_single_b = True
        self.smu_mgr.measure_iv('b')

    @Slot(str, float, float)
    def on_new_measurement_acquired(self, ch, curr, volt):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        s_volt = self._format_si(volt, "V")
        s_curr = self._format_si(curr, "A")
        
        # --- Statistik Berechnung ---
        now = time.time()
        power = abs(volt * curr)
        s_power = self._format_si(power, "W")
        
        res = abs(volt / curr) if abs(curr) > 1e-9 else float('inf')
        s_res = self._format_si(res, "Ω") if res != float('inf') else "Open"
        
        if ch == 'a':
            # Charge nur integrieren, wenn Output AN
            if self.pushButton_outputA.isChecked() and self.last_time_A:
                dt = now - self.last_time_A
                self.charge_A += curr * dt
            if self.pushButton_outputA.isChecked(): self.last_time_A = now
                
            s_charge = self._format_si(self.charge_A, "C")
            
            self.noise_buffer_A.append(curr)
            import statistics
            noise = statistics.stdev(self.noise_buffer_A) if len(self.noise_buffer_A) > 1 else 0.0
            s_noise = self._format_si(noise, "A_rms")

            self.label_voltageA.setText(s_volt); self.label_currentA.setText(s_curr)
            self.label_statsA.setText(f"P: {s_power}  |  R: {s_res}  |  Q: {s_charge}  |  σ: {s_noise}")
            
            if self.expect_single_a:
                self.modelA.insertRow(0, [QStandardItem(ts), QStandardItem(s_volt), QStandardItem(s_curr)])
                self.expect_single_a = False
        else:
            if self.pushButton_outputB.isChecked() and self.last_time_B:
                dt = now - self.last_time_B
                self.charge_B += curr * dt
            if self.pushButton_outputB.isChecked(): self.last_time_B = now

            s_charge = self._format_si(self.charge_B, "C")
            
            self.noise_buffer_B.append(curr)
            import statistics
            noise = statistics.stdev(self.noise_buffer_B) if len(self.noise_buffer_B) > 1 else 0.0
            s_noise = self._format_si(noise, "A_rms")

            self.label_voltageB.setText(s_volt); self.label_currentB.setText(s_curr)
            self.label_statsB.setText(f"P: {s_power}  |  R: {s_res}  |  Q: {s_charge}  |  σ: {s_noise}")
            
            if self.expect_single_b:
                self.modelB.insertRow(0, [QStandardItem(ts), QStandardItem(s_volt), QStandardItem(s_curr)])
                self.expect_single_b = False

    # --- Helpers ---

    def _set_channel_enabled(self, ch: str, en: bool):
        layout = self.gridLayout_channelA if ch == 'a' else self.gridLayout_channelB
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget(): item.widget().setEnabled(en)

    def _update_channel_labels(self, ch: str):
        is_v = (self.pushButton_voltageA if ch == 'a' else self.pushButton_voltageB).isChecked()
        le_lvl = self.label_levelA if ch == 'a' else self.label_levelB
        le_lim = self.label_limitA if ch == 'a' else self.label_limitB
        
        le_lvl.setText("Level [V]" if is_v else "Level [A]")
        le_lim.setText("Limit [A]" if is_v else "Limit [V]")

    def _format_si(self, value: float, unit: str) -> str:
        if value == 0: return f"0.00 {unit}"
        abs_val = abs(value)
        if abs_val >= 1e3: return f"{value/1e3:.2f} k{unit}"
        if abs_val >= 1: return f"{value:.3f} {unit}"
        if abs_val >= 1e-3: return f"{value*1e3:.2f} m{unit}"
        if abs_val >= 1e-6: return f"{value*1e6:.2f} µ{unit}"
        if abs_val >= 1e-9: return f"{value*1e9:.2f} n{unit}"
        return f"{value:.2e} {unit}"

    # --- Standard Slots ---

    @Slot(str)
    def on_profile_loaded(self, name):
        if self.smu_mgr.is_connected():
            self.sync_ui_from_manager('a'); self.sync_ui_from_manager('b')

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        if connected:
            self.label_status.setText(f"Connected"); self.label_status.setStyleSheet("color: green;")
            self.pushButton_connect.setText("Disconnect"); self.pushButton_connect.setChecked(True)
            self.comboBox_port.setEnabled(False)
            self._set_channel_enabled('a', True); self._set_channel_enabled('b', True)
            self.sync_ui_from_manager('a'); self.sync_ui_from_manager('b')
            # Timer starten für Always-On Monitoring
            self._check_monitor_timer()
        else:
            self.label_status.setText("Not Connected"); self.label_status.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect"); self.pushButton_connect.setChecked(False)
            self.comboBox_port.setEnabled(True)
            self._set_channel_enabled('a', False); self._set_channel_enabled('b', False)
            self.modelA.setRowCount(0); self.modelB.setRowCount(0)
            self.monitor_timer.stop()

    @Slot(list)
    def on_device_list_updated(self, ports):
        cur = self.comboBox_port.currentText()
        self.comboBox_port.clear()
        self.comboBox_port.addItems(ports)
        if self.smu_mgr.LastDevice in ports: self.comboBox_port.setCurrentText(self.smu_mgr.LastDevice)
        elif cur in ports: self.comboBox_port.setCurrentText(cur)

    @Slot()
    def on_connect_clicked(self):
        if self.smu_mgr.is_connected(): self.smu_mgr.disconnect()
        else: self.smu_mgr.connect(self.comboBox_port.currentText())

    def eventFilter(self, watched, event):
        if watched == self.comboBox_port and event.type() == QEvent.Type.MouseButtonPress:
            if not self.comboBox_port.view().isVisible(): self.smu_mgr.get_deviceList()
        return super().eventFilter(watched, event)