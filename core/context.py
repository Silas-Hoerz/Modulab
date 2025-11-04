# core/context.py
# This Python file uses the following encoding: utf-8

# Manager importieren
from modules.log.LogManager import LogManager
from modules.profile.ProfileManager import ProfileManager
from modules.device.DeviceManager import DeviceManager, Device

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
        
        
        
        self.log_manager.debug("ApplicationContext successfully initialized.")