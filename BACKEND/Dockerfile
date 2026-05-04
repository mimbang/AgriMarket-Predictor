FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# On installe juste le strict nécessaire pour PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

# CORRECTION : guvicorn n'existe pas (c'est gunicorn ou uvicorn)
# Et on sépare les arguments dans une liste pour que Docker les gère bien
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]