import sys
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel
from PySide6.QtCore import Slot, Signal, QEvent, QTimer, Qt, QCoreApplication

# ==========================================================================================
# IMPORT UI
# ==========================================================================================
# Wir versuchen den relativen Import. Wenn das fehlschlägt, geben wir den genauen Fehler aus.
try:
    from .ui_SpectrometerWidget import Ui_Form
except ImportError as e:
    print("---------------------------------------------------------")
    print(f"KRITISCHER FEHLER: Konnte 'ui_SpectrometerWidget.py' nicht importieren!")
    print(f"Fehlermeldung: {e}")
    print("Stelle sicher, dass die Datei 'ui_SpectrometerWidget.py' im Ordner 'modules/spectrometer/' liegt.")
    print("---------------------------------------------------------")
    raise e  # Programm stoppen, damit man den Fehler sieht

# ==========================================================================================
# Spectrometer Widget Logic
# ==========================================================================================

class SpectrometerWidget(QWidget, Ui_Form):
    """
    Verwaltet das Spektrometer-UI mit PyQtGraph.
    Verbindet die Logik (SpectrometerManager) mit dem Layout (Ui_Form).
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        # 1. UI aus deiner Datei laden
        # Hier wird self.widget_plot erstellt!
        self.setupUi(self)

        # Manager aus dem Context holen
        self.spec_mgr = context.spectrometer_manager
        self.log_mgr = context.log_manager
        self.profile_mgr = context.profile_manager

        # --- Timer Setup ---
        self.continuous_timer = QTimer(self)
        self.continuous_timer.setInterval(50) 
        self.continuous_timer.timeout.connect(self._on_timer_tick)

        self.temp_poll_timer = QTimer(self)
        self.temp_poll_timer.setInterval(1000) 
        self.temp_poll_timer.timeout.connect(self._poll_temperature)

        # --- Initialisierung ---
        # Jetzt existiert self.widget_plot sicher
        self.__setup_pyqtgraph() 
        self.__setup_initial_values()
        self.__connect_signals()

        # Event-Filter für ComboBox (Refresh bei Click)
        self.comboBox_deviceList.installEventFilter(self)

        # Initiale Suche nach Geräten
        self.spec_mgr.get_deviceList()

        self.context.experiment_manager.experiment_started.connect(self.on_experiment_started)
        self.context.experiment_manager.experiment_finished.connect(self.on_experiment_finished)
        self.context.experiment_manager.experiment_error.connect(self.on_experiment_finished) # Fehler = Ende

    def __setup_pyqtgraph(self):
        """Ersetzt den leeren Widget-Platzhalter mit dem PyQtGraph Plot."""
        
        # Sicherheitscheck (sollte durch setupUi erledigt sein)
        if not hasattr(self, 'widget_plot'):
            self.log_mgr.error("CRITICAL: 'widget_plot' not found in UI file. Please re-compile .ui file.")
            return

        # Layout holen oder erstellen
        if self.widget_plot.layout() is None:
            layout = QVBoxLayout(self.widget_plot)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = self.widget_plot.layout()

        # PlotWidget erstellen
        self.plot_widget = pg.PlotWidget(title="Spectrum (Not Connected)")
        layout.addWidget(self.plot_widget)

        # Styling (Dark Mode & Wissenschaftlich)
        self.plot_widget.setBackground('k') 
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Intensity', units='Counts')
        self.plot_widget.setLabel('bottom', 'Wavelength', units='nm')
        self.plot_widget.addLegend()

        # 1. Raw Curve (Gelb) - Standard: Hidden
        self.curve_raw = self.plot_widget.plot(name="Raw", pen=pg.mkPen(color='#ffff00', width=1))
        self.curve_raw.setVisible(False)

        # 2. Dark Curve (Rot, Gestrichelt) - Standard: Hidden
        self.curve_dark = self.plot_widget.plot(name="Dark", pen=pg.mkPen(color='#ff3333', style=Qt.DashLine, width=1.5))
        self.curve_dark.setVisible(False)

        # 3. Corrected Curve (Cyan, leicht gefüllt) - Standard: Visible
        self.curve_corrected = self.plot_widget.plot(name="Corrected", pen=pg.mkPen(color='#00e5ff', width=2))
        self.curve_corrected.setBrush(pg.mkBrush(color=(0, 229, 255, 30))) 
        self.curve_corrected.setFillLevel(0)

    def __setup_initial_values(self):
        """Lädt gespeicherte Werte und setzt Styles."""
        
        # GUI Status updaten (Disconnected)
        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        """Verbindet UI-Elemente mit Logik."""
        # --- Manager -> UI ---
        self.spec_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.spec_mgr.device_list_updated.connect(self.on_device_list_updated)
        
        # Daten-Signale
        self.spec_mgr.new_spectrum_acquired.connect(self.on_new_spectrum_acquired)
        self.spec_mgr.dark_measurement_progress.connect(self.on_dark_measurement_progress)

        # --- UI -> Manager ---
        self.pushButton_connect.clicked.connect(self.on_connect_clicked)
        
        # Messungen
        self.pushButton_acquireSingle.clicked.connect(self._acquire_single_wrapper)
        self.pushButton_acquireContinuous.clicked.connect(self.on_toggle_continuous)
        self.pushButton_acqurieDarkRead.clicked.connect(self.on_acquire_dark_clicked)

        # Settings
        self.checkBox_correctDarkCounts.toggled.connect(self.spec_mgr.set_correction_dark_count)
        self.checkBox_correctNonLinearity.toggled.connect(self.spec_mgr.set_correction_non_linearity)
        self.spinBox_integrationTime.valueChanged.connect(self.spec_mgr.set_integrationtime)
        self.spinBox_countDarkRead.valueChanged.connect(self.on_dark_read_count_changed)
        
        # Temperatur
        self.doubleSpinBox.editingFinished.connect(self.on_target_temp_changed)
        
        # Auf Profil-Laden warten für UI-Update
        if self.profile_mgr:
             self.profile_mgr.profile_loaded.connect(self.on_profile_loaded)

    @Slot()
    def on_experiment_started(self):
        """
        Wird aufgerufen, wenn ein Experiment startet.
        Sperrt die UI und stoppt den Live-Timer, um Hardware-Konflikte zu vermeiden.
        """
        self.log_mgr.info("SpectrometerWidget: Locking UI due to active experiment.")
        
        # 1. Timer stoppen (Verhindert Race Conditions auf USB!)
        if self.continuous_timer.isActive():
            self.continuous_timer.stop()
            self.pushButton_acquireContinuous.setChecked(False)
            self.pushButton_acquireContinuous.setText("Start")
        
        # 2. UI sperren (Verhindert ungültiges Dark Spectrum durch User-Eingabe)
        self.frame.setEnabled(False) # Sperrt den gesamten linken Bereich (Settings + Connect)
        
        # Optional: Plot aktiv lassen, damit man Updates sieht
        # self.widget_plot.setEnabled(True) 

    @Slot()
    def on_experiment_finished(self): # Nimmt optional error_msg an, falls nötig, hier via Signal ohne Args
        """
        Wird aufgerufen, wenn das Experiment endet. Gibt die UI wieder frei.
        """
        self.log_mgr.info("SpectrometerWidget: Unlocking UI.")
        self.frame.setEnabled(True)
        
        # Wir starten den Timer NICHT automatisch neu, das muss der User machen.
        
    # --- Interne Logik ---

    def _acquire_single_wrapper(self):
        """Wrapper für Single Shot."""
        if self.continuous_timer.isActive():
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()
        
        self.spec_mgr.acquire_spectrum()

    def _on_timer_tick(self):
        """Timer Tick für Continuous Mode."""
        if self.spec_mgr.is_connected():
            self.spec_mgr.acquire_spectrum()
        else:
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()

    # --- Slots ---

    @Slot(int)
    def on_dark_read_count_changed(self, value):
        """Speichert die Anzahl der Dark Scans im Profil."""
        if self.profile_mgr.get_current_profile_name():
            self.profile_mgr.write("Spec_DarkReadCount", value)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        """Wird aufgerufen, wenn Profil geladen wurde -> UI aktualisieren."""
        self.log_mgr.info(f"SpectrometerWidget: Loading settings from profile '{profile_name}'...")
        
        # Integration Time
        self.spinBox_integrationTime.blockSignals(True)
        self.spinBox_integrationTime.setValue(self.spec_mgr.get_integrationtime())
        self.spinBox_integrationTime.blockSignals(False)
        
        # Dark Count Correction
        self.checkBox_correctDarkCounts.blockSignals(True)
        self.checkBox_correctDarkCounts.setChecked(self.spec_mgr.get_correction_dark_count())
        self.checkBox_correctDarkCounts.blockSignals(False)

        # Non-Linearity Correction
        self.checkBox_correctNonLinearity.blockSignals(True)
        self.checkBox_correctNonLinearity.setChecked(self.spec_mgr.get_correction_non_linearity())
        self.checkBox_correctNonLinearity.blockSignals(False)

        # Target Temperature
        self.doubleSpinBox.blockSignals(True)
        self.doubleSpinBox.setValue(self.spec_mgr.get_temperature())
        self.doubleSpinBox.blockSignals(False)

        # Dark Read Count
        dark_read_count = self.profile_mgr.read("Spec_DarkReadCount")
        if dark_read_count is not None:
            self.spinBox_countDarkRead.blockSignals(True)
            self.spinBox_countDarkRead.setValue(int(dark_read_count))
            self.spinBox_countDarkRead.blockSignals(False)

    @Slot()
    def on_toggle_continuous(self):
        """Start/Stop Continuous Mode."""
        is_active = self.pushButton_acquireContinuous.isChecked()
        
        if is_active:
            self.pushButton_acquireContinuous.setText("Stop")
            self.pushButton_acquireSingle.setEnabled(False)
            self.pushButton_acqurieDarkRead.setEnabled(False)
            self.pushButton_connect.setEnabled(False) 
            self.continuous_timer.start()
        else:
            self.pushButton_acquireContinuous.setText("Start")
            self.continuous_timer.stop()
            self.pushButton_acquireSingle.setEnabled(True)
            self.pushButton_acqurieDarkRead.setEnabled(True)
            self.pushButton_connect.setEnabled(True)

    @Slot()
    def on_acquire_dark_clicked(self):
        """Startet Dark Measurement."""
        if self.continuous_timer.isActive():
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()

        scans = self.spinBox_countDarkRead.value()
        
        self.plot_widget.setTitle("Measuring Dark Spectrum...", color='#ff3333')
        self.curve_dark.setVisible(True)
        
        success = self.spec_mgr.acquire_dark_spectrum(scans)
        
        if success:
            self.plot_widget.setTitle(self.spec_mgr.get_activeDeviceName(), color='w')
            self.curve_dark.setVisible(False) 
        else:
            self.plot_widget.setTitle("Dark Measurement Failed", color='r')

    @Slot(object, object, int)
    def on_dark_measurement_progress(self, wavelengths, current_avg, progress_pct):
        """Live Update Dark Spectrum."""
        if wavelengths is None or current_avg is None: return
        self.curve_dark.setData(wavelengths, current_avg)
        self.plot_widget.setTitle(f"Measuring Dark Spectrum... {progress_pct}%", color='#ff3333')
        QCoreApplication.processEvents()

    @Slot(object, object)
    def on_new_spectrum_acquired(self, wavelengths, intensities):
        """
        Plot Update.
        Manager liefert 'Corrected'. Wir rekonstruieren 'Raw'.
        """
        if wavelengths is None or intensities is None: return

        # 1. Corrected
        self.curve_corrected.setData(wavelengths, intensities)

        # 2. Dark & Raw
        dark_data = self.spec_mgr.get_dark_spectrum_average()
        
        if dark_data is not None:
            self.curve_dark.setData(wavelengths, dark_data)
            try:
                # Rekonstruktion: Raw = Corrected + Dark
                raw_data = intensities + dark_data
                self.curve_raw.setData(wavelengths, raw_data)
            except ValueError:
                self.curve_raw.setData([], [])
        else:
            self.curve_dark.setData([], [])
            # Ohne Dark ist Raw == Corrected
            self.curve_raw.setData(wavelengths, intensities)

    def _poll_temperature(self):
        """1Hz Timer für Temperatur & Styles."""
        if not self.spec_mgr.is_connected(): return

        actual_temp = self.spec_mgr.get_temperature()
        target_temp = self.doubleSpinBox.value()
        
        self.doubleSpinBox_actualTemp.setValue(actual_temp)

        delta = abs(actual_temp - target_temp)
        new_state = "ok"
        if delta > 1.0: new_state = "critical"
        elif delta > 0.2: new_state = "warning"
        
        if self.doubleSpinBox_actualTemp.property("tempState") != new_state:
            self.doubleSpinBox_actualTemp.setProperty("tempState", new_state)
            self.doubleSpinBox_actualTemp.style().unpolish(self.doubleSpinBox_actualTemp)
            self.doubleSpinBox_actualTemp.style().polish(self.doubleSpinBox_actualTemp)

    @Slot()
    def on_target_temp_changed(self):
        target = self.doubleSpinBox.value()
        self.spec_mgr.set_temperature(target)

    @Slot(list)
    def on_device_list_updated(self, device_names):
        self.comboBox_deviceList.clear()
        self.comboBox_deviceList.addItems(device_names)
        if self.spec_mgr.LastDevice:
            for name in device_names:
                if self.spec_mgr.LastDevice in name:
                    self.comboBox_deviceList.setCurrentText(name)
                    break

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        if connected:
            self.label_device.setText(device_name)
            self.label_device.setStyleSheet("color: #00ff00;")
            self.pushButton_connect.setText("Disconnect")
            self.plot_widget.setTitle(device_name, color='w')

            # Enable UI
            self.spinBox_integrationTime.setEnabled(True)
            self.checkBox_correctDarkCounts.setEnabled(True)
            self.checkBox_correctNonLinearity.setEnabled(True)
            self.pushButton_acquireSingle.setEnabled(True)
            self.pushButton_acquireContinuous.setEnabled(True)
            self.pushButton_acqurieDarkRead.setEnabled(True)
            self.spinBox_countDarkRead.setEnabled(True)
            self.doubleSpinBox.setEnabled(True)
            self.comboBox_deviceList.setEnabled(False)

            # Limits & Timers
            min_us, max_us = self.spec_mgr.get_integrationtime_limits_us()
            self.spinBox_integrationTime.setRange(min_us, max_us)
            self.temp_poll_timer.start()
            self._poll_temperature()

        else:
            self.label_device.setText("Not Connected")
            self.label_device.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect")
            self.plot_widget.setTitle("Spectrum (Not Connected)", color='w')

            if self.continuous_timer.isActive():
                self.continuous_timer.stop()
                self.pushButton_acquireContinuous.setChecked(False)
                self.pushButton_acquireContinuous.setText("Start")

            self.temp_poll_timer.stop()
            self.doubleSpinBox_actualTemp.setProperty("tempState", "ok")
            self.doubleSpinBox_actualTemp.style().unpolish(self.doubleSpinBox_actualTemp)
            self.doubleSpinBox_actualTemp.style().polish(self.doubleSpinBox_actualTemp)

            # Disable UI
            self.spinBox_integrationTime.setEnabled(False)
            self.checkBox_correctDarkCounts.setEnabled(False)
            self.checkBox_correctNonLinearity.setEnabled(False)
            self.pushButton_acquireSingle.setEnabled(False)
            self.pushButton_acquireContinuous.setEnabled(False)
            self.pushButton_acqurieDarkRead.setEnabled(False)
            self.spinBox_countDarkRead.setEnabled(False)
            self.doubleSpinBox.setEnabled(False)
            self.comboBox_deviceList.setEnabled(True)
            
            # Clear Plot
            self.curve_corrected.setData([], [])
            self.curve_raw.setData([], [])
            self.curve_dark.setData([], [])

    @Slot()
    def on_connect_clicked(self):
        if self.spec_mgr.is_connected():
            self.spec_mgr.disconnect()
        else:
            sel = self.comboBox_deviceList.currentText()
            if sel: self.spec_mgr.connect(sel)

    def eventFilter(self, watched, event):
        if watched == self.comboBox_deviceList and event.type() == QEvent.Type.MouseButtonPress:
            if not self.comboBox_deviceList.view().isVisible():
                self.spec_mgr.get_deviceList()
        return super().eventFilter(watched, event)