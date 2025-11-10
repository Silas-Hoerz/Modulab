
import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Signal, QEvent

# Importiere die generierte UI-Klasse
try:
    # Passt den relativen Pfad an, falls nötig
    from .ui_SpectrometerWidget import Ui_Form 
except ImportError:
    print("Error: Could not find 'ui_SpectrometerWidget.py'.")
    # Notfall-Fallback, damit der Code nicht crasht
    from PySide6.QtWidgets import QLabel
    class Ui_Form:
        def setupUi(self, Form):
            self.vLayout = QVBoxLayout(Form)
            self.label_progress = QLabel("UI File not loaded", Form)
            self.vLayout.addWidget(self.label_progress)
        def retranslateUi(self, Form): pass

# Importiere die Plot-Bibliothek (Matplotlib)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrometerWidget(QWidget, Ui_Form):
    """
    Diese Klasse verwaltet das Spektrometer-UI-Panel.
    Sie verbindet die UI-Elemente (Buttons, ComboBox) mit dem SpectrometerManager.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Manager aus dem Kontext-Objekt holen
        self.spec_mgr = context.spectrometer_manager
        self.log_mgr = context.log_manager

        # Internen Status für Plot-Grenzen
        self.y_max_intensity = 65535.0 # Standardwert

        self.__setup_plot()
        self.__setup_ui()
        self.__connect_signals()

        # Event-Filter für die ComboBox (wie in deinem ExperimentWidget)
        self.comboBox_deviceList.installEventFilter(self)

        # Beim Start sofort nach Geräten suchen
        self.spec_mgr.get_deviceList()

    def __setup_plot(self):
        """
        Initialisiert das Matplotlib-Diagramm und fügt es in den 
        Platzhalter 'widget_plot' ein.
        """
        # Erstelle ein Layout FÜR den Platzhalter, da er von Haus aus keins hat
        plot_layout = QVBoxLayout(self.widget_plot)
        plot_layout.setContentsMargins(0, 0, 0, 0) # Fülle den Platz aus
        
        # Erstelle das Matplotlib Canvas
        self.plot_canvas = FigureCanvas(Figure(figsize=(5, 3), tight_layout=True))
        self.plot_ax = self.plot_canvas.figure.subplots()
        
        # Füge das Canvas zum Layout des Platzhalters hinzu
        plot_layout.addWidget(self.plot_canvas)
        
        # Initialisiere den Plot-Titel
        self.plot_ax.set_title("Spectrum (Not Connected)")
        self.plot_ax.set_xlabel("Wavelength (nm)")
        self.plot_ax.set_ylabel("Intensity (a.u.)")
        self.plot_canvas.draw()

    def __setup_ui(self):
        """Setzt den anfänglichen Zustand der UI-Elemente."""
        
        
        # Lade die gespeicherten Werte aus dem Manager
        try:
            self.spinBox_integrationTime.setValue(self.spec_mgr.get_integrationtime())
            self.checkBox_correctDarkCounts.setChecked(self.spec_mgr.get_correction_dark_count())
            self.checkBox_correctNonLinearity.setChecked(self.spec_mgr.get_correction_non_linearity())
        except Exception as e:
            self.log_mgr.error(f"Error setting initial UI values: {e}")

        # Setze den initialen (getrennten) Zustand
        # (Die on_connection_status_changed wird aufgerufen, falls der Re-Connect klappt)
        self.on_connection_status_changed(False, "")

    def __connect_signals(self):
        """Verbindet alle Signale und Slots."""
        
        # 1. Manager-Signale an UI-Slots (diese Klasse)
        self.spec_mgr.connection_status_changed.connect(self.on_connection_status_changed)
        self.spec_mgr.device_list_updated.connect(self.on_device_list_updated)
        self.spec_mgr.new_spectrum_acquired.connect(self.on_new_spectrum_acquired)

        # 2. UI-Elemente (Buttons, Checkboxen etc.) an Manager-Slots oder lokale Slots

        self.pushButton_connect.clicked.connect(self.on_connect_clicked)
        self.pushButton_acquire.clicked.connect(self.spec_mgr.acquire_spectrum)

        # Direkte Verbindung zu Settern (einfach)
        self.checkBox_correctDarkCounts.toggled.connect(self.spec_mgr.set_correction_dark_count)
        self.checkBox_correctNonLinearity.toggled.connect(self.spec_mgr.set_correction_non_linearity)

        # Verbindung über einen Slot, um den richtigen Wert zu senden (besser)
        # valueChanged sendet den int-Wert, den der Manager erwartet
        self.spinBox_integrationTime.valueChanged.connect(self.spec_mgr.set_integrationtime)


    # --- Slots für Signale vom SpectrometerManager ---

    @Slot(list)
    def on_device_list_updated(self, device_names):
        """Aktualisiert die ComboBox, wenn der Manager Geräte gefunden hat."""
        self.comboBox_deviceList.clear()
        self.comboBox_deviceList.addItems(device_names)
        
        # Versuche, das zuletzt verbundene Gerät auszuwählen
        if self.spec_mgr.LastDevice:
            for name in device_names:
                if self.spec_mgr.LastDevice in name:
                    self.comboBox_deviceList.setCurrentText(name)
                    break

    @Slot(bool, str)
    def on_connection_status_changed(self, connected, device_name):
        """
        Der wichtigste Slot: Schaltet die UI-Zustände um, wenn die 
        Verbindung aufgebaut oder getrennt wird.
        """
        if connected:
            self.label_device.setText(device_name)
            self.pushButton_connect.setText("Disconnect")
            
            # UI-Bereiche anzeigen (statt nur zu aktivieren)
            self.label_integrationTime.setVisible(True)
            self.spinBox_integrationTime.setVisible(True)
            self.checkBox_correctDarkCounts.setVisible(True)
            self.checkBox_correctNonLinearity.setVisible(True)
            self.pushButton_acquire.setVisible(True)
            self.widget_plot.setVisible(True)
            
            # UI-Bereiche aktivieren (HINWEIS: Dies ist der fehlerhafte Code aus deinem Original)
            # self.verticalLayout_settings.setEnabled(True) # -> Ersetzt
            # self.verticalLayout_acquisition.setEnabled(True) # -> Ersetzt
            
            self.comboBox_deviceList.setEnabled(False) # Auswahl sperren

            # Hardware-Limits abrufen und UI aktualisieren
            min_us, max_us = self.spec_mgr.get_integrationtime_limits_us()
            self.spinBox_integrationTime.setRange(min_us, max_us)
            
            # Max. Intensität für Plot-Skalierung holen
            self.y_max_intensity = self.spec_mgr.get_max_intensity()
            
            self.plot_ax.set_title(f"Spectrum ({device_name})")
            self.plot_canvas.draw()

        else: # Nicht verbunden
            self.label_device.setText("Not Connected")
            self.pushButton_connect.setText("Connect")
            
            # UI-Bereiche ausblenden (statt nur zu deaktivieren)
            self.label_integrationTime.setVisible(False)
            self.spinBox_integrationTime.setVisible(False)
            self.checkBox_correctDarkCounts.setVisible(False)
            self.checkBox_correctNonLinearity.setVisible(False)
            self.pushButton_acquire.setVisible(False)
            self.widget_plot.setVisible(False)

            # UI-Bereiche deaktivieren (HINWEIS: Dies ist der fehlerhafte Code aus deinem Original)
            # self.verticalLayout_settings.setEnabled(False) # -> Ersetzt
            # self.verticalLayout_acquisition.setEnabled(False) # -> Ersetzt
            
            self.comboBox_deviceList.setEnabled(True)  # Auswahl freigeben

            # Plot zurücksetzen
            self.y_max_intensity = 65535.0 # Standard
            self.plot_ax.clear()
            self.plot_ax.set_title("Spectrum (Not Connected)")
            self.plot_ax.set_xlabel("Wavelength (nm)")
            self.plot_ax.set_ylabel("Intensity (a.u.)")
            self.plot_canvas.draw()


    @Slot(object, object)
    def on_new_spectrum_acquired(self, wavelengths, intensities):
        """Aktualisiert den Plot, wenn ein neues Spektrum empfangen wird."""
        if wavelengths is None or intensities is None:
            return
            
        # Altes Diagramm löschen
        self.plot_ax.clear()
        
        # Neu zeichnen
        self.plot_ax.plot(wavelengths, intensities, color="cyan")
        
        # Beschriftungen und Limits setzen (clear() löscht sie)
        self.plot_ax.set_title(self.spec_mgr.get_activeDeviceName())
        self.plot_ax.set_xlabel("Wavelength (nm)")
        self.plot_ax.set_ylabel("Intensity (a.u.)")
        
        # Y-Achse auf den maximalen Wert des Spektrometers festlegen
        self.plot_ax.set_ylim(0, self.y_max_intensity * 1.05) # 5% Puffer
        
        # Diagramm neu rendern
        self.plot_canvas.draw()

    # --- Slots für UI-Aktionen ---

    @Slot()
    def on_connect_clicked(self):
        """Wird aufgerufen, wenn der Verbinden/Trennen-Button geklickt wird."""
        if self.spec_mgr.is_connected():
            self.spec_mgr.disconnect()
        else:
            selected_device = self.comboBox_deviceList.currentText()
            if not selected_device:
                self.log_mgr.warning("No spectrometer selected for connection.")
                return
            
            self.spec_mgr.connect(selected_device)
    
    # --- Event Filter für ComboBox ---
    
    def eventFilter(self, watched_object, event):
        """
        Fängt Events ab, um das Öffnen der ComboBox zu erkennen.
        (Kopiert von deinem ExperimentWidget-Beispiel)
        """
        if watched_object == self.comboBox_deviceList:
            if event.type() == QEvent.Type.MouseButtonPress:
                if not self.comboBox_deviceList.view().isVisible():
                    # ComboBox wird gerade geöffnet -> Liste aktualisieren
                    self.spec_mgr.get_deviceList()

        # Event an die Basisklasse weiterleiten
        return super().eventFilter(watched_object, event)