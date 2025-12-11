import sys
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Slot, Signal, QEvent, QTimer, Qt

# ==========================================================================================
# UI Setup (Kopie aus deinem Code oben, damit es runnable ist)
# ==========================================================================================
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(483, 400) # Etwas höher für Plot
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 6)
        self.frame = QFrame(Form)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout = QVBoxLayout(self.frame)
        
        # --- Top Bar: Connection ---
        self.horizontalLayout_4 = QHBoxLayout()
        self.label = QLabel(self.frame)
        self.label.setText("Device:")
        self.horizontalLayout_4.addWidget(self.label)
        self.comboBox_deviceList = QComboBox(self.frame)
        self.comboBox_deviceList.setMinimumSize(QSize(150, 0))
        self.horizontalLayout_4.addWidget(self.comboBox_deviceList)
        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setText("Connect")
        self.horizontalLayout_4.addWidget(self.pushButton_connect)
        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(self.horizontalSpacer)
        self.label_device = QLabel(self.frame)
        self.label_device.setText("No connection")
        self.horizontalLayout_4.addWidget(self.label_device)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        # --- Settings Row 1: Integration & Correction ---
        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_connection = QVBoxLayout()
        self.label_integrationTime = QLabel("Integration Time [us]:", self.frame)
        self.verticalLayout_connection.addWidget(self.label_integrationTime)
        self.spinBox_integrationTime = QSpinBox(self.frame)
        self.spinBox_integrationTime.setMaximum(60000000) # Groß genug setzen
        self.spinBox_integrationTime.setValue(100000)
        self.verticalLayout_connection.addWidget(self.spinBox_integrationTime)
        self.horizontalLayout.addLayout(self.verticalLayout_connection)

        self.verticalLayout_settings = QVBoxLayout()
        self.checkBox_correctDarkCounts = QCheckBox("Correct dark counts", self.frame)
        self.verticalLayout_settings.addWidget(self.checkBox_correctDarkCounts)
        self.checkBox_correctNonLinearity = QCheckBox("Correct non linearity", self.frame)
        self.verticalLayout_settings.addWidget(self.checkBox_correctNonLinearity)
        self.horizontalLayout.addLayout(self.verticalLayout_settings)

        # --- Settings Row 2: Temperature ---
        self.verticalLayout_2 = QVBoxLayout()
        self.horizontalLayout_5 = QHBoxLayout()
        self.label_actualTemp = QLabel("Actual Temp:", self.frame)
        self.horizontalLayout_5.addWidget(self.label_actualTemp)
        self.doubleSpinBox_actualTemp = QDoubleSpinBox(self.frame)
        self.doubleSpinBox_actualTemp.setReadOnly(True)
        self.doubleSpinBox_actualTemp.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBox_actualTemp.setSuffix(" °C")
        self.doubleSpinBox_actualTemp.setMinimum(-100.0)
        self.horizontalLayout_5.addWidget(self.doubleSpinBox_actualTemp)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.label_2 = QLabel("Target Temp:", self.frame)
        self.horizontalLayout_3.addWidget(self.label_2)
        self.doubleSpinBox = QDoubleSpinBox(self.frame) # Target Temp
        self.doubleSpinBox.setSuffix(" °C")
        self.doubleSpinBox.setMinimum(-100.0)
        self.horizontalLayout_3.addWidget(self.doubleSpinBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer_3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        # --- Acquisition Bar ---
        self.verticalLayout_acquisition = QVBoxLayout()
        self.horizontalLayout_2 = QHBoxLayout()
        self.pushButton_acqurieDarkRead = QPushButton("Read Dark", self.frame)
        self.horizontalLayout_2.addWidget(self.pushButton_acqurieDarkRead)
        self.spinBox_countDarkRead = QSpinBox(self.frame)
        self.spinBox_countDarkRead.setMinimum(1)
        self.spinBox_countDarkRead.setMaximum(1000)
        self.spinBox_countDarkRead.setValue(10)
        self.spinBox_countDarkRead.setSuffix(" Scans")
        self.horizontalLayout_2.addWidget(self.spinBox_countDarkRead)
        
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_acquireSingle = QPushButton("Single", self.frame)
        self.horizontalLayout_2.addWidget(self.pushButton_acquireSingle)
        self.pushButton_acquireContinuous = QPushButton("Start", self.frame)
        self.pushButton_acquireContinuous.setCheckable(True) # Wichtig für Start/Stop Toggle
        self.horizontalLayout_2.addWidget(self.pushButton_acquireContinuous)
        self.verticalLayout_acquisition.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_acquisition)

        # --- Plot Widget Placeholder ---
        self.widget_plot = QWidget(self.frame)
        self.widget_plot.setMinimumSize(QSize(380, 200))
        sizePolicyPlot = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.widget_plot.setSizePolicy(sizePolicyPlot)
        self.verticalLayout.addWidget(self.widget_plot)

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Spectrometer", None))

