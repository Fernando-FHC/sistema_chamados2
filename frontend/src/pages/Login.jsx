/**
 * Página de Login.
 *
 * Valida o formulário com React Hook Form + Zod antes de enviar
 * a requisição ao backend. Em caso de erro de credenciais, exibe a
 * mensagem retornada pela API.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Box, Card, CardContent, TextField, Button, Typography,
  Alert, CircularProgress,
} from '@mui/material'
import { LockOutlined as LockIcon } from '@mui/icons-material'
import { apiAuth } from '../api/api.js'
import { useAuth } from '../context/AuthContext.jsx'

// Schema de validação com Zod
const schema = z.object({
  nome_usuario: z.string().min(1, 'Informe o usuário.'),
  senha:        z.string().min(1, 'Informe a senha.'),
})

export default function Login() {
  const { login }    = useAuth()
  const navigate     = useNavigate()
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) })

  const onSubmit = async (dados) => {
    setErro('')
    setEnviando(true)
    try {
      const res = await apiAuth.login(dados)
      login(res.data.token, res.data.usuario)
      // Admin vai para o dashboard; usuário comum vai para chamados
      navigate(res.data.usuario.tipo_usuario === 'Administrador' ? '/dashboard' : '/chamados')
    } catch (e) {
      setErro(e.response?.data?.erro ?? 'Erro ao conectar com o servidor.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="grey.100"
    >
      <Card sx={{ width: 380, boxShadow: 4 }}>
        <CardContent sx={{ p: 4 }}>
          {/* Ícone + título */}
          <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
            <Box
              sx={{
                bgcolor: 'primary.main', borderRadius: '50%',
                width: 52, height: 52, display: 'flex',
                alignItems: 'center', justifyContent: 'center', mb: 1,
              }}
            >
              <LockIcon sx={{ color: 'white' }} />
            </Box>
            <Typography variant="h6" fontWeight={700}>
              Sistema de Chamados
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Informe suas credenciais para entrar
            </Typography>
          </Box>

          {/* Formulário */}
          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            <TextField
              {...register('nome_usuario')}
              label="Usuário"
              fullWidth
              margin="normal"
              autoFocus
              error={!!errors.nome_usuario}
              helperText={errors.nome_usuario?.message}
            />
            <TextField
              {...register('senha')}
              label="Senha"
              type="password"
              fullWidth
              margin="normal"
              error={!!errors.senha}
              helperText={errors.senha?.message}
            />

            {erro && <Alert severity="error" sx={{ mt: 1 }}>{erro}</Alert>}

            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              sx={{ mt: 2 }}
              disabled={enviando}
            >
              {enviando ? <CircularProgress size={22} color="inherit" /> : 'Entrar'}
            </Button>
          </Box>

          <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={2}>
            Contas padrão: admin / admin123 · usuario / usuario123
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}
