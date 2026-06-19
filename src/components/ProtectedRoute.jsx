/**
 * Guarda de rotas (Route Guard).
 *
 * Sem autenticação → redireciona para /login.
 * Com apenasAdmin=true e usuário não-admin → redireciona para /chamados.
 */

import { Navigate, Outlet } from 'react-router-dom'
import { CircularProgress, Box } from '@mui/material'
import { useAuth } from '../context/AuthContext.jsx'

export default function ProtectedRoute({ apenasAdmin = false }) {
  const { usuario, carregando } = useAuth()

  // Aguarda o AuthContext restaurar a sessão do localStorage
  if (carregando) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    )
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  if (apenasAdmin && usuario.tipo_usuario !== 'Administrador') {
    return <Navigate to="/chamados" replace />
  }

  return <Outlet />
}
