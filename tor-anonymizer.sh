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

print_enterprise_banner() {
    echo -e "${PURPLE}"
    cat << "ENTERPRISE_BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v3.0.0                 ║
║                   ENTERPRISE STEALTH MODE                    ║
║                                                              ║
║          🔒 Multi-Layer Protection                          ║
║          🌐 Enterprise Grade Anonymity                      ║
║          🛡️  Advanced Threat Prevention                     ║
║          📊 Real-time Monitoring                            ║
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

# Enterprise functions
setup_enterprise_environment() {
    log "Setting up enterprise environment..."
    
    mkdir -p "${SCRIPT_DIR}/logs" "${TOR_DATA_DIR}" "${BACKUP_DIR}"
    
    # Create enterprise directory structure
    local dirs=("logs" "tor_data" "backups" "configs" "cache")
    for dir in "${dirs[@]}"; do
        mkdir -p "${SCRIPT_DIR}/${dir}"
    done
    
    # Set secure permissions
    chmod 700 "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/tor_data"
    chmod 600 "${LOG_FILE}" 2>/dev/null || true
    
    success "Enterprise environment configured"
}

activate_enterprise_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        source "$VENV_DIR/bin/activate"
        return 0
    else
        error "Enterprise virtual environment not found. Run ./INSTALL.sh first."
        return 1
    fi
}

