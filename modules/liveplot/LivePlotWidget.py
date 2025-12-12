import sys
import os
import numpy as np
import pyqtgraph as pg
from collections import deque

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QFileDialog, QSpinBox, QTabBar)
from PySide6.QtCore import Slot, Qt, QTimer

try:
    from .ui_LivePlotWidget import Ui_LivePlot 
except ImportError:
    class Ui_LivePlot:
        def setupUi(self, Form): pass

# ==============================================================================
# Helper: Multi-Plot Session Tab
# ==============================================================================
class SessionTabWidget(QWidget):
    def __init__(self, name, main_widget):
        super().__init__()
        self.main_widget = main_widget 
        self.session_name = name 
        
        # Grid Logic
        self.plot_items = {} # Key -> PlotItem
        self.curves = {}     # Key -> PlotDataItem
        self.next_row = 0
        self.next_col = 0
        
        # Layout
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.name_edit = QLineEdit(name)
        self.name_edit.textChanged.connect(self.update_tab_title)
        header.addWidget(QLabel("Measurement:"))
        header.addWidget(self.name_edit)
        layout.addLayout(header)

        # Graphics Container (Das Grid für die Plots)
        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground('k')
        layout.addWidget(self.glw)

        # Footer
        footer = QHBoxLayout()
        self.btn_export = QPushButton("Export All Plots in Session")
        self.btn_export.clicked.connect(self.on_export_clicked)
        footer.addStretch()
        footer.addWidget(self.btn_export)
        layout.addLayout(footer)

    def add_plot(self, key, title, xl, yl, log_x, log_y):
        """Erstellt einen neuen Plot im Grid."""
        # Neuer Plot
        p = self.glw.addPlot(row=self.next_row, col=self.next_col, title=title)
        p.setLabel('bottom', xl)
        p.setLabel('left', yl)
        p.showGrid(x=True, y=True, alpha=0.3)
        p.setLogMode(x=log_x, y=log_y)
        
        # Kurve
        curve = p.plot(pen=pg.mkPen('#ffff00', width=2), symbol='o', symbolSize=3)
        
        # Merken
        self.plot_items[key] = p
        self.curves[key] = curve
        
        # Grid weiterschalten (2 Spalten Layout)
        self.next_col += 1
        if self.next_col > 1:
            self.next_col = 0
            self.next_row += 1

    def update_curve(self, key, x, y, append=True):
        """Aktualisiert die Daten einer Kurve."""
        if key not in self.curves: return
        
        # Hinweis: Das Widget hält keine Datenkopie mehr (das macht der Manager).
        # Wir bekommen hier direkt die Daten zum Zeichnen (bei Append allerdings nur den Punkt).
        # Da wir für Append den ganzen Verlauf brauchen, holen wir ihn aus dem Manager Cache?
        # NEIN -> Performance. 
        # BESSER: Das Widget hält DOCH einen lokalen Cache für die Visualisierung.
        
        if not hasattr(self, 'local_data_cache'):
            self.local_data_cache = {}
            
        if key not in self.local_data_cache:
            self.local_data_cache[key] = {'x': [], 'y': []}
            
        if append:
            self.local_data_cache[key]['x'].append(x)
            self.local_data_cache[key]['y'].append(y)
            self.curves[key].setData(self.local_data_cache[key]['x'], self.local_data_cache[key]['y'])
        else:
            # Replace Mode (Spectrum)
            self.curves[key].setData(x, y)
            # Cache updaten (für Export via Widget falls nötig, sonst via Manager)
            self.local_data_cache[key]['x'] = x
            self.local_data_cache[key]['y'] = y

    def update_tab_title(self, new_text):
        idx = self.main_widget.tabWidget.indexOf(self)
        if idx != -1: self.main_widget.tabWidget.setTabText(idx, new_text)

    def on_export_clicked(self):
        # Wir holen die Daten lieber frisch aus dem Manager, da dort die "Wahrheit" liegt
        mgr_data = self.main_widget.plot_mgr.active_sessions.get(self.session_name, {})
        
        # Aber wir brauchen den Dateinamen
        profile = self.main_widget.context.profile_manager
        export_mgr = self.main_widget.context.export_manager
        last_dir = profile.read("Export_LastDir") or os.path.expanduser("~")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Session", os.path.join(last_dir, f"{self.name_edit.text()}.h5"), "HDF5 Files (*.h5)"
        )
        
        if file_path:
            # Multi-Dataset Export via ExportManager
            # Wir müssen das Format etwas anpassen für den ExportManager
            # Hier ist ein Custom Export sinnvoll:
            import h5py
            from datetime import datetime
            
            try:
                with h5py.File(file_path, 'w') as f:
                    f.attrs['Export_Date'] = datetime.now().isoformat()
                    
                    for plot_key, plot_data in mgr_data.items():
                        g = f.create_group(plot_key)
                        g.create_dataset('x', data=plot_data['x'])
                        g.create_dataset('y', data=plot_data['y'])
                
                self.main_widget.log_mgr.info(f"Session exported to {file_path}")
            except Exception as e:
                self.main_widget.log_mgr.error(f"Export failed: {e}")


