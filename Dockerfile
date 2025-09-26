FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs tor_data

# Copy Tor configuration
COPY torrc.example /etc/tor/torrc

# Set permissions
RUN chmod +x tor-anonymizer.sh

# Expose Tor ports
EXPOSE 9050 9051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -s --socks5-hostname localhost:9050 http://check.torproject.org/ | grep -q Congratulations

# Start application
CMD ["python", "tor_anonymizer.py"]
