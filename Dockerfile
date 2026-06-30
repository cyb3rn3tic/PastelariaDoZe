FROM python:3.11-slim

# Define o diretório principal
WORKDIR /app

# Supondo que o seu requirements.txt também esteja na raiz. 
# (Se ele estiver dentro da src, mude esta linha para: COPY src/requirements.txt .)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia a pasta src do seu computador para dentro do container
COPY ./src ./src

# Entra na pasta src para o Uvicorn achar o main.py
WORKDIR /app/src

EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]