#!/bin/bash
#
# TOR Anonymizer - Bash Wrapper
# Author: root-shost
# GitHub: https://github.com/root-shost/-tor-anonymizer
# Version: 2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/src/tor_anonymizer.py"
CONFIG_DIR="$SCRIPT_DIR/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

check_dependencies() {
    local deps=("python3" "tor" "curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            print_error "Missing dependency: $dep"
            exit 1
        fi
    done
}

show_help() {
    echo "TOR Anonymizer v2.0 - by root-shost"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --install     Install and configure Tor"
    echo "  --start       Start Tor service"
    echo "  --stop        Stop Tor service"
    echo "  --change-ip   Change IP address"
    echo "  --status      Show current status"
    echo "  --help        Show this help message"
    echo ""
}

main() {
    case "${1:-}" in
        "--install")
            check_root
            python3 "$PYTHON_SCRIPT"
            ;;
        "--start")
            check_root
            systemctl start tor
            print_success "Tor service started"
            ;;
        "--stop")
            check_root
            systemctl stop tor
            print_success "Tor service stopped"
            ;;
        "--change-ip")
            check_root
            print_status "Changing IP address..."
            ;;
        "--status")
            if curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org; then
                print_success "Tor is running"
            else
                print_error "Tor is not running"
            fi
            ;;
        "--help"|"-h")
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
