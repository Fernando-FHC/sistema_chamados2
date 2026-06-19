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
