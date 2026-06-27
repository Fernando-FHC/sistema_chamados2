# -*- coding: utf-8 -*-
"""
Backend Flask do Sistema de Chamados.

Expõe uma API REST consumida pelo frontend React. A autenticação é feita
por token: ao fazer login, o servidor gera um token aleatório e o armazena
em memória. Cada requisição subsequente deve incluir o token no cabeçalho
"Authorization: Bearer <token>".
"""

import secrets
import sys
import os

from flask import Flask, request, jsonify, g
from functools import wraps

sys.path.insert(0, os.path.dirname(__file__))

from database import Conexao
from repositorios import (
    CategoriaRepositorio,
    TecnicoRepositorio,
    SolicitanteRepositorio,
    ChamadoRepositorio,
    UsuarioRepositorio,
)

# --------------------------------------------------------------------
# Inicialização
# --------------------------------------------------------------------

app = Flask(__name__)

_origens_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _origens_env.split(",") if o.strip()]


def _origem_permitida(origem: str) -> bool:
    return not ALLOWED_ORIGINS or origem in ALLOWED_ORIGINS


@app.after_request
def adicionar_cors(response):
    origem = request.headers.get("Origin", "")
    if _origem_permitida(origem):
        response.headers["Access-Control-Allow-Origin"]  = origem
        response.headers["Access-Control-Allow-Headers"] = (
            "Authorization, Content-Type, Accept"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
    return response


@app.route("/api/<path:caminho>", methods=["OPTIONS"])
def preflight(caminho):
    return "", 204


# Dicionário de sessões ativas: token -> id_usuario
sessoes: dict[str, int] = {}

# Conexão única com o banco — repositórios reconectam automaticamente
# via _cursor() se a conexão cair por inatividade
_conexao_bd = Conexao()
_conexao_bd.conectar()
_conexao_bd.criar_tabelas()
_conexao_bd.popular_dados_iniciais()

# Passa _conexao_bd (objeto Conexao) junto com a conexão pymysql,
# para que _cursor() possa chamar _conexao_bd.reconectar() quando necessário
_conn = _conexao_bd.conexao

repo_categoria   = CategoriaRepositorio(_conn, _conexao_bd)
repo_tecnico     = TecnicoRepositorio(_conn, _conexao_bd)
repo_solicitante = SolicitanteRepositorio(_conn, _conexao_bd)
repo_chamado     = ChamadoRepositorio(_conn, _conexao_bd)
repo_usuario     = UsuarioRepositorio(_conn, _conexao_bd)

# --------------------------------------------------------------------
# Helpers de autenticação
# --------------------------------------------------------------------

def _usuario_do_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    id_usuario = sessoes.get(token)
    if id_usuario is None:
        return None
    return repo_usuario.buscar_por_id(id_usuario)


def requer_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        usuario = _usuario_do_token()
        if usuario is None:
            return jsonify({"erro": "Não autenticado."}), 401
        g.usuario = usuario
        return f(*args, **kwargs)
    return wrapper


def requer_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        usuario = _usuario_do_token()
        if usuario is None:
            return jsonify({"erro": "Não autenticado."}), 401
        if not usuario.eh_administrador:
            return jsonify({"erro": "Acesso restrito a administradores."}), 403
        g.usuario = usuario
        return f(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------
# Serializadores
# --------------------------------------------------------------------

def s_categoria(c):
    return {"id_categoria": c.id_categoria, "nome": c.nome, "descricao": c.descricao or ""}

def s_tecnico(t):
    return {"id_tecnico": t.id_tecnico, "nome": t.nome, "especialidade": t.especialidade or "",
            "telefone": t.telefone or "", "email": t.email or ""}

def s_solicitante(s):
    return {"id_solicitante": s.id_solicitante, "nome": s.nome, "setor": s.setor or "",
            "telefone": s.telefone or "", "email": s.email or ""}

def s_chamado(c):
    return {
        "id_chamado": c.id_chamado, "titulo": c.titulo, "descricao": c.descricao or "",
        "prioridade": c.prioridade, "status": c.status,
        "data_abertura": c.data_abertura, "data_fechamento": c.data_fechamento,
        "id_categoria": c.id_categoria, "id_solicitante": c.id_solicitante,
        "id_tecnico": c.id_tecnico,
        "nome_categoria": c.nome_categoria,
        "nome_solicitante": c.nome_solicitante,
        "nome_tecnico": c.nome_tecnico,
    }

def s_usuario(u):
    return {"id_usuario": u.id_usuario, "nome_usuario": u.nome_usuario,
            "tipo_usuario": u.tipo_usuario, "nome_completo": u.nome_completo or ""}

# --------------------------------------------------------------------
# Rotas: Autenticação
# --------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    dados = request.get_json() or {}
    nome_usuario = dados.get("nome_usuario", "").strip()
    senha = dados.get("senha", "")
    if not nome_usuario or not senha:
        return jsonify({"erro": "Informe usuário e senha."}), 400
    usuario = repo_usuario.autenticar(nome_usuario, senha)
    if usuario is None:
        return jsonify({"erro": "Usuário ou senha inválidos."}), 401
    token = secrets.token_hex(32)
    sessoes[token] = usuario.id_usuario
    return jsonify({"token": token, "usuario": s_usuario(usuario)})


@app.route("/api/logout", methods=["POST"])
@requer_login
def logout():
    token = request.headers["Authorization"][7:]
    sessoes.pop(token, None)
    return jsonify({"mensagem": "Sessão encerrada."})


@app.route("/api/me", methods=["GET"])
@requer_login
def me():
    return jsonify(s_usuario(g.usuario))

# --------------------------------------------------------------------
# Rotas: Categorias
# --------------------------------------------------------------------

@app.route("/api/categorias", methods=["GET"])
@requer_login
def listar_categorias():
    return jsonify([s_categoria(c) for c in repo_categoria.listar()])


@app.route("/api/categorias", methods=["POST"])
@requer_admin
def criar_categoria():
    dados = request.get_json() or {}
    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        id_novo = repo_categoria.criar(nome, descricao)
        return jsonify(s_categoria(repo_categoria.buscar_por_id(id_novo))), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/categorias/<int:id>", methods=["PUT"])
@requer_admin
def atualizar_categoria(id):
    dados = request.get_json() or {}
    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        if repo_categoria.atualizar(id, nome, descricao):
            return jsonify(s_categoria(repo_categoria.buscar_por_id(id)))
        return jsonify({"erro": "Categoria não encontrada."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/categorias/<int:id>", methods=["DELETE"])
@requer_admin
def excluir_categoria(id):
    try:
        if repo_categoria.excluir(id):
            return jsonify({"mensagem": "Excluído com sucesso."})
        return jsonify({"erro": "Categoria não encontrada."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# --------------------------------------------------------------------
# Rotas: Técnicos
# --------------------------------------------------------------------

@app.route("/api/tecnicos", methods=["GET"])
@requer_login
def listar_tecnicos():
    return jsonify([s_tecnico(t) for t in repo_tecnico.listar()])


@app.route("/api/tecnicos", methods=["POST"])
@requer_admin
def criar_tecnico():
    d = request.get_json() or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        id_novo = repo_tecnico.criar(nome, d.get("especialidade",""), d.get("telefone",""), d.get("email",""))
        return jsonify(s_tecnico(repo_tecnico.buscar_por_id(id_novo))), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/tecnicos/<int:id>", methods=["PUT"])
@requer_admin
def atualizar_tecnico(id):
    d = request.get_json() or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        if repo_tecnico.atualizar(id, nome, d.get("especialidade",""), d.get("telefone",""), d.get("email","")):
            return jsonify(s_tecnico(repo_tecnico.buscar_por_id(id)))
        return jsonify({"erro": "Técnico não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/tecnicos/<int:id>", methods=["DELETE"])
@requer_admin
def excluir_tecnico(id):
    try:
        if repo_tecnico.excluir(id):
            return jsonify({"mensagem": "Excluído com sucesso."})
        return jsonify({"erro": "Técnico não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# --------------------------------------------------------------------
# Rotas: Solicitantes
# --------------------------------------------------------------------

@app.route("/api/solicitantes", methods=["GET"])
@requer_login
def listar_solicitantes():
    return jsonify([s_solicitante(s) for s in repo_solicitante.listar()])


@app.route("/api/solicitantes", methods=["POST"])
@requer_admin
def criar_solicitante():
    d = request.get_json() or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        id_novo = repo_solicitante.criar(nome, d.get("setor",""), d.get("telefone",""), d.get("email",""))
        return jsonify(s_solicitante(repo_solicitante.buscar_por_id(id_novo))), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/solicitantes/<int:id>", methods=["PUT"])
@requer_admin
def atualizar_solicitante(id):
    d = request.get_json() or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório."}), 400
    try:
        if repo_solicitante.atualizar(id, nome, d.get("setor",""), d.get("telefone",""), d.get("email","")):
            return jsonify(s_solicitante(repo_solicitante.buscar_por_id(id)))
        return jsonify({"erro": "Solicitante não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/solicitantes/<int:id>", methods=["DELETE"])
@requer_admin
def excluir_solicitante(id):
    try:
        if repo_solicitante.excluir(id):
            return jsonify({"mensagem": "Excluído com sucesso."})
        return jsonify({"erro": "Solicitante não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# --------------------------------------------------------------------
# Rotas: Chamados
# --------------------------------------------------------------------

@app.route("/api/chamados", methods=["GET"])
@requer_login
def listar_chamados():
    status = request.args.get("status")
    if status:
        chamados = repo_chamado.listar_por_status(status)
    else:
        chamados = repo_chamado.listar()
    return jsonify([s_chamado(c) for c in chamados])


@app.route("/api/chamados", methods=["POST"])
@requer_login
def criar_chamado():
    d = request.get_json() or {}
    titulo         = d.get("titulo", "").strip()
    descricao      = d.get("descricao", "").strip()
    prioridade     = d.get("prioridade", "Média")
    id_categoria   = d.get("id_categoria")
    id_solicitante = d.get("id_solicitante")
    id_tecnico     = d.get("id_tecnico")
    if not titulo or not descricao:
        return jsonify({"erro": "Título e descrição são obrigatórios."}), 400
    if not id_categoria or not id_solicitante:
        return jsonify({"erro": "Categoria e solicitante são obrigatórios."}), 400
    try:
        id_novo = repo_chamado.criar(titulo, descricao, prioridade,
                                     id_categoria, id_solicitante, id_tecnico)
        return jsonify(s_chamado(repo_chamado.buscar_por_id(id_novo))), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/chamados/<int:id>", methods=["PUT"])
@requer_admin
def atualizar_chamado(id):
    d = request.get_json() or {}
    titulo     = d.get("titulo", "").strip()
    descricao  = d.get("descricao", "").strip()
    prioridade = d.get("prioridade", "Média")
    id_tecnico = d.get("id_tecnico")
    if not titulo or not descricao:
        return jsonify({"erro": "Título e descrição são obrigatórios."}), 400
    try:
        if repo_chamado.atualizar(id, titulo, descricao, prioridade, id_tecnico):
            return jsonify(s_chamado(repo_chamado.buscar_por_id(id)))
        return jsonify({"erro": "Chamado não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/chamados/<int:id>/fechar", methods=["PATCH"])
@requer_admin
def fechar_chamado(id):
    chamado = repo_chamado.buscar_por_id(id)
    if not chamado:
        return jsonify({"erro": "Chamado não encontrado."}), 404
    if chamado.status == "Fechado":
        return jsonify({"erro": "Chamado já está fechado."}), 400
    repo_chamado.fechar_chamado(id)
    return jsonify(s_chamado(repo_chamado.buscar_por_id(id)))


@app.route("/api/chamados/<int:id>", methods=["DELETE"])
@requer_admin
def excluir_chamado(id):
    try:
        if repo_chamado.excluir(id):
            return jsonify({"mensagem": "Excluído com sucesso."})
        return jsonify({"erro": "Chamado não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# --------------------------------------------------------------------
# Rotas: Usuários
# --------------------------------------------------------------------

@app.route("/api/usuarios", methods=["GET"])
@requer_admin
def listar_usuarios():
    return jsonify([s_usuario(u) for u in repo_usuario.listar()])


@app.route("/api/usuarios", methods=["POST"])
@requer_admin
def criar_usuario():
    d = request.get_json() or {}
    nome_usuario  = d.get("nome_usuario", "").strip()
    senha         = d.get("senha", "")
    tipo_usuario  = d.get("tipo_usuario", "Usuário")
    nome_completo = d.get("nome_completo", "").strip()
    if not nome_usuario or not senha:
        return jsonify({"erro": "Usuário (login) e senha são obrigatórios."}), 400
    try:
        id_novo = repo_usuario.criar(nome_usuario, senha, tipo_usuario, nome_completo)
        return jsonify(s_usuario(repo_usuario.buscar_por_id(id_novo))), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/usuarios/<int:id>", methods=["PUT"])
@requer_admin
def atualizar_usuario(id):
    d = request.get_json() or {}
    tipo_usuario  = d.get("tipo_usuario", "Usuário")
    nome_completo = d.get("nome_completo", "").strip()
    nova_senha    = d.get("senha", "").strip() or None
    if id == g.usuario.id_usuario and tipo_usuario != "Administrador":
        return jsonify({"erro": "Você não pode remover seu próprio acesso de Administrador."}), 400
    try:
        if repo_usuario.atualizar(id, tipo_usuario, nome_completo, nova_senha):
            return jsonify(s_usuario(repo_usuario.buscar_por_id(id)))
        return jsonify({"erro": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
@requer_admin
def excluir_usuario(id):
    if id == g.usuario.id_usuario:
        return jsonify({"erro": "Você não pode excluir o usuário com o qual está logado."}), 400
    try:
        if repo_usuario.excluir(id):
            return jsonify({"mensagem": "Excluído com sucesso."})
        return jsonify({"erro": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# --------------------------------------------------------------------
# Rota: Dashboard
# Usa _cursor() via repo_chamado para garantir reconexão automática
# --------------------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
@requer_admin
def dashboard():
    # Usa _cursor() do repositório para aproveitar a reconexão automática
    cursor = repo_chamado._cursor()

    cursor.execute("SELECT status, COUNT(*) as total FROM chamados GROUP BY status")
    por_status = [{"status": r["status"], "total": r["total"]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT cat.nome AS categoria, COUNT(*) AS total
        FROM chamados c
        JOIN categorias cat ON c.id_categoria = cat.id_categoria
        GROUP BY cat.nome
    """)
    por_categoria = [{"categoria": r["categoria"], "total": r["total"]} for r in cursor.fetchall()]

    cursor.execute("SELECT prioridade, COUNT(*) as total FROM chamados GROUP BY prioridade")
    por_prioridade = [{"prioridade": r["prioridade"], "total": r["total"]} for r in cursor.fetchall()]

    totais = {}
    for tabela, chave in [("chamados","chamados"), ("categorias","categorias"),
                           ("tecnicos","tecnicos"), ("solicitantes","solicitantes"),
                           ("usuarios","usuarios")]:
        cursor.execute(f"SELECT COUNT(*) AS c FROM {tabela}")
        totais[chave] = cursor.fetchone()["c"]

    return jsonify({
        "por_status": por_status,
        "por_categoria": por_categoria,
        "por_prioridade": por_prioridade,
        "totais": totais,
    })


if __name__ == "__main__":
    print("Backend rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
