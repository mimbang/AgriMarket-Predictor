# 1. On passe sur 'slim', beaucoup plus léger pour la prod
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 2. On installe 'cron' et les libs pour Postgres
RUN apt-get update && apt-get install -y \
    cron \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Cache des dépendances
COPY requirements.txt .
# On force l'utilisation des binaires pour éviter la compilation lente
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# 4. Copie du projet
COPY . .

# 5. Configuration Cron
# On s'assure que le fichier crontab existe avant de le copier
COPY crontab /etc/cron.d/agri-cron
RUN chmod 0644 /etc/cron.d/agri-cron && crontab /etc/cron.d/agri-cron

# 6. Lancement (On utilise l'exécution en mode JSON pour capturer les logs proprement)
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8000"]