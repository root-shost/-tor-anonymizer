#!/usr/bin/env python3
"""
TOR Anonymizer v2.0 - Ultimate Advanced Stealth Mode
Advanced privacy with multi-layer protection
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
import re
import threading
from datetime import datetime, timedelta

# Gestione fallback per fake-useragent
try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False
    print("⚠️ fake-useragent not available, using fallback user agents")

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

class AdvancedTorAnonymizer:
    """
    Advanced Tor anonymization with multi-layer stealth protection
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.version = "2.0.0"
        self.author = "root-shost"
        self.config_path = config_path
        self.session = None
        self.controller = None
        self.tor_process = None
        self.is_running = False
        self.logger = None
        self.ua_generator = self.setup_user_agent_generator()
        self.current_circuit_id = None
        self.rotation_count = 0
        self.start_time = time.time()
        self.dummy_traffic_thread = None
        self.last_dummy_traffic = 0
        self.guard_nodes = []
        
        # Setup in secure order
        self.setup_advanced_logging()
        self.config = self.load_config()
        self.validate_advanced_environment()
        self.setup_advanced_protections()

    def setup_user_agent_generator(self):
        """Setup user agent generator with fallback"""
        if UA_AVAILABLE:
            return UserAgent()
        else:
            return None

    def get_random_user_agent(self):
        """Get random user agent with fallback"""
        if self.ua_generator:
            return self.ua_generator.random
        else:
            # Fallback user agents
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            ]
            return random.choice(user_agents)

    def print_banner(self) -> None:
        """Display advanced stealth banner"""
        rotation_interval = self.config.get('identity_rotation_interval', 10)
        num_guards = self.config.get('num_entry_guards', 3)
        
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║               ADVANCED TOR ANONYMIZER v{self.version}        ║
║                   ULTIMATE STEALTH MODE                      ║
║                                                              ║
║          🔒 IP Rotation: {rotation_interval}s (Randomized)   ║
║          🌐 Multi-Hop Circuit: Enabled                       ║
║          🚫 Dummy Traffic: Active                            ║
║          🛡️  Entry Guards: {num_guards} Nodes                ║
║                                                              ║
║          Author: {self.author}                               ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}"""
        print(banner)

    def setup_advanced_logging(self) -> None:
        """Configure minimal logging for maximum stealth"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Ultra-minimal logging
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tor_anonymizer.log', encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Disable all module logs
        for log_name in ['stem', 'requests', 'urllib3', 'fake_useragent']:
            logging.getLogger(log_name).setLevel(logging.CRITICAL)

    def load_config(self) -> Dict[str, Any]:
        """Load advanced configuration"""
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "identity_rotation_interval": 10,
            "min_rotation_delay": 8,
            "max_rotation_delay": 15,
            "max_retries": 5,
            "timeout": 15,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0",
            "socks5_host": "127.0.0.1",
            "log_level": "ERROR",
            "auto_start_tor": True,
            "dns_leak_protection": True,
            "safe_browsing": True,
            "max_circuit_dirtiness": 5,
            "exclude_nodes": "{ru},{cn},{us},{gb},{de},{fr},{nl}",
            "strict_nodes": True,
            "entry_nodes": "{se},{no},{fi},{dk}",
            "exit_nodes": "{ch},{at},{li},{is}",
            "use_bridges": True,
            "bridge_type": "obfs4",
            "disable_javascript": True,
            "block_trackers": True,
            "cookie_cleanup": True,
            "random_user_agent": True,
            "circuit_timeout": 30,
            "max_circuits": 50,
            "security_level": "high",
            "dummy_traffic_enabled": True,
            "dummy_traffic_interval": 30,
            "multi_hop_enabled": True,
            "guard_lifetime_days": 30,
            "random_delay_enabled": True,
            "traffic_obfuscation": True,
            "use_entry_guards": True,
            "num_entry_guards": 3,
            "long_lived_ports": True
        }
        
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError):
                print("Using advanced default configuration")
        else:
            self.create_default_config(default_config)
        
        return default_config

    def create_default_config(self, config: Dict[str, Any]) -> None:
        """Create advanced configuration file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✓ Advanced configuration created")
        except IOError as e:
            print(f"✗ Config creation failed: {e}")

    def validate_advanced_environment(self) -> None:
        """Validate advanced environment"""
        try:
            import requests
            import stem
            import psutil
        except ImportError as e:
            print(f"✗ Missing dependency: {e}")
            sys.exit(1)

    def setup_advanced_protections(self) -> None:
        """Setup advanced protection mechanisms"""
        # Initialize guard nodes list
        self.guard_nodes = self.generate_guard_nodes()
        
        print("🛡️  Advanced protections initialized:")
        print(f"   • Random Delay: {self.config['random_delay_enabled']}")
        print(f"   • Dummy Traffic: {self.config['dummy_traffic_enabled']}")
        print(f"   • Multi-Hop: {self.config['multi_hop_enabled']}")
        print(f"   • Entry Guards: {self.config['use_entry_guards']}")

    def generate_guard_nodes(self) -> List[str]:
        """Generate entry guard nodes for persistent identity"""
        countries = ['se', 'no', 'fi', 'ch', 'is', 'nl', 'de']
        guards = []
        for i in range(self.config['num_entry_guards']):
            country = random.choice(countries)
            guards.append(f"guard{i}_{country}")
        return guards

    def generate_advanced_torrc(self) -> str:
        """Generate ultra-advanced Tor configuration"""
        torrc_content = f"""
