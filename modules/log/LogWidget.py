# modules/log/LogWidget.py
import os
import sys
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QLabel, QSizePolicy
from PySide6.QtCore import Slot, Signal, QTimer, QSize, Qt
from PySide6.QtGui import QColor, QTextCursor, QIcon

from .ui_LogWidget import Ui_Form

# Hilfsfunktion für Pfade (muss verfügbar sein, kopiere ich hier rein zur Sicherheit)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LogWidget(QWidget, Ui_Form):
    
    # Farben für den Text
    COLOR_ERROR_FG = "#FF4545" # Helles Rot für Dark Mode
    COLOR_WARNING_FG = "#FFB000"
    COLOR_INFO_FG = "#DDDDDD"
    COLOR_DEBUG_FG = "#808080" # Grau

    # Priority Levels für Status Label (Höher = Wichtiger)
    PRIORITY_NONE = 0
    PRIORITY_INFO = 1
    PRIORITY_WARNING = 2
    PRIORITY_ERROR = 3

    request_profile_dialog = Signal()
    request_device_dialog = Signal()

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.context = context
        self.log_mgr = context.log_manager
        self.profile_mgr = context.profile_manager
        self.device_mgr = context.device_manager

        # --- 1. UI Erweiterung: Filter Buttons ---
        self._init_filter_toolbar()

        # --- 2. Initialzustand ---
        self.status_label.setChecked(False)
        self.history_text.setVisible(False)
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(150)
        
        # --- 3. Status Label Logik Variablen ---
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._reset_status_label)
        self._current_priority = self.PRIORITY_NONE

        # --- 4. Verbindungen ---
        self.status_label.toggled.connect(self.on_toggle_expand)
        self.log_mgr.message_logged.connect(self.on_new_message)

        # Profil & Device Signale
        if self.profile_mgr and hasattr(self.profile_mgr, "profile_loaded"):
            self.profile_mgr.profile_loaded.connect(self.on_profile_changed)
        if self.device_mgr and hasattr(self.device_mgr, "device_loaded"):
            self.device_mgr.device_loaded.connect(self.on_device_changed)

        self.pushButton_profile.clicked.connect(self.on_profile_clicked)
        self.pushButton_device.clicked.connect(self.on_device_clicked)

        # Initial laden
        self.__load_history()

    def _init_filter_toolbar(self):
        """Erstellt nachträglich eine Toolbar über dem Textfeld."""
        # Wir holen uns das Layout, in dem history_text liegt (verticalLayout_2 in ui file)
        layout = self.verticalLayout_2
        
        # Neue Toolbar Layout
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setContentsMargins(0,0,0,0)
        self.filter_layout.setSpacing(2)
        
        # Buttons erstellen
        self.btn_error = self._create_filter_btn("Error", "error24dp.svg", True)
        self.btn_warn = self._create_filter_btn("Warning", "warning24dp.svg", True)
        self.btn_info = self._create_filter_btn("Info", "info24dp.svg", True)
        self.btn_debug = self._create_filter_btn("Debug", "bug24dp.svg", False) # Default aus
        
        # Spacer damit Buttons links sind
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.filter_layout.addWidget(self.btn_error)
        self.filter_layout.addWidget(self.btn_warn)
        self.filter_layout.addWidget(self.btn_info)
        self.filter_layout.addWidget(self.btn_debug)
        self.filter_layout.addWidget(spacer)

        # Toolbar ÜBER dem Textfeld einfügen (Index 0)
        layout.insertLayout(0, self.filter_layout)
        
        # Toolbar initial verstecken, nur zeigen wenn Log ausgeklappt
        self._set_toolbar_visible(False)

    def _create_filter_btn(self, tooltip, icon_name, checked):
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setToolTip(f"Show {tooltip}")
        btn.setAutoRaise(True)
        # Icon laden
        icon_path = resource_path(os.path.join('resources', icon_name))
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(20, 20))
        # Stylesheet für visuelles Feedback beim Check
        btn.setStyleSheet("""
            QToolButton { border: 1px solid transparent; border-radius: 3px; }
            QToolButton:checked { background-color: rgba(255, 255, 255, 40); border: 1px solid gray; }
            QToolButton:hover { background-color: rgba(255, 255, 255, 20); }
        """)
        btn.clicked.connect(self._repopulate_log_text)
        return btn

    def _set_toolbar_visible(self, visible):
        # Wir iterieren über die Items im Layout, um sie zu verstecken/zeigen
        for i in range(self.filter_layout.count()):
            item = self.filter_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setVisible(visible)

    # --- Logik für Textfeld ---

    def _repopulate_log_text(self):
        """Löscht das Textfeld und füllt es basierend auf den Filtern neu."""
        self.history_text.clear()
        all_msgs = self.log_mgr.get_all_messages()
        
        # Um Performance zu sparen bei riesigen Logs, könnte man hier slicen (z.B. letzte 1000)
        for msg in all_msgs:
            self._append_if_allowed(msg)

    def _append_if_allowed(self, log_entry):
        msg_type = log_entry['type']
        
        # Filter Prüfung
        show = False
        if msg_type == self.log_mgr.ERROR and self.btn_error.isChecked(): show = True
        elif msg_type == self.log_mgr.WARNING and self.btn_warn.isChecked(): show = True
        elif msg_type == self.log_mgr.INFO and self.btn_info.isChecked(): show = True
        elif msg_type == self.log_mgr.DEBUG and self.btn_debug.isChecked(): show = True
        
        if show:
            self.__add_message_to_history_widget(log_entry)

    def __add_message_to_history_widget(self, log_entry):
        """Rein visuelles Hinzufügen (ohne Logik-Prüfung)"""
        msg_type = log_entry['type']
        
        if msg_type == self.log_mgr.ERROR: color = self.COLOR_ERROR_FG
        elif msg_type == self.log_mgr.WARNING: color = self.COLOR_WARNING_FG
        elif msg_type == self.log_mgr.DEBUG: color = self.COLOR_DEBUG_FG
        else: color = self.COLOR_INFO_FG

        self.history_text.setTextColor(QColor(color))
        time_str = log_entry['timestamp'].strftime('%H:%M:%S')
        # Icons im Text wären auch möglich, aber Text reicht meistens
        msg = f"[{time_str}] [{log_entry['type']}] {log_entry['message']}"
        self.history_text.append(msg)

    def __load_history(self):
        self._repopulate_log_text()
        # Status Label initialisieren (letzten nicht-debug status suchen)
        msgs = self.log_mgr.get_all_messages()
        for msg in reversed(msgs):
            if msg['type'] != self.log_mgr.DEBUG:
                self.__update_status_label(msg)
                break

    # --- Die neue STATUS LABEL Logik ---

    def __update_status_label(self, log_entry):
        """
        Intelligente Status-Aktualisierung mit Priority Locking und Cooldown.
        """
        msg_type = log_entry['type']
        
        # 1. Priorität der neuen Nachricht ermitteln
        new_priority = self.PRIORITY_NONE
        timeout = 2000 # Standard 2s (Info)

        if msg_type == self.log_mgr.ERROR:
            new_priority = self.PRIORITY_ERROR
            timeout = 5000 # Error bleibt 5s
        elif msg_type == self.log_mgr.WARNING:
            new_priority = self.PRIORITY_WARNING
            timeout = 4000
        elif msg_type == self.log_mgr.INFO:
            new_priority = self.PRIORITY_INFO
            timeout = 2000
        elif msg_type == self.log_mgr.DEBUG:
            # Debug zeigen wir im Status Label gar nicht an (zu viel Rauschen)
            return

        # 2. Check: Darf die neue Nachricht die alte überschreiben?
        # Wenn aktuell eine höhere Prio läuft UND der Timer noch aktiv ist -> Ignorieren
        if self._current_priority > new_priority and self._status_timer.isActive():
            # Ausnahme: Wenn es genau die gleiche Nachricht ist, verlängern wir vielleicht?
            # Hier: Einfach ignorieren ("Info" soll "Error" nicht verdrängen)
            return

        # 3. Nachricht anzeigen
        self._current_priority = new_priority
        
        # Style setzen (für Farben via CSS im UI File)
        if msg_type == self.log_mgr.ERROR:
            self.status_label.setProperty("logStatus", "error")
        elif msg_type == self.log_mgr.WARNING:
            self.status_label.setProperty("logStatus", "warning")
        else:
            self.status_label.setProperty("logStatus", "info")

        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        
        self.status_label.setText(log_entry['message'])
        
        # 4. Timer starten (Restart, falls er schon lief)
        self._status_timer.start(timeout)

    @Slot()
    def _reset_status_label(self):
        """Wird vom Timer aufgerufen, wenn Cooldown vorbei ist."""
        self.status_label.setText("Ready")
        self.status_label.setProperty("logStatus", "info") # Reset Farbe
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
        
        self._current_priority = self.PRIORITY_NONE

    # --- Slots ---

    @Slot(dict)
    def on_new_message(self, log_entry):
        # 1. Textfeld Update (nur wenn Filter passt)
        self._append_if_allowed(log_entry)
        
        # 2. Scroll-to-bottom wenn sichtbar
        if self.history_text.isVisible():
            self.history_text.moveCursor(QTextCursor.End)
            
        # 3. Status Label Update
        self.__update_status_label(log_entry)

    @Slot(bool)
    def on_toggle_expand(self, is_checked):
        self.history_text.setVisible(is_checked)
        self._set_toolbar_visible(is_checked) # Toolbar auch toggeln
        
        if is_checked:
            self.history_text.moveCursor(QTextCursor.End)

    @Slot(str)
    def on_profile_changed(self, profile_name):
        self.pushButton_profile.setText(f"Profile: {profile_name}" if profile_name else "No Profile")

    @Slot(str)
    def on_device_changed(self, device_name):
        self.pushButton_device.setText(f"Device: {device_name}" if device_name else "No Device")

    @Slot()
    def on_profile_clicked(self): self.request_profile_dialog.emit()
    
    @Slot()
    def on_device_clicked(self): self.request_device_dialog.emit()