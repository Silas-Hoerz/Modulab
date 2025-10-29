# This Python file uses the following encoding: utf-8

from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PySide6.QtCore import Qt

from ui_form import Ui_MainWindow

# Module importieren
from  modules.profile.ProfileManager import ProfileManager


# View importieren
from modules.log.LogWidget import LogWidget

class MainWindow(QMainWindow):
    def __init__(self,log_manager, profile_manager, parent=None):
        
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Manager speichern
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager
        
        # --- Log Widget ---
        self.log_widget = LogWidget(log_manager = self.log_mgr, parent = self)
        self.ui.statusbar.addWidget(self.log_widget,1)



        
