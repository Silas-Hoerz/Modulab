# modules/sweep/SweepWidget.py
# -*- coding: utf-8 -*-
import os
import numpy as np
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QButtonGroup, QComboBox
from PySide6.QtCore import Slot, Qt, Signal

try:
    from .ui_SweepWidget import Ui_Sweep 
except ImportError:
    class Ui_Sweep:
        def setupUi(self, Form): pass

class SweepGenerator:
    @staticmethod
    def generate(mode, start, end, steps, custom_str=""):
        try:
            if mode == "Linear Single":
                return np.linspace(start, end, steps)
            elif mode == "Linear Dual":
                fwd = np.linspace(start, end, steps)
                bwd = np.linspace(end, start, steps)
                return np.concatenate((fwd, bwd))
            elif mode == "Logarithmic":
                if start == 0: start = 1e-6
                if end == 0: end = 1e-6
                if np.sign(start) != np.sign(end): return np.linspace(start, end, steps)
                return np.logspace(np.log10(abs(start)), np.log10(abs(end)), steps) * np.sign(start)
            elif mode == "Custom List":
                clean_str = custom_str.replace('\n', ',').replace(';', ',')
                parts = [float(x.strip()) for x in clean_str.split(',') if x.strip()]
                return np.array(parts)
        except Exception:
            return np.array([0.0])
        return np.array([0.0])

