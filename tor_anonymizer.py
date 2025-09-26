#!/usr/bin/env python3
"""
TOR Anonymizer - Professional Privacy Tool
Author: Andrea Filippo Mongelli
GitHub: https://github.com/root-shost/-tor-anonymizer
Version: 2.0
License: MIT
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Logger:
    """Professional logging system"""
    
    def __init__(self, log_file: str = "tor-anonymizer.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, level: str, message: str) -> None:
        """Log message with timestamp and level"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        # Print to console with colors
        self._print_colored(level, message)
    
    def _print_colored(self, level: str, message: str) -> None:
        """Print colored message to console"""
        color_map = {
            'INFO': Colors.BLUE,
            'SUCCESS': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'DEBUG': Colors.CYAN
        }
        
        color = color_map.get(level.upper(), Colors.WHITE)
        print(f"{color}[{level.upper()}]{Colors.END} {message}")

class TorAnonymizer:
    """Main TOR Anonymizer class"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        self.version = "2.0"
        self.author = "root-shost"
        self.logger = Logger()
        self.config = self._load_config(config_file)
        self.is_running = False
        
        # Set default values
        self.config.setdefault('tor_socks_port', 9050)
        self.config.setdefault('tor_control_port', 9051)
        self.config.setdefault('ip_change_interval', 10)
        self.config.setdefault('max_circuit_dirtiness', 10)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.log('WARNING', f'Config file {config_file} not found, using defaults')
            return {}
        except json.JSONDecodeError as e:
            self.logger.log('ERROR', f'Invalid config file: {e}')
            return {}
    
    def print_banner(self) -> None:
        """Display professional banner"""
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                   TOR ANONYMIZER v{self.version}             ║
║                       Ultimate Privacy Tool                  ║
║                                                              ║
║          Author: {self.author}                               ║
║         GitHub: github.com/root-shost/-tor-anonymizer        ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        dependencies = ['tor', 'curl', 'proxychains', 'nyx', 'python3']
        missing = []
        
        for dep in dependencies:
            if not self._command_exists(dep):
                missing.append(dep)
        
        if missing:
            self.logger.log('WARNING', f'Missing dependencies: {", ".join(missing)}')
            return self._install_dependencies(missing)
        
        self.logger.log('SUCCESS', 'All dependencies are satisfied')
        return True
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in system"""
        try:
            subprocess.run(['which', command], check=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_dependencies(self, packages: list) -> bool:
        """Install system dependencies"""
        try:
            self.logger.log('INFO', 'Installing dependencies...')
            
            # Update package list
            subprocess.run(['apt', 'update'], check=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Install packages
            subprocess.run(['apt', 'install', '-y'] + packages, check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.logger.log('SUCCESS', 'Dependencies installed successfully')
            return True
        except subprocess.CalledProcessError as e:
            self.logger.log('ERROR', f'Failed to install dependencies: {e}')
            return False
    
    def configure_tor(self) -> bool:
        """Configure Tor with optimal settings"""
        try:
            self._backup_tor_config()
            tor_config = self._generate_tor_config()
            
            with open('/etc/tor/torrc', 'w') as f:
                f.write(tor_config)
            
            self.logger.log('SUCCESS', 'Tor configuration applied successfully')
            return True
        except Exception as e:
            self.logger.log('ERROR', f'Configuration failed: {e}')
            return False
    
    def _generate_tor_config(self) -> str:
        """Generate optimal Tor configuration"""
        return f"""# TOR Anonymizer Configuration
# Generated by root-shost
# GitHub: https://github.com/root-shost/-tor-anonymizer

# Basic Settings
SocksPort {self.config['tor_socks_port']}
ControlPort {self.config['tor_control_port']}
RunAsDaemon 1
DataDirectory /var/lib/tor
Log notice file /var/log/tor/notices.log

# Security & Privacy
SafeLogging 1
SocksPolicy accept 127.0.0.1
SocksPolicy reject *

# Authentication
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1

# Ultra-Fast IP Rotation
MaxCircuitDirtiness {self.config['max_circuit_dirtiness']}
CircuitBuildTimeout 10
LearnCircuitBuildTimeout 0

# Performance
MaxClientCircuitsPending 32
MaxMemInQueues 256 MB

# Exit Policy
ExitPolicy accept *:*
"""
    
    def start_tor_service(self) -> bool:
        """Start Tor service"""
        try:
            # Stop existing Tor processes
            subprocess.run(['systemctl', 'stop', 'tor'], capture_output=True)
            subprocess.run(['pkill', 'tor'], capture_output=True)
            time.sleep(2)
            
            # Start Tor service
            subprocess.run(['systemctl', 'start', 'tor'], check=True)
            time.sleep(5)
            
            if self._is_tor_ready():
                self.logger.log('SUCCESS', 'Tor service started successfully')
                return True
            else:
                self.logger.log('ERROR', 'Tor service failed to start')
                return False
        except Exception as e:
            self.logger.log('ERROR', f'Failed to start Tor: {e}')
            return False
    
    def _is_tor_ready(self) -> bool:
        """Check if Tor is ready to use"""
        try:
            return self.get_current_ip() is not None
        except:
            return False
    
    def get_current_ip(self) -> Optional[str]:
        """Get current external IP through Tor"""
        try:
            proxies = {
                'http': f'socks5://127.0.0.1:{self.config["tor_socks_port"]}',
                'https': f'socks5://127.0.0.1:{self.config["tor_socks_port"]}'
            }
            response = requests.get('https://api.ipify.org', proxies=proxies, timeout=10)
            return response.text
        except:
            return None
    
    def change_ip(self) -> Optional[str]:
        """Change Tor circuit to get new IP"""
        try:
            if self._change_ip_via_control():
                self.logger.log('SUCCESS', 'IP changed via control port')
            else:
                self.logger.log('WARNING', 'Restarting Tor service for IP change')
                self.start_tor_service()
            
            time.sleep(3)
            new_ip = self.get_current_ip()
            self.logger.log('INFO', f'New IP: {new_ip}')
            return new_ip
        except Exception as e:
            self.logger.log('ERROR', f'IP change failed: {e}')
            return None
    
    def start_auto_ip_changer(self, interval: int = 10) -> None:
        """Start automatic IP rotation"""
        self.logger.log('INFO', f'Starting auto IP changer (interval: {interval}s)')
        self.is_running = True
        
        def changer():
            count = 0
            while self.is_running:
                count += 1
                old_ip = self.get_current_ip()
                new_ip = self.change_ip()
                
                if old_ip != new_ip:
                    self.logger.log('SUCCESS', f'Cycle {count}: IP changed {old_ip} → {new_ip}')
                else:
                    self.logger.log('WARNING', f'Cycle {count}: IP unchanged ({new_ip})')
                
                time.sleep(interval)
        
        thread = threading.Thread(target=changer, daemon=True)
        thread.start()
        
        self.logger.log('INFO', 'Auto IP changer started. Press Ctrl+C to stop.')
        return thread

def main():
    """Main entry point"""
    anonymizer = TorAnonymizer()
    anonymizer.print_banner()
    
    # Check root privileges
    if os.geteuid() != 0:
        anonymizer.logger.log('ERROR', 'This script requires root privileges')
        sys.exit(1)
    
    # Check dependencies
    if not anonymizer.check_dependencies():
        sys.exit(1)
    
    # Example usage
    anonymizer.configure_tor()
    anonymizer.start_tor_service()
    
    # Test IP change
    anonymizer.change_ip()

if __name__ == '__main__':
    main()
