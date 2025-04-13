import cv2  # Biblioteca de visão computacional
import mediapipe as mp  # Framework capaz de detctar elementos em vídeos e imagens
import numpy as np  # Biblioteca que realiza operações em arrays multidimensionais
import pygame # Biblioteca para criar interfaces visuais com manipulaçoes de imagens
import matplotlib.pyplot as plt  # Biblioteca para criação de gráficos 2D e 3D com visualizações estáticas, animadas e interativas
from matplotlib.colors import LinearSegmentedColormap  # Classe pra criar paleta de cores personalizadas
import json  # Biblioteca para armazenamento e manipulação de dados no formato JSON
import mysql.connector # Biblioteca que permite a interação entre o Python e o banco de dados MySQL 
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
def save_matriz_to_db(idPessoa, matriz_olhar):
    # A função .toList(), converte a matriz do mapa em uma lista de listas, ou seja, cada linha da matriz, torna-se uma sub-lista dentro da lista principal.
    # A função json.dumps() converte essa lista em uma String no formato JSON
    matriz_json = json.dumps(matriz_olhar.tolist())  
    print("Matriz JSON para salvar:", matriz_json)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pi_tdah"
    )
    query = conn.cursor() # O método cursor permite fazer consultas, interagir com o banco de dados
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    try:
        query.execute("""
            INSERT INTO TestesEyeTracking (idPessoa, dataCriacao, tipo, duracao, matriz, fase)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (idPessoa, now, 'Único estímulo', '00:01:00', matriz_json, 'Primeira fase'))
        conn.commit() # Finaliza fazendo com o que os dados sejam salvos no BD
    except mysql.connector.Error as err:
        print(f"Erro ao inserir dados no banco de dados: {err}")
    finally:
        query.close()
        conn.close()
        
def collect_matriz_json_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pi_tdah"
    )
    query = conn.cursor() # O método cursor permite fazer consultas, interagir com o banco de dados
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        query.execute("""
            SELECT matriz FROM TestesEyeTracking ORDER BY idTeste DESC LIMIT 1;
        """)
        
        # Obtendo o dado da consulta
        result = query.fetchone()
        
        # Certificando que um resultado foi encontrado
        if result:
            matriz = result[0]
        else:
            matriz = None  # Caso não haja dado para o id fornecido
        
        return matriz
    except mysql.connector.Error as err:
        print(f"Erro ao inserir dados no banco de dados: {err}")
    finally:
        query.close()
        conn.close()


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

# Chamada das funções 
save_matriz_to_db(1, matriz)

# Fechamento das janelas 
waiting = True
while waiting:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            waiting = False  

pygame.quit()  

