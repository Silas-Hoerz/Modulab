# modules/experiment/ExperimentWidget.py
# This Python file uses the following encoding: utf-8

import sys
import os
import webbrowser
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot, Signal, QEvent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DOC_PATH = os.path.join(PROJECT_ROOT, 'docs','_build', 'html', 'index.html')

# Importiere die generierte UI-Klasse
try:
    # Stelle sicher, dass deine UI-Datei "ui_ExperimentWidget.py" heißt
    from .ui_ExperimentWidget import Ui_Form 
except ImportError:
    print("Error: Could not find 'ui_ExperimentWidget.py'.")
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

        # Nur weil die Comboboxen kein opened Event haben ):
        self.comboBox_experiments.installEventFilter(self)

        # Beim Start sofort nach Experimenten suchen
        self.exp_mgr.search_experiments()

    def __setup_ui(self):
        """Setzt den anfänglichen Zustand der UI-Elemente."""
        self.label_progress.setText("Ready.")
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
        self.pushButton_docs.clicked.connect(self.on_docs_clicked)
        self.pushButton_edit.clicked.connect(self.on_edit_clicked)
        self.exp_mgr.experiments_found.connect(self.on_experiments_found)

        # 2. Manager-Signale an UI-Slots (diese Klasse)
        self.exp_mgr.experiments_found.connect(self.on_experiments_found)
        self.exp_mgr.experiment_started.connect(self.on_experiment_started)
        
        self.exp_mgr.experiment_finished.connect(self.on_experiment_finished) 
        
        self.exp_mgr.experiment_error.connect(self.on_experiment_error)
        
        # Verbinde das neue Progress-Signal mit dem UI-Slot
        self.exp_mgr.progress_updated.connect(self.on_progress_updated)

    # --- Slots für UI-Aktionen ---

    @Slot()
    def on_combobox_clicked(self):
        """
        Wenn Combobox geöffnet wird dann soll die liste aktualisiert werden
        """
        self.exp_mgr.search_experiments()



    @Slot()
    def on_start_clicked(self):
        """Wird aufgerufen, wenn der Start-Button geklickt wird."""
        selected_script = self.comboBox_experiments.currentText()
        
        if not selected_script:
            self.log_mgr.warning("No experiment script selected.")
            self.label_progress.setText("Please select a script.")
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
            self.label_progress.setText("Resuming...")
            self.is_paused = False
        else:
            # Zustand war "Running", also jetzt "Pausing"
            self.exp_mgr.pause_experiment()
            self.pushButton_pause.setText("Resume")
            self.label_progress.setText("Paused.")
            self.is_paused = True

    @Slot()
    def on_docs_clicked(self):
        """
        Öffnet die generierte Sphinx-Dokumentation im Standard-Webbrowser.
        """
        if not os.path.exists(DOC_PATH):
            print(f"Fehler: Dokumentation nicht gefunden unter {DOC_PATH}")
            print("Bitte zuerst die Doku mit Sphinx generieren (z.B. 'cd docs && make html').")
            return
            
        # 'file://' ist wichtig, um dem Browser zu sagen, dass es eine lokale Datei ist.
        webbrowser.open_new_tab(f"file://{DOC_PATH}")

    @Slot()
    def on_edit_clicked(self):
        selected_script = self.comboBox_experiments.currentText()
        
        if not selected_script:
            return
        experiment_path = self.exp_mgr.experiment_files[selected_script]
        

        os.startfile(experiment_path)
    # --- Slots für Signale vom ExperimentManager ---

    @Slot(list)
    def on_experiments_found(self, script_names):
        """Füllt die ComboBox, wenn der Manager Skripte gefunden hat."""
        self.comboBox_experiments.clear()
        self.comboBox_experiments.addItems(script_names)
        if script_names:
            self.label_progress.setText(f"{len(script_names)} experiment(s) found.")
            self.pushButton_start.setEnabled(True)
        else:
            self.label_progress.setText("No experiments found in folder.")
            self.pushButton_start.setEnabled(False)

    @Slot()
    def on_experiment_started(self):
        """Aktualisiert die UI, wenn ein Experiment startet."""
        self.label_progress.setText("Experiment started...")
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
        self.label_progress.setText("Experiment finished successfully.")
        self.pushButton_start.setEnabled(True)
        self.comboBox_experiments.setEnabled(True) # Auswahl freigeben
        self.pushButton_pause.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_pause.setText("Pause")
        self.is_paused = False

    @Slot(str)
    def on_experiment_error(self, error_msg):
        """Setzt die UI zurück und zeigt eine Fehlermeldung an."""
        self.label_progress.setText(f"Error: {error_msg}")
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


    ## Bitte ignorieren DAS IST NUR FÜR DIE COMBOBOX 
    def eventFilter(self, watched_object, event):
        """
        Fängt Events ab, bevor sie das beobachtete Widget erreichen.
        """
        # 1. Prüfen, ob das Event von unserer ComboBox kommt
        if watched_object == self.comboBox_experiments:
            
            # 2. Prüfen, ob das Event ein Mausklick ist
            if event.type() == QEvent.Type.MouseButtonPress:
                
                # 3. Prüfen, ob die Popup-Liste aktuell NICHT sichtbar ist
                #    (Wir wollen das Signal nur beim Öffnen, nicht beim Schließen)
                if not self.comboBox_experiments.view().isVisible():
                    # 4. Jetzt den Slot manuell aufrufen
                    self.on_combobox_clicked()

        # Wichtig: Das Event an die Basisklasse weiterleiten,
        # damit der Klick weiterhin verarbeitet wird (und das Popup öffnet).
        return super().eventFilter(watched_object, event)



