import cv2 as cv
import numpy as np

videoCapture = cv.VideoCapture(0)
prevCircle = None
dist = lambda x1,y1,x2,y2: (x1-x2)**2+(y1-y2)**2
orange_MIN = np.array([0,92,160],np.uint8)
orange_MAX = np.array([20,202,255],np.uint8)
x_value = 0
y_value = 0
while True:
    ret,frame = videoCapture.read()
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    mask = cv.inRange(hsv, orange_MIN, orange_MAX)
    result = cv.bitwise_and(frame,frame, mask=mask)
    if not ret: break
    
    grayFrame = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    blurFrame = cv.GaussianBlur(grayFrame, (17,17), 0)
    
    circles = cv.HoughCircles(blurFrame, cv.HOUGH_GRADIENT,1.2,100,param1=100,param2=30,minRadius=1,maxRadius=1000)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        chosen = None
        for i in circles[0,:]:
            if chosen is None :
                chosen = i
            if prevCircle is not None :
                if dist(chosen[0],chosen[1],prevCircle[0],prevCircle[1]) <= dist(i[0],i[1],prevCircle[0],prevCircle[1]):
                    chosen = i
        cv.circle(frame, (chosen[0],chosen[1]),1,(0,100,100),3)
        
        cv.circle(frame,(chosen[0],chosen[1]),chosen[2],(255,0,255),3)
        prevCircle = chosen
        x_value = chosen[0]
        y_value = chosen[1]
    cv.imshow("circles",frame)
    cv.imshow("mask",result)
                
    print(x_value)
    
    
    
    
    if cv.waitKey(1) == (27): break
    
videoCapture.release()
cv.destroyAllWindows()
    
    
        
        
