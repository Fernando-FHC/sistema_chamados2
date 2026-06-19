/**
 * Página de Chamados.
 *
 * Administradores têm controle total: abrir, editar, fechar e excluir.
 * Usuários comuns só podem abrir novos chamados (sem atribuir técnico)
 * e visualizar a listagem — os botões de ação não aparecem para eles.
 */

import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, Typography, CircularProgress, Alert,
  Select, MenuItem, FormControl, InputLabel, FormHelperText, Chip,
  Tooltip, Divider,
} from '@mui/material'
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon,
  Lock as FecharIcon,
} from '@mui/icons-material'
import { apiChamados, apiCategorias, apiTecnicos, apiSolicitantes } from '../api/api.js'
import { useAuth } from '../context/AuthContext.jsx'

// ---- Esquema Zod ----

const schema = z.object({
  titulo:        z.string().min(1, 'Título é obrigatório').max(200),
  descricao:     z.string().min(1, 'Descrição é obrigatória'),
  prioridade:    z.enum(['Baixa', 'Média', 'Alta'], { required_error: 'Prioridade é obrigatória' }),
  id_categoria:  z.number({ invalid_type_error: 'Categoria é obrigatória' }).min(1),
  id_solicitante:z.number({ invalid_type_error: 'Solicitante é obrigatório' }).min(1),
  id_tecnico:    z.number().nullable().optional(),
})

// ---- Chips coloridos para status e prioridade ----

const corStatus = { Aberto: 'error', 'Em Andamento': 'warning', Fechado: 'success' }
const corPrior  = { Alta: 'error', Média: 'warning', Baixa: 'success' }

