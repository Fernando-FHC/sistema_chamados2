import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, Typography, CircularProgress, Alert,
  Divider, Tooltip,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { apiTecnicos } from '../api/api.js'

const schema = z.object({
  nome:         z.string().min(1, 'Nome é obrigatório'),
  especialidade:z.string().optional(),
  telefone:     z.string().optional(),
  email:        z.string().email('E-mail inválido').optional().or(z.literal('')),
})

const VAZIO = { nome: '', especialidade: '', telefone: '', email: '' }

export default function Tecnicos() {
  const [tecnicos,     setTecnicos]     = useState([])
  const [carregando,   setCarregando]   = useState(true)
  const [dialogAberto, setDialogAberto] = useState(false)
  const [editando,     setEditando]     = useState(null)
  const [erroDialog,   setErroDialog]   = useState('')
  const [erroGeral,    setErroGeral]    = useState('')

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema), defaultValues: VAZIO,
  })

  const carregar = async () => {
    try { const res = await apiTecnicos.listar(); setTecnicos(res.data) }
    catch { setErroGeral('Não foi possível carregar os técnicos.') }
    finally { setCarregando(false) }
  }

  useEffect(() => { carregar() }, [])

  const abrirNovo = () => { setEditando(null); reset(VAZIO); setErroDialog(''); setDialogAberto(true) }
  const abrirEditar = (t) => {
    setEditando(t)
    reset({ nome: t.nome, especialidade: t.especialidade, telefone: t.telefone, email: t.email })
    setErroDialog(''); setDialogAberto(true)
  }

  const onSubmit = async (dados) => {
    try {
      if (editando) await apiTecnicos.atualizar(editando.id_tecnico, dados)
      else          await apiTecnicos.criar(dados)
      setDialogAberto(false); carregar()
    } catch (e) {
      setErroDialog(e.response?.data?.erro ?? 'Erro ao salvar.')
    }
  }

  const excluir = async (id) => {
    if (!window.confirm('Excluir este técnico?')) return
    try { await apiTecnicos.excluir(id); carregar() }
    catch (e) { alert(e.response?.data?.erro ?? 'Erro ao excluir.') }
  }

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight={700}>Técnicos</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={abrirNovo}>Novo Técnico</Button>
      </Box>

      {erroGeral && <Alert severity="error" sx={{ mb: 2 }}>{erroGeral}</Alert>}

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'primary.main' }}>
            <TableRow>
              {['ID', 'Nome', 'Especialidade', 'Telefone', 'E-mail', 'Ações'].map((h, i) => (
                <TableCell key={h} align={i === 5 ? 'right' : 'left'}
                           sx={{ color: 'white', fontWeight: 700 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tecnicos.length === 0 && (
              <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                Nenhum técnico cadastrado.
              </TableCell></TableRow>
            )}
            {tecnicos.map((t) => (
              <TableRow key={t.id_tecnico} hover>
                <TableCell>{t.id_tecnico}</TableCell>
                <TableCell><b>{t.nome}</b></TableCell>
                <TableCell>{t.especialidade}</TableCell>
                <TableCell>{t.telefone}</TableCell>
                <TableCell>{t.email}</TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton size="small" onClick={() => abrirEditar(t)}><EditIcon fontSize="small" /></IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton size="small" color="error" onClick={() => excluir(t.id_tecnico)}><DeleteIcon fontSize="small" /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogAberto} onClose={() => setDialogAberto(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{editando ? 'Editar Técnico' : 'Novo Técnico'}</DialogTitle>
          <Divider />
          <DialogContent>
            <TextField {...register('nome')} label="Nome *" fullWidth margin="normal"
              error={!!errors.nome} helperText={errors.nome?.message} />
            <TextField {...register('especialidade')} label="Especialidade" fullWidth margin="normal" />
            <TextField {...register('telefone')} label="Telefone" fullWidth margin="normal" />
            <TextField {...register('email')} label="E-mail" fullWidth margin="normal"
              error={!!errors.email} helperText={errors.email?.message} />
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
