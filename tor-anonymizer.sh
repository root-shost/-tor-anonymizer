#!/bin/bash
# TOR ANONYMIZER LAUNCHER v3.0.1 - ULTIMATE ENTERPRISE STEALTH MODE - FIXED

# ANSI color codes
PURPLE='\033[0;95m'
CYAN='\033[0;96m'
BLUE='\033[0;94m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
RED='\033[0;91m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
END='\033[0m'

# Script info
SCRIPT_NAME="tor-anonymizer.sh"
SCRIPT_VERSION="3.0.1"
SCRIPT_AUTHOR="root-shost"
GITHUB_URL="github.com/root-shost/tor-anonymizer"

# Configuration
TOR_ANONYMIZER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$TOR_ANONYMIZER_DIR/logs"
CONFIG_FILE="$TOR_ANONYMIZER_DIR/settings.json"
PID_FILE="$TOR_ANONYMIZER_DIR/tor-anonymizer.pid"
LOG_FILE="$LOG_DIR/tor-anonymizer.log"
SECURITY_LOG="$LOG_DIR/security-audit.log"
PYTHON_SCRIPT="$TOR_ANONYMIZER_DIR/tor_anonymizer.py"

# Create directories
mkdir -p "$LOG_DIR"

print_banner() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v3.0.1                 ║
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
EOF
    echo -e "${END}"
}

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
    
    case $level in
        "INFO") echo -e "${BLUE}[INFO]${END} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${END} $message" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${END} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${END} $message" ;;
        *) echo "$message" ;;
    esac
}

check_dependencies() {
    log_message "INFO" "Checking enterprise dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_message "ERROR" "Python3 not found. Please install: sudo apt-get install python3"
        exit 1
    fi
    
    # Check Tor
    if ! command -v tor &> /dev/null; then
        log_message "WARNING" "Tor not found. Attempting to install..."
        sudo apt-get update && sudo apt-get install -y tor || {
            log_message "ERROR" "Failed to install Tor. Please install manually: sudo apt-get install tor"
            exit 1
        }
    fi
    
    # Check Python packages
    local packages=("requests" "stem" "psutil" "socks")
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            log_message "WARNING" "Python package $package not found. Installing..."
            pip3 install "$package" || {
                log_message "ERROR" "Failed to install $package. Please install manually: pip3 install $package"
                exit 1
            }
        fi
    done
    
    log_message "SUCCESS" "All enterprise dependencies available"
}

check_tor_service() {
    log_message "INFO" "Checking Tor service status..."
    
    if systemctl is-active --quiet tor; then
        log_message "SUCCESS" "Tor service is running"
        return 0
    else
        log_message "WARNING" "Tor service is not running. Starting..."
        sudo systemctl start tor
        
        if systemctl is-active --quiet tor; then
            log_message "SUCCESS" "Tor service started successfully"
            return 0
        else
            log_message "ERROR" "Failed to start Tor service"
            return 1
        fi
    fi
}

setup_enterprise_environment() {
    log_message "INFO" "Setting up enterprise environment..."
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    
    # Set proper permissions
    chmod 755 "$TOR_ANONYMIZER_DIR"
    chmod 644 "$CONFIG_FILE" 2>/dev/null || true
    
    # Verify Python script exists
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        log_message "ERROR" "Main Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Make Python script executable
    chmod +x "$PYTHON_SCRIPT"
    
    log_message "SUCCESS" "Enterprise environment configured"
}

start_enterprise_service() {
    log_message "INFO" "Starting Enterprise Tor Anonymizer..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_message "WARNING" "Enterprise service already running (PID: $pid)"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Start the service
    python3 "$PYTHON_SCRIPT" --mode "$1" >> "$LOG_FILE" 2>&1 &
    local service_pid=$!
    
    echo "$service_pid" > "$PID_FILE"
    
    # Wait a bit and check if it's still running
    sleep 3
    if kill -0 "$service_pid" 2>/dev/null; then
        log_message "SUCCESS" "Enterprise service started (PID: $service_pid)"
        return 0
    else
        log_message "ERROR" "Enterprise service failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_enterprise_service() {
    log_message "INFO" "Stopping Enterprise Tor Anonymizer..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 2
            
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid"
                sleep 1
            fi
            
            rm -f "$PID_FILE"
            log_message "SUCCESS" "Enterprise service stopped"
        else
            rm -f "$PID_FILE"
            log_message "WARNING" "PID file existed but process was not running"
        fi
    else
        log_message "WARNING" "No PID file found - attempting to kill any running processes"
        pkill -f "python3.*tor_anonymizer.py" && log_message "SUCCESS" "Killed running processes" || log_message "INFO" "No processes found"
    fi
    
    # Ensure Tor service remains running
    sudo systemctl start tor 2>/dev/null || true
}

restart_enterprise_service() {
    log_message "INFO" "Restarting Enterprise Tor Anonymizer..."
    stop_enterprise_service
    sleep 2
    start_enterprise_service "$1"
}

