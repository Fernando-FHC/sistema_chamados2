/**
 * Layout principal da aplicação (pós-login).
 *
 * Usa o componente Drawer do MUI para a barra lateral e o AppBar
 * para o cabeçalho. Os itens do menu mudam de acordo com o perfil
 * do usuário logado (Administrador vê todas as páginas; Usuário só
 * vê Chamados).
 */

import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box, Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, AppBar, Toolbar, Typography, IconButton,
  Divider, Tooltip, Avatar,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  ConfirmationNumber as ChamadosIcon,
  Category as CategoriasIcon,
  Engineering as TecnicosIcon,
  Groups as SolicitantesIcon,
  ManageAccounts as UsuariosIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'
import { useAuth } from '../context/AuthContext.jsx'

const LARGURA_DRAWER = 230

export default function Layout() {
  const { usuario, logout } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const [aberto, setAberto] = useState(true)

  const ehAdmin = usuario?.tipo_usuario === 'Administrador'

  const itensMenu = [
    ...(ehAdmin ? [{ texto: 'Dashboard',    icone: <DashboardIcon />,   rota: '/dashboard' }] : []),
    { texto: 'Chamados',      icone: <ChamadosIcon />,    rota: '/chamados' },
    ...(ehAdmin ? [
      { texto: 'Categorias',  icone: <CategoriasIcon />,  rota: '/categorias' },
      { texto: 'Técnicos',    icone: <TecnicosIcon />,    rota: '/tecnicos' },
      { texto: 'Solicitantes',icone: <SolicitantesIcon />,rota: '/solicitantes' },
      { texto: 'Usuários',    icone: <UsuariosIcon />,    rota: '/usuarios' },
    ] : []),
  ]

  const conteudoDrawer = (
    <Box>
      <Toolbar sx={{ bgcolor: 'primary.main' }}>
        <Typography variant="subtitle1" color="white" fontWeight={700} noWrap>
          Sistema de Chamados
        </Typography>
      </Toolbar>
      <Divider />

      <List dense>
        {itensMenu.map(({ texto, icone, rota }) => (
          <ListItem key={rota} disablePadding>
            <ListItemButton
              selected={location.pathname === rota}
              onClick={() => navigate(rota)}
              sx={{ '&.Mui-selected': { bgcolor: 'primary.light', color: 'primary.contrastText' } }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: 'inherit' }}>{icone}</ListItemIcon>
              <ListItemText primary={texto} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />
      <List dense>
        <ListItem disablePadding>
          <ListItemButton onClick={logout}>
            <ListItemIcon sx={{ minWidth: 36 }}><LogoutIcon color="error" /></ListItemIcon>
            <ListItemText primary="Sair" primaryTypographyProps={{ color: 'error' }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Cabeçalho */}
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={() => setAberto(!aberto)} sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Sistema de Abertura, Controle e Fechamento de Chamados
          </Typography>
          <Tooltip title={`${usuario?.nome_completo} (${usuario?.tipo_usuario})`}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 34, height: 34, fontSize: 14, cursor: 'default' }}>
              {usuario?.nome_completo?.[0]?.toUpperCase() ?? 'U'}
            </Avatar>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Barra lateral */}
      <Drawer
        variant="persistent"
        open={aberto}
        sx={{
          width: aberto ? LARGURA_DRAWER : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: LARGURA_DRAWER, boxSizing: 'border-box' },
        }}
      >
        {conteudoDrawer}
      </Drawer>

      {/* Conteúdo principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: '64px',
          ml: aberto ? `${LARGURA_DRAWER}px` : 0,
          transition: 'margin 0.2s',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
