import sys

import time
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QHBoxLayout, QFrame
                             )
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class OpenCv(QWidget):
    def __init__(self):
        super().__init__()
        # Basisinstellingen voor het venster
        self.setWindowTitle("OpenCv tracker")
        self.setGeometry(100, 100, 600, 500)# x, y, width, height
        self.setStyleSheet("""
            background-color: #2E2E2E;
            color: #FFFFFF;
        """)

         # Variabelen voor belasting
        self.cpu_load_active = False# Of de CPU belast wordt
        self.ram_load_active = False# Of RAM belast wordt
        self.ram_load_data = None# Hier slaan we de RAM data in op

        # Matplotlib setup voor CPU grafiek
        self.cpu_figure = Figure(facecolor='#3A3A3A') # Donkere achtergrond
        self.cpu_canvas = FigureCanvas(self.cpu_figure)
        self.cpu_ax = self.cpu_figure.add_subplot(111)  # 1 rij, 1 kolom, 1e plot
        
        # Styling van de grafiek
        self.cpu_ax.set_facecolor('#3A3A3A')# Matcht met de rest
        self.cpu_ax.tick_params(axis='x', colors='white')
        self.cpu_ax.tick_params(axis='y', colors='white')
        self.cpu_ax.set_ylim(0, 100) # Percentage dus 0-100
        self.cpu_ax.set_ylabel('X-as', color='white')
        self.cpu_ax.set_xlabel('Time (s)', color='white')
        self.cpu_ax.set_title('X-as', color='white')
        self.cpu_ax.grid(True, color='#555555') # Subtiele grid
        
        self.cpu_line, = self.cpu_ax.plot([], [], color='#02AAAA', linewidth=2)
        self.cpu_data = []# Hier komt alle CPU data in
        self.time_data = list(range(60)) # Tijdsas van 60 seconden

        

         # CPU label  groot en opvallend
        self.cpu_label = QLabel("Open Cv tracker")
        self.cpu_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #02AAAA;
        """)

        
        
        

        

        
        
         # Hoofd layout (alles onder elkaar)
        main_layout = QVBoxLayout()
        # CPU frame met grafiek
        cpu_frame = QFrame()
        cpu_frame.setStyleSheet("background-color: #3A3A3A; border-radius: 7px;")
        cpu_layout = QVBoxLayout(cpu_frame)
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_canvas)  # Voeg grafiek toe
          # RAM frame met progress bar 
       
        # Voeg alles toe aan hoofd layout     
        main_layout.addWidget(cpu_frame)
        
        
        self.setLayout(main_layout)
        # Timer voor live updates (elke 1000ms = 1 sec)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    
    
    

    def update_data(self):
        #Haalt CPU/RAM data op en update de GUI
        # CPU data
        
        cpu_usage =  10 
        
        
        self.cpu_data.append(cpu_usage)
        if len(self.cpu_data) > 60:  # Beperk tot 60 data punten
            self.cpu_data.pop(0)
        # Update grafiek
        self.cpu_line.set_data(self.time_data[-len(self.cpu_data):], self.cpu_data)
        self.cpu_ax.relim()  # Herbereken limieten
        self.cpu_ax.autoscale_view(scalex=True, scaley=False) # Alleen y-as auto
        self.cpu_ax.set_xlim(max(0, len(self.cpu_data)-60), len(self.cpu_data))  # Scrollend venster
        self.cpu_canvas.draw()  # Teken opnieuw
        
        
        
        

    def closeEvent(self, event):
        self.cpu_load_active = False
        self.ram_load_active = False
        self.ram_load_data = None
        event.accept()   # Laat het venster sluiten

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenCv()
    window.show()
    sys.exit(app.exec_())  # Start de applicatie