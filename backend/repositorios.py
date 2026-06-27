# -*- coding: utf-8 -*-
"""
Módulo com as classes de repositório, responsáveis por toda a
manutenção (CRUD) das tabelas do banco de dados.

A classe RepositorioBase é abstrata (módulo abc) e define o
"contrato" que todo repositório deve seguir: criar, listar, buscar
por id, atualizar e excluir. Cada tabela tem seu próprio repositório
concreto, que implementa esse contrato de um jeito específico
(isso é o conceito de polimorfismo).

O método _cursor() em RepositorioBase garante que a conexão está
viva antes de abrir qualquer cursor — reconecta automaticamente se
o MariaDB encerrou a conexão por inatividade (erros 2006/2013:
"MySQL server has gone away" / "Lost connection").
"""

import pymysql
from abc import ABC, abstractmethod
from datetime import datetime

from modelos import Categoria, Tecnico, Solicitante, Chamado, Usuario
from seguranca import gerar_hash_senha, verificar_senha


class RepositorioBase(ABC):
    """Classe abstrata com as operações básicas de CRUD."""

    def __init__(self, conexao, db=None):
        self.conexao = conexao
        self._db = db  # referência ao objeto Conexao para reconexão

    def _cursor(self):
        """
        Retorna um cursor com conexão garantidamente válida.

        Reconecta automaticamente se o MariaDB encerrou a conexão
        por inatividade (2006: MySQL server has gone away /
        2013: Lost connection during query).
        """
        try:
            self.conexao.ping(reconnect=True)
        except Exception:
            if self._db is not None:
                self.conexao = self._db.reconectar()
        return self.conexao.cursor()

    @abstractmethod
    def criar(self, *args, **kwargs): ...

    @abstractmethod
    def listar(self): ...

    @abstractmethod
    def buscar_por_id(self, id_registro: int): ...

    @abstractmethod
    def atualizar(self, id_registro: int, *args, **kwargs): ...

    @abstractmethod
    def excluir(self, id_registro: int): ...


class CategoriaRepositorio(RepositorioBase):
    def criar(self, nome, descricao):
        cursor = self._cursor()
        cursor.execute(
            "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
            (nome, descricao),
        )
        self.conexao.commit()
        return cursor.lastrowid

    def listar(self):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM categorias ORDER BY id_categoria")
        return [
            Categoria(linha["id_categoria"], linha["nome"], linha["descricao"])
            for linha in cursor.fetchall()
        ]

    def buscar_por_id(self, id_categoria):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM categorias WHERE id_categoria = %s", (id_categoria,))
        linha = cursor.fetchone()
        if linha is None:
            return None
        return Categoria(linha["id_categoria"], linha["nome"], linha["descricao"])

    def atualizar(self, id_categoria, nome, descricao):
        cursor = self._cursor()
        cursor.execute(
            "UPDATE categorias SET nome = %s, descricao = %s WHERE id_categoria = %s",
            (nome, descricao, id_categoria),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def excluir(self, id_categoria):
        cursor = self._cursor()
        cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id_categoria,))
        self.conexao.commit()
        return cursor.rowcount > 0


