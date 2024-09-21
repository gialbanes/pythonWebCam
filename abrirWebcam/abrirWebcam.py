import cv2
import os
from datetime import datetime

if not os.path.exists('fotos'):
    os.makedirs('fotos')
if not os.path.exists('videos'):
    os.makedirs('videos')

eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Não abriu")  
    exit()

fourcc = cv2.VideoWriter_fourcc(*'ABCD')
video = None
recording = False

while True:
    ret, frame = cap.read()  
    
    if not ret:
        print("Não tem frame")  
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    eyes = eye_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,  
        minNeighbors=60,   
        minSize=(20,20)   
    )
    
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  

    cv2.imshow('Webcam', frame)  
    
    k = cv2.waitKey(1) 
    
    if k == ord('s'):
        photo_name = f'fotos/foto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        cv2.imwrite(photo_name, frame)
        print("Imagem salva!")
    
    elif k == ord('r'):
        if not recording:
            video_name = f'videos/video_{datetime.now().strftime("%Y%m%d_%H%M%S")}.avi'
            video = cv2.VideoWriter(video_name, fourcc, 20.0, (640, 480))
            recording = True
            print(f"Gravação iniciada!")
        else:
            if video is not None:
                video.release()  
                video = None  
            recording = False
            print("Gravação encerrada.")
    
    if recording and video is not None:
        video.write(frame)  
    
    if k == ord('q'):
        break  

if video is not None:
    video.release()  

cap.release()  
cv2.destroyAllWindows()  
print("Encerrou")  
