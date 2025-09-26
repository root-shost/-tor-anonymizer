#!/bin/bash

# TOR Anonymizer Script v2.0.0
# Professional Tor privacy tool

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/settings.json"
LOG_FILE="${SCRIPT_DIR}/logs/tor_anonymizer.log"
TORRC_FILE="/etc/tor/torrc"

print_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║                   TOR ANONYMIZER v2.0.0                      ║
║                       Ultimate Privacy Tool                  ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/-tor-anonymizer        ║
╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

check_dependencies() {
    local deps=("tor" "python3" "curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Required dependency not found: $dep"
            return 1
        fi
    done
    success "All dependencies found"
}

setup_environment() {
    log "Setting up environment..."
    
    # Create necessary directories
    mkdir -p "${SCRIPT_DIR}/logs"
    mkdir -p "${SCRIPT_DIR}/data"
    
    # Check if settings.json exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warning "settings.json not found, creating default..."
        cat > "$CONFIG_FILE" << EOF
{
    "tor_port": 9050,
    "control_port": 9051,
    "control_password": "$(openssl rand -base64 32)",
    "identity_rotation_interval": 300,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
}
EOF
        success "Default configuration created"
    fi
    
    # Set proper permissions
    chmod 600 "$CONFIG_FILE"
}

install_python_deps() {
    log "Installing Python dependencies..."
    
    # Check if virtual environment should be used
    if [[ ! -d "venv" ]]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        pip install requests stem colorama psutil
    fi
    
    success "Python dependencies installed"
}

check_tor_service() {
    log "Checking Tor service..."
    
    if pgrep -x "tor" > /dev/null; then
        warning "Tor is already running"
        return 0
    fi
    
    # Start Tor service
    if systemctl is-active --quiet tor; then
        log "Starting system Tor service..."
        sudo systemctl start tor
    else
        log "Starting Tor directly..."
        tor --runasdaemon 1
    fi
    
    # Wait for Tor to start
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl --socks5-hostname localhost:9050 --connect-timeout 10 http://httpbin.org/ip &> /dev/null; then
            success "Tor is ready"
            return 0
        fi
        log "Waiting for Tor to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    error "Tor failed to start within timeout"
    return 1
}

test_connection() {
    log "Testing Tor connection..."
    
    local response
    if response=$(curl -s --socks5-hostname localhost:9050 http://httpbin.org/ip); then
        local ip=$(echo "$response" | grep -oE '"origin":\s*"[^"]+"' | cut -d'"' -f4)
        success "Connection successful. Current IP: $ip"
        return 0
    else
        error "Connection test failed"
        return 1
    fi
}

rotate_identity() {
    log "Rotating Tor identity..."
    
    if curl --socks5-hostname localhost:9050 --connect-timeout 10 http://httpbin.org/ip &> /dev/null; then
        # Use control port to signal new identity
        echo -e "AUTHENTICATE \"$(jq -r .control_password $CONFIG_FILE)\"\r\nSIGNAL NEWNYM\r\nQUIT" | \
            nc localhost 9051 > /dev/null 2>&1 && \
        success "Identity rotated successfully" || \
        error "Identity rotation failed"
    else
        error "Cannot rotate identity - Tor not responding"
    fi
}

start_anonymizer() {
    log "Starting Tor Anonymizer..."
    
    if check_tor_service && test_connection; then
        source venv/bin/activate
        python3 tor_anonymizer.py
    else
        error "Failed to start Tor Anonymizer"
        exit 1
    fi
}

stop_anonymizer() {
    log "Stopping Tor Anonymizer..."
    
    pkill -f "python3 tor_anonymizer.py" || true
    success "Tor Anonymizer stopped"
}

status_check() {
    log "Checking service status..."
    
    if pgrep -f "python3 tor_anonymizer.py" > /dev/null; then
        success "Tor Anonymizer is running"
    else
        warning "Tor Anonymizer is not running"
    fi
    
    if pgrep -x "tor" > /dev/null; then
        success "Tor service is running"
        test_connection
    else
        error "Tor service is not running"
    fi
}

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start Tor Anonymizer"
    echo "  stop      - Stop Tor Anonymizer"
    echo "  status    - Check service status"
    echo "  install   - Install dependencies"
    echo "  test      - Test Tor connection"
    echo "  rotate    - Rotate Tor identity"
    echo "  help      - Show this help message"
    echo ""
}

main() {
    print_banner
    
    local command=${1:-help}
    
    case $command in
        start)
            check_dependencies
            setup_environment
            install_python_deps
            start_anonymizer
            ;;
        stop)
            stop_anonymizer
            ;;
        status)
            status_check
            ;;
        install)
            check_dependencies
            setup_environment
            install_python_deps
            ;;
        test)
            check_tor_service
            test_connection
            ;;
        rotate)
            rotate_identity
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
