#!/bin/bash

# TOR Anonymizer Script v2.0.0 - Secure Implementation
set -euo pipefail

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="${SCRIPT_DIR}/settings.json"
readonly LOG_FILE="${SCRIPT_DIR}/logs/tor_anonymizer.log"

print_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║                   TOR ANONYMIZER v2.0.0                      ║
║                       Ultimate Privacy Tool                  ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/-tor-anonymizer        ║
╚══════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
}

log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

check_dependencies() {
    local deps=("tor" "python3" "curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Dependency missing: $dep"
            return 1
        fi
    done
    success "Dependencies verified"
}

setup_environment() {
    log "Setting up environment..."
    mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/data"
    
    # Secure config file handling
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warning "Creating secure default configuration..."
        cat > "$CONFIG_FILE" << 'EOF'
{
    "tor_port": 9050,
    "control_port": 9051,
    "control_password": "change_this_secure_password",
    "identity_rotation_interval": 300,
    "max_retries": 3,
    "timeout": 30
}
EOF
        chmod 600 "$CONFIG_FILE"
    fi
}

check_tor_service() {
    if curl --socks5-hostname localhost:9050 --max-time 10 http://httpbin.org/ip &>/dev/null; then
        return 0
    fi
    
    log "Starting Tor service..."
    if command -v systemctl &> /dev/null && systemctl is-active tor &>/dev/null; then
        sudo systemctl start tor
    else
        tor --runasdaemon 1
    fi
    
    local attempt=1
    while [[ $attempt -le 30 ]]; do
        if curl --socks5-hostname localhost:9050 --max-time 5 http://httpbin.org/ip &>/dev/null; then
            success "Tor service ready"
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    error "Tor service failed to start"
    return 1
}

main() {
    print_banner
    local command=${1:-help}
    
    case $command in
        start)
            check_dependencies && setup_environment && check_tor_service && \
            python3 tor_anonymizer.py
            ;;
        stop) pkill -f "python3 tor_anonymizer.py" && success "Service stopped" ;;
        status) 
            pgrep -f "python3 tor_anonymizer.py" && success "Running" || error "Stopped"
            ;;
        *) echo "Usage: $0 {start|stop|status}"; exit 1 ;;
    esac
}

main "$@"
