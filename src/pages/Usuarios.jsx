import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, Typography, CircularProgress, Alert,
  Divider, Tooltip, Select, MenuItem, FormControl, InputLabel,
  FormHelperText, Chip,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { apiUsuarios } from '../api/api.js'
import { useAuth } from '../context/AuthContext.jsx'

// Ao criar: senha obrigatória. Ao editar: senha opcional (em branco = mantém).
const schemaCriar = z.object({
  nome_usuario:  z.string().min(1, 'Login é obrigatório').max(50),
  senha:         z.string().min(4, 'Senha deve ter ao menos 4 caracteres'),
  tipo_usuario:  z.enum(['Usuário', 'Administrador']),
  nome_completo: z.string().optional(),
})

const schemaEditar = z.object({
  senha:         z.string().min(4, 'Mínimo 4 caracteres').optional().or(z.literal('')),
  tipo_usuario:  z.enum(['Usuário', 'Administrador']),
  nome_completo: z.string().optional(),
})

const VAZIO = { nome_usuario: '', senha: '', tipo_usuario: 'Usuário', nome_completo: '' }

export default function Usuarios() {
  const { usuario: usuarioLogado } = useAuth()

  const [usuarios,     setUsuarios]     = useState([])
  const [carregando,   setCarregando]   = useState(true)
  const [dialogAberto, setDialogAberto] = useState(false)
  const [editando,     setEditando]     = useState(null)
  const [erroDialog,   setErroDialog]   = useState('')
  const [erroGeral,    setErroGeral]    = useState('')

  const schema = editando ? schemaEditar : schemaCriar

  const { register, handleSubmit, reset, control, formState: { errors } } = useForm({
    resolver: zodResolver(schema), defaultValues: VAZIO,
  })

  const carregar = async () => {
    try { const res = await apiUsuarios.listar(); setUsuarios(res.data) }
    catch { setErroGeral('Não foi possível carregar os usuários.') }
    finally { setCarregando(false) }
  }

  useEffect(() => { carregar() }, [])

  const abrirNovo = () => { setEditando(null); reset(VAZIO); setErroDialog(''); setDialogAberto(true) }
  const abrirEditar = (u) => {
    setEditando(u)
    reset({ senha: '', tipo_usuario: u.tipo_usuario, nome_completo: u.nome_completo })
    setErroDialog(''); setDialogAberto(true)
  }

  const onSubmit = async (dados) => {
    try {
      if (editando) {
        // Passa senha apenas se preenchida
        const payload = { tipo_usuario: dados.tipo_usuario, nome_completo: dados.nome_completo }
        if (dados.senha) payload.senha = dados.senha
        await apiUsuarios.atualizar(editando.id_usuario, payload)
      } else {
        await apiUsuarios.criar(dados)
      }
      setDialogAberto(false); carregar()
    } catch (e) {
      setErroDialog(e.response?.data?.erro ?? 'Erro ao salvar.')
    }
  }

  const excluir = async (id) => {
    if (id === usuarioLogado?.id_usuario) {
      alert('Você não pode excluir o usuário com o qual está logado.'); return
    }
    if (!window.confirm('Excluir este usuário?')) return
    try { await apiUsuarios.excluir(id); carregar() }
    catch (e) { alert(e.response?.data?.erro ?? 'Erro ao excluir.') }
  }

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight={700}>Usuários do Sistema</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={abrirNovo}>Novo Usuário</Button>
      </Box>

      {erroGeral && <Alert severity="error" sx={{ mb: 2 }}>{erroGeral}</Alert>}

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'primary.main' }}>
            <TableRow>
              {['ID', 'Login', 'Nome Completo', 'Tipo', 'Ações'].map((h, i) => (
                <TableCell key={h} align={i === 4 ? 'right' : 'left'}
                           sx={{ color: 'white', fontWeight: 700 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {usuarios.length === 0 && (
              <TableRow><TableCell colSpan={5} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                Nenhum usuário cadastrado.
              </TableCell></TableRow>
            )}
            {usuarios.map((u) => (
              <TableRow key={u.id_usuario} hover
                sx={u.id_usuario === usuarioLogado?.id_usuario ? { bgcolor: 'primary.50' } : {}}>
                <TableCell>{u.id_usuario}</TableCell>
                <TableCell><b>{u.nome_usuario}</b></TableCell>
                <TableCell>{u.nome_completo}</TableCell>
                <TableCell>
                  <Chip
                    label={u.tipo_usuario}
                    color={u.tipo_usuario === 'Administrador' ? 'primary' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton size="small" onClick={() => abrirEditar(u)}><EditIcon fontSize="small" /></IconButton>
                  </Tooltip>
                  <Tooltip title={u.id_usuario === usuarioLogado?.id_usuario
                    ? 'Não é possível excluir o usuário logado' : 'Excluir'}>
                    <span>
                      <IconButton size="small" color="error"
                        disabled={u.id_usuario === usuarioLogado?.id_usuario}
                        onClick={() => excluir(u.id_usuario)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </span>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogAberto} onClose={() => setDialogAberto(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{editando ? `Editar: ${editando.nome_usuario}` : 'Novo Usuário'}</DialogTitle>
          <Divider />
          <DialogContent>
            {/* Login — só exibido ao criar */}
            {!editando && (
              <TextField {...register('nome_usuario')} label="Login *" fullWidth margin="normal"
                error={!!errors.nome_usuario} helperText={errors.nome_usuario?.message} />
            )}

            <TextField
              {...register('senha')}
              label={editando ? 'Nova senha (em branco mantém a atual)' : 'Senha *'}
              type="password" fullWidth margin="normal"
              error={!!errors.senha} helperText={errors.senha?.message}
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Tipo de usuário</InputLabel>
              <Controller
                name="tipo_usuario"
                control={control}
                render={({ field }) => (
                  <Select {...field} label="Tipo de usuário">
                    <MenuItem value="Usuário">Usuário</MenuItem>
                    <MenuItem value="Administrador">Administrador</MenuItem>
                  </Select>
                )}
              />
            </FormControl>

            <TextField {...register('nome_completo')} label="Nome completo" fullWidth margin="normal" />

            {erroDialog && <Alert severity="error" sx={{ mt: 1 }}>{erroDialog}</Alert>}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogAberto(false)}>Cancelar</Button>
            <Button type="submit" variant="contained">Salvar</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  )
}
