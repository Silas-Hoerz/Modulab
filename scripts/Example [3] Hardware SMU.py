import time

def run_experiment(api):
    """
    Führt einen einfachen Voltage-Sweep auf der SMU durch.
    """
    logger = api.log_mgr
    smu = api.smu_mgr # Zugriff auf SmuManager 

    # 1. Verbinden (Nutze DUMMY für Tests ohne Hardware) 
    port = "DUMMY" 
    # port = "COM3" # Für echte Hardware
    
    if not smu.connect(port):
        logger.error("Konnte SMU nicht verbinden. Abbruch.")
        return

    logger.info(f"Verbunden mit: {smu.get_activeDeviceName()}") 

    channel = 'a'

    # 2. Kanal konfigurieren 
    smu.reset_channel(channel)
    smu.set_sense_local(channel)        # 2-Wire Messung
    smu.set_source_voltage(channel)     # Wir geben Spannung vor
    smu.set_source_limit(channel, 0.1)  # Strombegrenzung auf 100mA (Compliance)
    
    # 3. Output einschalten [cite: 578]
    smu.set_output_state(channel, True)

    # 4. Einfacher Sweep
    logger.info("Starte Sweep...")
    for i in range(5):
        voltage_target = i * 1.0 # 0V, 1V, 2V, ...
        
        # Spannung setzen 
        smu.set_source_level(channel, voltage_target)
        
        time.sleep(0.2) # Einschwingzeit
        
        # Messen
        result = smu.measure_iv(channel)
        if result:
            current, voltage = result
            logger.info(f"Set: {voltage_target}V -> Meas: {voltage:.3f}V, {current:.3e}A")

    # 5. Aufräumen
    smu.set_source_level(channel, 0.0)
    smu.set_output_state(channel, False)
    smu.disconnect()