#!/bin/bash
# TOR Anonymizer Launcher v2.0.0 - Advanced Version
set -euo pipefail

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="${SCRIPT_DIR}/settings.json"
readonly LOG_FILE="${SCRIPT_DIR}/logs/tor_anonymizer.log"
readonly VENV_DIR="${SCRIPT_DIR}/venv"

print_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║                   TOR ANONYMIZER v2.0.0                      ║
║                       Ultimate Privacy Tool                  ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
}

log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }

activate_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        source "$VENV_DIR/bin/activate"
        return 0
    else
        warning "Virtual environment not found. Run ./INSTALL.sh first."
        return 1
    fi
}

check_installation() {
    if [[ ! -d "$VENV_DIR" ]]; then
        error "Installation incomplete. Please run: ./INSTALL.sh"
        return 1
    fi
    
    if [[ ! -f "settings.json" ]]; then
        error "Configuration missing. Please run: ./INSTALL.sh"
        return 1
    fi
    
    return 0
}

check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python3 not found. Please run: ./INSTALL.sh"
        return 1
    fi
    
    if ! command -v tor &> /dev/null; then
        warning "Tor not found. The tool will try to install it automatically."
        return 1
    fi
    
    success "Dependencies verified"
}

check_tor_connection() {
    log "Testing Tor connection..."
    
    if curl --socks5-hostname localhost:9050 --max-time 10 -s https://check.torproject.org/ | grep -q "Congratulations"; then
        success "Tor connection verified by torproject.org"
        return 0
    elif curl --socks5-hostname localhost:9050 --max-time 10 -s http://httpbin.org/ip &>/dev/null; then
        success "Tor connection successful (basic test)"
        return 0
    elif netstat -tuln 2>/dev/null | grep -q ":9050"; then
        warning "Tor port 9050 is listening but connection test failed"
        return 1
    else
        warning "Tor not responding on port 9050"
        return 1
    fi
}

setup_environment() {
    log "Setting up environment..."
    mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warning "Creating default configuration..."
        cat > "$CONFIG_FILE" << 'EOF'
{
    "tor_port": 9050,
    "control_port": 9051,
    "identity_rotation_interval": 300,
    "max_retries": 3,
    "timeout": 30,
    "auto_start_tor": true
}
EOF
        success "Default configuration created"
    fi
}

show_status() {
    log "Checking service status..."
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        success "Tor Anonymizer is RUNNING"
        info "Check logs: tail -f logs/tor_anonymizer.log"
    else
        error "Tor Anonymizer is STOPPED"
    fi
    
    if check_tor_connection; then
        info "Tor proxy: socks5://127.0.0.1:9050"
        local current_ip
        current_ip=$(curl --socks5-hostname localhost:9050 -s http://icanhazip.com 2>/dev/null || echo "Unknown")
        info "Current Tor IP: $current_ip"
    else
        warning "Tor proxy not available"
    fi
}

start_service() {
    if ! check_installation; then
        return 1
    fi
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Tor Anonymizer is already running"
        return 0
    fi
    
    log "Starting Tor Anonymizer..."
    
    if ! activate_venv; then
        return 1
    fi
    
    if ! check_tor_connection; then
        warning "Tor not running. Attempting to start..."
        sudo systemctl start tor 2>/dev/null || true
        sleep 3
        
        if ! check_tor_connection; then
            log "Starting built-in Tor service..."
            tor -f torrc.example 2>/dev/null &
            sleep 5
        fi
    fi
    
    nohup python3 tor_anonymizer.py >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    sleep 3
    if kill -0 "$pid" 2>/dev/null; then
        success "Tor Anonymizer started (PID: $pid)"
        info "Log file: $LOG_FILE"
        
        sleep 2
        if check_tor_connection; then
            success "Service started successfully"
        else
            warning "Service started but Tor connection needs verification"
        fi
    else
        error "Failed to start Tor Anonymizer"
        error "Check logs: $LOG_FILE"
        return 1
    fi
}

stop_service() {
    log "Stopping Tor Anonymizer..."
    
    pkill -f "python3.*tor_anonymizer.py" || true
    sleep 2
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Forcing shutdown..."
        pkill -9 -f "python3.*tor_anonymizer.py" || true
    fi
    
    if [[ -f "tor.pid" ]]; then
        kill "$(cat tor.pid)" 2>/dev/null || true
        rm -f tor.pid
    fi
    
    success "Tor Anonymizer stopped"
}

restart_service() {
    stop_service
    sleep 2
    start_service
}

show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        tail -f "$LOG_FILE"
    else
        error "Log file not found: $LOG_FILE"
        info "No logs available yet. Start the service first."
    fi
}

