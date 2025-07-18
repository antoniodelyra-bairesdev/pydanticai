# Estágio 1: Build - Usando Python 3.12
FROM python:3.12-slim as builder

WORKDIR /usr/src/app

# Instalar dependências do sistema para compilação
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e gerar wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# Estágio 2: Produção - Usando Python 3.12
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema (apenas runtime)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do estágio builder
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

# Instalar dependências a partir dos wheels
RUN pip install --no-cache /wheels/*

# Copiar código da aplicação
COPY src/ ./src/

# Criar diretório para uploads
RUN mkdir -p uploads/temp

# Expor porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "src.docling_pdf.main:app", "--host", "0.0.0.0", "--port", "8000"] 