import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material'

import { AuthProvider } from './context/AuthContext.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Layout from './components/Layout.jsx'

import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Chamados from './pages/Chamados.jsx'
import Categorias from './pages/Categorias.jsx'
import Tecnicos from './pages/Tecnicos.jsx'
import Solicitantes from './pages/Solicitantes.jsx'
import Usuarios from './pages/Usuarios.jsx'

const tema = createTheme({
  palette: {
    primary: { main: '#1565c0' },
    secondary: { main: '#f57c00' },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
})

export default function App() {
  return (
    <ThemeProvider theme={tema}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Rota pública: login */}
            <Route path="/login" element={<Login />} />

            {/* Rotas protegidas: qualquer usuário logado */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/" element={<Navigate to="/chamados" replace />} />
                <Route path="/chamados" element={<Chamados />} />

                {/* Rotas exclusivas para Administrador */}
                <Route element={<ProtectedRoute apenasAdmin />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/categorias" element={<Categorias />} />
                  <Route path="/tecnicos" element={<Tecnicos />} />
                  <Route path="/solicitantes" element={<Solicitantes />} />
                  <Route path="/usuarios" element={<Usuarios />} />
                </Route>
              </Route>
            </Route>

            {/* Qualquer rota inválida volta para a raiz */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
