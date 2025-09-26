FROM python:3.9-slim

# Install system dependencies securely
RUN apt-get update && apt-get install -y \
    tor \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 toruser && \
    mkdir -p /home/toruser/app && \
    chown -R toruser:toruser /home/toruser

# Switch to non-root user
USER toruser
WORKDIR /home/toruser/app

# Copy requirements first for better caching
COPY --chown=toruser:toruser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application files
COPY --chown=toruser:toruser . .

# Create necessary directories
RUN mkdir -p logs tor_data

# Copy Tor configuration
COPY --chown=toruser:toruser torrc.example ./torrc

# Set Python path
ENV PYTHONPATH=/home/toruser/app
ENV PATH="/home/toruser/.local/bin:${PATH}"

# Expose Tor ports
EXPOSE 9050 9051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -s --socks5-hostname localhost:9050 http://check.torproject.org/ | grep -q Congratulations

# Start application
CMD ["python", "tor_anonymizer.py"]
