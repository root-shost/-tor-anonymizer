#!/bin/bash
# TOR Anonymizer Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        return 1
    fi
    
    # Check Python modules
    if ! python3 -c "import requests, stem, psutil" 2>/dev/null; then
        error "Required Python modules not installed"
        log "Install with: pip3 install requests stem psutil"
        return 1
    fi
    
    # Check Tor
    if ! command -v tor &> /dev/null; then
        warning "Tor is not installed or not in PATH"
        log "Install Tor: sudo apt install tor"
    fi
    
    success "All dependencies available"
    return 0
}

setup_environment() {
    log "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs tor_data
    
    # Create default config if not exists
    if [ ! -f "settings.json" ]; then
        cat > settings.json << EOF
{
    "tor_port": 9050,
    "control_port": 9051,
    "identity_rotation_interval": 10,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "socks5_host": "127.0.0.1",
    "auto_start_tor": true,
    "dns_leak_protection": true,
    "fast_rotation_mode": true
}
EOF
        log "Default configuration created"
    fi
    
    success "Environment setup completed"
}

start_anonymizer() {
    log "Starting Tor Anonymizer with 10-second IP rotation..."
    
    if python3 tor-anonymizer.py --test 2>/dev/null; then
        success "Tor Anonymizer started successfully"
        log "Starting interactive mode..."
        python3 tor-anonymizer.py
    else
        error "Failed to start Tor Anonymizer"
        error "Check logs: $SCRIPT_DIR/logs/tor_anonymizer.log"
        return 1
    fi
}

case "${1:-start}" in
    "start")
        check_dependencies || exit 1
        setup_environment
        start_anonymizer
        ;;
    "test")
        python3 tor-anonymizer.py --test
        ;;
    "status")
        python3 -c "
import json
from pathlib import Path
if Path('logs/tor_anonymizer.log').exists():
    with open('logs/tor_anonymizer.log', 'r') as f:
        lines = f.readlines()[-10:]
    print('Last 10 log entries:')
    for line in lines:
        print(line.strip())
else:
    print('No log file found')
        "
        ;;
    "stop")
        pkill -f "python3 tor-anonymizer.py"
        pkill -f "tor -f torrc"
        success "Tor Anonymizer stopped"
        ;;
    "install")
        log "Installing dependencies..."
        pip3 install requests stem psutil
        sudo apt update
        sudo apt install -y tor
        success "Installation completed"
        ;;
    *)
        echo "Usage: $0 {start|test|status|stop|install}"
        echo "  start   - Start Tor Anonymizer (default)"
        echo "  test    - Test connection"
        echo "  status  - Show status"
        echo "  stop    - Stop running instance"
        echo "  install - Install dependencies"
        exit 1
        ;;
esac
