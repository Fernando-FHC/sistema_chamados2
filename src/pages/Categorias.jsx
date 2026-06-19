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
import { apiCategorias } from '../api/api.js'

const schema = z.object({
  nome:     z.string().min(1, 'Nome é obrigatório').max(100),
  descricao:z.string().optional(),
})

export default function Categorias() {
  const [categorias,   setCategorias]   = useState([])
  const [carregando,   setCarregando]   = useState(true)
  const [dialogAberto, setDialogAberto] = useState(false)
  const [editando,     setEditando]     = useState(null)
  const [erroDialog,   setErroDialog]   = useState('')
  const [erroGeral,    setErroGeral]    = useState('')

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { nome: '', descricao: '' },
  })

  const carregar = async () => {
    try {
      const res = await apiCategorias.listar()
      setCategorias(res.data)
    } catch {
      setErroGeral('Não foi possível carregar as categorias.')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => { carregar() }, [])

  const abrirNovo = () => {
    setEditando(null); reset({ nome: '', descricao: '' }); setErroDialog(''); setDialogAberto(true)
  }
  const abrirEditar = (cat) => {
    setEditando(cat); reset({ nome: cat.nome, descricao: cat.descricao }); setErroDialog(''); setDialogAberto(true)
  }

  const onSubmit = async (dados) => {
    try {
      if (editando) await apiCategorias.atualizar(editando.id_categoria, dados)
      else          await apiCategorias.criar(dados)
      setDialogAberto(false); carregar()
    } catch (e) {
      setErroDialog(e.response?.data?.erro ?? 'Erro ao salvar.')
    }
  }

  const excluir = async (id) => {
    if (!window.confirm('Excluir esta categoria?')) return
    try { await apiCategorias.excluir(id); carregar() }
    catch (e) { alert(e.response?.data?.erro ?? 'Erro ao excluir.') }
  }

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight={700}>Categorias</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={abrirNovo}>Nova Categoria</Button>
      </Box>

      {erroGeral && <Alert severity="error" sx={{ mb: 2 }}>{erroGeral}</Alert>}

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'primary.main' }}>
            <TableRow>
              {['ID', 'Nome', 'Descrição', 'Ações'].map((h, i) => (
                <TableCell key={h} align={i === 3 ? 'right' : 'left'}
                           sx={{ color: 'white', fontWeight: 700 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {categorias.length === 0 && (
              <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                Nenhuma categoria cadastrada.
              </TableCell></TableRow>
            )}
            {categorias.map((c) => (
              <TableRow key={c.id_categoria} hover>
                <TableCell>{c.id_categoria}</TableCell>
                <TableCell><b>{c.nome}</b></TableCell>
                <TableCell>{c.descricao}</TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton size="small" onClick={() => abrirEditar(c)}><EditIcon fontSize="small" /></IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton size="small" color="error" onClick={() => excluir(c.id_categoria)}><DeleteIcon fontSize="small" /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogAberto} onClose={() => setDialogAberto(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{editando ? 'Editar Categoria' : 'Nova Categoria'}</DialogTitle>
          <Divider />
          <DialogContent>
            <TextField {...register('nome')} label="Nome *" fullWidth margin="normal"
              error={!!errors.nome} helperText={errors.nome?.message} />
            <TextField {...register('descricao')} label="Descrição" fullWidth margin="normal" multiline rows={2} />
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
