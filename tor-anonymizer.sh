#!/bin/bash

# Configurazioni
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/settings.json"
LOG_FILE="$SCRIPT_DIR/tor_anonymizer.log"

# Funzione di logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Verifica dipendenze
check_dependencies() {
    local deps=("tor" "curl" "python3" "docker" "docker-compose")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log "ERRORE: $dep non installato"
            return 1
        fi
    done
    return 0
}

# Controlla servizi
check_services() {
    log "Enterprise Service Status Check..."
    
    # Controlla Tor
    if pgrep -x "tor" > /dev/null; then
        log "Service Status: RUNNING"
        log "Tor Proxy: AVAILABLE on 127.0.0.1:9050"
    else
        log "Service Status: STOPPED"
        log "Tor Proxy: NOT AVAILABLE"
    fi
}

# Avvia servizi
start_services() {
    log "Starting Enterprise Services..."
    
    # Avvia Docker compose
    if docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null; then
        log "Docker services started successfully"
    else
        log "ERROR: Failed to start Docker services"
        return 1
    fi
    
    # Attiva avvio servizi Python
    cd "$SCRIPT_DIR" && python3 -m tor_anonymizer --start
}

# Ferma servizi
stop_services() {
    log "Stopping Enterprise Services..."
    
    # Ferma Docker
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null
    
    # Ferma processi Python
    pkill -f "tor_anonymizer" || true
    
    log "All services stopped"
}

# Menu principale
show_menu() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               ULTIMATE TOR ANONYMIZER v3.0.0                 ║"
    echo "║                   ENTERPRISE STEALTH MODE                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "1) Start Anonymization Services"
    echo "2) Stop Services"
    echo "3) Check Status"
    echo "4) Test Anonymity"
    echo "5) Exit"
    echo ""
    read -p "Select option [1-5]: " choice
    
    case $choice in
        1) start_services ;;
        2) stop_services ;;
        3) check_services ;;
        4) test_anonymity ;;
        5) exit 0 ;;
        *) echo "Invalid option"; show_menu ;;
    esac
}

# Test anonimato
test_anonymity() {
    log "Running anonymity test..."
    curl --socks5 127.0.0.1:9050 -s https://check.torproject.org/ | grep -q "Congratulations"
    if [ $? -eq 0 ]; then
        log "✓ Tor anonymity test PASSED"
    else
        log "✗ Tor anonymity test FAILED"
    fi
}

# Main
main() {
    cd "$SCRIPT_DIR"
    
    if ! check_dependencies; then
        log "Please install missing dependencies first"
        log "Run: ./install.sh"
        exit 1
    fi
    
    show_menu
}

main "$@"
