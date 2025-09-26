FROM python:3.9-slim

# Installa Tor prima delle dipendenze Python
RUN apt-get update && apt-get install -y \
    tor \
    torsocks \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configurazione Tor di default
COPY torrc.example /etc/tor/torrc

# Crea utente non-root
RUN useradd -m -u 1000 toruser && \
    chown -R toruser:toruser /app

USER toruser

EXPOSE 9050 9051

CMD ["python", "tor_anonymizer.py"]
