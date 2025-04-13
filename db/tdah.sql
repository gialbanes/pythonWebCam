-- Criação do banco de dados
CREATE DATABASE pi_tdah;
USE pi_tdah;

-- Tabela Pessoas
CREATE TABLE Pessoas (
    idPessoa INT AUTO_INCREMENT PRIMARY KEY,
    nomePessoa VARCHAR(100) NOT NULL,
    senha VARCHAR(100) NOT NULL,
    cpfPessoa VARCHAR(14) UNIQUE NOT NULL,
    dataNasc DATE NOT NULL
);

-- Tabela EmailsPessoa
CREATE TABLE EmailsPessoa (
    idEmail INT AUTO_INCREMENT PRIMARY KEY,
    idPessoa INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    FOREIGN KEY (idPessoa) REFERENCES Pessoas(idPessoa)
);

-- Tabela TelefonesPessoa
CREATE TABLE TelefonesPessoa (
    idTelefonePessoa INT AUTO_INCREMENT PRIMARY KEY,
    idPessoa INT NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    FOREIGN KEY (idPessoa) REFERENCES Pessoas(idPessoa)
);

-- Tabela TestesEyeTracking
CREATE TABLE TestesEyeTracking (
    idTeste INT AUTO_INCREMENT PRIMARY KEY,
    idPessoa INT NOT NULL,
    dataCriacao DATETIME NOT NULL,
    tipo VARCHAR(50),
    duracao time,
    matriz json,
    fase VARCHAR(50),
    FOREIGN KEY (idPessoa) REFERENCES Pessoas(idPessoa)
);

-- Tabela Imagens
CREATE TABLE Imagens (
    idImagem INT AUTO_INCREMENT PRIMARY KEY,
    caminho VARCHAR(255) NOT NULL,
    dimensao VARCHAR(50),
    descricao TEXT,
    dataCriacao DATETIME,
    dataAlteracao DATETIME
);

-- Inserção de dados na tabela Pessoas
INSERT INTO Pessoas (nomePessoa, senha, cpfPessoa, dataNasc)
VALUES 
('Giovana da Silva', 'senha123', '123.456.789-00', '2001-04-12'),
('Carlos Henrique', 'senha456', '234.567.890-11', '1995-08-22'),
('Ana Paula Mendes', 'senha789', '345.678.901-22', '1997-12-03'),
('Juliana Santos', 'senha101', '456.789.012-33', '1998-07-19'),
('Roberto Almeida', 'senha202', '567.890.123-44', '1988-05-04'),
('Lucas Pereira', 'senha303', '678.901.234-55', '1992-11-15'),
('Fernanda Costa', 'senha404', '789.012.345-66', '1990-01-25'),
('Paulo Oliveira', 'senha505', '890.123.456-77', '1985-03-30');

-- Inserção de dados na tabela EmailsPessoa
INSERT INTO EmailsPessoa (idPessoa, email)
VALUES 
(1, 'giovana.silva@example.com'),
(2, 'carlos.henrique@example.com'),
(3, 'ana.mendes@example.com'),
(4, 'juliana.santos@example.com'),
(5, 'roberto.almeida@example.com'),
(6, 'lucas.pereira@example.com'),
(7, 'fernanda.costa@example.com'),
(8, 'paulo.oliveira@example.com');

-- Inserção de dados na tabela TelefonesPessoa
INSERT INTO TelefonesPessoa (idPessoa, telefone)
VALUES 
(1, '(11) 98765-4321'),
(2, '(21) 99876-5432'),
(3, '(31) 99887-6543'),
(4, '(41) 98888-7777'),
(5, '(51) 97999-8888'),
(6, '(61) 96788-9999'),
(7, '(71) 95677-7777'),
(8, '(81) 95566-6666');

-- Inserção de dados na tabela Imagens
INSERT INTO Imagens (caminho, dimensao, descricao, dataCriacao, dataAlteracao)
VALUES 
('imagens/img1.jpg', '800x800', 'Atenção Seletiva (único estímulo)', '2025-04-13 10:00:00', '2025-04-13 10:30:00'),
('imagens/img2.jpg', '800x800', 'Atenção Seletiva (dois estímulos)', '2025-04-12 14:00:00', '2025-04-12 15:00:00'),
('imagens/img3.jpg', '800x800', 'Atenção Alternada', '2025-04-11 09:00:00', '2025-04-11 09:30:00');
