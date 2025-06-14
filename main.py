import sys
import time
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QHBoxLayout, QFrame, QPushButton, QTabWidget,QTableView)

from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2 as cv
import numpy as np
from PyQt5.QtGui import QPixmap, QImage #

x_value = None
y_value = None

class VideoThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.videoCapture = cv.VideoCapture(0)
        self.running = True
        self.prevCircle = None
        self.orange_MIN = np.array([0, 61, 226], np.uint8)
        self.orange_MAX = np.array([47, 246, 255], np.uint8)
        self.points = []  #lijst om punten te bewaren voor het lijn
        #self.total_distance = 0
        self.video_label = None
    def dist(self, x1, y1, x2, y2):
        return (x1 - x2) ** 2 + (y1 - y2) ** 2

    
    
    
    def run(self):
        while self.running:
            ret, frame = self.videoCapture.read()
            if not ret:
                break

            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)    #gebruik hsv kleur code ipv RGB
            mask = cv.inRange(hsv, self.orange_MIN, self.orange_MAX)  # Filtert op alleen Oranje kleur zodat alleen de bal zichtbaar zal zijn.
            result = cv.bitwise_and(frame, frame, mask=mask) 

            gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)  #maak het zwart wit zodat er minder verschillen zijn voor het tracken te optimaliseren

            # Als al eerder een cirkel gevonden is beperk dan het zoekgebied
            if self.prevCircle is not None:#zorgt ervoor dat de ROI pas er bij komt nadat de bal als eerst wordt gevonden.
                x, y, r = self.prevCircle
                radius = 150  # Hoe groot het zoekgebied rond vorige cirkel is
                x1 = max(0, x - radius)
                y1 = max(0, y - radius)# De ROI vierkant wordt hier bepaald door de radius plus het coordinaat van de getrackde circel zelf.
                x2 = min(gray.shape[1], x + radius)
                y2 = min(gray.shape[0], y + radius)
                
                cropped = gray[y1:y2, x1:x2]
                blur = cv.GaussianBlur(cropped, (17, 17), 0)  #blurt de circel zodat hij makkelijker als circel gezien wordt.

                circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1.2, 100,
                                           param1=100, param2=30, minRadius=1, maxRadius=1000) #hoe groot en hoe klein de circel mag zijn en hoe rond de cricel moet zijn.

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    # Pas cirkelcoordinaten aan naar volledige beeld
                    for i in circles[0, :]:
                        i[0] += x1
                        i[1] += y1
            else:
                # Eerste kee volledige beeld gebruiken
                blur = cv.GaussianBlur(gray, (17, 17), 0)
                circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1.2, 100,
                               param1=100, param2=30, minRadius=1, maxRadius=1000)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                chosen = None
                for i in circles[0, :]:
                    if chosen is None:
                        chosen = i
                    if self.prevCircle is not None:
                        if self.dist(chosen[0], chosen[1], self.prevCircle[0], self.prevCircle[1]) > \
                                self.dist(i[0], i[1], self.prevCircle[0], self.prevCircle[1]):
                            chosen = i
                cv.circle(frame, (chosen[0], chosen[1]), 1, (0, 100, 100), 3)
                cv.circle(frame, (chosen[0], chosen[1]), chosen[2], (255, 0, 255), 3)
                #if self.prevCircle is not None:
                #    dx = chosen[0] - self.prevCircle[0]
                #    dy = chosen[1] - self.prevCircle[1]
                #    distance = (dx**2 + dy**2) ** 0.5
                    #self.total_distance += distance
                self.prevCircle = chosen
                global x_value
                x_value = chosen[0]
                global y_value
                y_value = chosen[1]#de x en y coordinaten worden naar het pyqt gui  geimporteert met behulp van dit

                #voeg de positie toe aan het lijn
                self.points.append((chosen[0], chosen[1]))
                if len(self.points) > 100:
                    self.points.pop(0)

               #teken lijnen tussen punten
                for i in range(1, len(self.points)):
                    cv.line(frame, self.points[i - 1], self.points[i], (0, 255, 0), 2)
            #cm_distance = self.total_distance / 100000  # pas 100 aan naargelang je test
            #cv.putText(frame, f"Afstand: {cm_distance:.2f} cm", (200, 30),
            #           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #cv.putText(frame, f"Afstand: {int(self.total_distance)} px", (10, 30),
            #       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Toon frame in PyQt5 label
            if self.video_label is not None:
                rgb_image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888) #dit had heb ik van een andere code die ik eerde rhad gemaakt maar het werkte niet omdat ik in de pyqt5 classe fouten heb gemaakt.
                pixmap = QPixmap.fromImage(qt_image)
                self.video_label.setPixmap(pixmap)

        self.videoCapture.release()
        