class SweepWidget(QWidget, Ui_Sweep):
    
    sig_progress = Signal(int, float)

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.context = context
        self.log = context.log_manager
        self.profile = context.profile_manager
        
        self.is_running = False
        self.is_paused = False
        self._loading = False 

        # --- 1. Preview Graph ---
        layout = QVBoxLayout(self.widget_preview)
        layout.setContentsMargins(0,0,0,0)
        self.plot_preview = pg.PlotWidget()
        self.plot_preview.setBackground('k')
        self.plot_preview.showGrid(x=True, y=True, alpha=0.3)
        self.plot_preview.setMouseEnabled(x=False, y=False)
        self.plot_preview.hideButtons()
        self.plot_preview.setLabel('left', 'Source Level')
        
        self.curve_plan = self.plot_preview.plot(pen=pg.mkPen('#666666', width=2, style=Qt.DashLine))
        self.curve_done = self.plot_preview.plot(pen=pg.mkPen('#ffff00', width=2))
        self.scat_curr = self.plot_preview.plot(symbol='o', symbolBrush='#ffff00', symbolSize=10, pen=None)
        layout.addWidget(self.plot_preview)

        # --- 2. Button Groups ---
        self.bg_channel = QButtonGroup(self)
        self.bg_channel.addButton(self.pushButton_channelA); self.bg_channel.addButton(self.pushButton_channelB)
        self.bg_channel.setExclusive(True)

        self.bg_source = QButtonGroup(self)
        self.bg_source.addButton(self.pushButton_voltage); self.bg_source.addButton(self.pushButton_current)
        self.bg_source.setExclusive(True)

        self.bg_term = QButtonGroup(self)
        self.bg_term.addButton(self.pushButton_returnZero); self.bg_term.addButton(self.pushButton_holdFinal)
        self.bg_term.setExclusive(True)

        # --- 3. Events ---
        self.comboBox_mode.currentIndexChanged.connect(self._on_config_changed)
        self.pushButton_voltage.clicked.connect(self._on_source_changed)
        self.pushButton_current.clicked.connect(self._on_source_changed)
        self.pushButton_loadCustom.clicked.connect(self._load_custom_file)
        self.pushButton_saveCustom.clicked.connect(self._save_custom_file)
        
        for w in [self.doubleSpinBox_start, self.doubleSpinBox_end, self.spinBox_steps, 
                  self.plainTextEdit_customPoints, self.doubleSpinBox_delay, self.doubleSpinBox_delayCustom]:
            if hasattr(w, 'valueChanged'): w.valueChanged.connect(self._update_preview_data)
            elif hasattr(w, 'textChanged'): w.textChanged.connect(self._update_preview_data)
        self.comboBox_mode.currentIndexChanged.connect(self._update_preview_data)

        self.pushButton_start_pause.clicked.connect(self.on_start_pause_clicked)
        self.pushButton_stop.clicked.connect(self.on_stop_clicked)
        
        self.sig_progress.connect(self._on_worker_progress)
        self.context.experiment_manager.experiment_finished.connect(self._on_experiment_finished_signal)

        # Settings Save Connect
        self._connect_save_triggers()

        # Init UI
        self._on_source_changed()
        self._on_config_changed()
        
        # Load Profile
        if self.profile.get_current_profile_name():
            self.load_settings(self.profile.get_current_profile_name())
        
        if hasattr(self.profile, 'profile_loaded'):
            self.profile.profile_loaded.connect(self.load_settings)

        self._update_preview_data()

    # --- File Logic ---
    def _get_custom_dir(self):
        base = os.path.join(os.path.expanduser("~"), "Modulab", "CustomSweeps")
        if not os.path.exists(base): os.makedirs(base, exist_ok=True)
        return base

    def _load_custom_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Sweep List", self._get_custom_dir(), "Text/CSV (*.txt *.csv)")
        if fname:
            try:
                with open(fname, 'r') as f: self.plainTextEdit_customPoints.setPlainText(f.read())
            except Exception as e: self.log.error(f"Could not load file: {e}")

    def _save_custom_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Sweep List", self._get_custom_dir(), "Text/CSV (*.txt *.csv)")
        if fname:
            try:
                with open(fname, 'w') as f: f.write(self.plainTextEdit_customPoints.toPlainText())
            except Exception as e: self.log.error(f"Could not save file: {e}")

    # --- Profile Logic ---
    def _connect_save_triggers(self):
        widgets = [self.doubleSpinBox_start, self.doubleSpinBox_end, self.spinBox_steps,
                   self.doubleSpinBox_limit, self.doubleSpinBox_delay, self.doubleSpinBox_delayCustom, 
                   self.comboBox_mode]
        for w in widgets:
            if hasattr(w, 'valueChanged'): w.valueChanged.connect(self.save_settings)
            if hasattr(w, 'currentIndexChanged'): w.currentIndexChanged.connect(self.save_settings)
        
        self.bg_channel.buttonClicked.connect(self.save_settings)
        self.bg_source.buttonClicked.connect(self.save_settings)
        self.bg_term.buttonClicked.connect(self.save_settings)
        self.plainTextEdit_customPoints.textChanged.connect(self.save_settings)

    @Slot()
    def save_settings(self):
        if self._loading: return 
        p = self.profile
        if not p.get_current_profile_name(): return

        p.write("Sweep_Start", self.doubleSpinBox_start.value())
        p.write("Sweep_End", self.doubleSpinBox_end.value())
        p.write("Sweep_Steps", self.spinBox_steps.value())
        p.write("Sweep_Limit", self.doubleSpinBox_limit.value())
        p.write("Sweep_Delay", self.doubleSpinBox_delay.value())
        p.write("Sweep_DelayCustom", self.doubleSpinBox_delayCustom.value())
        p.write("Sweep_Mode_Index", self.comboBox_mode.currentIndex())
        p.write("Sweep_Custom_Text", self.plainTextEdit_customPoints.toPlainText())
        p.write("Sweep_Is_ChB", self.pushButton_channelB.isChecked())
        p.write("Sweep_Is_CurrentSrc", self.pushButton_current.isChecked())
        p.write("Sweep_Is_Hold", self.pushButton_holdFinal.isChecked())

    @Slot(str)
    def load_settings(self, profile_name):
        p = self.profile
        self._loading = True
        try:
            def set_val(key, widget, cast=float):
                val = p.read(key)
                if val is not None:
                    if isinstance(widget, QComboBox): widget.setCurrentIndex(int(val))
                    elif hasattr(widget, 'setValue'): widget.setValue(cast(val))
                    elif hasattr(widget, 'setPlainText'): widget.setPlainText(str(val))

            set_val("Sweep_Start", self.doubleSpinBox_start)
            set_val("Sweep_End", self.doubleSpinBox_end)
            set_val("Sweep_Steps", self.spinBox_steps, int)
            set_val("Sweep_Limit", self.doubleSpinBox_limit)
            set_val("Sweep_Delay", self.doubleSpinBox_delay)
            set_val("Sweep_DelayCustom", self.doubleSpinBox_delayCustom)
            set_val("Sweep_Mode_Index", self.comboBox_mode, int)
            set_val("Sweep_Custom_Text", self.plainTextEdit_customPoints, str)

            if p.read("Sweep_Is_ChB"): self.pushButton_channelB.setChecked(True)
            else: self.pushButton_channelA.setChecked(True)

            if p.read("Sweep_Is_CurrentSrc"): self.pushButton_current.setChecked(True)
            else: self.pushButton_voltage.setChecked(True)

            if p.read("Sweep_Is_Hold"): self.pushButton_holdFinal.setChecked(True)
            else: self.pushButton_returnZero.setChecked(True)
            
            self._on_config_changed()
            self._on_source_changed()
            self._update_preview_data()

        except Exception as e:
            self.log.error(f"Error loading Sweep settings: {e}")
        finally:
            self._loading = False

    # --- UI Logic ---
    def _on_config_changed(self):
        mode = self.comboBox_mode.currentText()
        is_custom = (mode == "Custom List")
        self.widget_StandardPage.setVisible(not is_custom)
        self.widget_customPage.setVisible(is_custom)
        self._update_preview_data()

    def _on_source_changed(self):
        is_volt = self.pushButton_voltage.isChecked()
        u_src = " V" if is_volt else " A"
        u_lim = " A" if is_volt else " V"
        self.doubleSpinBox_start.setSuffix(u_src)
        self.doubleSpinBox_end.setSuffix(u_src)
        self.doubleSpinBox_limit.setSuffix(u_lim)
        self.plot_preview.setLabel('left', "Voltage" if is_volt else "Current", units='V' if is_volt else 'A')

    # --- Preview Logic ---
    def _get_current_points(self):
        return SweepGenerator.generate(
            mode=self.comboBox_mode.currentText(),
            start=self.doubleSpinBox_start.value(),
            end=self.doubleSpinBox_end.value(),
            steps=self.spinBox_steps.value(),
            custom_str=self.plainTextEdit_customPoints.toPlainText()
        )

    def _update_preview_data(self):
        points = self._get_current_points()
        if len(points) > 0:
            x = np.arange(len(points))
            self.curve_plan.setData(x, points)
            self.curve_done.setData([], [])
            self.scat_curr.setData([], [])
            self.progressBar.setMaximum(len(points))

    # --- Execution Logic ---
    @Slot()
    def on_start_pause_clicked(self):
        if self.context.experiment_manager.is_experiment_running() and self.is_running:
            if self.is_paused:
                self.context.experiment_manager.resume_experiment()
                self.pushButton_start_pause.setText("Pause")
                self.is_paused = False
            else:
                self.context.experiment_manager.pause_experiment()
                self.pushButton_start_pause.setText("Resume")
                self.is_paused = True
            return

        self._start_sweep()

    @Slot()
    def on_stop_clicked(self):
        self.context.experiment_manager.stop_experiment()
        self.pushButton_start_pause.setEnabled(False) 

    def _start_sweep(self):
        points = self._get_current_points()
        if len(points) == 0: return

        is_custom = (self.comboBox_mode.currentText() == "Custom List")
        delay_val = self.doubleSpinBox_delayCustom.value() if is_custom else self.doubleSpinBox_delay.value()

        # Metadata für den Export vorbereiten
        cfg = {
            'channel': 'a' if self.pushButton_channelA.isChecked() else 'b',
            'limit': self.doubleSpinBox_limit.value(),
            'delay': delay_val,
            'return_zero': self.pushButton_returnZero.isChecked(),
            'source_mode': 'V' if self.pushButton_voltage.isChecked() else 'I',
            'session_name': f"Sweep {time.strftime('%H_%M_%S')}"
        }

        # Device Infos holen
        dut_name = "Unknown"
        if hasattr(self.context, 'device_manager'):
             dev = self.context.device_manager.get_active_device()
             if dev: dut_name = dev.name
        cfg['dut'] = dut_name

        self.widget_configuration.setEnabled(False)
        self.widget_StandardPage.setEnabled(False)
        self.widget_customPage.setEnabled(False)
        self.widget_execution.setEnabled(True)
        
        self.pushButton_start_pause.setText("Pause")
        self.pushButton_start_pause.setChecked(True)
        self.pushButton_stop.setEnabled(True)
        self.progressBar.setValue(0)
        self.curve_done.setData([], [])
        
        self.is_running = True
        self.is_paused = False

        self.context.experiment_manager.run_custom_function(
            _worker_sweep_routine,
            points=points,
            cfg=cfg,
            progress_signal=self.sig_progress
        )

    @Slot(int, float)
    def _on_worker_progress(self, idx, val):
        self.progressBar.setValue(idx + 1)
        all_points = self.curve_plan.yData
        if all_points is not None and idx < len(all_points):
             self.curve_done.setData(np.arange(idx+1), all_points[:idx+1])
             self.scat_curr.setData([idx], [all_points[idx]])

    @Slot()
    def _on_experiment_finished_signal(self):
        if not self.is_running: return 
        self.widget_configuration.setEnabled(True)
        self.widget_StandardPage.setEnabled(True)
        self.widget_customPage.setEnabled(True)
        self.pushButton_start_pause.setText("Start")
        self.pushButton_start_pause.setChecked(False)
        self.pushButton_start_pause.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.scat_curr.setData([], [])
        self.is_running = False
        self.is_paused = False

