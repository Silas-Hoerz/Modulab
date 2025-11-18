# main.py
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QRect

import sys
from core.context import ApplicationContext
from core.mainwindow import MainWindow
import core.std_includes

#pyinstaller --name Modulab --onefile --windowed --icon=resources/logo.ico --add-data "resources;resources" --add-data "docs;docs" --hidden-import=seabreeze.backends.cseabreeze main.py


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Originalbild laden
    pixmap = QPixmap("resources/logo.png")

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
    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, main_window.show)

    # Profile- und Device-Dialoge danach
    def show_startup_dialogs():
        main_window.show_profile_dialog()
        main_window.show_device_dialog()

    QTimer.singleShot(1600, show_startup_dialogs)

    sys.exit(app.exec())
