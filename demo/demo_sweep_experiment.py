import numpy as np
import time

# Das Script muss eine Funktion 'run_experiment(api)' definieren.
# 'api' ist die Instanz der ExperimentAPI, die Zugriff auf alle Manager bietet.

def run_experiment(api):
    """
    Führt einen I/V-Sweep (-1V bis +1V) durch und nimmt bei jedem Schritt 
    ein Spektrum auf. Speichert alles in einer HDF5-Datei.
    """
    
    # --- 1. SETUP & KONFIGURATION ---
    api.log_message("=== Starte Demo-Experiment ===")
    
    # Parameter definieren
    start_v = -1.0
    stop_v = 1.0
    steps = 11  # Anzahl der Punkte
    integration_time_us = 50 * 1000 # 50 ms
    smu_channel = 'a'
    
    # Verbindung zu den Geräten herstellen
    if not api.smu_mgr.is_connected():
        # Versuche Verbindung zum letzten Gerät oder DUMMY falls kein echtes da ist
        if not api.smu_mgr.connect_LastDevice():
            api.log_message("Kein SMU gefunden. Verbinde mit DUMMY...")
            api.smu_mgr.connect("DUMMY")

    if not api.spectrometer_mgr.is_connected():
        # Versuche Verbindung, sonst Abbruch (Spectrometer hat meist keinen Dummy)
        if not api.spectrometer_mgr.connect_LastDevice():
            api.log_message("ACHTUNG: Kein Spektrometer verbunden! Versuche Auto-Connect...")
            device_list = api.spectrometer_mgr.get_deviceList()
            if device_list:
                api.spectrometer_mgr.connect(device_list[0])
            else:
                api.log_message("Kein Spektrometer gefunden. Spektren werden leer sein.")

    # --- 2. DEVICE MANAGEMENT ---
    # Wir simulieren, dass wir an einem bestimmten Pixel messen.
    dev_name = "Demo_Pixel_01"
    
    # Prüfen ob Device existiert, sonst erstellen (Guter Showcase für DeviceManager)
    device = api.device_mgr.get_device_by_name(dev_name)
    if not device:
        api.log_message(f"Erstelle neues Device: {dev_name}")
        api.device_mgr.create_device(
            name=dev_name, 
            geometry="rectangle", 
            length=2e-3, # 2mm
            width=2e-3,  # 2mm
            tags=["Demo", "Perovskite"]
        )
    
    # Device aktiv setzen, damit wir später darauf referenzieren können
    api.device_mgr.set_active_device(dev_name)
    active_area = api.device_mgr.get_active_device_area()

    # --- 3. HARDWARE KONFIGURATION ---
    
    # SMU Config
    api.smu_mgr.reset_channel(smu_channel)
    api.smu_mgr.set_source_voltage(smu_channel) # Wir geben Spannung vor
    api.smu_mgr.set_source_limit(smu_channel, 0.01) # 10mA Compliance
    
    # Spectrometer Config
    api.spectrometer_mgr.set_integrationtime(integration_time_us)
    api.spectrometer_mgr.set_correction_dark_count(True)

    # --- 4. EXPORT VORBEREITUNG ---
    
    # Optional: User nach Speicherort fragen (oder einfach Standard nutzen)
    api.export_mgr.select_directory_dialog() 
    
    # HDF5 Datei erstellen
    filename = f"Sweep_{dev_name}"
    if not api.export_mgr.new(filename, dataset_name ="IV_Spectroscopy"):
        api.log_mgr.error("Konnte Export nicht starten. Abbruch.")
        return

    # Statische Metadaten schreiben (Wird nur 1x gespeichert!)
    api.export_mgr.add_static("Device_Name", dev_name)
    api.export_mgr.add_static("Active_Area", active_area, "m^2")
    api.export_mgr.add_static("Integration_Time", integration_time_us, "us")
    api.export_mgr.add_group_attribute("Operator", "Modulab User")

    # Trick: Einmal Spektrum aufnehmen, um die Wellenlängen-Achse zu bekommen.
    # Diese ändert sich während des Sweeps nicht, also speichern wir sie statisch!
    wl, _ = api.spectrometer_mgr.acquire_spectrum()
    if wl is not None:
        api.export_mgr.add_static("Wavelengths", wl, "nm")

    # --- 5. MESS-SCHLEIFE (Der eigentliche Sweep) ---
    
    api.log_message("Starte Sweep...")
    api.smu_mgr.set_output_state(smu_channel, True) # Output ON

    try:
        voltage_points = np.linspace(start_v, stop_v, steps)
        
        for i, v_set in enumerate(voltage_points):
            # A) Check ob User Pause/Stop gedrückt hat (via API Flags)
            if api._is_stopped: 
                raise Exception("Abbruch durch Benutzer.")
            while api._is_paused:
                time.sleep(0.1)

            # B) Hardware ansteuern
            api.smu_mgr.set_source_level(smu_channel, v_set) # Spannung setzen
            time.sleep(0.1) # Kurze Wartezeit zum Einschwingen

            # C) Messen
            curr, meas_v = api.smu_mgr.measure_iv(smu_channel) or (float('nan'), float('nan'))
            
            # Spektrum aufnehmen (nur Intensitäten interessieren uns hier dynamisch)
            _, intensities = api.spectrometer_mgr.acquire_spectrum()

            # D) Daten Sammeln (Staging)
            api.export_mgr.add("Voltage_Set", v_set, "V")
            api.export_mgr.add("Voltage_Meas", meas_v, "V")
            api.export_mgr.add("Current", curr, "A")
            
            # Berechnete Größe (z.B. Stromdichte J) live hinzufügen
            if active_area and active_area > 0:
                api.export_mgr.add("Current_Density", curr / active_area, "A/m^2")

            if intensities is not None:
                # Wir speichern hier nur die Intensitäten. Die Wellenlängen (x-Achse) 
                # haben wir oben schon statisch gespeichert -> Spart Speicherplatz!
                api.export_mgr.add("Spectra_Dynamic", intensities, "counts")

            # E) Commit: Daten schreiben & Live-Plot updaten
            api.export_mgr.commit()
            
            # Log & Progress Update
            progress = int((i + 1) / steps * 100)
            api.log_message(f"Step {i+1}/{steps}: {meas_v:.2f} V -> {curr:.2e} A")

    except Exception as e:
        api.log_mgr.error(f"Fehler während des Experiments: {e}")
        raise e # Weiterwerfen damit Worker Bescheid weiß

    finally:
        # --- 6. CLEANUP ---
        # Dieser Block wird IMMER ausgeführt, auch bei Fehlern.
        api.log_message("Räume auf...")
        
        # Sicherstellen, dass Spannung weg ist
        api.smu_mgr.set_output_state(smu_channel, False)
        
        # Export Datei sauber schließen
        api.export_mgr.stop()
        
        api.log_message("Experiment beendet.")