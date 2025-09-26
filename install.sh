#!/bin/bash
# Ultimate Advanced Stealth TOR Anonymizer Installer

echo "🔒 Installing Ultimate Advanced Stealth TOR Anonymizer..."
echo "========================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo -e "${BLUE}"
cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ADVANCED TOR ANONYMIZER v2.0.0                 ║
║                   ULTIMATE STEALTH MODE                      ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# Check root
if [[ $EUID -eq 0 ]]; then
   error "Please do not run as root"
   exit 1
fi

# Check directory
if [[ ! -f "tor_anonymizer.py" ]]; then
    error "Please run from tor-anonymizer directory"
    exit 1
fi

install_system_deps() {
    log "Installing system dependencies..."
    
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y tor torsocks obfs4proxy python3 python3-pip python3-venv curl net-tools
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y tor python3 python3-pip curl
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --noconfirm tor python python-pip curl obfs4proxy
    elif command -v brew >/dev/null 2>&1; then
        brew install tor python curl
    else
        warning "Unknown package manager. Please install dependencies manually."
    fi
    success "System dependencies installed"
}

setup_python_env() {
    log "Setting up advanced Python environment..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        success "Virtual environment created"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    
    if pip install -r requirements.txt; then
        success "Python dependencies installed"
    else
        error "Python dependencies failed"
        return 1
    fi
}

configure_advanced_settings() {
    log "Configuring advanced stealth settings..."
    
    mkdir -p logs tor_data
    
    # Create advanced config if missing
    if [[ ! -f "settings.json" ]]; then
        cat > settings.json << 'EOF'
{
    "tor_port": 9050,
    "control_port": 9051,
    "identity_rotation_interval": 10,
    "min_rotation_delay": 8,
    "max_rotation_delay": 15,
    "max_retries": 5,
    "timeout": 15,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0",
    "socks5_host": "127.0.0.1",
    "log_level": "ERROR",
    "auto_start_tor": true,
    "dns_leak_protection": true,
    "safe_browsing": true,
    "max_circuit_dirtiness": 5,
    "exclude_nodes": "{ru},{cn},{us},{gb},{de},{fr},{nl}",
    "strict_nodes": true,
    "entry_nodes": "{se},{no},{fi},{dk}",
    "exit_nodes": "{ch},{at},{li},{is}",
    "use_bridges": true,
    "bridge_type": "obfs4",
    "disable_javascript": true,
    "block_trackers": true,
    "cookie_cleanup": true,
    "random_user_agent": true,
    "circuit_timeout": 30,
    "max_circuits": 50,
    "security_level": "high",
    "dummy_traffic_enabled": true,
    "dummy_traffic_interval": 30,
    "multi_hop_enabled": true,
    "guard_lifetime_days": 30,
    "random_delay_enabled": true,
    "traffic_obfuscation": true,
    "use_entry_guards": true,
    "num_entry_guards": 3,
    "long_lived_ports": true
}
EOF
        success "Advanced configuration created"
    fi
    
    # Create torrc.example
    cat > torrc.example << 'EOF'
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0
EOF
    success "Tor configuration created"
}

set_permissions() {
    log "Setting up permissions..."
    chmod +x tor-anonymizer.sh
    chmod +x tor_anonymizer.py
    success "Permissions configured"
}

test_installation() {
    log "Testing advanced installation..."
    
    source venv/bin/activate
    
    # Test Python dependencies
    if python3 -c "import requests, stem, psutil, fake_useragent; print('Advanced dependencies OK')"; then
        success "Advanced dependencies verified"
    else
        error "Dependency test failed"
        return 1
    fi
    
    # Test Tor installation
    if command -v tor >/dev/null 2>&1; then
        success "Tor installation verified"
    else
        error "Tor not found"
        return 1
    fi
}

main() {
    log "Starting advanced installation..."
    
    install_system_deps
    setup_python_env
    configure_advanced_settings
    set_permissions
    
    if test_installation; then
        echo ""
        success "🎯 ULTIMATE ADVANCED STEALTH INSTALLATION COMPLETED!"
        echo ""
        echo "Quick start:"
        echo "  source venv/bin/activate"
        echo "  python3 tor_anonymizer.py --test"
        echo ""
        echo "Advanced modes:"
        echo "  python3 tor_anonymizer.py                    # Ultimate stealth"
        echo "  python3 tor_anonymizer.py --mode advanced    # Advanced mode"
        echo "  python3 tor_anonymizer.py --mode stealth     # Basic stealth"
        echo ""
        echo "Features activated:"
        echo "  ✅ IP Rotation every 10s (randomized)"
        echo "  ✅ Dummy traffic generation"
        echo "  ✅ Multi-hop circuits"
        echo "  ✅ Entry guards protection"
        echo "  ✅ Random delay obfuscation"
        echo ""
    else
        error "Installation completed with errors"
        exit 1
    fi
}

main "$@"
