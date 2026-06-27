/**
 * Dashboard (somente Administrador).
 */
import { useState, useEffect } from 'react'
import {
  Grid, Card, CardContent, Typography, Box, CircularProgress, Alert,
  List, ListItem, ListItemText, ListItemIcon, Chip, Divider,
} from '@mui/material'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  ConfirmationNumber, Category, Engineering, Groups, Person,
  Event as EventIcon,
} from '@mui/icons-material'
import { apiDashboard } from '../api/api.js'

const COR_STATUS     = { Aberto: '#f44336', 'Em Andamento': '#ff9800', Fechado: '#4caf50' }
const COR_PRIORIDADE = { Alta: '#f44336', Média: '#ff9800', Baixa: '#4caf50' }

// ── Card de total ────────────────────────────────────────────────────
function CardTotal({ label, valor, cor, icone }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={0.5}>
          <Box sx={{ color: cor }}>{icone}</Box>
          <Typography variant="body2" color="text.secondary">{label}</Typography>
        </Box>
        <Typography variant="h3" fontWeight={700} sx={{ color: cor }}>
          {valor}
        </Typography>
      </CardContent>
    </Card>
  )
}

// ── Widget de feriados (BrasilAPI) ───────────────────────────────────
function WidgetFeriados() {
  const [feriados, setFeriados]     = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro]             = useState('')

  useEffect(() => {
    const ano = new Date().getFullYear()
    // BrasilAPI — feriados nacionais (API pública, sem autenticação)
    fetch(`https://brasilapi.com.br/api/feriados/v1/${ano}`)
      .then((res) => {
        if (!res.ok) throw new Error('Falha ao buscar feriados')
        return res.json()
      })
      .then((data) => {
        // Filtra apenas os que ainda não passaram e pega os próximos 6
        const hoje = new Date()
        hoje.setHours(0, 0, 0, 0)
        const proximos = data
          .filter((f) => new Date(f.date + 'T00:00:00') >= hoje)
          .slice(0, 6)
        setFeriados(proximos)
      })
      .catch(() => setErro('Não foi possível carregar os feriados.'))
      .finally(() => setCarregando(false))
  }, [])

  const formatarData = (dateStr) => {
    // dateStr vem como "YYYY-MM-DD"
    const [ano, mes, dia] = dateStr.split('-')
    return `${dia}/${mes}`
  }

  const diasRestantes = (dateStr) => {
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0)
    const feriado = new Date(dateStr + 'T00:00:00')
    const diff = Math.round((feriado - hoje) / (1000 * 60 * 60 * 24))
    if (diff === 0) return 'Hoje!'
    if (diff === 1) return 'Amanhã'
    return `em ${diff} dias`
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <EventIcon color="primary" />
          <Typography variant="subtitle1" fontWeight={600}>
            Próximos Feriados Nacionais
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary" display="block" mb={1}>
          via BrasilAPI — brasilapi.com.br
        </Typography>
        <Divider sx={{ mb: 1 }} />

        {carregando && <CircularProgress size={24} />}
        {erro && <Alert severity="warning" sx={{ fontSize: 12 }}>{erro}</Alert>}

        {!carregando && !erro && feriados.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            Nenhum feriado próximo este ano.
          </Typography>
        )}

        <List dense disablePadding>
          {feriados.map((f) => {
            const restantes = diasRestantes(f.date)
            const urgente = restantes === 'Hoje!' || restantes === 'Amanhã'
            return (
              <ListItem key={f.date} disablePadding sx={{ mb: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <Typography variant="body2" fontWeight={700} color="primary">
                    {formatarData(f.date)}
                  </Typography>
                </ListItemIcon>
                <ListItemText
                  primary={f.name}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
                <Chip
                  label={restantes}
                  size="small"
                  color={urgente ? 'error' : 'default'}
                  sx={{ fontSize: 10, height: 20 }}
                />
              </ListItem>
            )
          })}
        </List>
      </CardContent>
    </Card>
  )
}

// ── Dashboard principal ──────────────────────────────────────────────
export default function Dashboard() {
  const [dados, setDados]           = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro]             = useState('')

  useEffect(() => {
    apiDashboard()
      .then((res) => setDados(res.data))
      .catch(() => setErro('Não foi possível carregar o dashboard.'))
      .finally(() => setCarregando(false))
  }, [])

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>
  if (erro)       return <Alert severity="error">{erro}</Alert>

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>Dashboard</Typography>

      {/* Cards de totais */}
      <Grid container spacing={2} mb={3}>
        {[
          { label: 'Chamados',    valor: dados.totais.chamados,    cor: '#1565c0', icone: <ConfirmationNumber /> },
          { label: 'Categorias',  valor: dados.totais.categorias,  cor: '#2e7d32', icone: <Category /> },
          { label: 'Técnicos',    valor: dados.totais.tecnicos,    cor: '#e65100', icone: <Engineering /> },
          { label: 'Solicitantes',valor: dados.totais.solicitantes,cor: '#6a1b9a', icone: <Groups /> },
          { label: 'Usuários',    valor: dados.totais.usuarios,    cor: '#00695c', icone: <Person /> },
        ].map((item) => (
          <Grid item xs={6} sm={4} md={2.4} key={item.label}>
            <CardTotal {...item} />
          </Grid>
        ))}
      </Grid>

      {/* Gráficos + Feriados */}
      <Grid container spacing={2}>

        {/* Pie: por status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Chamados por Status
              </Typography>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={dados.por_status}
                    dataKey="total"
                    nameKey="status"
                    cx="50%" cy="50%"
                    outerRadius={80}
                    labelLine={false}
                    label={({ status, percent }) =>
                      percent > 0 ? `${status} ${(percent * 100).toFixed(0)}%` : ''
                    }
                  >
                    {dados.por_status.map((entry) => (
                      <Cell key={entry.status} fill={COR_STATUS[entry.status] ?? '#8884d8'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Bar: por categoria */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Chamados por Categoria
              </Typography>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={dados.por_categoria} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="categoria" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="total" name="Total" fill="#1565c0" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Bar: por prioridade */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Chamados por Prioridade
              </Typography>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={dados.por_prioridade} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="prioridade" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="total" name="Total" radius={[4, 4, 0, 0]}>
                    {dados.por_prioridade.map((entry) => (
                      <Cell key={entry.prioridade} fill={COR_PRIORIDADE[entry.prioridade] ?? '#8884d8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Widget de feriados — BrasilAPI */}
        <Grid item xs={12} md={4}>
          <WidgetFeriados />
        </Grid>

      </Grid>
    </Box>
  )
}
