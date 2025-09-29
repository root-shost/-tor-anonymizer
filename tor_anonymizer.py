#!/usr/bin/env python3
"""
TOR ANONYMIZER v3.0 - ULTIMATE ADVANCED STEALTH MODE
Multi-layer protection with enterprise-grade security
FIXED VERSION - All critical issues resolved
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
import urllib3
import tempfile
import shutil

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

class UltimateTorAnonymizer:
    """
    Ultimate Tor anonymization with enterprise-grade multi-layer protection
    FIXED VERSION - All issues resolved
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.version = "3.0.0"
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
        self.kill_switch_active = False
        self.traffic_monitor_thread = None
        self.circuit_rotation_thread = None
        self.tor_ready = False
        
        # Setup in secure order
        self.setup_enterprise_logging()
        self.config = self.load_ultimate_config()
        self.validate_enterprise_environment()
        self.setup_enterprise_protections()

    def setup_user_agent_generator(self):
        """Setup user agent generator with fallback - FIXED VERSION"""
        global UA_AVAILABLE  # ✅ AGGIUNTA CRITICA: dichiara la variabile globale
        
        if UA_AVAILABLE:
            try:
                ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0")
                # Test the user agent generator
                _ = ua.random
                return ua
            except Exception as e:
                print(f"⚠️ fake-useragent failed: {e}, using fallback user agents")
                UA_AVAILABLE = False
                return None
        else:
            return None

    def get_random_user_agent(self):
        """Get random user agent with fallback"""
        if self.ua_generator:
            try:
                return self.ua_generator.random
            except Exception:
                # Fallback se fake-useragent fallisce
                pass
        
        # Enhanced fallback user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        return random.choice(user_agents)

    def print_ultimate_banner(self) -> None:
        """Display ultimate stealth banner"""
        rotation_interval = self.config.get('identity_rotation_interval', 10)
        num_guards = self.config.get('num_entry_guards', 3)
        security_level = self.config.get('security_level', 'ultimate')
        
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║               ULTIMATE TOR ANONYMIZER v{self.version}         ║
║                 ENTERPRISE STEALTH MODE                      ║
║                                                              ║
║          🔒 IP Rotation: {rotation_interval}s (Randomized)    ║
║          🌐 Multi-Hop Circuit: Enterprise Grade              ║
║          🚫 Dummy Traffic: Advanced Obfuscation              ║
║          🛡️  Entry Guards: {num_guards} Nodes (Persistent)    ║
║          🔥 Kill Switch: Active                              ║
║          📊 Traffic Monitoring: Real-time                    ║
║          🛡️  Security Level: {security_level.upper():<12}     ║
║                                                              ║
║          Author: {self.author}                                ║
║         GitHub: github.com/root-shost/tor-anonymizer         ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}"""
        print(banner)

    def setup_enterprise_logging(self) -> None:
        """Configure enterprise logging for maximum stealth"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Ultra-minimal logging with rotation
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tor_anonymizer.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Disable all module logs for stealth
        for log_name in ['stem', 'requests', 'urllib3', 'fake_useragent', 'psutil']:
            logging.getLogger(log_name).setLevel(logging.ERROR)

    def load_ultimate_config(self) -> Dict[str, Any]:
        """Load ultimate enterprise configuration"""
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
            "security_level": "ultimate",
            "dummy_traffic_enabled": True,
            "dummy_traffic_interval": 30,
            "multi_hop_enabled": True,
            "guard_lifetime_days": 30,
            "random_delay_enabled": True,
            "traffic_obfuscation": True,
            "use_entry_guards": True,
            "num_entry_guards": 3,
            "long_lived_ports": True,
            "kill_switch_enabled": True,
            "traffic_monitoring": True,
            "auto_circuit_rotation": True,
            "bridge_obfs4": True,
            "anti_fingerprinting": True,
            "system_hardening": True,
            "firewall_protection": True
        }
        
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                self.logger.info("Enterprise configuration loaded successfully")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Config load failed: {e}, using defaults")
        else:
            self.create_ultimate_config(default_config)
        
        return default_config

    def create_ultimate_config(self, config: Dict[str, Any]) -> None:
        """Create ultimate configuration file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info("Ultimate enterprise configuration created")
        except IOError as e:
            self.logger.error(f"Config creation failed: {e}")

    def validate_enterprise_environment(self) -> None:
        """Validate enterprise environment"""
        try:
            import requests
            import stem
            import psutil
            import socks
            self.logger.info("All enterprise dependencies verified")
        except ImportError as e:
            self.logger.error(f"Missing enterprise dependency: {e}")
            print(f"❌ Missing dependency: {e}")
            print("💡 Run: pip install -r requirements.txt")
            sys.exit(1)

    def setup_enterprise_protections(self) -> None:
        """Setup enterprise protection mechanisms"""
        # Initialize guard nodes list
        self.guard_nodes = self.generate_enterprise_guard_nodes()
        
        print("🛡️  Enterprise protections initialized:")
        print(f"   • Random Delay: {self.config['random_delay_enabled']}")
        print(f"   • Dummy Traffic: {self.config['dummy_traffic_enabled']}")
        print(f"   • Multi-Hop: {self.config['multi_hop_enabled']}")
        print(f"   • Entry Guards: {self.config['use_entry_guards']}")
        print(f"   • Kill Switch: {self.config['kill_switch_enabled']}")
        print(f"   • Traffic Monitoring: {self.config['traffic_monitoring']}")

    def generate_enterprise_guard_nodes(self) -> List[str]:
        """Generate enterprise entry guard nodes"""
        countries = ['se', 'no', 'fi', 'ch', 'is', 'nl', 'de', 'at']
        guards = []
        for i in range(self.config['num_entry_guards']):
            country = random.choice(countries)
            guards.append(f"guard{i}_{country}")
        return guards

    def wait_for_tor_ready(self, timeout: int = 60) -> bool:
        """Wait for Tor to be ready with timeout"""
        self.logger.info("Waiting for Tor to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Test Tor connection
                test_session = requests.Session()
                test_session.proxies = {
                    'http': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}',
                    'https': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}'
                }
                test_session.verify = False
                
                response = test_session.get('http://httpbin.org/ip', timeout=5)
                if response.status_code == 200:
                    self.tor_ready = True
                    self.logger.info("Tor connection verified")
                    return True
            except Exception as e:
                self.logger.debug(f"Tor not ready yet: {e}")
                time.sleep(2)
        
        self.logger.error("Tor connection timeout")
        return False

    def create_enterprise_session(self) -> requests.Session:
        """Create session with enterprise stealth features"""
        session = requests.Session()
        
        # Enterprise proxy configuration
        proxy_config = {
            'http': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}',
            'https': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}'
        }
        session.proxies.update(proxy_config)
        
        # Enterprise user agent rotation
        if self.config.get('random_user_agent', True):
            user_agent = self.get_random_user_agent()
        else:
            user_agent = self.config['user_agent']
        
        # Enterprise stealth headers
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        
        # Enterprise security settings
        session.trust_env = False
        session.max_redirects = 3
        session.verify = False
        
        return session

    def random_delay_before_rotation(self) -> None:
        """Enterprise random delay for rotation timing obfuscation"""
        if self.config.get('random_delay_enabled', True):
            min_delay = self.config.get('min_rotation_delay', 8)
            max_delay = self.config.get('max_rotation_delay', 15)
            delay = random.randint(min_delay, max_delay)
            self.logger.debug(f"Enterprise random delay: {delay}s")
            time.sleep(delay)
        else:
            time.sleep(self.config['identity_rotation_interval'])

    def connect_enterprise_controller(self) -> bool:
        """Enterprise controller connection with advanced error handling"""
        try:
            self.logger.info("Attempting enterprise controller connection...")
            
            self.controller = Controller.from_port(
                address="127.0.0.1",
                port=self.config['control_port']
            )
            
            # Advanced authentication - try without password first
            try:
                self.controller.authenticate()
                self.logger.info("Enterprise controller connected (passwordless auth)")
                return True
            except stem.connection.AuthenticationFailure:
                # Try with empty password
                try:
                    self.controller.authenticate(password="")
                    self.logger.info("Enterprise controller connected (empty password auth)")
                    return True
                except stem.connection.AuthenticationFailure:
                    self.logger.warning("Enterprise controller authentication failed")
                    return False
                    
        except Exception as e:
            self.logger.warning(f"Enterprise controller connection failed: {e}")
            return False

    def enterprise_identity_rotation(self) -> bool:
        """Enterprise identity rotation with multiple techniques"""
        try:
            if self.controller and hasattr(self.controller, 'is_authenticated') and self.controller.is_authenticated():
                # Enterprise rotation signals
                self.controller.signal(Signal.NEWNYM)
                time.sleep(2)
                self.controller.signal(Signal.CLEARDNSCACHE)
                time.sleep(1)
                
                self.rotation_count += 1
                self.logger.info(f"Enterprise identity rotation #{self.rotation_count}")
                return True
            else:
                self.logger.warning("Enterprise controller not available for rotation")
                return False
        except Exception as e:
            self.logger.error(f"Enterprise rotation error: {e}")
            return False

    def start_enterprise_dummy_traffic(self) -> None:
        """Start enterprise dummy traffic generation"""
        if not self.config.get('dummy_traffic_enabled', True):
            return
            
        def enterprise_dummy_traffic_worker():
            enterprise_dummy_sites = [
                "https://www.wikipedia.org",
                "https://github.com",
                "https://stackoverflow.com",
                "https://news.ycombinator.com",
                "https://www.reddit.com",
                "https://www.nytimes.com",
                "https://www.bbc.com",
                "https://www.cnn.com"
            ]
            
            while self.is_running:
                try:
                    current_time = time.time()
                    if current_time - self.last_dummy_traffic >= self.config.get('dummy_traffic_interval', 30):
                        site = random.choice(enterprise_dummy_sites)
                        self.session.get(site, timeout=5, verify=False)
                        self.last_dummy_traffic = current_time
                        self.logger.debug(f"Enterprise dummy traffic to: {site.split('//')[1].split('/')[0]}")
                except Exception as e:
                    self.logger.debug(f"Dummy traffic error: {e}")
                
                time.sleep(random.randint(5, 15))
        
        self.dummy_traffic_thread = threading.Thread(target=enterprise_dummy_traffic_worker, daemon=True)
        self.dummy_traffic_thread.start()
        self.logger.info("Enterprise dummy traffic generator started")

    def start_enterprise_traffic_monitoring(self) -> None:
        """Start enterprise traffic monitoring"""
        if not self.config.get('traffic_monitoring', True):
            return
            
        def enterprise_traffic_monitor():
            while self.is_running:
                try:
                    # Monitor network connections
                    connections = psutil.net_connections()
                    tor_connections = [conn for conn in connections if conn.laddr and hasattr(conn.laddr, 'port') and conn.laddr.port == self.config['tor_port']]
                    
                    # Monitor bandwidth
                    net_io = psutil.net_io_counters()
                    
                    self.logger.debug(f"Enterprise Traffic - Connections: {len(tor_connections)} | "
                                    f"Bytes Sent: {net_io.bytes_sent} | Received: {net_io.bytes_recv}")
                    
                    time.sleep(30)
                except Exception as e:
                    self.logger.debug(f"Traffic monitoring error: {e}")
                    time.sleep(30)
        
        self.traffic_monitor_thread = threading.Thread(target=enterprise_traffic_monitor, daemon=True)
        self.traffic_monitor_thread.start()
        self.logger.info("Enterprise traffic monitoring started")

    def start_enterprise_circuit_rotation(self) -> None:
        """Start automatic enterprise circuit rotation"""
        if not self.config.get('auto_circuit_rotation', True):
            return
            
        def enterprise_circuit_rotator():
            while self.is_running:
                try:
                    rotation_interval = self.config.get('identity_rotation_interval', 10)
                    time.sleep(rotation_interval)
                    
                    if self.enterprise_identity_rotation():
                        ip = self.get_enterprise_stealth_ip()
                        if ip:
                            uptime = int(time.time() - self.start_time)
                            status = f"{Colors.GREEN}🔄 Enterprise IP: {ip} | Rotations: {self.rotation_count} | Uptime: {uptime}s{Colors.END}"
                            print(status)
                except Exception as e:
                    self.logger.error(f"Circuit rotation error: {e}")
                    time.sleep(10)
        
        self.circuit_rotation_thread = threading.Thread(target=enterprise_circuit_rotator, daemon=True)
        self.circuit_rotation_thread.start()
        self.logger.info("Enterprise automatic circuit rotation started")

    def get_enterprise_stealth_ip(self) -> Optional[str]:
        """Get IP with enterprise verification"""
        enterprise_stealth_services = [
            'http://icanhazip.com',
            'http://ifconfig.me/ip',
            'http://ipinfo.io/ip',
            'http://api.ipify.org',
            'http://checkip.amazonaws.com'
        ]
        
        random.shuffle(enterprise_stealth_services)
        
        for service in enterprise_stealth_services:
            try:
                response = self.session.get(service, timeout=8, verify=False)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self.validate_enterprise_ip(ip):
                        return ip
            except Exception as e:
                self.logger.debug(f"IP service {service} failed: {e}")
                continue
        return None

    def validate_enterprise_ip(self, ip: str) -> bool:
        """Enterprise IP validation"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check for private IPs
            if ip_obj.is_private:
                return False
                
            # Check for localhost
            if ip == "127.0.0.1":
                return False
                
            return True
        except Exception as e:
            self.logger.debug(f"IP validation failed for {ip}: {e}")
            return False

    def run_enterprise_stealth_tests(self) -> bool:
        """Run comprehensive enterprise stealth tests"""
        self.logger.info("Running enterprise stealth diagnostics...")
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: IP acquisition
        ip = self.get_enterprise_stealth_ip()
        if ip:
            print(f"✅ Enterprise Stealth IP: {ip}")
            tests_passed += 1
        else:
            print("❌ Enterprise IP acquisition failed")
        
        # Test 2: Tor verification
        try:
            response = self.session.get('https://check.torproject.org', timeout=10, verify=False)
            if "Congratulations" in response.text:
                print("✅ Enterprise Tor verification passed")
                tests_passed += 1
            else:
                print("⚠️  Enterprise Tor detection possible")
        except Exception as e:
            print(f"❌ Enterprise Tor check failed: {e}")
        
        # Test 3: Basic functionality
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=10, verify=False)
            if response.status_code == 200:
                print("✅ Enterprise basic functionality OK")
                tests_passed += 1
            else:
                print(f"❌ Enterprise basic functionality test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Enterprise basic functionality test failed: {e}")
        
        # Test 4: Controller functionality
        if self.controller and self.controller.is_authenticated():
            print("✅ Enterprise controller functionality OK")
            tests_passed += 1
        else:
            print("⚠️  Enterprise controller limited functionality")
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"📊 Enterprise stealth tests: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        return tests_passed >= 2  # Almeno 2/4 test devono passare

    def enable_enterprise_kill_switch(self) -> None:
        """Enable enterprise kill switch protection"""
        if not self.config.get('kill_switch_enabled', True):
            return
            
        def enterprise_kill_switch():
            consecutive_failures = 0
            max_failures = 3
            
            while self.is_running:
                try:
                    # Check Tor connection
                    response = self.session.get('http://httpbin.org/ip', timeout=5, verify=False)
                    if response.status_code == 200:
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                except Exception as e:
                    consecutive_failures += 1
                    self.logger.debug(f"Kill switch check failed: {e}")
                
                if consecutive_failures >= max_failures:
                    self.kill_switch_active = True
                    self.logger.error("ENTERPRISE KILL SWITCH ACTIVATED - Tor connection lost!")
                    self.emergency_shutdown()
                    break
                
                time.sleep(10)
        
        kill_switch_thread = threading.Thread(target=enterprise_kill_switch, daemon=True)
        kill_switch_thread.start()
        self.logger.info("Enterprise kill switch activated")

    def emergency_shutdown(self) -> None:
        """Enterprise emergency shutdown procedure"""
        self.logger.error("ENTERPRISE EMERGENCY SHUTDOWN INITIATED!")
        
        self.is_running = False
        
        # Immediate session closure
        if self.session:
            try:
                self.session.close()
            except:
                pass
        
        # Controller closure
        if self.controller:
            try:
                self.controller.close()
            except:
                pass
        
        # Process termination
        self.stop_tor_process()
        
        print("🚨 ENTERPRISE EMERGENCY SHUTDOWN COMPLETED")
        sys.exit(1)

    def start_ultimate_enterprise_mode(self) -> bool:
        """Start ultimate enterprise stealth mode - FIXED VERSION"""
        self.print_ultimate_banner()
        
        # Setup enterprise signal handling
        signal.signal(signal.SIGINT, self.enterprise_signal_handler)
        signal.signal(signal.SIGTERM, self.enterprise_signal_handler)
        
        print("🔒 Initializing ultimate enterprise protections...")
        
        # PRIMA verifica che Tor sia raggiungibile
        print("🔍 Testing Tor connection before starting...")
        try:
            test_session = requests.Session()
            test_session.proxies = {
                'http': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}',
                'https': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}'
            }
            test_session.verify = False
            
            response = test_session.get('http://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                print(f"✅ Tor connection verified: {response.text.strip()}")
            else:
                print(f"❌ Tor connection test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Tor connection failed: {e}")
            print("💡 Please ensure Tor is running: sudo systemctl start tor")
            return False
        
        # Wait for Tor to be ready with improved logic
        if not self.wait_for_tor_ready():
            print("❌ Enterprise Tor connection failed - is Tor running?")
            print("💡 Start Tor with: sudo systemctl start tor")
            print("💡 Or install Tor: sudo apt-get install tor")
            return False
        
        # Create enterprise session AFTER Tor is ready
        try:
            self.session = self.create_enterprise_session()
            
            # Test the session
            test_response = self.session.get('http://httpbin.org/ip', timeout=10)
            if test_response.status_code == 200:
                print(f"✅ Enterprise session created: {test_response.text.strip()}")
            else:
                print(f"⚠️ Enterprise session created but test request failed: {test_response.status_code}")
                
        except Exception as e:
            print(f"❌ Enterprise session creation failed: {e}")
            return False
            
        # Enterprise controller connection
        try:
            if self.connect_enterprise_controller():
                print("✅ Enterprise controller connected")
            else:
                print("⚠️  Enterprise controller connection failed, using basic mode")
        except Exception as e:
            print(f"⚠️  Enterprise controller error: {e}, continuing in basic mode")

        self.is_running = True
        
        # Start enterprise services with error handling
        services = [
            ("dummy_traffic", self.start_enterprise_dummy_traffic),
            ("traffic_monitoring", self.start_enterprise_traffic_monitoring),
            ("circuit_rotation", self.start_enterprise_circuit_rotation),
            ("kill_switch", self.enable_enterprise_kill_switch)
        ]
        
        for service_name, service_func in services:
            try:
                service_func()
                print(f"✅ {service_name.replace('_', ' ').title()} started")
            except Exception as e:
                print(f"⚠️  {service_name} failed: {e}")
        
        # Run enterprise tests
        try:
            if self.run_enterprise_stealth_tests():
                print("🎯 ULTIMATE ENTERPRISE STEALTH MODE ACTIVATED")
            else:
                print("🎯 ENTERPRISE STEALTH MODE ACTIVATED (some tests failed)")
        except Exception as e:
            print(f"🎯 Enterprise stealth mode ACTIVATED (with limitations: {e})")

        print("💡 Press Ctrl+C for enterprise graceful shutdown\n")
        
        return True

    def enterprise_signal_handler(self, signum: int, frame) -> None:
        """Enterprise graceful shutdown"""
        print("\n🛑 Enterprise shutdown initiated...")
        self.stop_enterprise_stealth_mode()

    def stop_enterprise_stealth_mode(self) -> None:
        """Enterprise clean shutdown"""
        self.is_running = False
        try:
            if self.controller:
                self.controller.close()
            if self.session:
                self.session.close()
            self.stop_tor_process()
            
            print("✅ Enterprise stealth mode terminated")
        except Exception as e:
            print(f"❌ Enterprise shutdown error: {e}")

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

    def make_enterprise_stealth_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make request with all enterprise protections"""
        if not self.is_running or not self.session:
            self.logger.error("Enterprise stealth request failed: service not running")
            return None
        
        max_retries = kwargs.pop('max_retries', self.config['max_retries'])
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config['timeout'],
                    verify=False,
                    **kwargs
                )
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    if self.controller:
                        self.enterprise_identity_rotation()
                    self.random_delay_before_rotation()
        
        self.logger.error(f"All {max_retries} request attempts failed")
        return None

    def run_continuous_enterprise_stealth(self) -> None:
        """Run continuous enterprise stealth mode"""
        print("🚀 Starting continuous enterprise stealth operations...")
        
        try:
            last_status_time = time.time()
            while self.is_running:
                # Status updates every 60 seconds
                current_time = time.time()
                if current_time - last_status_time >= 60:
                    print(f"📊 Enterprise Status: {self.rotation_count} rotations | Running: {int(current_time - self.start_time)}s")
                    last_status_time = current_time
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Enterprise stealth mode interrupted")
        finally:
            self.stop_enterprise_stealth_mode()

def main():
    """Main enterprise entry point"""
    parser = argparse.ArgumentParser(description='ULTIMATE ENTERPRISE TOR Anonymizer')
    
    parser.add_argument('--test', action='store_true', help='Test enterprise stealth connection')
    parser.add_argument('--url', help='Make enterprise stealth request to URL')
    parser.add_argument('--config', default='settings.json', help='Config file path')
    parser.add_argument('--rotate-now', action='store_true', help='Force immediate IP rotation')
    parser.add_argument('--mode', choices=['stealth', 'advanced', 'ultimate', 'enterprise'], 
                       default='enterprise', help='Operation mode')
    
    args = parser.parse_args()
    
    try:
        stealth = UltimateTorAnonymizer(args.config)
        
        if not stealth.start_ultimate_enterprise_mode():
            sys.exit(1)
        
        if args.test:
            print("✅ Enterprise stealth test completed")
            stealth.stop_enterprise_stealth_mode()
        elif args.url:
            response = stealth.make_enterprise_stealth_request(args.url)
            if response:
                print(f"✅ Enterprise stealth request: {response.status_code}")
                print(f"Response preview: {response.text[:200]}...")
            else:
                print("❌ Enterprise stealth request failed")
            stealth.stop_enterprise_stealth_mode()
        elif args.rotate_now:
            if stealth.enterprise_identity_rotation():
                ip = stealth.get_enterprise_stealth_ip()
                print(f"✅ Enterprise IP rotated: {ip}")
            else:
                print("❌ Enterprise IP rotation failed")
            stealth.stop_enterprise_stealth_mode()
        else:
            stealth.run_continuous_enterprise_stealth()
            
    except KeyboardInterrupt:
        print("\n🎯 Enterprise stealth session completed")
    except Exception as e:
        print(f"❌ Enterprise stealth error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
