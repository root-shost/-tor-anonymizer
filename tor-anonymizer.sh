#!/bin/bash
# TOR ANONYMIZER LAUNCHER v3.0 - ULTIMATE ENTERPRISE VERSION
set -euo pipefail

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly ORANGE='\033[0;33m'
readonly NC='\033[0m'

# Enterprise Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="${SCRIPT_DIR}/settings.json"
readonly LOG_FILE="${SCRIPT_DIR}/logs/tor_anonymizer.log"
readonly SECURITY_LOG="${SCRIPT_DIR}/logs/security_audit.log"
readonly VENV_DIR="${SCRIPT_DIR}/venv"
readonly TOR_DATA_DIR="${SCRIPT_DIR}/tor_data"
readonly BACKUP_DIR="${SCRIPT_DIR}/backups"
readonly TORRC_FILE="${SCRIPT_DIR}/torrc.enterprise"
readonly PID_FILE="${SCRIPT_DIR}/tor_anonymizer.pid"

print_enterprise_banner() {
    echo -e "${PURPLE}"
    cat << "ENTERPRISE_BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v3.0.0                 ║
║                   ENTERPRISE STEALTH MODE                    ║
║                                                              ║
║          🔒 Multi-Layer Protection                           ║
║          🌐 Enterprise Grade Anonymity                       ║
║          🛡️  Advanced Threat Prevention                      ║
║          📊 Real-time Monitoring                             ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
ENTERPRISE_BANNER
    echo -e "${NC}"
}

