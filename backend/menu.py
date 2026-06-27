# -*- coding: utf-8 -*-
"""
Módulo de interface (menu em modo texto) do sistema.

A classe Aplicacao concentra toda a interação com o usuário via
terminal e delega a manutenção dos dados para os repositórios. Antes
de mostrar qualquer menu, é necessário fazer login; o menu exibido
depois muda de acordo com o perfil da conta (Administrador tem
controle total, Usuário só pode abrir chamados).
"""

import pymysql.err

from database import Conexao
from repositorios import (
    CategoriaRepositorio,
    TecnicoRepositorio,
    SolicitanteRepositorio,
    ChamadoRepositorio,
    UsuarioRepositorio,
)


# --------------------------------------------------------------------
# Funções auxiliares de leitura/validação de entrada do usuário
# --------------------------------------------------------------------
def ler_inteiro(mensagem, permitir_vazio=False):
    """Lê um número inteiro, repetindo a pergunta até que seja válido."""
    while True:
        valor = input(mensagem).strip()
        if permitir_vazio and valor == "":
            return None
        try:
            return int(valor)
        except ValueError:
            print("Entrada inválida. Digite apenas números.")


def ler_texto(mensagem, obrigatorio=True):
    """Lê um texto, repetindo a pergunta caso esteja vazio (quando obrigatório)."""
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("Este campo não pode ficar em branco.")


def ler_opcao_valida(mensagem, opcoes_validas):
    """Lê um texto garantindo que o valor esteja dentro de uma lista de opções."""
    opcoes_formatadas = "/".join(opcoes_validas)
    while True:
        valor = input(f"{mensagem} ({opcoes_formatadas}): ").strip().title()
        if valor in opcoes_validas:
            return valor
        print(f"Opção inválida. Escolha entre: {opcoes_formatadas}")


def ler_opcao_valida_ou_manter(mensagem, opcoes_validas, valor_atual):
    """Igual à anterior, mas ENTER em branco mantém o valor atual (usado em updates)."""
    opcoes_formatadas = "/".join(opcoes_validas)
    while True:
        valor = input(f"{mensagem} [{valor_atual}] ({opcoes_formatadas}, ENTER mantém): ").strip()
        if valor == "":
            return valor_atual
        valor = valor.title()
        if valor in opcoes_validas:
            return valor
        print(f"Opção inválida. Escolha entre: {opcoes_formatadas}")


def confirmar(mensagem):
    """Pede uma confirmação s/n ao usuário."""
    return ler_texto(mensagem).strip().lower() == "s"


def pausar():
    input("\nPressione ENTER para continuar...")


