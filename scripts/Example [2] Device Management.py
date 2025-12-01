def run_experiment(api):
    """
    Erstellt Devices und wählt eines für die Messung aus.
    """
    logger = api.log_mgr
    dev_mgr = api.device_mgr # Zugriff auf DeviceManager

    logger.info("Richte Devices ein...")

    # 1. Neues Device erstellen (Rechteck)
    # Maße in Metern! (2mm x 2mm)
    dev_name = "Pixel"
    if not dev_mgr.get_device_by_name(dev_name):
        dev_mgr.create_device(
            name=dev_name,
            geometry="rectangle",
            tags=["Batch_1", "Blue"],
            length=2e-3,
            width=2e-3
        )
        logger.info(f"Device '{dev_name}' erstellt.")

    # 2. Ein weiteres Device erstellen (Kreis mit Loch)
    ring_name = "Ring_Struktur_B2"
    if not dev_mgr.get_device_by_name(ring_name):
        dev_mgr.create_device(
            name=ring_name,
            geometry="circle",
            radius=100e-6,         # 100µm Außenradius
            cutout_radius=50e-6    # 50µm Innenradius (Loch)
        )

    # 3. Liste aller Devices abrufen
    all_devices = dev_mgr.list_device_names()
    logger.debug(f"Verfügbare Devices: {all_devices}")

    # 4. Aktives Device setzen (Wichtig für Metadaten im Export)
    dev_mgr.set_active_device(dev_name)
    
    # 5. Fläche abrufen (für Berechnungen)
    area = dev_mgr.get_active_device_area()
    logger.info(f"Aktives Device: {dev_name}, Fläche: {area} m^2")