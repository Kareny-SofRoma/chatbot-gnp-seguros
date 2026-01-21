FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data/pdfs

# Expose port (Railway will inject PORT env var)
EXPOSE 8000

# Run application with PORT variable support for Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
