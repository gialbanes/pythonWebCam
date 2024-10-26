import cv2  
import mediapipe as mp  
import numpy as np  
import pygame 
import matplotlib.pyplot as plt  
from matplotlib.colors import LinearSegmentedColormap  
import json  
import mysql.connector  

WIDTH, HEIGHT = 1560, 1024  
GRID_SIZE = 100  

pygame.init()  
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Rastreamento Ocular e Heatmap")  

try:
    design_image = pygame.image.load('img.png')  
    design_image = pygame.transform.scale(design_image, (WIDTH, HEIGHT))  
except pygame.error as e:
    print(f"Erro ao carregar a imagem: {e}")  
    design_image = None  

mp_face_mesh = mp.solutions.face_mesh  
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)  

RIGHT_IRIS = [469, 470, 471, 472]  
LEFT_IRIS = [474, 475, 476, 477]  

def get_iris_center(landmarks, iris_points):
    x = np.mean([landmarks[point].x for point in iris_points])  
    y = np.mean([landmarks[point].y for point in iris_points])  
    return int(x * WIDTH), int(y * HEIGHT)  

heatmap = np.zeros((HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE))  

colors = [(1, 1, 1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]  
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)  

def save_heatmap_to_db(heatmap_matrix, user_id=1):
    heatmap_json = json.dumps(heatmap_matrix.tolist())  
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="uEye"
    )
    query = conn.cursor()  
    query.execute("""  
        INSERT INTO heatmaps (user_id, grid_size, heatmap_data)
        VALUES (%s, %s, %s);
    """, (user_id, GRID_SIZE, heatmap_json))  
    conn.commit()  
    query.close()  
    conn.close()  

def display_heatmap(heatmap):
    heatmap_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  

    max_count = np.max(heatmap) if np.any(heatmap) else 1  
    for y in range(heatmap.shape[0]):
        for x in range(heatmap.shape[1]):
            count = heatmap[y, x]  
            if count > 0:
                normalized_value = count / max_count  
                color = cmap(normalized_value)  
                rgba_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), 128)  
                pygame.draw.rect(heatmap_surface, rgba_color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))  

    screen.blit(design_image, (0, 0))  
    screen.blit(heatmap_surface, (0, 0))  
    pygame.display.flip()  

cap = cv2.VideoCapture(0)  
running = True  

while cap.isOpened() and running:  
    success, frame = cap.read()  
    if not success:  
        break

    frame = cv2.flip(frame, 1)  
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    results = face_mesh.process(rgb_frame)  

    if results.multi_face_landmarks:  
        for face_landmarks in results.multi_face_landmarks:  
            right_iris_center = get_iris_center(face_landmarks.landmark, RIGHT_IRIS)  
            left_iris_center = get_iris_center(face_landmarks.landmark, LEFT_IRIS)  
            
            iris_x = int((right_iris_center[0] + left_iris_center[0]) / 2)
            iris_y = int((right_iris_center[1] + left_iris_center[1]) / 2)

            grid_x = iris_x // GRID_SIZE  
            grid_y = iris_y // GRID_SIZE  

            if 0 <= grid_x < heatmap.shape[1] and 0 <= grid_y < heatmap.shape[0]:
                heatmap[grid_y, grid_x] += 1  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False  

    screen.fill((0, 0, 0))  
    if design_image is not None:
        screen.blit(design_image, (0, 0))  

    pygame.display.flip()  

cap.release()  
save_heatmap_to_db(heatmap)  

display_heatmap(heatmap)  

waiting = True
while waiting:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            waiting = False  

pygame.quit()  
