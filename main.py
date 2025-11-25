# main.py
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QRect
from qt_material import apply_stylesheet

import sys, os
from core.context import ApplicationContext
from core.mainwindow import MainWindow
import core.std_includes

# python -m venv .venv  
# .venv/Scripts/Activate.ps1
# python -m pip install --upgrade pip
# pip install -r requirements.txt

# Build:
# pyinstaller --noconfirm Modulab.spec 

def resource_path(relative_path):
    """ Ermittelt den absoluten Pfad zu Ressourcen, funktioniert für dev und PyInstaller """
    try:
        # PyInstaller erstellt einen temporären Ordner in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
   
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # Originalbild laden
    image_path = resource_path("resources/logo.png")
    pixmap = QPixmap(image_path)

    # --- Zuschneiden & Skalieren auf 600x400 ---
    target_width, target_height = 600, 400
    # Erst auf Zielgröße skalieren (verzerrt, falls nötig)
    scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    
    # Optional: Du könntest auch einen Ausschnitt aus dem Originalbild nehmen:
    # rect = QRect(0, 0, target_width, target_height)
    # scaled_pixmap = pixmap.copy(rect)

    # SplashScreen erstellen
    splash = QSplashScreen(scaled_pixmap, Qt.WindowStaysOnTopHint)

    # Splash zentrieren
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - target_width) // 2
    y = (screen_geometry.height() - target_height) // 2
    splash.move(x, y)

    splash.show()

    # --- Kontext & MainWindow ---
    app_context = ApplicationContext()
    main_window = MainWindow(context=app_context)

    # Splash für kurze Zeit anzeigen, dann MainWindow zeigen
    QTimer.singleShot(150, splash.close)
    QTimer.singleShot(150, main_window.show)

    # Profile- und Device-Dialoge danach
    def show_startup_dialogs():
        main_window.show_profile_dialog()
        main_window.show_device_dialog()

    QTimer.singleShot(1600, show_startup_dialogs)

    sys.exit(app.exec())
