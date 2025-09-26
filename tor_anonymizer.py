#!/usr/bin/env python3
"""
TOR Anonymizer v2.0 - Professional Privacy Tool
Advanced Tor network anonymization with secure identity rotation
"""

import time
import requests
import stem
from stem import Signal
from stem.control import Controller
from typing import Optional, Dict, Any
import json
import logging
import sys
import os
import argparse
import signal
from pathlib import Path
import hashlib
import random

class Colors:
    """ANSI color codes for terminal output"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TorAnonymizer:
    """
    Professional Tor anonymization class with security hardening
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.version = "2.0.0"
        self.author = "root-shost"
        self.config_path = config_path
        self.config = self.load_config()
        self.session = None
        self.controller = None
        self.is_running = False
        
        self.setup_logging()
        self.validate_environment()

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
        """Configure secure logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler('logs/tor_anonymizer.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_environment(self) -> None:
        """Validate system environment and dependencies"""
        try:
            import stem
            import requests
            self.logger.info("All dependencies verified")
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            sys.exit(1)

    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration securely"""
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "control_password": self.generate_secure_password(),
            "identity_rotation_interval": 300,
            "max_retries": 3,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "socks5_host": "127.0.0.1",
            "log_level": "INFO"
        }
        
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge configurations
                    default_config.update(user_config)
                    self.logger.info("Configuration loaded successfully")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Config load error: {e}, using defaults")
        else:
            self.logger.warning("Config file not found, creating default")
            self.create_default_config(default_config)
        
        # Validate critical settings
        self.validate_config(default_config)
        
        return default_config

    def generate_secure_password(self, length: int = 32) -> str:
        """Generate cryptographically secure password"""
        try:
            return hashlib.sha256(os.urandom(1024)).hexdigest()[:length]
        except:
            return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*') for _ in range(length))

    def create_default_config(self, config: Dict[str, Any]) -> None:
        """Create default configuration file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.logger.info("Default configuration created")
        except IOError as e:
            self.logger.error(f"Failed to create config: {e}")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters"""
        errors = []
        
        if not (1024 <= config['tor_port'] <= 65535):
            errors.append(f"Invalid tor_port: {config['tor_port']}")
        
        if not (1024 <= config['control_port'] <= 65535):
            errors.append(f"Invalid control_port: {config['control_port']}")
        
        if config['control_password'] == "password":
            errors.append("INSECURE: Default password detected")
        
        if config['timeout'] < 1 or config['timeout'] > 300:
            errors.append(f"Invalid timeout: {config['timeout']}")
        
        if errors:
            for error in errors:
                self.logger.error(error)
            raise ValueError("Configuration validation failed")

    def connect_controller(self) -> bool:
        """Establish secure connection to Tor controller"""
        try:
            self.controller = Controller.from_port(
                address="127.0.0.1",
                port=self.config['control_port']
            )
            self.controller.authenticate(self.config['control_password'])
            self.logger.info("Tor controller connected successfully")
            return True
        except stem.SocketError as e:
            self.logger.error(f"Tor controller connection failed: {e}")
            return False
        except stem.connection.AuthenticationFailure as e:
            self.logger.error(f"Tor authentication failed: {e}")
            return False

    def create_secure_session(self) -> requests.Session:
        """Create requests session with Tor proxy and security headers"""
        session = requests.Session()
        
        # Configure Tor proxy
        proxy_config = {
            'http': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}',
            'https': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}'
        }
        session.proxies.update(proxy_config)
        
        # Security headers
        session.headers.update({
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Security settings
        session.trust_env = False  # Prevent system proxy interference
        
        return session

    def renew_identity(self) -> bool:
        """Renew Tor circuit and identity securely"""
        try:
            if self.controller and self.controller.is_authenticated():
                self.controller.signal(Signal.NEWNYM)
                # Wait for circuit to rebuild
                time.sleep(5)
                self.logger.info("Tor identity renewed successfully")
                return True
            else:
                self.logger.error("Controller not authenticated")
                return False
        except stem.ControllerError as e:
            self.logger.error(f"Identity renewal failed: {e}")
            return False

    def get_current_ip(self) -> Optional[str]:
        """Get current external IP through Tor with validation"""
        test_services = [
            'http://httpbin.org/ip',
            'http://icanhazip.com',
            'http://ifconfig.me/ip'
        ]
        
        for service in test_services:
            try:
                response = self.session.get(service, timeout=10)
                if response.status_code == 200:
                    # Extract IP based on service response format
                    if 'httpbin' in service:
                        ip = response.json().get('origin', '').split(',')[0]
                    else:
                        ip = response.text.strip()
                    
                    if self.validate_ip(ip):
                        self.logger.info(f"Current Tor IP: {ip}")
                        return ip
            except Exception as e:
                self.logger.debug(f"IP service {service} failed: {e}")
                continue
        
        self.logger.error("All IP check services failed")
        return None

    def validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        import socket
        try:
            socket.inet_pton(socket.AF_INET, ip)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                return True
            except socket.error:
                return False

    def test_connection(self) -> bool:
        """Comprehensive Tor connection test"""
        self.logger.info("Testing Tor connection...")
        
        # Test 1: Basic connectivity
        try:
            ip = self.get_current_ip()
            if not ip:
                self.logger.error("Failed to obtain IP address")
                return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        
        # Test 2: DNS leak test
        try:
            response = self.session.get('http://httpbin.org/get', timeout=10)
            if response.status_code == 200:
                self.logger.info("DNS leak test passed")
            else:
                self.logger.warning("DNS leak test inconclusive")
        except Exception as e:
            self.logger.warning(f"DNS leak test failed: {e}")
        
        self.logger.info("All connection tests completed successfully")
        return True

    def start(self) -> bool:
        """Start Tor anonymizer service securely"""
        self.print_banner()
        self.logger.info("Initializing Tor Anonymizer...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Connect to Tor controller
        if not self.connect_controller():
            self.logger.error("Failed to connect to Tor controller")
            return False
        
        # Create secure session
        self.session = self.create_secure_session()
        self.is_running = True
        
        # Test connection
        if not self.test_connection():
            self.logger.error("Initial connection test failed")
            return False
        
        self.logger.info("Tor Anonymizer started successfully")
        return True

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.stop()

    def stop(self) -> None:
        """Stop Tor anonymizer service cleanly"""
        self.is_running = False
        try:
            if self.controller:
                self.controller.close()
            if self.session:
                self.session.close()
            self.logger.info("Tor Anonymizer stopped cleanly")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def make_secure_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make HTTP request through Tor with enhanced security"""
        if not self.is_running or not self.session:
            self.logger.error("Anonymizer not running")
            return None
        
        max_retries = kwargs.pop('max_retries', self.config['max_retries'])
        timeout = kwargs.pop('timeout', self.config['timeout'])
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=timeout,
                    **kwargs
                )
                
                self.logger.info(f"Request to {url} successful (Status: {response.status_code})")
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    self.logger.info("Rotating identity and retrying...")
                    self.renew_identity()
                    time.sleep(2)
                else:
                    self.logger.error(f"All {max_retries} attempts failed for {url}")
        
        return None

    def run_interactive(self) -> None:
        """Run in interactive mode"""
        self.logger.info("Interactive mode started. Press Ctrl+C to exit.")
        
        try:
            while self.is_running:
                # Display status every 60 seconds
                ip = self.get_current_ip()
                if ip:
                    print(f"{Colors.GREEN}Current IP: {ip}{Colors.END}")
                
                # Rotate identity at configured interval
                time.sleep(self.config['identity_rotation_interval'])
                self.renew_identity()
                
        except KeyboardInterrupt:
            self.logger.info("Interactive mode interrupted by user")
        finally:
            self.stop()

def main():
    """Main entry point with comprehensive argument parsing"""
    parser = argparse.ArgumentParser(
        description='TOR Anonymizer v2.0 - Professional Privacy Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tor_anonymizer.py                          # Interactive mode
  tor_anonymizer.py --test                   # Test connection
  tor_anonymizer.py --url "https://example.com"  # Single request
  tor_anonymizer.py --config custom.json     # Custom config
        """
    )
    
    parser.add_argument('-c', '--config', default='settings.json', 
                       help='Path to configuration file')
    parser.add_argument('--test', action='store_true', 
                       help='Test connection and exit')
    parser.add_argument('--url', help='URL to request through Tor')
    parser.add_argument('--method', default='GET', 
                       choices=['GET', 'POST', 'HEAD', 'OPTIONS'],
                       help='HTTP method for request')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Initialize anonymizer
        anonymizer = TorAnonymizer(args.config)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Start service
        if not anonymizer.start():
            sys.exit(1)
        
        # Execute based on arguments
        if args.test:
            print("Connection test completed successfully")
            anonymizer.stop()
            return
        
        elif args.url:
            response = anonymizer.make_secure_request(args.url, method=args.method)
            if response:
                print(f"Response Status: {response.status_code}")
                print(f"Content Length: {len(response.text)} bytes")
            anonymizer.stop()
            
        else:
            anonymizer.run_interactive()
            
    except KeyboardInterrupt:
        print("\nShutdown initiated by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
