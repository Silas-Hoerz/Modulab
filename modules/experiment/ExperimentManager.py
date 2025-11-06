"""
context:
Ich entwickle eine Software für das Labor eines instituts an einer Universität. Diese Software ist möglichst modular wartbar und erwiterbar. Sie besitzt ein pySide6 UI. Ich habe bereits einige Module entwickelt, das wäre ein ProfileManager dieser legt kann Profile anlegen und laden. Ein Profil bietet die möglichkeit Profilspezifische informationen zu speichern, bspw. gibt es ein Modul devices dies kümmert sich um die geometrische abmessungen und sonstige eigenschaften des zu vermessenen bauttiels diese werden auch im Profil gespeichert. Es gibt bereits ein Modul Log das sich um alle logging dinge kümmert. es fängt alle infos errors ab und hat auch eine ansicht im UI. Der erste Use case der software ist folgender: Wir nehmen elektroluminiszenz messungen an bautteilen auf einem wafer vor. dazu muss das Device mit Piezos positioniert werden (später HAL Position) dann wird eine spannung oder stromvon einer SMU via nadeln auf dem device eingeprägt, dann wir das emittierte spektrum des devices gemessen. Dieses soll verarbeitet werden mit allen nötigen infos und in einem Origin kompatiblen Format abgespeichert werden.Das ist aktuell die Basis. Ich möchte eine sauber Kapselung zwischen den Modulen, sprich keine große python datei wo keiner mehr durchblickt. Der Ablauf eines Experiments sollte möglichst abstrakt sein (set_pos(x,y,z), set_SMU(v,i), get_spectrum(), get_realVI(), export(data)) dazu möchte ich custom python scripte laden können die dann nach anwendung schnell und einfach angepasst werden können. diese sollen dann ausführbar sein. wichtig ist mir wissenschaftlich zu arbeiten sprich die erhobenen daten sollen repräsentativ sein. wie sieht es mit mehrfach messungen aus. nur der durchschnitt würde evtl. das ergebniss verfälschen... Das müssen wir sauber ausarbeiten. Wie soll die modulstruktur sein. Jedes Modul hat bei mir einen Manager. dieser hat get set funktionen etc. und kümmert sich geschlossen um seine aufgabe er hat nach ausßen kaum schnittstellen. bspw. der SmuManager soll sich nur um die ansteuerung initialisierung des SMU kümmer er kennt kein UI sondern erfüllt nur die Kernaufgabe. ich habe dann noch bspw. SmuWidget das noch eine grafische benutzeroberfläche zu der SMU bietet und die öffentlichen Funktionen des Managers nutzt. Das ist aktuell meine Struktur. Ich habe jetzt mit dem ExperimentManager begonnen dieser soll ein dateiverzeichnis anlegen, User scripte suchen können. und auch user scripte laden und abspielen können mit pausier funktion etc. das User script soll dann später möglichst abstrakt die Experimente durchführen analysen machen und auch exportieren.
"""



# ExperimentAPI ist ganz unten in der Datei definiert dort müssen neue Module referenziert werden, die API stellt 
# die Schnittstelle zwischen dem User Experiment Script und den echten Managern/Modulen dar.

import os, sys , importlib.util
from PySide6.QtCore import QObject, Signal, Slot, QDir, QThread




# ==========================================================================================
# ExperimentManager
# ==========================================================================================

