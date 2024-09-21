import cv2

eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

if not cap.isOpened():
    print("não abriu")  
    exit()

while True:
    ret, frame = cap.read()  
    
    if not ret:
        print("não tem frame")  
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    eyes = eye_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.3,  
        minNeighbors=5,   
        minSize=(20,20)   
    )

    for(x, y, w, h) in eyes:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)  

    cv2.imshow('Webcam', frame)  
    
    k = cv2.waitKey(1) 
    
    if k == ord('q'):
        break  

cv2.destroyAllWindows()  
cap.release()  
print("Encerrou")  
