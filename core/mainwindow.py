# core/mainwindow.py
# This Python file uses the following encoding: utf-8
import sys
import os
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QDialog, QToolButton, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Slot, QUrl

from core.ui_form import Ui_MainWindow
from core.context import ApplicationContext 

# Views importieren
from modules.log.LogWidget import LogWidget
from modules.device.DeviceWidget import DeviceWidget
from modules.profile.ProfileWidget import ProfileWidget
from modules.spectrometer.SpectrometerWidget import SpectrometerWidget
from modules.smu.SmuWidget import SmuWidget
from modules.liveplot.LivePlotWidget import LivePlotWidget
from modules.data.Hdf5Viewer import Hdf5Viewer
from modules.waterfall.WaterfallWidget import WaterfallWidget
from modules.sweep.SweepWidget import SweepWidget

from modules.experiment.ExperimentWidget import ExperimentWidget

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    
    def __init__(self, context: ApplicationContext, parent=None):
        
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        icon_path = resource_path(os.path.join('resources', 'logo.ico'))
        self.setWindowIcon(QIcon(icon_path))

        self.context = context

        # 1. Grid-Verhalten aktivieren
        self.setDockNestingEnabled(True)

        # 2. Zentrales Widget verstecken (für lückenloses Grid)
        self.central_placeholder = QWidget(self)
        self.setCentralWidget(self.central_placeholder)
        self.central_placeholder.hide() 

        # 3. Widgets instanziieren
        self.log_widget = LogWidget(context=self.context, parent=self)
        self.ui.statusbar.addWidget(self.log_widget, 1)

        self.profile_widget_dialog = ProfileWidget(context=self.context, parent=self)
        self.device_widget_dialog = DeviceWidget(context=self.context, parent=self)

        self.spectrometer_widget = SpectrometerWidget(context=self.context, parent=self)
        self.experiment_widget = ExperimentWidget(context=self.context, parent=self)
        self.smu_widget = SmuWidget(context=self.context, parent=self)
        self.waterfall_widget = WaterfallWidget(context=self.context, parent=self)
        self.liveplot_widget = LivePlotWidget(context=self.context)
        self.hdf5viewer_widget = Hdf5Viewer() 
        
        # 4. Docks erstellen
        self.experiment_dock = QDockWidget("Experiments", self)
        self.experiment_dock.setWidget(self.experiment_widget)
        self.experiment_dock.setObjectName("ExperimentDock")

        self.spectrometer_dock = QDockWidget("Spectrometer", self)
        self.spectrometer_dock.setWidget(self.spectrometer_widget)
        self.spectrometer_dock.setObjectName("SpectrometerDock")

        self.smu_dock = QDockWidget("SMU", self)
        self.smu_dock.setWidget(self.smu_widget)
        self.smu_dock.setObjectName("SmuDock")

        self.waterfall_dock = QDockWidget("Waterfall (2D)", self)
        self.waterfall_dock.setWidget(self.waterfall_widget)
        self.waterfall_dock.setObjectName("WaterfallDock")

        self.liveplot_dock = QDockWidget("Live Plot (XY)", self)
        self.liveplot_dock.setWidget(self.liveplot_widget)
        self.liveplot_dock.setObjectName("LivePlotDock")

        self.hdf5viewer_dock = QDockWidget("Hdf5 Viewer", self)
        self.hdf5viewer_dock.setWidget(self.hdf5viewer_widget)
        self.hdf5viewer_dock.setObjectName("Hdf5ViewerDock")

        self.sweep_widget = SweepWidget(context=self.context, parent=self)
        self.sweep_dock = QDockWidget("Standard Sweep", self)
        self.sweep_dock.setWidget(self.sweep_widget)
        self.sweep_dock.setObjectName("SweepDock")

        # --- 5. LAYOUT AUFBAU (Schritt für Schritt) ---
        
        # Wichtig: Zuerst alle sichtbar machen, damit Qt die Geometrie berechnen kann
        self.experiment_dock.setVisible(True)
        self.spectrometer_dock.setVisible(True)
        self.smu_dock.setVisible(True)
        self.waterfall_dock.setVisible(True)
        self.liveplot_dock.setVisible(True)
        self.hdf5viewer_dock.setVisible(True)

        # SCHRITT A: Den "Anker" setzen.
        # Wir setzen Experiments als Startpunkt, der erst mal ALLES einnimmt.
        self.addDockWidget(Qt.LeftDockWidgetArea, self.experiment_dock)

        # SCHRITT B: Oben und Unten trennen.
        # Wir "schneiden" Waterfall vertikal unter Experiment.
        # Jetzt: Oben=Exp, Unten=Waterfall
        self.splitDockWidget(self.experiment_dock, self.waterfall_dock, Qt.Vertical)

        # SCHRITT C: Die untere Reihe auffüllen (Waterfall | LivePlot | HDF5)
        # Wir schneiden LivePlot horizontal rechts neben Waterfall.
        self.splitDockWidget(self.waterfall_dock, self.liveplot_dock, Qt.Horizontal)
        # Wir schneiden Hdf5 horizontal rechts neben LivePlot.
        self.splitDockWidget(self.liveplot_dock, self.hdf5viewer_dock, Qt.Horizontal)

        # SCHRITT D: Die obere Reihe in Links und Rechts teilen
        # Wir schneiden SMU horizontal rechts neben Experiment.
        # Da Experiment "über" der unteren Reihe liegt, bleibt SMU auch oben.
        self.splitDockWidget(self.experiment_dock, self.smu_dock, Qt.Horizontal)

        # SCHRITT E: Oben-Links vertikal teilen (Experiment / Spectrometer)
        # Wir wollen, dass Experiment oben und Spectrometer direkt darunter ist.
        self.splitDockWidget(self.experiment_dock, self.spectrometer_dock, Qt.Vertical)

        # SCHRITT F: Größenverhältnisse anpassen
        # Da "Experiments" flach sein soll, ändern wir das Verhältnis zu Spectrometer.
        # Wir sagen: Exp soll klein, Spectrometer groß sein.
        self.resizeDocks([self.experiment_dock, self.spectrometer_dock], [100, 500], Qt.Vertical)
        
        # Wir geben der SMU rechts etwas mehr Breite, falls nötig
        self.resizeDocks([self.spectrometer_dock, self.smu_dock], [400, 400], Qt.Horizontal)


        # --- 6. Menu & Corner ---
        menu_bar = self.menuBar()
        self.view_menu = menu_bar.addMenu("View")
        
        docks = [self.experiment_dock, self.spectrometer_dock, self.smu_dock, 
                 self.waterfall_dock, self.liveplot_dock, self.hdf5viewer_dock,self.sweep_dock]
        for dock in docks:
            self.view_menu.addAction(dock.toggleViewAction())

        corner_widget = QWidget(self)
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(5)

        self.issue_btn = QToolButton(self)
        self.issue_btn.setText("Issue?")
        self.issue_btn.setAutoRaise(True)
        self.issue_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Silas-Hoerz/Modulab/issues")))

        gh_icon_path = resource_path(os.path.join('resources', 'github.svg')) 
        self.github_btn = QToolButton(self)
        self.github_btn.setIcon(QIcon(gh_icon_path))
        self.github_btn.setAutoRaise(True)
        self.github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Silas-Hoerz/Modulab")))

        corner_layout.addWidget(self.issue_btn)
        corner_layout.addWidget(self.github_btn)
        self.menuBar().setCornerWidget(corner_widget, Qt.TopRightCorner)

        # --- 7. Signale ---
        self.log_widget.request_profile_dialog.connect(self.show_profile_dialog)
        self.log_widget.request_device_dialog.connect(self.show_device_dialog)
        self.context.export_manager.export_finished.connect(self.on_export_finished_ui)
        
        self.setWindowState(Qt.WindowMaximized) 

    def show_profile_dialog(self):
        self.profile_widget_dialog.exec()

    def show_device_dialog(self):
        self.device_widget_dialog.exec()

    @Slot(str)
    def on_export_finished_ui(self, filepath):
        self.hdf5viewer_widget.load_file(filepath)
        self.hdf5viewer_dock.setVisible(True)
        self.hdf5viewer_dock.raise_()
        self.hdf5viewer_dock.activateWindow()