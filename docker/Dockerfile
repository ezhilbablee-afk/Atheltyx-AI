FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY . /app

# Expose HTTP port
EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')"

# Run launcher
CMD ["python", "run.py", "--port", "8080", "--no-browser"]
