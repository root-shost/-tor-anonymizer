FROM python:3.11-slim

# Security hardening
LABEL maintainer="root-shost"
LABEL version="2.0.0"
LABEL description="Secure Tor Anonymization Tool"

# Security environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TOR_PORT=9050 \
    CONTROL_PORT=9051 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies securely
RUN apt-get update && apt-get install -y \
    tor \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application directory
WORKDIR /app

# Copy Tor configuration
COPY torrc.example /etc/tor/torrc

# Copy application files
COPY requirements.txt .
COPY tor_anonymizer.py .
COPY settings.json .

# Install Python dependencies securely
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user with secure permissions
RUN groupadd -r toruser && useradd -r -g toruser toruser && \
    chown -R toruser:toruser /app && \
    chown -R toruser:toruser /var/lib/tor && \
    chmod 600 /etc/tor/torrc

# Switch to non-root user
USER toruser

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -s --socks5-hostname localhost:9050 http://httpbin.org/ip >/dev/null || exit 1

# Expose ports
EXPOSE 9050 9051

# Secure entry point
CMD ["sh", "-c", "tor --runasdaemon 1 && sleep 5 && python tor_anonymizer.py"]