run_test() {
    log "Running comprehensive test..."
    
    if check_tor_connection; then
        success "Tor connection: OK"
    else
        error "Tor connection: FAILED"
    fi
    
    log "Testing Python module..."
    if python3 tor_anonymizer.py --test; then
        success "Python module test: OK"
    else
        error "Python module test: FAILED"
    fi
    
    log "Testing basic functionality..."
    if python3 -c "
import requests
proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
try:
    r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
    print('✓ Basic proxy test: OK')
except Exception as e:
    print('✗ Basic proxy test: FAILED')
"; then
        success "Basic functionality: OK"
    else
        error "Basic functionality: FAILED"
    fi
}

install_dependencies() {
    log "Running full installation..."
    
    if [[ -f "INSTALL.sh" ]]; then
        chmod +x INSTALL.sh
        ./INSTALL.sh
    else
        error "INSTALL.sh not found. Please download the complete repository."
        return 1
    fi
}

# === NUOVE FUNZIONI AVANZATE ===
advanced_stealth_mode() {
    if ! check_installation; then
        return 1
    fi
    
    log "Starting ULTIMATE ADVANCED STEALTH mode..."
    activate_venv
    
    python3 tor_anonymizer.py --mode ultimate
}

basic_stealth_mode() {
    if ! check_installation; then
        return 1
    fi
    
    log "Starting BASIC STEALTH mode..."
    activate_venv
    
    python3 tor_anonymizer.py --mode stealth
}

advanced_test() {
    if ! check_installation; then
        return 1
    fi
    
    log "Running ADVANCED stealth tests..."
    activate_venv
    
    python3 tor_anonymizer.py --test
}
# === FINE NUOVE FUNZIONI ===

usage() {
    echo -e "${PURPLE}Tor Anonymizer Management Script - Advanced Version${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|test|install|ultimate|advanced|test-advanced|help}"
    echo
    echo "Basic Commands:"
    echo "  start    - Start the Tor Anonymizer service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
    echo "  status   - Show service status"
    echo "  logs     - Tail log file"
    echo "  test     - Run basic tests"
    echo "  install  - Install dependencies"
    echo
    echo "Advanced Stealth Commands:"
    echo "  ultimate       - Ultimate stealth mode (IP rotation every 10s)"
    echo "  advanced       - Advanced stealth mode"
    echo "  test-advanced  - Run advanced stealth tests"
    echo
    echo "Quick start:"
    echo "  $0 install      # First time setup"
    echo "  $0 ultimate     # Ultimate stealth mode"
    echo "  $0 status       # Check status"
    echo
}

main() {
    local command=${1:-help}
    
    case $command in
        start)
            check_dependencies && setup_environment && start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_dependencies && setup_environment && restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        test)
            check_dependencies && setup_environment && run_test
            ;;
        install)
            install_dependencies
            ;;
        # === NUOVI COMANDI AVANZATI ===
        ultimate|stealth)
            advanced_stealth_mode
            ;;
        advanced)
            advanced_stealth_mode
            ;;
        test-advanced)
            advanced_test
            ;;
        # === FINE NUOVI COMANDI ===
        help|--help|-h|"")
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
print_banner
main "$@"
