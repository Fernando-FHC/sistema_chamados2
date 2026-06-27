-- ============================================================
--  Schema do Sistema de Chamados — MariaDB
-- ============================================================
USE chamados_db;

-- ── categorias ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT          PRIMARY KEY AUTO_INCREMENT,
    nome         VARCHAR(100) NOT NULL UNIQUE,
    descricao    TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── tecnicos ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS tecnicos (
    id_tecnico    INT          PRIMARY KEY AUTO_INCREMENT,
    nome          VARCHAR(150) NOT NULL,
    especialidade VARCHAR(150),
    telefone      VARCHAR(20),
    email         VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── solicitantes ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS solicitantes (
    id_solicitante INT          PRIMARY KEY AUTO_INCREMENT,
    nome           VARCHAR(150) NOT NULL,
    setor          VARCHAR(150),
    telefone       VARCHAR(20),
    email          VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── chamados ─────────────────────────────────────────────────
-- Tabela central do sistema.

CREATE TABLE IF NOT EXISTS chamados (
    id_chamado      INT          PRIMARY KEY AUTO_INCREMENT,
    titulo          VARCHAR(200) NOT NULL,
    descricao       TEXT,
    prioridade      ENUM('Baixa','Média','Alta')
                        NOT NULL DEFAULT 'Média',
    status          ENUM('Aberto','Em Andamento','Fechado')
                        NOT NULL DEFAULT 'Aberto',
    data_abertura   VARCHAR(20)  NOT NULL,
    data_fechamento VARCHAR(20),
    id_categoria    INT          NOT NULL,
    id_solicitante  INT          NOT NULL,
    id_tecnico      INT,
    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_solicitante)
        REFERENCES solicitantes(id_solicitante),
    FOREIGN KEY (id_tecnico)
        REFERENCES tecnicos(id_tecnico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── usuarios ─────────────────────────────────────────────────
-- Armazena apenas o hash da senha (SHA-256 = 64 caracteres hex)
-- e o salt (8 caracteres aleatórios) — nunca a senha em texto puro.

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario    INT          PRIMARY KEY AUTO_INCREMENT,
    nome_usuario  VARCHAR(50)  NOT NULL UNIQUE,
    senha_hash    VARCHAR(64)  NOT NULL,
    salt          VARCHAR(8)   NOT NULL,
    tipo_usuario  ENUM('Administrador','Usuário')
                      NOT NULL DEFAULT 'Usuário',
    nome_completo VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