# ==========================================================================================
# Spectrometer Widget Implementation
# ==========================================================================================

class SpectrometerWidget(QWidget, Ui_Form):
    """
    Verwaltet das Spektrometer-UI mit PyQtGraph, Temperatur-Kontrolle und 
    Dark-Spectrum-Management.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Manager aus dem Context holen
        self.spec_mgr = context.spectrometer_manager
        self.log_mgr = context.log_manager

        # Timer für kontinuierliche Messung (Non-Blocking)
        self.continuous_timer = QTimer(self)
        self.continuous_timer.setInterval(50) # Check alle 50ms (Hardware limitiert eh)
        self.continuous_timer.timeout.connect(self._on_timer_tick)

        # UI Setup
        self.__setup_pyqtgraph() # Neues Plotting System
        self.__setup_ui()
        self.__connect_signals()

        # Event-Filter für ComboBox (Refresh bei Click)
        self.comboBox_deviceList.installEventFilter(self)

        # Initiale Suche
        self.spec_mgr.get_deviceList()

    def __setup_pyqtgraph(self):
        """Initialisiert das PyQtGraph Widget."""
        # Layout für den Platzhalter 'widget_plot'
        layout = QVBoxLayout(self.widget_plot)
        layout.setContentsMargins(0, 0, 0, 0)

        # PlotWidget erstellen
        self.plot_widget = pg.PlotWidget(title="Spectrum (Not Connected)")
        layout.addWidget(self.plot_widget)

        # Styling (Dark Mode & Wissenschaftlich)
        self.plot_widget.setBackground('k') # Schwarz/Transparent
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Intensity', units='Counts')
        self.plot_widget.setLabel('bottom', 'Wavelength', units='nm')

        # Kurve erstellen (Cyan, leicht gefüllt für Glow-Effekt)
        # Pen width=2 für gute Sichtbarkeit
        self.plot_curve = self.plot_widget.plot(pen=pg.mkPen(color='#00e5ff', width=2))
        
        # Füllung unter der Kurve (Optional, sieht aber modern aus)
        self.plot_curve.setBrush(pg.mkBrush(color=(0, 229, 255, 30))) # Transparentes Cyan
        self.plot_curve.setFillLevel(0)

        # Referenzlinie für Dark Spectrum (wird nur angezeigt, wenn Dark gemessen wird)
        self.dark_curve = self.plot_widget.plot(pen=pg.mkPen(color='#ff3333', style=Qt.DashLine, width=1))
        self.dark_curve.setVisible(False)

    def __setup_ui(self):
        """Setzt Initiale Werte aus dem Manager."""
        try:
            self.spinBox_integrationTime.setValue(self.spec_mgr.get_integrationtime())
            self.checkBox_correctDarkCounts.setChecked(self.spec_mgr.get_correction_dark_count())
            self.checkBox_correctNonLinearity.setChecked(self.spec_mgr.get_correction_non_linearity())
            self.doubleSpinBox.setValue(self.spec_mgr.get_temperature()) # Target Temp
        except Exception as e:
            self.log_mgr.error(f"Error setting initial UI values: {e}")

        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        """Verbindet Signale und Slots."""
        # --- Manager -> UI ---
        self.spec_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.spec_mgr.device_list_updated.connect(self.on_device_list_updated)
        
        # Wichtig: Spektrum Daten empfangen
        self.spec_mgr.new_spectrum_acquired.connect(self.on_new_spectrum_acquired)
        
        # Wichtig: Live-Update während Dark Measurement
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
        
        # Temperatur: Wenn Wert geändert und Enter gedrückt oder Fokus verloren
        self.doubleSpinBox.editingFinished.connect(self.on_target_temp_changed)

    # --- Interne Logik ---

    def _acquire_single_wrapper(self):
        """Wrapper, um die Single-Messung auszulösen."""
        # Falls Timer läuft, stoppen wir ihn kurz oder lassen ihn laufen?
        # Üblicherweise stoppt "Single" den Continuous Mode nicht zwingend, 
        # aber um Konflikte zu vermeiden, ist es sauberer:
        if self.continuous_timer.isActive():
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()
        
        self.spec_mgr.acquire_spectrum()

    def _on_timer_tick(self):
        """Wird vom Timer aufgerufen -> Löst Messung aus."""
        if self.spec_mgr.is_connected():
            # acquire_spectrum sendet automatisch das Signal new_spectrum_acquired
            self.spec_mgr.acquire_spectrum()
        else:
            # Falls Verbindung weg ist, Timer stoppen
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()

    # --- Slots ---

    @Slot()
    def on_toggle_continuous(self):
        """Startet oder stoppt den kontinuierlichen Mess-Timer."""
        is_active = self.pushButton_acquireContinuous.isChecked()
        
        if is_active:
            self.pushButton_acquireContinuous.setText("Stop")
            # Buttons disablen, die während Messung nicht gedrückt werden sollen
            self.pushButton_acquireSingle.setEnabled(False)
            self.pushButton_acqurieDarkRead.setEnabled(False)
            self.pushButton_connect.setEnabled(False) 
            
            # Timer Starten
            self.continuous_timer.start()
            self.log_mgr.info("Continuous measurement started.")
        else:
            self.pushButton_acquireContinuous.setText("Start")
            self.continuous_timer.stop()
            
            # Buttons wieder freigeben
            self.pushButton_acquireSingle.setEnabled(True)
            self.pushButton_acqurieDarkRead.setEnabled(True)
            self.pushButton_connect.setEnabled(True)
            self.log_mgr.info("Continuous measurement stopped.")

    @Slot()
    def on_acquire_dark_clicked(self):
        """Startet den Dark-Spectrum Prozess."""
        # Continuous mode stoppen falls aktiv
        if self.continuous_timer.isActive():
            self.pushButton_acquireContinuous.setChecked(False)
            self.on_toggle_continuous()

        scans = self.spinBox_countDarkRead.value()
        
        # UI Feedback: Dark Kurve sichtbar machen
        self.dark_curve.setVisible(True)
        self.plot_widget.setTitle("Measuring Dark Spectrum...", color='#ff3333')
        
        # Da measure_dark_spectrum blockierend ist (in der aktuellen Implementierung läuft die Schleife im Manager),
        # müssen wir hier aufpassen. 
        # Option A: Die Schleife im Manager processed Events (wie im Manager Code angemerkt).
        # Option B: Wir rufen es hier auf und verlassen uns auf das Progress-Signal für Updates.
        # Da wir QObject/Signale nutzen, wird die GUI responsive bleiben, sofern der Manager 
        # in der Loop 'QCoreApplication.processEvents()' ruft oder in einem Thread läuft.
        # Falls der Manager im MainThread läuft und keine processEvents hat, friert die GUI hier kurz ein,
        # ABER das Signal 'dark_measurement_progress' wird erst NACH der Arbeit verarbeitet.
        
        # HINWEIS: Für echte "Live"-Updates während einer Schleife im gleichen Thread 
        # muss der Manager QApplication.processEvents() rufen.
        
        success = self.spec_mgr.acquire_dark_spectrum(scans)
        
        if success:
            self.plot_widget.setTitle(self.spec_mgr.get_activeDeviceName(), color='w')
            self.dark_curve.setVisible(False) # Verstecken oder stehen lassen als Referenz? -> Verstecken.
        else:
            self.plot_widget.setTitle("Dark Measurement Failed", color='r')

    @Slot(object, object, int)
    def on_dark_measurement_progress(self, wavelengths, current_avg, progress_pct):
        """Zeigt den Fortschritt der Dark-Messung im Plot an."""
        if wavelengths is None or current_avg is None:
            return
            
        # Wir nutzen eine rote Kurve für Dark Data Visualisierung
        self.dark_curve.setData(wavelengths, current_avg)
        self.plot_widget.setTitle(f"Measuring Dark Spectrum... {progress_pct}%", color='#ff3333')
        
        # Erzwingen des Repaints (wichtig bei Schleifen)
        QCoreApplication.processEvents()

    @Slot(object, object)
    def on_new_spectrum_acquired(self, wavelengths, intensities):
        """Aktualisiert den Plot und die Temperatur."""
        if wavelengths is None or intensities is None:
            return

        # 1. Plot Update (PyQtGraph setData ist sehr schnell)
        self.plot_curve.setData(wavelengths, intensities)

        # 2. Temperatur Update (bei jeder Messung aktualisieren)
        # Wir lesen den Wert aus dem Manager, der ggf. Hardware abfragt.
        # Um Performance zu sparen, könnte man das auch nur jede 10. Messung machen.
        try:
             # Nutze get_temperature() vom Manager
            current_temp = self.spec_mgr.get_temperature()
            self.doubleSpinBox_actualTemp.setValue(current_temp)
        except:
            pass

    @Slot()
    def on_target_temp_changed(self):
        """Sendet neue Zieltemperatur an Manager."""
        target = self.doubleSpinBox.value()
        self.spec_mgr.set_temperature(target)

    @Slot(list)
    def on_device_list_updated(self, device_names):
        """Aktualisiert ComboBox."""
        self.comboBox_deviceList.clear()
        self.comboBox_deviceList.addItems(device_names)
        if self.spec_mgr.LastDevice:
            for name in device_names:
                if self.spec_mgr.LastDevice in name:
                    self.comboBox_deviceList.setCurrentText(name)
                    break

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        """Schaltet UI Elemente an/aus."""
        if connected:
            self.label_device.setText(device_name)
            self.label_device.setStyleSheet("color: #00ff00;") # Grün
            self.pushButton_connect.setText("Disconnect")
            self.plot_widget.setTitle(device_name, color='w')

            # Enable Controls
            self.spinBox_integrationTime.setEnabled(True)
            self.checkBox_correctDarkCounts.setEnabled(True)
            self.checkBox_correctNonLinearity.setEnabled(True)
            self.pushButton_acquireSingle.setEnabled(True)
            self.pushButton_acquireContinuous.setEnabled(True)
            self.pushButton_acqurieDarkRead.setEnabled(True)
            self.spinBox_countDarkRead.setEnabled(True)
            self.doubleSpinBox.setEnabled(True)
            
            self.comboBox_deviceList.setEnabled(False)

            # Limits und Initialwerte
            min_us, max_us = self.spec_mgr.get_integrationtime_limits_us()
            self.spinBox_integrationTime.setRange(min_us, max_us)
            
            # Temperatur Init
            self.doubleSpinBox.setValue(self.spec_mgr.get_temperature())

        else:
            self.label_device.setText("Not Connected")
            self.label_device.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect")
            self.plot_widget.setTitle("Spectrum (Not Connected)", color='w')

            # Timer stoppen
            if self.continuous_timer.isActive():
                self.continuous_timer.stop()
                self.pushButton_acquireContinuous.setChecked(False)
                self.pushButton_acquireContinuous.setText("Start")

            # Disable Controls
            self.spinBox_integrationTime.setEnabled(False)
            self.checkBox_correctDarkCounts.setEnabled(False)
            self.checkBox_correctNonLinearity.setEnabled(False)
            self.pushButton_acquireSingle.setEnabled(False)
            self.pushButton_acquireContinuous.setEnabled(False)
            self.pushButton_acqurieDarkRead.setEnabled(False)
            self.spinBox_countDarkRead.setEnabled(False)
            self.doubleSpinBox.setEnabled(False)

            self.comboBox_deviceList.setEnabled(True)
            
            # Plot leeren
            self.plot_curve.setData([], [])

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