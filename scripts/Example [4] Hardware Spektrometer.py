import numpy as np

def run_experiment(api):
    """
    Nimmt ein Spektrum auf und analysiert den Peak.
    """
    logger = api.log_mgr
    spec = api.spectrometer_mgr # Zugriff auf SpectrometerManager 

    # 1. Verbinden (Sucht automatisch oder nimmt letztes Gerät) 
    if not spec.is_connected():
        logger.info("Versuche Verbindung zum Spektrometer...")
        # Alternativ: spec.connect("Seriennummer")
        if not spec.connect_LastDevice():
            # Wenn kein letztes Gerät, nimm das erste verfügbare
            devices = spec.get_deviceList()
            if devices:
                spec.connect(devices[0])
            else:
                logger.error("Kein Spektrometer gefunden.")
                return

    # 2. Konfiguration
    integration_time_us = 50000 # 50ms
    spec.set_integrationtime(integration_time_us)
    spec.set_correction_dark_count(True) # Dark Counts abziehen

    logger.info(f"Integration time set to {spec.get_integrationtime()} us")

    # 3. Spektrum aufnehmen
    wavelengths, intensities = spec.acquire_spectrum()

    if wavelengths is not None:
        # Einfache Analyse
        max_idx = np.argmax(intensities)
        peak_wl = wavelengths[max_idx]
        peak_int = intensities[max_idx]
        
        logger.info(f"Spektrum aufgenommen. Peak bei {peak_wl:.1f}nm (Int: {peak_int})")
    else:
        logger.error("Fehler bei der Spektrum-Aufnahme.")