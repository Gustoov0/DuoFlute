# Imagem base: Python 3.12 em versão enxuta
FROM python:3.12-slim

# Não gera arquivos .pyc e mostra os logs na hora (útil com Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala as dependências primeiro: o Docker reaproveita essa camada
# enquanto o requirements.txt não mudar, e os builds ficam bem mais rápidos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e a configuração das migrações
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

EXPOSE 8000

# Comando padrão ao iniciar o container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]