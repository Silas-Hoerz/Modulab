import numpy as np
import time

def run_experiment(api):
    """
    IVL-Sweep mit Multi-Plot (Linear + Logarithmisch) in EINEM Tab.
    """
    # 1. Manager holen (Lokale Variablen)
    log_mgr = api.log_mgr
    smu_mgr = api.smu_mgr
    spectrometer_mgr = api.spectrometer_mgr 
    export_mgr = api.export_mgr 
    liveplot_mgr = api.liveplot_mgr 
    device_mgr = api.device_mgr

    # 2. Parameter
    start_v = -2.0
    end_v = 5.0
    steps = 100
    channel = 'a'
    
    if not smu_mgr.is_connected():
        log_mgr.warning("SMU nicht verbunden! Nutze DUMMY.")
        smu_mgr.connect("DUMMY")
    
    # --- Live Plot Setup (Multi-Plot) ---
    session = "IVL Sweep"
    
    # 1. Tab erstellen
    liveplot_mgr.start_session(session)
    
    # 2. Plots definieren (werden ins Grid gepackt)
    # Plot A: Linear
    liveplot_mgr.define_plot(session, "lin_iv", "Linear IV", "Voltage [V]", "Current [A]")
    
    # Plot B: Logarithmisch (Absolutwert)
    liveplot_mgr.define_plot(session, "log_iv", "Log IV (|I|)", "Voltage [V]", "Log Current [A]", log_y=True)
    
    # Plot C: Spektrum (optional)
    if spectrometer_mgr.is_connected():
        liveplot_mgr.define_plot(session, "spec", "Last Spectrum", "Wavelength", "Counts")

    # --- Export Setup ---
    if not export_mgr.new("IVL_Sweep_Live", dataset_name="IVL_Data"):
        log_mgr.error("Export Fehler.")
        return

    # Messung Vorbereiten
    smu_mgr.reset_channel(channel)
    smu_mgr.set_source_voltage(channel)
    smu_mgr.set_source_limit(channel, 0.05)
    smu_mgr.set_output_state(channel, True)
    
    voltages = np.linspace(start_v, end_v, steps)
    log_mgr.info("Starte Sweep...")

    try:
        for i, v_target in enumerate(voltages):
            if api._is_stopped: break
            while api._is_paused: time.sleep(0.1)

            # Messen
            smu_mgr.set_source_level(channel, v_target)
            time.sleep(0.1)
            val_current, val_voltage = smu_mgr.measure_iv(channel) or (0, 0)
            
            # Spektrum
            spectrum_corr = None
            if spectrometer_mgr.is_connected():
                wl, spectrum_corr = spectrometer_mgr.acquire_spectrum()

            # --- Daten an Plot senden ---
            # 1. Linear
            liveplot_mgr.append_data(session, "lin_iv", val_voltage, val_current)
            
            # 2. Logarithmisch (WICHTIG: Absolutwert für Log-Plot, da log(-x) nan ist)
            # PyQtGraph logMode macht log10(y). Wir müssen sicherstellen, dass y > 0 ist.
            # Bei logMode=True erwartet pg den rohen Wert, rechnet aber selbst.
            # Wir übergeben abs(I) + epsilon um 0 zu vermeiden.
            liveplot_mgr.append_data(session, "log_iv", val_voltage, abs(val_current) + 1e-13)

            # 3. Spektrum (Setzen statt Append)
            if spectrum_corr is not None:
                liveplot_mgr.set_data(session, "spec", wl, spectrum_corr)

            # --- Daten an Export senden ---
            export_mgr.add("Voltage", val_voltage, "V")
            export_mgr.add("Current", val_current, "A")
            if spectrum_corr is not None:
                export_mgr.add("Spectrum", spectrum_corr, "cnt")
            export_mgr.commit()

            log_mgr.info(f"Step {i+1}/{steps}: {val_voltage:.2f}V -> {val_current:.2e}A")

    except Exception as e:
        log_mgr.error(f"Fehler: {e}")
    
    finally:
        smu_mgr.set_source_level(channel, 0)
        smu_mgr.set_output_state(channel, False)
        export_mgr.stop()
        log_mgr.info("Fertig.")