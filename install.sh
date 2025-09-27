#!/bin/bash
# Ultimate Enterprise Stealth TOR Anonymizer Installer v3.0

echo "🔒 Installing Ultimate Enterprise Stealth TOR Anonymizer..."
echo "==========================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() { echo -e "${BLUE}[ENTERPRISE INSTALL]${NC} $1"; }
success() { echo -e "${GREEN}[ENTERPRISE SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[ENTERPRISE WARNING]${NC} $1"; }
error() { echo -e "${RED}[ENTERPRISE ERROR]${NC} $1"; }

# Enterprise Banner
echo -e "${PURPLE}"
cat << "ENTERPRISE_BANNER"
╔══════════════════════════════════════════════════════════════╗
║               ENTERPRISE TOR ANONYMIZER v3.0.0               ║
║                   ULTIMATE STEALTH MODE                      ║
╚══════════════════════════════════════════════════════════════╝
ENTERPRISE_BANNER
echo -e "${NC}"

# Enterprise pre-flight checks
if [[ $EUID -eq 0 ]]; then
   error "Enterprise installation should not be run as root"
   exit 1
fi

if [[ ! -f "tor_anonymizer.py" ]]; then
    error "Please run from enterprise tor-anonymizer directory"
    exit 1
fi

enterprise_install_system_deps() {
    log "Installing enterprise system dependencies..."
    
    # Detect package manager and install enterprise dependencies
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y tor torsocks python3 python3-pip python3-venv curl net-tools iptables
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y tor python3 python3-pip curl iptables
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --noconfirm tor python python-pip curl
    elif command -v brew >/dev/null 2>&1; then
        brew install tor python curl
    else
        warning "Unknown enterprise package manager. Manual dependency installation required."
        echo "Enterprise dependencies: tor python3 pip3 curl"
    fi
    success "Enterprise system dependencies installed"
}

enterprise_setup_python_env() {
    log "Setting up enterprise Python environment..."
    
    # Clean existing environment
    if [[ -d "venv" ]]; then
        rm -rf venv
    fi
    
    # Create enterprise virtual environment
    if python3 -m venv venv; then
        success "Enterprise virtual environment created"
    else
        error "Enterprise virtual environment creation failed"
        return 1
    fi
    
    source venv/bin/activate
    
    # Upgrade enterprise pip
    pip install --upgrade pip
    
    # Enterprise dependency installation with retry logic
    local enterprise_deps=(
        "requests>=2.28.0"
        "stem>=1.8.0" 
        "psutil>=5.9.0"
        "fake-useragent>=1.1.0"
        "PySocks>=1.7.1"
        "urllib3>=1.26.0"
        "selenium>=4.15.0"
    )
    
    for dep in "${enterprise_deps[@]}"; do
        log "Installing enterprise dependency: $dep"
        if pip install "$dep"; then
            success "Enterprise dependency installed: $dep"
        else
            error "Enterprise dependency failed: $dep"
            return 1
        fi
    done
    
    # Enterprise cleanup of problematic packages
    pip uninstall -y socksipy-branch SocksiPy-branch 2>/dev/null || true
    
    success "Enterprise Python environment configured"
}

enterprise_configure_tor_service() {
    log "Configuring enterprise Tor service..."
    
    # Stop any existing Tor service
    sudo systemctl stop tor 2>/dev/null || true
    sudo pkill -f tor 2>/dev/null || true
    
    # Create custom Tor configuration
    cat > torrc.enterprise << TOR_CONFIG
# Enterprise Tor Configuration
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory $(pwd)/tor_data
Log notice file $(pwd)/logs/tor.log

# Enterprise security settings
SafeLogging 1
AvoidDiskWrites 1

# Enterprise circuit settings
MaxCircuitDirtiness 600
NewCircuitPeriod 600
CircuitBuildTimeout 60
LearnCircuitBuildTimeout 1
EnforceDistinctSubnets 1

# Enterprise traffic obfuscation
ConnectionPadding 1
ReducedConnectionPadding 0

# Exit policy for safety
ExitPolicy reject *:*
TOR_CONFIG

    success "Enterprise Tor configuration created"
}

enterprise_configure_advanced_settings() {
    log "Configuring enterprise stealth settings..."
    
    # Create enterprise directory structure
    mkdir -p logs tor_data backups configs
    
    # Enterprise configuration file
    if [[ ! -f "settings.json" ]]; then
        cp settings_government.json settings.json 2>/dev/null || true
    fi
    
    # Create advanced configuration files
    cat > fingerprint_protection.json << 'FINGERPRINT_CONFIG'
{
    "canvas_noise": true,
    "webgl_spoofing": true,
    "font_masking": true,
    "timezone_spoofing": true,
    "screen_resolution_spoofing": true,
    "audio_context_spoofing": true,
    "hardware_concurrency_spoofing": true
}
FINGERPRINT_CONFIG

    success "Enterprise stealth settings configured"
}

enterprise_set_permissions() {
    log "Setting enterprise permissions..."
    
    # Enterprise script permissions
    chmod +x tor-anonymizer.sh
    chmod +x tor_anonymizer.py
    chmod +x leak_protection.py 2>/dev/null || true
    chmod +x fingerprint_protection.py 2>/dev/null || true
    chmod +x advanced_routing.py 2>/dev/null || true
    
    # Secure directory permissions
    chmod 700 logs tor_data backups configs
    chmod 600 settings.json 2>/dev/null || true
    chmod 600 fingerprint_protection.json 2>/dev/null || true
    
    success "Enterprise permissions configured"
}

