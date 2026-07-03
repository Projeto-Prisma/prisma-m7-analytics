# Imagem base leve do Python
FROM python:3.11-slim

# Criação de um usuário não-root por segurança
RUN adduser --disabled-password --gecos '' prismauser

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Passa a posse dos arquivos para o usuário comum
RUN chown -R prismauser:prismauser /app
USER prismauser

EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]