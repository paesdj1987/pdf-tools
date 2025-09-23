# Usa Python slim como base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependências do sistema (OCR + utilitários)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-por \
    ocrmypdf ghostscript qpdf \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Usuário não-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8055

# Comando inicial
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8055"]
