# modules/experiment/ExperimentWidget.py
# This Python file uses the following encoding: utf-8

import sys
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot, Signal

# Importiere die generierte UI-Klasse
try:
    # Stelle sicher, dass deine UI-Datei "ui_ExperimentWidget.py" heißt
    from .ui_ExperimentWidget import Ui_Form 
except ImportError:
    print("Fehler: Konnte 'ui_ExperimentWidget.py' nicht finden.")
    # Notfall-Fallback, damit der Code nicht crasht
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    class Ui_Form:
        def setupUi(self, Form):
            Form.setObjectName("Experiment")
            self.vLayout = QVBoxLayout(Form)
            self.label_progress = QLabel("UI File not loaded", Form)
            self.vLayout.addWidget(self.label_progress)
        def retranslateUi(self, Form):
            pass

class ExperimentWidget(QWidget, Ui_Form):
    """
    Diese Klasse verwaltet das Experiment-UI-Panel.
    Sie verbindet die UI-Elemente (Buttons, ComboBox) mit dem ExperimentManager.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Manager aus dem Kontext-Objekt holen
        self.exp_mgr = context.experiment_manager
        self.log_mgr = context.log_manager

        # Internen Status für den Pause/Resume-Toggle-Button
        self.is_paused = False

        self.__setup_ui()
        self.__connect_signals()

        # Beim Start sofort nach Experimenten suchen
        self.exp_mgr.search_experiments()

    def __setup_ui(self):
        """Setzt den anfänglichen Zustand der UI-Elemente."""
        self.label_progress.setText("Bereit.")
        self.pushButton_start.setEnabled(True)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_pause.setText("Pause")
        self.is_paused = False

    def __connect_signals(self):
        """Verbindet alle Signale und Slots."""
        
        # 1. UI-Elemente (Buttons) an Manager-Slots
        self.pushButton_start.clicked.connect(self.on_start_clicked)
        self.pushButton_pause.clicked.connect(self.on_pause_clicked)
        self.pushButton_stop.clicked.connect(self.exp_mgr.stop_experiment)

        # 2. Manager-Signale an UI-Slots (diese Klasse)
        self.exp_mgr.experiments_found.connect(self.on_experiments_found)
        self.exp_mgr.experiment_started.connect(self.on_experiment_started)
        
        # WICHTIG: Den korrigierten Signalnamen verwenden!
        self.exp_mgr.experiment_finished.connect(self.on_experiment_finished) 
        
        self.exp_mgr.experiment_error.connect(self.on_experiment_error)
        
        # Verbinde das neue Progress-Signal mit dem UI-Slot
        self.exp_mgr.progress_updated.connect(self.on_progress_updated)

    # --- Slots für UI-Aktionen ---

    @Slot()
    def on_start_clicked(self):
        """Wird aufgerufen, wenn der Start-Button geklickt wird."""
        selected_script = self.comboBox_experiments.currentText()
        
        if not selected_script:
            self.log_mgr.warning("Kein Experiment-Skript ausgewählt.")
            self.label_progress.setText("Bitte ein Skript auswählen.")
            return
        
        # Den Manager anweisen, das Experiment zu starten
        self.exp_mgr.start_experiment(selected_script)

    @Slot()
    def on_pause_clicked(self):
        """Toggelt den Pause/Resume-Zustand."""
        if self.is_paused:
            # Zustand war "Paused", also jetzt "Resuming"
            self.exp_mgr.resume_experiment()
            self.pushButton_pause.setText("Pause")
            self.label_progress.setText("Setze fort...")
            self.is_paused = False
        else:
            # Zustand war "Running", also jetzt "Pausing"
            self.exp_mgr.pause_experiment()
            self.pushButton_pause.setText("Resume")
            self.label_progress.setText("Pausiert.")
            self.is_paused = True

    # --- Slots für Signale vom ExperimentManager ---

    @Slot(list)
    def on_experiments_found(self, script_names):
        """Füllt die ComboBox, wenn der Manager Skripte gefunden hat."""
        self.comboBox_experiments.clear()
        self.comboBox_experiments.addItems(script_names)
        if script_names:
            self.label_progress.setText(f"{len(script_names)} Experimente gefunden.")
            self.pushButton_start.setEnabled(True)
        else:
            self.label_progress.setText("Keine Experimente im Ordner gefunden.")
            self.pushButton_start.setEnabled(False)

    @Slot()
    def on_experiment_started(self):
        """Aktualisiert die UI, wenn ein Experiment startet."""
        self.label_progress.setText("Experiment gestartet...")
        self.pushButton_start.setEnabled(False)
        self.comboBox_experiments.setEnabled(False) # Auswahl sperren
        self.pushButton_pause.setEnabled(True)
        self.pushButton_stop.setEnabled(True)
        
        # Sicherstellen, dass der Button-Status korrekt ist
        self.pushButton_pause.setText("Pause")
        self.is_paused = False

    @Slot()
    def on_experiment_finished(self):
        """Setzt die UI zurück, wenn ein Experiment beendet ist."""
        self.label_progress.setText("Experiment erfolgreich beendet.")
        self.pushButton_start.setEnabled(True)
        self.comboBox_experiments.setEnabled(True) # Auswahl freigeben
        self.pushButton_pause.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_pause.setText("Pause")
        self.is_paused = False

    @Slot(str)
    def on_experiment_error(self, error_msg):
        """Setzt die UI zurück und zeigt eine Fehlermeldung an."""
        self.label_progress.setText(f"Fehler: {error_msg}")
        # UI zurücksetzen (fast wie bei "finished")
        self.pushButton_start.setEnabled(True)
        self.comboBox_experiments.setEnabled(True)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_pause.setText("Pause")
        self.is_paused = False

    @Slot(int, str)
    def on_progress_updated(self, percent, message):
        """Aktualisiert das Progress-Label (sofern nicht pausiert)."""
        if not self.is_paused:
            # Prozentanzeige (falls übergeben) oder nur Nachricht
            if percent > 0:
                self.label_progress.setText(f"[{percent}%] {message}")
            else:
                self.label_progress.setText(message)