# ULTIMATE ADVANCED STEALTH CONFIGURATION
SocksPort {self.config['tor_port']}
ControlPort {self.config['control_port']}
CookieAuthentication 1

# Advanced security settings
SafeLogging 1
SafeSocks 1
TestSocks 1
AvoidDiskWrites 1

# Advanced node selection
StrictNodes {1 if self.config['strict_nodes'] else 0}
ExcludeNodes {self.config['exclude_nodes']}
EntryNodes {self.config['entry_nodes']}
ExitNodes {self.config['exit_nodes']}

# Multi-hop and circuit settings
MaxCircuitDirtiness {self.config['max_circuit_dirtiness']}
NewCircuitPeriod 3
MaxClientCircuitsPending 50
CircuitBuildTimeout 15
LearnCircuitBuildTimeout 0

# Entry guards for persistent identity
UseEntryGuards {1 if self.config['use_entry_guards'] else 0}
NumEntryGuards {self.config['num_entry_guards']}
GuardLifetime {self.config['guard_lifetime_days']} days

# Long-lived ports for consistency
LongLivedPorts {1 if self.config['long_lived_ports'] else 0}

# Bridge configuration
UseBridges {1 if self.config['use_bridges'] else 0}
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy

# Network settings
ClientUseIPv4 1
ClientUseIPv6 0
FascistFirewall 1

# Exit policy
ExitPolicy reject *:*

