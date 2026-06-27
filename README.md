# Sistema de Chamados — Frontend React

Frontend do Sistema de Abertura, Controle e Fechamento de Chamados de Informática, Telefonia e Manutenção Geral, desenvolvido com **React + Vite** e conectado a um backend **Flask** via API REST.

---

## Tecnologias e bibliotecas utilizadas

| Biblioteca | Versão | Finalidade |
|---|---|---|
| `react` | 18 | Biblioteca principal de UI |
| `react-dom` | 18 | Renderização no navegador |
| `react-router-dom` | 6 | Roteamento SPA e proteção de rotas |
| `@mui/material` | 6 | Componentes visuais (Material UI) |
| `@mui/icons-material` | 6 | Ícones Material Design |
| `@emotion/react` + `@emotion/styled` | 11 | Engine de CSS-in-JS (dependência do MUI) |
| `react-hook-form` | 7 | Gerenciamento e validação de formulários |
| `@hookform/resolvers` | 3 | Integração entre RHF e Zod |
| `zod` | 3 | Schema de validação de dados (TypeScript-first) |
| `recharts` | 2 | Gráficos (PieChart, BarChart, ResponsiveContainer) |
| `axios` | 1 | Requisições HTTP ao backend Flask |
| `vite` | 6 | Bundler e servidor de desenvolvimento |

---

## APIs externas consumidas

### 1. ViaCEP — `https://viacep.com.br`
- **Gratuita, sem autenticação, sem limite de uso**
- Usada na página de **Solicitantes**: ao digitar um CEP válido (8 dígitos), o campo "Setor / Localização" é preenchido automaticamente com bairro, cidade e UF.
- Exemplo de chamada: `GET https://viacep.com.br/ws/01310100/json/`

### 2. BrasilAPI — `https://brasilapi.com.br`
- **Gratuita, open source, sem autenticação**
- Usada no **Dashboard**: exibe os próximos feriados nacionais do ano com contagem regressiva.
- Exemplo de chamada: `GET https://brasilapi.com.br/api/feriados/v1/2026`

---

## Estrutura do projeto

```
frontend/
├── index.html
├── vite.config.js
├── vercel.json          # configuração para deploy no Vercel
├── .env.example         # modelo das variáveis de ambiente
├── package.json
└── src/
    ├── main.jsx             # ponto de entrada
    ├── App.jsx              # rotas e tema MUI
    ├── api/
    │   └── api.js           # instância Axios + funções de API
    ├── context/
    │   └── AuthContext.jsx  # autenticação global (token + usuário logado)
    ├── components/
    │   ├── Layout.jsx        # AppBar + Drawer lateral + navegação
    │   └── ProtectedRoute.jsx # guarda de rotas por autenticação e perfil
    └── pages/
        ├── Login.jsx         # tela de login (RHF + Zod)
        ├── Dashboard.jsx     # gráficos Recharts + feriados (BrasilAPI)
        ├── Chamados.jsx      # CRUD principal + filtro por status
        ├── Categorias.jsx    # CRUD de categorias
        ├── Tecnicos.jsx      # CRUD de técnicos
        ├── Solicitantes.jsx  # CRUD + busca de CEP (ViaCEP)
        └── Usuarios.jsx      # CRUD de contas de acesso
```

---

## Como executar localmente

### Pré-requisitos
- Node.js 18+ e npm
- Python 3.8+ com Flask rodando (backend)

### 1. Iniciar o backend Flask

```bash
# Na pasta do projeto Python
cd sistema_chamados
pip install flask flask-cors
python api.py
# Backend disponível em http://localhost:5000
```

### 2. Configurar as variáveis de ambiente

```bash
cd frontend
cp .env.example .env
# O arquivo .env já aponta para http://localhost:5000/api por padrão
# Não é necessário alterar para rodar localmente
```

### 3. Instalar dependências e iniciar o frontend

```bash
npm install
npm run dev
# Acesse http://localhost:5173
```

### Credenciais padrão

| Usuário   | Senha        | Perfil        |
|-----------|--------------|---------------|
| `admin`   | `admin123`   | Administrador |
| `usuario` | `usuario123` | Usuário       |

---

## Controle de acesso por perfil

| Funcionalidade | Administrador | Usuário |
|---|:---:|:---:|
| Dashboard com gráficos | ✅ | ❌ |
| Feriados nacionais (BrasilAPI) | ✅ | ❌ |
| Gerenciar Categorias | ✅ | ❌ |
| Gerenciar Técnicos | ✅ | ❌ |
| Gerenciar Solicitantes | ✅ | ❌ |
| Gerenciar Usuários | ✅ | ❌ |
| Abrir novo chamado | ✅ | ✅ |
| Listar chamados | ✅ | ✅ |
| Editar / Fechar / Excluir chamados | ✅ | ❌ |
| Busca de CEP (ViaCEP) | ✅ | ❌ |

