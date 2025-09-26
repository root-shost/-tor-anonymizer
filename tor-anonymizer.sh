#!/bin/bash

# TOR Anonymizer Launcher v2.0.1
# Advanced IP Rotation every 10 seconds
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
readonly PID_FILE="${SCRIPT_DIR}/tor_anonymizer.pid"

print_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║                   TOR ANONYMIZER v2.0.1                      ║
║         Ultimate Privacy Tool with Fast IP Rotation          ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
║                                                              ║
║           🔄 IP Rotation: Every 10 seconds                   ║
║           🌐 Multiple Circuits: Active                       ║
║           🔒 Enhanced Security: Enabled                      ║
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
    local deps=("python3" "curl" "tor")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        info "Install with: sudo apt install tor curl python3 python3-pip"
        return 1
    fi
    success "All dependencies available"
}

check_tor_connection() {
    log "Testing Tor connection and IP rotation..."
    
    local initial_ip
    local new_ip
    local rotation_detected=false
    
    # Get initial IP
    initial_ip=$(curl --socks5-hostname localhost:9050 --max-time 10 -s http://icanhazip.com 2>/dev/null || echo "Unknown")
    info "Initial IP: $initial_ip"
    
    # Wait for rotation (15 seconds to be safe)
    info "Waiting for IP rotation (15 seconds)..."
    sleep 15
    
    # Get new IP
    new_ip=$(curl --socks5-hostname localhost:9050 --max-time 10 -s http://icanhazip.com 2>/dev/null || echo "Unknown")
    info "New IP after rotation: $new_ip"
    
    if [[ "$initial_ip" != "$new_ip" ]] && [[ "$initial_ip" != "Unknown" ]] && [[ "$new_ip" != "Unknown" ]]; then
        success "✅ IP rotation working correctly!"
        info "IP changed from: $initial_ip to: $new_ip"
        rotation_detected=true
    else
        warning "⚠️  IP rotation not detected or same IP"
    fi
    
    # Test Tor project validation
    if curl --socks5-hostname localhost:9050 --max-time 10 -s https://check.torproject.org/ | grep -q "Congratulations"; then
        success "✅ Tor connection verified by torproject.org"
    else
        warning "⚠️  Tor project check inconclusive"
    fi
    
    return 0
}

setup_environment() {
    log "Setting up environment..."
    mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data" "${SCRIPT_DIR}/monitoring"
    
    # Create default config if missing
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warning "Creating default configuration with 10-second IP rotation..."
        python3 -c "
import json
config = {
    'tor_port': 9050,
    'control_port': 9051,
    'identity_rotation_interval': 10,
    'max_retries': 3,
    'timeout': 30,
    'auto_start_tor': True,
    'fast_rotation_mode': True,
    'rotation_strategy': 'time_based',
    'min_rotation_interval': 10,
    'max_rotation_interval': 300
}
with open('settings.json', 'w') as f:
    json.dump(config, f, indent=4)
print('Default config with 10-second rotation created')
"
    fi
    
    # Create default torrc if missing
    if [[ ! -f "${SCRIPT_DIR}/torrc" ]]; then
        cat > "${SCRIPT_DIR}/torrc" << 'TORRC'
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0
MaxCircuitDirtiness 10
NewCircuitPeriod 15
MaxClientCircuitsPending 32
CircuitBuildTimeout 10
LearnCircuitBuildTimeout 0
TORRC
        info "Default torrc configuration created"
    fi
}

show_status() {
    local current_ip
    local rotation_count=0
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            success "Tor Anonymizer is RUNNING (PID: $pid)"
            
            # Try to get rotation count from logs
            if [[ -f "$LOG_FILE" ]]; then
                rotation_count=$(grep -c "Tor identity renewed successfully" "$LOG_FILE" 2>/dev/null || echo 0)
                info "Total IP rotations: $rotation_count"
            fi
        else
            error "Tor Anonymizer is STOPPED (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        error "Tor Anonymizer is STOPPED"
    fi
    
    # Test current connection
    if current_ip=$(curl --socks5-hostname localhost:9050 --max-time 5 -s http://icanhazip.com 2>/dev/null); then
        success "✅ Tor proxy: socks5://127.0.0.1:9050"
        info "Current Tor IP: $current_ip"
        info "Rotation interval: 10 seconds"
        info "Next rotation in: ~$((10 - ($(date +%s) % 10))) seconds"
    else
        warning "❌ Tor proxy not responding"
    fi
}

start_service() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            warning "Tor Anonymizer is already running (PID: $pid)"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    log "Starting Tor Anonymizer with 10-second IP rotation..."
    
    # Ensure Python virtual environment is activated if exists
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        info "Using Python virtual environment"
    fi
    
    # Start the service
    nohup python3 tor_anonymizer.py >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    sleep 3
    if kill -0 "$pid" 2>/dev/null; then
        success "Tor Anonymizer started (PID: $pid)"
        info "Log file: $LOG_FILE"
        info "PID file: $PID_FILE"
        
        # Wait a bit and test connection
        sleep 5
        if check_tor_connection; then
            success "✅ Service started successfully with IP rotation"
        else
            warning "⚠️  Service started but connection test had issues"
        fi
    else
        error "❌ Failed to start Tor Anonymizer"
        error "Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_service() {
    log "Stopping Tor Anonymizer..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 3
            
            if kill -0 "$pid" 2>/dev/null; then
                warning "Forcing shutdown..."
                kill -9 "$pid"
                sleep 1
            fi
            
            rm -f "$PID_FILE"
            success "Tor Anonymizer stopped"
        else
            error "Process not running, removing stale PID file"
            rm -f "$PID_FILE"
        fi
    else
        warning "No PID file found, attempting to stop by process name..."
        pkill -f "python3.*tor_anonymizer.py" || true
    fi
    
    # Stop any Tor processes started by the tool
    if [[ -f "${SCRIPT_DIR}/torrc" ]]; then
        pkill -f "tor -f ${SCRIPT_DIR}/torrc" || true
    fi
}

restart_service() {
    stop_service
    sleep 2
    start_service
}

show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        info "Showing last 20 lines of log file. Press Ctrl+C to exit."
        tail -n 20 "$LOG_FILE"
        echo
        info "Following logs in real-time..."
        tail -f "$LOG_FILE"
    else
        error "Log file not found: $LOG_FILE"
    fi
}

monitor_service() {
    log "Starting real-time monitoring..."
    
    local iteration=0
    while true; do
        clear
        print_banner
        echo
        
        # Show status
        show_status
        echo
        
        # Show recent log entries
        info "Recent activity:"
        tail -n 5 "$LOG_FILE" 2>/dev/null | while read line; do
            echo "  📝 $line"
        done
        
        echo
        info "Monitoring refresh: 5 seconds | Iteration: $iteration"
        info "Press Ctrl+C to stop monitoring"
        
        sleep 5
        iteration=$((iteration + 1))
    done
}

run_test() {
    log "Running comprehensive test suite..."
    
    echo
    info "1. Testing dependencies..."
    if check_dependencies; then
        success "✅ Dependencies test passed"
    else
        error "❌ Dependencies test failed"
        return 1
    fi
    
    echo
    info "2. Testing Tor connection and IP rotation..."
    if check_tor_connection; then
        success "✅ Connection test passed"
    else
        error "❌ Connection test failed"
        return 1
    fi
    
    echo
    info "3. Testing Python module..."
    if python3 tor_anonymizer.py --test 2>/dev/null; then
        success "✅ Python module test passed"
    else
        error "❌ Python module test failed"
        return 1
    fi
    
    echo
    success "🎉 All tests completed successfully!"
}

usage() {
    echo -e "${PURPLE}Tor Anonymizer Management Script v2.0.1${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|monitor|test|install|clean}"
    echo
    echo "Commands:"
    echo "  start    - Start the Tor Anonymizer service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
    echo "  status   - Show service status and current IP"
    echo "  logs     - Show and follow log file"
    echo "  monitor  - Real-time monitoring dashboard"
    echo "  test     - Run comprehensive tests"
    echo "  install  - Install dependencies"
    echo "  clean    - Clean logs and data"
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
    
    # Install system dependencies
    if command -v apt-get &> /dev/null; then
        info "Installing system dependencies via apt..."
        sudo apt update
        sudo apt install -y tor curl python3 python3-pip
    elif command -v yum &> /dev/null; then
        info "Installing system dependencies via yum..."
        sudo yum install -y tor curl python3 python3-pip
    else
        warning "Cannot detect package manager. Please install Tor manually."
    fi
    
    success "All dependencies installed"
}

clean_environment() {
    log "Cleaning environment..."
    
    stop_service
    
    # Remove generated files
    rm -rf "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data" "${SCRIPT_DIR}/__pycache__"
    rm -f "${SCRIPT_DIR}/torrc" "${SCRIPT_DIR}/tor_anonymizer.pid"
    
    # Recreate necessary directories
    mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data"
    
    success "Environment cleaned"
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
        monitor)
            monitor_service
            ;;
        test)
            check_dependencies && setup_environment && run_test
            ;;
        install)
            install_dependencies
            ;;
        clean)
            clean_environment
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
