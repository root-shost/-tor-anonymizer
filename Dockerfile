FROM python:3.11-slim

# Set metadata
LABEL maintainer="root-shost"
LABEL version="2.0.0"
LABEL description="Professional Tor Anonymization Tool"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TOR_PORT=9050 \
    CONTROL_PORT=9051

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy Tor configuration
COPY torrc.example /etc/tor/torrc

# Copy application files
COPY requirements.txt .
COPY pyproject.toml .
COPY tor_anonymizer.py .
COPY settings.json .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -r toruser && \
    chown -R toruser:toruser /app && \
    chown -R toruser:toruser /var/lib/tor

# Switch to non-root user
USER toruser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -s --socks5-hostname localhost:9050 http://httpbin.org/ip >/dev/null || exit 1

# Expose ports
EXPOSE 9050 9051

# Start command
CMD ["sh", "-c", "tor & python tor_anonymizer.py"]