check_enterprise_installation() {
    if [[ ! -d "$VENV_DIR" ]]; then
        error "Enterprise installation incomplete. Please run: ./INSTALL.sh"
        return 1
    fi
    
    if [[ ! -f "settings.json" ]]; then
        error "Enterprise configuration missing. Please run: ./INSTALL.sh"
        return 1
    fi
    
    # Check for enterprise dependencies
    local missing_deps=()
    for dep in python3 tor curl netstat; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing enterprise dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

check_enterprise_tor_connection() {
    log "Testing enterprise Tor connection..."
    
    local test_services=(
        "https://check.torproject.org"
        "http://httpbin.org/ip"
        "http://icanhazip.com"
    )
    
    for service in "${test_services[@]}"; do
        if curl --socks5-hostname localhost:9050 --max-time 10 --retry 2 -s "$service" &>/dev/null; then
            success "Enterprise Tor connection verified: $service"
            return 0
        fi
    done
    
    # Advanced fallback test
    if netstat -tuln 2>/dev/null | grep -q ":9050"; then
        warning "Tor port 9050 listening but connection tests failed"
        return 1
    else
        error "Enterprise Tor connection completely failed"
        return 1
    fi
}

enterprise_security_audit() {
    log "Running enterprise security audit..."
    
    local audit_passed=0
    local audit_total=0
    
    # Audit 1: File permissions
    ((audit_total++))
    if [[ $(stat -c %a "$SCRIPT_DIR" 2>/dev/null) -le 755 ]]; then
        ((audit_passed++))
        info "Directory permissions: OK"
    else
        security_alert "Insecure directory permissions"
    fi
    
    # Audit 2: Tor process
    ((audit_total++))
    if pgrep -x tor &>/dev/null; then
        ((audit_passed++))
        info "Tor process: RUNNING"
    else
        security_alert "Tor process not running"
    fi
    
    # Audit 3: Network isolation
    ((audit_total++))
    if ! netstat -tuln 2>/dev/null | grep -q -E ":(80|443|53).*LISTEN"; then
        ((audit_passed++))
        info "Network isolation: OK"
    else
        security_alert "Potential network isolation issue"
    fi
    
    success "Enterprise security audit: $audit_passed/$audit_total passed"
}

start_enterprise_service() {
    if ! check_enterprise_installation; then
        return 1
    fi
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Enterprise Tor Anonymizer is already running"
        show_enterprise_status
        return 0
    fi
    
    log "Starting Enterprise Tor Anonymizer..."
    
    # Force enterprise virtual environment activation
    if ! activate_enterprise_venv; then
        error "Failed to activate enterprise virtual environment"
        return 1
    fi
    
    # Enterprise security audit
    enterprise_security_audit
    
    # Check enterprise Tor connection
    if ! check_enterprise_tor_connection; then
        warning "Enterprise Tor not running. Attempting advanced startup..."
        sudo systemctl start tor 2>/dev/null || true
        sleep 8
    fi
    
    # Start the enterprise application
    log "Launching Enterprise Tor Anonymizer..."
    if nohup python3 tor_anonymizer.py --mode enterprise >> "$LOG_FILE" 2>&1 & then
        local pid=$!
        sleep 8
        
        if kill -0 "$pid" 2>/dev/null; then
            success "Enterprise Tor Anonymizer started (PID: $pid)"
            info "Enterprise Log file: $LOG_FILE"
            info "Security Audit log: $SECURITY_LOG"
            
            # Monitor startup
            sleep 3
            show_enterprise_status
            return 0
        else
            error "Enterprise process died immediately. Check logs: $LOG_FILE"
            if [[ -f "$LOG_FILE" ]]; then
                error "Last enterprise errors from log:"
                tail -15 "$LOG_FILE" | while read line; do
                    error "  $line"
                done
            fi
            return 1
        fi
    else
        error "Failed to start Enterprise Tor Anonymizer"
        return 1
    fi
}

stop_enterprise_service() {
    log "Stopping Enterprise Tor Anonymizer..."
    
    # Graceful shutdown
    pkill -f "python3.*tor_anonymizer.py" || true
    sleep 3
    
    # Forceful shutdown if needed
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        warning "Enterprise graceful shutdown failed, forcing..."
        pkill -9 -f "python3.*tor_anonymizer.py" || true
        sleep 2
    fi
    
    # Verify shutdown
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        error "Enterprise shutdown failed - process still running"
        return 1
    else
        success "Enterprise Tor Anonymizer stopped"
        return 0
    fi
}

restart_enterprise_service() {
    log "Restarting Enterprise Tor Anonymizer..."
    stop_enterprise_service
    sleep 5
    start_enterprise_service
}

show_enterprise_status() {
    log "Enterprise Service Status Check..."
    
    local status="STOPPED"
    local color="$RED"
    local pid=""
    
    if pgrep -f "python3.*tor_anonymizer.py" > /dev/null; then
        status="RUNNING"
        color="$GREEN"
        pid=$(pgrep -f "python3.*tor_anonymizer.py")
    fi
    
    echo -e "   Service Status: ${color}${status}${NC}"
    
    if [[ -n "$pid" ]]; then
        echo -e "   Process PID: $pid"
        echo -e "   Log File: $LOG_FILE"
    fi
    
    # Enterprise Tor connection status
    if check_enterprise_tor_connection; then
        local current_ip
        current_ip=$(curl --socks5-hostname localhost:9050 -s http://icanhazip.com 2>/dev/null || echo "Unknown")
        echo -e "   Tor Proxy: ${GREEN}socks5://127.0.0.1:9050${NC}"
        echo -e "   Current IP: ${GREEN}$current_ip${NC}"
    else
        echo -e "   Tor Proxy: ${RED}NOT AVAILABLE${NC}"
    fi
    
    # Enterprise security status
    enterprise_security_audit
}

show_enterprise_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        log "Displaying enterprise logs (Ctrl+C to exit)..."
        tail -f "$LOG_FILE"
    else
        error "Enterprise log file not found: $LOG_FILE"
        info "No enterprise logs available yet. Start the service first."
    fi
}

show_security_logs() {
    if [[ -f "$SECURITY_LOG" ]]; then
        log "Displaying security audit logs..."
        tail -50 "$SECURITY_LOG"
    else
        warning "Security audit log not found: $SECURITY_LOG"
    fi
}

run_enterprise_test() {
    log "Running enterprise comprehensive test..."
    
    if ! check_enterprise_installation; then
        return 1
    fi
    
    activate_enterprise_venv
    
    echo "=== ENTERPRISE TEST SUITE ==="
    
    # Test 1: Tor connection
    if check_enterprise_tor_connection; then
        success "Enterprise Tor connection: OK"
    else
        error "Enterprise Tor connection: FAILED"
    fi
    
    # Test 2: Python module
    if python3 tor_anonymizer.py --test; then
        success "Enterprise Python module: OK"
    else
        error "Enterprise Python module: FAILED"
    fi
    
    # Test 3: Security audit
    enterprise_security_audit
    
    success "Enterprise test suite completed"
}

enterprise_emergency_stop() {
    log "🚨 ENTERPRISE EMERGENCY STOP INITIATED!"
    
    # Immediate process termination
    pkill -9 -f "python3.*tor_anonymizer.py" 2>/dev/null || true
    pkill -9 -x tor 2>/dev/null || true
    
    # Clear caches
    rm -rf "${TOR_DATA_DIR}"/* 2>/dev/null || true
    
    # Backup logs
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$LOG_FILE" "${BACKUP_DIR}/emergency_log_${backup_timestamp}.log" 2>/dev/null || true
    
    success "Enterprise emergency stop completed"
}

enterprise_ultimate_mode() {
    if ! check_enterprise_installation; then
        return 1
    fi
    
    log "Starting ULTIMATE ENTERPRISE STEALTH mode..."
    activate_enterprise_venv
    
    python3 tor_anonymizer.py --mode enterprise
}

enterprise_advanced_mode() {
    if ! check_enterprise_installation; then
        return 1
    fi
    
    log "Starting ADVANCED ENTERPRISE mode..."
    activate_enterprise_venv
    
    python3 tor_anonymizer.py --mode advanced
}

enterprise_stealth_mode() {
    if ! check_enterprise_installation; then
        return 1
    fi
    
    log "Starting ENTERPRISE STEALTH mode..."
    activate_enterprise_venv
    
    python3 tor_anonymizer.py --mode stealth
}

enterprise_install_dependencies() {
    log "Running enterprise installation..."
    
    if [[ -f "INSTALL.sh" ]]; then
        chmod +x INSTALL.sh
        ./INSTALL.sh
    else
        error "ENTERPRISE INSTALL.sh not found. Please download the complete repository."
        return 1
    fi
}

enterprise_update() {
    log "Checking for enterprise updates..."
    
    # Backup current configuration
    if [[ -f "settings.json" ]]; then
        cp "settings.json" "settings.json.backup.$(date +%Y%m%d)"
        success "Enterprise configuration backed up"
    fi
    
    # Placeholder for update logic
    warning "Enterprise update system in development"
    info "Manual update recommended: git pull && ./INSTALL.sh"
}

enterprise_usage() {
    echo -e "${PURPLE}Ultimate Enterprise Tor Anonymizer Management Script v3.0.0${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|security-logs|test|install|update|emergency-stop}"
    echo "       {ultimate|advanced|stealth|help}"
    echo
    echo "Enterprise Service Commands:"
    echo "  start           - Start enterprise service"
    echo "  stop            - Stop enterprise service"
    echo "  restart         - Restart enterprise service"
    echo "  status          - Enterprise status check"
    echo "  logs            - Tail enterprise log file"
    echo "  security-logs   - View security audit logs"
    echo "  test            - Run enterprise test suite"
    echo "  install         - Enterprise installation"
    echo "  update          - Check for updates"
    echo "  emergency-stop  - Immediate emergency shutdown"
    echo
    echo "Enterprise Stealth Modes:"
    echo "  ultimate        - Ultimate enterprise stealth (IP rotation every 10s)"
    echo "  advanced        - Advanced enterprise mode"
    echo "  stealth         - Basic enterprise stealth"
    echo
    echo "Enterprise Quick Start:"
    echo "  $0 install      # Enterprise installation"
    echo "  $0 ultimate     # Ultimate enterprise mode"
    echo "  $0 status       # Enterprise status check"
    echo
}

# Main enterprise function
enterprise_main() {
    local command=${1:-help}
    
    print_enterprise_banner
    setup_enterprise_environment
    
    case $command in
        start)
            check_enterprise_installation && start_enterprise_service
            ;;
        stop)
            stop_enterprise_service
            ;;
        restart)
            check_enterprise_installation && restart_enterprise_service
            ;;
        status)
            show_enterprise_status
            ;;
        logs)
            show_enterprise_logs
            ;;
        security-logs)
            show_security_logs
            ;;
        test)
            check_enterprise_installation && run_enterprise_test
            ;;
        install)
            enterprise_install_dependencies
            ;;
        update)
            enterprise_update
            ;;
        emergency-stop)
            enterprise_emergency_stop
            ;;
        ultimate)
            enterprise_ultimate_mode
            ;;
        advanced)
            enterprise_advanced_mode
            ;;
        stealth)
            enterprise_stealth_mode
            ;;
        help|--help|-h|"")
            enterprise_usage
            ;;
        *)
            error "Unknown enterprise command: $command"
            enterprise_usage
            exit 1
            ;;
    esac
}

# Run enterprise main function
enterprise_main "$@"
