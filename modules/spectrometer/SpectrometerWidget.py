
import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout,QSizePolicy
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
from matplotlib.colors import to_rgba

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
        Initialisiert das Matplotlib-Diagramm im Dark-Mode Style.
        """
        # Erstelle ein Layout FÜR den Platzhalter
        plot_layout = QVBoxLayout(self.widget_plot)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Figure erstellen (Hintergrund transparent für Integration in GUI)
        self.fig = Figure(tight_layout=True)
        self.fig.patch.set_facecolor('none')  # Transparent!
        
        # Canvas erstellen
        self.plot_canvas = FigureCanvas(self.fig)
        self.plot_canvas.setStyleSheet("background-color:transparent;")

        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_canvas.updateGeometry()

        # Subplot erstellen
        self.plot_ax = self.fig.subplots()
        
        # 2. Initiales Styling anwenden (ruft unsere Helper-Funktion auf)
        self.__style_axis()
        
        # Titel initial setzen
        self.plot_ax.set_title("Spectrum (Not Connected)", color="white")

        # Füge das Canvas zum Layout hinzu
        plot_layout.addWidget(self.plot_canvas)
        
        self.plot_canvas.draw()

    def __style_axis(self):
        """
        Hilfsfunktion: Setzt das Aussehen der Achsen auf 'Modern Dark Mode'.
        Muss nach jedem ax.clear() erneut aufgerufen werden!
        """
        # Hintergrund der Achsen: Entweder auch 'none' oder ein leichtes Dunkelgrau
        self.plot_ax.set_facecolor('none') 
        
        # Farben der Achsen-Linien (Spines)
        for spine in self.plot_ax.spines.values():
            spine.set_color('#aaaaaa') # Hellgrau
            
        # Farben der Ticks und Labels
        self.plot_ax.tick_params(axis='x', colors='white')
        self.plot_ax.tick_params(axis='y', colors='white')
        
        # Grid hinzufügen (sieht technischer aus)
        self.plot_ax.grid(True, linestyle=':', alpha=0.3, color='white')
        
        self.plot_ax.set_xlabel("Wavelength (nm)", color='white')     # <--- HIER
        self.plot_ax.set_ylabel("Intensity (a.u.)", color='white')    # <--- HIER

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
        Der wichtigste Slot: Schaltet die UI-Zustände um.
        KORRIGIERT: Erzwingt weiße Schriftfarbe bei Statusänderungen.
        """
        if connected:
            self.label_device.setText(device_name)
            self.label_device.setStyleSheet("color: green;")
            self.pushButton_connect.setText("Disconnect")
            
            # UI-Bereiche aktivieren
            self.label_integrationTime.setEnabled(True)
            self.spinBox_integrationTime.setEnabled(True)
            self.checkBox_correctDarkCounts.setEnabled(True)
            self.checkBox_correctNonLinearity.setEnabled(True)
            self.pushButton_acquire.setEnabled(True)
            self.widget_plot.setEnabled(True)
            
            self.comboBox_deviceList.setEnabled(False) 

            # Limits holen
            min_us, max_us = self.spec_mgr.get_integrationtime_limits_us()
            self.spinBox_integrationTime.setRange(min_us, max_us)
            
            self.y_max_intensity = self.spec_mgr.get_max_intensity()
            
            # --- FIX: Farbe explizit auf Weiß setzen ---
            self.plot_ax.set_title(f"Spectrum ({device_name})", color='white', fontweight='bold')
            # Sicherstellen, dass Labels weiß bleiben (falls sie durch draw resettet wurden)
            self.plot_ax.xaxis.label.set_color('white')
            self.plot_ax.yaxis.label.set_color('white')
            
            self.plot_canvas.draw()

        else: # Nicht verbunden
            self.label_device.setText("Not Connected")
            self.label_device.setStyleSheet("color: red;")
            self.pushButton_connect.setText("Connect")
            
            # UI-Bereiche deaktivieren
            self.label_integrationTime.setEnabled(False)
            self.spinBox_integrationTime.setEnabled(False)
            self.checkBox_correctDarkCounts.setEnabled(False)
            self.checkBox_correctNonLinearity.setEnabled(False)
            self.pushButton_acquire.setEnabled(False)
            self.widget_plot.setEnabled(False)

            self.comboBox_deviceList.setEnabled(True)

            # Plot zurücksetzen
            self.y_max_intensity = 65535.0 
            
            self.plot_ax.clear()
            
            # --- FIX: Styling wieder anwenden, da clear() alles löscht ---
            self.__style_axis() 
            
            # Titel explizit weiß setzen
            self.plot_ax.set_title("Spectrum (Not Connected)", color='white')
            
            # Hinweis: set_xlabel/ylabel sind jetzt schon in __style_axis() enthalten,
            # müssen hier also nicht doppelt stehen, solange __style_axis() aufgerufen wird.
            
            self.plot_canvas.draw()


    @Slot(object, object)
    def on_new_spectrum_acquired(self, wavelengths, intensities):
        """Aktualisiert den Plot modern und performant."""
        if wavelengths is None or intensities is None:
            return
            
        # Altes Diagramm löschen
        self.plot_ax.clear()
        
        # 1. Plotten der Linie (Cyan leuchtet gut auf Dunkel)
        # 'lw=1.5' macht die Linie etwas dicker
        self.plot_ax.plot(wavelengths, intensities, color="#00e5ff", lw=1.5)
        
        # 2. "Glow"-Effekt: Bereich darunter leicht füllen
        # alpha=0.2 macht es durchscheinend
        self.plot_ax.fill_between(wavelengths, intensities, color="#00e5ff", alpha=0.15)
        
        # 3. Styling wiederherstellen (wird durch clear() gelöscht)
        self.__style_axis()
        
        # Titel setzen
        self.plot_ax.set_title(self.spec_mgr.get_activeDeviceName(), color="white", fontweight='bold')
        
        # Limits setzen
        self.plot_ax.set_ylim(0, self.y_max_intensity * 1.05)
        # X-Limits festsetzen verhindert "Springen" der Achse
        if len(wavelengths) > 0:
            self.plot_ax.set_xlim(min(wavelengths), max(wavelengths))
        
        # Zeichnen
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