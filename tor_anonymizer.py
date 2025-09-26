#!/usr/bin/env python3
"""
TOR Anonymizer - Professional Privacy Tool
Advanced Tor network anonymization with multiple identity rotation
"""

import time
import requests
import stem
import stem.control
from stem import Signal
from stem.control import Controller
from typing import Optional, Dict, List
import json
import logging
import sys
import os
import signal
import argparse
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TorAnonymizer:
    """
    Advanced Tor anonymization class with identity rotation and monitoring
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.version = "2.0.0"
        self.author = "root-shost"
        self.config_path = config_path
        self.config = self.load_config()
        self.session = None
        self.controller = None
        self.is_running = False
        
        # Setup logging
        self.setup_logging()
        
        # Validate Tor configuration
        self.validate_tor_config()

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
{Colors.END}"""
        print(banner)

    def setup_logging(self) -> None:
        """Configure advanced logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tor_anonymizer.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict:
        """Load configuration with validation"""
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "control_password": "password",
            "identity_rotation_interval": 300,
            "max_retries": 3,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            self.logger.warning(f"Config load error: {e}, using defaults")
            
        return default_config

    def validate_tor_config(self) -> None:
        """Validate Tor configuration requirements"""
        required_ports = [self.config['tor_port'], self.config['control_port']]
        for port in required_ports:
            if not (1024 <= port <= 65535):
                raise ValueError(f"Invalid port {port}. Must be between 1024-65535")

    def connect_controller(self) -> bool:
        """Establish connection to Tor controller"""
        try:
            self.controller = Controller.from_port(
                port=self.config['control_port']
            )
            self.controller.authenticate(self.config['control_password'])
            self.logger.info("Tor controller connected successfully")
            return True
        except Exception as e:
            self.logger.error(f"Controller connection failed: {e}")
            return False

    def create_session(self) -> requests.Session:
        """Create requests session with Tor proxy"""
        session = requests.Session()
        proxy_config = {
            'http': f'socks5://127.0.0.1:{self.config["tor_port"]}',
            'https': f'socks5://127.0.0.1:{self.config["tor_port"]}'
        }
        session.proxies.update(proxy_config)
        session.headers.update({'User-Agent': self.config['user_agent']})
        return session

    def renew_identity(self) -> bool:
        """Renew Tor circuit and identity"""
        try:
            if self.controller:
                self.controller.signal(Signal.NEWNYM)
                time.sleep(2)  # Wait for circuit renewal
                self.logger.info("Tor identity renewed")
                return True
        except Exception as e:
            self.logger.error(f"Identity renewal failed: {e}")
        return False

    def get_current_ip(self) -> Optional[str]:
        """Get current external IP through Tor"""
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=10)
            return response.json().get('origin')
        except Exception as e:
            self.logger.error(f"IP check failed: {e}")
            return None

    def test_connection(self) -> bool:
        """Test Tor connection and anonymity"""
        try:
            ip = self.get_current_ip()
            if ip:
                self.logger.info(f"Current Tor IP: {ip}")
                return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
        return False

    def start(self) -> None:
        """Start Tor anonymizer service"""
        self.print_banner()
        self.logger.info("Starting Tor Anonymizer...")
        
        if not self.connect_controller():
            raise ConnectionError("Failed to connect to Tor controller")
            
        self.session = self.create_session()
        self.is_running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("Tor Anonymizer started successfully")
        
        # Initial connection test
        if not self.test_connection():
            self.logger.warning("Initial connection test failed")

    def signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def stop(self) -> None:
        """Stop Tor anonymizer service"""
        self.is_running = False
        if self.controller:
            self.controller.close()
        self.logger.info("Tor Anonymizer stopped")

    def make_request(self, url: str, max_retries: int = None) -> Optional[requests.Response]:
        """Make HTTP request through Tor with retry logic"""
        if max_retries is None:
            max_retries = self.config['max_retries']
            
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=self.config['timeout'])
                self.logger.info(f"Request to {url} successful")
                return response
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    self.renew_identity()
                    time.sleep(2)
                    
        self.logger.error(f"All {max_retries} attempts failed for {url}")
        return None

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='TOR Anonymizer - Professional Privacy Tool')
    parser.add_argument('-c', '--config', default='settings.json', 
                       help='Path to configuration file')
    parser.add_argument('--test', action='store_true', 
                       help='Test connection and exit')
    parser.add_argument('url', nargs='?', help='URL to request through Tor')
    
    args = parser.parse_args()
    
    try:
        anonymizer = TorAnonymizer(args.config)
        anonymizer.start()
        
        if args.test:
            if anonymizer.test_connection():
                print("Connection test: SUCCESS")
            else:
                print("Connection test: FAILED")
            anonymizer.stop()
            return
            
        if args.url:
            response = anonymizer.make_request(args.url)
            if response:
                print(f"Response status: {response.status_code}")
                print(f"Response length: {len(response.text)} bytes")
        
        # Interactive mode
        else:
            print("Interactive mode - Press Ctrl+C to exit")
            while anonymizer.is_running:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
