#!/bin/bash

# =============================================================================
# TOR ANONYMIZER - Ultimate Privacy Tool
# GitHub Repository: https://github.com/root-shost/tor-anonymizer
# Version: 2.0
# Author: Andrea Filippo Mongelli
# =============================================================================

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funzioni di utilità
print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   TOR ANONYMIZER v2.0                        ║"
    echo "║                 Ultimate Privacy Tool                        ║"
    echo "║                                                              ║"
    echo "║    GitHub: https://github.com/tuo-repo/tor-anonymizer        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Funzione per verificare i permessi root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_status "Script eseguito come root"
    else
        print_error "Questo script richiede permessi root!"
        echo "Usage: sudo ./tor-anonymizer.sh"
        exit 1
    fi
}

# Funzione per verificare le dipendenze
check_dependencies() {
    local deps=("tor" "curl" "proxychains" "nyx" "nc")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v $dep &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_warning "Dipendenze mancanti: ${missing[*]}"
        read -p "Vuoi installarle automaticamente? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            print_error "Installa manualmente le dipendenze prima di continuare"
            exit 1
        fi
    fi
}

install_dependencies() {
    print_info "Installazione dipendenze..."
    apt update
    apt install -y tor curl proxychains nyx netcat
    print_status "Dipendenze installate"
}

# Configurazione Tor
configure_tor() {
    print_info "Configurazione Tor in corso..."
    
    # Backup configurazione originale
    if [ -f "/etc/tor/torrc" ]; then
        cp /etc/tor/torrc /etc/tor/torrc.backup.$(date +%Y%m%d_%H%M%S)
        print_status "Backup config creato: /etc/tor/torrc.backup"
    fi
    
    # Configurazione ultra-rapida
    cat > /etc/tor/torrc << 'TOR_CONFIG'
# =============================================================================
# TOR ANONYMIZER Configuration - Ultra Fast IP Rotation
# Generated automatically by tor-anonymizer.sh
# =============================================================================

# Basic Settings
SocksPort 9050
ControlPort 9051
RunAsDaemon 1
DataDirectory /var/lib/tor
Log notice file /var/log/tor/notices.log
User debian-tor

# Security
SafeLogging 1
SocksPolicy accept 127.0.0.1
SocksPolicy reject *

# Authentication for IP Rotation
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1

# Ultra-Fast IP Rotation (10 seconds)
MaxCircuitDirtiness 10
CircuitBuildTimeout 10
LearnCircuitBuildTimeout 0
NewCircuitPeriod 10

# Performance
MaxClientCircuitsPending 32
MaxMemInQueues 256 MB
AvoidDiskWrites 0

# Exit Policy
ExitPolicy accept *:*

# Stream Isolation
SocksPort 9052 IsolateDestAddr IsolateDestPort IsolateClientProtocol

# Hidden Services (Optional)
#HiddenServiceDir /var/lib/tor/hidden_service/
#HiddenServicePort 80 127.0.0.1:8080
TOR_CONFIG

    # Fix permessi
    chown -R debian-tor:debian-tor /var/lib/tor 2>/dev/null
    chmod 700 /var/lib/tor 2>/dev/null
    
    mkdir -p /var/log/tor
    chown debian-tor:debian-tor /var/log/tor 2>/dev/null
    
    print_status "Configurazione Tor completata"
}

# Funzioni di servizio
start_tor() {
    print_info "Avvio Tor..."
    systemctl stop tor 2>/dev/null
    pkill tor 2>/dev/null
    systemctl start tor
    sleep 5
    
    if systemctl is-active --quiet tor; then
        print_status "Tor avviato correttamente"
        show_current_ip
    else
        print_error "Impossibile avviare Tor"
        return 1
    fi
}

stop_tor() {
    print_info "Arresto Tor..."
    systemctl stop tor 2>/dev/null
    pkill tor 2>/dev/null
    print_status "Tor arrestato"
}

restart_tor() {
    stop_tor
    start_tor
}

show_current_ip() {
    local ip=$(curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org 2>/dev/null)
    if [ -n "$ip" ]; then
        print_status "IP corrente: $ip"
        return 0
    else
        print_error "Impossibile ottenere l'IP"
        return 1
    fi
}

change_ip() {
    print_info "Cambio IP in corso..."
    
    if [ -r "/var/lib/tor/control_auth_cookie" ]; then
        local cookie=$(xxd -p -c 32 /var/lib/tor/control_auth_cookie 2>/dev/null)
        if [ -n "$cookie" ]; then
            echo -e "authenticate ${cookie}\nsignal newnym\nquit" | nc 127.0.0.1 9051 2>/dev/null
            if [ $? -eq 0 ]; then
                print_status "IP cambiato con successo (autenticazione)"
            else
                print_warning "Riavvio Tor per cambio IP..."
                restart_tor
            fi
        fi
    else
        print_warning "Riavvio Tor per cambio IP..."
        restart_tor
    fi
    
    sleep 3
    show_current_ip
}