# ==============================================================================
# WORKER FUNCTION
# ==============================================================================
def _worker_sweep_routine(api, points, cfg, progress_signal):
    """
    Führt den Sweep aus und sendet Daten an den ExportManager.
    """
    log = api.log_mgr
    smu = api.smu_mgr
    spec = api.spectrometer_mgr
    data_mgr = api.export_mgr
    
    ch = cfg['channel']
    sess_name = cfg['session_name']
    
    log.info(f"Starting Sweep '{sess_name}' ({len(points)} pts)...")
    if not smu.is_connected(): smu.connect("DUMMY")

    # 1. Session starten (RAM Buffer anlegen)
    metadata = {
        "Source": cfg['source_mode'],
        "Limit": cfg['limit'],
        "Delay": cfg['delay'],
        "Channel": ch,
        "DUT": cfg.get('dut', 'Unknown')
    }
    data_mgr.start_session(sess_name, metadata)

    # 2. Hardware Config
    smu.reset_channel(ch)
    if cfg['source_mode'] == 'V':
        smu.set_source_voltage(ch)
    else:
        smu.set_source_current(ch)
        
    smu.set_source_limit(ch, cfg['limit'])
    smu.set_output_state(ch, True)

    try:
        for i, val in enumerate(points):
            # Check Stop
            if api._is_stopped: 
                log.info("Sweep stopped by user.")
                break
            
            # Check Pause
            while api._is_paused: 
                if api._is_stopped: break 
                time.sleep(0.1)
            if api._is_stopped: break

            # A. Source setzen
            smu.set_source_level(ch, val)
            
            # B. Warten (Delay)
            delay_left = cfg['delay']
            while delay_left > 0:
                if api._is_stopped: break
                step = min(0.1, delay_left)
                time.sleep(step)
                delay_left -= step
            if api._is_stopped: break

            # C. Messen
            meas_i, meas_v = smu.measure_iv(ch) or (0.0, 0.0)
            
            # D. Spektrum
            spectrum_corr = None
            wl = None
            if spec.is_connected():
                wl, spectrum_corr = spec.acquire_spectrum()

            # E. Daten zentral speichern (Löst Live-Plot aus)
            data_mgr.add_data_point(
                session_name=sess_name,
                set_val=val,
                meas_v=meas_v,
                meas_i=meas_i,
                spectrum=spectrum_corr,
                wl=wl
            )
            
            progress_signal.emit(i, val)

    except Exception as e:
        log.error(f"Sweep crashed: {e}")
        
    finally:
        if cfg['return_zero']:
            smu.set_source_level(ch, 0)
            smu.set_output_state(ch, False)
        log.info("Sweep finished.")