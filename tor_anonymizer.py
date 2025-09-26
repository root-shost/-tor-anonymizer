#!/usr/bin/env python3
"""
TOR Anonymizer v2.0.1 - Professional Privacy Tool with Fast IP Rotation
Advanced Tor network anonymization with 10-second identity rotation
"""

import time
import requests
import stem
from stem import Signal
from stem.control import Controller
from typing import Optional, Dict, Any, List
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
import threading
from datetime import datetime, timedelta
import urllib3

# Disable insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

class IPRotationManager:
    """Manager for automatic IP rotation with configurable intervals"""
    
    def __init__(self, anonymizer: 'TorAnonymizer', interval: int = 10):
        self.anonymizer = anonymizer
        self.interval = interval
        self.rotation_count = 0
        self.last_rotation = datetime.now()
        self.is_running = False
        self.rotation_thread = None
        self.logger = anonymizer.logger
        
    def start_rotation(self):
        """Start automatic IP rotation"""
        if self.is_running:
            self.logger.warning("Rotation already running")
            return
            
        self.is_running = True
        self.rotation_thread = threading.Thread(
            target=self._rotation_worker, 
            daemon=True,
            name="IPRotationWorker"
        )
        self.rotation_thread.start()
        self.logger.info(f"🚀 IP rotation started with {self.interval}-second interval")
        
    def stop_rotation(self):
        """Stop automatic IP rotation"""
        self.is_running = False
        if self.rotation_thread and self.rotation_thread.is_alive():
            self.rotation_thread.join(timeout=5)
        self.logger.info("🛑 IP rotation stopped")
        
    def _rotation_worker(self):
        """Worker thread for automatic rotation"""
        while self.is_running:
            try:
                time.sleep(self.interval)
                
                if self.is_running and self.anonymizer.is_running:
                    if self.anonymizer.renew_identity():
                        self.rotation_count += 1
                        self.last_rotation = datetime.now()
                        
                        # Log rotation every 5 rotations to avoid spam
                        if self.rotation_count % 5 == 0:
                            ip = self.anonymizer.get_current_ip() or "Unknown"
                            self.logger.info(
                                f"🔄 Rotation #{self.rotation_count} completed | "
                                f"IP: {ip} | Next rotation in {self.interval}s"
                            )
                            
            except Exception as e:
                self.logger.error(f"Rotation worker error: {e}")
                time.sleep(5)