class OpenCv(QWidget):
        def __init__(self):
            super().__init__()
            # Basisinstellingen voor het venster
            self.setWindowTitle("OpenCv tracker")
            self.setGeometry(100, 100, 1200, 900)# x, y, width, height
            self.setStyleSheet("""
                background-color: #2E2E2E;
                color: #FFFFFF;
            """)

            # Variabelen voor belasting
            self.x_load_active = False# Of de x belast wordt
            self.y_load_active = False# Of de y belast wordt
            
            self.video_label = QLabel()
            self.video_label.setFixedSize(600, 600)

            # Matplotlib setup voor x grafiek
            self.x_figure = Figure(facecolor='#3A3A3A') # Donkere achtergrond
            self.x_canvas = FigureCanvas(self.x_figure)
            self.x_ax = self.x_figure.add_subplot(111)  # 1 rij, 1 kolom, 1e plot
            
            # Matplotlib setup voor y grafiek
            self.y_figure = Figure(facecolor='#3A3A3A') # Donkere achtergrond
            self.y_canvas = FigureCanvas(self.y_figure)
            self.y_ax = self.y_figure.add_subplot(111)  # 1 rij, 1 kolom, 1e plot
            
            # Styling van de grafiek
            self.x_ax.set_facecolor('#3A3A3A')# Matcht met de rest
            self.x_ax.tick_params(axis='x', colors='white')
            self.x_ax.tick_params(axis='y', colors='white')
            self.x_ax.set_ylim(0, 600) # Percentage dus 0-100
            self.x_ax.set_ylabel('X-as', color='white')
            self.x_ax.set_xlabel('Time (s)', color='white')
            self.x_ax.set_title('X-as', color='white')
            self.x_ax.grid(True, color='#555555')
            self.x_line, = self.x_ax.plot([], [], color='#02AAAA', linewidth=2)
            self.x_data = []
            
            # Styling van de grafiek
            self.y_ax.set_facecolor('#3A3A3A')# Matcht met de rest
            self.y_ax.tick_params(axis='x', colors='white')
            self.y_ax.tick_params(axis='y', colors='white')
            self.y_ax.set_ylim(0, 600) # Percentage dus 0-100
            self.y_ax.set_ylabel('Y-as', color='white')
            self.y_ax.set_xlabel('Time (s)', color='white')
            self.y_ax.set_title('Y-as', color='white')
            self.y_ax.grid(True, color='#555555')
            
            self.y_line, = self.y_ax.plot([], [], color='#eb4933', linewidth=2)
            self.y_data = []
            
            self.time_data = list(range(60))
            self.ytime_data = list(range(60)) 

            

            
            self.x_label = QLabel("Open Cv tracker")
            self.x_label.setStyleSheet("""
                font-size: 28px;
                font-weight: bold;
                color: #02AAAA;
            """)
            
            self.y_label = QLabel("")
            self.y_label.setStyleSheet("""
                font-size: 28py;
                font-weight: bold;
                color: #02AAAA;
            """)
            
            
            

            

            
            
            # Hoofd layout (alles onder elkaar)
            main_layout = QHBoxLayout()
            sub_main_layout = QVBoxLayout()
            button_layout = QHBoxLayout()
            grafiek_layout = QVBoxLayout()
            
            
            
            
            #buttons voor start en stop
            
            self.start_button = QPushButton("Start grafiek")
            self.start_button.setStyleSheet("background-color: #02AAAA; color: white; font-size: 16px;")
            self.start_button.clicked.connect(self.start_graph)

            self.stop_button = QPushButton("Stop grafiek")
            self.stop_button.setStyleSheet("background-color: #eb4933; color: white; font-size: 16px;")
            self.stop_button.clicked.connect(self.stop_graph)

            
            self.tabs = QTabWidget()
            self.tab1 = QWidget()# de tabs die niet goed werken boven de grafieken
            self.tab2 = QWidget()
            self.tabs.addTab(self.tab1, "Grafiek")
            self.tabs.addTab(self.tab2, "Tabel")
            
            
            
            
            
            
            # x frame met grafiek
            
            x_frame = QFrame()
            x_frame.setStyleSheet("background-color: #3A3A3A; border-radius: 7px;")
            x_layout = QVBoxLayout(x_frame)
            x_layout.addWidget(self.x_label)
            x_layout.addWidget(self.x_canvas)  # Voeg grafiek toe
            
            # y frame met grafiek
            y_frame = QFrame()
            y_frame.setStyleSheet("background-color: #3A3A3A; border-radius: 7py;")
            y_layout = QVBoxLayout(y_frame)
            y_layout.addWidget(self.y_label)
            y_layout.addWidget(self.y_canvas)  # Voeg grafiek toe
            
            
            sub_main_layout.addWidget(self.tabs)
            
            # Voeg alles toe aan hoofd layout     
            grafiek_layout.addWidget(x_frame)
            
            # Voeg alles toe aan hoofd layout     
            grafiek_layout.addWidget(y_frame)
            
            
            sub_main_layout.addLayout(grafiek_layout)
            
            
            self.setLayout(main_layout)
            # Timer voor live updates (elke 1000ms = 1 sec)
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_data)
            self.timer.start(100)
            
            sub_main_layout.addLayout(grafiek_layout)
            button_layout.addWidget(self.start_button)#Hier voeg ik alle buttons grafiek en videos aan de gepaste layout.
            button_layout.addWidget(self.stop_button)
            sub_main_layout.addLayout(button_layout)
            main_layout.addLayout(sub_main_layout)
            main_layout.addWidget(self.video_label)
            
            
        def start_graph(self):
            if not self.timer.isActive():#een start en stop knop hier stop de timer en start ik hem weer in de volgende definitie
                self.timer.start(100)

        def stop_graph(self):
            if self.timer.isActive():
                self.timer.stop()


        def update_data(self):
            #Haalt x/RAM data op en update de GUI
            # x data
            
             
            
            
            self.x_data.append(x_value)
            if len(self.x_data) >60:  # Beperk tot 60 data punten
                self.x_data.pop(0)
            # Update grafiek
            self.x_line.set_data(self.time_data[-len(self.x_data):], self.x_data)
            self.x_ax.relim()  # Herbereken limieten
            self.x_ax.autoscale_view(scalex=False, scaley=False) # Alleen y-as auto
            self.x_ax.set_xlim(60,0) # Ik heb dit verandert na mijn opdracht van het OC
            self.x_ax.invert_xaxis() #Ik heb dit verandert na mijn opdracht van het OC
            self.x_canvas.draw()  # Teken opnieuw
            
            self.y_data.append(y_value)
            if len(self.y_data) >60:  # Beperk tot 60 data punten
                self.y_data.pop(0)
            # Update grafiek
            self.y_line.set_data(self.ytime_data[-len(self.y_data):], self.y_data)
            self.y_ax.relim()
            self.y_ax.autoscale_view(scalex=False, scaley=False)
            self.y_ax.set_ylim(0, 600)  # Houd y tussen 0 en 600 pixels
            self.y_ax.set_xlim(60,0)  #Ik heb dit verandert na mijn opdracht van het OC
            
            self.y_ax.invert_xaxis()  #Ik heb dit verandert na mijn opdracht van het OC
            self.y_canvas.draw()
                                      # Teken opnieuw
            
            
            
             

        def closeEvent(self, event):
            event.accept()   # Laat het venster sluiten

if __name__ == "__main__":
    opencv_thread = VideoThread()
    

    # Start PyQt GUI
    app = QApplication(sys.argv)
    window = OpenCv()
    opencv_thread.video_label = window.video_label  # Geef label door aan thread
    opencv_thread.start()
    window.show()
    app.exec_()

    # Stop de video thread als GUI gesloten is
    opencv_thread.running = False
    opencv_thread.join()

