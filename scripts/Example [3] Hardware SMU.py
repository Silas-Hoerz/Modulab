import time

def run_experiment(api):
    """
    Führt einen einfachen Voltage-Sweep auf der SMU durch.
    Zeigt die Nutzung der neuen, sicheren SMU-Methoden.
    """
    logger = api.log_mgr
    smu = api.smu_mgr

    # 1. Verbinden
    # Wir nutzen 'connect_LastDevice', um das Profil zu respektieren
    if not smu.is_connected():
        if not smu.connect_LastDevice():
            smu.connect("DUMMY")

    logger.info(f"Verbunden mit: {smu.get_activeDeviceName()}") 

    channel = 'a'

    # 2. Kanal konfigurieren (Werte werden im Profil gespeichert!)
    smu.reset_channel(channel)
    smu.set_sense_local(channel)        
    smu.set_source_voltage(channel)     
    smu.set_source_limit(channel, 0.1)  # 100mA Limit
    
    # 3. Output einschalten
    smu.set_output_state(channel, True)

    logger.info("Starte Sweep...")
    
    # Wir nutzen hier KEINEN LivePlot, sondern schauen nur auf das Dashboard
    for i in range(5):
        if api._is_stopped: break
        
        voltage_target = i * 1.0
        smu.set_source_level(channel, voltage_target)
        
        time.sleep(0.5) # Langsam, damit man das Dashboard beobachten kann
        
        result = smu.measure_iv(channel)
        if result:
            current, voltage = result
            logger.info(f"Set: {voltage_target}V -> Meas: {voltage:.3f}V, {current:.3e}A")

    # 4. Aufräumen
    smu.set_source_level(channel, 0.0)
    smu.set_output_state(channel, False)
    # smu.disconnect() -> Lassen wir verbunden für weitere Tests