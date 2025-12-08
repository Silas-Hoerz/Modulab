import sys
import numpy as np
import os
# QWidget, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, und HINZUFÜGUNG von QApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QFileDialog, QMessageBox, QApplication 
from PySide6.QtCore import Slot, Signal, QEvent, Qt

# Importiere die generierte UI-Klasse (bleibt unverändert)
try:
    from .ui_WaterfallWidget import Ui_Form 
except ImportError:
    from PySide6.QtWidgets import QLabel
    class Ui_Form:
        def setupUi(self, Form):
            self.vLayout = QVBoxLayout(Form)
            self.label_status = QLabel("UI File not loaded", Form)
            self.vLayout.addWidget(self.label_status)
        def retranslateUi(self, Form): pass

# Importiere die Plot-Bibliothek (Matplotlib)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import colormaps
# Axes3D wird nicht mehr benötigt

class WaterfallWidget(QWidget, Ui_Form):
    """
    Diese Klasse verwaltet das 2D Spektrogramm (Heatmap) UI-Panel.
    """

    # Vordefinierte Colormaps für die ComboBox
    COLORMAPS = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'jet'] 
    
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.waterfall_mgr = context.waterfall_manager
        self.log_mgr = context.log_manager
        
        # Interner Zustand
        # Z-Offset ist für 2D-Heatmaps irrelevant, kann aber für ein Re-Plot genutzt werden
        self.z_offset = 0.05 
        # Standard Colormap auf 'jet' setzen, wie gewünscht
        self.current_colormap = 'jet' 

        self.__setup_plot()
        self.__setup_ui()
        self.__connect_signals()
        
        # UI initial setzen
        self.doubleSpinBox_zOffset.setValue(self.z_offset)
        self.checkBox_autoScale.setChecked(True)
        self.comboBox_colormap.setCurrentText(self.current_colormap) # 'jet' auswählen
        
        self.update_status()

    def __setup_plot(self):
        """
        Initialisiert das Matplotlib 2D-Diagramm (Image-Plot).
        """
        plot_layout = QVBoxLayout(self.widget_plot)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Figure erstellen
        self.fig = Figure(figsize=(8, 6), tight_layout=True)
        # Hintergrundfarbe setzen: Dunkelgrau (#252525)
        bg_color = '#252525'
        self.fig.patch.set_facecolor(bg_color) 
        
        self.plot_canvas = FigureCanvas(self.fig)
        # Setze das Canvas-Stylesheet nur für die Ränder/Rahmen, nicht für den Hintergrund
        # Der Plot-Hintergrund wird über ax.set_facecolor gesetzt.
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 2D-Subplot erstellen
        self.plot_ax = self.fig.add_subplot(111)
        
        # Initiales Styling anwenden
        self.__style_plot_2d(bg_color)
        
        plot_layout.addWidget(self.plot_canvas)
        
        self.plot_canvas.draw()

    def __style_plot_2d(self, bg_color):
        """
        Setzt das Aussehen der 2D-Achsen auf 'Modern Dark Mode'.
        """
        ax = self.plot_ax
        text_color = 'white'
        grid_color = '#404040' 

        # Hintergrund der Achsenfläche
        ax.set_facecolor(bg_color)
        
        # Farben der Achsen-Linien (Spines)
        for spine in ax.spines.values():
            spine.set_color(grid_color) 
            
        # Farben der Ticks und Labels
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        
        ax.set_xlabel("Wavelength (nm)", color=text_color)
        ax.set_ylabel("Measurement Index", color=text_color) 
        



    def __setup_ui(self):
        """Setzt den anfänglichen Zustand der UI-Elemente."""
        
        # ComboBox mit Colormaps füllen
        self.comboBox_colormap.addItems(self.COLORMAPS)
        
        # Z-Offset (jetzt irrelevant, aber beibehalten)
        self.doubleSpinBox_zOffset.setRange(0.001, 1.0)
        self.doubleSpinBox_zOffset.setSingleStep(0.01)

    def __connect_signals(self):
        """Verbindet alle Signale und Slots."""
        # ... (Signale bleiben gleich)
        self.waterfall_mgr.waterfall_data_updated.connect(self.on_data_updated)
        self.waterfall_mgr.waterfall_cleared.connect(self.on_waterfall_cleared)

        self.pushButton_clear.clicked.connect(self.waterfall_mgr.clear_data)
        self.pushButton_savePlot.clicked.connect(self.on_save_plot_clicked)
        self.pushButton_saveData.clicked.connect(self.on_save_data_clicked)
        
        self.doubleSpinBox_zOffset.valueChanged.connect(self.on_z_offset_changed)
        self.comboBox_colormap.currentTextChanged.connect(self.on_colormap_changed)
        self.checkBox_autoScale.toggled.connect(self.on_auto_scale_changed)


    # --- Slots für Daten-Updates vom WaterfallManager ---

    @Slot(list, object)
    def on_data_updated(self, z_indices, data_matrix):
        """
        Aktualisiert das 2D-Spektrogramm (Heatmap).
        X-Achse: Wellenlänge, Y-Achse: Index/Zeit, Farbe: Intensität.
        """
        wavelengths, _, _ = self.waterfall_mgr.get_waterfall_data()
        
        if len(wavelengths) == 0:
            self.log_mgr.warning("Received update without wavelengths.")
            return

        # 1. Plot leeren
        self.plot_ax.clear()
        
        # 2. Styling wiederherstellen
        self.__style_plot_2d(self.fig.patch.get_facecolor()) 
        
        # 3. Daten plotten als Bild (imshow)
        # Transponieren der Datenmatrix ist wichtig: imshow zeigt standardmäßig Zeilen=Y, Spalten=X
        # Wir wollen: Y = Messindex (Zeilen), X = Wellenlänge (Spalten)
        
        # Umfang der Achsen definieren (Extent)
        extent = [
            min(wavelengths), 
            max(wavelengths), 
            z_indices[-1] + 1, # Max Index (Anzahl der Messungen)
            z_indices[0] - 1 if len(z_indices) > 0 else 0 # Min Index
        ]
        
        # Daten-Darstellung: origin='upper' (höherer Index oben)
        # aspect='auto' sorgt für die Füllung des Achsenbereichs
        img = self.plot_ax.imshow(
            data_matrix, 
            cmap=self.current_colormap, 
            aspect='auto', 
            extent=extent, 
            origin='lower' # 'lower' damit der Index von unten nach oben wächst
        )

        # 4. Colorbar hinzufügen (optional, aber sehr empfohlen für Heatmaps)
        # Prüfen, ob die Colorbar bereits existiert und entfernen
        if hasattr(self, 'cbar') and self.cbar is not None:
            self.cbar.remove()
        
        # Fügen Sie die Colorbar hinzu
        self.cbar = self.fig.colorbar(img, ax=self.plot_ax, label="Intensity (a.u.)")
        self.cbar.ax.yaxis.label.set_color('white')
        self.cbar.ax.tick_params(colors='white')


        # 5. Achsen-Limits setzen
        # X-Achse (Wellenlänge): Manuell festlegen
        self.plot_ax.set_xlim(min(wavelengths), max(wavelengths))
        
        # Y-Achse (Index/Zeit): Auf die Anzahl der Messungen begrenzen
        self.plot_ax.set_ylim(z_indices[0] if z_indices else 0, z_indices[-1] + 1 if z_indices else 1)
        
        # 6. Titel/Status
        self.update_status()
        
        # 7. Zeichnen
        self.plot_canvas.draw()
        
        # 8. GUI-Events sofort verarbeiten, um die Aktualisierung sichtbar zu machen.
        QApplication.processEvents() # <--- KORREKTUR für Live-Update

    @Slot()
    def on_waterfall_cleared(self):
        """Reagiert auf das Löschen des Datenpuffers."""
        self.plot_ax.clear()
        self.__style_plot_2d(self.fig.patch.get_facecolor())
        
        # Colorbar entfernen
        if hasattr(self, 'cbar') and self.cbar is not None:
            self.cbar.remove()
            self.cbar = None
            
        self.update_status()
        self.plot_canvas.draw()
        QApplication.processEvents() # Auch hier, falls ein Clear mitten im Plot passiert


    # --- Lokale UI-Aktionen (Speichern und Einstellungen) ---

    def update_status(self):
        """Aktualisiert das Status-Label."""
        count = self.waterfall_mgr.z_counter
        self.label_status.setText(f"Data Points: {count} spectra buffered")
        
    @Slot(float)
    def on_z_offset_changed(self, value):
        """
        Der Z-Offset ist bei 2D nicht visuell relevant, aber wir nutzen die
        Änderung, um einen Re-Plot zu erzwingen, falls sich der Benutzer nur
        "umschauen" will.
        """
        self.z_offset = value
        _, data_matrix, z = self.waterfall_mgr.get_waterfall_data()
        if self.waterfall_mgr.z_counter > 0:
            self.on_data_updated(z, data_matrix)
        
    @Slot(str)
    def on_colormap_changed(self, name):
        """Ändert die Colormap und erzwingt ein Re-Plot."""
        self.current_colormap = name
        # Erzwinge Re-Plot
        _, data_matrix, z = self.waterfall_mgr.get_waterfall_data()
        if self.waterfall_mgr.z_counter > 0:
            self.on_data_updated(z, data_matrix)
            
    @Slot(bool)
    def on_auto_scale_changed(self, checked):
        """
        Bei 2D Heatmaps steuert Auto-Scale die Limits der Farbintensität (vmin/vmax).
        Da imshow standardmäßig Autoscaling durchführt, ist hier keine manuelle 
        vmax/vmin-Steuerung nötig. Wir lassen die Methode aber bestehen,
        falls dies später implementiert werden soll.
        """
        self.log_mgr.info(f"Color intensity auto-scaling set to: {checked}")
        # Ein Re-Plot kann ausgelöst werden, um die Änderung zu bestätigen:
        _, data_matrix, z = self.waterfall_mgr.get_waterfall_data()
        if self.waterfall_mgr.z_counter > 0:
            self.on_data_updated(z, data_matrix)


    @Slot()
    def on_save_plot_clicked(self):
        """Öffnet Dialog zum Speichern des Plots (PNG, SVG, PDF)."""
        # ... (Logik bleibt unverändert, verwendet den Manager)
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Spectrogram Plot", 
            os.getcwd(), 
            "Plot Files (*.png *.svg *.pdf);;PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"
        )
        
        if file_path:
            success = self.waterfall_mgr.save_plot_image(self.fig, file_path)
            if success:
                self.log_mgr.info(f"Plot saved successfully to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save plot image.")

    @Slot()
    def on_save_data_clicked(self):
        """Öffnet Dialog zum Speichern der Rohdaten (CSV, NPY)."""
        # ... (Logik bleibt unverändert, verwendet den Manager)
        if self.waterfall_mgr.z_counter == 0:
            QMessageBox.warning(self, "No Data", "There are no spectra buffered to save.")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Save Waterfall Raw Data", 
            os.getcwd(), 
            "CSV (Comma Separated) (*.csv);;NumPy Binary (*.npy)"
        )
        
        if file_path:
            format = 'csv' if selected_filter.endswith('*.csv)') else 'npy'
            
            success = self.waterfall_mgr.save_raw_data(file_path, format)
            if success:
                self.log_mgr.info(f"Data saved successfully to {file_path} as {format}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save raw data.")