# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from ui_form import Ui_MainWindow

# Manager importieren
from modules.log.LogManager import LogManager
from modules.profile.ProfileManager import ProfileManager
from modules.device.DeviceManager import DeviceManager

# View importieren
from mainwindow import MainWindow


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Manager initialisieren
    log_mgr = LogManager()
    profile_mgr = ProfileManager(log_manager = log_mgr)
    device_mgr = DeviceManager(log_manager = log_mgr, profile_manager = profile_mgr)

    # Views initialisieren


    main_window = MainWindow(log_manager=log_mgr, profile_manager = profile_mgr, device_manager = device_mgr)
    main_window.show()

    print("Profil anlegen")
    print(profile_mgr.create_profile("TEst1"))
    print("Profil laden")
    print(profile_mgr.load_profile("TEst1"))
    print("Profil writen")
    print(profile_mgr.write("last_used", "23.10.2025_10:15" ))
    print("Profil read")
    print(profile_mgr.read("last_used"))
    print("Profil writen")
    print(profile_mgr.write("last_used", "23.10.2025_10:18" ))
    print("Profil read")
    print(profile_mgr.read("last_used"))


    
    log_mgr.info("Info!!!!!!!!!!!!!!!!")
    log_mgr.warning("Warnung!!!!!!!!!!!!!!!!")
    log_mgr.debug("Debug!!!!!!!!!!!!!!!!")
    log_mgr.error("Error!!!!!!!!!!!!!!!!")


    sys.exit(app.exec())
