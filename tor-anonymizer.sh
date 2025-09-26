#!/bin/bash

# TOR Anonymizer Launcher v2.0.0
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

check_dependencies() {
    log "Checking dependencies..."
    local deps=("python3" "curl")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        return 1
    fi
    success "All dependencies available"
}

check_tor_connection() {
    log "Testing Tor connection..."
    if curl --socks5-hostname localhost:9050 --max-time 10 -s https://check.torproject.org/ | grep -q "Congratulations"; then
        success "Tor connection successful"
        return 0
    elif curl --socks5-hostname localhost:9050 --max-time 10 -s http://httpbin.org/ip &>/dev/null; then
        warning "Tor connected but torproject check failed"
        return 0
    else
        warning "Tor not responding on port 9050"
        return 1
    fi
}

setup_environment() {
    log "Setting up environment..."
    mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data"
    
    # Create default config if missing
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warning "Creating default configuration..."
        python3 -c "
import json
config = {
    'tor_port': 9050,
    'control_port': 9051,
    'identity_rotation_interval': 300,
    'max_retries': 3,
    'timeout': 30,
    'auto_start_tor': True
}
with open('settings.json', 'w') as f:
    json.dump(config, f, indent=4)
print('Default config created')
"
    fi
    
    # Check if Tor is installed
    if ! command -v tor &> /dev/null; then
        warning "Tor is not installed. The tool will try to use system Tor if available."
        info "To install Tor: sudo apt install tor"
    fi
}

show_status() {
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        success "Tor Anonymizer is RUNNING"
        info "Check logs: tail -f logs/tor_anonymizer.log"
    else
        error "Tor Anonymizer is STOPPED"
    fi
    
    if check_tor_connection; then
        info "Tor proxy: socks5://127.0.0.1:9050"
        
        # Show current IP through Tor
        local current_ip=$(curl --socks5-hostname localhost:9050 -s http://icanhazip.com 2>/dev/null || echo "Unknown")
        info "Current Tor IP: $current_ip"
    else
        warning "Tor proxy not available"
    fi
}

start_service() {
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Tor Anonymizer is already running"
        return 0
    fi
    
    log "Starting Tor Anonymizer..."
    
    # Ensure Python virtual environment is activated if exists
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        info "Using Python virtual environment"
    fi
    
    nohup python3 tor_anonymizer.py >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    sleep 5
    if kill -0 "$pid" 2>/dev/null; then
        success "Tor Anonymizer started (PID: $pid)"
        info "Log file: $LOG_FILE"
        
        # Wait a bit and test connection
        sleep 3
        if check_tor_connection; then
            success "Service started successfully"
        else
            warning "Service started but Tor connection test failed"
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
        sleep 1
    fi
    
    # Stop any Tor processes started by the tool
    if [[ -f "torrc" ]]; then
        pkill -f "tor -f torrc" || true
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
    fi
}

run_test() {
    log "Running comprehensive test..."
    
    if check_tor_connection; then
        success "Tor connection: OK"
    else
        error "Tor connection: FAILED"
    fi
    
    # Test Python script directly
    if python3 tor_anonymizer.py --test; then
        success "Python module test: OK"
    else
        error "Python module test: FAILED"
    fi
}

usage() {
    echo -e "${PURPLE}Tor Anonymizer Management Script${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|test|install}"
    echo
    echo "Commands:"
    echo "  start    - Start the Tor Anonymizer service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
    echo "  status   - Show service status"
    echo "  logs     - Tail log file"
    echo "  test     - Run comprehensive tests"
    echo "  install  - Install dependencies"
    echo
}

install_dependencies() {
    log "Installing dependencies..."
    
    # Check if we're in a virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        warning "Not in a virtual environment. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Install Python dependencies
    if pip install -r requirements.txt; then
        success "Python dependencies installed"
    else
        error "Failed to install Python dependencies"
        return 1
    fi
    
    # Check system dependencies
    if ! command -v tor &> /dev/null; then
        warning "Tor is not installed. You may need to install it manually:"
        info "Debian/Ubuntu: sudo apt install tor"
        info "CentOS/RHEL: sudo yum install tor"
        info "Arch: sudo pacman -S tor"
    else
        success "Tor is installed"
    fi
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
print_banner
main "$@"
