import sys
import os
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QFileDialog, QSizePolicy, 
                               QSpinBox, QTabBar) # Checkbox entfernt
from PySide6.QtCore import Slot, Qt, QTimer

# Import UI Handling
try:
    from .ui_LivePlotWidget import Ui_LivePlot 
except ImportError:
    try:
        from ui_LivePlotWidget import Ui_LivePlot
    except ImportError:
        class Ui_LivePlot:
            def setupUi(self, Form): pass

# ==============================================================================
# Session Tab Widget (Ein Tab pro Messung)
# ==============================================================================
class SessionTabWidget(QWidget):
    def __init__(self, name, main_widget):
        super().__init__()
        self.main_widget = main_widget 
        self.session_name = name 
        
        self.plot_items = {} 
        self.curves = {}     
        self.next_row = 0; self.next_col = 0
        self.local_data_cache = {}

        # Layout Setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("Measurement:"))
        self.name_edit = QLineEdit(name)
        self.name_edit.setReadOnly(True)
        header.addWidget(self.name_edit)
        layout.addLayout(header)

        self.glw = pg.GraphicsLayoutWidget()
        self.glw.setBackground('k')
        layout.addWidget(self.glw)

        # Footer mit Export Button
        footer = QHBoxLayout()
        self.btn_export = QPushButton("Export Measurement...")
        self.btn_export.clicked.connect(self.on_export_clicked)
        footer.addStretch()
        footer.addWidget(self.btn_export)
        layout.addLayout(footer)

    def add_plot(self, key, title, xl, yl, log_x, log_y):
        if key in self.plot_items: return
        p = self.glw.addPlot(row=self.next_row, col=self.next_col, title=title)
        p.setLabel('bottom', xl); p.setLabel('left', yl)
        p.showGrid(x=True, y=True, alpha=0.3); p.setLogMode(x=log_x, y=log_y)
        p.addLegend(offset=(10, 10))
        curve = p.plot(pen=pg.mkPen('#ffff00', width=2), symbol='o', symbolSize=3, name="Data")
        self.plot_items[key] = p; self.curves[key] = curve
        self.local_data_cache[key] = {'x': [], 'y': []}
        
        self.next_col += 1
        if self.next_col > 1:
            self.next_col = 0; self.next_row += 1

    def update_curve(self, key, x, y, append=True):
        if key not in self.curves: return
        if append:
            self.local_data_cache[key]['x'].append(x)
            self.local_data_cache[key]['y'].append(y)
            self.curves[key].setData(self.local_data_cache[key]['x'], self.local_data_cache[key]['y'])
        else:
            self.curves[key].setData(x, y)

    def on_export_clicked(self):
        profile = self.main_widget.context.profile_manager
        default_dir = profile.read("Export_LastDir") or os.path.expanduser("~")
        default_file = os.path.join(default_dir, f"{self.session_name}.h5")
        filter_str = "HDF5 Files (*.h5);;CSV Files (*.csv)"
        
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Measurement Data", default_file, filter_str)
        if filepath:
            self.main_widget.export_mgr.save_session_to_disk(self.session_name, filepath)


