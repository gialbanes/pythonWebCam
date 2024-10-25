# nesse código ainda tem algum problema com a parte do olho, vou resolver ainda
# integração com o BD ok
# geração da imagem do heatmap ok 
import cv2
import mediapipe as mp
import numpy as np
import pygame
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import json
import mysql.connector

# Configurações iniciais
WIDTH, HEIGHT = 1560, 1024  # Tamanho da tela
GRID_SIZE = 100  # Tamanho da célula do heatmap
heatmap = np.zeros((HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE))

# Inicializando MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Define um colormap que vai de transparente -> verde -> amarelo -> vermelho
colors = [(1, 1, 1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]  # RGBA
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

def show_heatmap(matrix, background_image):
    plt.figure(figsize=(8, 6), dpi=100)
    
    # Usar as dimensões da imagem redimensionada
    plt.imshow(background_image, extent=[0, img_width, img_height, 0])  # Usar img_width e img_height
    plt.imshow(matrix, cmap=cmap, alpha=0.5, interpolation='nearest', extent=[0, img_width, img_height, 0])
    
    plt.axis('off')
    plt.show()

# Função para salvar o heatmap como imagem com fundo transparente
def save_heatmap_image_transparent(matrix, filename):
    plt.figure(figsize=(8, 6), dpi=100)
    plt.imshow(matrix, cmap=cmap, alpha=0.5, interpolation='nearest', extent=[0, WIDTH, HEIGHT, 0])
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=300, transparent=True)
    plt.close()

# Função para salvar a matriz de heatmap no banco de dados
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

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Deixa a tela com o tamanho passado
pygame.display.set_caption("Heatmap com Movimento do Olho")

# Carrega a imagem do design
try:
    design_image = pygame.image.load('img.png')  # Carrega a imagem
    original_img_width, original_img_height = design_image.get_width(), design_image.get_height()  # Dimensões reais da imagem
    design_image = pygame.transform.scale(design_image, (1568, 1343))  # Redimensiona para o tamanho da janela
    img_width, img_height = design_image.get_size()  # Atualiza para as novas dimensões da imagem
except pygame.error as e:
    print(f"Erro ao carregar a imagem: {e}")
    design_image = None

# Captura de vídeo
vc = cv2.VideoCapture(0)
def detect_face(frame):
    global heatmap
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            left_eye_landmarks = [face_landmarks.landmark[i] for i in range(469, 473)]
            right_eye_landmarks = [face_landmarks.landmark[i] for i in range(474, 478)]

            left_iris_x = np.mean([landmark.x for landmark in left_eye_landmarks])
            left_iris_y = np.mean([landmark.y for landmark in left_eye_landmarks])
            right_iris_x = np.mean([landmark.x for landmark in right_eye_landmarks])
            right_iris_y = np.mean([landmark.y for landmark in right_eye_landmarks])

            h, w, _ = frame.shape
            # Inverter a coordenada X como em um espelho
            pupil_median_x = w - ((int(left_iris_x * w) + int(right_iris_x * w)) // 2)
            pupil_median_y = (int(left_iris_y * h) + int(right_iris_y * h)) // 2

            grid_x = pupil_median_x // GRID_SIZE
            grid_y = pupil_median_y // GRID_SIZE

            if 0 <= grid_x < heatmap.shape[1] and 0 <= grid_y < heatmap.shape[0]:
                heatmap[grid_y, grid_x] += 1

    return frame

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    rval, frame = vc.read()
    if not rval:
        break

    frame = detect_face(frame)

    screen.fill((0, 0, 0))
    if design_image is not None:
        screen.blit(design_image, (0, 0))

    pygame.display.flip()

# Após fechar a janela do design, exibe o heatmap
if design_image is not None:
    design_image_np = np.array(pygame.surfarray.pixels3d(design_image)).transpose(1, 0, 2)
    
    # Aqui, você pode redimensionar o heatmap para que corresponda às dimensões da imagem de design, se necessário
    heatmap_resized = cv2.resize(heatmap, (img_width // GRID_SIZE, img_height // GRID_SIZE))  # Ajuste o tamanho

    # Mostra o heatmap com a imagem de design redimensionada
    show_heatmap(heatmap_resized, design_image_np)  
    save_heatmap_image_transparent(heatmap_resized, filename="heatmap_transparent.png")
    save_heatmap_to_db(heatmap_resized)

vc.release()
pygame.quit()