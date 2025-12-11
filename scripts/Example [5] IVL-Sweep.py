import numpy as np
import time

def run_experiment(api):
    """
    IVL-Sweep mit Datenspeicherung.
    
    Demonstriert:
    1. Automatische Dark-Correction des Managers.
    2. Speicherung der Rohdaten und Korrekturdaten zur Validierung.
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
    
    # Hardware Checks
    if not smu.is_connected():
        log.warning("SMU nicht verbunden! Nutze DUMMY.")
        smu.connect("DUMMY")
    
    # --- 2. Export vorbereiten ---
    # Neue HDF5 Datei anlegen
    if not export.new("IVL_Sweep_Valid", dataset_name="IVL_Data"):
        log.error("Konnte Export-Datei nicht erstellen.")
        return

    # 2a. Statische Metadaten (User, Device, etc.)
    export.add_static("Operator", "User")
    
    active_dev = dev_mgr.get_active_device()
    if active_dev:
        export.add_static("Device_Name", active_dev.name)
        export.add_static("Device_Area", active_dev.get_area(), "m^2")

    # 2b. DARK SPECTRUM REFERENZ SPEICHERN ("Anhang")
    # Da sich das Dark Spectrum während des Sweeps nicht ändert, speichern wir es 
    # einmalig als statische Referenz. Das spart Speicherplatz und gilt als "Anhang".
    
    # Info: Neue Dark-Messung kann im Manager via GUI oder spec.acquire_dark_spectrum(n) gemacht werden.
    if spec.is_connected():
        dark_avg = spec.get_dark_spectrum_average()
        
        if dark_avg is not None:
            # Wir speichern das Referenz-Dunkelspektrum, das aktuell für die Korrektur genutzt wird
            export.add_static("Appendix_Dark_Spectrum_Avg", dark_avg, "counts")
            log.info("Dunkelspektrum-Referenz wurde in HDF5 gespeichert.")
        else:
            log.warning("Kein Dunkelspektrum im Manager hinterlegt (Korrektur ist inaktiv oder leer).")
            # Wir können optional vermerken, dass ohne Dark Correction gemessen wurde
            export.add_static("Info_Dark_Correction", "None")


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
            
            # Abbruchbedingungen
            if api._is_stopped: 
                log.info("Experiment vom User gestoppt.")
                break
            while api._is_paused:
                time.sleep(0.1)

            # A) SMU setzen & messen
            smu.set_source_level(channel, v_target)
            time.sleep(0.1) # Warten auf Stabilität
            val_current, val_voltage = smu.measure_iv(channel) or (0, 0)
            
            # B) Spektrometer messen
            # Wir holen uns hier BEIDE Varianten für volle Nachvollziehbarkeit
            spectrum_corr = np.zeros(10) # Fallback
            spectrum_raw = np.zeros(10)  # Fallback
            
            if spec.is_connected():
                # 1. Das korrigierte Spektrum (Standard für Plots)
                # Zieht automatisch das gespeicherte Dark Spectrum ab, falls vorhanden.
                _, spectrum_corr = spec.acquire_spectrum()
                
                # 2. Das Roh-Spektrum (Zur Überprüfung / Nachrechnung)
                # Holt die Daten direkt vom Sensor ohne Abzug.
                _, spectrum_raw = spec.acquire_spectrum_raw()
                
                # Safety checks falls Fehler auftraten
                if spectrum_corr is None: spectrum_corr = np.zeros(10)
                if spectrum_raw is None: spectrum_raw = np.zeros(10)


            # C) Daten stagen
            export.add("Voltage", val_voltage, "V")
            export.add("Current", val_current, "A")
            export.add("Set_Voltage", v_target, "V")
            
            # Spektren speichern
            export.add("Spectrum", spectrum_corr, "counts (corrected)")
            export.add("Spectrum_Raw", spectrum_raw, "counts (raw)")
            
            # Stromdichte
            if active_dev and active_dev.get_area() > 0:
                j = val_current / active_dev.get_area()
                export.add("J", j * 0.1, "mA/cm^2")

            # D) Commit: Schreibt Zeile in HDF5
            export.commit()

            # Log
            log.info(f"Step {i+1}/{steps}: {val_voltage:.2f}V")

    except Exception as e:
        log.error(f"Fehler im Ablauf: {e}")
    
    finally:
        # --- 5. Abschluss ---
        smu.set_source_level(channel, 0)
        smu.set_output_state(channel, False)
        export.stop()
        log.info("Messung beendet.")