export default function Chamados() {
  const { usuario } = useAuth()
  const ehAdmin = usuario?.tipo_usuario === 'Administrador'

  const [chamados,     setChamados]     = useState([])
  const [categorias,   setCategorias]   = useState([])
  const [solicitantes, setSolicitantes] = useState([])
  const [tecnicos,     setTecnicos]     = useState([])
  const [carregando,   setCarregando]   = useState(true)
  const [filtroStatus, setFiltroStatus] = useState('')
  const [dialogAberto, setDialogAberto] = useState(false)
  const [editando,     setEditando]     = useState(null)  // null = novo, objeto = editar
  const [erroDialog,   setErroDialog]   = useState('')
  const [erroGeral,    setErroGeral]    = useState('')

  const { register, handleSubmit, reset, control, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { titulo: '', descricao: '', prioridade: 'Média',
                     id_categoria: '', id_solicitante: '', id_tecnico: null },
  })

  // ---- Carregamento ----

  const carregar = async () => {
    setErroGeral('')
    try {
      const [resCh, resCat, resSol, resTec] = await Promise.all([
        apiChamados.listar(filtroStatus || undefined),
        apiCategorias.listar(),
        apiSolicitantes.listar(),
        apiTecnicos.listar(),
      ])
      setChamados(resCh.data)
      setCategorias(resCat.data)
      setSolicitantes(resSol.data)
      setTecnicos(resTec.data)
    } catch {
      setErroGeral('Não foi possível carregar os dados.')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => { carregar() }, [filtroStatus])

  // ---- Abertura do dialog ----

  const abrirNovo = () => {
    setEditando(null)
    reset({ titulo: '', descricao: '', prioridade: 'Média',
            id_categoria: '', id_solicitante: '', id_tecnico: null })
    setErroDialog('')
    setDialogAberto(true)
  }

  const abrirEditar = (chamado) => {
    setEditando(chamado)
    reset({
      titulo:         chamado.titulo,
      descricao:      chamado.descricao,
      prioridade:     chamado.prioridade,
      id_categoria:   chamado.id_categoria,
      id_solicitante: chamado.id_solicitante,
      id_tecnico:     chamado.id_tecnico ?? null,
    })
    setErroDialog('')
    setDialogAberto(true)
  }

  const fecharDialog = () => setDialogAberto(false)

  // ---- Submit do formulário ----

  const onSubmit = async (dados) => {
    // Usuários comuns não podem atribuir técnico
    if (!ehAdmin) dados.id_tecnico = null
    try {
      if (editando) {
        await apiChamados.atualizar(editando.id_chamado, dados)
      } else {
        await apiChamados.criar(dados)
      }
      fecharDialog()
      carregar()
    } catch (e) {
      setErroDialog(e.response?.data?.erro ?? 'Erro ao salvar.')
    }
  }

  // ---- Ações de linha ----

  const fecharChamado = async (id) => {
    if (!window.confirm('Deseja fechar este chamado?')) return
    try {
      await apiChamados.fechar(id)
      carregar()
    } catch (e) {
      alert(e.response?.data?.erro ?? 'Erro ao fechar.')
    }
  }

  const excluir = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este chamado?')) return
    try {
      await apiChamados.excluir(id)
      carregar()
    } catch (e) {
      alert(e.response?.data?.erro ?? 'Erro ao excluir.')
    }
  }

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>

  return (
    <Box>
      {/* Cabeçalho da página */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap" gap={1}>
        <Typography variant="h5" fontWeight={700}>Chamados</Typography>
        <Box display="flex" gap={1} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Filtrar por status</InputLabel>
            <Select
              label="Filtrar por status"
              value={filtroStatus}
              onChange={(e) => setFiltroStatus(e.target.value)}
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="Aberto">Aberto</MenuItem>
              <MenuItem value="Em Andamento">Em Andamento</MenuItem>
              <MenuItem value="Fechado">Fechado</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<AddIcon />} onClick={abrirNovo}>
            Novo Chamado
          </Button>
        </Box>
      </Box>

      {erroGeral && <Alert severity="error" sx={{ mb: 2 }}>{erroGeral}</Alert>}

      {/* Tabela de chamados */}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'primary.main' }}>
            <TableRow>
              {['ID','Título','Categoria','Prioridade','Status','Técnico','Aberto em'].map(h => (
                <TableCell key={h} sx={{ color: 'white', fontWeight: 700 }}>{h}</TableCell>
              ))}
              {ehAdmin && <TableCell sx={{ color: 'white', fontWeight: 700 }} align="right">Ações</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {chamados.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                  Nenhum chamado encontrado.
                </TableCell>
              </TableRow>
            )}
            {chamados.map((c) => (
              <TableRow key={c.id_chamado} hover>
                <TableCell>{c.id_chamado}</TableCell>
                <TableCell sx={{ maxWidth: 200 }}>
                  <Typography variant="body2" noWrap title={c.titulo}>{c.titulo}</Typography>
                </TableCell>
                <TableCell>{c.nome_categoria}</TableCell>
                <TableCell>
                  <Chip label={c.prioridade} color={corPrior[c.prioridade]} size="small" />
                </TableCell>
                <TableCell>
                  <Chip label={c.status} color={corStatus[c.status]} size="small" />
                </TableCell>
                <TableCell>{c.nome_tecnico ?? '—'}</TableCell>
                <TableCell>{c.data_abertura}</TableCell>
                {ehAdmin && (
                  <TableCell align="right">
                    <Tooltip title="Editar">
                      <IconButton size="small" onClick={() => abrirEditar(c)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {c.status !== 'Fechado' && (
                      <Tooltip title="Fechar chamado">
                        <IconButton size="small" color="success" onClick={() => fecharChamado(c.id_chamado)}>
                          <FecharIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Excluir">
                      <IconButton size="small" color="error" onClick={() => excluir(c.id_chamado)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog de criação/edição */}
      <Dialog open={dialogAberto} onClose={fecharDialog} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{editando ? 'Editar Chamado' : 'Abrir Novo Chamado'}</DialogTitle>
          <Divider />
          <DialogContent>
            <TextField
              {...register('titulo')}
              label="Título *"
              fullWidth margin="normal"
              error={!!errors.titulo}
              helperText={errors.titulo?.message}
            />
            <TextField
              {...register('descricao')}
              label="Descrição *"
              fullWidth margin="normal"
              multiline rows={3}
              error={!!errors.descricao}
              helperText={errors.descricao?.message}
            />

            {/* Prioridade */}
            <FormControl fullWidth margin="normal" error={!!errors.prioridade}>
              <InputLabel>Prioridade *</InputLabel>
              <Controller
                name="prioridade"
                control={control}
                render={({ field }) => (
                  <Select {...field} label="Prioridade *">
                    <MenuItem value="Baixa">Baixa</MenuItem>
                    <MenuItem value="Média">Média</MenuItem>
                    <MenuItem value="Alta">Alta</MenuItem>
                  </Select>
                )}
              />
              <FormHelperText>{errors.prioridade?.message}</FormHelperText>
            </FormControl>

            {/* Categoria — bloqueada ao editar */}
            <FormControl fullWidth margin="normal" error={!!errors.id_categoria}
                         disabled={!!editando}>
              <InputLabel>Categoria *</InputLabel>
              <Controller
                name="id_categoria"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Categoria *"
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  >
                    {categorias.map((c) => (
                      <MenuItem key={c.id_categoria} value={c.id_categoria}>{c.nome}</MenuItem>
                    ))}
                  </Select>
                )}
              />
              <FormHelperText>
                {errors.id_categoria?.message ?? (editando ? 'A categoria não pode ser alterada.' : '')}
              </FormHelperText>
            </FormControl>

            {/* Solicitante — bloqueado ao editar */}
            <FormControl fullWidth margin="normal" error={!!errors.id_solicitante}
                         disabled={!!editando}>
              <InputLabel>Solicitante *</InputLabel>
              <Controller
                name="id_solicitante"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Solicitante *"
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  >
                    {solicitantes.map((s) => (
                      <MenuItem key={s.id_solicitante} value={s.id_solicitante}>{s.nome}</MenuItem>
                    ))}
                  </Select>
                )}
              />
              <FormHelperText>
                {errors.id_solicitante?.message ?? (editando ? 'O solicitante não pode ser alterado.' : '')}
              </FormHelperText>
            </FormControl>

            {/* Técnico (somente Admin) */}
            {ehAdmin && (
              <FormControl fullWidth margin="normal">
                <InputLabel>Técnico responsável</InputLabel>
                <Controller
                  name="id_tecnico"
                  control={control}
                  render={({ field }) => (
                    <Select
                      {...field}
                      label="Técnico responsável"
                      onChange={(e) =>
                        field.onChange(e.target.value === '' ? null : Number(e.target.value))
                      }
                      value={field.value ?? ''}
                    >
                      <MenuItem value=""><em>Sem técnico</em></MenuItem>
                      {tecnicos.map((t) => (
                        <MenuItem key={t.id_tecnico} value={t.id_tecnico}>{t.nome}</MenuItem>
                      ))}
                    </Select>
                  )}
                />
              </FormControl>
            )}

            {erroDialog && <Alert severity="error" sx={{ mt: 1 }}>{erroDialog}</Alert>}
          </DialogContent>
          <DialogActions>
            <Button onClick={fecharDialog}>Cancelar</Button>
            <Button type="submit" variant="contained">
              {editando ? 'Salvar' : 'Abrir Chamado'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  )
}