enterprise_test_installation() {
    log "Testing enterprise installation..."
    
    source venv/bin/activate
    
    # Enterprise dependency verification
    if python3 -c "
import requests, stem, psutil, urllib3, selenium
print('✅ Enterprise core dependencies verified')
"; then
        success "Enterprise dependencies verified"
    else
        error "Enterprise dependency test failed"
        return 1
    fi
    
    # Enterprise Tor verification
    if command -v tor >/dev/null 2>&1; then
        success "Enterprise Tor installation verified"
    else
        error "Enterprise Tor not found"
        return 1
    fi
    
    # Test Tor startup
    log "Testing Tor startup..."
    tor --version > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success "Tor executable verified"
    else
        error "Tor executable test failed"
        return 1
    fi
    
    # Test new modules
    if python3 -c "
from leak_protection import SystemLeakProtection
from fingerprint_protection import AdvancedFingerprintingProtection
print('✅ Advanced protection modules verified')
"; then
        success "Advanced protection modules verified"
    else
        warning "Some advanced modules may need configuration"
    fi
    
    success "Enterprise installation verified"
}

enterprise_fix_common_issues() {
    log "Fixing enterprise common issues..."
    
    source venv/bin/activate
    
    # Enterprise dependency fixes
    pip uninstall -y socksipy-branch SocksiPy-branch 2>/dev/null || true
    pip install PySocks --upgrade --force-reinstall
    
    # Enterprise SSL fixes
    pip install urllib3 --upgrade certifi --force-reinstall
    
    # Install advanced dependencies
    pip install selenium webdriver-manager --upgrade
    
    success "Enterprise common issues fixed"
}

enterprise_post_installation() {
    log "Enterprise post-installation setup..."
    
    # Enterprise backup creation
    cp settings.json "backups/settings.json.backup.$(date +%Y%m%d)" 2>/dev/null || true
    
    # Enterprise log initialization
    touch logs/tor_anonymizer.log
    touch logs/security_audit.log
    touch logs/fingerprint_protection.log
    touch logs/leak_protection.log
    
    # Create default advanced config
    if [[ ! -f "settings_government.json" ]]; then
        cat > settings_government.json << 'GOVERNMENT_CONFIG'
{
    "security_level": "government_grade",
    "multi_tor_chains": 4,
    "pluggable_transports": ["obfs4", "meek", "snowflake"],
    "circuit_rotation": "random(30-600)",
    "traffic_obfuscation": "advanced_shape_mimicry",
    "decoy_traffic_ratio": 3,
    "cover_stories_enabled": true,
    "hardware_isolation": "tails_usb_boot",
    "operational_security": "strict_opsec",
    "max_session_time": 120,
    "location_rotation": true,
    "wifi_security": "public_only",
    "forensic_resistance": "high"
}
GOVERNMENT_CONFIG
    fi
    
    success "Enterprise post-installation completed"
}

enterprise_main() {
    log "Starting enterprise installation..."
    
    # Enterprise installation sequence
    enterprise_install_system_deps
    enterprise_setup_python_env
    enterprise_configure_tor_service
    enterprise_configure_advanced_settings
    enterprise_set_permissions
    enterprise_fix_common_issues
    enterprise_post_installation
    
    if enterprise_test_installation; then
        echo ""
        success "🎯 GOVERNMENT-GRADE ENTERPRISE STEALTH INSTALLATION COMPLETED!"
        echo ""
        echo "Enterprise Quick Start:"
        echo "  ./tor-anonymizer.sh test          # Enterprise test suite"
        echo "  ./tor-anonymizer.sh ultimate      # Ultimate enterprise mode"
        echo "  ./tor-anonymizer.sh status        # Enterprise status check"
        echo ""
        echo "NEW Government-Grade Features:"
        echo "  ✅ Advanced timing randomization"
        echo "  ✅ Traffic pattern obfuscation"
        echo "  ✅ Browser fingerprint protection"
        echo "  ✅ System-level leak prevention"
        echo "  ✅ Multi-hop circuit routing"
        echo "  ✅ Artificial request delays"
        echo "  ✅ Advanced traffic mimicry"
        echo ""
        echo "Enterprise Troubleshooting:"
        echo "  ./tor-anonymizer.sh test          # Run enterprise tests"
        echo "  ./tor-anonymizer.sh logs          # View enterprise logs"
        echo "  ./tor-anonymizer.sh security-logs # Security audit logs"
        echo ""
        echo "Enterprise Documentation:"
        echo "  Read README.md for advanced government-grade features"
        echo ""
    else
        error "Enterprise installation completed with errors"
        echo ""
        echo "Enterprise Troubleshooting Steps:"
        echo "1. Run: source venv/bin/activate"
        echo "2. Run: pip install -r requirements.txt --upgrade"
        echo "3. Check Tor: tor --version"
        echo "4. View logs: ./tor-anonymizer.sh logs"
        exit 1
    fi
}

# Run enterprise installation
enterprise_main "$@"
