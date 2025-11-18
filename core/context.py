# core/context.py
# This Python file uses the following encoding: utf-8

# Manager importieren
from modules.log.LogManager import LogManager
from modules.profile.ProfileManager import ProfileManager
from modules.device.DeviceManager import DeviceManager, Device
from modules.experiment.ExperimentManager import ExperimentManager
from modules.export.ExportManager import ExportManager

from modules.spectrometer.SpectrometerManager import SpectrometerManager
from modules.smu.SmuManager import SmuManager

class ApplicationContext:
    """
    Ein zentraler "Service-Container", der alle Manager bündelt.
    Er wird einmal in main.py erstellt und dann durch die Anwendung
    gereicht.
    """
    def __init__(self):
        
        self.log_manager = LogManager()
        
        self.profile_manager = ProfileManager(
            log_manager=self.log_manager
        )
        
        self.device_manager = DeviceManager(
            log_manager=self.log_manager, 
            profile_manager=self.profile_manager
        )

        self.spectrometer_manager = SpectrometerManager(
            log_manager=self.log_manager, 
            profile_manager=self.profile_manager
        )

        self.smu_manager = SmuManager(
            log_manager=self.log_manager, 
            profile_manager=self.profile_manager
        )

        self.export_manager = ExportManager(
            log_manager=self.log_manager, 
            profile_manager=self.profile_manager
        )

        # Wir übergeben einfach den ganzen Kontext (self).
        # Damit hat der ExperimentManager Zugriff auf ALLES, was hier definiert ist.
        self.experiment_manager = ExperimentManager(context=self)
    
        
        
        self.log_manager.debug("ApplicationContext successfully initialized.")