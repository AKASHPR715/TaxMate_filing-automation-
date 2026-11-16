# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    PYTHONPATH=/home/user/app

# Install system dependencies (poppler-utils is required for pdf2image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs containers as user with UID 1000
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install python dependencies as user
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy entrypoint script and application code
COPY --chown=user:user entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY --chown=user:user . .

USER user

# Hugging Face Spaces listens on port 7860
EXPOSE 7860

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Command to run the application on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
