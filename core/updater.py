import sys
import os
import subprocess
import requests
import tempfile
from packaging import version
from PySide6.QtCore import QObject, QThread, Signal, QUrl, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtGui import QDesktopServices
from core.constants import APP_VERSION

# Konstanten
GITHUB_REPO = "Silas-Hoerz/Modulab"
CURRENT_VERSION = APP_VERSION

class UpdateChecker(QThread):
    """Prüft im Hintergrund auf Updates via GitHub API"""
    update_found = Signal(str, str, str) # version, url, release_notes
    no_update = Signal()

    def run(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                remote_tag = data.get("tag_name", "0.0.0").lstrip("v")
                
                # Semantic Version Check
                if version.parse(remote_tag) > version.parse(CURRENT_VERSION):
                    # Suche nach der .exe in den Assets
                    assets = data.get("assets", [])
                    download_url = ""
                    for asset in assets:
                        if asset["name"].endswith(".exe"):
                            download_url = asset["browser_download_url"]
                            break
                    
                    if download_url:
                        self.update_found.emit(remote_tag, download_url, data.get("body", ""))
                        return

            self.no_update.emit()
        except Exception as e:
            print(f"Update Check Error: {e}")
            self.no_update.emit()

class Downloader(QThread):
    """Lädt die Datei herunter und meldet den Fortschritt"""
    progress = Signal(int)
    finished = Signal(str) # Pfad zur heruntergeladenen Datei
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            # Temp Pfad für den Download
            temp_dir = tempfile.gettempdir()
            save_path = os.path.join(temp_dir, "Modulab_new.exe")
            
            downloaded = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)
            
            self.finished.emit(save_path)
        except Exception as e:
            self.error.emit(str(e))

class UpdateManager(QObject):
    """Verwaltet den gesamten Update-Prozess inkl. UI"""
    
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent = parent_window
        self.checker = None
        self.downloader = None
        self.download_url = ""
        self.new_version = ""

    def start_check(self):
        """Startet den Update-Check (Entry Point)"""
        self.checker = UpdateChecker()
        self.checker.update_found.connect(self._on_update_found)
        # Optional: Connect no_update, falls du eine Meldung willst, dass alles aktuell ist
        self.checker.start()

    def _on_update_found(self, new_version, url, notes):
        self.new_version = new_version
        self.download_url = url
        
        # Dialog anzeigen (Englisch)
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Update Available")
        msg.setText(f"Version {new_version} is available!\n\nRelease Notes:\n{notes}")
        msg.setInformativeText("Do you want to download and install the update now?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec() == QMessageBox.Yes:
            self._start_download()

    def _start_download(self):
        # Fortschrittsbalken erstellen (Englisch)
        self.progress_dialog = QProgressDialog("Downloading update...", "Cancel", 0, 100, self.parent)
        
        # FIX: Hier verwenden wir jetzt Qt.WindowModal statt True
        self.progress_dialog.setWindowModality(Qt.WindowModal) 
        self.progress_dialog.setMinimumDuration(0)
        
        self.downloader = Downloader(self.download_url)
        self.downloader.progress.connect(self.progress_dialog.setValue)
        self.downloader.finished.connect(self._install_update)
        # Error Message (Englisch)
        self.downloader.error.connect(lambda e: QMessageBox.critical(self.parent, "Error", f"Download failed: {e}"))
        
        self.downloader.start()

    def _install_update(self, new_exe_path):
        self.progress_dialog.close()
        
        # WICHTIG: Prüfen ob wir als EXE laufen (PyInstaller)
        if not getattr(sys, 'frozen', False):
            # Warnung im Dev Mode (Englisch)
            QMessageBox.warning(self.parent, "Dev Mode", "Update downloaded, but automatic restart cannot be performed in developer mode.\nThe file is located at: " + new_exe_path)
            return

        # Installations-Frage (Englisch)
        reply = QMessageBox.question(self.parent, "Installation", "Download complete. The application needs to restart. Restart now?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self._perform_restart_mechanism(new_exe_path)

    def _perform_restart_mechanism(self, new_exe_path):
        """Erstellt ein Batch-Skript, das die alte Exe löscht und die neue platziert"""
        current_exe = sys.executable
        directory = os.path.dirname(current_exe)
        
        # Batch-Script Inhalt
        # 1. Warten (damit Main App schließen kann)
        # 2. Verschieben der neuen Exe über die alte
        # 3. Starten der neuen Exe
        # 4. Löschen des Batch Scripts selbst
        bat_script = f"""
@echo off
timeout /t 2 /nobreak > NUL
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
        """
        
        bat_path = os.path.join(directory, "update_installer.bat")
        with open(bat_path, "w") as f:
            f.write(bat_script)
            
        # Batch starten und App beenden
        subprocess.Popen([bat_path], shell=True)
        sys.exit(0)