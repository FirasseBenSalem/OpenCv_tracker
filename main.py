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
        self.videoCapture = cv.VideoCapture(0)
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
            if cv.waitKey(1) & 0xFF == 27:
                self.running = False
                break

        self.videoCapture.release()
        cv.destroyAllWindows()
    
            
class OpenCv(QWidget):
    def __init__(self):
        super().__init__()
        # ... jouw bestaande init code ...

        self.x_data = []
        self.max_points = 100  # Max aantal data punten zichtbaar
        self.x_line, = self.x_ax.plot([], [], color='#02AAAA', linewidth=2)

        # Timer om de grafiek regelmatig te updaten
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # update elke 100 ms

    def update_data(self):
        global x_value
        if x_value is not None:
            self.x_data.append(x_value)

        # Beperk data tot max 100 punten
        if len(self.x_data) > self.max_points:
            self.x_data.pop(0)

        # Update x-as limiet zodat laatste 100 zichtbaar zijn
        self.x_line.set_data(range(len(self.x_data)), self.x_data)
        self.x_ax.set_xlim(0, self.max_points)
        self.x_ax.set_ylim(0, 640)  # Pas aan als nodig (bijv. webcam breedte)

        self.x_canvas.draw()
            
            
            
             

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
            
    
    
    
    
    

