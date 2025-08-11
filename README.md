# Focus Quest

Focus Quest é um aplicativo interativo desenvolvido para realizar o rastreamento ocular em tempo real. O sistema coleta dados do movimento ocular e os armazena para análise posterior.

## 🚀 Funcionalidades
- **Rastreamento Ocular**: Captura e rastreia o movimento dos olhos em tempo real.
- **Armazenamento de Dados**: Salva os dados de foco ocular em um banco de dados MongoDB.
- **Análise de Desempenho**: Permite a coleta de acertos, erros e o tempo de foco para avaliação.
- **Interface Visual**: Mostra o design e resultados diretamente na tela do jogo.

## 🛠️ Tecnologias Utilizadas
- **OpenCV**: Biblioteca de visão computacional para capturar imagens da webcam e processá-las.
- **MediaPipe**: Framework para rastreamento de pontos faciais e oculares.
- **Pygame**: Biblioteca para criar interfaces gráficas e interatividade.
- **MongoDB**: Banco de dados para armazenar os resultados dos testes de rastreamento ocular.
- **Python**: Linguagem de programação principal para a lógica do aplicativo.

## 📂 Estrutura do Projeto

```plaintext
pythonWebcam/
├── main.py                 # Script do rastreamento ocular
├── README.md               # Documentação do projeto
├── .gitignore              # Arquivos ignorados pelo Git
├── img.png                 # Imagem de uma fase do jogo que será aberta pelo PyGame
```

## Atenção!
O MediaPipe não possui compatibilidade com a versão 3.13 do Python. Portanto, se for necessário, crie uma venv com a versão 3.12. 

1. Baixe a versão correta do Python 

2. No terminal do seu projeto, para criar a venv: 
```bash
py -3.12 -m venv venv312  
```

3. Em seguida, ative a venv com: 
```bash
venv312\Scripts\activate
```

4. Para checar que a versão está correta:
```bash
python --version
```

## 📦 Instalação
1. Clone o repositório:

```bash
git clone https://github.com/gialbanes/pythonWebcam.git
cd pythonWebcam
```

2. Instale as dependências:

```bash
pip install opencv-python mediapipe numpy pygame pymongo
```

3. Execute o script principal:
```bash
python main.py
```

## 🕹️ Como testar?
1. Ao iniciar a aplicação, a camêra será inicializada e uma janela do PyGame aberta com uma imagem de uma fase do jogo

2. Permaneça olhando para os elementos da tela enquanto o rastreamento ocualar acontece

3. Ao fechar a janela do PyGame, no seu terminal, serão exibidos alguns dados, sendo eles:
- As últimas 3 matrizes registradas no banco, correnpondente ao seu olhar nas supostas 3 fases do jogo (até o momento é somente uma fase)
- Média de acertos nas 3 fases
- Média de erros nas 3 fases
- O tempo que você demorou no rastreamento ocular 

Esses dados serão utilizados para análises futuras do comportamento do jogador, para assim, gerar o feedback à ele.


## 📖 Funções Principais
- get_iris_center(): Calcula o centro da íris com base nos pontos fornecidos pelo MediaPipe.

- save_matriz_to_db(): Salva os dados de rastreamento ocular (foco e tempo de observação) no banco de dados MongoDB.

- collect_matriz_json_data(): Coleta os últimos dados salvos no banco para análise de desempenho.

## 📄 Licença
Este projeto está licenciado sob a MIT License.

Desenvolvido com ❤️ por Amanda, Arthur e Giovana.
