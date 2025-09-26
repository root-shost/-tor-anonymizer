#!/usr/bin/env python3
"""Script per fixare i problemi del tor-anonymizer"""

import json
import os
from pathlib import Path

def fix_settings_json():
    """Corregge il file settings.json"""
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
        "safe_browsing": True
    }
    
    with open('settings.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("✓ settings.json fixed")

def create_torrc_example():
    """Crea un torrc.example corretto"""
    torrc = """SocksPort 9050
ControlPort 9051
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log"""
    
    with open('torrc.example', 'w') as f:
        f.write(torrc)
    print("✓ torrc.example created")

if __name__ == "__main__":
    fix_settings_json()
    create_torrc_example()
    print("🎯 Fix completato! Ora il tool dovrebbe funzionare correttamente.")
