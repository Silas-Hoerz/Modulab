# This Python file uses the following encoding: utf-8
import os

from .ui_LogWidget import Ui_Form

from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout, QTextEdit, QLabel
# from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Slot # QFile, QIODevice,
from PySide6.QtGui import QColor, QTextCursor

class LogWidget(QWidget, Ui_Form):
    """

    """

    # --- Farbdefinitionen für die Logik ---
    COLOR_ERROR_BG = "#C00000"
    COLOR_ERROR_FG = "#C00000"
    COLOR_WARNING_BG = "#FF9000"
    COLOR_WARNING_FG = "#FF9000"
    COLOR_INFO_BG = "transparent"
    COLOR_INFO_FG = "#DDDDDD"
    COLOR_DEBUG_FG = "gray"


    def __init__(self, log_manager, parent=None):

        super().__init__(parent)

        self.setupUi(self)


        self.log_mgr = log_manager


        # # Ui File laden
        # ui_file_path = os.path.join(os.path.dirname(__file__), "LogWidget.ui")

        # if not os.path.exists(ui_file_path):
        #     print(f"FATAL: UI-Datei nicht gefunden unter: {ui_file_path}")
        #     # Fallback, damit es nicht crasht
        #     self.setLayout(QVBoxLayout())
        #     self.layout().addWidget(QLabel("Fehler: LogWidget.ui nicht gefunden!"))
        #     return

        # ui_file = QFile(ui_file_path)
        # if not ui_file.open(QIODevice.ReadOnly):
        #     print(f"FATAL: Konnte UI-Datei nicht öffnen: {ui_file_path}")
        #     return

        # loader = QUiLoader()

        # widget = loader.load(ui_file, self)
        # ui_file.close()

        # layout = QVBoxLayout(self)
        # layout.addWidget(widget)

        # layout.setContentsMargins(0, 0, 0, 0)
        # self.setLayout(layout)

        # self.status_label = widget.findChild(QCheckBox, "status_label")
        # self.history_text = widget.findChild(QTextEdit, "history_text")

        # if not self.status_label or not self.history_text:
        #     print("'status_label' oder 'history_text' in LogWidget.ui nicht gefunden!")
        #     return

        # # Ui File vollständig geladen puhh

        self.status_label.setChecked(False)
        self.history_text.setVisible(False)
        self.history_text.setReadOnly(True)

        self.status_label.toggled.connect(self.on_toggle_expand)

        self.__load_history()
        self.log_mgr.message_logged.connect(self.on_new_message)

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