# Enhanced logging functions
log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ENTERPRISE ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2; }
warning() { echo -e "${YELLOW}[ENTERPRISE WARNING]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}[ENTERPRISE SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }
info() { echo -e "${CYAN}[ENTERPRISE INFO]${NC} $1" | tee -a "$LOG_FILE"; }
security_alert() { echo -e "${ORANGE}[SECURITY ALERT]${NC} $1" | tee -a "$SECURITY_LOG"; }

# Tor management functions
stop_tor() {
    log "Stopping any existing Tor processes..."
    
    # Stop using PID file
    if [[ -f "${SCRIPT_DIR}/tor.pid" ]]; then
        local tor_pid=$(cat "${SCRIPT_DIR}/tor.pid")
        kill "$tor_pid" 2>/dev/null || true
        rm -f "${SCRIPT_DIR}/tor.pid"
    fi
    
    # Kill any remaining Tor processes
    pkill -f "tor.*9050" 2>/dev/null || true
    pkill -x tor 2>/dev/null || true
    pkill -f "tor.*enterprise" 2>/dev/null || true
    
    # Additional cleanup
    sleep 2
    if pgrep -x tor >/dev/null; then
        warning "Forcing Tor shutdown..."
        pkill -9 -x tor 2>/dev/null || true
    fi
    
    success "Tor service stopped"
}

start_tor() {
    log "Starting Enterprise Tor service..."
    
    # Stop any existing Tor processes first
    stop_tor
    
    # Create Tor data directory
    mkdir -p "$TOR_DATA_DIR"
    
    # Start Tor with enterprise configuration
    local tor_command
    if [[ -f "$TORRC_FILE" ]]; then
        tor_command="tor -f \"$TORRC_FILE\" --DataDirectory \"$TOR_DATA_DIR\""
    else
        tor_command="tor --SocksPort 9050 --ControlPort 9051 --CookieAuthentication 1 --DataDirectory \"$TOR_DATA_DIR\""
    fi
    
    eval "$tor_command > \"${SCRIPT_DIR}/logs/tor.log\" 2>&1 &"
    local tor_pid=$!
    echo "$tor_pid" > "${SCRIPT_DIR}/tor.pid"
    
    # Wait for Tor to start
    local max_wait=30
    local wait_time=0
    
    while [[ $wait_time -lt $max_wait ]]; do
        if netstat -tuln 2>/dev/null | grep -q ":9050"; then
            success "Enterprise Tor service started (PID: $tor_pid)"
            return 0
        fi
        sleep 1
        ((wait_time++))
    done
    
    error "Enterprise Tor service failed to start within $max_wait seconds"
    return 1
}

check_tor_connection() {
    local max_retries=5
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        if curl --socks5-hostname 127.0.0.1:9050 --max-time 10 -s \
               "http://httpbin.org/ip" > /dev/null 2>&1; then
            return 0
        fi
        ((retry_count++))
        sleep 2
    done
    
    return 1
}

get_current_ip() {
    curl --socks5-hostname 127.0.0.1:9050 --max-time 10 -s http://icanhazip.com 2>/dev/null || echo "Unknown"
}

# Enterprise functions
setup_environment() {
    log "Setting up enterprise environment..."
    
    mkdir -p "${SCRIPT_DIR}/logs" "${TOR_DATA_DIR}" "${BACKUP_DIR}"
    
    # Create enterprise directory structure
    local dirs=("logs" "tor_data" "backups" "configs" "cache")
    for dir in "${dirs[@]}"; do
        mkdir -p "${SCRIPT_DIR}/${dir}"
    done
    
    # Set secure permissions
    chmod 700 "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data" 2>/dev/null || true
    chmod 600 "$LOG_FILE" 2>/dev/null || true
    
    success "Enterprise environment configured"
}

check_installation() {
    # Check for basic dependencies
    local missing_deps=()
    for dep in python3 tor curl; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    # Check if Python script exists
    if [[ ! -f "tor_anonymizer.py" ]]; then
        error "Main Python script tor_anonymizer.py not found"
        return 1
    fi
    
    # Check if settings.json exists, create if not
    if [[ ! -f "settings.json" ]]; then
        warning "settings.json not found, creating default configuration..."
        python3 tor_anonymizer.py --test 2>/dev/null && success "Default configuration created" || warning "Configuration creation may have issues"
    fi
    
    return 0
}

security_audit() {
    log "Running enterprise security audit..."
    
    local audit_passed=0
    local audit_total=0
    
    # Audit 1: File permissions
    ((audit_total++))
    if [[ $(stat -c %a "$SCRIPT_DIR" 2>/dev/null || echo "755") -le 755 ]]; then
        ((audit_passed++))
        info "Directory permissions: OK"
    else
        security_alert "Insecure directory permissions"
    fi
    
    # Audit 2: Tor process
    ((audit_total++))
    if pgrep -f "tor.*9050" &>/dev/null; then
        ((audit_passed++))
        info "Tor process: RUNNING"
    else
        security_alert "Tor process not running"
    fi
    
    # Audit 3: Port availability
    ((audit_total++))
    if netstat -tuln 2>/dev/null | grep -q ":9050"; then
        ((audit_passed++))
        info "Tor port: LISTENING"
    else
        security_alert "Tor port not listening"
    fi
    
    # Audit 4: Python process
    ((audit_total++))
    if pgrep -f "python3.*tor_anonymizer.py" &>/dev/null; then
        ((audit_passed++))
        info "Python process: RUNNING"
    else
        security_alert "Python process not running"
    fi
    
    success "Enterprise security audit: $audit_passed/$audit_total passed"
}

start() {
    show_banner
    log "Setting up enterprise environment..."
    setup_environment
    
    if ! check_installation; then
        error "Installation check failed"
        exit 1
    fi
    
    log_success "Enterprise environment configured"
    
    log "Starting Enterprise Tor Anonymizer..."
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Enterprise Tor Anonymizer is already running"
        status
        return 0
    fi
    
    log "Starting Enterprise Tor service..."
    
    # Stop any existing processes
    stop_tor
    sleep 2
    
    # Start Tor
    if ! start_tor; then
        error "Failed to start Tor service"
        exit 1
    fi
    
    # Wait for Tor connection
    log "Waiting for Tor connection..."
    sleep 8
    
    if ! check_tor_connection; then
        error "Tor connection failed"
        stop_tor
        exit 1
    fi
    
    log_success "Tor connection verified"
    
    # Run security audit
    security_audit
    
    # Start Python application
    log "Launching Enterprise Tor Anonymizer..."
    
    # Start in background and capture PID
    python3 tor_anonymizer.py > "${SCRIPT_DIR}/logs/python_output.log" 2>&1 &
    local python_pid=$!
    echo $python_pid > "$PID_FILE"
    
    # Wait for process to stabilize
    sleep 5
    
    # Check if process is still running
    if kill -0 $python_pid 2>/dev/null; then
        success "Enterprise Tor Anonymizer started successfully (PID: $python_pid)"
        log "Check status with: $0 status"
        log "View logs with: $0 logs"
    else
        error "Python process terminated immediately"
        log "Check logs/python_output.log for details:"
        tail -20 "${SCRIPT_DIR}/logs/python_output.log" 2>/dev/null | while read line; do
            error "  $line"
        done
        stop_tor
        exit 1
    fi
}

stop() {
    show_banner
    log "Stopping Enterprise Tor Anonymizer..."
    
    # Stop Python process
    if [[ -f "$PID_FILE" ]]; then
        local python_pid=$(cat "$PID_FILE")
        kill "$python_pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
    
    # Forceful shutdown if needed
    pkill -f "python3.*tor_anonymizer.py" 2>/dev/null || true
    sleep 2
    
    # Final cleanup
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Forcing Python process shutdown..."
        pkill -9 -f "python3.*tor_anonymizer.py" 2>/dev/null || true
    fi
    
    # Stop Tor
    stop_tor
    
    # Verify shutdown
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        error "Shutdown failed - process still running"
        return 1
    else
        success "Enterprise Tor Anonymizer stopped"
        return 0
    fi
}

status() {
    show_banner
    log "Enterprise Service Status Check..."
    
    local status="STOPPED"
    local color="$RED"
    local pid=""
    
    # Check Python process
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        status="RUNNING"
        color="$GREEN"
        pid=$(pgrep -f "python3.*tor_anonymizer.py")
    fi
    
    echo -e "   Service Status: ${color}${status}${NC}"
    
    if [[ -n "$pid" ]]; then
        echo -e "   Process PID: $pid"
    fi
    
    # Check Tor status
    if pgrep -f "tor.*9050" > /dev/null; then
        local tor_pid=$(pgrep -f "tor.*9050")
        local current_ip=$(get_current_ip)
        echo -e "   Tor Proxy: ${GREEN}socks5://127.0.0.1:9050${NC}"
        echo -e "   Tor PID: $tor_pid"
        echo -e "   Current IP: ${GREEN}$current_ip${NC}"
    else
        echo -e "   Tor Proxy: ${RED}NOT AVAILABLE${NC}"
    fi
    
    # Security audit
    security_audit
}

logs() {
    show_banner
    if [[ -f "$LOG_FILE" ]]; then
        log "Displaying enterprise logs (Ctrl+C to exit)..."
        tail -f "$LOG_FILE"
    else
        error "Enterprise log file not found: $LOG_FILE"
        info "No logs available yet. Start the service first."
    fi
}

security_logs() {
    show_banner
    if [[ -f "$SECURITY_LOG" ]]; then
        log "Displaying security audit logs..."
        tail -50 "$SECURITY_LOG"
    else
        warning "Security audit log not found: $SECURITY_LOG"
    fi
}

test_connection() {
    show_banner
    log "Running enterprise connection test..."
    
    if ! check_installation; then
        return 1
    fi
    
    echo "=== ENTERPRISE CONNECTION TEST ==="
    
    # Test 1: Tor service
    if start_tor; then
        sleep 5
        if check_tor_connection; then
            success "Tor service: OK"
            local current_ip=$(get_current_ip)
            echo -e "   Current IP: ${GREEN}$current_ip${NC}"
        else
            error "Tor connection: FAILED"
        fi
        stop_tor
    else
        error "Tor startup: FAILED"
    fi
    
    # Test 2: Python script
    if python3 tor_anonymizer.py --test 2>/dev/null; then
        success "Python script: OK"
    else
        error "Python script: FAILED"
    fi
    
    success "Enterprise connection test completed"
}

emergency_stop() {
    show_banner
    log "🚨 ENTERPRISE EMERGENCY STOP INITIATED!"
    
    # Immediate process termination
    pkill -9 -f "python3.*tor_anonymizer.py" 2>/dev/null || true
    stop_tor
    
    # Clear caches
    rm -rf "${TOR_DATA_DIR}"/* 2>/dev/null || true
    
    # Backup logs
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$LOG_FILE" "${BACKUP_DIR}/emergency_log_${backup_timestamp}.log" 2>/dev/null || true
    
    success "Enterprise emergency stop completed"
}

restart() {
    log "Restarting Enterprise Tor Anonymizer..."
    stop
    sleep 3
    start
}

show_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v3.0.0                 ║
║                   ENTERPRISE STEALTH MODE                    ║
║                                                              ║
║          🔒 Multi-Layer Protection                           ║
║          🌐 Enterprise Grade Anonymity                       ║
║          🛡️  Advanced Threat Prevention                      ║
║          📊 Real-time Monitoring                             ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
}

usage() {
    echo -e "${PURPLE}Ultimate Enterprise Tor Anonymizer Management Script v3.0.0${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|security-logs|test|emergency-stop}"
    echo
    echo "Commands:"
    echo "  start           - Start enterprise service"
    echo "  stop            - Stop enterprise service"
    echo "  restart         - Restart enterprise service"
    echo "  status          - Show service status"
    echo "  logs            - Tail log file"
    echo "  security-logs   - View security logs"
    echo "  test            - Run connection test"
    echo "  emergency-stop  - Immediate emergency shutdown"
    echo
    echo "Examples:"
    echo "  $0 start        # Start the service"
    echo "  $0 status       # Check status"
    echo "  $0 logs         # View logs"
    echo
}

# Main execution
main() {
    local command=${1:-status}
    
    case $command in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        security-logs)
            security_logs
            ;;
        test)
            test_connection
            ;;
        emergency-stop)
            emergency_stop
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

# Run main function
main "$@"
