import numpy as np
import time

def run_experiment(api):
    """
    Kompletter IVL-Sweep mit Datenspeicherung und Live-Plotting.
    """
    # Manager Referenzen holen
    log = api.log_mgr
    smu = api.smu_mgr
    spec = api.spectrometer_mgr
    export = api.export_mgr 
    dev_mgr = api.device_mgr

    # --- 1. Parameter Setup ---
    start_v = -2.0
    end_v = 5.0
    steps = 20
    channel = 'a'
    
    # Sicherstellen, dass Hardware verbunden ist
    if not smu.is_connected():
        log.warning("SMU nicht verbunden! Nutze DUMMY.")
        smu.connect("DUMMY")
        
    # --- 2. Export vorbereiten ---
    # Dialog um Ordner zu wählen (oder festen Pfad nutzen) 
    # save_path = export.select_directory_dialog() 
    
    # Neue HDF5 Datei anlegen
    if not export.new("OLED_IVL_Sweep", dataset_name="IVL_Data"):
        log.error("Konnte Export-Datei nicht erstellen.")
        return

    # Statische Metadaten speichern (einmalig) 
    export.add_static("Operator", "User")
    
    active_dev = dev_mgr.get_active_device()
    if active_dev:
        export.add_static("Device_Name", active_dev.name)
        export.add_static("Device_Area", active_dev.get_area(), "m^2")

    # --- 3. Messung vorbereiten ---
    smu.reset_channel(channel)
    smu.set_source_voltage(channel)
    smu.set_source_limit(channel, 0.05) # 50mA Limit
    smu.set_output_state(channel, True)
    
    voltages = np.linspace(start_v, end_v, steps)
    
    log.info("Starte Messschleife...")

    try:
        # --- 4. Messschleife ---
        for i, v_target in enumerate(voltages):
            
            # Prüfen ob User Pause/Stop gedrückt hat
            if api._is_stopped: 
                log.info("Experiment vom User gestoppt.")
                break
            while api._is_paused:
                time.sleep(0.1)

            # A) SMU setzen & messen
            smu.set_source_level(channel, v_target)
            time.sleep(0.1) # Warten auf Stabilität
            
            val_current, val_voltage = smu.measure_iv(channel) or (0, 0)
            
            # B) Spektrometer messen (nur wenn "an", z.B. Spannung > 2.5V)
            # Hier simulieren wir ein Spektrum, falls kein Gerät da ist
            spectrum_int = np.zeros(100)
            if spec.is_connected():
                 _, spectrum_int = spec.acquire_spectrum()
                 if spectrum_int is None: spectrum_int = np.zeros(100)

            # C) Daten für Export stagen (fügt sie zum Puffer hinzu) 
            # Diese Keys ('Voltage', 'Current') werden im LivePlotWidget als Titel genutzt
            export.add("Voltage", val_voltage, "V")
            export.add("Current", val_current, "A")
            export.add("Set_Voltage", v_target, "V")
            
            # Spektrum als Array speichern
            export.add("Spectrum", spectrum_int, "counts")
            
            # Stromdichte berechnen (wenn Device vorhanden)
            if active_dev and active_dev.get_area() > 0:
                j = val_current / active_dev.get_area() # A/m^2
                j_mA_cm2 = j * 0.1 # Umrechnung
                export.add("J", j_mA_cm2, "mA/cm^2")

            # D) Commit: Schreibt Daten in Datei & sendet sie an Plot
            export.commit()

            # Progress update
            progress_pct = int((i + 1) / steps * 100)
            log.info(f"Step {i+1}/{steps}: {val_voltage:.2f}V -> {val_current:.2e}A")

    except Exception as e:
        log.error(f"Fehler im Ablauf: {e}")
    
    finally:
        # --- 5. Abschluss ---
        smu.set_source_level(channel, 0)
        smu.set_output_state(channel, False)
        
        # Datei schließen 
        export.stop()
        log.info("Messung beendet.")