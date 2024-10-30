import cv2  
import mediapipe as mp  
import numpy as np  
import pygame 
import matplotlib.pyplot as plt  
from matplotlib.colors import LinearSegmentedColormap  
import json  
import mysql.connector  
import io  
from datetime import datetime  # Para gerar um identificador único para o nome do arquivo
import os  # Para manipulação de diretórios

# Configurações da tela e do grid
WIDTH, HEIGHT = 1560, 1024  
GRID_SIZE = 70  

# Inicialização do Pygame
pygame.init()  
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Rastreamento Ocular e Heatmap")  

# Carrega a imagem do design
try:
    design_image = pygame.image.load('img.png')  
    design_image = pygame.transform.scale(design_image, (WIDTH, HEIGHT))  
except pygame.error as e:
    print(f"Erro ao carregar a imagem: {e}")  
    design_image = None  

# Inicialização do MediaPipe
mp_face_mesh = mp.solutions.face_mesh  
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)  

RIGHT_IRIS = [469, 470, 471, 472]  
LEFT_IRIS = [474, 475, 476, 477]  

# Função para calcular o centro da íris
def get_iris_center(landmarks, iris_points):
    x = np.mean([landmarks[point].x for point in iris_points])  
    y = np.mean([landmarks[point].y for point in iris_points])  
    return int(x * WIDTH), int(y * HEIGHT)  

# Matriz do heatmap
heatmap = np.zeros((HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE))  

# Cores para o heatmap
colors = [(1, 1, 1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]  
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)  

# Função para salvar o heatmap no banco de dados como um caminho de arquivo (VARCHAR)
def save_heatmap_to_db(heatmap_matrix, filepath, id_cliente=1, id_tela=1):
    heatmap_json = json.dumps(heatmap_matrix.tolist())  # Converte o heatmap em JSON
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="uEye"
    )
    query = conn.cursor()
    
    # Captura a data atual
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        query.execute("""
            INSERT INTO heatmaps (id_cliente, id_tela, grid_size, heatmap_data, heatmap_image, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (id_cliente, id_tela, GRID_SIZE, heatmap_json, filepath, now))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir dados no banco de dados: {err}")
    finally:
        query.close()
        conn.close()

# Função para salvar o heatmap como imagem com fundo transparente
def save_heatmap_image_transparent(matrix, filename):
    plt.figure(figsize=(8, 6), dpi=100)
    plt.imshow(matrix, cmap=cmap, alpha=0.5, interpolation='nearest', extent=[0, WIDTH, HEIGHT, 0])
    plt.axis('off')  # Desliga os eixos
    plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=300, transparent=True)  # Salva com fundo transparente
    plt.close()  # Fecha a figure

# Função para gerar um nome de arquivo único usando data e hora
def generate_unique_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Gera o timestamp
    return f"heatmap_transparent_{timestamp}.png"

# Função para exibir o heatmap na interface
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

# Inicialização da captura de vídeo
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

# Cria e salva a imagem do heatmap com nome único e caminho local
if not os.path.exists("heatmaps"):
    os.makedirs("heatmaps")  # Cria a pasta se não existir

unique_filename = generate_unique_filename()
local_filepath = f"./heatmaps/{unique_filename}"  # Exemplo de caminho local

save_heatmap_image_transparent(heatmap, filename=local_filepath)

# Salva o caminho da imagem no banco de dados como VARCHAR
save_heatmap_to_db(heatmap, local_filepath)

# Exibe o heatmap na interface
display_heatmap(heatmap)

# Mantém a tela aberta para visualização do heatmap
waiting = True
while waiting:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            waiting = False  

pygame.quit()  
