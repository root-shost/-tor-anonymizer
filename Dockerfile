FROM python:3.9-slim

# Install system dependencies including Tor
RUN apt-get update && apt-get install -y \
    tor \
    torsocks \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 toruser && \
    chown -R toruser:toruser /app && \
    chown -R toruser:toruser /var/lib/tor

# Create directories for Tor data
RUN mkdir -p /app/logs /app/tor_data && \
    chown toruser:toruser /app/logs /app/tor_data

# Copy Tor configuration
COPY torrc.example /etc/tor/torrc

USER toruser

# Expose Tor ports
EXPOSE 9050 9051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --socks5-hostname localhost:9050 -f http://httpbin.org/ip || exit 1

CMD ["python", "tor_anonymizer.py"]
