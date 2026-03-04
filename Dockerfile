# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# poppler-utils is required for PDF processing (pdf2image)
# netcat-openbsd is for waiting for DB
RUN apt-get update && apt-get install -y \
    poppler-utils \
    netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script to a location not overridden by volume mount
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Command to run the application
# Gunicorn manages worker processes; each worker runs uvicorn (ASGI)
# 1 worker is recommended for serverless free tier to avoid OOM
# GCP Cloud Run provides the PORT environment variable
CMD ["sh", "-c", "gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120"]
