FROM python:3.9-slim

# Installazione sicura
RUN apt-get update && apt-get install -y \
    tor \
    && rm -rf /var/lib/apt/lists/*

# Utente non-root per sicurezza
RUN useradd -m -u 1000 toruser
WORKDIR /app

# Copia file necessari
COPY requirements.txt .
COPY tor_anonymizer.py .
COPY torrc.example .

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura permessi sicuri
RUN chown -R toruser:toruser /app
USER toruser

# Configurazione Tor sicura
COPY torrc.example /etc/tor/torrc

# Avvio applicazione
CMD ["python", "tor_anonymizer.py"]
