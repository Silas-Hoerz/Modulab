# modules/log/LogWidget.py
# This Python file uses the following encoding: utf-8
import os

from .ui_LogWidget import Ui_Form

from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout, QTextEdit, QLabel
# from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QColor, QTextCursor

class LogWidget(QWidget, Ui_Form):
    """
    Status Leiste mit ausklappbarem Log-Fenster.
    """
    # Farben haben hier nichts zu suchen, aber egal...
    # --- Farbdefinitionen für die Logik ---
    COLOR_ERROR_FG = "#C00000"
    COLOR_WARNING_FG = "#FF9000"
    COLOR_INFO_FG = "#DDDDDD"
    COLOR_DEBUG_FG = "gray"

    # Signale um Dialoge anzufordern
    request_profile_dialog = Signal()
    request_device_dialog = Signal()

    def __init__(self, context, parent=None):

        super().__init__(parent)

        self.setupUi(self)

        self.log_mgr = context.log_manager
        self.profile_mgr = context.profile_manager
        self.device_mgr = context.device_manager

        self.status_label.setChecked(False)
        self.history_text.setVisible(False)
        self.history_text.setReadOnly(True)

        self.status_label.toggled.connect(self.on_toggle_expand)

        self.__load_history()
        self.log_mgr.message_logged.connect(self.on_new_message)

        # Signale von Profil und Device: nur verbinden, wenn das Signal-Attribut existiert
        if self.profile_mgr and hasattr(self.profile_mgr, "profile_loaded"):
            try:
                self.profile_mgr.profile_loaded.connect(self.on_profile_changed)
            except Exception as e:
                self.log_mgr.error(f"Failed to connect profile_loaded: {e}")

        if self.device_mgr and hasattr(self.device_mgr, "device_loaded"):
            try:
                self.device_mgr.device_loaded.connect(self.on_device_changed)
            except Exception as e:
                self.log_mgr.error(f"Failed to connect device_loaded: {e}")

        # Hat nicht viel mit Logs zu tun aber sollte in die Statusleiste passen
        self.pushButton_profile.clicked.connect(self.on_profile_clicked)
        self.pushButton_device.clicked.connect(self.on_device_clicked)

    @Slot(str)
    def on_profile_changed(self, profile_name):
        """
        Dieser Slot wird aufgerufen, wenn der ProfileManager
        das Signal 'profile_loaded' sendet.
        """
        if profile_name:
            # Setzt den Text (z.B. "Profil: Default")
            self.pushButton_profile.setText(f"Profile: {profile_name}")
        else:
            self.pushButton_profile.setText("No Profile")
    @Slot(str)
    def on_device_changed(self, device_name):
        """
        Dieser Slot wird aufgerufen, wenn der DeviceManager
        das Signal 'device_loaded' sendet.
        """
        if device_name:
            self.pushButton_device.setText(f"Device: {device_name}")
        else:
            self.pushButton_device.setText("No Device")

    @Slot()
    def on_profile_clicked(self):
        self.request_profile_dialog.emit()
    @Slot()
    def on_device_clicked(self):
        self.request_device_dialog.emit()

    def __load_history(self):
        """ Lädt alle bisherigen Logs beim Start """
        all_msg = self.log_mgr.get_all_messages()
        if not all_msg:
            return
        for msg in all_msg:
            self.__add_message_to_history(msg)

        if all_msg:
            for msg in all_msg:
                self.__add_message_to_history(msg)

        latest_status_msg = None
        for msg in reversed(all_msg):
            if msg['type'] != self.log_mgr.DEBUG:
                latest_status_msg =msg
                break

        if latest_status_msg:
            self.__update_status_label(latest_status_msg)

    def __add_message_to_history(self, log_entry):
        """ Fügt einen Eintrag dem Textfeld hinzu (mit Farbe). """
        msg_type = log_entry['type']

        if msg_type == self.log_mgr.ERROR:
            color = self.COLOR_ERROR_FG
        elif msg_type == self.log_mgr.WARNING:
            color = self.COLOR_WARNING_FG
        elif msg_type == self.log_mgr.DEBUG:
            color = self.COLOR_DEBUG_FG
        else:
            color = self.COLOR_INFO_FG

        self.history_text.setTextColor(QColor(color))

        time_str = log_entry['timestamp'].strftime('%H:%M:%S')
        msg = f"[{time_str}] [{log_entry['type']}] {log_entry['message']}"
        self.history_text.append(msg)

        self.history_text.moveCursor(QTextCursor.End)

    def __update_status_label(self, log_entry):
        """ Aktualisiert das Label (mit Farbe) """

        msg_type = log_entry['type']

        if msg_type == self.log_mgr.ERROR:
            self.status_label.setProperty("logStatus", "error")
        elif msg_type == self.log_mgr.WARNING:
            self.status_label.setProperty("logStatus", "warning")
        else: # INFO
            self.status_label.setProperty("logStatus", "info")

        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        self.status_label.update()

        self.status_label.setText(log_entry['message'])

    @Slot(dict)
    def on_new_message(self, log_entry):
        """
        Slot wird aufgerufen, wenn der LogManager eine neue Nachricht sendet.
        """
        self.__add_message_to_history(log_entry)
        if log_entry['type'] != self.log_mgr.DEBUG:
            self.__update_status_label(log_entry)

    @Slot(bool)
    def on_toggle_expand(self, is_checked):
        """
        Slot zum aus oder einklappen des 'history_text'
        """
        print("click")
        self.history_text.setVisible(is_checked)
        if is_checked:
            self.history_text.moveCursor(QTextCursor.End)
