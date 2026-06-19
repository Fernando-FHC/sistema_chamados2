# ── Imagem base ──────────────────────────────────────────────
# python:3.12-slim é menor que a imagem completa e suficiente
# para rodar Flask + PyMySQL + Gunicorn.
FROM python:3.12-slim

# ── Diretório de trabalho dentro do container ─────────────────
WORKDIR /app

# ── Dependências Python ───────────────────────────────────────
# Copiamos o requirements.txt primeiro (antes do restante do código)
# para aproveitar o cache de camadas do Docker: se o código mudar
# mas o requirements.txt não, o "pip install" não precisa rodar de novo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Código-fonte ──────────────────────────────────────────────
COPY . .

# ── Porta exposta ─────────────────────────────────────────────
# O Gunicorn vai escutar na 8001 dentro do container.
# Essa porta NÃO é exposta diretamente à internet — o Nginx
# no host faz o proxy de HTTPS → http://127.0.0.1:8001.
EXPOSE 8001

# ── Comando de inicialização ──────────────────────────────────
# 2 workers é suficiente para um projeto acadêmico/pequeno.
# Em produção com mais carga, aumente para (2 * núcleos) + 1.
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "2", "api:app"]