class ExperimentManager(QObject):
    """
    Verantwortlich für das Laden und Ausführen von Experiment-Skripten in einem separaten Thread.
    """

    # Signale für die YouEye (o )_(o )
    experiments_found = Signal(list)
    experiment_started = Signal()
    experiment_finished = Signal()
    experiment_error = Signal(str)

    # Pause / Resume??? Progress??? vllt später
    progress_updated = Signal(int,str)

    def __init__(self, log_manager = None, profile_manager = None, device_manager = None):
        super().__init__()
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager
        self.device_mgr = device_manager

        self.api = ExperimentAPI(self.log_mgr, self.profile_mgr, self.device_mgr) 

        self.working_dir = os.path.join(os.path.expanduser('~'),'Modulab','Experiments')
        self.experiment_files = {}
        self.worker_thread = None # Die Ausführung des Experiments soll in einem eigenen Thread stattfinden unabhängig vom rest dieser wunderschönen modularen Softwarearchitektur
        self.worker = None

        try:
            os.makedirs(self.working_dir, exist_ok = True)
            self.log_mgr.debug(f"Working Dir: '{self.working_dir}'")
        except Exception as e:
            self.log_mgr.error(f"Directory could not be created: {e}")
        
    def search_experiments(self):
        """
        Sucht nach Python-Skripten im Arbeitsverzeichnis
        """
        self.experiment_files = {}
        if not os.path.exists(self.working_dir):
            self.log_mgr.warning(f"Working directory '{self.working_dir}' does not exist.")
            return self.experiment_files
        
        qdir = QDir(self.working_dir)
        py_files = qdir.entryList(["*.py"], QDir.Files)

        display_names = []

        for file_name in py_files:
            display_name = file_name.replace(".py", "")
            full_path = os.path.join(self.working_dir, file_name)
            self.experiment_files[display_name] = full_path
            display_names.append(display_name)
            # self.script_combo.addItem(display_name) # Das ist aufgabe vom Widget bzw. View
        self.experiments_found.emit(display_names)

    @Slot(str)
    def start_experiment(self, experiment_name):
        """
        Startet die Ausführung des Experiments im eigenen Thread
        """
        if self.worker_thread and self.worker_thread.isRunning():
            self.log_mgr.warning("Experiment is already running.")
            return
        
        if experiment_name not in self.experiment_files:
            self.log_mgr.error(f"Experiment '{experiment_name}' not found.")
            return
        
        experiment_path = self.experiment_files[experiment_name]

        self.worker_thread = QThread()
        self.worker = ExperimentWorker(self.api, experiment_path)
        self.worker.moveToThread(self.worker_thread)

        self.worker.finished.connect(self.on_worker_finished)
        self.worker.error.connect(self.on_worker_error)

        self.worker.progress_updated.connect(self.on_worker_progress)

        self.worker_thread.started.connect(self.worker.run)

        self.worker_thread.start()
        self.experiment_started.emit()
        self.log_mgr.info(f"Experiment started: {experiment_name}")

    @Slot()
    def on_worker_finished(self):
        """ Aufrämen nach Beendigung des Experiments """
        self.log_mgr.info("Experiment finished.")
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker_thread = None
        self.worker = None
        self.experiment_finished.emit()
     
    @Slot(str)
    def on_worker_error(self, error_message):
        """ Fehlerbehandlung """
        self.log_mgr.error(f"Experiment error: {error_message}")
        self.experiment_error.emit(error_message)
        self.on_worker_finished() # Aufrämen 



    @Slot()
    def pause_experiment(self):
        if self.worker:
            self.worker.pause()

    @Slot()
    def resume_experiment(self):
        if self.worker:
            self.worker.resume()

    @Slot()
    def stop_experiment(self):
        if self.worker:
            self.worker.stop()

    @Slot(int, str)
    def on_worker_progress(self, percent, message):
        self.progress_updated.emit(percent, message)




# ==========================================================================================
# ExperimentWorker
# ==========================================================================================


class ExperimentWorker(QObject):
    """ Führt das Experiment-Skript in einem eigenen Thread aus. """
    finished = Signal()
    error = Signal(str)
    progress_updated = Signal(int, str) # z.B. (Prozent, Nachricht)

    def __init__(self, api, experiment_path):
        super().__init__()
        self.api = api
        self.experiment_path = experiment_path

        # Signale an die API weiterleiten
        self.api._is_paused = False
        self.api._is_stopped = False
    
    @Slot()
    def run(self):
        """ Lädt und führt das Experiment-Skript aus. """
        try:
            self.api.log_mgr.info(f"Loading experiment script: {self.experiment_path}")

            spec = importlib.util.spec_from_file_location("user_experiment", self.experiment_path)
            user_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_module)

            if not hasattr(user_module, "run_experiment"):
                raise AttributeError("Experiment script must define a 'run_experiment(api)' function.")
            
            self.api.log_mgr.info("Starting experiment...")                         
            user_module.run_experiment(self.api)               
            self.api.log_mgr.info("Experiment completed successfully.")

        except ExperimentStoppedException:
            self.error.emit("Experiment was stopped by user.")
        except Exception as e:
            self.api.log_mgr.error(f"Experiment error: {e}")
            self.error.emit(str(e))
        finally:
            self.finished.emit()
    
    @Slot()
    def pause(self):
        self.api._is_paused = True
        self.api.log_mgr.info("Experiment paused by user.")
    
    @Slot()
    def resume(self):
        self.api._is_paused = False
        self.api.log_mgr.info("Experiment resumed by user.")
    
    @Slot()
    def stop(self):
        self.api._is_stopped = True
        self.api.log_mgr.info("Experiment stop requested by user.")




# ==========================================================================================
# ExperimentAPI
# ==========================================================================================

# Schnittstelle für Experiment-Skripte, um mit den Managern und Modulen zu interagieren. 
# Neue Module, die im Experiment-Skript verwendet werden sollen, müssen hier referenziert werden.
# Good Luck! 

class ExperimentAPI():
    def __init__ (self, log_manager, profile_manager, device_manager):      # <- Hier Manager einbinden
        self.log_mgr = log_manager
        self.profile_mgr = profile_manager
        self.device_mgr = device_manager
        # self.next_mgr = next_manager                                      # <- Hier 

        self._is_paused = False
        self._is_stopped = False


    # !!!
    # Die Folgenden Funktionen sind vereinfache Schnittstellen zu den Managern/Modulen
    # Es kann auch direkt auf die Manager/Module zugegriffen werden 
    # über bspw. api.device_mgr.get_device("device_name") 
    # Die Öffentlichen Funktionen findet man in den Manager/Modul Klassen. No shit, Sherlock...
    # Das wäre natürlich flexibler, aber auch komplexer für den User.
    
    
 
    def log_message(self, msg):
        """Ermöglicht dem Skript, in das Haupt-Log zu schreiben."""
        self.log_mgr.info(f"[USER SCRIPT] {msg}")

# Eigene Exception für sauberen Stopp
class ExperimentStoppedException(Exception):
    pass