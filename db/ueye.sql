create database if not exists ueye;
use ueye;

create table heatmaps (
id_heatmap int auto_increment primary key,
id_tela int,
id_teste int,
grid_size int,
heatmap_data json,
heatmap_image varchar(255),
created_at datetime,	
constraint fk_id_tela_heatmap foreign key(id_tela) references telas(id_tela),
constraint fk_id_teste_heatmap foreign key(id_teste) references testesEyeTracking(id_teste)
);

create table designers(
id_designer int auto_increment primary key,
nome_designer varchar(255),
senha CHAR(64)
);

create table emails_designer(
id_email int auto_increment primary key,
id_designer int, 
email varchar(255),
constraint fk_id_designer_email foreign key(id_designer) references designers(id_designer)
);

create table clientes(
id_cliente int auto_increment primary key,
nome_cliente varchar(255),
cargo varchar(100)
);

create table projetos(
id_projeto int auto_increment primary key, 
nome_projeto varchar(255),
descricao varchar(300),
data_criacao date, 
data_atualizacao date,
versao double,
qtd_telas int,
id_designer int,
constraint fk_id_designer_projetos foreign key(id_designer) references designers(id_designer)
);

create table testesEyeTracking(
id_teste int auto_increment primary key, 
data_teste date, 
id_projeto int, 
id_cliente int, 
duracao int,
constraint fk_id_projeto_teste foreign key(id_projeto) references projetos(id_projeto),
constraint fk_id_cliente_teste foreign key(id_cliente) references clientes(id_cliente)
);

create table formularios(
id_form int auto_increment primary key, 
perguntas varchar(400),
id_cliente int, 
nivel_satisfacao int, 
id_projeto int,
constraint fk_id_cliente_form foreign key(id_cliente) references clientes(id_cliente),
constraint fk_id_projeto_form foreign key(id_projeto) references projetos(id_projeto)
);

create table telas(
id_tela int auto_increment primary key,
nome_tela varchar(100),
id_projeto int,
constraint fk_id_projeto_tela foreign key(id_projeto) references projetos(id_projeto)
);

insert into designers (nome_designer, senha) values
('Ana Martins', sha2('senhaAna2024', 256)),
('Bruno Silva', sha2('senhaBruno@01', 256)),
('Carla Souza', sha2('senhaCarla2024!', 256)),
('Daniel Lima', sha2('d4nielL!ma', 256)),
('Elisa Mendes', sha2('elisa2023Senha', 256)),
('Fernando Costa', sha2('fernand@123', 256)),
('Gabriela Dias', sha2('gabr13la!', 256)),
('Henrique Teixeira', sha2('henr1qu3@!', 256)),
('Inês Rocha', sha2('Ines_2024!', 256)),
('João Pedro Alves', sha2('jpa@123Senha', 256));

insert into emails_designer (id_designer, email) values
(1, 'ana.martins@email.com'),
(2, 'bruno.silva@email.com'),
(3, 'carla.souza@email.com'),
(4, 'daniel.lima@email.com'),
(5, 'elisa.mendes@email.com'),
(6, 'fernando.costa@email.com'),
(7, 'gabriela.dias@email.com'),
(8, 'henrique.teixeira@email.com'),
(9, 'ines.rocha@email.com'),
(10, 'joao.pedro.alves@email.com');

INSERT INTO clientes (nome_cliente, cargo) VALUES 
('Ana Silva', 'Gerente de Projetos'),
('Carlos Souza', 'Desenvolvedor de Software'),
('Mariana Costa', 'Analista de Marketing'),
('João Santos', 'Diretor Comercial'),
('Paula Pereira', 'Designer Gráfico'),
('Ricardo Oliveira', 'Analista de Sistemas'),
('Fernanda Lima', 'Coordenadora de RH'),
('Lucas Almeida', 'Especialista em Vendas'),
('Gabriela Torres', 'Consultora de TI'),
('Felipe Andrade', 'Engenheiro de Software');

insert into projetos (nome_projeto, descricao, data_criacao, data_atualizacao, versao, qtd_telas) values
('UX Redesign', 'Projeto de redesign de interfaces para aumentar a usabilidade', '2023-02-15', '2023-10-20', 1.5, 20),
('E-commerce App', 'Aplicativo para facilitar compras online', '2023-04-22', '2024-01-30', 2.1, 15),
('Sistema de Cadastro', 'Sistema para gerenciamento de cadastros de clientes', '2023-06-11', '2024-02-15', 1.8, 10),
('Plataforma Educacional', 'Plataforma para cursos e treinamentos online', '2022-08-05', '2023-12-18', 3.0, 30),
('App de Delivery', 'Aplicativo de entregas para restaurantes locais', '2023-01-19', '2024-06-10', 1.9, 25),
('Portal Financeiro', 'Portal de gerenciamento financeiro para empresas', '2023-07-12', '2024-04-01', 2.3, 12),
('Dashboard Analytics', 'Dashboard para visualização de dados analíticos', '2023-03-09', '2024-03-10', 1.7, 18),
('Gestão de Projetos', 'Sistema para gerenciar e acompanhar projetos', '2022-11-30', '2023-09-25', 2.0, 22),
('Marketplace', 'Marketplace para produtos de beleza', '2023-05-20', '2024-05-18', 2.5, 16),
('Rede Social', 'Rede social focada em profissionais da área de TI', '2023-09-18', '2024-09-20', 1.3, 27);

insert into testesEyeTracking (data_teste, id_projeto, id_cliente, duracao) values
('2023-10-10', 1, 1, 90),
('2024-01-15', 2, 2, 120),
('2024-03-05', 3, 3, 110),
('2024-02-12', 4, 4, 95),
('2024-05-20', 5, 5, 85),
('2024-07-30', 6, 6, 125),
('2024-08-19', 7, 7, 100),
('2024-09-25', 8, 8, 115),
('2024-10-15', 9, 9, 105),
('2024-11-05', 10, 10, 130);

insert into formularios (perguntas, id_cliente, nivel_satisfacao, id_projeto) values
('Pergunta 1', 1, 4, 1),
('Pergunta 2', 2, 3, 2),
('Pergunta 3', 3, 5, 3),
('Pergunta 4', 4, 2, 4),
('Pergunta 5', 5, 4, 5),
('Pergunta 6', 6, 3, 6),
('Pergunta 7', 7, 5, 7),
('Pergunta 8', 8, 1, 8),
('Pergunta 9', 9, 4, 9),
('Pergunta 10', 10, 2, 10);

insert into telas (nome_tela) values
('Tela de Login'),
('Tela de Cadastro'),
('Tela Inicial'),
('Tela de Produtos'),
('Tela de Carrinho'),
('Tela de Pagamento'),
('Tela de Pagamento'),
('Tela de Histórico de Compras'),
('Tela de Perfil do Usuário'),
('Tela de Configurações'),
('Tela de Ajuda');