start_anonymous_browser() {
    print_info "Avvio browser anonimo..."
    
    if ! show_current_ip; then
        print_error "Tor non è attivo. Avvio prima Tor..."
        start_tor
    fi
    
    # Crea script temporaneo per browser
    local browser_script="/tmp/tor-browser-$$.sh"
    cat > $browser_script << 'BROWSER_SCRIPT'
#!/bin/bash
echo "🌐 Browser Anonimo Attivo - IP cambia ogni 30 secondi"
echo "🔒 Tutto il traffico passa attraverso Tor"
echo "⏹️  Chiudi questa finestra per fermare"

while true; do
    IP=$(curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org 2>/dev/null)
    echo "🕐 $(date '+%H:%M:%S') - IP: $IP"
    sleep 30
done
BROWSER_SCRIPT

    chmod +x $browser_script
    
    # Avvia Firefox attraverso Tor
    print_info "Avvio Firefox in modalità anonima..."
    sudo -u kali proxychains firefox --new-window https://check.torproject.org 2>/dev/null &
    
    # Avvia monitoraggio IP
    gnome-terminal -- $browser_script 2>/dev/null ||
    xterm -e $browser_script 2>/dev/null ||
    echo "Apri manualmente un terminale ed esegui: $browser_script"
    
    print_status "Browser anonimo avviato"
}

monitor_tor() {
    print_info "Avvio monitoraggio Tor..."
    if command -v nyx &> /dev/null; then
        nyx -i 127.0.0.1:9051
    else
        print_error "Nyx non installato. Installalo con: apt install nyx"
        show_tor_status
    fi
}

show_tor_status() {
    print_info "Stato sistema Tor:"
    echo "----------------------------------------"
    
    # Stato servizio
    if systemctl is-active --quiet tor; then
        echo -e "Servizio Tor: ${GREEN}ATTIVO${NC}"
    else
        echo -e "Servizio Tor: ${RED}INATTIVO${NC}"
    fi
    
    # Porte in ascolto
    echo -e "\nPorte in ascolto:"
    netstat -tlnp 2>/dev/null | grep 905 | while read line; do
        echo "  $line"
    done || echo "  Nessuna porta Tor in ascolto"
    
    # IP corrente
    echo -e "\nConnessione Tor:"
    if show_current_ip; then
        echo -e "Stato: ${GREEN}FUNZIONANTE${NC}"
    else
        echo -e "Stato: ${RED}NON FUNZIONANTE${NC}"
    fi
    
    # Processi attivi
    echo -e "\nProcessi Tor attivi:"
    ps aux | grep tor | grep -v grep | while read line; do
        echo "  $line"
    done || echo "  Nessun processo Tor attivo"
}

auto_ip_changer() {
    print_info "Avvio cambio IP automatico ogni 10 secondi..."
    echo "Questo processo continuerà fino a Ctrl+C"
    echo "----------------------------------------"
    
    local count=0
    while true; do
        count=$((count + 1))
        change_ip
        echo "Ciclo completato: $count - Prossimo cambio tra 10 secondi..."
        echo "----------------------------------------"
        sleep 10
    done
}

# Menu principale
show_menu() {
    print_banner
    echo -e "${CYAN}Scegli un'opzione:${NC}"
    echo -e "  ${GREEN}1${NC}) 📦 Installazione e Configurazione Completa"
    echo -e "  ${GREEN}2${NC}) 🚀 Avvia Tor"
    echo -e "  ${GREEN}3${NC}) ⏹️  Arresta Tor"
    echo -e "  ${GREEN}4${NC}) 🔄 Riavvia Tor"
    echo -e "  ${GREEN}5${NC}) 🌐 Cambia IP (Nuova Identità)"
    echo -e "  ${GREEN}6${NC}) 🔄 Cambio IP Automatico (10 secondi)"
    echo -e "  ${GREEN}7${NC}) 🌐 Browser Anonimo"
    echo -e "  ${GREEN}8${NC}) 📊 Monitoraggio Tor (Nyx)"
    echo -e "  ${GREEN}9${NC}) 📋 Stato Sistema"
    echo -e "  ${GREEN}0${NC}) ❌ Esci"
    echo
    echo -e "${YELLOW}IP Attuale:${NC} $(curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org 2>/dev/null || echo 'Non disponibile')"
    echo
}

# Gestione menu
main_menu() {
    while true; do
        show_menu
        read -p "Seleziona un'opzione (0-9): " choice
        
        case $choice in
            1)
                print_info "Installazione completa..."
                check_dependencies
                configure_tor
                start_tor
                ;;
            2)
                start_tor
                ;;
            3)
                stop_tor
                ;;
            4)
                restart_tor
                ;;
            5)
                change_ip
                ;;
            6)
                auto_ip_changer
                ;;
            7)
                start_anonymous_browser
                ;;
            8)
                monitor_tor
                ;;
            9)
                show_tor_status
                ;;
            0)
                print_info "Arrivederci! 👋"
                exit 0
                ;;
            *)
                print_error "Opzione non valida!"
                ;;
        esac
        
        echo
        read -p "Premi Enter per continuare..."
    done
}

# Gestione segnali
trap 'print_info "Script interrotto. Arrivederci!"; exit 0' INT TERM

# Main execution
main() {
    check_root
    check_dependencies
    
    # Se passato parametro, esegui direttamente
    case "$1" in
        "install")
            configure_tor
            start_tor
            ;;
        "start")
            start_tor
            ;;
        "stop")
            stop_tor
            ;;
        "restart")
            restart_tor
            ;;
        "status")
            show_tor_status
            ;;
        "changeip")
            change_ip
            ;;
        "browser")
            start_anonymous_browser
            ;;
        "monitor")
            monitor_tor
            ;;
        *)
            main_menu
            ;;
    esac
}

# Avvio script
main "$@"
EOF

sudo chmod +x /usr/local/bin/tor-anonymizer.sh
