import time

def run_experiment(api):
    """
    Demonstriert die korrekte Implementierung von Pause- und Stopp-Funktionen.
    """
    logger = api.log_mgr
    
    # Simuliere eine Messung mit vielen Schritten (z.B. 50 Punkte)
    total_steps = 50
    
    logger.info("Experiment gestartet. Warte auf Befehle...")

    try:
        for i in range(total_steps):
            
            # -----------------------------------------------------------
            # 1. STOPP-LOGIK (Muss am Anfang oder Ende der Schleife stehen)
            # -----------------------------------------------------------
            if api._is_stopped:
                logger.warning("Abbruch durch Benutzer erkannt!")
                # Hier können noch Aufräumarbeiten stattfinden (z.B. Laser aus)
                break # Bricht die for-Schleife ab

            # -----------------------------------------------------------
            # 2. PAUSE-LOGIK (Wartet, solange 'paused' True ist)
            # -----------------------------------------------------------
            if api._is_paused:
                logger.info("Experiment pausiert. Warte auf Fortsetzung...")
                
                # Wir bleiben in dieser while-Schleife gefangen, bis der User "Resume" drückt
                while api._is_paused:
                    # WICHTIG: Prüfen, ob während der Pause "Stopp" gedrückt wurde
                    if api._is_stopped:
                        break 
                    
                    time.sleep(0.1) # Kurz warten, um CPU nicht zu blockieren
                
                # Wenn wir hier ankommen, geht es entweder weiter oder wir stoppen
                if api._is_stopped:
                    logger.warning("Abbruch während der Pause erkannt!")
                    break
                else:
                    logger.info("Experiment fortgesetzt.")

            # -----------------------------------------------------------
            # 3. DIE EIGENTLICHE ARBEIT
            # -----------------------------------------------------------
            
            # Simuliere Messzeit (z.B. Spektrometer-Aufnahme)
            time.sleep(0.5) 
            
            # Fortschritt berechnen und loggen
            # (Das könnte man auch als Signal an einen Progress-Bar senden)
            logger.info(f"Messpunkt {i+1} von {total_steps} verarbeitet.")


    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    finally:
        # -----------------------------------------------------------
        # 4. AUFRÄUMEN (Wird IMMER ausgeführt, auch bei Stop/Error)
        # -----------------------------------------------------------
        # Dies ist der wichtigste Teil für sicheren Betrieb!
        # Hier sicherstellen, dass Spannungen auf 0 gesetzt werden, Shutter zugehen etc.
        logger.info("Experiment beendet. Führe Shutdown-Prozedur durch (Sicherheitszustand herstellen).")