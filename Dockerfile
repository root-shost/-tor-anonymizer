FROM python:3.9-slim

LABEL maintainer="root-shost"
LABEL version="2.0"
LABEL description="TOR Anonymizer - Professional Privacy Tool"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    proxychains4 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy application files
COPY requirements.txt .
COPY src/ ./src/
COPY config/ ./config/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -r -s /bin/false toruser
RUN chown -R toruser:toruser /app

# Expose Tor ports
EXPOSE 9050 9051

# Switch to non-root user
USER toruser

# Set entrypoint
CMD ["python", "src/tor_anonymizer.py"]
