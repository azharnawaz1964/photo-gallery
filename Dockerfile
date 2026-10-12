FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies and create mount directory
RUN apt-get update && apt-get install -y --no-install-recommends \
    nfs-common \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /mnt/filestore \
    && chmod 777 /mnt/filestore

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .

# Run with gunicorn on the port provided by Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
