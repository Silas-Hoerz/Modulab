import sys
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QLabel
from PySide6.QtCore import Slot, Qt

try:
    from .ui_WaterfallWidget import Ui_Form 
except ImportError:
    try:
        from ui_WaterfallWidget import Ui_Form
    except ImportError:
        class Ui_Form:
            def setupUi(self, Form): 
                self.widget_plot = QWidget(Form)
                layout = QVBoxLayout(self.widget_plot)
                layout.addWidget(QLabel("UI File Missing", Form))

class WaterfallWidget(QWidget, Ui_Form):
    """
    High-Performance Waterfall Plot mit Profile-Support.
    """

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.mgr = context.waterfall_manager
        self.log = context.log_manager
        # Profile Manager holen
        self.profile = context.profile_manager

        # --- Interne Variablen & Defaults laden ---
        self.img_array = None       
        self.wavelengths = None
        self.buffer_size = 100
        self.current_cmap_name = "Jet"

        self.__setup_pyqtgraph()
        self.__setup_ui()
        self.__connect_signals()

    def __setup_pyqtgraph(self):
        if self.widget_plot.layout() is None:
            layout = QVBoxLayout(self.widget_plot)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = self.widget_plot.layout()

        self.graphics_layout = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graphics_layout)
        
        self.plot_item = self.graphics_layout.addPlot(row=0, col=0)
        self.plot_item.setLabel('bottom', 'Wavelength', units='nm')
        self.plot_item.setLabel('left', 'History', units='Scans')
        self.plot_item.invertY(True) 

        self.img_item = pg.ImageItem()
        self.plot_item.addItem(self.img_item)

        self.hist_lut = pg.HistogramLUTItem()
        self.hist_lut.setImageItem(self.img_item)
        self.graphics_layout.addItem(self.hist_lut, row=0, col=1)

    def __setup_ui(self):
        # Colormaps füllen
        preferred = ['jet', 'viridis', 'plasma', 'inferno', 'magma', 'turbo', 'hsv', 'ocean', 'gray']
        display_names = [m.capitalize() for m in preferred]
        
        self.comboBox_colormap.clear()
        self.comboBox_colormap.addItems(display_names)
        
        # Gespeicherte Werte in UI setzen (block Signals verhindert, dass wir sofort Events triggern)
        self.comboBox_colormap.blockSignals(True)
        self.comboBox_colormap.setCurrentText(self.current_cmap_name.capitalize())
        self.on_colormap_changed(self.current_cmap_name) # Anwenden
        self.comboBox_colormap.blockSignals(False)
        
        self.spinBox_bufferSize.blockSignals(True)
        self.spinBox_bufferSize.setValue(self.buffer_size)
        self.spinBox_bufferSize.blockSignals(False)
        
        # Dem Manager mitteilen, wie viel er speichern soll (mindestens so viel wie angezeigt wird)
        # Wir geben ihm etwas Puffer (z.B. 2x Anzeige), damit beim Scrollen Daten da sind,
        # oder einfach exakt die Anzeige-Größe für Save.
        # Hier: Wir sagen ihm "Speichere mind. BufferSize"
        self.mgr.set_history_limit(max(2000, self.buffer_size)) 

    def __connect_signals(self):
        self.mgr.new_spectrum_available.connect(self.on_new_spectrum)
        self.mgr.waterfall_cleared.connect(self.on_clear)
        
        self.pushButton_clear.clicked.connect(self.mgr.clear_data)
        self.pushButton_saveData.clicked.connect(self.on_save_data)
        self.pushButton_savePlot.clicked.connect(self.on_save_plot)
        
        self.comboBox_colormap.currentTextChanged.connect(self.on_colormap_changed)
        self.spinBox_bufferSize.valueChanged.connect(self.on_buffer_size_changed)

        self.profile.profile_loaded.connect(self.on_profile_loaded)

    @Slot(str)
    def on_profile_loaded(self, profile_name):
        """Lädt Einstellungen, sobald ein Profil vom User gewählt wurde."""
        self.log.info(f"WaterfallWidget: Loading settings from profile '{profile_name}'...")
        
        saved_size = self.profile.read("Waterfall_HistoryLines")
        if saved_size is not None:
            self.buffer_size = int(saved_size)
            self.spinBox_bufferSize.blockSignals(True)
            self.spinBox_bufferSize.setValue(self.buffer_size)
            self.spinBox_bufferSize.blockSignals(False)
            self.mgr.set_history_limit(max(2000, self.buffer_size))

        saved_cmap = self.profile.read("Waterfall_Colormap")
        if saved_cmap:
            self.current_cmap_name = saved_cmap
            self.comboBox_colormap.blockSignals(True)
            self.comboBox_colormap.setCurrentText(self.current_cmap_name.capitalize())
            self.on_colormap_changed(self.current_cmap_name)
            self.comboBox_colormap.blockSignals(False)

    # --- Logik ---

    @Slot(object, object)
    def on_new_spectrum(self, wavelengths, intensities):
        num_points = len(intensities)
        
        if self.img_array is None or self.img_array.shape[0] != num_points:
            self.wavelengths = wavelengths
            self.img_array = np.zeros((num_points, self.buffer_size))
            
            x_min = wavelengths[0]
            x_range = wavelengths[-1] - wavelengths[0]
            x_scale = x_range / num_points
            
            self.img_item.resetTransform()
            self.img_item.scale(x_scale, 1)
            self.img_item.translate(x_min / x_scale, 0) # Wichtig: Translate VOR Scale im Transform-Stack
            self.img_item.setPos(x_min, 0) # Oder setPos direkt
            
            self.plot_item.setLimits(xMin=x_min, xMax=wavelengths[-1])
            self.plot_item.setXRange(x_min, wavelengths[-1])

        self.img_array = np.roll(self.img_array, 1, axis=1)
        self.img_array[:, 0] = intensities
        self.img_item.setImage(self.img_array, autoLevels=False)

    @Slot(int)
    def on_buffer_size_changed(self, val):
        """Ändert History-Größe und speichert Einstellung."""
        self.buffer_size = val
        self.img_array = None # Reset
        
        # Profil speichern
        if self.profile.get_current_profile_name():
            self.profile.write("Waterfall_HistoryLines", val)
        
        # Dem Manager auch Bescheid geben (optional, falls er mitwachsen soll)
        self.mgr.set_history_limit(max(2000, val))

    @Slot(str)
    def on_colormap_changed(self, name):
        """Setzt Colormap und speichert Einstellung."""
        try:
            mpl_cmap = plt.get_cmap(name.lower())
            pos = np.linspace(0, 1, 256)
            rgba = mpl_cmap(pos) * 255
            colors = rgba.astype(int)
            cmap = pg.ColorMap(pos, colors)
            self.hist_lut.gradient.setColorMap(cmap)
            
            # Profil speichern
            if self.profile.get_current_profile_name():
                self.profile.write("Waterfall_Colormap", name)
            
        except Exception as e:
            self.log.error(f"Error setting colormap '{name}': {e}")

    @Slot()
    def on_clear(self):
        self.img_array = None
        self.img_item.clear()

    @Slot()
    def on_save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Image (*.png)")
        if file_path:
            exporter = pg.exporters.ImageExporter(self.graphics_layout.scene())
            exporter.parameters()['width'] = 1920
            exporter.export(file_path)
            self.log.info(f"Plot saved to {file_path}")

    @Slot()
    def on_save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV (*.csv)")
        if file_path:
            self.mgr.save_raw_data(file_path, 'csv')