FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies and kubectl
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    sqlite3 \
    libsqlite3-dev \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p ~/.kube

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/static/db /app/static/js /app/templates && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Copy requirements first for better caching
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest coverage

# Copy application code
COPY --chown=appuser:appuser . .

# Set permissions for runtime directories
RUN chmod -R 777 /app/logs /app/static/db

# Switch to non-root user
USER appuser

# Volume configuration for persistence
VOLUME ["/app/logs", "/app/static/db", "/root/.kube"]

# Expose port
EXPOSE 5000

# Enhanced health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/k8s/status || exit 1

# Command to run the application with optimized settings
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "--keep-alive", "5", "--log-level", "info", "app:app"]
