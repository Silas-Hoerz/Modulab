import numpy as np
import time

def run_experiment(api):
    """
    IVL-Sweep: Nur Visualisierung im Live-Plot.
    Speicherung erfolgt explizit durch den User über den 'Export'-Button im Tab.
    """
    log = api.log_mgr
    smu = api.smu_mgr
    spec = api.spectrometer_mgr
    # export = api.export_mgr
    plot = api.liveplot_mgr
    dev_mgr = api.device_mgr
    profile = api.profile_mgr

    # 1. Parameter & Metadaten sammeln
    start_v = -2.0; end_v = 5.0; steps = 20; channel = 'a'
    
    metadata = {
        "Created_By": profile.read("User_Name") or "Unknown",
        "Date": time.strftime("%Y-%m-%d %H_%M_%S"),
        "Sweep_Start": start_v,
        "Sweep_End": end_v,
        "Device": "None"
    }
    
    active_dev = dev_mgr.get_active_device()
    if active_dev:
        metadata["Device"] = active_dev.name
        metadata["Area_m2"] = active_dev.get_area()

    # Hardware Init
    if not smu.is_connected(): smu.connect("DUMMY")
    
    # 2. Live Plot Session starten (Mit Metadaten!)
    session = f"IVL {time.strftime('%H_%M_%S')}"
    plot.start_session(session, metadata=metadata)
    
    # Plots definieren
    plot.define_plot(session, "iv_lin", "J-V Linear", "Voltage [V]", "Current Density [mA/cm^2]")
    plot.define_plot(session, "iv_log", "J-V Log", "Voltage [V]", "Log J [mA/cm^2]", log_y=True)
    
    # 3. Messung
    smu.reset_channel(channel)
    smu.set_source_voltage(channel)
    smu.set_source_limit(channel, 0.1)
    smu.set_output_state(channel, True)
    
    voltages = np.linspace(start_v, end_v, steps)
    log.info("Starte Sweep (Daten werden im LivePlot gesammelt)...")

    try:
        for i, v in enumerate(voltages):
            if api._is_stopped: break
            while api._is_paused: time.sleep(0.1)

            # SMU
            smu.set_source_level(channel, v)
            time.sleep(0.1)
            curr, meas_v = smu.measure_iv(channel) or (0,0)
            
            # Berechnung Dichte
            area = active_dev.get_area() if active_dev else 1.0
            if area == 0: area = 1.0
            j = (curr / area) * 0.1 # A/m^2 -> mA/cm^2 (Faktor 0.1 stimmt nicht ganz, 1A/m2 = 0.1mA/cm2)
            # A/m^2 = 1000 mA / 10000 cm^2 = 0.1 mA/cm^2. Korrekt.

            # Daten an Plot senden
            plot.append_data(session, "iv_lin", meas_v, j)
            # Log Plot (abs + epsilon)
            plot.append_data(session, "iv_log", meas_v, abs(j) + 1e-12)

            log.info(f"Step {i+1}/{steps}: {meas_v:.2f}V")

    except Exception as e:
        log.error(f"Fehler: {e}")
    
    finally:
        smu.set_source_level(channel, 0)
        smu.set_output_state(channel, False)
        plot.stop_session(session)
        log.info("Messung fertig. Bitte Tab exportieren zum Speichern!")