class TorAnonymizer:
    """
    Professional Tor anonymization class with 10-second IP rotation
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.version = "2.0.1"
        self.author = "root-shost"
        self.config_path = config_path
        self.session = None
        self.controller = None
        self.tor_process = None
        self.is_running = False
        self.logger = None
        self.rotation_manager = None
        self.start_time = None
        
        # Correct initialization order
        self.setup_logging()
        self.config = self.load_config()
        self.validate_environment()

    def print_banner(self) -> None:
        """Display professional banner"""
        rotation_interval = self.config.get('identity_rotation_interval', 10)
        tor_port = self.config.get('tor_port', 9050)
        control_port = self.config.get('control_port', 9051)
        
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TOR ANONYMIZER v{self.version}                    ║
║                  Ultimate Privacy Tool with Fast IP Rotation                 ║
║                                                                              ║
║          Author: {self.author}{' '*(58-len(self.author))}║
║         GitHub: github.com/root-shost/tor-anonymizer{' '*(25-len('github.com/root-shost/tor-anonymizer'))}║
║                                                                              ║
║           🔄 IP Rotation: Every {rotation_interval:3} seconds{' '*(38-len(f'Every {rotation_interval} seconds'))}║
║           🌐 Tor Port: {tor_port:5} | Control Port: {control_port:5}{' '*(30-len(f'{tor_port} | Control Port: {control_port}'))}║
║           🔒 Fast Rotation: {'ENABLED' if self.config.get('fast_rotation_mode', True) else 'DISABLED'}{' '*(40-len('ENABLED' if self.config.get('fast_rotation_mode', True) else 'DISABLED'))}║
║           ⚡ Max Circuits: {self.config.get('max_circuits', 100):3}{' '*(41-len(str(self.config.get('max_circuits', 100))))}║
║           🛡️  DNS Protection: {'ENABLED' if self.config.get('dns_leak_protection', True) else 'DISABLED'}{' '*(35-len('ENABLED' if self.config.get('dns_leak_protection', True) else 'DISABLED'))}║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""
        print(banner)

    def setup_logging(self) -> None:
        """Configure secure logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create more detailed log format
        log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
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
            # Verify critical modules
            import requests
            import stem
            import psutil
            
            self.logger.info("All dependencies verified")
            
            # Check Tor installation
            try:
                result = subprocess.run(["tor", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    tor_version = result.stdout.strip().split('\n')[0]
                    self.logger.info(f"Tor installed: {tor_version}")
                else:
                    self.logger.warning("Tor is not installed or not in PATH")
            except Exception as e:
                self.logger.warning(f"Tor check failed: {e}")
                
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            self.logger.info("Install dependencies with: pip install requests stem psutil")
            sys.exit(1)

    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration securely"""
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "identity_rotation_interval": 10,
            "max_retries": 3,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "socks5_host": "127.0.0.1",
            "log_level": "INFO",
            "auto_start_tor": True,
            "dns_leak_protection": True,
            "safe_browsing": True,
            "max_circuit_dirtiness": 10,
            "exclude_nodes": "",
            "strict_nodes": False,
            "fast_rotation_mode": True,
            "circuit_timeout": 60,
            "max_circuits": 100
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
            self.logger.warning("Config file not found, using defaults")
        
        # Validate critical settings
        self.validate_config(default_config)
        
        return default_config

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters"""
        errors = []
        
        # Validate ports
        if not (1024 <= config['tor_port'] <= 65535):
            errors.append(f"Invalid tor_port: {config['tor_port']}")
        
        if not (1024 <= config['control_port'] <= 65535):
            errors.append(f"Invalid control_port: {config['control_port']}")
        
        # Validate rotation interval
        if config['identity_rotation_interval'] < 5:
            self.logger.warning("Very fast rotation interval (<5s) may cause instability")
        elif config['identity_rotation_interval'] > 3600:
            errors.append("Rotation interval too long (>3600s)")
        
        if config['timeout'] < 1 or config['timeout'] > 300:
            errors.append(f"Invalid timeout: {config['timeout']}")
        
        if errors:
            for error in errors:
                self.logger.error(error)
            raise ValueError("Configuration validation failed")
        
        self.logger.info(f"Rotation interval set to {config['identity_rotation_interval']} seconds")

    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0
        except:
            return False

    def kill_existing_tor(self):
        """Kill existing Tor processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'tor' in proc.info['name'].lower():
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        self.logger.info(f"Killed existing Tor process: {proc.info['pid']}")
                    except:
                        try:
                            proc.kill()
                            self.logger.warning(f"Force killed Tor process: {proc.info['pid']}")
                        except:
                            pass
            time.sleep(2)  # Wait for processes to terminate
        except Exception as e:
            self.logger.warning(f"Error killing existing Tor processes: {e}")

    def start_tor_service(self) -> bool:
        """Start Tor service with fast rotation configuration"""
        try:
            # Kill existing Tor processes
            self.kill_existing_tor()
            
            # Create necessary directories
            Path("tor_data").mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            # Create optimized torrc for fast rotation
            torrc_content = f"""
SocksPort {self.config['tor_port']}
ControlPort {self.config['control_port']}
CookieAuthentication 1
DataDirectory ./tor_data
Log notice file ./logs/tor.log
RunAsDaemon 0

# Fast rotation optimization
MaxCircuitDirtiness {self.config.get('max_circuit_dirtiness', 10)}
NewCircuitPeriod 15
MaxClientCircuitsPending 32
CircuitBuildTimeout 10
LearnCircuitBuildTimeout 0
ClientUseIPv4 1
ClientUseIPv6 0

# Security settings
SafeSocks 1
TestSocks 1
WarnUnsafeSocks 1

# Performance optimization for fast rotation
NumEntryGuards 1
UseEntryGuards 1
EnforceDistinctSubnets 1
""".strip()

            with open('torrc', 'w', encoding='utf-8') as f:
                f.write(torrc_content)
            
            # Start Tor
            self.tor_process = subprocess.Popen(
                ["tor", "-f", "torrc"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.logger.info("Waiting for Tor to start with fast rotation configuration...")
            
            # Wait for startup
            for i in range(30):
                time.sleep(1)
                if self.is_port_available(self.config['tor_port']):
                    continue
                    
                try:
                    controller = Controller.from_port(port=self.config['control_port'])
                    controller.authenticate()
                    controller.close()
                    self.logger.info("Tor service started successfully")
                    
                    # Register cleanup
                    atexit.register(self.stop_tor_process)
                    return True
                except:
                    if i % 5 == 0:
                        self.logger.info(f"Waiting for Tor... ({i+1}/30)")
                    continue
                    
            self.logger.error("Tor service failed to start within timeout")
            # Read error output for debugging
            if self.tor_process:
                stdout, stderr = self.tor_process.communicate(timeout=1)
                if stderr:
                    self.logger.error(f"Tor error: {stderr}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start Tor service: {e}")
            return False

    def stop_tor_process(self) -> None:
        """Stop Tor process gracefully"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                stdout, stderr = self.tor_process.communicate(timeout=10)
                self.logger.info("Tor process stopped")
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
                self.tor_process.wait()
                self.logger.warning("Tor process killed forcefully")
            except Exception as e:
                self.logger.error(f"Error stopping Tor process: {e}")
            finally:
                self.tor_process = None

    def connect_controller(self) -> bool:
        """Establish secure connection to Tor controller"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                self.controller = Controller.from_port(
                    address="127.0.0.1",
                    port=self.config['control_port']
                )
                
                # Try cookie authentication
                try:
                    self.controller.authenticate()
                    self.logger.info("Tor controller connected (cookie auth)")
                    return True
                except stem.connection.AuthenticationFailure:
                    self.logger.error("Cookie authentication failed")
                    return False
                    
            except stem.SocketError as e:
                self.logger.warning(f"Tor controller connection failed (attempt {attempt + 1}): {e}")
                
                if attempt == max_retries - 1:
                    self.logger.error("All connection attempts failed")
                    return False
                time.sleep(2)
                
            except stem.connection.AuthenticationFailure as e:
                self.logger.error(f"Tor authentication failed: {e}")
                return False
                
        return False

    def create_secure_session(self) -> requests.Session:
        """Create requests session with enhanced Tor proxy configuration"""
        session = requests.Session()
        
        # Enhanced proxy configuration for fast rotation
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
            'DNT': '1',
        })
        
        # Security settings
        session.trust_env = False
        session.max_redirects = 5
        
        return session

    def renew_identity(self) -> bool:
        """Renew Tor circuit and identity securely"""
        try:
            if self.controller and self.controller.is_authenticated():
                self.controller.signal(Signal.NEWNYM)
                # Reduced wait time for faster rotation
                time.sleep(2)
                self.logger.debug("Tor identity renewed successfully")
                return True
            else:
                self.logger.error("Controller not authenticated")
                return False
        except stem.ControllerError as e:
            self.logger.error(f"Identity renewal failed: {e}")
            return False

    def validate_ip(self, ip: str) -> bool:
        """Enhanced IP validation with Tor network checks"""
        try:
            ipaddress.ip_address(ip)
            
            # Check for common non-Tor IPs
            non_tor_ranges = [
                ipaddress.ip_network('192.168.0.0/16'),
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
            ]
            
            ip_obj = ipaddress.ip_address(ip)
            if any(ip_obj in network for network in non_tor_ranges):
                self.logger.warning(f"IP {ip} appears to be in private range")
                return False
                
            return True
            
        except ValueError:
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
                    if 'httpbin' in service:
                        ip = response.json().get('origin', '').split(',')[0]
                    else:
                        ip = response.text.strip()
                    
                    if self.validate_ip(ip):
                        return ip
            except Exception as e:
                self.logger.debug(f"IP service {service} failed: {e}")
                continue
        
        self.logger.error("All IP check services failed")
        return None

    def test_connection(self) -> bool:
        """Comprehensive Tor connection test"""
        self.logger.info("Testing Tor connection...")
        
        # Test 1: Basic connectivity
        try:
            ip = self.get_current_ip()
            if not ip:
                self.logger.error("Failed to obtain IP address")
                return False
            else:
                self.logger.info(f"✓ Current Tor IP: {ip}")
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        
        # Test 2: Tor project check
        try:
            response = self.session.get('https://check.torproject.org', timeout=10)
            if "Congratulations" in response.text:
                self.logger.info("✓ Tor connection verified by torproject.org")
            else:
                self.logger.warning("⚠ Not using Tor according to torproject.org")
        except Exception as e:
            self.logger.warning(f"Tor project check failed: {e}")
        
        self.logger.info("Connection tests completed successfully")
        return True

    def start(self) -> bool:
        """Start Tor anonymizer service securely"""
        self.print_banner()
        self.start_time = datetime.now()
        self.logger.info("Initializing Tor Anonymizer...")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start Tor service
        if not self.start_tor_service():
            self.logger.error("Failed to start Tor service")
            return False
        
        # Connect to Tor controller
        if not self.connect_controller():
            self.logger.error("Failed to connect to Tor controller")
            return False
        
        # Create secure session
        self.session = self.create_secure_session()
        self.is_running = True
        
        # Initialize rotation manager
        rotation_interval = self.config.get('identity_rotation_interval', 10)
        self.rotation_manager = IPRotationManager(self, rotation_interval)
        
        # Test connection
        if not self.test_connection():
            self.logger.error("Initial connection test failed")
            return False
        
        # Start automatic rotation
        if rotation_interval > 0:
            self.rotation_manager.start_rotation()
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"Tor Anonymizer started successfully in {uptime:.2f} seconds")
        return True

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.stop()

    def stop(self) -> None:
        """Stop Tor anonymizer service cleanly"""
        self.is_running = False
        
        if self.rotation_manager:
            self.rotation_manager.stop_rotation()
        
        try:
            if self.controller:
                self.controller.close()
            if self.session:
                self.session.close()
            self.stop_tor_process()
            
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
                self.logger.info(f"Tor Anonymizer stopped after {uptime:.2f} seconds")
                
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
        
        rotation_count = 0
        start_time = time.time()
        last_ip = None
        
        try:
            while self.is_running:
                # Display status
                ip = self.get_current_ip()
                current_time = time.time()
                uptime = current_time - start_time
                
                if ip and ip != last_ip:
                    status_msg = f"{Colors.GREEN}🔄 IP: {ip} | Rotations: {rotation_count} | Uptime: {int(uptime)}s{Colors.END}"
                    print(f"\r{status_msg}", end="", flush=True)
                    last_ip = ip
                    rotation_count += 1
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Interactive mode interrupted by user")
        finally:
            self.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='TOR Anonymizer v2.0.1 - Professional Privacy Tool')
    
    parser.add_argument('-c', '--config', default='settings.json', help='Configuration file')
    parser.add_argument('--test', action='store_true', help='Test connection and exit')
    parser.add_argument('--url', help='URL to request through Tor')
    parser.add_argument('--method', default='GET', choices=['GET', 'POST', 'HEAD', 'OPTIONS'])
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-auto-tor', action='store_true', help='Disable automatic Tor startup')
    parser.add_argument('--interval', type=int, help='IP rotation interval in seconds')
    
    args = parser.parse_args()
    
    try:
        # Initialize anonymizer
        anonymizer = TorAnonymizer(args.config)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        if args.no_auto_tor:
            anonymizer.config['auto_start_tor'] = False
        
        if args.interval:
            anonymizer.config['identity_rotation_interval'] = args.interval
        
        # Start service
        if not anonymizer.start():
            sys.exit(1)
        
        # Execute based on arguments
        if args.test:
            print("✓ Connection test completed successfully")
            anonymizer.stop()
        elif args.url:
            response = anonymizer.make_secure_request(args.url, method=args.method)
            if response:
                print(f"✓ Response Status: {response.status_code}")
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
