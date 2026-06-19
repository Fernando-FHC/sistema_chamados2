# -*- coding: utf-8 -*-
"""
Módulo com as classes de modelo (entidades) do sistema.

Cada classe representa uma linha das tabelas do banco de dados.
Seguindo o paradigma de Orientação a Objetos, os atributos ficam
encapsulados dentro do objeto, e cada classe sabe como se exibir
(método __str__), em vez de deixar essa lógica espalhada pelo resto
do programa.
"""


class Categoria:
    def __init__(self, id_categoria, nome, descricao):
        self.id_categoria = id_categoria
        self.nome = nome
        self.descricao = descricao

    def __str__(self):
        return f"[{self.id_categoria}] {self.nome} - {self.descricao}"


class Tecnico:
    def __init__(self, id_tecnico, nome, especialidade, telefone, email):
        self.id_tecnico = id_tecnico
        self.nome = nome
        self.especialidade = especialidade
        self.telefone = telefone
        self.email = email

    def __str__(self):
        return (
            f"[{self.id_tecnico}] {self.nome} | {self.especialidade} "
            f"| Tel: {self.telefone} | E-mail: {self.email}"
        )


class Solicitante:
    def __init__(self, id_solicitante, nome, setor, telefone, email):
        self.id_solicitante = id_solicitante
        self.nome = nome
        self.setor = setor
        self.telefone = telefone
        self.email = email

    def __str__(self):
        return (
            f"[{self.id_solicitante}] {self.nome} | Setor: {self.setor} "
            f"| Tel: {self.telefone} | E-mail: {self.email}"
        )


class Usuario:
    """
    Representa uma conta de acesso ao sistema (login).

    O campo tipo_usuario define o nível de permissão: 'Administrador'
    tem controle total sobre o sistema, enquanto 'Usuário' só pode
    abrir novos chamados.
    """

    def __init__(self, id_usuario, nome_usuario, senha_hash, salt, tipo_usuario, nome_completo):
        self.id_usuario = id_usuario
        self.nome_usuario = nome_usuario
        self.senha_hash = senha_hash
        self.salt = salt
        self.tipo_usuario = tipo_usuario
        self.nome_completo = nome_completo

    @property
    def eh_administrador(self):
        return self.tipo_usuario == "Administrador"

    def __str__(self):
        return f"[{self.id_usuario}] {self.nome_usuario} ({self.tipo_usuario}) - {self.nome_completo}"


class Chamado:
    """
    Representa um chamado de suporte.

    Os campos nome_categoria, nome_solicitante e nome_tecnico são
    auxiliares, usados apenas para exibição (são preenchidos a partir
    de um JOIN no banco), e não existem como colunas na tabela
    "chamados" — eles existem em "categorias", "solicitantes" e
    "tecnicos", respectivamente.
    """

    def __init__(
        self,
        id_chamado,
        titulo,
        descricao,
        prioridade,
        status,
        data_abertura,
        data_fechamento,
        id_categoria,
        id_solicitante,
        id_tecnico,
        nome_categoria=None,
        nome_solicitante=None,
        nome_tecnico=None,
    ):
        self.id_chamado = id_chamado
        self.titulo = titulo
        self.descricao = descricao
        self.prioridade = prioridade
        self.status = status
        self.data_abertura = data_abertura
        self.data_fechamento = data_fechamento
        self.id_categoria = id_categoria
        self.id_solicitante = id_solicitante
        self.id_tecnico = id_tecnico
        self.nome_categoria = nome_categoria
        self.nome_solicitante = nome_solicitante
        self.nome_tecnico = nome_tecnico

    def __str__(self):
        tecnico_str = self.nome_tecnico if self.nome_tecnico else "Não atribuído"
        fechamento_str = self.data_fechamento if self.data_fechamento else "-"
        return (
            f"[{self.id_chamado}] {self.titulo}\n"
            f"    Categoria: {self.nome_categoria} | Prioridade: {self.prioridade} "
            f"| Status: {self.status}\n"
            f"    Solicitante: {self.nome_solicitante} | Técnico: {tecnico_str}\n"
            f"    Aberto em: {self.data_abertura} | Fechado em: {fechamento_str}\n"
            f"    Descrição: {self.descricao}"
        )
