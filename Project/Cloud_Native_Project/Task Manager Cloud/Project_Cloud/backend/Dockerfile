# Stage 1: Build
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim-bookworm

WORKDIR /app

# Create non-root user
RUN groupadd appgroup && useradd -g appgroup appuser

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Fix permissions
RUN chown -R appuser:appgroup /app

# Switch user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

