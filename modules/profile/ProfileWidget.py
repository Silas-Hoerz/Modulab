# modules/profile/ProfileWidget.py
# This Python file uses the following encoding: utf-8

import os # Zugriff auf Dateisystem

try:
    from .ui_ProfileWidget import Ui_Form
except ImportError:
    print("Fehler: Konnte 'ui_ProfileWidget.py' nicht finden.")
    from PySide6.QtWidgets import QWidget
    class Ui_Form:
        def setupUi(self, Form):
            Form.setObjectName("Profile")

from PySide6.QtWidgets import QDialog, QMessageBox, QInputDialog
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QCloseEvent

class ProfileWidget(QDialog, Ui_Form):


    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.profile_mgr = context.profile_manager
        self.log_mgr = context.log_manager

        self.__setup_ui()

        try:
            last_profile = self.profile_mgr.get_last_profile_name()
            if last_profile:
                items = self.listWidget_profiles.findItems(last_profile, Qt.MatchExactly)
                if items:
                    self.listWidget_profiles.setCurrentItem(items[0])
        except Exception as e:
            self.log_mgr.error(f"Error selecting last active profile: {e}")
            
        self.__connect_signals()

    def __setup_ui(self):
        self.profile_names = self.profile_mgr.list_profiles()
        self.listWidget_profiles.clear()
        self.listWidget_profiles.addItems(self.profile_names)

    def __connect_signals(self):
        self.pushButton_new.clicked.connect(self.on_new_profile)
        self.pushButton_delete.clicked.connect(self.on_delete_profile)
        self.pushButton_done.clicked.connect(self.on_done)

    @Slot()
    def on_new_profile(self):
        profile_name, ok = QInputDialog.getText(self, "New Profile", "Type the name of the new profile:")
        if ok and profile_name:
            success = self.profile_mgr.create_profile(profile_name)
            if success:
                self.__setup_ui()
                # Neu erstelltes Profil auswählen
                try:
                    items = self.listWidget_profiles.findItems(profile_name, Qt.MatchExactly)
                    if items:
                        self.listWidget_profiles.setCurrentItem(items[0])
                except Exception as e:
                    self.log_mgr.error(f"Error selecting new profile: {e}")
                

    @Slot()
    def on_delete_profile(self):
        selected_items = self.listWidget_profiles.selectedItems()
        if not selected_items:
            return
        profile_name = selected_items[0].text()
        confirm = QMessageBox.question(self, "Delete Profile", f"Are you sure you want to delete profile '{profile_name}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            success = self.profile_mgr.delete_profile(profile_name)
            if success:
                self.__setup_ui()

               
    @Slot()
    def on_done(self):
        selected_items = self.listWidget_profiles.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to continue.")
            return
        profile_name = selected_items[0].text()
        success = self.profile_mgr.load_profile(profile_name)
        if success:
            # Sende neuen Profilnamen an LogWidget
            self.accept()
        else:
            
            QMessageBox.critical(self, "Error", f"Failed to load profile '{profile_name}'.")

    @Slot()
    def closeEvent(self, event: QCloseEvent):
        # Verhindert das Schließen über das 'X'-Symbol
        event.ignore()