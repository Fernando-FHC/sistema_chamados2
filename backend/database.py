# -*- coding: utf-8 -*-
"""
Módulo responsável pela conexão com o banco de dados MariaDB e pela
criação da estrutura de tabelas do Sistema de Chamados.

As credenciais de conexão são lidas do arquivo .env (via python-dotenv),
para que nunca fiquem escritas diretamente no código-fonte.

Dependências externas (instalar com pip):
    pip install pymysql python-dotenv
"""

import os

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

from seguranca import gerar_hash_senha

# Carrega as variáveis definidas no arquivo .env, se existir.
# Variáveis já definidas no ambiente do sistema operacional têm prioridade.
load_dotenv()


class Conexao:
    """Encapsula a conexão com o banco de dados MariaDB."""

    def __init__(self):
        self.conexao = None

    def conectar(self):
        """Abre a conexão com o MariaDB usando as variáveis de ambiente."""
        self.conexao = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "chamados"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "chamados_db"),
            charset="utf8mb4",
            # DictCursor faz fetchone() e fetchall() retornarem dicionários
            # ({"campo": valor}) em vez de tuplas, mantendo a mesma sintaxe
            # de acesso por nome de coluna que usávamos com o sqlite3.Row.
            cursorclass=pymysql.cursors.DictCursor,
        )
        return self.conexao

    def desconectar(self) -> None:
        """Fecha a conexão com o banco, se estiver aberta."""
        if self.conexao is not None:
            self.conexao.close()

    def criar_tabelas(self) -> None:
        """Cria as tabelas do sistema, caso ainda não existam.

        Diferenças em relação ao SQLite:
        - Cada CREATE TABLE é executado individualmente (não existe executescript).
        - AUTO_INCREMENT no lugar de AUTOINCREMENT.
        - ENUM no lugar de CHECK para valores fixos — mais idiomático no MariaDB.
        - ENGINE=InnoDB é obrigatório para suporte a chaves estrangeiras.
        - charset=utf8mb4 suporta emojis e caracteres especiais do português.
        """
        cursor = self.conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id_categoria INT          PRIMARY KEY AUTO_INCREMENT,
                nome         VARCHAR(100) NOT NULL UNIQUE,
                descricao    TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tecnicos (
                id_tecnico    INT          PRIMARY KEY AUTO_INCREMENT,
                nome          VARCHAR(150) NOT NULL,
                especialidade VARCHAR(150),
                telefone      VARCHAR(20),
                email         VARCHAR(150)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitantes (
                id_solicitante INT          PRIMARY KEY AUTO_INCREMENT,
                nome           VARCHAR(150) NOT NULL,
                setor          VARCHAR(150),
                telefone       VARCHAR(20),
                email          VARCHAR(150)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario    INT          PRIMARY KEY AUTO_INCREMENT,
                nome_usuario  VARCHAR(50)  NOT NULL UNIQUE,
                senha_hash    VARCHAR(64)  NOT NULL,
                salt          VARCHAR(8)   NOT NULL,
                tipo_usuario  ENUM('Administrador','Usuário')
                                  NOT NULL DEFAULT 'Usuário',
                nome_completo VARCHAR(150)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        self.conexao.commit()

    def popular_dados_iniciais(self) -> None:
        """Insere registros de exemplo apenas se as tabelas estiverem vazias.

        Diferença do SQLite: fetchone()[0] não funciona com DictCursor —
        é necessário nomear a coluna com AS e acessar pelo nome.
        """
        cursor = self.conexao.cursor()

        cursor.execute("SELECT COUNT(*) AS total FROM categorias")
        if cursor.fetchone()["total"] == 0:
            cursor.executemany(
                "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
                [
                    ("Informática",      "Problemas com computadores, redes e sistemas"),
                    ("Telefonia",        "Problemas com ramais, telefones e centrais"),
                    ("Manutenção Geral", "Reparos elétricos, hidráulicos e estruturais"),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM tecnicos")
        if cursor.fetchone()["total"] == 0:
            cursor.executemany(
                "INSERT INTO tecnicos (nome, especialidade, telefone, email) VALUES (%s, %s, %s, %s)",
                [
                    ("Carlos Souza", "Redes e Hardware", "(11) 99999-0001", "carlos@empresa.com"),
                    ("Marina Lima",  "Telefonia",        "(11) 99999-0002", "marina@empresa.com"),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM solicitantes")
        if cursor.fetchone()["total"] == 0:
            cursor.executemany(
                "INSERT INTO solicitantes (nome, setor, telefone, email) VALUES (%s, %s, %s, %s)",
                [
                    ("Ana Paula",     "Financeiro",       "(11) 98888-0001", "ana@empresa.com"),
                    ("Bruno Tavares", "Recursos Humanos", "(11) 98888-0002", "bruno@empresa.com"),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        if cursor.fetchone()["total"] == 0:
            hash_admin,   salt_admin   = gerar_hash_senha("admin123")
            hash_usuario, salt_usuario = gerar_hash_senha("usuario123")
            cursor.executemany(
                """INSERT INTO usuarios
                   (nome_usuario, senha_hash, salt, tipo_usuario, nome_completo)
                   VALUES (%s, %s, %s, %s, %s)""",
                [
                    ("admin",   hash_admin,   salt_admin,   "Administrador", "Administrador do Sistema"),
                    ("usuario", hash_usuario, salt_usuario, "Usuário",       "Usuário Padrão"),
                ],
            )

        self.conexao.commit()