check_enterprise_status() {
    log_message "INFO" "Enterprise Service Status Check..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_message "SUCCESS" "Service Status: RUNNING (PID: $pid)"
            
            # Test Tor connection
            log_message "INFO" "Testing enterprise Tor connection..."
            if python3 -c "
import requests, time
try:
    session = requests.Session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
    session.verify = False
    response = session.get('http://httpbin.org/ip', timeout=10)
    if response.status_code == 200:
        print('✅ Tor connection: ACTIVE')
        print(f'🌐 Current IP: {response.text.strip()}')
    else:
        print('⚠️ Tor connection: UNSTABLE')
except Exception as e:
    print('❌ Tor connection: FAILED')
"; then
                true
            fi
            
            return 0
        else
            rm -f "$PID_FILE"
            log_message "ERROR" "Service Status: STOPPED (stale PID file)"
            return 1
        fi
    else
        log_message "ERROR" "Service Status: STOPPED"
        return 1
    fi
}

show_enterprise_logs() {
    log_message "INFO" "Tailing enterprise log file..."
    if [[ -f "$LOG_FILE" ]]; then
        tail -f "$LOG_FILE"
    else
        log_message "WARNING" "Log file not found: $LOG_FILE"
    fi
}

show_security_logs() {
    log_message "INFO" "Showing security audit logs..."
    if [[ -f "$SECURITY_LOG" ]]; then
        cat "$SECURITY_LOG"
    else
        log_message "WARNING" "Security log file not found: $SECURITY_LOG"
    fi
}

run_enterprise_test() {
    log_message "INFO" "Running enterprise test suite..."
    
    # Test basic connectivity
    if check_tor_service; then
        log_message "SUCCESS" "Tor service test: PASSED"
    else
        log_message "ERROR" "Tor service test: FAILED"
        return 1
    fi
    
    # Test Python script
    if python3 -c "import sys; sys.path.append('$TOR_ANONYMIZER_DIR'); from tor_anonymizer import UltimateTorAnonymizer; print('✅ Python import test: PASSED')"; then
        log_message "SUCCESS" "Python import test: PASSED"
    else
        log_message "ERROR" "Python import test: FAILED"
        return 1
    fi
    
    log_message "SUCCESS" "Enterprise test suite completed"
}

install_enterprise_dependencies() {
    log_message "INFO" "Installing enterprise dependencies..."
    
    # Update system
    sudo apt-get update
    
    # Install Tor
    sudo apt-get install -y tor
    
    # Install Python packages
    pip3 install requests stem psutil PySocks fake-useragent
    
    # Configure Tor
    sudo systemctl enable tor
    sudo systemctl start tor
    
    log_message "SUCCESS" "Enterprise installation completed"
}

check_for_updates() {
    log_message "INFO" "Checking for updates..."
    # Placeholder for update check logic
    log_message "INFO" "Update check feature coming soon"
}

emergency_stop() {
    log_message "WARNING" "EMERGENCY STOP INITIATED!"
    
    # Kill all related processes
    pkill -f "python3.*tor_anonymizer.py" && log_message "INFO" "Killed Python processes" || true
    sudo systemctl stop tor && log_message "INFO" "Stopped Tor service" || true
    
    # Remove PID file
    rm -f "$PID_FILE"
    
    # Clear proxy settings
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    
    log_message "SUCCESS" "Emergency stop completed - all services terminated"
}

show_usage() {
    echo -e "${BOLD}Ultimate Enterprise Tor Anonymizer Management Script v${SCRIPT_VERSION}${END}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|security-logs|test|install|update|emergency-stop}"
    echo "       {ultimate|advanced|stealth|help}"
    echo
    echo -e "${BOLD}Enterprise Service Commands:${END}"
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
    echo -e "${BOLD}Enterprise Stealth Modes:${END}"
    echo "  ultimate        - Ultimate enterprise stealth (IP rotation every 30s)"
    echo "  advanced        - Advanced enterprise mode"
    echo "  stealth         - Basic enterprise stealth"
    echo
    echo -e "${BOLD}Enterprise Quick Start:${END}"
    echo "  $0 install      # Enterprise installation"
    echo "  $0 ultimate     # Ultimate enterprise mode"
    echo "  $0 status       # Enterprise status check"
    echo
}

# Main execution
case "${1:-}" in
    start)
        print_banner
        setup_enterprise_environment
        check_dependencies
        check_tor_service
        start_enterprise_service "${2:-enterprise}"
        ;;
    stop)
        print_banner
        setup_enterprise_environment
        stop_enterprise_service
        ;;
    restart)
        print_banner
        setup_enterprise_environment
        check_dependencies
        check_tor_service
        restart_enterprise_service "${2:-enterprise}"
        ;;
    status)
        print_banner
        setup_enterprise_environment
        check_enterprise_status
        ;;
    logs)
        setup_enterprise_environment
        show_enterprise_logs
        ;;
    security-logs)
        setup_enterprise_environment
        show_security_logs
        ;;
    test)
        print_banner
        setup_enterprise_environment
        run_enterprise_test
        ;;
    install)
        print_banner
        install_enterprise_dependencies
        ;;
    update)
        print_banner
        check_for_updates
        ;;
    emergency-stop)
        print_banner
        emergency_stop
        ;;
    ultimate|advanced|stealth)
        print_banner
        setup_enterprise_environment
        check_dependencies
        check_tor_service
        start_enterprise_service "$1"
        ;;
    help|--help|-h)
        print_banner
        show_usage
        ;;
    *)
        print_banner
        setup_enterprise_environment
        show_usage
        ;;
esac
