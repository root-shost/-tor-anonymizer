#!/usr/bin/env python3
"""Script per fixare i problemi del tor-anonymizer"""

import json
import os
import sys
from pathlib import Path

def main():
    print("🔧 Applying fixes to tor-anonymizer...")
    
    # Fix settings.json
    print("1. Fixing settings.json...")
    config = {
        "tor_port": 9050,
        "control_port": 9051,
        "identity_rotation_interval": 300,
        "max_retries": 3,
        "timeout": 30,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
        "socks5_host": "127.0.0.1",
        "log_level": "INFO",
        "auto_start_tor": True,
        "dns_leak_protection": True,
        "safe_browsing": True,
        "max_circuit_dirtiness": 600,
        "exclude_nodes": "",
        "strict_nodes": False
    }
    
    with open('settings.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("   ✅ settings.json fixed")
    
    # Create torrc.example
    print("2. Creating torrc.example...")
    torrc = """SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0

# Security settings
SafeLogging 1
SafeSocks 1
TestSocks 1

# Exit policy (restrictive)
ExitPolicy reject *:*

# Circuit settings
MaxCircuitDirtiness 600
NewCircuitPeriod 30
MaxClientCircuitsPending 32"""
    
    with open('torrc.example', 'w') as f:
        f.write(torrc)
    print("   ✅ torrc.example created")
    
    # Create necessary directories
    print("3. Creating directories...")
    Path("logs").mkdir(exist_ok=True)
    Path("tor_data").mkdir(exist_ok=True)
    print("   ✅ Directories created")
    
    print("\n🎯 All fixes applied successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: ./tor-anonymizer.sh install")
    print("2. Test the tool: ./tor-anonymizer.sh test")
    print("3. Start the service: ./tor-anonymizer.sh start")

if __name__ == "__main__":
    main()
