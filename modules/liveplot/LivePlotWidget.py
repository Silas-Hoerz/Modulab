import sys
import os
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QFileDialog, QSizePolicy, 
                               QSpinBox, QTabBar)
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
        """Öffnet Dialog: HDF5 Standard, CSV Optional."""
        profile = self.main_widget.context.profile_manager
        default_dir = profile.read("Export_LastDir") or os.path.expanduser("~")
        
        # Standard Name = Session Name + .h5
        default_file = os.path.join(default_dir, f"{self.session_name}.h5")
        
        # FILTER: Der erste String ist der Default im Explorer
        filter_str = "HDF5 Files (*.h5);;CSV Files (*.csv)"
        
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Measurement Data", 
            default_file, 
            filter_str
        )
        
        if filepath:
            # ExportManager entscheidet anhand der Endung (.h5 oder .csv)
            self.main_widget.export_mgr.save_session_to_disk(self.session_name, filepath)


# ==============================================================================
# LivePlotWidget Main Class
# ==============================================================================
class LivePlotWidget(QWidget, Ui_LivePlot):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self) # Lädt das Basis-UI (ohne SpinBox/Label im Dashboard)
        
        self.context = context 
        self.plot_mgr = context.liveplot_manager
        self.export_mgr = context.export_manager 
        self.log_mgr = context.log_manager
        
        self.tabWidget.clear()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close_requested)

        # WICHTIG: Erst das Dashboard aufbauen (erzeugt self.spinBox_history)
        self.__setup_dashboard_tab()
        
        self.active_session_widgets = {}

        # Signale verbinden
        self.plot_mgr.monitor_updated.connect(self.on_monitor_updated)
        self.plot_mgr.spectrum_updated.connect(self.on_spectrum_updated)
        self.export_mgr.session_updated.connect(self.on_session_data_updated)
        
        if hasattr(self.context.profile_manager, 'profile_loaded'):
             self.context.profile_manager.profile_loaded.connect(self.on_profile_loaded)

        # JETZT existiert self.spinBox_history, da __setup_dashboard_tab aufgerufen wurde
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
        """Erstellt das Dashboard und erzeugt Label/Spinbox manuell."""
        d_widget = QWidget()
        lay = QVBoxLayout(d_widget)
        lay.setContentsMargins(0,0,0,0)

        # --- TOOLBAR MANUELL ERSTELLEN ---
        tb_layout = QHBoxLayout()
        
        # Label erstellen
        lbl_hist = QLabel("History Points:")
        
        # SpinBox erstellen und der Klassen-Instanz zuweisen!
        self.spinBox_history = QSpinBox()
        self.spinBox_history.setRange(100, 100000)
        self.spinBox_history.setSingleStep(100)
        self.spinBox_history.valueChanged.connect(self.on_history_size_changed)
        
        tb_layout.addWidget(lbl_hist)
        tb_layout.addWidget(self.spinBox_history)
        tb_layout.addStretch() # Rest auffüllen
        
        lay.addLayout(tb_layout)
        # ----------------------------------
        
        # Plot Area
        self.dl = pg.GraphicsLayoutWidget()
        self.dl.setBackground('k')
        lay.addWidget(self.dl)
        
        # Plots definieren
        self.p_v = self.dl.addPlot(row=0, col=0, title="Voltage Monitor")
        self.p_v.setLabel('left', "V")
        self.c_v_a = self.p_v.plot(pen='c')
        self.c_v_b = self.p_v.plot(pen='m')
        
        self.p_c = self.dl.addPlot(row=0, col=1, title="Current Monitor")
        self.p_c.setLabel('left', "I")
        self.c_c_a = self.p_c.plot(pen='c')
        self.c_c_b = self.p_c.plot(pen='m')
        
        self.p_s = self.dl.addPlot(row=1, col=0, colspan=2, title="Live Spectrum")
        self.c_s = self.p_s.plot(pen='#00ff00', fillLevel=0, brush=(0,255,0,50))

        idx = self.tabWidget.addTab(d_widget, "Dashboard")
        # Dashboard darf nicht geschlossen werden (Close Button rechts entfernen)
        self.tabWidget.tabBar().setTabButton(idx, QTabBar.RightSide, None)

    # --- Slots ---
    @Slot(int)
    def on_history_size_changed(self, val): 
        self.plot_mgr.set_monitor_buffer_size(val)

    @Slot(int)
    def on_tab_close_requested(self, index):
        if index == 0: return # Dashboard protect
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
            if 'a' in d: 
                self.c_v_a.setData(np.array(d['a']['v']))
                self.c_c_a.setData(np.array(d['a']['i']))
            if 'b' in d: 
                self.c_v_b.setData(np.array(d['b']['v']))
                self.c_c_b.setData(np.array(d['b']['i']))
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
        if data['spectrum'] is not None: 
            tab.update_curve("spec", data['wl'], data['spectrum'], append=False)

    def _create_session_tab(self, name):
        tab = SessionTabWidget(name, self)
        tab.add_plot("iv_i", "Current", "Set", "I [A]", False, False)
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