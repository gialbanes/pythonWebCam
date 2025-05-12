import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
from datetime import datetime
from pymongo import MongoClient

WIDTH, HEIGHT = 1560, 1024  # Tamanho da janela
GRID_SIZE = 70  # Tamanho de cada cédula

pygame.init()  # Inicializa o Pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Define uma janela com as dimensões
pygame.display.set_caption("Rastreamento Ocular e Heatmap")  # Nome da janela

# Tenta carregar a imagem do design
try:
    design_image = pygame.image.load('img.png')  # Carrega a imagem do layout
    design_image = pygame.transform.scale(design_image, (WIDTH, HEIGHT))  # Redimensiona para caber na janela
except pygame.error as e:
    print(f"Erro ao carregar a imagem: {e}")  # Exibe erro se a imagem não for encontrada
    design_image = None

# Inicializa o MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Define os landmarks para o cálculo do centro da íris
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_IRIS = [474, 475, 476, 477]

# Função que calcula a média das coordenadas X e Y dos pontos da íris
def get_iris_center(landmarks, iris_points):
    x = np.mean([landmarks[point].x for point in iris_points])
    y = np.mean([landmarks[point].y for point in iris_points])
    return int(x * WIDTH), int(y * HEIGHT)  # Converte para coordenadas da tela

# Função para salvar dados no MongoDB
def save_matriz_to_db(idUsuario, idFase, matrizFoco, tempoFocoEsperado, tempoFoco, acertos, erros, duracao="00:01:00"):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["pi"]
        collection = db["TestesRastreamentoOcular"]
        doc = {
            "idUsuario": idUsuario,
            "idFase": idFase,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duracao": duracao,
            "matrizFoco": matrizFoco,
            "tempoFocoEsperado": tempoFocoEsperado,
            "tempoFoco": tempoFoco,
            "acertos": acertos,
            "erros": erros
        }
        collection.insert_one(doc)
        print("✅ Dados salvos com sucesso no MongoDB!")
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")

# Função para coletar dados do banco para análise
def collect_matriz_json_data():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["pi"]
        collection = db["TestesRastreamentoOcular"]
        resultado = collection.find({}, sort=[("_id", -1)]).limit(3)
        
        total_acertos = 0
        total_erros = 0
        
        for doc in resultado:
            acertos = doc.get("acertos", 0)
            erros = doc.get("erros", 0)
            total_acertos += acertos
            total_erros += erros
            matriz = doc["matrizFoco"]
            print(f"📊 Matriz Foco: {matriz}")
        
        print(f"✅ Total de acertos nos últimos 3 testes: {total_acertos}")
        print(f"❌ Total de erros nos últimos 3 testes: {total_erros}")
        print(f"🕒 Tempo total de foco: {tempo_foco_total:.2f} segundos")
    except Exception as e:
        print(f"❌ Erro ao buscar dados no MongoDB: {e}")

# Inicia a câmera
cap = cv2.VideoCapture(0)
running = True

tempo_foco_inicio = None
tempo_foco_total = 0
matriz = []

# Loop principal
while cap.isOpened() and running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    success, frame = cap.read()  # Captura um frame da webcam
    if not success:
        break  # Encerra se a captura falhar

    # Espelha a imagem
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte para RGB
    results = face_mesh.process(rgb_frame)  # Processa a imagem com o MediaPipe

    if design_image:
        screen.blit(design_image, (0, 0))  # Desenha a imagem de fundo na tela

    if results.multi_face_landmarks:
        if tempo_foco_inicio is None:
            tempo_foco_inicio = time.time()  # Inicia a contagem do tempo de foco

        for face_landmarks in results.multi_face_landmarks:
            right_iris_center = get_iris_center(face_landmarks.landmark, RIGHT_IRIS)
            left_iris_center = get_iris_center(face_landmarks.landmark, LEFT_IRIS)
            iris_x = int((right_iris_center[0] + left_iris_center[0]) / 2)
            iris_y = int((right_iris_center[1] + left_iris_center[1]) / 2)

            if 0 <= iris_x < WIDTH and 0 <= iris_y < HEIGHT:
                matriz.append([iris_x, iris_y])

        if tempo_foco_inicio is not None:
            tempo_foco_total += time.time() - tempo_foco_inicio
            tempo_foco_inicio = time.time()  # Reinicia o tempo para medir o próximo intervalo
    else:
        if tempo_foco_inicio is not None:
            tempo_foco_total += time.time() - tempo_foco_inicio
            tempo_foco_inicio = None

    pygame.display.update()  # Atualiza a tela com as novas mudanças

# Libera o recurso da câmera
cap.release()

# Salva os dados no banco de dados
save_matriz_to_db(
    idUsuario=1,
    idFase=1,
    matrizFoco=matriz,
    tempoFocoEsperado=0.3,
    tempoFoco=tempo_foco_total,
    acertos=5,
    erros=2
)

# Coleta os dados dos últimos testes
collect_matriz_json_data()

# Fechamento das janelas
pygame.quit()
