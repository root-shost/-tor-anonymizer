# TOR Anonymizer 🔒

Professional Privacy Tool for Advanced Anonymization

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ⚠️ IMPORTANT SECURITY NOTICE

**This tool is designed for:**
- Authorized penetration testing
- Privacy research and education  
- Security auditing and awareness
- Legal anonymity requirements

**⚠️ Use responsibly and comply with all applicable laws.**

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
pip install -r requirements.txt

# Start the anonymizer
python tor_anonymizer.py

### Method 2: Using Docker
```bash
docker-compose up -d
docker logs tor-anonymizer -f

### Method 3: Script Usage
```bash
chmod +x tor-anonymizer.sh

# Start service
sudo ./tor-anonymizer.sh start

# Check status
./tor-anonymizer.sh status

# Stop service
sudo ./tor-anonymizer.sh stop

### Command Line Usage
```bash
# Test connection
python tor_anonymizer.py --test

# Single request
python tor_anonymizer.py --url "https://example.com"

# Interactive mode
python tor_anonymizer.py


