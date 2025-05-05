import cv2  # Biblioteca de visão computacional
import mediapipe as mp  # Framework capaz de detctar elementos em vídeos e imagens
import numpy as np  # Biblioteca que realiza operações em arrays multidimensionais
import pygame # Biblioteca para criar interfaces visuais com manipulaçoes de imagens
import matplotlib.pyplot as plt  # Biblioteca para criação de gráficos 2D e 3D com visualizações estáticas, animadas e interativas
from matplotlib.colors import LinearSegmentedColormap  # Classe pra criar paleta de cores personalizadas
import json  # Biblioteca para armazenamento e manipulação de dados no formato JSON
from pymongo import MongoClient # Biblioteca que permite a interação entre o Python e o BDNR mongo 
from datetime import datetime # Biblioteca que fornece classes para manipular data e hora 
import os  # Biblioteca para interagir com o sistema operacional 


WIDTH, HEIGHT = 1560, 1024  # Tamanho da janela
GRID_SIZE = 70  # Tamanho de cada cédula do HeatMap

pygame.init()  # Inicialização do PyGame
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Define uma janela com as dimensões definidas anteriormente 
pygame.display.set_caption("Rastreamento Ocular e Heatmap") # Nomeia essa tela 

# Tenta carregar a imagem do design com as dimensões definidas anteriormente
try:
    design_image = pygame.image.load('img.png')  
    design_image = pygame.transform.scale(design_image, (WIDTH, HEIGHT))  
except pygame.error as e:
    print(f"Erro ao carregar a imagem: {e}")  
    design_image = None  

# Inicializa o MediaPipe e refina os landmarks 
mp_face_mesh = mp.solutions.face_mesh  
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)  

# Define os landmarks utilizados para o cálculo do centro da irís 
RIGHT_IRIS = [469, 470, 471, 472]  
LEFT_IRIS = [474, 475, 476, 477]  

# Função que calcula a média das coordenadas x e y dos pontos da íris para determinar o centro
def get_iris_center(landmarks, iris_points):
    x = np.mean([landmarks[point].x for point in iris_points])  
    y = np.mean([landmarks[point].y for point in iris_points])  
    return int(x * WIDTH), int(y * HEIGHT)  

# Cria a matriz do heatmap, inicialmente preenchida com zeros
matriz = np.zeros((HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE))  

# Função para salvar a matriz no banco de dados
def save_matriz_to_db(idUsuario: int, idFase: int, matrizFoco: list, tempoFocoEsperado: float, tempoFoco: float, acertos: int, erros: int, duracao: str = "00:01:00"):
    # A função .toList(), converte a matriz do mapa em uma lista de listas, ou seja, cada linha da matriz, torna-se uma sub-lista dentro da lista principal.
    try: 
        client = MongoClient("mongodb://localhost:27017/")
        db = client["pi"]
        collection = db["TestesRastreamentoOcular"]
        
        doc = {
            "idUsuario": idUsuario,
            "idFase": idFase,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duracao": duracao,
            "matrizFoco": matrizFoco.tolist(),
            "tempoFocoEsperado": tempoFocoEsperado,
            "tempoFoco": tempoFoco,
            "acertos": acertos,
            "erros": erros  
        }
        collection.insert_one(doc)
        print("✅ Dados salvos com sucesso no mongoDB!")
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        
def collect_matriz_json_data():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["pi"]
        collection = db["TestesRastreamentoOcular"]
        
        # Buscar a matriz mais recente pelo id decrescente
        resultado = collection.find({}, sort=[("_id", -1)]).limit(3)
        
        total_acertos = 0 
        total_erros = 0 
        
        for doc in resultado:
            acertos = doc.get("acertos", 0)
            erros = doc.get("erros", 0)
            total_acertos += acertos
            total_erros += erros
            matriz = doc["matrizFoco"]
            print(f"Matriz Foco: {matriz}")
            
        # Exibe o total de acertos e erros no terminal
        print(f"Total de acertos nos últimos 3 testes: {total_acertos}")
        print(f"Total de erros nos últimos 3 testes: {total_erros}")
    except Exception as e:
        print(f"❌ Erro ao buscar dados no MongoDB: {e}")
        return None


# Inicia a câmera 
cap = cv2.VideoCapture(0)  
running = True  


while cap.isOpened() and running:  
    success, frame = cap.read()  
    if not success:  
        break

    # Espelha a imagem
    frame = cv2.flip(frame, 1)  
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    results = face_mesh.process(rgb_frame) 
    
    if design_image:
        screen.blit(design_image, (0, 0)) 

    # Para cada rosto detectado no frame:
    if results.multi_face_landmarks:  
        for face_landmarks in results.multi_face_landmarks:  
            # Calcula o centro da irís do olho direito e esquerdo através da função criada anteriormente
            right_iris_center = get_iris_center(face_landmarks.landmark, RIGHT_IRIS)  
            left_iris_center = get_iris_center(face_landmarks.landmark, LEFT_IRIS)  
            
            # Faz a média do centro da irís direita e esquerda, para ser somente um ponto representando os olhos
            iris_x = int((right_iris_center[0] + left_iris_center[0]) / 2)
            iris_y = int((right_iris_center[1] + left_iris_center[1]) / 2)

            # Converte o centro aproximado do olhar para um grid específico no mapa
            grid_x = iris_x // GRID_SIZE  
            grid_y = iris_y // GRID_SIZE  

            # Verifica se o olhar mapeado pra tela está dentro do heatmap pra evitar erros 
            if 0 <= grid_x < matriz.shape[1] and 0 <= grid_y < matriz.shape[0]:
                # Incrementa o valor de cada cédula
                matriz[grid_y, grid_x] += 1  

    # Permite fechar a janela do pygame e encerrar o rastreamento ocular quando eu clico pra sair
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False  

    # Atualiza a tela com as novas mudanças.
    pygame.display.flip()  

# Libera o recuso da câmera 
cap.release()  

# Chamada da função pra salvar a matriz no mongo
save_matriz_to_db(
    idUsuario=1,
    idFase=1,
    matrizFoco=matriz, 
    tempoFocoEsperado=0.3,
    tempoFoco=0.3,
    acertos=5,
    erros=2
)
collect_matriz_json_data()

# Fechamento das janelas 
waiting = True
while waiting:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            waiting = False  

pygame.quit()  

