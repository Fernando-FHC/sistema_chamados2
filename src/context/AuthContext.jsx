/**
 * Contexto de autenticação.
 *
 * Armazena o usuário logado e o token no localStorage do navegador,
 * e configura o cabeçalho Authorization da instância Axios para que
 * todas as requisições subsequentes já incluam o token.
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { api, apiAuth } from '../api/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(true)

  // Ao montar, tenta restaurar a sessão salva no localStorage
  useEffect(() => {
    const token       = localStorage.getItem('token')
    const usuarioJson = localStorage.getItem('usuario')
    if (token && usuarioJson) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setUsuario(JSON.parse(usuarioJson))
    }
    setCarregando(false)
  }, [])

  const login = (token, usuario) => {
    localStorage.setItem('token', token)
    localStorage.setItem('usuario', JSON.stringify(usuario))
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    setUsuario(usuario)
  }

  const logout = async () => {
    try { await apiAuth.logout() } catch {}
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
    delete api.defaults.headers.common['Authorization']
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, login, logout, carregando }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook para acessar o contexto de autenticação em qualquer componente
export const useAuth = () => useContext(AuthContext)