# --------------------------------------------------------------------
# Classe principal da aplicação
# --------------------------------------------------------------------
class Aplicacao:
    def __init__(self):
        self.conexao_bd = Conexao()
        self.conexao_bd.conectar()
        self.conexao_bd.criar_tabelas()
        self.conexao_bd.popular_dados_iniciais()

        conexao = self.conexao_bd.conexao
        self.repo_categoria = CategoriaRepositorio(conexao)
        self.repo_tecnico = TecnicoRepositorio(conexao)
        self.repo_solicitante = SolicitanteRepositorio(conexao)
        self.repo_chamado = ChamadoRepositorio(conexao)
        self.repo_usuario = UsuarioRepositorio(conexao)

        self.usuario_logado = None

    # ---------------- LOOP PRINCIPAL ----------------
    def executar(self):
        print("=" * 58)
        print(" SISTEMA DE ABERTURA, CONTROLE E FECHAMENTO DE CHAMADOS")
        print(" Informática | Telefonia | Manutenção Geral")
        print("=" * 58)
        try:
            while True:
                self.usuario_logado = self._fazer_login()
                continuar_no_sistema = self._menu_principal()
                if not continuar_no_sistema:
                    print("\nEncerrando o sistema. Até logo!")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\nPrograma interrompido pelo usuário. Encerrando com segurança...")
        finally:
            self.conexao_bd.desconectar()

    def _fazer_login(self):
        print("\n----------------------- LOGIN -----------------------")
        while True:
            nome_usuario = ler_texto("Usuário: ")
            senha = ler_texto("Senha: ")
            usuario = self.repo_usuario.autenticar(nome_usuario, senha)
            if usuario is not None:
                print(f"\nBem-vindo(a), {usuario.nome_completo}! ({usuario.tipo_usuario})")
                return usuario
            print("Usuário ou senha inválidos. Tente novamente.\n")

    def _menu_principal(self):
        """
        Mostra o menu principal de acordo com o perfil do usuário logado.
        Retorna True se o sistema deve voltar para a tela de login
        (logout) ou False se o programa deve ser encerrado.
        """
        eh_admin = self.usuario_logado.eh_administrador

        while True:
            print("\n------------------- MENU PRINCIPAL -------------------")
            if eh_admin:
                print("1 - Gerenciar Categorias")
                print("2 - Gerenciar Técnicos")
                print("3 - Gerenciar Solicitantes")
                print("4 - Gerenciar Chamados")
                print("5 - Gerenciar Usuários")
            else:
                print("1 - Abrir novo chamado")
                print("2 - Listar chamados")
            print("8 - Encerrar sessão (voltar ao login)")
            print("0 - Sair do sistema")
            print("-" * 56)
            opcao = input("Escolha uma opção: ").strip()

            if eh_admin and opcao == "1":
                self._menu_categorias()
            elif eh_admin and opcao == "2":
                self._menu_tecnicos()
            elif eh_admin and opcao == "3":
                self._menu_solicitantes()
            elif eh_admin and opcao == "4":
                self._menu_chamados()
            elif eh_admin and opcao == "5":
                self._menu_usuarios()
            elif not eh_admin and opcao == "1":
                try:
                    self._abrir_chamado(permitir_atribuir_tecnico=False)
                except pymysql.err.IntegrityError as erro:
                    print(f"Não foi possível concluir a operação: {erro}")
                except Exception as erro:
                    print(f"Ocorreu um erro inesperado: {erro}")
                pausar()
            elif not eh_admin and opcao == "2":
                self._listar(self.repo_chamado.listar(), "chamado", detalhado=True)
                pausar()
            elif opcao == "8":
                print(f"\nSessão de '{self.usuario_logado.nome_usuario}' encerrada.")
                return True
            elif opcao == "0":
                return False
            else:
                print("Opção inválida. Tente novamente.")

    # ---------------- CATEGORIAS ----------------
    def _menu_categorias(self):
        while True:
            print("\n---------------- GERENCIAR CATEGORIAS ----------------")
            print("1 - Cadastrar categoria")
            print("2 - Listar categorias")
            print("3 - Buscar categoria por ID")
            print("4 - Atualizar categoria")
            print("5 - Excluir categoria")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    nome = ler_texto("Nome da categoria: ")
                    descricao = ler_texto("Descrição: ", obrigatorio=False)
                    id_novo = self.repo_categoria.criar(nome, descricao)
                    print(f"Categoria cadastrada com sucesso! (ID {id_novo})")
                elif opcao == "2":
                    self._listar(self.repo_categoria.listar(), "categoria")
                elif opcao == "3":
                    id_categoria = ler_inteiro("ID da categoria: ")
                    categoria = self.repo_categoria.buscar_por_id(id_categoria)
                    print(categoria if categoria else "Categoria não encontrada.")
                elif opcao == "4":
                    self._atualizar_categoria()
                elif opcao == "5":
                    self._excluir_categoria()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida.")
            except pymysql.err.IntegrityError as erro:
                print(f"Não foi possível concluir a operação (restrição de integridade): {erro}")
            except Exception as erro:
                print(f"Ocorreu um erro inesperado: {erro}")
            pausar()

    def _atualizar_categoria(self):
        id_categoria = ler_inteiro("ID da categoria que deseja atualizar: ")
        categoria = self.repo_categoria.buscar_por_id(id_categoria)
        if not categoria:
            print("Categoria não encontrada.")
            return
        print(f"Dados atuais: {categoria}")
        nome = ler_texto(f"Novo nome [{categoria.nome}] (ENTER mantém): ", obrigatorio=False) or categoria.nome
        descricao = ler_texto(
            f"Nova descrição [{categoria.descricao}] (ENTER mantém): ", obrigatorio=False
        ) or categoria.descricao
        if self.repo_categoria.atualizar(id_categoria, nome, descricao):
            print("Categoria atualizada com sucesso!")
        else:
            print("Não foi possível atualizar a categoria.")

    def _excluir_categoria(self):
        id_categoria = ler_inteiro("ID da categoria que deseja excluir: ")
        if not confirmar("Tem certeza? Esta ação não pode ser desfeita (s/n): "):
            print("Operação cancelada.")
            return
        if self.repo_categoria.excluir(id_categoria):
            print("Categoria excluída com sucesso!")
        else:
            print("Categoria não encontrada.")

    # ---------------- TÉCNICOS ----------------
    def _menu_tecnicos(self):
        while True:
            print("\n----------------- GERENCIAR TÉCNICOS -----------------")
            print("1 - Cadastrar técnico")
            print("2 - Listar técnicos")
            print("3 - Buscar técnico por ID")
            print("4 - Atualizar técnico")
            print("5 - Excluir técnico")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    nome = ler_texto("Nome do técnico: ")
                    especialidade = ler_texto("Especialidade: ", obrigatorio=False)
                    telefone = ler_texto("Telefone: ", obrigatorio=False)
                    email = ler_texto("E-mail: ", obrigatorio=False)
                    id_novo = self.repo_tecnico.criar(nome, especialidade, telefone, email)
                    print(f"Técnico cadastrado com sucesso! (ID {id_novo})")
                elif opcao == "2":
                    self._listar(self.repo_tecnico.listar(), "técnico")
                elif opcao == "3":
                    id_tecnico = ler_inteiro("ID do técnico: ")
                    tecnico = self.repo_tecnico.buscar_por_id(id_tecnico)
                    print(tecnico if tecnico else "Técnico não encontrado.")
                elif opcao == "4":
                    self._atualizar_tecnico()
                elif opcao == "5":
                    self._excluir_tecnico()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida.")
            except pymysql.err.IntegrityError as erro:
                print(f"Não foi possível concluir a operação (restrição de integridade): {erro}")
            except Exception as erro:
                print(f"Ocorreu um erro inesperado: {erro}")
            pausar()

    def _atualizar_tecnico(self):
        id_tecnico = ler_inteiro("ID do técnico que deseja atualizar: ")
        tecnico = self.repo_tecnico.buscar_por_id(id_tecnico)
        if not tecnico:
            print("Técnico não encontrado.")
            return
        print(f"Dados atuais: {tecnico}")
        nome = ler_texto(f"Novo nome [{tecnico.nome}] (ENTER mantém): ", obrigatorio=False) or tecnico.nome
        especialidade = ler_texto(
            f"Nova especialidade [{tecnico.especialidade}] (ENTER mantém): ", obrigatorio=False
        ) or tecnico.especialidade
        telefone = ler_texto(
            f"Novo telefone [{tecnico.telefone}] (ENTER mantém): ", obrigatorio=False
        ) or tecnico.telefone
        email = ler_texto(f"Novo e-mail [{tecnico.email}] (ENTER mantém): ", obrigatorio=False) or tecnico.email
        if self.repo_tecnico.atualizar(id_tecnico, nome, especialidade, telefone, email):
            print("Técnico atualizado com sucesso!")
        else:
            print("Não foi possível atualizar o técnico.")

    def _excluir_tecnico(self):
        id_tecnico = ler_inteiro("ID do técnico que deseja excluir: ")
        if not confirmar("Tem certeza? Esta ação não pode ser desfeita (s/n): "):
            print("Operação cancelada.")
            return
        if self.repo_tecnico.excluir(id_tecnico):
            print("Técnico excluído com sucesso!")
        else:
            print("Técnico não encontrado.")

    # ---------------- SOLICITANTES ----------------
    def _menu_solicitantes(self):
        while True:
            print("\n--------------- GERENCIAR SOLICITANTES ---------------")
            print("1 - Cadastrar solicitante")
            print("2 - Listar solicitantes")
            print("3 - Buscar solicitante por ID")
            print("4 - Atualizar solicitante")
            print("5 - Excluir solicitante")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    nome = ler_texto("Nome do solicitante: ")
                    setor = ler_texto("Setor/Departamento: ", obrigatorio=False)
                    telefone = ler_texto("Telefone: ", obrigatorio=False)
                    email = ler_texto("E-mail: ", obrigatorio=False)
                    id_novo = self.repo_solicitante.criar(nome, setor, telefone, email)
                    print(f"Solicitante cadastrado com sucesso! (ID {id_novo})")
                elif opcao == "2":
                    self._listar(self.repo_solicitante.listar(), "solicitante")
                elif opcao == "3":
                    id_solicitante = ler_inteiro("ID do solicitante: ")
                    solicitante = self.repo_solicitante.buscar_por_id(id_solicitante)
                    print(solicitante if solicitante else "Solicitante não encontrado.")
                elif opcao == "4":
                    self._atualizar_solicitante()
                elif opcao == "5":
                    self._excluir_solicitante()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida.")
            except pymysql.err.IntegrityError as erro:
                print(f"Não foi possível concluir a operação (restrição de integridade): {erro}")
            except Exception as erro:
                print(f"Ocorreu um erro inesperado: {erro}")
            pausar()

    def _atualizar_solicitante(self):
        id_solicitante = ler_inteiro("ID do solicitante que deseja atualizar: ")
        solicitante = self.repo_solicitante.buscar_por_id(id_solicitante)
        if not solicitante:
            print("Solicitante não encontrado.")
            return
        print(f"Dados atuais: {solicitante}")
        nome = ler_texto(
            f"Novo nome [{solicitante.nome}] (ENTER mantém): ", obrigatorio=False
        ) or solicitante.nome
        setor = ler_texto(
            f"Novo setor [{solicitante.setor}] (ENTER mantém): ", obrigatorio=False
        ) or solicitante.setor
        telefone = ler_texto(
            f"Novo telefone [{solicitante.telefone}] (ENTER mantém): ", obrigatorio=False
        ) or solicitante.telefone
        email = ler_texto(
            f"Novo e-mail [{solicitante.email}] (ENTER mantém): ", obrigatorio=False
        ) or solicitante.email
        if self.repo_solicitante.atualizar(id_solicitante, nome, setor, telefone, email):
            print("Solicitante atualizado com sucesso!")
        else:
            print("Não foi possível atualizar o solicitante.")

    def _excluir_solicitante(self):
        id_solicitante = ler_inteiro("ID do solicitante que deseja excluir: ")
        if not confirmar("Tem certeza? Esta ação não pode ser desfeita (s/n): "):
            print("Operação cancelada.")
            return
        if self.repo_solicitante.excluir(id_solicitante):
            print("Solicitante excluído com sucesso!")
        else:
            print("Solicitante não encontrado.")

    # ---------------- CHAMADOS ----------------
    def _menu_chamados(self):
        while True:
            print("\n----------------- GERENCIAR CHAMADOS -----------------")
            print("1 - Abrir novo chamado")
            print("2 - Listar todos os chamados")
            print("3 - Listar chamados por status")
            print("4 - Buscar chamado por ID")
            print("5 - Atualizar chamado")
            print("6 - Fechar chamado")
            print("7 - Excluir chamado")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self._abrir_chamado()
                elif opcao == "2":
                    self._listar(self.repo_chamado.listar(), "chamado", detalhado=True)
                elif opcao == "3":
                    status = ler_opcao_valida("Status", ["Aberto", "Em Andamento", "Fechado"])
                    self._listar(self.repo_chamado.listar_por_status(status), "chamado", detalhado=True)
                elif opcao == "4":
                    id_chamado = ler_inteiro("ID do chamado: ")
                    chamado = self.repo_chamado.buscar_por_id(id_chamado)
                    print(chamado if chamado else "Chamado não encontrado.")
                elif opcao == "5":
                    self._atualizar_chamado()
                elif opcao == "6":
                    self._fechar_chamado()
                elif opcao == "7":
                    self._excluir_chamado()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida.")
            except pymysql.err.IntegrityError as erro:
                print(f"Não foi possível concluir a operação (restrição de integridade): {erro}")
            except Exception as erro:
                print(f"Ocorreu um erro inesperado: {erro}")
            pausar()

    def _listar(self, registros, nome_entidade, detalhado=False):
        if not registros:
            print(f"Nenhum(a) {nome_entidade} encontrado(a).")
            return
        print(f"\n{len(registros)} registro(s) encontrado(s):\n")
        for registro in registros:
            print(registro)
            if detalhado:
                print("-" * 56)

    def _escolher_categoria(self):
        categorias = self.repo_categoria.listar()
        print("\nCategorias disponíveis:")
        for categoria in categorias:
            print(f"  {categoria.id_categoria} - {categoria.nome}")
        return ler_inteiro("Informe o ID da categoria: ")

    def _escolher_solicitante(self):
        solicitantes = self.repo_solicitante.listar()
        print("\nSolicitantes cadastrados:")
        for solicitante in solicitantes:
            print(f"  {solicitante.id_solicitante} - {solicitante.nome} ({solicitante.setor})")
        return ler_inteiro("Informe o ID do solicitante: ")

    def _escolher_tecnico(self, obrigatorio=False):
        tecnicos = self.repo_tecnico.listar()
        print("\nTécnicos disponíveis:")
        for tecnico in tecnicos:
            print(f"  {tecnico.id_tecnico} - {tecnico.nome} ({tecnico.especialidade})")
        if not obrigatorio:
            print("  (deixe em branco para não atribuir nenhum técnico agora)")
        return ler_inteiro("Informe o ID do técnico: ", permitir_vazio=not obrigatorio)

    def _abrir_chamado(self, permitir_atribuir_tecnico=True):
        print("\n--- Abertura de novo chamado ---")
        titulo = ler_texto("Título do chamado: ")
        descricao = ler_texto("Descrição do problema: ")
        prioridade = ler_opcao_valida("Prioridade", ["Baixa", "Média", "Alta"])
        id_categoria = self._escolher_categoria()
        id_solicitante = self._escolher_solicitante()
        if permitir_atribuir_tecnico:
            # A atribuição de técnico é uma ação de controle/gestão, feita
            # apenas por Administradores; usuários comuns abrem o chamado
            # sem técnico definido (ele é atribuído depois, na atualização).
            id_tecnico = self._escolher_tecnico(obrigatorio=False)
        else:
            id_tecnico = None
        id_novo = self.repo_chamado.criar(
            titulo, descricao, prioridade, id_categoria, id_solicitante, id_tecnico
        )
        print(f"\nChamado aberto com sucesso! (ID {id_novo})")

    def _atualizar_chamado(self):
        id_chamado = ler_inteiro("ID do chamado que deseja atualizar: ")
        chamado = self.repo_chamado.buscar_por_id(id_chamado)
        if not chamado:
            print("Chamado não encontrado.")
            return
        print(f"Dados atuais:\n{chamado}\n")
        titulo = ler_texto(f"Novo título [{chamado.titulo}] (ENTER mantém): ", obrigatorio=False) or chamado.titulo
        descricao = ler_texto(
            "Nova descrição (ENTER mantém): ", obrigatorio=False
        ) or chamado.descricao
        prioridade = ler_opcao_valida_ou_manter("Nova prioridade", ["Baixa", "Média", "Alta"], chamado.prioridade)
        novo_id_tecnico = self._escolher_tecnico(obrigatorio=False)
        id_tecnico = novo_id_tecnico if novo_id_tecnico is not None else chamado.id_tecnico
        if self.repo_chamado.atualizar(id_chamado, titulo, descricao, prioridade, id_tecnico):
            print("Chamado atualizado com sucesso!")
        else:
            print("Não foi possível atualizar o chamado.")

    def _fechar_chamado(self):
        id_chamado = ler_inteiro("ID do chamado que deseja fechar: ")
        chamado = self.repo_chamado.buscar_por_id(id_chamado)
        if not chamado:
            print("Chamado não encontrado.")
            return
        if chamado.status == "Fechado":
            print("Este chamado já está fechado.")
            return
        if self.repo_chamado.fechar_chamado(id_chamado):
            print("Chamado fechado com sucesso!")

    def _excluir_chamado(self):
        id_chamado = ler_inteiro("ID do chamado que deseja excluir: ")
        if not confirmar("Tem certeza? Esta ação não pode ser desfeita (s/n): "):
            print("Operação cancelada.")
            return
        if self.repo_chamado.excluir(id_chamado):
            print("Chamado excluído com sucesso!")
        else:
            print("Chamado não encontrado.")

    # ---------------- USUÁRIOS (somente Administrador) ----------------
    def _menu_usuarios(self):
        while True:
            print("\n----------------- GERENCIAR USUÁRIOS -----------------")
            print("1 - Cadastrar usuário")
            print("2 - Listar usuários")
            print("3 - Buscar usuário por ID")
            print("4 - Atualizar usuário")
            print("5 - Excluir usuário")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self._cadastrar_usuario()
                elif opcao == "2":
                    self._listar(self.repo_usuario.listar(), "usuário")
                elif opcao == "3":
                    id_usuario = ler_inteiro("ID do usuário: ")
                    usuario = self.repo_usuario.buscar_por_id(id_usuario)
                    print(usuario if usuario else "Usuário não encontrado.")
                elif opcao == "4":
                    self._atualizar_usuario()
                elif opcao == "5":
                    self._excluir_usuario()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida.")
            except pymysql.err.IntegrityError as erro:
                print(f"Não foi possível concluir a operação (restrição de integridade): {erro}")
            except Exception as erro:
                print(f"Ocorreu um erro inesperado: {erro}")
            pausar()

    def _cadastrar_usuario(self):
        nome_usuario = ler_texto("Nome de usuário (login): ")
        senha = ler_texto("Senha: ")
        tipo = ler_opcao_valida("Tipo de usuário", ["Usuário", "Administrador"])
        nome_completo = ler_texto("Nome completo: ", obrigatorio=False)
        id_novo = self.repo_usuario.criar(nome_usuario, senha, tipo, nome_completo)
        print(f"Usuário cadastrado com sucesso! (ID {id_novo})")

    def _atualizar_usuario(self):
        id_usuario = ler_inteiro("ID do usuário que deseja atualizar: ")
        usuario = self.repo_usuario.buscar_por_id(id_usuario)
        if not usuario:
            print("Usuário não encontrado.")
            return
        print(f"Dados atuais: {usuario}")
        tipo = ler_opcao_valida_ou_manter("Novo tipo", ["Usuário", "Administrador"], usuario.tipo_usuario)
        if id_usuario == self.usuario_logado.id_usuario and tipo != "Administrador":
            print("Você não pode remover seu próprio acesso de Administrador enquanto estiver logado.")
            return
        nome_completo = ler_texto(
            f"Novo nome completo [{usuario.nome_completo}] (ENTER mantém): ", obrigatorio=False
        ) or usuario.nome_completo
        nova_senha = ler_texto("Nova senha (ENTER para manter a senha atual): ", obrigatorio=False)
        if self.repo_usuario.atualizar(id_usuario, tipo, nome_completo, nova_senha or None):
            print("Usuário atualizado com sucesso!")
        else:
            print("Não foi possível atualizar o usuário.")

    def _excluir_usuario(self):
        id_usuario = ler_inteiro("ID do usuário que deseja excluir: ")
        if id_usuario == self.usuario_logado.id_usuario:
            print("Você não pode excluir o usuário com o qual está logado.")
            return
        if not confirmar("Tem certeza? Esta ação não pode ser desfeita (s/n): "):
            print("Operação cancelada.")
            return
        if self.repo_usuario.excluir(id_usuario):
            print("Usuário excluído com sucesso!")
        else:
            print("Usuário não encontrado.")