---

## Deploy no Vercel

### Passo a passo

#### 1. Hospedar o backend

O backend Flask precisa estar hospedado em algum serviço antes de publicar o frontend. Opções gratuitas:
- **Render** (render.com) — recomendado, plano gratuito disponível
- **Railway** (railway.app) — plano free com créditos mensais

Após hospedar, anote a URL do backend (ex: `https://seu-backend.onrender.com/api`).

#### 2. Fazer upload para o GitHub

```bash
# Na raiz do repositório (pasta sistema_chamados/)
git init
git add .
git commit -m "feat: sistema de chamados com React + Flask"
git branch -M main
git remote add origin https://github.com/seu-usuario/seu-repositorio.git
git push -u origin main
```

> O `.gitignore` já exclui `node_modules/`, `dist/` e arquivos `.env`.

#### 3. Publicar no Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login com sua conta GitHub
2. Clique em **"New Project"** e importe seu repositório
3. Configure o projeto:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (detectado automaticamente)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Em **Environment Variables**, adicione:
   ```
   VITE_API_URL = https://seu-backend.onrender.com/api
   ```
5. Clique em **Deploy**

O `vercel.json` já está configurado para que o React Router funcione corretamente (todas as rotas redirecionam para `index.html`).

---

## Build de produção

```bash
npm run build
# Gera a pasta dist/ com os arquivos estáticos otimizados
```

---

## Observações

- As senhas são armazenadas no banco como hash SHA-256 com salt aleatório — nunca em texto puro.
- O token de autenticação é salvo no `localStorage` do navegador e adicionado automaticamente ao cabeçalho `Authorization` de todas as requisições Axios.
- Ao trocar de usuário (logout), o token é invalidado no backend e removido do `localStorage`.


# Sistema de Chamados

Sistema de abertura, controle e fechamento de chamados de Informática,
Telefonia e Manutenção Geral.

## Estrutura do projeto

```
sistema_chamados/
├── backend/                  # API REST (Flask + MariaDB)
│   ├── api.py                # endpoints REST e autenticação por token
│   ├── database.py           # conexão com o MariaDB
│   ├── modelos.py            # classes de entidade (Categoria, Chamado…)
│   ├── repositorios.py       # CRUD de cada tabela (herança + polimorfismo)
│   ├── seguranca.py          # hash de senhas com SHA-256 + salt
│   ├── menu.py               # interface de terminal (versão sem frontend)
│   ├── main.py               # ponto de entrada do modo terminal
│   ├── schema.sql            # DDL das tabelas para MariaDB
│   ├── requirements.txt      # dependências Python
│   ├── Dockerfile            # imagem da API para Docker
│   └── .dockerignore         # arquivos excluídos do build Docker
│
├── frontend/                 # Interface web (React + Vite)
│   ├── src/
│   │   ├── api/api.js        # funções Axios para chamar o backend
│   │   ├── context/          # AuthContext (token + usuário logado)
│   │   ├── components/       # Layout (barra lateral) e ProtectedRoute
│   │   └── pages/            # Login, Dashboard, Chamados, Categorias…
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json           # configuração de deploy no Vercel
│   └── .env.example          # VITE_API_URL
│
├── docker-compose.yml        # orquestra backend + MariaDB em Docker
├── nginx-chamados.conf       # vhost Nginx para o VPS
├── .env.example              # modelo de variáveis de ambiente
├── .gitignore
└── README.md                 # este arquivo
```

---

## Como rodar localmente (sem Docker)

### Backend (terminal)

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env    # preencha DB_HOST, DB_USER, DB_PASSWORD…
python main.py                # modo terminal
# ou
python api.py                 # modo API REST (porta 5000)
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # ajuste VITE_API_URL se necessário
npm run dev                   # http://localhost:5173
```

---

## Como rodar com Docker (produção no VPS)

```bash
# 1. Copie e preencha as variáveis de ambiente
cp .env.example .env
nano .env

# 2. Suba os containers (MariaDB + API Flask)
docker compose up -d --build

# 3. Acompanhe os logs
docker logs chamados-api -f

# 4. Teste localmente (antes de configurar o Nginx)
curl http://127.0.0.1:8001/api/login \
  -X POST -H "Content-Type: application/json" \
  -d '{"nome_usuario":"admin","senha":"admin123"}'
```

Consulte a documentação do frontend (`frontend/README.md`) para
instruções de deploy no Vercel.

---

## Credenciais padrão

| Usuário   | Senha        | Perfil        |
|-----------|--------------|---------------|
| `admin`   | `admin123`   | Administrador |
| `usuario` | `usuario123` | Usuário       |

> Troque as senhas padrão após o primeiro acesso em produção
> (menu Usuários → selecione a conta → campo Nova senha).
