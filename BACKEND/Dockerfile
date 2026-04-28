FROM python:3.9-slim

# Installation des dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On copie les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt || \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# On copie tout le contenu du dossier backend dans /app
COPY . .

# On expose le port
EXPOSE 8000

# Commande de lancement (SANS LE # DEVANT)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]