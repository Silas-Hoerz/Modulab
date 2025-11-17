# Modulab - Spektrometer- und SMU-Steuerung

Modulab ist eine Desktop-Anwendung zur Steuerung und Datenerfassung von Spektrometern (insbesondere Ocean Optics Geräten) und Source Measure Units (SMUs) wie dem Keithley 2602. Die Software ermöglicht die Konfiguration von Geräten, die Aufnahme von Messdaten (z.B. Spektren), deren Visualisierung und die Verwaltung von Geräteprofilen.

## Funktionen

*   **Spektrometer-Steuerung:** Konfiguration und Datenerfassung von Ocean Optics Spektrometern.
*   **SMU-Steuerung:** Ansteuerung von Keithley 2602 SMUs für präzise Messungen.
*   **Datenakquise:** Erfassung von Spektren und elektrischen Messdaten.
*   **Visualisierung:** Anzeige von Messdaten in Echtzeit.
*   **Profilverwaltung:** Speichern und Laden von Gerätekonfigurationen.
*   **Logging:** Umfassende Protokollierung aller Vorgänge.

## Installation und Nutzung (Portable EXE)

Modulab wird als portable ausführbare Datei (`.exe`) bereitgestellt, die keine Installation erfordert.

1.  **Herunterladen:** Laden Sie die neueste Version der `Modulab.exe` von [Link zur Download-Quelle, falls vorhanden] herunter.
2.  **Ausführen:** Speichern Sie die `Modulab.exe` an einem beliebigen Ort auf Ihrem System und starten Sie sie per Doppelklick.

**Hinweis:** Stellen Sie sicher, dass die erforderlichen Treiber für Ihre Spektrometer- und SMU-Geräte auf Ihrem System installiert sind, damit Modulab die Geräte erkennen und steuern kann.

## Entwicklung

Für Entwickler und zur Erstellung der ausführbaren Datei:

1.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Portable EXE erstellen (mit PyInstaller):**
    ```bash
    pyinstaller --name Modulab --onefile --windowed --icon=resources/logo.ico --add-data "resources;resources" --add-data "docs;docs" --hidden-import=seabreeze.backends.cseabreeze main.py
    ```
    Dieser Befehl erstellt die `Modulab.exe` im `dist/` Verzeichnis.

---

