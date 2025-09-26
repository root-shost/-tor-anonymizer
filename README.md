# TOR Anonymizer 🔒

Professional Privacy Tool for Advanced Anonymization

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

# ⚠️ DISCLAIMER LEGALE E AVVISO DI SICUREZZA CRITICO

## INTENSO D'USO APPROPRIATO
Questo strumento è sviluppato ESCLUSIVAMENTE per:
- Test di penetrazione autorizzati
- Ricerca sulla privacy e educazione alla sicurezza
- Audit di sicurezza con permesso esplicito
- Sviluppo di contromisure di sicurezza

## ⚖️ AVVERTENZE LEGALI
- **VIETATO** l'uso per attività illegali o non autorizzate
- L'autore **NON** è responsabile per uso improprio
- Verificare le leggi locali prima dell'utilizzo
- Richiedere sempre autorizzazioni scritte per testing

## 🚨 CONSEGUENZE
L'uso non autorizzato può risultare in:
- Azioni legali penali e civili
- Violazione di termini di servizio

# 👨‍💻 Author - **Andrea Filippo Mongelli** - **Offensive Specialist**

## 🚀 Features

- ✅ Automatic IP rotation via Tor network
- ✅ Professional Python implementation
- ✅ Docker container support
- ✅ Real-time connection monitoring
- ✅ Comprehensive logging system
- ✅ Secure configuration management

## 📦 Installation & Quick Start

### Method 1: Direct Execution
```bash
git clone https://github.com/root-shost/-tor-anonymizer.git
cd tor-anonymizer

# Install dependencies
```bash
./install.sh 
or
pip install -r requirements.txt

# Start the service
```bash
./tor-anonymizer.sh start

# Check status
```bash
./tor-anonymizer.sh status

# Test connection
```bash
./tor-anonymizer.sh test

# View logs
```bash
./tor-anonymizer.sh logs

# Stop the service
```bash
./tor-anonymizer.sh stop

# Activate virtual environment
```bash
source venv/bin/activate

# Test connection
```bash
python3 tor_anonymizer.py --test

# Interactive mode
python3 tor_anonymizer.py

# Single request
python3 tor_anonymizer.py --url "https://example.com"

# Interactive mode
```bash
python tor_anonymizer.py


