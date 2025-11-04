# main.py
# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication

# Importiere nur noch den Context und die MainWindow
from core.context import ApplicationContext
from core.mainwindow import MainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)

    # 1. Nur noch EINEN Manager-Kontext initialisieren
    app_context = ApplicationContext()

    # 2. Den Kontext an das Hauptfenster übergeben
    main_window = MainWindow(context=app_context)
    main_window.show()

    app_context.log_manager.error("Hauptfenster gestartet.")

    sys.exit(app.exec())