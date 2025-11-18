import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtCore import Slot

class LivePlotWidget(QWidget):
    """
    Ein intelligentes Widget, das alle eingehenden Daten vom ExportManager visualisiert.
    """
    def __init__(self, context):
        super().__init__()
        self.context = context
        export_manager = self.context.export_manager
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        
        # Referenzen zu den Plot-Objekten speichern
        self.plots = {} 
        self.curves = {}
        self.images = {} # Für Heatmaps/Wasserfall-Plots bei Spektren
        
        # Position im Grid
        self.next_row = 0
        self.next_col = 0
        
        # Daten-Puffer für die Historie (X-Achse = Index)
        self.data_history = {} 

        # Verbindung herstellen
        export_manager.data_committed.connect(self.update_plots)

    @Slot(dict)
    def update_plots(self, data_payload):
        """
        Wird bei jedem 'commit()' aufgerufen.
        data_payload = {'Voltage': {'value': 5.0, 'unit': 'V'}, ...}
        """
        try:
            for name, content in data_payload.items():
                val = content['value']
                unit = content['unit']
                
                # 1. Plot erstellen, falls noch nicht vorhanden
                if name not in self.plots:
                    self._create_plot_for(name, val, unit)
                
                # 2. Daten updaten
                self._update_data_for(name, val)
                
        except Exception as e:
            print(f"Plot Error: {e}")

    def _create_plot_for(self, name, sample_val, unit):
        """Entscheidet dynamisch, ob Line-Plot oder Spektrum-Plot nötig ist."""
        arr = np.asanyarray(sample_val)
        
        # Setup PyQtGraph Styling
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        if arr.ndim == 0: 
            # === SKALAR (z.B. Strom, Spannung) ===
            plot_widget = pg.PlotWidget(title=f"{name}")
            plot_widget.setLabel('left', name, units=unit)
            plot_widget.setLabel('bottom', 'Index')
            plot_widget.showGrid(x=True, y=True)
            
            # Kurve erstellen
            curve = plot_widget.plot(pen=pg.mkPen('b', width=2))
            
            self.plots[name] = plot_widget
            self.curves[name] = curve
            self.data_history[name] = [] # Liste für Historie
            
            # Layout Logik (2 Spalten Grid)
            self.layout.addWidget(plot_widget, self.next_row, self.next_col)
            
        else:
            # === ARRAY (z.B. Spektrum) ===
            # Hier nehmen wir einen einfachen Plot, der das *aktuelle* Spektrum zeigt
            plot_widget = pg.PlotWidget(title=f"{name} (Live)")
            plot_widget.setLabel('left', 'Intensity', units=unit)
            plot_widget.setLabel('bottom', 'Pixel / Wavelength')
            
            curve = plot_widget.plot(pen=pg.mkPen('r', width=2))
            
            self.plots[name] = plot_widget
            self.curves[name] = curve
            
            # Arrays kriegen oft eine eigene Zeile (breit)
            if self.next_col > 0: 
                self.next_row += 1
                self.next_col = 0
            self.layout.addWidget(plot_widget, self.next_row, self.next_col, 1, 2) # Span 2 Columns
            self.next_row += 1
            return # Early return, damit Grid-Logik unten nicht doppelt läuft

        # Grid Logik weiterführen
        self.next_col += 1
        if self.next_col > 1:
            self.next_col = 0
            self.next_row += 1

    def _update_data_for(self, name, val):
        arr = np.asanyarray(val)
        
        if arr.ndim == 0:
            # Historie erweitern
            self.data_history[name].append(float(arr))
            # Kurve mit allen bisherigen Punkten updaten
            self.curves[name].setData(self.data_history[name])
        else:
            # Bei Arrays zeigen wir nur das AKTUELLE Array (keine Historie im RAM halten für Plot)
            self.curves[name].setData(arr)