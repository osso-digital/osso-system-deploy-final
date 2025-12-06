# Dockerfile para deploy em Google Cloud Run
# Base leve e compatível com Python 3.11 (ajuste a versão se necessário)
FROM python:3.11-slim

# Evitar mensagens interativas
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório da aplicação
WORKDIR /app

# Dependências do SO necessárias (ajuste conforme libs nativas que usar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia o código da aplicação
COPY . /app

# Porta usada pelo Cloud Run
ENV PORT=8080

# Recomendações: não deixar chaves em arquivos no repo
# Se tiver 'meu-segredo.json', NÃO copie para a imagem em produção - use Secret Manager ou Workload Identity.

# Expor a porta (documentação/boa prática)
EXPOSE 8080

# CMD para rodar com gunicorn:
# Ajuste 'osso_api:app' se seu módulo/app tiver outro nome (ex: main:create_app()).
# Configuração conservadora: 1 worker, threads 8, timeout 0 (sem timeout limitado).
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 osso_api:app
