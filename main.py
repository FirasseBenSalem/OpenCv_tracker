import sys
import time
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QHBoxLayout, QFrame
                             )
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2 as cv
import numpy as np
x_value = None

class VideoThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.videoCapture = cv.VideoCapture("openneer.mp4")
        self.fps = self.videoCapture.get(cv.CAP_PROP_FPS)
        self.frame_delay = 1.0 / self.fps 
        self.running = True
        self.prevCircle = None
        self.orange_MIN = np.array([0, 92, 160], np.uint8)
        self.orange_MAX = np.array([20, 202, 255], np.uint8)
        
    def dist(self, x1, y1, x2, y2):
        return (x1 - x2) ** 2 + (y1 - y2) ** 2




    def run(self):
        while self.running:
            ret, frame = self.videoCapture.read()
            if not ret:
                break

            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            mask = cv.inRange(hsv, self.orange_MIN, self.orange_MAX)
            result = cv.bitwise_and(frame, frame, mask=mask)

            gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(gray, (17, 17), 0)

            circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1.2, 100, param1=100, param2=30, minRadius=1, maxRadius=1000)

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
                self.prevCircle = chosen
                global x_value
                x_value = chosen[0]

            cv.imshow("Circles", frame)
            time.sleep(self.frame_delay)
            if cv.waitKey(1) & 0xFF == 27:
                self.running = False
                break

        self.videoCapture.release()
        cv.destroyAllWindows()
    
            
class OpenCv(QWidget):
        def __init__(self):
            super().__init__()
            # Basisinstellingen voor het venster
            self.setWindowTitle("OpenCv tracker")
            self.setGeometry(100, 100, 600, 600)# x, y, width, height
            self.setStyleSheet("""
                background-color: #2E2E2E;
                color: #FFFFFF;
            """)

            # Variabelen voor belasting
            self.x_load_active = False# Of de x belast wordt
            

            # Matplotlib setup voor x grafiek
            self.x_figure = Figure(facecolor='#3A3A3A') # Donkere achtergrond
            self.x_canvas = FigureCanvas(self.x_figure)
            self.x_ax = self.x_figure.add_subplot(111)  # 1 rij, 1 kolom, 1e plot
            
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
            self.max_seconds = 10
            self.max_data = self.max_seconds * self.fps
            self.time_data = list(np.linspace(0, self.max_seconds, self.max_points)) 

            

            
            self.x_label = QLabel("Open Cv tracker")
            self.x_label.setStyleSheet("""
                font-size: 28px;
                font-weight: bold;
                color: #02AAAA;
            """)

            
            
            

            

            
            
            # Hoofd layout (alles onder elkaar)
            main_layout = QVBoxLayout()
            # x frame met grafiek
            x_frame = QFrame()
            x_frame.setStyleSheet("background-color: #3A3A3A; border-radius: 7px;")
            x_layout = QVBoxLayout(x_frame)
            x_layout.addWidget(self.x_label)
            x_layout.addWidget(self.x_canvas)  # Voeg grafiek toe
            # RAM frame met progress bar 
        
            # Voeg alles toe aan hoofd layout     
            main_layout.addWidget(x_frame)
            
            
            self.setLayout(main_layout)
            # Timer voor live updates (elke 1000ms = 1 sec)
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_data)
            self.timer.start(10)

        
        
        

        def update_data(self):
            #Haalt x/RAM data op en update de GUI
            # x data
            
             
            
            
            self.x_data.append(x_value)
            if len(self.x_data) > self.max_points:
                self.x_data.pop(0)
            # Update grafiek
            self.x_line.set_data(self.time_data[-len(self.x_data):], self.x_data)
            self.x_ax.relim()  # Herbereken limieten
            self.x_ax.autoscale_view(scalex=True, scaley=False) # Alleen y-as auto
            self.x_ax.set_xlim(0, self.max_seconds)
            self.x_canvas.draw()  # Teken opnieuw
            
            
            
             

        def closeEvent(self, event):
            event.accept()   # Laat het venster sluiten

if __name__ == "__main__":
    opencv_thread = VideoThread()
    opencv_thread.start()

    # Start PyQt GUI
    app = QApplication(sys.argv)
    window = OpenCv()
    window.show()
    app.exec_()

    # Stop de video thread als GUI gesloten is
    opencv_thread.running = False
    opencv_thread.join()
    print(cv2.CAP_PROP_FPS)
            
    
    
    
    
    

