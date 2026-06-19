/**
 * Módulo de acesso à API REST do backend Flask.
 *
 * Usa uma instância compartilhada do Axios configurada com a URL base
 * do servidor. O token de autenticação é adicionado automaticamente
 * aos cabeçalhos quando o usuário está logado (via AuthContext).
 */

import axios from 'axios'

// Instância compartilhada do Axios. O AuthContext configura o cabeçalho
// Authorization nessa instância quando o usuário faz login.
//
// A URL base é lida da variável de ambiente VITE_API_URL (definida em
// ".env" localmente ou nas configurações do projeto no Vercel).
// Se a variável não estiver definida, usa o servidor local de desenvolvimento.
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
})

// ---- Autenticação ----

export const apiAuth = {
  login:  (dados)  => api.post('/login', dados),
  logout: ()       => api.post('/logout'),
  me:     ()       => api.get('/me'),
}

// ---- Categorias ----

export const apiCategorias = {
  listar:    ()           => api.get('/categorias'),
  criar:     (dados)      => api.post('/categorias', dados),
  atualizar: (id, dados)  => api.put(`/categorias/${id}`, dados),
  excluir:   (id)         => api.delete(`/categorias/${id}`),
}

// ---- Técnicos ----

export const apiTecnicos = {
  listar:    ()           => api.get('/tecnicos'),
  criar:     (dados)      => api.post('/tecnicos', dados),
  atualizar: (id, dados)  => api.put(`/tecnicos/${id}`, dados),
  excluir:   (id)         => api.delete(`/tecnicos/${id}`),
}

// ---- Solicitantes ----

export const apiSolicitantes = {
  listar:    ()           => api.get('/solicitantes'),
  criar:     (dados)      => api.post('/solicitantes', dados),
  atualizar: (id, dados)  => api.put(`/solicitantes/${id}`, dados),
  excluir:   (id)         => api.delete(`/solicitantes/${id}`),
}

// ---- Chamados ----

export const apiChamados = {
  listar:    (status)     => api.get('/chamados', { params: status ? { status } : {} }),
  criar:     (dados)      => api.post('/chamados', dados),
  atualizar: (id, dados)  => api.put(`/chamados/${id}`, dados),
  fechar:    (id)         => api.patch(`/chamados/${id}/fechar`),
  excluir:   (id)         => api.delete(`/chamados/${id}`),
}

// ---- Usuários ----

export const apiUsuarios = {
  listar:    ()           => api.get('/usuarios'),
  criar:     (dados)      => api.post('/usuarios', dados),
  atualizar: (id, dados)  => api.put(`/usuarios/${id}`, dados),
  excluir:   (id)         => api.delete(`/usuarios/${id}`),
}

// ---- Dashboard ----

export const apiDashboard = () => api.get('/dashboard')
