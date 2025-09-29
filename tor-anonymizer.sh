#!/bin/bash
# TOR ANONYMIZER LAUNCHER v3.0.2 - COMPLETE ENTERPRISE VERSION

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
readonly PYTHON_SCRIPT="${SCRIPT_DIR}/tor_anonymizer.py"

# Enhanced logging
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }
info() { echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }

print_banner() {
    echo -e "${PURPLE}"
    cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v3.0.2                 ║
║                   ENTERPRISE STEALTH MODE                    ║
║                                                              ║
║          🔒 All Enterprise Features Active                   ║
║          🌐 Complete Stealth Protection                      ║
║          🛡️  Advanced Threat Prevention                     ║
║          📊 Real-time Monitoring & Analytics                 ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
}

check_dependencies() {
    log "Checking enterprise dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 not found"
        missing_deps+=("python3")
    else
        info "Python3: $(python3 --version 2>&1)"
    fi
    
    # Check Tor
    if ! command -v tor &> /dev/null; then
        error "Tor not found in PATH"
        missing_deps+=("tor")
    else
        info "Tor: $(tor --version 2>&1 | head -n1)"
    fi
    
    # Check Python dependencies
    if ! python3 -c "import requests, stem, psutil" &> /dev/null; then
        warning "Some Python dependencies missing"
        info "Installing dependencies from requirements.txt..."
        pip3 install -r requirements.txt 2>/dev/null || {
            error "Failed to install Python dependencies"
            missing_deps+=("python-deps")
        }
    else
        success "Python dependencies verified"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

check_tor_service() {
    log "Checking Tor service status..."
    
    # Check if Tor port is listening
    if netstat -tuln 2>/dev/null | grep -q ":9050.*LISTEN"; then
        success "Tor port 9050 is listening"
        return 0
    fi
    
    # Check systemd service
    if systemctl is-active --quiet tor 2>/dev/null; then
        success "Tor service is running (systemd)"
        return 0
    fi
    
    # Check process
    if pgrep -x tor > /dev/null; then
        success "Tor process is running"
        return 0
    fi
    
    warning "Tor service not detected"
    return 1
}

start_tor_service() {
    log "Starting Tor service..."
    
    if command -v sudo > /dev/null; then
        if sudo systemctl start tor 2>/dev/null; then
            success "Tor service started via systemctl"
            return 0
        fi
        
        if sudo service tor start 2>/dev/null; then
            success "Tor service started via service"
            return 0
        fi
    fi
    
    # Fallback: start Tor directly
    warning "Attempting to start Tor directly..."
    tor --runasdaemon 1 2>/dev/null && {
        success "Tor started directly"
        return 0
    }
    
    error "Failed to start Tor service"
    return 1
}

wait_for_tor() {
    log "Waiting for Tor to be ready..."
    local max_wait=30
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if curl --socks5 127.0.0.1:9050 -s http://httpbin.org/ip > /dev/null 2>&1; then
            success "Tor network is ready"
            return 0
        fi
        sleep 1
        ((wait_time++))
    done
    
    error "Tor network connection timeout"
    return 1
}

get_pid() {
    pgrep -f "python3.*tor_anonymizer.py" 2>/dev/null | head -1
}

check_status() {
    local pid=$(get_pid)
    
    if [ -n "$pid" ]; then
        success "Enterprise Tor Anonymizer is RUNNING (PID: $pid)"
        
        # Show additional info
        if [ -f "$LOG_FILE" ]; then
            local rotations=$(grep -c "identity rotation" "$LOG_FILE" 2>/dev/null || echo "0")
            info "Rotations performed: $rotations"
        fi
        
        # Test Tor connectivity
        if curl --socks5 127.0.0.1:9050 -s http://httpbin.org/ip > /dev/null 2>&1; then
            local current_ip=$(curl --socks5 127.0.0.1:9050 -s http://icanhazip.com)
            success "Tor Proxy: socks5://127.0.0.1:9050"
            info "Current IP: $current_ip"
        else
            warning "Tor connectivity test failed"
        fi
        
        return 0
    else
        error "Enterprise Tor Anonymizer is STOPPED"
        return 1
    fi
}

start_service() {
    log "Starting Ultimate Enterprise Tor Anonymizer..."
    
    # Check if already running
    if get_pid > /dev/null; then
        warning "Service is already running"
        check_status
        return 0
    fi
    
    # Run pre-flight checks
    if ! check_dependencies; then
        error "Dependency check failed"
        return 1
    fi
    
    # Ensure Tor is running
    if ! check_tor_service; then
        warning "Tor service not running, attempting to start..."
        if ! start_tor_service; then
            error "Cannot start Tor automatically"
            info "Please start Tor manually: sudo systemctl start tor"
            return 1
        fi
    fi
    
    # Wait for Tor network
    if ! wait_for_tor; then
        error "Tor network not ready"
        return 1
    fi
    
    # Start the enterprise service
    log "Launching enterprise stealth mode..."
    cd "$SCRIPT_DIR"
    
    if nohup python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 & then
        local pid=$!
        sleep 3
        
        if get_pid > /dev/null; then
            success "Ultimate Enterprise Tor Anonymizer started successfully"
            info "Log file: $LOG_FILE"
            
            # Show initial status
            sleep 2
            check_status
            return 0
        else
            error "Process started but terminated immediately"
            if [ -f "$LOG_FILE" ]; then
                error "Last errors from log:"
                tail -10 "$LOG_FILE" | while read line; do
                    error "  $line"
                done
            fi
            return 1
        fi
    else
        error "Failed to start enterprise service"
        return 1
    fi
}

stop_service() {
    log "Stopping Enterprise Tor Anonymizer..."
    
    local pid=$(get_pid)
    
    if [ -n "$pid" ]; then
        # Graceful shutdown first
        if kill -TERM "$pid" 2>/dev/null; then
            log "Sent termination signal to process $pid"
            
            # Wait for graceful shutdown
            local max_wait=10
            local wait_time=0
            
            while [ $wait_time -lt $max_wait ]; do
                if ! get_pid > /dev/null; then
                    break
                fi
                sleep 1
                ((wait_time++))
            done
            
            # Force kill if still running
            if get_pid > /dev/null; then
                warning "Process did not terminate gracefully, forcing..."
                kill -KILL "$pid" 2>/dev/null
                sleep 2
            fi
        fi
        
        # Verify process is gone
        if ! get_pid > /dev/null; then
            success "Enterprise service stopped successfully"
        else
            error "Failed to stop process"
            return 1
        fi
    else
        warning "No running enterprise service found"
    fi
    
    return 0
}

restart_service() {
    log "Restarting Enterprise Tor Anonymizer..."
    
    if stop_service; then
        sleep 3
        if start_service; then
            success "Enterprise service restarted successfully"
            return 0
        else
            error "Failed to restart enterprise service"
            return 1
        fi
    else
        error "Failed to stop service for restart"
        return 1
    fi
}

show_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        error "Log file not found: $LOG_FILE"
        return 1
    fi
    
    log "Showing enterprise logs (Ctrl+C to exit)..."
    tail -f "$LOG_FILE"
}

run_tests() {
    log "Running enterprise test suite..."
    
    if python3 "$PYTHON_SCRIPT" --test; then
        success "Enterprise test suite completed successfully"
    else
        error "Enterprise test suite failed"
        return 1
    fi
}

emergency_stop() {
    log "🚨 EMERGENCY STOP INITIATED!"
    
    # Immediate process termination
    pkill -9 -f "python3.*tor_anonymizer.py" 2>/dev/null || true
    sleep 2
    
    # Verify shutdown
    if get_pid > /dev/null; then
        error "Emergency stop failed - processes still running"
        return 1
    else
        success "Emergency stop completed"
        return 0
    fi
}

show_usage() {
    echo -e "${PURPLE}Ultimate Enterprise Tor Anonymizer Management Script v3.0.2${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|test|emergency-stop|help}"
    echo
    echo "Enterprise Service Commands:"
    echo "  start           - Start enterprise service with all features"
    echo "  stop            - Stop enterprise service gracefully"
    echo "  restart         - Restart enterprise service"
    echo "  status          - Show enterprise status and IP information"
    echo "  logs            - Tail enterprise log file in real-time"
    echo "  test            - Run enterprise test suite"
    echo "  emergency-stop  - Immediate emergency shutdown"
    echo
    echo "Enterprise Features:"
    echo "  ✅ Dummy Traffic Generation"
    echo "  ✅ Real-time Traffic Monitoring"
    echo "  ✅ Automatic Circuit Rotation"
    echo "  ✅ Kill Switch Protection"
    echo "  ✅ Advanced Fingerprint Protection"
    echo
    echo "Examples:"
    echo "  $0 start      # Start enterprise stealth mode"
    echo "  $0 status     # Check service status and current IP"
    echo "  $0 logs       # Monitor enterprise logs"
    echo "  $0 test       # Run comprehensive tests"
}

main() {
    local command="${1:-help}"
    
    print_banner
    
    case "$command" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        test)
            run_tests
            ;;
        emergency-stop)
            emergency_stop
            ;;
        help|--help|-h|"")
            show_usage
            ;;
        *)
            error "Unknown command: $command"
            show_usage
            return 1
            ;;
    esac
}

# Run main function
main "$@"
