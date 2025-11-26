# main.py
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

import sys, os
from core.context import ApplicationContext
from core.mainwindow import MainWindow
from core.constants import APP_VERSION
from core.updater import UpdateManager

# python -m venv .venv  
# .venv/Scripts/Activate.ps1
# python -m pip install --upgrade pip
# pip install -r requirements.txt

# Build:
# pyinstaller --noconfirm Modulab.spec 

def resource_path(relative_path):
    """ Ermittelt den absoluten Pfad zu Ressourcen, funktioniert für dev und PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
   
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")


    image_path = resource_path("resources/logo.png")
    pixmap = QPixmap(image_path)
    target_width, target_height = 600, 400
    scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(scaled_pixmap, Qt.WindowStaysOnTopHint)
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - target_width) // 2
    y = (screen_geometry.height() - target_height) // 2
    splash.move(x, y)
    splash.show()

    # --- Kontext & MainWindow ---
    app_context = ApplicationContext()
    main_window = MainWindow(context=app_context)

    QTimer.singleShot(150, splash.close)
    QTimer.singleShot(150, main_window.show)

    update_mgr = UpdateManager(main_window)

    # Profile- und Device-Dialoge danach
    def show_startup_dialogs():
        main_window.show_profile_dialog()
        main_window.show_device_dialog()

        update_mgr.start_check()

    QTimer.singleShot(1600, show_startup_dialogs)

    sys.exit(app.exec())
