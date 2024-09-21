import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

if not cap.isOpened():
    print("não abriu")
    exit()
    
while True:
    ret, frame = cap.read() 
    
    if not ret:
        print("não tem frame")
        break;
    
    cv2.imshow("Imagem", frame)
    k = cv2.waitKey(1) 
    
    if k == ord('q'):
        break
    
    if cv2.getWindowProperty("Imagem", cv2.WND_PROP_VISIBLE) < 1:
        break
    
cv2.destroyAllWindows()
cap.release()
print("Encerrou")




