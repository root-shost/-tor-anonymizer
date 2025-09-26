#!/bin/bash
# TOR Anonymizer - Auto Installer Script
set -euo pipefail

echo "🔧 TOR Anonymizer Auto-Installer"
echo "=================================="

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
║                   TOR ANONYMIZER v2.0.0                      ║
║                       Ultimate Privacy Tool                  ║
║                                                              ║
║          Author: root-shost                                  ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# Check if we're in the right directory
if [[ ! -f "tor_anonymizer.py" ]]; then
    error "Please run this script from the tor-anonymizer directory"
    exit 1
fi

# Function to install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    # Check OS and install Tor
    if command -v apt-get >/dev/null 2>&1; then
        # Debian/Ubuntu/Kali
        sudo apt-get update
        sudo apt-get install -y tor torsocks python3 python3-pip python3-venv curl
    elif command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        sudo yum install -y tor python3 python3-pip curl
    elif command -v pacman >/dev/null 2>&1; then
        # Arch
        sudo pacman -S --noconfirm tor python python-pip curl
    elif command -v brew >/dev/null 2>&1; then
        # macOS
        brew install tor python curl
    else
        warning "Cannot detect package manager. Please install Tor manually."
        return 1
    fi
    success "System dependencies installed"
}

# Function to setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log "Installing Python packages..."
        pip install -r requirements.txt
        success "Python dependencies installed"
    else
        error "requirements.txt not found"
        return 1
    fi
}

# Function to configure Tor
configure_tor() {
    log "Configuring Tor..."
    
    # Create necessary directories
    mkdir -p logs tor_data
    
    # Create default settings.json if missing
    if [[ ! -f "settings.json" ]]; then
        cat > settings.json << 'EOF'
{
    "tor_port": 9050,
    "control_port": 9051,
    "identity_rotation_interval": 300,
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "socks5_host": "127.0.0.1",
    "log_level": "INFO",
    "auto_start_tor": true,
    "dns_leak_protection": true,
    "safe_browsing": true
}
EOF
        success "Default configuration created"
    fi
    
    # Create torrc.example if missing
    if [[ ! -f "torrc.example" ]]; then
        cat > torrc.example << 'EOF'
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0
EOF
        success "Tor configuration example created"
    fi
}

# Function to test installation
test_installation() {
    log "Testing installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Python script
    if python3 -c "import requests, stem, psutil; print('Python dependencies OK')" 2>/dev/null; then
        success "Python dependencies verified"
    else
        error "Python dependencies test failed"
        return 1
    fi
    
    # Test Tor installation
    if command -v tor >/dev/null 2>&1; then
        success "Tor is installed"
    else
        error "Tor is not installed"
        return 1
    fi
    
    # Make script executable
    chmod +x tor-anonymizer.sh
    success "Script permissions set"
}

# Function to start Tor service
start_tor_service() {
    log "Starting Tor service..."
    
    # Stop any existing Tor processes
    sudo systemctl stop tor 2>/dev/null || true
    pkill -f "tor" 2>/dev/null || true
    
    # Start Tor with our configuration
    if [[ -f "torrc.example" ]]; then
        tor -f torrc.example &
        TOR_PID=$!
        echo $TOR_PID > tor.pid
        sleep 5
        
        if kill -0 $TOR_PID 2>/dev/null; then
            success "Tor service started (PID: $TOR_PID)"
        else
            error "Failed to start Tor service"
            return 1
        fi
    else
        error "Tor configuration not found"
        return 1
    fi
}

# Main installation process
main() {
    log "Starting installation process..."
    
    # Install system dependencies
    if ! install_system_deps; then
        warning "System dependency installation had issues, continuing..."
    fi
    
    # Setup Python environment
    if ! setup_python_env; then
        error "Python environment setup failed"
        exit 1
    fi
    
    # Configure Tor
    configure_tor
    
    # Test installation
    if ! test_installation; then
        error "Installation test failed"
        exit 1
    fi
    
    # Start Tor service
    if start_tor_service; then
        success "Tor service started successfully"
    else
        warning "Tor service startup had issues, but installation completed"
    fi
    
    echo ""
    success "🎯 TOR Anonymizer installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Test the installation: ./tor-anonymizer.sh test"
    echo "2. Start the service: ./tor-anonymizer.sh start"
    echo "3. Check status: ./tor-anonymizer.sh status"
    echo ""
    echo "Quick test:"
    echo "  source venv/bin/activate && python3 tor_anonymizer.py --test"
    echo ""
}

# Run main function
main "$@"
