# core/mainwindow.py
# This Python file uses the following encoding: utf-8

from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QDialog
from PySide6.QtCore import Qt, Slot

from core.ui_form import Ui_MainWindow
from core.context import ApplicationContext 

# Views importieren
from modules.log.LogWidget import LogWidget
from modules.device.DeviceWidget import DeviceWidget
from modules.profile.ProfileWidget import ProfileWidget
from modules.spectrometer.SpectrometerWidget import SpectrometerWidget

from modules.experiment.ExperimentWidget import ExperimentWidget


class MainWindow(QMainWindow):
    
    # Die Signatur ist jetzt sauber: nur noch EIN 'context'-Argument
    def __init__(self, context: ApplicationContext, parent=None):
        
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Den Kontext für später speichern
        self.context = context
        
        # --- Log Widget ---
        # Das LogWidget bekommt den gesamten Kontext
        self.log_widget = LogWidget(context=self.context, parent=self)
        self.ui.statusbar.addWidget(self.log_widget, 1)

        # --- Profile Widget ---
        # Das ProfileWidget bekommt den gesamten Kontext
        self.profile_widget_dialog = ProfileWidget(context=self.context, parent=self)
    
        # --- Device Widget ---
        # Das DeviceWidget bekommt AUCH den gesamten Kontext
        self.device_widget_dialog = DeviceWidget(context=self.context, parent=self)

        # --- Spectrometer Widget ---
        self.spectrometer_widget = SpectrometerWidget(context = self.context, parent=self)
        self.spectrometer_dock = QDockWidget("Spectrometer",self)
        self.spectrometer_dock.setObjectName("Spectrometer")
        self.spectrometer_dock.setWidget(self.spectrometer_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.spectrometer_dock)

        # --- Experiment Widget ---
        self.experiment_widget = ExperimentWidget(context=self.context, parent=self)
        self.experiment_dock = QDockWidget("Experiments", self)
        self.experiment_dock.setObjectName("Experiments") 
        self.experiment_dock.setWidget(self.experiment_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.experiment_dock)

        # --- Menu Bar ---
        menu_bar = self.menuBar()
        self.view_menu = menu_bar.addMenu("View")
        self.view_menu.addAction(self.spectrometer_dock.toggleViewAction())
        self.view_menu.addAction(self.experiment_dock.toggleViewAction())

        # Signale verbinden
        self.log_widget.request_profile_dialog.connect(self.show_profile_dialog)
        self.log_widget.request_device_dialog.connect(self.show_device_dialog)

        # --- Startup Aktionen ---
        self.show_profile_dialog()
        self.show_device_dialog()


    def show_profile_dialog(self):
        result = self.profile_widget_dialog.exec()

    def show_device_dialog(self):
        result = self.device_widget_dialog.exec()
        pass