# ==============================================================================
# LivePlotWidget Main Class
# ==============================================================================
class LivePlotWidget(QWidget, Ui_LivePlot):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self) 
        
        self.context = context 
        self.plot_mgr = context.liveplot_manager
        self.export_mgr = context.export_manager 
        self.log_mgr = context.log_manager
        
        self.tabWidget.clear()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)

        # Dashboard aufbauen
        self.__setup_dashboard_tab()
        
        self.active_session_widgets = {}

        # Signale verbinden
        self.plot_mgr.monitor_updated.connect(self.on_monitor_updated)
        self.plot_mgr.spectrum_updated.connect(self.on_spectrum_updated)
        self.export_mgr.session_updated.connect(self.on_session_data_updated)
        
        if hasattr(self.context.profile_manager, 'profile_loaded'):
             self.context.profile_manager.profile_loaded.connect(self.on_profile_loaded)

        if hasattr(self, 'spinBox_history'):
            self.spinBox_history.setValue(self.plot_mgr.monitor_maxlen)

        # Timer
        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.setInterval(33)
        self.dashboard_timer.timeout.connect(self._refresh_dashboard_plots)
        self.dashboard_timer.start()
        
        self._pending_monitor_data = None
        self._pending_spectrum_data = None

    def __setup_dashboard_tab(self):
        """Erstellt das Dashboard."""
        d_widget = QWidget()
        lay = QVBoxLayout(d_widget)
        lay.setContentsMargins(0,0,0,0)

        # --- TOOLBAR (Nur History Spinbox) ---
        tb_layout = QHBoxLayout()
        lbl_hist = QLabel("History Points:")
        self.spinBox_history = QSpinBox()
        self.spinBox_history.setRange(100, 100000)
        self.spinBox_history.setSingleStep(100)
        self.spinBox_history.valueChanged.connect(self.on_history_size_changed)
        
        tb_layout.addWidget(lbl_hist)
        tb_layout.addWidget(self.spinBox_history)
        tb_layout.addStretch() 
        lay.addLayout(tb_layout)
        
        # --- PLOTS ---
        self.dl = pg.GraphicsLayoutWidget()
        self.dl.setBackground('k')
        lay.addWidget(self.dl)
        
        # 2x2 Layout
        
        # 1. Voltage
        self.p_v = self.dl.addPlot(row=0, col=0, title="Voltage Monitor")
        self.p_v.setLabel('left', "V")
        self.p_v.showGrid(x=True, y=True, alpha=0.3)
        self.p_v.addLegend() # Legend nötig für Interaktion
        self.c_v_a = self.p_v.plot(pen='c', name="Ch A")
        self.c_v_b = self.p_v.plot(pen='m', name="Ch B")
        self._make_legend_interactive(self.p_v) # <--- INTERACTIVE
        
        # 2. Current Linear
        self.p_c = self.dl.addPlot(row=0, col=1, title="Current Monitor (Linear)")
        self.p_c.setLabel('left', "I")
        self.p_c.showGrid(x=True, y=True, alpha=0.3)
        self.p_c.addLegend()
        self.c_c_a = self.p_c.plot(pen='c', name="Ch A")
        self.c_c_b = self.p_c.plot(pen='m', name="Ch B")
        self._make_legend_interactive(self.p_c) # <--- INTERACTIVE
        
        # 3. Current Log
        self.p_log = self.dl.addPlot(row=1, col=0, title="Current Monitor (Log)")
        self.p_log.setLabel('left', "I (Log)", units='A')
        self.p_log.setLogMode(y=True) 
        self.p_log.showGrid(x=True, y=True, alpha=0.3)
        self.p_log.addLegend()
        self.c_log_a = self.p_log.plot(pen='c', name="Ch A")
        self.c_log_b = self.p_log.plot(pen='m', name="Ch B")
        self._make_legend_interactive(self.p_log) # <--- INTERACTIVE

        # 4. Spectrum
        self.p_s = self.dl.addPlot(row=1, col=1, title="Live Spectrum")
        self.p_s.setLabel('bottom', "nm")
        self.p_s.showGrid(x=True, y=True, alpha=0.3)
        self.c_s = self.p_s.plot(pen='#00ff00', fillLevel=0, brush=(0,255,0,50))

        idx = self.tabWidget.addTab(d_widget, "Dashboard")
        self.tabWidget.tabBar().setTabButton(idx, QTabBar.RightSide, None)

    # --- Feature: Clickable Legend ---
    
    def _make_legend_interactive(self, plot_item):
        """
        Macht die Legende anklickbar, um Kurven ein/auszuschalten.
        """
        legend = plot_item.legend
        if not legend: return

        # Wir iterieren über die Items in der Legende
        # pyqtgraph legend.items ist eine Liste von (sample, label)
        for sample, label in legend.items:
            # Das 'sample' Objekt hält eine Referenz auf das PlotItem (die Kurve)
            curve_item = sample.item 
            
            # Wir definieren eine Click-Funktion via Closure, um curve_item zu binden
            def create_click_handler(c_item, l_item, s_item):
                def click_handler(ev):
                    # Toggle Visibility
                    new_state = not c_item.isVisible()
                    c_item.setVisible(new_state)
                    
                    # Visuelles Feedback: Text und Linie dimmen wenn inaktiv
                    opacity = 1.0 if new_state else 0.3
                    l_item.setOpacity(opacity)
                    s_item.setOpacity(opacity)
                    
                    # Event akzeptieren (wichtig für PyQt)
                    ev.accept()
                return click_handler

            # Funktion erstellen
            handler = create_click_handler(curve_item, label, sample)
            
            # Monkey-Patching: Wir überschreiben das mousePressEvent des Labels und des Samples
            label.mousePressEvent = handler
            sample.mousePressEvent = handler

    # --- Slots ---
    @Slot(int)
    def on_history_size_changed(self, val): 
        self.plot_mgr.set_monitor_buffer_size(val)

    @Slot(int)
    def on_tab_close_requested(self, index):
        if index == 0: return 
        w = self.tabWidget.widget(index)
        if isinstance(w, SessionTabWidget):
             if w.session_name in self.active_session_widgets: 
                 del self.active_session_widgets[w.session_name]
        self.tabWidget.removeTab(index)
        w.deleteLater()

    # --- Updates ---
    @Slot(dict)
    def on_monitor_updated(self, d): 
        self._pending_monitor_data = d

    @Slot(object, object)
    def on_spectrum_updated(self, w, i): 
        self._pending_spectrum_data = (w, i)

    def _refresh_dashboard_plots(self):
        if self._pending_monitor_data:
            d = self._pending_monitor_data
            
            def get_data(ch, key):
                if ch in d and len(d[ch][key]) > 0: return np.array(d[ch][key])
                return np.array([])

            # Channel A
            va = get_data('a', 'v'); ia = get_data('a', 'i')
            # Channel B
            vb = get_data('b', 'v'); ib = get_data('b', 'i')

            # Linear
            self.c_v_a.setData(va); self.c_c_a.setData(ia)
            self.c_v_b.setData(vb); self.c_c_b.setData(ib)
            
            # Log
            if len(ia) > 0: self.c_log_a.setData(np.abs(ia) + 1e-13)
            else: self.c_log_a.setData([])
            if len(ib) > 0: self.c_log_b.setData(np.abs(ib) + 1e-13)
            else: self.c_log_b.setData([])

            self._pending_monitor_data = None
            
        if self._pending_spectrum_data:
            w, i = self._pending_spectrum_data
            if w is not None: self.c_s.setData(w, i)
            self._pending_spectrum_data = None

    @Slot(str, dict)
    def on_session_data_updated(self, s_name, data):
        if s_name not in self.active_session_widgets: 
            self._create_session_tab(s_name)
        
        tab = self.active_session_widgets[s_name]
        tab.update_curve("iv_i", data['x'], data['i'], append=True)
        tab.update_curve("iv_v", data['x'], data['v'], append=True)
        
        val_abs = abs(data['i']) + 1e-13
        tab.update_curve("iv_log", data['x'], val_abs, append=True)

        if data['spectrum'] is not None: 
            tab.update_curve("spec", data['wl'], data['spectrum'], append=False)

    def _create_session_tab(self, name):
        tab = SessionTabWidget(name, self)
        tab.add_plot("iv_i", "Current (Lin)", "Set", "I [A]", False, False)
        tab.add_plot("iv_log", "Current (Log)", "Set", "I [A]", False, True)
        tab.add_plot("iv_v", "Voltage", "Set", "V [V]", False, False)
        tab.add_plot("spec", "Spectrum", "nm", "Cnt", False, False)
        idx = self.tabWidget.addTab(tab, name)
        self.tabWidget.setCurrentIndex(idx)
        self.active_session_widgets[name] = tab

    @Slot(str)
    def on_profile_loaded(self, name):
        if hasattr(self, 'spinBox_history'):
            self.spinBox_history.blockSignals(True)
            self.spinBox_history.setValue(self.plot_mgr.monitor_maxlen)
            self.spinBox_history.blockSignals(False)