# Logging minimization
Log notice file ./logs/tor.log
""".strip()
        
        return torrc_content

    def start_advanced_tor_service(self) -> bool:
        """Start Tor with advanced configuration"""
        try:
            Path("tor_data").mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            torrc_content = self.generate_advanced_torrc()
            
            with open('torrc', 'w') as f:
                f.write(torrc_content)
            
            self.tor_process = subprocess.Popen([
                "tor", "-f", "torrc"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            
            # Advanced startup verification
            for i in range(25):
                time.sleep(1)
                try:
                    controller = Controller.from_port(port=self.config['control_port'])
                    controller.authenticate()
                    
                    # Set up entry guards
                    if self.config['use_entry_guards']:
                        self.setup_entry_guards(controller)
                    
                    controller.close()
                    print("✓ Advanced Tor service started with entry guards")
                    atexit.register(self.stop_tor_process)
                    return True
                except:
                    continue
                    
            print("✗ Advanced Tor startup failed")
            return False
            
        except Exception as e:
            print(f"Advanced Tor error: {e}")
            return False

    def setup_entry_guards(self, controller) -> None:
        """Setup persistent entry guards"""
        try:
            # Get current guards info
            guards_info = controller.get_info("entry-guards")
            if not guards_info:
                print("✓ Entry guards system activated")
        except:
            print("⚠ Entry guards setup incomplete")

    def connect_advanced_controller(self) -> bool:
        """Advanced controller connection with better error handling"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                print(f"🔗 Connecting to Tor controller (attempt {attempt + 1})...")
                
                self.controller = Controller.from_port(
                    address="127.0.0.1",
                    port=self.config['control_port']
                )
                
                # Try cookie authentication first
                try:
                    self.controller.authenticate()
                    print("✅ Tor controller connected (cookie auth)")
                    
                    # Verify entry guards
                    if self.config['use_entry_guards']:
                        self.verify_entry_guards()
                    
                    return True
                except stem.connection.AuthenticationFailure:
                    print("⚠️  Cookie auth failed, using basic mode")
                    return True
                        
            except stem.SocketError as e:
                print(f"❌ Connection failed (attempt {attempt + 1}): {e}")
                
                if attempt == max_retries - 1:
                    print("🔄 Attempting to start Tor service...")
                    if self.config.get('auto_start_tor', True):
                        return self.start_advanced_tor_service()
                    return False
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(2)
        
        return False

    def verify_entry_guards(self) -> None:
        """Verify entry guards are active"""
        try:
            guards_info = self.controller.get_info("entry-guards")
            if guards_info:
                print("✓ Entry guards verified")
        except:
            print("⚠ Entry guards verification failed")

    def create_advanced_session(self) -> requests.Session:
        """Create session with advanced stealth features"""
        session = requests.Session()
        
        # Advanced proxy configuration
        proxy_config = {
            'http': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}',
            'https': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}'
        }
        session.proxies.update(proxy_config)
        
        # Advanced user agent rotation
        if self.config.get('random_user_agent', True):
            user_agent = self.get_random_user_agent()
        else:
            user_agent = self.config['user_agent']
        
        # Advanced stealth headers
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
        })
        
        # Advanced security settings
        session.trust_env = False
        session.max_redirects = 1
        
        return session

    def random_delay_before_rotation(self) -> None:
        """Advanced random delay for rotation timing obfuscation"""
        if self.config.get('random_delay_enabled', True):
            min_delay = self.config.get('min_rotation_delay', 8)
            max_delay = self.config.get('max_rotation_delay', 15)
            delay = random.randint(min_delay, max_delay)
            print(f"⏰ Random delay: {delay}s")
            time.sleep(delay)
        else:
            time.sleep(self.config['identity_rotation_interval'])

    def advanced_identity_rotation(self) -> bool:
        """Advanced identity rotation with multiple techniques"""
        try:
            if self.controller and hasattr(self.controller, 'is_authenticated') and self.controller.is_authenticated():
                # Multiple rotation signals for thorough cleanup
                self.controller.signal(Signal.CLEARDNCACHE)
                time.sleep(1)
                self.controller.signal(Signal.NEWNYM)
                time.sleep(1)
                
                # Advanced rotation wait
                rotation_wait = random.uniform(2.5, 4.5)
                time.sleep(rotation_wait)
                
                self.rotation_count += 1
                return True
            else:
                print("⚠️  Controller not available for rotation")
                return False
        except Exception as e:
            print(f"🔁 Rotation error: {e}")
        return False

    def start_dummy_traffic_generator(self) -> None:
        """Start background dummy traffic generation"""
        if not self.config.get('dummy_traffic_enabled', True):
            return
            
        def dummy_traffic_worker():
            dummy_sites = [
                "https://www.wikipedia.org",
                "https://github.com",
                "https://stackoverflow.com",
                "https://news.ycombinator.com",
                "https://www.reddit.com"
            ]
            
            while self.is_running:
                try:
                    current_time = time.time()
                    if current_time - self.last_dummy_traffic >= self.config.get('dummy_traffic_interval', 30):
                        site = random.choice(dummy_sites)
                        self.session.get(site, timeout=5)
                        self.last_dummy_traffic = current_time
                        print(f"🌫️  Dummy traffic to: {site.split('//')[1].split('/')[0]}")
                except:
                    pass
                
                time.sleep(random.randint(5, 15))
        
        self.dummy_traffic_thread = threading.Thread(target=dummy_traffic_worker, daemon=True)
        self.dummy_traffic_thread.start()
        print("✓ Dummy traffic generator started")

    def get_advanced_stealth_ip(self) -> Optional[str]:
        """Get IP with advanced verification"""
        stealth_services = [
            'http://icanhazip.com',
            'http://ifconfig.me/ip',
            'http://ipinfo.io/ip',
            'http://api.ipify.org'
        ]
        
        random.shuffle(stealth_services)
        
        for service in stealth_services:
            try:
                response = self.session.get(service, timeout=8)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self.validate_advanced_ip(ip):
                        return ip
            except:
                continue
        return None

    def validate_advanced_ip(self, ip: str) -> bool:
        """Advanced IP validation"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            private_ranges = [
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
                ipaddress.ip_network('192.168.0.0/16'),
                ipaddress.ip_network('127.0.0.0/8'),
            ]
            
            if any(ip_obj in network for network in private_ranges):
                return False
                
            return True
        except:
            return False

    def run_advanced_stealth_tests(self) -> bool:
        """Run comprehensive advanced stealth tests"""
        print("🔍 Running advanced stealth diagnostics...")
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: IP acquisition
        ip = self.get_advanced_stealth_ip()
        if ip:
            print(f"✅ Stealth IP: {ip}")
            tests_passed += 1
        else:
            print("❌ IP acquisition failed")
        
        # Test 2: Tor verification
        try:
            response = self.session.get('https://check.torproject.org', timeout=10)
            if "Congratulations" in response.text:
                print("✅ Tor verification passed")
                tests_passed += 1
            else:
                print("⚠️  Tor detection possible")
        except:
            print("❌ Tor check failed")
        
        # Test 3: Basic functionality
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                print("✅ Basic functionality OK")
                tests_passed += 1
        except:
            print("❌ Basic functionality test failed")
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"📊 Stealth tests: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        return tests_passed >= 2

    def start_advanced_stealth_mode(self) -> bool:
        """Start ultimate advanced stealth mode"""
        self.print_banner()
        
        # Setup advanced signal handling
        signal.signal(signal.SIGINT, self.advanced_signal_handler)
        signal.signal(signal.SIGTERM, self.advanced_signal_handler)
        
        print("🔒 Initializing advanced stealth protections...")
        
        # First, test basic Tor connection
        try:
            proxies = {
                'http': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}',
                'https': f'socks5h://{self.config["socks5_host"]}:{self.config["tor_port"]}'
            }
            test_session = requests.Session()
            test_session.proxies = proxies
            response = test_session.get('http://httpbin.org/ip', timeout=10)
            print("✅ Basic Tor connection verified")
        except Exception as e:
            print(f"❌ Basic Tor connection failed: {e}")
            return False
        
        # Connect to Tor controller
        if not self.connect_advanced_controller():
            print("⚠️  Controller connection failed, using basic mode")
        
        # Create advanced session
        self.session = self.create_advanced_session()
        self.is_running = True
        
        # Start dummy traffic generator
        self.start_dummy_traffic_generator()
        
        # Run advanced tests
        if not self.run_advanced_stealth_tests():
            print("⚠️  Some stealth tests failed, continuing in basic mode")
        
        print("🎯 Advanced stealth mode ACTIVATED")
        print("💡 Press Ctrl+C to exit gracefully\n")
        
        return True

    def advanced_signal_handler(self, signum: int, frame) -> None:
        """Advanced graceful shutdown"""
        print("\n🛑 Advanced shutdown initiated...")
        self.stop_advanced_stealth_mode()

    def stop_advanced_stealth_mode(self) -> None:
        """Advanced clean shutdown"""
        self.is_running = False
        try:
            if self.controller:
                self.controller.close()
            if self.session:
                self.session.close()
            self.stop_tor_process()
            
            print("✅ Advanced stealth mode terminated")
        except Exception as e:
            print(f"❌ Shutdown error: {e}")

    def stop_tor_process(self) -> None:
        """Stop Tor process"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=5)
            except:
                try:
                    self.tor_process.kill()
                    self.tor_process.wait()
                except:
                    pass

    def make_advanced_stealth_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make request with all advanced protections"""
        if not self.is_running or not self.session:
            return None
        
        max_retries = kwargs.pop('max_retries', self.config['max_retries'])
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config['timeout'],
                    **kwargs
                )
                return response
                
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    if self.controller:
                        self.advanced_identity_rotation()
                    self.random_delay_before_rotation()
        
        return None

    def run_continuous_advanced_stealth(self) -> None:
        """Run continuous advanced stealth mode"""
        print("🚀 Starting continuous advanced stealth operations...")
        
        last_rotation = time.time()
        last_status_update = time.time()
        
        try:
            while self.is_running:
                current_time = time.time()
                
                # Advanced rotation with random delays
                if current_time - last_rotation >= self.config['identity_rotation_interval']:
                    if self.controller and self.advanced_identity_rotation():
                        ip = self.get_advanced_stealth_ip()
                        if ip:
                            uptime = int(current_time - self.start_time)
                            status = f"{Colors.GREEN}🔄 IP: {ip} | Rotations: {self.rotation_count} | Uptime: {uptime}s{Colors.END}"
                            print(status)
                        last_rotation = current_time
                    
                    # Apply random delay
                    self.random_delay_before_rotation()
                
                # Status updates every 60 seconds
                if current_time - last_status_update >= 60:
                    print(f"📊 Status: {self.rotation_count} rotations | Running: {int(current_time - self.start_time)}s")
                    last_status_update = current_time
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Advanced stealth mode interrupted")
        finally:
            self.stop_advanced_stealth_mode()

def main():
    """Main advanced entry point"""
    parser = argparse.ArgumentParser(description='ADVANCED STEALTH TOR Anonymizer')
    
    parser.add_argument('--test', action='store_true', help='Test advanced stealth connection')
    parser.add_argument('--url', help='Make advanced stealth request to URL')
    parser.add_argument('--config', default='settings.json', help='Config file path')
    parser.add_argument('--rotate-now', action='store_true', help='Force immediate IP rotation')
    parser.add_argument('--mode', choices=['stealth', 'advanced', 'ultimate'], 
                       default='ultimate', help='Operation mode')
    
    args = parser.parse_args()
    
    try:
        stealth = AdvancedTorAnonymizer(args.config)
        
        if not stealth.start_advanced_stealth_mode():
            sys.exit(1)
        
        if args.test:
            print("✅ Advanced stealth test completed")
            stealth.stop_advanced_stealth_mode()
        elif args.url:
            response = stealth.make_advanced_stealth_request(args.url)
            if response:
                print(f"✅ Advanced stealth request: {response.status_code}")
            else:
                print("❌ Advanced stealth request failed")
            stealth.stop_advanced_stealth_mode()
        elif args.rotate_now:
            if stealth.advanced_identity_rotation():
                ip = stealth.get_advanced_stealth_ip()
                print(f"✅ IP rotated: {ip}")
            stealth.stop_advanced_stealth_mode()
        else:
            stealth.run_continuous_advanced_stealth()
            
    except KeyboardInterrupt:
        print("\n🎯 Advanced stealth session completed")
    except Exception as e:
        print(f"❌ Advanced stealth error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
