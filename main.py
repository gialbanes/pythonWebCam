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
heatmap = np.zeros((HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE))  

# Definição das cores do heatmap
colors = [(1, 1, 1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (1, 0, 0, 1)]  
# Cria uma mapa de cores lineares com o nome "custom_map" e com as cores definidas anteriormente
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)  

# Função para salvar a matriz do heatmap no banco de dados
def save_heatmap_to_db(heatmap_matrix, filepath, id_tela=1, id_teste=1):
    # A função .toList(), converte a matriz do mapa em uma lista de listas, ou seja, cada linha da matriz, torna-se uma sub-lista dentro da lista principal.
    # A função json.dumps() converte essa lista em uma String no formato JSON
    heatmap_json = json.dumps(heatmap_matrix.tolist())  
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="uEye"
    )
    query = conn.cursor() # O método cursor permite fazer consultas, interagir com o banco de dados
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    try:
        query.execute("""
            INSERT INTO heatmaps (id_tela, id_teste, grid_size, heatmap_data, heatmap_image, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (id_tela, id_teste, GRID_SIZE, heatmap_json, filepath, now))
        conn.commit() # Finaliza fazendo com o que os dados sejam salvos no BD
    except mysql.connector.Error as err:
        print(f"Erro ao inserir dados no banco de dados: {err}")
    finally:
        query.close()
        conn.close()

# Função para salvar a imagem do heatmap com o fundo transparente 
def save_heatmap_image_transparent(matrix, filename):
    plt.figure(figsize=(8, 6), dpi=100)
    # Exibe a matriz como uma imagem 2D como um mapa de calor
    # cmap=cmap: cores definidas anteriormente 
    # interpolation='nearest': faz com que os pixels sejam exibidos como blocos sólidos 
    # extent=[0, WIDTH, HEIGHT, 0]: define os limites da imagem de acordo com as dimensões definidas anteriormente
    plt.imshow(matrix, cmap=cmap, alpha=0.5, interpolation='nearest', extent=[0, WIDTH, HEIGHT, 0])
    # Desliga os eixos da figure, ou seja, na janela só aparece  o heatmap
    plt.axis('off')  
    # Salva a imagem
    # bbox_inches='tight': Remove os espaços em branco ao redor da imagem, recortando-a para ajustar exatamente ao conteúdo.
    # pad_inches=0:  Elimina qualquer espaço de preenchimento adicional ao redor da imagem.
    plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=300, transparent=True)  
    plt.close()  

# Função para gerar um nome único a cada imagem gerada através do heatmap 
def generate_unique_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
    return f"heatmap_transparent_{timestamp}.png"

# Função pra exibir a imagem do heatmap em cima do design 
def display_heatmap(heatmap):
    # Cria uma superfície onde o heatmap será desenhado, definindo as dimensões criadas anteriormente e fazendo com que a superfície suporte transparência
    heatmap_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  

    # Encontra o valor máximo na matriz pra normalizar as intensidades das cores 
    # if np.any(heatmap): verifica se tem algum valor diferente de 0 na matriz, ou seja, se o cliente focou em uma região
    # np.max(heatmap): se tiver valores diferentes de 0, essa função retorna o valor máximo na matriz
    # else 1: se todos os valores da matriz forem 0, o max_count é definido como 1, só pra evitar divisão por 0 na próxima etapa.
    max_count = np.max(heatmap) if np.any(heatmap) else 1  
    # Percorre cada grid_size da matriz
    for y in range(heatmap.shape[0]): # Linhas
        for x in range(heatmap.shape[1]): # Colunas
            # Conta a intensidade em cada cédula, ou seja, de quanto foi o foco visual do cliente
            count = heatmap[y, x]  
            if count > 0:
                # Normaliza o valor de count de 0 a 1 
                normalized_value = count / max_count  
                # Converte o valor em uma cor de acordo com o mapa de cores lineares criado anteriormente 
                color = cmap(normalized_value)  
                # Transforma as cores R, G, e B de 0-1 para 0-255 e define 128 para o canal de transparência (A), tornando as áreas semitransparentes
                rgba_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), 128)  
                # Desenha um quadrado preenchido na superfície criada pra representar o foco x,y
                # x * GRID_SIZE, y * GRID_SIZE: posição do quadrado na superfície
                # GRID_SIZE, GRID_SIZE: largura e altura do quadrado
                pygame.draw.rect(heatmap_surface, rgba_color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))  

    # Exibe o design com o HeatMap em cima no canto superior esquerdo da janela
    screen.blit(design_image, (0, 0))  
    screen.blit(heatmap_surface, (0, 0))  
    pygame.display.flip()  

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
            if 0 <= grid_x < heatmap.shape[1] and 0 <= grid_y < heatmap.shape[0]:
                # Incrementa o valor de cada cédula
                heatmap[grid_y, grid_x] += 1  

    # Permite fechar a janela do pygame e encerrar o rastreamento ocular quando eu clico pra sair
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False  

    # Prepara a tela pra receber o design com o heatmap por cima
    # Limpa a tela, preenchendo-a com preto
    screen.fill((0, 0, 0))  
    if design_image is not None:
         # Desenha design_image na tela
        screen.blit(design_image, (0, 0))  

    # Atualiza a tela com as novas mudanças.
    pygame.display.flip()  

# Libera o recuso da câmera 
cap.release()  

# Cria a pasta "heatmaps" se ela não existir
if not os.path.exists("heatmaps"):
    os.makedirs("heatmaps")  

# Chamada das funções 
unique_filename = generate_unique_filename()
local_filepath = f"./heatmaps/{unique_filename}"  

save_heatmap_image_transparent(heatmap, filename=local_filepath)

save_heatmap_to_db(heatmap, local_filepath)

display_heatmap(heatmap)

# Fechamento das janelas 
waiting = True
while waiting:
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            waiting = False  

pygame.quit()  