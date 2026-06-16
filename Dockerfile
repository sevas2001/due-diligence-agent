# Imagen única para API y frontend (cambia el CMD en docker-compose).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Deps primero para aprovechar la cache de capas.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY frontend ./frontend
COPY scripts ./scripts

EXPOSE 8000 8501

# Por defecto arranca la API; el frontend sobreescribe el comando en compose.
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
