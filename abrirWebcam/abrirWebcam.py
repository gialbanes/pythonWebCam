"""
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
"""

import cv2
import mediapipe as mp

cam = cv2.VideoCapture(0)
face_mash = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

_, frame = cam.read()
frame_h, frame_w, _ = frame.shape

#pega as coordenadas da iris e converte pra pixels  
def posicao_iris(x, y, frame_w, frame_h):
    x_px = int(x * frame_w)
    y_px = int(y * frame_h)
    return x_px, y_px

while True:
    _, img = cam.read()
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #processando a imagem para obter os landmarks
    results = face_mash.process(rgb_img)
    landmark_points = results.multi_face_landmarks
    
    if landmark_points:
        landmarks = landmark_points[0].landmark
        
        #calcula a média dos pontos das bordas da iris do olho direito, ou seja, está pegando o centro
        right_iris_x = (landmarks[469].x + landmarks[470].x + landmarks[471].x + landmarks[472].x) / 4
        right_iris_y = (landmarks[469].y + landmarks[470].y + landmarks[471].y + landmarks[472].y) / 4

        left_iris_x = (landmarks[474].x + landmarks[475].x + landmarks[476].x + landmarks[477].x) / 4
        left_iris_y = (landmarks[474].y + landmarks[475].y + landmarks[476].y + landmarks[477].y) / 4
        
        #adaptando as coordendas p pixels por meio da função criada anteriormente 
        right_iris_x_px, right_iris_y_px = posicao_iris(right_iris_x, right_iris_y, frame_w, frame_h)
        left_iris_x_px, left_iris_y_px = posicao_iris(left_iris_x, left_iris_y, frame_w, frame_h) 
        
        #desenhando as bolinhas 
        cv2.circle(img, (right_iris_x_px, right_iris_y_px), 2, (255, 255, 0), -1)    
        cv2.circle(img, (left_iris_x_px, left_iris_y_px), 2, (255, 255, 0), -1)    
            
    cv2.imshow("Frame", img)
    
    if cv2.waitKey(20) & 0xFF==ord('q'):
        break
    
cam.release()
cv2.destroyAllWindows()

