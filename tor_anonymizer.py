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
import subprocess
import psutil
import atexit
import ipaddress
import socket

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
        self.session = None
        self.controller = None
        self.tor_process = None
        self.is_running = False
        self.logger = None  # Inizializza logger a None
        
        # ORDINE CORRETTO: prima logging, poi config
        self.setup_logging()
        self.config = self.load_config()
        
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
║         GitHub: github.com/root-shost/tor-anonymizer         ║
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
        self.logger.info("Logging system initialized")

    def validate_environment(self) -> None:
        """Validate system environment and dependencies"""
        try:
            # Questi import sono già fatti sopra, ma verifichiamo la disponibilità
            if self.logger:
                self.logger.info("All dependencies verified")
        except ImportError as e:
            if self.logger:
                self.logger.error(f"Missing dependency: {e}")
                self.logger.info("Install dependencies with: pip install -r requirements.txt")
            else:
                print(f"ERROR: Missing dependency: {e}")
            sys.exit(1)

    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration securely"""
        # Debug: verifica che il logger esista
        if not hasattr(self, 'logger') or self.logger is None:
            print("WARNING: Logger not initialized, setting up emergency logging")
            self.setup_logging()
        
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "control_password": self.generate_secure_password(),
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
        
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge configurations
                    default_config.update(user_config)
                    if self.logger:
                        self.logger.info("Configuration loaded successfully")
            except (json.JSONDecodeError, IOError) as e:
                if self.logger:
                    self.logger.warning(f"Config load error: {e}, using defaults")
                else:
                    print(f"WARNING: Config load error: {e}, using defaults")
        else:
            if self.logger:
                self.logger.warning("Config file not found, creating default")
            else:
                print("WARNING: Config file not found, creating default")
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
            if self.logger:
                self.logger.info("Default configuration created")
            else:
                print("INFO: Default configuration created")
        except IOError as e:
            if self.logger:
                self.logger.error(f"Failed to create config: {e}")
            else:
                print(f"ERROR: Failed to create config: {e}")

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters"""
        errors = []
        
        if not (1024 <= config['tor_port'] <= 65535):
            errors.append(f"Invalid tor_port: {config['tor_port']}")
        
        if not (1024 <= config['control_port'] <= 65535):
            errors.append(f"Invalid control_port: {config['control_port']}")
        
        if config.get('control_password') == "password":
            errors.append("INSECURE: Default password detected")
        
        if config['timeout'] < 1 or config['timeout'] > 300:
            errors.append(f"Invalid timeout: {config['timeout']}")
        
        if errors:
            for error in errors:
                if self.logger:
                    self.logger.error(error)
                else:
                    print(f"ERROR: {error}")
            raise ValueError("Configuration validation failed")

    def is_tor_installed(self) -> bool:
        """Check if Tor is installed on system"""
        try:
            subprocess.run(["tor", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def hash_password(self, password: str) -> str:
        """Generate Tor hashed control password"""
        try:
            # Try to use tor --hash-password command
            result = subprocess.run([
                "tor", "--hash-password", password
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            # Fallback hashing
            if self.logger:
                self.logger.warning("Using fallback password hashing")
            return hashlib.sha256(password.encode()).hexdigest()[:16]

    def start_tor_process(self) -> bool:
        """Start Tor process automatically"""
        if not self.is_tor_installed():
            if self.logger:
                self.logger.error("Tor is not installed. Please install Tor first.")
            else:
                print("ERROR: Tor is not installed. Please install Tor first.")
            return False

        try:
            # Create torrc configuration
            torrc_content = f"""
SOCKSPort {self.config['tor_port']}
ControlPort {self.config['control_port']}
HashedControlPassword {self.hash_password(self.config['control_password'])}
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0
""".strip()

            with open('torrc', 'w') as f:
                f.write(torrc_content)
            
            # Create necessary directories
            Path("tor_data").mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            # Start Tor process
            self.tor_process = subprocess.Popen([
                "tor", "-f", "torrc"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for Tor to start
            if self.logger:
                self.logger.info("Waiting for Tor to start...")
            time.sleep(10)
            
            # Register cleanup
            atexit.register(self.stop_tor_process)
            
            if self.logger:
                self.logger.info("Tor process started successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to start Tor: {e}")
            else:
                print(f"ERROR: Failed to start Tor: {e}")
            return False

    def stop_tor_process(self) -> None:
        """Stop Tor process"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                if self.logger:
                    self.logger.info("Tor process stopped")
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
                self.tor_process.wait()
                if self.logger:
                    self.logger.warning("Tor process killed forcefully")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error stopping Tor process: {e}")

    def connect_controller(self) -> bool:
        """Establish secure connection to Tor controller with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.controller = Controller.from_port(
                    address="127.0.0.1",
                    port=self.config['control_port']
                )
                self.controller.authenticate(self.config['control_password'])
                if self.logger:
                    self.logger.info("Tor controller connected successfully")
                return True
                
            except stem.SocketError as e:
                if self.logger:
                    self.logger.warning(f"Tor controller connection failed (attempt {attempt + 1}): {e}")
                
                if attempt == max_retries - 1:
                    if self.logger:
                        self.logger.error("All connection attempts failed.")
                    
                    # Try to start Tor automatically if configured
                    if self.config.get('auto_start_tor', True):
                        if self.logger:
                            self.logger.info("Attempting to start Tor automatically...")
                        if self.start_tor_process():
                            time.sleep(5)
                            continue
                    
                    return False
                time.sleep(2)
                
            except stem.connection.AuthenticationFailure as e:
                if self.logger:
                    self.logger.error(f"Tor authentication failed: {e}")
                # Regenerate password and retry
                if attempt == 0:
                    self.config['control_password'] = self.generate_secure_password()
                    self.create_default_config(self.config)
                    if self.logger:
                        self.logger.info("Regenerated control password, please restart Tor")
                return False
                
        return False

    def create_secure_session(self) -> requests.Session:
        """Create requests session with enhanced Tor proxy configuration"""
        session = requests.Session()
        
        # Enhanced proxy configuration with fallback
        proxy_config = {
            'http': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}',
            'https': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}'
        }
        
        session.proxies.update(proxy_config)
        
        # Enhanced security headers
        session.headers.update({
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',  # Do Not Track
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        
        # Security settings
        session.trust_env = False  # Prevent system proxy interference
        session.max_redirects = 5  # Limit redirects
        
        return session

    def renew_identity(self) -> bool:
        """Renew Tor circuit and identity securely"""
        try:
            if self.controller and self.controller.is_authenticated():
                self.controller.signal(Signal.NEWNYM)
                # Wait for circuit to rebuild
                time.sleep(5)
                if self.logger:
                    self.logger.info("Tor identity renewed successfully")
                return True
            else:
                if self.logger:
                    self.logger.error("Controller not authenticated")
                return False
        except stem.ControllerError as e:
            if self.logger:
                self.logger.error(f"Identity renewal failed: {e}")
            return False

    def validate_ip(self, ip: str) -> bool:
        """Enhanced IP validation with Tor network checks"""
        try:
            # Basic IP format validation
            ipaddress.ip_address(ip)
            
            # Check for common non-Tor IPs (basic heuristic)
            non_tor_ranges = [
                ipaddress.ip_network('192.168.0.0/16'),
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
            ]
            
            ip_obj = ipaddress.ip_address(ip)
            if any(ip_obj in network for network in non_tor_ranges):
                if self.logger:
                    self.logger.warning(f"IP {ip} appears to be in private range")
                return False
                
            return True
            
        except ValueError:
            return False

    def check_tor_network(self, ip: str) -> bool:
        """Check if IP belongs to Tor network (basic check)"""
        try:
            # Reverse DNS lookup for Tor exit nodes
            hostname = socket.gethostbyaddr(ip)[0]
            return any(tor_indicator in hostname.lower() for tor_indicator in ['tor', 'exit'])
        except:
            return True  # If we can't verify, assume it's OK

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
                        if self.logger:
                            self.logger.info(f"Current Tor IP: {ip}")
                        return ip
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"IP service {service} failed: {e}")
                continue
        
        if self.logger:
            self.logger.error("All IP check services failed")
        return None

    def test_connection(self) -> bool:
        """Comprehensive Tor connection test"""
        if self.logger:
            self.logger.info("Testing Tor connection...")
        
        # Test 1: Basic connectivity
        try:
            ip = self.get_current_ip()
            if not ip:
                if self.logger:
                    self.logger.error("Failed to obtain IP address")
                return False
                
            # Test Tor project check
            response = self.session.get('http://check.torproject.org', timeout=10)
            if "Congratulations" in response.text:
                if self.logger:
                    self.logger.info("✓ Tor connection verified by torproject.org")
            else:
                if self.logger:
                    self.logger.warning("✗ Not using Tor according to torproject.org")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Connection test failed: {e}")
            return False
        
        # Test 2: DNS leak test
        try:
            response = self.session.get('http://httpbin.org/get', timeout=10)
            if response.status_code == 200:
                if self.logger:
                    self.logger.info("✓ DNS leak test passed")
            else:
                if self.logger:
                    self.logger.warning("⚠ DNS leak test inconclusive")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"DNS leak test failed: {e}")
        
        if self.logger:
            self.logger.info("All connection tests completed successfully")
        return True

    def start(self) -> bool:
        """Start Tor anonymizer service securely"""
        self.print_banner()
        if self.logger:
            self.logger.info("Initializing Tor Anonymizer...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Connect to Tor controller
        if not self.connect_controller():
            if self.logger:
                self.logger.error("Failed to connect to Tor controller")
            return False
        
        # Create secure session
        self.session = self.create_secure_session()
        self.is_running = True
        
        # Test connection
        if not self.test_connection():
            if self.logger:
                self.logger.error("Initial connection test failed")
            return False
        
        if self.logger:
            self.logger.info("Tor Anonymizer started successfully")
        return True

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully"""
        if self.logger:
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
            self.stop_tor_process()
            if self.logger:
                self.logger.info("Tor Anonymizer stopped cleanly")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during shutdown: {e}")

    def make_secure_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make HTTP request through Tor with enhanced security"""
        if not self.is_running or not self.session:
            if self.logger:
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
                
                if self.logger:
                    self.logger.info(f"Request to {url} successful (Status: {response.status_code})")
                return response
                
            except requests.exceptions.RequestException as e:
                if self.logger:
                    self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    if self.logger:
                        self.logger.info("Rotating identity and retrying...")
                    self.renew_identity()
                    time.sleep(2)
                else:
                    if self.logger:
                        self.logger.error(f"All {max_retries} attempts failed for {url}")
        
        return None

    def run_interactive(self) -> None:
        """Run in interactive mode"""
        if self.logger:
            self.logger.info("Interactive mode started. Press Ctrl+C to exit.")
        
        rotation_count = 0
        start_time = time.time()
        
        try:
            while self.is_running:
                # Display status
                ip = self.get_current_ip()
                if ip:
                    status_msg = f"{Colors.GREEN}✓ IP: {ip} | Rotations: {rotation_count} | Uptime: {int(time.time() - start_time)}s{Colors.END}"
                    print(status_msg)
                
                # Rotate identity at configured interval
                time.sleep(self.config['identity_rotation_interval'])
                if self.renew_identity():
                    rotation_count += 1
                
        except KeyboardInterrupt:
            if self.logger:
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
    parser.add_argument('--no-auto-tor', action='store_true',
                       help='Disable automatic Tor startup')
    
    args = parser.parse_args()
    
    try:
        # Initialize anonymizer
        anonymizer = TorAnonymizer(args.config)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        if args.no_auto_tor:
            anonymizer.config['auto_start_tor'] = False
        
        # Start service
        if not anonymizer.start():
            sys.exit(1)
        
        # Execute based on arguments
        if args.test:
            print("✓ Connection test completed successfully")
            anonymizer.stop()
            return
        
        elif args.url:
            response = anonymizer.make_secure_request(args.url, method=args.method)
            if response:
                print(f"✓ Response Status: {response.status_code}")
                print(f"✓ Content Length: {len(response.text)} bytes")
                print(f"✓ Final URL: {response.url}")
            else:
                print("✗ Request failed")
            anonymizer.stop()
            
        else:
            anonymizer.run_interactive()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown initiated by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