# ==============================================================================
# Haupt-Widget
# ==============================================================================
class LivePlotWidget(QWidget, Ui_LivePlot):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.context = context 
        self.plot_mgr = context.liveplot_manager
        self.log_mgr = context.log_manager
        
        self.tabWidget.clear()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)

        self.__setup_dashboard_tab()
        self.active_session_widgets = {}

        # Signale
        self.plot_mgr.monitor_updated.connect(self.on_monitor_updated)
        self.plot_mgr.spectrum_updated.connect(self.on_spectrum_updated)
        
        # Session Signale
        self.plot_mgr.session_started.connect(self.on_session_started)
        self.plot_mgr.plot_defined.connect(self.on_plot_defined)
        self.plot_mgr.data_appended.connect(self.on_data_appended)
        self.plot_mgr.data_set.connect(self.on_data_set)
        
        if hasattr(self.context.profile_manager, 'profile_loaded'):
             self.context.profile_manager.profile_loaded.connect(self.on_profile_loaded)

        self.spinBox_history.setValue(self.plot_mgr.monitor_maxlen)

        # Dashboard Timer
        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.setInterval(33)
        self.dashboard_timer.timeout.connect(self._refresh_dashboard_plots)
        self.dashboard_timer.start()
        
        self._pending_monitor_data = None
        self._pending_spectrum_data = None

    def __setup_dashboard_tab(self):
        """Monitor Dashboard."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        layout.setContentsMargins(0,0,0,0)

        toolbar = QHBoxLayout()
        lbl_hist = QLabel("<b>History Points:</b>")
        self.spinBox_history = QSpinBox()
        self.spinBox_history.setRange(100, 100000)
        self.spinBox_history.setSingleStep(100)
        self.spinBox_history.setSuffix(" pts")
        self.spinBox_history.valueChanged.connect(self.on_history_size_changed)
        toolbar.addWidget(lbl_hist); toolbar.addWidget(self.spinBox_history); toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.dash_layout = pg.GraphicsLayoutWidget()
        self.dash_layout.setBackground('k')
        layout.addWidget(self.dash_layout)
        
        # Plots (Monitor)
        self.p_volt = self.dash_layout.addPlot(row=0, col=0, title="Voltage")
        self.p_volt.setLabel('left', "V", units='V')
        self.p_volt.addLegend()
        self.curve_volt_a = self.p_volt.plot(pen='c', name="Ch A")
        self.curve_volt_b = self.p_volt.plot(pen='m', name="Ch B")

        self.p_curr = self.dash_layout.addPlot(row=0, col=1, title="Current")
        self.p_curr.setLabel('left', "I", units='A')
        self.p_curr.addLegend()
        self.curve_curr_a = self.p_curr.plot(pen='c', name="Ch A")
        self.curve_curr_b = self.p_curr.plot(pen='m', name="Ch B")

        self.p_log = self.dash_layout.addPlot(row=1, col=0, title="Log Current")
        self.p_log.setLabel('left', "Log(|I|)", units='A')
        self.p_log.setLogMode(y=True)
        self.p_log.addLegend()
        self.curve_log_a = self.p_log.plot(pen='c', name="Ch A")
        self.curve_log_b = self.p_log.plot(pen='m', name="Ch B")

        self.p_spec = self.dash_layout.addPlot(row=1, col=1, title="Spectrum")
        self.p_spec.setLabel('bottom', "nm")
        self.curve_spec = self.p_spec.plot(pen='#00ff00')
        self.curve_spec.setBrush(pg.mkBrush(color=(0, 255, 0, 50)))
        self.curve_spec.setFillLevel(0)

        idx = self.tabWidget.addTab(dashboard_widget, "Dashboard")
        self.tabWidget.tabBar().setTabButton(idx, QTabBar.RightSide, None)

    # --- Slots ---
    @Slot(int)
    def on_history_size_changed(self, val):
        self.plot_mgr.set_monitor_buffer_size(val)

    @Slot(int)
    def on_tab_close_requested(self, index):
        if index == 0: return
        widget = self.tabWidget.widget(index)
        if isinstance(widget, SessionTabWidget):
            self.plot_mgr.remove_session(widget.session_name)
            if widget.session_name in self.active_session_widgets:
                del self.active_session_widgets[widget.session_name]
        self.tabWidget.removeTab(index)
        widget.deleteLater()

    # --- Dashboard Logic ---
    @Slot(dict)
    def on_monitor_updated(self, data):
        self._pending_monitor_data = data

    @Slot(object, object)
    def on_spectrum_updated(self, wl, intens):
        self._pending_spectrum_data = (wl, intens)

    def _refresh_dashboard_plots(self):
        if self._pending_monitor_data:
            data = self._pending_monitor_data
            def to_np(d): return np.array(d)
            if 'a' in data and len(data['a']['v']) > 0:
                self.curve_volt_a.setData(to_np(data['a']['v']))
                self.curve_curr_a.setData(to_np(data['a']['i']))
                self.curve_log_a.setData(np.abs(to_np(data['a']['i'])) + 1e-15)
            if 'b' in data and len(data['b']['v']) > 0:
                self.curve_volt_b.setData(to_np(data['b']['v']))
                self.curve_curr_b.setData(to_np(data['b']['i']))
                self.curve_log_b.setData(np.abs(to_np(data['b']['i'])) + 1e-15)
            self._pending_monitor_data = None

        if self._pending_spectrum_data:
            wl, intens = self._pending_spectrum_data
            if wl and intens is not None: self.curve_spec.setData(wl, intens)
            self._pending_spectrum_data = None

    @Slot(str)
    def on_profile_loaded(self, name):
        self.spinBox_history.blockSignals(True)
        self.spinBox_history.setValue(self.plot_mgr.monitor_maxlen)
        self.spinBox_history.blockSignals(False)

    # --- Session Logic (Multi-Plot) ---

    @Slot(str)
    def on_session_started(self, name):
        tab = SessionTabWidget(name, self)
        idx = self.tabWidget.addTab(tab, name)
        self.tabWidget.setCurrentIndex(idx)
        self.active_session_widgets[name] = tab

    @Slot(str, str, str, str, str, bool, bool)
    def on_plot_defined(self, session, key, title, xl, yl, logx, logy):
        if session in self.active_session_widgets:
            self.active_session_widgets[session].add_plot(key, title, xl, yl, logx, logy)

    @Slot(str, str, float, float)
    def on_data_appended(self, session, key, x, y):
        if session in self.active_session_widgets:
            self.active_session_widgets[session].update_curve(key, x, y, append=True)

    @Slot(str, str, object, object)
    def on_data_set(self, session, key, x, y):
        if session in self.active_session_widgets:
            self.active_session_widgets[session].update_curve(key, x, y, append=False)