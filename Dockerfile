FROM python:3.12.10-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create data directory for SQLite and uploads
RUN mkdir -p /app/data /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/atlas.db

# Expose port for webhook (Render will set the actual PORT)
EXPOSE 8000

# Health check using PORT environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; port = os.environ.get('PORT', '8000'); requests.get(f'http://0.0.0.0:{port}/health')"

# Run the application using Render's PORT environment variable
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