class TecnicoRepositorio(RepositorioBase):
    def criar(self, nome, especialidade, telefone, email):
        cursor = self._cursor()
        cursor.execute(
            "INSERT INTO tecnicos (nome, especialidade, telefone, email) VALUES (%s, %s, %s, %s)",
            (nome, especialidade, telefone, email),
        )
        self.conexao.commit()
        return cursor.lastrowid

    def listar(self):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM tecnicos ORDER BY id_tecnico")
        return [
            Tecnico(linha["id_tecnico"], linha["nome"], linha["especialidade"],
                    linha["telefone"], linha["email"])
            for linha in cursor.fetchall()
        ]

    def buscar_por_id(self, id_tecnico):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,))
        linha = cursor.fetchone()
        if linha is None:
            return None
        return Tecnico(linha["id_tecnico"], linha["nome"], linha["especialidade"],
                       linha["telefone"], linha["email"])

    def atualizar(self, id_tecnico, nome, especialidade, telefone, email):
        cursor = self._cursor()
        cursor.execute(
            "UPDATE tecnicos SET nome=%s, especialidade=%s, telefone=%s, email=%s WHERE id_tecnico=%s",
            (nome, especialidade, telefone, email, id_tecnico),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def excluir(self, id_tecnico):
        cursor = self._cursor()
        cursor.execute("DELETE FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,))
        self.conexao.commit()
        return cursor.rowcount > 0


class SolicitanteRepositorio(RepositorioBase):
    def criar(self, nome, setor, telefone, email):
        cursor = self._cursor()
        cursor.execute(
            "INSERT INTO solicitantes (nome, setor, telefone, email) VALUES (%s, %s, %s, %s)",
            (nome, setor, telefone, email),
        )
        self.conexao.commit()
        return cursor.lastrowid

    def listar(self):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM solicitantes ORDER BY id_solicitante")
        return [
            Solicitante(linha["id_solicitante"], linha["nome"], linha["setor"],
                        linha["telefone"], linha["email"])
            for linha in cursor.fetchall()
        ]

    def buscar_por_id(self, id_solicitante):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM solicitantes WHERE id_solicitante = %s", (id_solicitante,))
        linha = cursor.fetchone()
        if linha is None:
            return None
        return Solicitante(linha["id_solicitante"], linha["nome"], linha["setor"],
                           linha["telefone"], linha["email"])

    def atualizar(self, id_solicitante, nome, setor, telefone, email):
        cursor = self._cursor()
        cursor.execute(
            "UPDATE solicitantes SET nome=%s, setor=%s, telefone=%s, email=%s WHERE id_solicitante=%s",
            (nome, setor, telefone, email, id_solicitante),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def excluir(self, id_solicitante):
        cursor = self._cursor()
        cursor.execute("DELETE FROM solicitantes WHERE id_solicitante = %s", (id_solicitante,))
        self.conexao.commit()
        return cursor.rowcount > 0


class ChamadoRepositorio(RepositorioBase):
    """
    Repositório da tabela central do sistema. Além do CRUD básico,
    contém métodos próprios do domínio (fechar_chamado, listar_por_status).
    """

    CONSULTA_BASE = """
        SELECT c.*, cat.nome AS nome_categoria,
               s.nome AS nome_solicitante, t.nome AS nome_tecnico
        FROM chamados c
        JOIN categorias cat ON c.id_categoria = cat.id_categoria
        JOIN solicitantes s ON c.id_solicitante = s.id_solicitante
        LEFT JOIN tecnicos t ON c.id_tecnico = t.id_tecnico
    """

    def criar(self, titulo, descricao, prioridade, id_categoria, id_solicitante, id_tecnico=None):
        data_abertura = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor = self._cursor()
        cursor.execute(
            """INSERT INTO chamados
               (titulo, descricao, prioridade, status, data_abertura,
                id_categoria, id_solicitante, id_tecnico)
               VALUES (%s, %s, %s, 'Aberto', %s, %s, %s, %s)""",
            (titulo, descricao, prioridade, data_abertura, id_categoria, id_solicitante, id_tecnico),
        )
        self.conexao.commit()
        return cursor.lastrowid

    def _montar_chamado(self, linha):
        return Chamado(
            linha["id_chamado"], linha["titulo"], linha["descricao"],
            linha["prioridade"], linha["status"], linha["data_abertura"],
            linha["data_fechamento"], linha["id_categoria"],
            linha["id_solicitante"], linha["id_tecnico"],
            nome_categoria=linha["nome_categoria"],
            nome_solicitante=linha["nome_solicitante"],
            nome_tecnico=linha["nome_tecnico"],
        )

    def listar(self):
        cursor = self._cursor()
        cursor.execute(self.CONSULTA_BASE + " ORDER BY c.id_chamado")
        return [self._montar_chamado(linha) for linha in cursor.fetchall()]

    def listar_por_status(self, status):
        cursor = self._cursor()
        cursor.execute(self.CONSULTA_BASE + " WHERE c.status = %s ORDER BY c.id_chamado", (status,))
        return [self._montar_chamado(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_chamado):
        cursor = self._cursor()
        cursor.execute(self.CONSULTA_BASE + " WHERE c.id_chamado = %s", (id_chamado,))
        linha = cursor.fetchone()
        return self._montar_chamado(linha) if linha else None

    def atualizar(self, id_chamado, titulo, descricao, prioridade, id_tecnico):
        cursor = self._cursor()
        cursor.execute(
            """UPDATE chamados
               SET titulo = %s, descricao = %s, prioridade = %s, id_tecnico = %s
               WHERE id_chamado = %s""",
            (titulo, descricao, prioridade, id_tecnico, id_chamado),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def fechar_chamado(self, id_chamado):
        data_fechamento = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor = self._cursor()
        cursor.execute(
            "UPDATE chamados SET status = 'Fechado', data_fechamento = %s WHERE id_chamado = %s",
            (data_fechamento, id_chamado),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def excluir(self, id_chamado):
        cursor = self._cursor()
        cursor.execute("DELETE FROM chamados WHERE id_chamado = %s", (id_chamado,))
        self.conexao.commit()
        return cursor.rowcount > 0


class UsuarioRepositorio(RepositorioBase):
    """
    Repositório das contas de acesso (login) ao sistema.
    """

    def criar(self, nome_usuario, senha, tipo_usuario, nome_completo):
        senha_hash, salt = gerar_hash_senha(senha)
        cursor = self._cursor()
        cursor.execute(
            """INSERT INTO usuarios (nome_usuario, senha_hash, salt, tipo_usuario, nome_completo)
               VALUES (%s, %s, %s, %s, %s)""",
            (nome_usuario, senha_hash, salt, tipo_usuario, nome_completo),
        )
        self.conexao.commit()
        return cursor.lastrowid

    def _montar(self, linha):
        return Usuario(
            linha["id_usuario"], linha["nome_usuario"], linha["senha_hash"],
            linha["salt"], linha["tipo_usuario"], linha["nome_completo"],
        )

    def listar(self):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
        return [self._montar(linha) for linha in cursor.fetchall()]

    def buscar_por_id(self, id_usuario):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        linha = cursor.fetchone()
        return self._montar(linha) if linha else None

    def buscar_por_nome_usuario(self, nome_usuario):
        cursor = self._cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
        linha = cursor.fetchone()
        return self._montar(linha) if linha else None

    def atualizar(self, id_usuario, tipo_usuario, nome_completo, nova_senha=None):
        cursor = self._cursor()
        if nova_senha:
            senha_hash, salt = gerar_hash_senha(nova_senha)
            cursor.execute(
                """UPDATE usuarios SET tipo_usuario = %s, nome_completo = %s,
                   senha_hash = %s, salt = %s WHERE id_usuario = %s""",
                (tipo_usuario, nome_completo, senha_hash, salt, id_usuario),
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET tipo_usuario = %s, nome_completo = %s WHERE id_usuario = %s",
                (tipo_usuario, nome_completo, id_usuario),
            )
        self.conexao.commit()
        return cursor.rowcount > 0

    def excluir(self, id_usuario):
        cursor = self._cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        self.conexao.commit()
        return cursor.rowcount > 0

    def autenticar(self, nome_usuario, senha):
        """Retorna o objeto Usuario se as credenciais forem válidas, ou None."""
        usuario = self.buscar_por_nome_usuario(nome_usuario)
        if usuario is None:
            return None
        if verificar_senha(senha, usuario.senha_hash, usuario.salt):
            return usuario
        return None
