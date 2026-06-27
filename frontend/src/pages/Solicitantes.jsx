/**
 * Página de Solicitantes.
 */
import { useState, useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, Typography, CircularProgress, Alert,
  Divider, Tooltip, InputAdornment,
} from '@mui/material'
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon,
  Search as SearchIcon, CheckCircle as CheckIcon,
} from '@mui/icons-material'
import { apiSolicitantes } from '../api/api.js'

const schema = z.object({
  nome:     z.string().min(1, 'Nome é obrigatório'),
  setor:    z.string().optional(),
  telefone: z.string().optional(),
  email:    z.string().email('E-mail inválido').optional().or(z.literal('')),
})

const VAZIO = { nome: '', setor: '', telefone: '', email: '' }

// ── Hook de busca ViaCEP ─────────────────────────────────────────────
function useCep(setValue) {
  const [cep, setCep]                     = useState('')
  const [buscandoCep, setBuscandoCep]     = useState(false)
  const [cepEncontrado, setCepEncontrado] = useState(false)
  const [erroCep, setErroCep]             = useState('')
  const ultimoCep = useRef('')

  const buscarCep = async (valor) => {
    const nums = valor.replace(/\D/g, '')
    if (nums.length !== 8 || nums === ultimoCep.current) return

    ultimoCep.current = nums
    setBuscandoCep(true)
    setCepEncontrado(false)
    setErroCep('')

    try {
      // ViaCEP — API pública brasileira gratuita, sem autenticação
      const res  = await fetch(`https://viacep.com.br/ws/${nums}/json/`)
      const data = await res.json()

      if (data.erro) { setErroCep('CEP não encontrado.'); return }

      // Preenche o campo "setor" com localização obtida do CEP
      const localizacao = [data.logradouro, data.complemento, data.bairro, data.localidade, data.uf]
        .filter(Boolean).join(' — ')
      setValue('setor', localizacao, { shouldDirty: true })
      setCepEncontrado(true)
    } catch {
      setErroCep('Não foi possível consultar o CEP.')
    } finally {
      setBuscandoCep(false)
    }
  }

  const handleCepChange = (e) => {
    const valor = e.target.value
    setCep(valor)
    setCepEncontrado(false)
    setErroCep('')
    if (valor.replace(/\D/g, '').length === 8) buscarCep(valor)
  }

  const resetCep = () => {
    setCep(''); setCepEncontrado(false); setErroCep(''); ultimoCep.current = ''
  }

  return { cep, buscandoCep, cepEncontrado, erroCep, handleCepChange, resetCep }
}

// ── Componente principal ─────────────────────────────────────────────

export default function Solicitantes() {
  const [solicitantes, setSolicitantes] = useState([])
  const [carregando,   setCarregando]   = useState(true)
  const [dialogAberto, setDialogAberto] = useState(false)
  const [editando,     setEditando]     = useState(null)
  const [erroDialog,   setErroDialog]   = useState('')
  const [erroGeral,    setErroGeral]    = useState('')

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(schema), defaultValues: VAZIO,
  })

  const { cep, buscandoCep, cepEncontrado, erroCep, handleCepChange, resetCep } = useCep(setValue)

  const carregar = async () => {
    try { const res = await apiSolicitantes.listar(); setSolicitantes(res.data) }
    catch { setErroGeral('Não foi possível carregar os solicitantes.') }
    finally { setCarregando(false) }
  }

  useEffect(() => { carregar() }, [])

  const abrirNovo = () => {
    setEditando(null); reset(VAZIO); resetCep(); setErroDialog(''); setDialogAberto(true)
  }

  const abrirEditar = (s) => {
    setEditando(s)
    reset({ nome: s.nome, setor: s.setor, telefone: s.telefone, email: s.email })
    resetCep(); setErroDialog(''); setDialogAberto(true)
  }

  const onSubmit = async (dados) => {
    try {
      if (editando) await apiSolicitantes.atualizar(editando.id_solicitante, dados)
      else          await apiSolicitantes.criar(dados)
      setDialogAberto(false); carregar()
    } catch (e) {
      setErroDialog(e.response?.data?.erro ?? 'Erro ao salvar.')
    }
  }

  const excluir = async (id) => {
    if (!window.confirm('Excluir este solicitante?')) return
    try { await apiSolicitantes.excluir(id); carregar() }
    catch (e) { alert(e.response?.data?.erro ?? 'Erro ao excluir.') }
  }

  if (carregando) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight={700}>Solicitantes</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={abrirNovo}>
          Novo Solicitante
        </Button>
      </Box>

      {erroGeral && <Alert severity="error" sx={{ mb: 2 }}>{erroGeral}</Alert>}

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'primary.main' }}>
            <TableRow>
              {['ID', 'Nome', 'Setor / Localização', 'Telefone', 'E-mail', 'Ações'].map((h, i) => (
                <TableCell key={h} align={i === 5 ? 'right' : 'left'}
                           sx={{ color: 'white', fontWeight: 700 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {solicitantes.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                  Nenhum solicitante cadastrado.
                </TableCell>
              </TableRow>
            )}
            {solicitantes.map((s) => (
              <TableRow key={s.id_solicitante} hover>
                <TableCell>{s.id_solicitante}</TableCell>
                <TableCell><b>{s.nome}</b></TableCell>
                <TableCell>{s.setor}</TableCell>
                <TableCell>{s.telefone}</TableCell>
                <TableCell>{s.email}</TableCell>
                <TableCell align="right">
                  <Tooltip title="Editar">
                    <IconButton size="small" onClick={() => abrirEditar(s)}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Excluir">
                    <IconButton size="small" color="error" onClick={() => excluir(s.id_solicitante)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogAberto} onClose={() => setDialogAberto(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{editando ? 'Editar Solicitante' : 'Novo Solicitante'}</DialogTitle>
          <Divider />
          <DialogContent>
            <TextField
              {...register('nome')}
              label="Nome *" fullWidth margin="normal"
              error={!!errors.nome} helperText={errors.nome?.message}
            />

            {/* Campo auxiliar de CEP — consulta ViaCEP, não salvo no banco */}
            <TextField
              label="CEP (busca automática)"
              value={cep}
              onChange={handleCepChange}
              fullWidth margin="normal"
              placeholder="Ex: 17900-000"
              inputProps={{ maxLength: 9 }}
              error={!!erroCep}
              helperText={
                erroCep ? erroCep
                : cepEncontrado ? '✓ Localização preenchida via ViaCEP'
                : 'Digite o CEP para preencher o setor automaticamente'
              }
              FormHelperTextProps={{ sx: { color: cepEncontrado && !erroCep ? 'success.main' : undefined } }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {buscandoCep
                      ? <CircularProgress size={18} />
                      : cepEncontrado
                      ? <CheckIcon color="success" fontSize="small" />
                      : <SearchIcon color="disabled" fontSize="small" />}
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              {...register('setor')}
              label="Setor / Localização"
              fullWidth margin="normal"
              helperText="Preenchido pelo CEP ou informado manualmente"
            />

            <TextField {...register('telefone')} label="Telefone" fullWidth margin="normal" />

            <TextField
              {...register('email')}
              label="E-mail" fullWidth margin="normal"
              error={!!errors.email} helperText={errors.email?.message}
            />

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
