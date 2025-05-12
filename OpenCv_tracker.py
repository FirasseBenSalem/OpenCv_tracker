import cv2 as cv
import numpy as np
import time
import datetime

cap = cv.VideoCapture(1)

while True:
    current_time = str(datetime.datetime.now())
    
    
         
    HOUR        = datetime.datetime.now().hour   
    MINUTE      = datetime.datetime.now().minute
    
    ret,frame = cap.read()
    
    if not ret:
        break
    width = int(cap.get(3))
    height = int(cap.get(4))
    
    
    
    font = cv.FONT_HERSHEY_COMPLEX
    cv.putText(frame,f"{HOUR}:{MINUTE}", (0,30),font,1,(255,0,0),1,cv.LINE_AA)
    
    
    
    
    cv.imshow('frame',frame)
    
    if cv.waitKey(1) == 27:
        break
cap.release()
cv.destroyAllWindows()
