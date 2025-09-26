#!/bin/bash
# Script di avvio migliorato per Tor Anonymizer

set -e  # Exit on error

echo "🔒 Tor Anonymizer - Avvio Sicuro"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non installato"
    exit 1
fi

# Check dependencies
if [ ! -f "requirements.txt" ]; then
    echo "❌ File requirements.txt non trovato"
    exit 1
fi

# Install dependencies if needed
if ! python3 -c "import requests, stem" &> /dev/null; then
    echo "📦 Installazione dipendenze..."
    pip3 install -r requirements.txt
fi

# Check Tor installation
if ! command -v tor &> /dev/null; then
    echo "❌ Tor non installato"
    echo "💡 Installa con: sudo apt install tor"
    exit 1
fi

# Run application
echo "🚀 Avvio applicazione..."
python3 tor_anonymizer.py
