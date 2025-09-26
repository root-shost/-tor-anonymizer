#!/bin/bash
#
# TOR Anonymizer - Fixed Version
# Author: root-shost
# GitHub: https://github.com/root-shost/tor-anonymizer

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/tor-anonymizer.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root: sudo $0"
    fi
}

check_dependencies() {
    local deps=("tor" "curl" "proxychains" "nyx")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Missing dependency: $dep. Install with: apt install $dep"
        fi
    done
    success "All dependencies satisfied"
}

check_tor_running() {
    if ! curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org > /dev/null 2>&1; then
        error "Tor is not running. Start with: systemctl start tor"
    fi
}

get_current_user() {
    # Get the actual desktop user, not hardcoded 'kali'
    local user=$(who | awk '{print $1}' | head -1)
    if [[ -z "$user" ]]; then
        user=$(logname 2>/dev/null || echo "root")
    fi
    echo "$user"
}

change_ip_fixed() {
    log "Changing IP address..."
    
    # Method 1: Try cookie authentication
    local cookie_file="/var/lib/tor/control_auth_cookie"
    if [[ -r "$cookie_file" ]]; then
        local cookie=$(xxd -p -c 32 "$cookie_file" 2>/dev/null)
        if [[ -n "$cookie" ]]; then
            if echo -e "authenticate $cookie\nsignal newnym\nquit" | nc 127.0.0.1 9051 2>&1 | grep -q "250"; then
                success "IP changed via authentication"
                return 0
            fi
        fi
    fi
    
    # Method 2: Restart Tor service (fallback)
    warning "Authentication failed, restarting Tor service..."
    systemctl restart tor
    sleep 5
    
    if check_tor_running; then
        success "IP changed via service restart"
        return 0
    else
        error "Failed to change IP"
        return 1
    fi
}

start_anonymous_browser_fixed() {
    local user=$(get_current_user)
    log "Starting browser for user: $user"
    
    check_tor_running
    
    if [[ "$user" == "root" ]]; then
        warning "Running as root, browser might not start properly"
        proxychains firefox --new-window https://check.torproject.org &
    else
        sudo -u "$user" proxychains firefox --new-window https://check.torproject.org &
    fi
    
    success "Browser started through Tor"
}

show_status() {
    log "Checking system status..."
    
    # Tor service
    if systemctl is-active --quiet tor; then
        success "Tor service: RUNNING"
    else
        error "Tor service: STOPPED"
    fi
    
    # Ports
    if netstat -tln | grep -q 9050; then
        success "Port 9050: LISTENING"
    else
        error "Port 9050: NOT LISTENING"
    fi
    
    # IP check
    local ip=$(curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org 2>/dev/null || echo "UNREACHABLE")
    log "Current IP: $ip"
}

install_fixed() {
    log "Starting installation..."
    check_root
    check_dependencies
    
    # Backup original config
    if [[ -f "/etc/tor/torrc" ]]; then
        cp /etc/tor/torrc /etc/tor/torrc.backup.$(date +%Y%m%d_%H%M%S)
        success "Backup created"
    fi
    
    # Create optimal configuration
    cat > /etc/tor/torrc << 'EOF'
# TOR Anonymizer Configuration - Fixed Version
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1
RunAsDaemon 1
DataDirectory /var/lib/tor
Log notice file /var/log/tor/notices.log
SafeLogging 1
ExitPolicy accept *:*
MaxCircuitDirtiness 10
CircuitBuildTimeout 10
LearnCircuitBuildTimeout 0
EOF
    
    # Fix permissions
    chown -R debian-tor:debian-tor /var/lib/tor 2>/dev/null || true
    chmod 700 /var/lib/tor 2>/dev/null || true
    
    # Start service
    systemctl enable tor
    systemctl start tor
    sleep 5
    
    if check_tor_running; then
        success "Installation completed successfully"
    else
        error "Installation completed but Tor failed to start"
    fi
}

case "${1:-}" in
    "install")
        install_fixed
        ;;
    "start-browser")
        start_anonymous_browser_fixed
        ;;
    "change-ip")
        change_ip_fixed
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {install|start-browser|change-ip|status}"
        echo "Example: sudo $0 install"
        exit 1
        ;;
esac
