# ---------- Frontend build ----------
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---------- Backend runtime ----------
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend + docs
COPY backend/ /app/backend/
COPY data/ /app/data/

# Copy built frontend
COPY --from=frontend /frontend/dist /app/frontend/dist

# Make backend importable
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000
CMD ["uvicorn", "--app-dir", "/app/backend", "agentic_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
