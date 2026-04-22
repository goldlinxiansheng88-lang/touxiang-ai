FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for common wheels (psycopg, cryptography, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

