# ============================================================
# Sister Nani — Medical AI Agent
# Google Cloud Run Deployment
# ============================================================
FROM python:3.11-slim

# Install system dependencies (for psycopg2, audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory for media files
RUN mkdir -p /app/medical_ai_agent/uploads

# Cloud Run sets PORT env var (default 8080)
ENV PORT=8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import requests; requests.get(f'http://localhost:{__import__(\"os\").getenv(\"PORT\",8080)}/docs')" || exit 1

# Run with uvicorn
CMD exec uvicorn medical_ai_agent.api:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 2 \
    --timeout-keep-alive 120
