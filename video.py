import pygame # Biblioteca para criar interfaces visuais com manipulações de imagens
import cv2 # Biblioteca de visão computacional

# o vídeo é aberto pela função VideoCapture; o objeto video vai ser usado para ler os frames do vídeo
video = cv2.VideoCapture("teste.mp4")

# tenta ler o primeiro frame, se conseguir: success=true
success, video_image = video.read()

# armazena os frames por segundo do vídeo
fps = video.get(cv2.CAP_PROP_FPS)

# cria a janela do pygame com as dimensões do primeiro frame do vídeo
window = pygame.display.set_mode(video_image.shape[1::-1])

# cria um objeto de controle de tempo para o pygame, garantindo que o vídeo seja exibido com a taxa de FPS
clock = pygame.time.Clock()

run = success  # variáveis que controlam o loop principal; a execução vai continuar enquanto houver frames para exibir
while run:
    clock.tick(fps)  # garante que o vídeo será exibido a uma taxa de FPS constante
    for event in pygame.event.get():  # verifica os eventos do pygame (como o fechamento da janela)
        if event.type == pygame.QUIT:  # se o evento for o fechamento da janela, sai do loop
            run = False
    
    # tenta ler o próximo frame do vídeo
    success, video_image = video.read()

    if success:
        # converte o frame para um formato que o Pygame pode exibir
        video_surf = pygame.image.frombuffer(
            video_image.tobytes(), video_image.shape[1::-1], "BGR")
    else:
        # se não houver mais frames, sai do loop
        run = False

    # exibe o frame na janela do Pygame
    window.blit(video_surf, (0, 0))

    # atualiza a tela do Pygame
    pygame.display.flip()

# encerra o Pygame quando o loop termina
pygame.quit()

# sai do programa
exit()
