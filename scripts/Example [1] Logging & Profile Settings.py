import time

def run_experiment(api):
    """
    Demonstriert Logging und Profil-Verwaltung.
    """
    # 1. Zugriff auf den LogManager via API 
    logger = api.log_mgr
    profile = api.profile_mgr
    
    logger.info("--- Start des Konfigurations-Skripts ---") 

    # 2. Profil laden oder erstellen
    profile_name = "Experiment_Config_A"
    
    # Versuche Profil zu laden, sonst erstelle es neu 
    if not profile.load_profile(profile_name):
        logger.warning(f"Profil '{profile_name}' nicht gefunden. Erstelle neu...")
        profile.create_profile(profile_name)
        profile.load_profile(profile_name)

    # 3. Werte schreiben (werden in .json gespeichert) 
    logger.info("Speichere Parameter ins Profil...")
    profile.write("Start_Voltage", -2.0)
    profile.write("End_Voltage", 5.0)
    profile.write("Step_Size", 0.1)
    profile.write("User_Name", "Dr. Modulab")

    # 4. Werte lesen 
    saved_user = profile.read("User_Name")
    logger.info(f"Aktueller Benutzer laut Profil: {saved_user}")

    # Simuliere Arbeit
    time.sleep(1)
    
    logger.info("--- Konfiguration abgeschlossen ---")