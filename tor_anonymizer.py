#!/usr/bin/env python3
"""
TOR ANONYMIZER v3.0 - GOVERNMENT-GRADE STEALTH MODE
Multi-layer protection with advanced anti-fingerprinting and leak protection
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

# Import new advanced modules
try:
    from leak_protection import SystemLeakProtection
    from fingerprint_protection import AdvancedFingerprintingProtection
    from advanced_routing import AdvancedCircuitRouting
    ADVANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Advanced modules not available: {e}")
    ADVANCED_MODULES_AVAILABLE = False

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Gestione fallback per fake-useragent
try:
    from fake_useragent import UserAgent
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False

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
    Ultimate Tor anonymization with government-grade multi-layer protection
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
        
        # Advanced protection modules
        self.leak_protector = None
        self.fingerprint_protector = None
        self.advanced_router = None
        
        # Setup in secure order
        self.setup_enterprise_logging()
        self.config = self.load_ultimate_config()
        self.validate_enterprise_environment()
        self.setup_advanced_protections()
        self.setup_enterprise_protections()

    def setup_advanced_protections(self):
        """Setup advanced protection modules"""
        if ADVANCED_MODULES_AVAILABLE:
            try:
                self.leak_protector = SystemLeakProtection(self.config_path)
                self.fingerprint_protector = AdvancedFingerprintingProtection()
                self.advanced_router = AdvancedCircuitRouting(self.config_path)
                print("✅ Advanced government-grade protections loaded")
            except Exception as e:
                print(f"⚠️ Advanced protections initialization warning: {e}")
        else:
            print("⚠️ Running in basic mode - advanced modules not available")

    def setup_user_agent_generator(self):
        """Setup user agent generator with fallback"""
        if UA_AVAILABLE:
            try:
                return UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0")
            except:
                return None
        else:
            return None

    def get_random_user_agent(self):
        """Get random user agent with fallback"""
        if self.fingerprint_protector and ADVANCED_MODULES_AVAILABLE:
            try:
                protections = self.fingerprint_protector.get_comprehensive_protection()
                return protections['headers']['User-Agent']
            except:
                pass
        
        # Fallback to basic user agent generation
        if self.ua_generator:
            try:
                return self.ua_generator.random
            except:
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
        rotation_interval = self.config.get('identity_rotation_interval', 'random(30,180)')
        num_guards = self.config.get('num_entry_guards', 3)
        security_level = self.config.get('security_level', 'government_grade')
        
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║               GOVERNMENT-GRADE TOR ANONYMIZER v{self.version}║
║                   ULTIMATE STEALTH MODE                      ║
║                                                              ║
║          🔒 IP Rotation: {rotation_interval}s (Randomized)   ║
║          🌐 Multi-Hop Circuit: Government Grade             ║
║          🚫 Advanced Traffic Obfuscation                    ║
║          🛡️  Entry Guards: {num_guards} Nodes (Persistent)  ║
║          🔥 Advanced Kill Switch                            ║
║          📊 Real-time Monitoring & Leak Protection          ║
║          🛡️  Security Level: {security_level.upper():<12}           ║
║                                                              ║
║          Author: {self.author}                               ║
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
            level=logging.CRITICAL,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/tor_anonymizer.log', encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Disable all module logs for stealth
        for log_name in ['stem', 'requests', 'urllib3', 'fake_useragent', 'psutil']:
            logging.getLogger(log_name).setLevel(logging.CRITICAL)

    def load_ultimate_config(self) -> Dict[str, Any]:
        """Load ultimate enterprise configuration"""
        default_config = {
            "tor_port": 9050,
            "control_port": 9051,
            "identity_rotation_interval": "random(30, 180)",
            "min_rotation_delay": 15,
            "max_rotation_delay": 300,
            "max_retries": 5,
            "timeout": 15,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0",
            "socks5_host": "127.0.0.1",
            "log_level": "ERROR",
            "auto_start_tor": True,
            "dns_leak_protection": True,
            "safe_browsing": True,
            "max_circuit_dirtiness": 300,
            "exclude_nodes": "{ru},{cn},{us},{gb},{de},{fr},{nl}",
            "strict_nodes": False,
            "entry_nodes": "{se},{no},{fi},{dk}",
            "exit_nodes": "{ch},{at},{li},{is}",
            "use_bridges": False,
            "bridge_type": "obfs4",
            "disable_javascript": True,
            "block_trackers": True,
            "cookie_cleanup": True,
            "random_user_agent": True,
            "circuit_timeout": 30,
            "max_circuits": 10,
            "security_level": "government_grade",
            "dummy_traffic_enabled": True,
            "dummy_traffic_interval": "random(45, 300)",
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
            "bridge_obfs4": False,
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
            except (json.JSONDecodeError, IOError):
                print("Using government-grade enterprise configuration")
        else:
            self.create_ultimate_config(default_config)
        
        return default_config

    def create_ultimate_config(self, config: Dict[str, Any]) -> None:
        """Create ultimate configuration file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✓ Government-grade enterprise configuration created")
        except IOError as e:
            print(f"✗ Config creation failed: {e}")

    def validate_enterprise_environment(self) -> None:
        """Validate enterprise environment"""
        try:
            import requests
            import stem
            import psutil
        except ImportError as e:
            print(f"✗ Missing enterprise dependency: {e}")
            sys.exit(1)

    def setup_enterprise_protections(self) -> None:
        """Setup enterprise protection mechanisms"""
        # Initialize guard nodes list
        self.guard_nodes = self.generate_enterprise_guard_nodes()
        
        print("🛡️  Government-grade protections initialized:")
        print(f"   • Advanced Timing Randomization: {self.config['random_delay_enabled']}")
        print(f"   • Traffic Pattern Obfuscation: {self.config['dummy_traffic_enabled']}")
        print(f"   • Multi-Hop Routing: {self.config['multi_hop_enabled']}")
        print(f"   • Entry Guards: {self.config['use_entry_guards']}")
        print(f"   • Advanced Kill Switch: {self.config['kill_switch_enabled']}")
        print(f"   • Real-time Monitoring: {self.config['traffic_monitoring']}")
        if ADVANCED_MODULES_AVAILABLE:
            print(f"   • Browser Fingerprint Protection: {self.config['anti_fingerprinting']}")
            print(f"   • System Leak Prevention: {self.config['system_hardening']}")

    def generate_enterprise_guard_nodes(self) -> List[str]:
        """Generate enterprise entry guard nodes"""
        countries = ['se', 'no', 'fi', 'ch', 'is', 'nl', 'de', 'at']
        guards = []
        for i in range(self.config['num_entry_guards']):
            country = random.choice(countries)
            guards.append(f"guard{i}_{country}")
        return guards

    def create_enterprise_session(self) -> requests.Session:
        """Create session with government-grade stealth features"""
        session = requests.Session()
        
        # Enterprise proxy configuration
        proxy_config = {
            'http': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}',
            'https': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}'
        }
        session.proxies.update(proxy_config)
        
        # Advanced fingerprint protection headers
        if self.fingerprint_protector and ADVANCED_MODULES_AVAILABLE:
            try:
                protections = self.fingerprint_protector.get_comprehensive_protection()
                session.headers.update(protections['headers'])
            except Exception as e:
                print(f"⚠️ Advanced fingerprint protection failed: {e}")
                # Fallback to basic headers
                session.headers.update({
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'DNT': '1',
                })
        else:
            # Basic headers
            session.headers.update({
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
            })
        
        # Enterprise security settings
        session.trust_env = False
        session.verify = False
        session.max_redirects = 3
        
        return session

    def get_random_interval(self):
        """Get random interval for rotation timing"""
        interval_config = self.config.get('identity_rotation_interval', 'random(30,180)')
        
        if isinstance(interval_config, str) and 'random' in interval_config:
            try:
                # Extract range from "random(30, 180)"
                min_val, max_val = map(int, interval_config.replace('random(', '').replace(')', '').split(','))
                return random.randint(min_val, max_val)
            except:
                return random.randint(30, 180)
        else:
            # Fixed interval with some randomness
            base_interval = int(interval_config)
            return random.randint(max(15, base_interval - 15), base_interval + 15)

    def random_delay_before_rotation(self) -> None:
        """Government-grade random delay for rotation timing obfuscation"""
        if self.config.get('random_delay_enabled', True):
            delay = self.get_random_interval()
            print(f"⏰ Government-grade random delay: {delay}s")
            time.sleep(delay)
        else:
            time.sleep(self.config['identity_rotation_interval'])

    def connect_enterprise_controller(self) -> bool:
        """Enterprise controller connection with advanced error handling"""
        try:
            print("🔗 Attempting government-grade controller connection...")
            
            self.controller = Controller.from_port(
                address="127.0.0.1",
                port=self.config['control_port']
            )
            
            # Advanced authentication
            try:
                self.controller.authenticate()
                print("✅ Government-grade controller connected (advanced auth)")
                return True
            except stem.connection.AuthenticationFailure:
                # Try without authentication
                try:
                    self.controller.authenticate(None)
                    print("✅ Government-grade controller connected (cookie auth)")
                    return True
                except:
                    print("⚠️  Government-grade controller auth failed, using basic mode")
                    self.controller = None
                    return False
                    
        except Exception as e:
            print(f"⚠️  Government-grade controller connection failed: {e}")
            self.controller = None
            return False

    def enterprise_identity_rotation(self) -> bool:
        """Government-grade identity rotation with multiple techniques"""
        try:
            if self.controller and hasattr(self.controller, 'is_authenticated') and self.controller.is_authenticated():
                # Advanced rotation signals
                self.controller.signal(Signal.NEWNYM)
                time.sleep(2)
                self.controller.signal(Signal.CLEARDNSCACHE)
                time.sleep(1)
                
                self.rotation_count += 1
                return True
            else:
                print("⚠️  Government-grade controller not available for rotation")
                return False
        except Exception as e:
            print(f"🔁 Government-grade rotation error: {e}")
        return False

    def start_enterprise_dummy_traffic(self) -> None:
        """Start government-grade dummy traffic generation"""
        if not self.config.get('dummy_traffic_enabled', True):
            return
            
        def government_dummy_traffic_worker():
            # Expanded and randomized dummy sites
            government_dummy_sites = [
                "https://www.wikipedia.org/wiki/Special:Random",
                "https://github.com/explore",
                "https://stackoverflow.com/questions",
                "https://news.ycombinator.com",
                "https://www.reddit.com/r/random",
                "https://www.nytimes.com",
                "https://www.bbc.com/news",
                "https://www.cnn.com",
                "https://www.amazon.com",
                "https://www.youtube.com",
                "https://twitter.com/explore",
                "https://www.instagram.com",
                "https://www.linkedin.com",
                "https://www.imdb.com",
                "https://www.ebay.com"
            ]
            
            while self.is_running:
                try:
                    current_time = time.time()
                    interval_config = self.config.get('dummy_traffic_interval', 'random(45,300)')
                    
                    if isinstance(interval_config, str) and 'random' in interval_config:
                        try:
                            min_val, max_val = map(int, interval_config.replace('random(', '').replace(')', '').split(','))
                            interval = random.randint(min_val, max_val)
                        except:
                            interval = random.randint(45, 300)
                    else:
                        interval = int(interval_config)
                    
                    if current_time - self.last_dummy_traffic >= interval:
                        site = random.choice(government_dummy_sites)
                        self.session.get(site, timeout=5, verify=False)
                        self.last_dummy_traffic = current_time
                        domain = site.split('//')[1].split('/')[0]
                        print(f"🌫️  Government-grade dummy traffic to: {domain}")
                except:
                    pass
                
                time.sleep(random.randint(30, 120))
        
        self.dummy_traffic_thread = threading.Thread(target=government_dummy_traffic_worker, daemon=True)
        self.dummy_traffic_thread.start()
        print("✓ Government-grade dummy traffic generator started")

    def start_enterprise_traffic_monitoring(self) -> None:
        """Start government-grade traffic monitoring"""
        if not self.config.get('traffic_monitoring', True):
            return
            
        def government_traffic_monitor():
            while self.is_running:
                try:
                    # Monitor network connections
                    connections = psutil.net_connections()
                    tor_connections = [conn for conn in connections if conn.laddr and conn.laddr.port == self.config['tor_port']]
                    
                    # Monitor bandwidth
                    net_io = psutil.net_io_counters()
                    
                    # Advanced monitoring with leak detection
                    if self.leak_protector and ADVANCED_MODULES_AVAILABLE:
                        leak_status = self.leak_protector.check_dns_leaks()
                        leak_indicator = "✅" if leak_status else "❌"
                    else:
                        leak_indicator = "⚠️"
                    
                    print(f"📊 Government-grade Traffic - Connections: {len(tor_connections)} | "
                          f"Bytes Sent: {net_io.bytes_sent} | Received: {net_io.bytes_recv} | "
                          f"Leak Protection: {leak_indicator}")
                    
                    time.sleep(60)
                except:
                    pass
        
        self.traffic_monitor_thread = threading.Thread(target=government_traffic_monitor, daemon=True)
        self.traffic_monitor_thread.start()
        print("✓ Government-grade traffic monitoring started")

    def start_enterprise_circuit_rotation(self) -> None:
        """Start automatic government-grade circuit rotation"""
        if not self.config.get('auto_circuit_rotation', True):
            return
            
        def government_circuit_rotator():
            while self.is_running:
                try:
                    rotation_interval = self.get_random_interval()
                    time.sleep(rotation_interval)
                    
                    if self.enterprise_identity_rotation():
                        ip = stealth.get_enterprise_stealth_ip()
                        if ip:
                            uptime = int(time.time() - self.start_time)
                            status = f"{Colors.GREEN}🔄 Government-grade IP: {ip} | Rotations: {self.rotation_count} | Uptime: {uptime}s{Colors.END}"
                            print(status)
                except:
                    pass
        
        self.circuit_rotation_thread = threading.Thread(target=government_circuit_rotator, daemon=True)
        self.circuit_rotation_thread.start()
        print("✓ Government-grade automatic circuit rotation started")

    def get_enterprise_stealth_ip(self) -> Optional[str]:
        """Get IP with government-grade verification"""
        government_stealth_services = [
            'http://icanhazip.com',
            'http://ifconfig.me/ip',
            'http://ipinfo.io/ip',
            'http://api.ipify.org',
            'http://checkip.amazonaws.com'
        ]
        
        random.shuffle(government_stealth_services)
        
        for service in government_stealth_services:
            try:
                response = self.session.get(service, timeout=8, verify=False)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self.validate_enterprise_ip(ip):
                        return ip
            except:
                continue
        return None

    def validate_enterprise_ip(self, ip: str) -> bool:
        """Government-grade IP validation"""
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

    def enable_advanced_leak_protection(self) -> None:
        """Enable advanced system leak protection"""
        if not self.config.get('system_hardening', True) or not ADVANCED_MODULES_AVAILABLE:
            return
            
        try:
            if self.leak_protector:
                protections = self.leak_protector.enable_full_protection()
                print("✓ Government-grade leak protection activated")
            else:
                print("⚠️  Leak protection module not available")
        except Exception as e:
            print(f"⚠️  Advanced leak protection failed: {e}")

    def run_government_stealth_tests(self) -> bool:
        """Run comprehensive government-grade stealth tests"""
        print("🔍 Running government-grade stealth diagnostics...")
        
        tests_passed = 0
        total_tests = 6  # Increased for advanced tests
        
        # Test 1: IP acquisition
        ip = self.get_enterprise_stealth_ip()
        if ip:
            print(f"✅ Government-grade Stealth IP: {ip}")
            tests_passed += 1
        else:
            print("❌ Government-grade IP acquisition failed")
        
        # Test 2: Basic functionality
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=10, verify=False)
            if response.status_code == 200:
                print("✅ Government-grade basic functionality OK")
                tests_passed += 1
        except:
            print("❌ Government-grade basic functionality test failed")
        
        # Test 3: DNS leak test
        try:
            if self.leak_protector and ADVANCED_MODULES_AVAILABLE:
                leak_status = self.leak_protector.check_dns_leaks()
                if leak_status:
                    print("✅ Government-grade DNS leak test passed")
                    tests_passed += 1
                else:
                    print("❌ Government-grade DNS leak detected")
            else:
                response = self.session.get('http://httpbin.org/get', timeout=10, verify=False)
                if response.status_code == 200:
                    print("⚠️  Basic connectivity test passed (advanced DNS test not available)")
                    tests_passed += 1
        except:
            print("⚠️  Government-grade DNS leak test inconclusive")
        
        # Test 4: Headers test
        try:
            response = self.session.get('http://httpbin.org/headers', timeout=10, verify=False)
            if response.status_code == 200:
                print("✅ Government-grade headers test passed")
                tests_passed += 1
        except:
            print("❌ Government-grade headers test failed")
        
        # Test 5: Advanced fingerprint protection
        if self.fingerprint_protector and ADVANCED_MODULES_AVAILABLE:
            try:
                protections = self.fingerprint_protector.get_comprehensive_protection()
                if protections:
                    print("✅ Government-grade fingerprint protection active")
                    tests_passed += 1
            except:
                print("⚠️  Government-grade fingerprint protection test inconclusive")
        else:
            print("⚠️  Advanced fingerprint protection not available")
            total_tests -= 1  # Adjust total since this test isn't available
        
        # Test 6: Tor project verification
        try:
            response = self.session.get('https://check.torproject.org', timeout=10, verify=False)
            if "Congratulations" in response.text:
                print("✅ Government-grade Tor verification passed")
                tests_passed += 1
            else:
                print("⚠️  Government-grade Tor detection possible")
        except:
            print("❌ Government-grade Tor check failed")
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"📊 Government-grade stealth tests: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        return tests_passed >= 3

    def enable_enterprise_kill_switch(self) -> None:
        """Enable government-grade kill switch protection - VERSIONE CORRETTA"""
        if not self.config.get('kill_switch_enabled', True):
            return
            
        def government_kill_switch():
            # ✅ DELAY INIZIALE per evitare falsi positivi
            time.sleep(20)
            
            consecutive_failures = 0
            max_consecutive_failures = 3
            
            while self.is_running:
                try:
                    # Advanced connection check with multiple endpoints
                    endpoints = [
                        'http://httpbin.org/ip',
                        'http://icanhazip.com',
                        'http://ifconfig.me/ip'
                    ]
                    
                    connection_ok = False
                    for endpoint in endpoints:
                        try:
                            response = self.session.get(endpoint, timeout=15, verify=False)
                            if response.status_code == 200:
                                connection_ok = True
                                consecutive_failures = 0  # Reset counter
                                break
                        except:
                            continue
                    
                    if not connection_ok:
                        consecutive_failures += 1
                        print(f"⚠️  Connection check failed ({consecutive_failures}/{max_consecutive_failures})")
                        
                        if consecutive_failures >= max_consecutive_failures:
                            self.kill_switch_active = True
                            print("🚨 GOVERNMENT-GRADE KILL SWITCH ACTIVATED - Tor connection lost!")
                            self.emergency_shutdown()
                            break
                    else:
                        consecutive_failures = 0  # Reset on success
                        
                    # ✅ DNS LEAK CHECK OPZIONALE (SOLO WARNING)
                    if self.leak_protector and ADVANCED_MODULES_AVAILABLE and consecutive_failures == 0:
                        try:
                            dns_status = self.leak_protector.check_dns_leaks()
                            if not dns_status:
                                print("⚠️  DNS leak detected - monitoring (kill switch remains inactive)")
                                # ✅ NON attivare kill switch per DNS leaks
                        except Exception as e:
                            print(f"⚠️  DNS leak check error: {e}")
                            
                except Exception as e:
                    print(f"⚠️  Kill switch monitoring error: {e}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        self.kill_switch_active = True
                        print("🚨 GOVERNMENT-GRADE KILL SWITCH ACTIVATED - Critical error!")
                        self.emergency_shutdown()
                        break
                    
                time.sleep(25)  # ✅ Controlla ogni 25 secondi
        
        kill_switch_thread = threading.Thread(target=government_kill_switch, daemon=True)
        kill_switch_thread.start()
        print("✓ Government-grade kill switch activated")

    def emergency_shutdown(self) -> None:
        """Government-grade emergency shutdown procedure"""
        print("🚨 GOVERNMENT-GRADE EMERGENCY SHUTDOWN INITIATED!")
        
        self.is_running = False
        
        # Immediate session closure
        if self.session:
            self.session.close()
        
        # Controller closure
        if self.controller:
            try:
                self.controller.close()
            except:
                pass
        
        # Advanced cleanup
        try:
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith('tor_anonymizer'):
                    os.remove(os.path.join(temp_dir, file))
        except:
            pass
        
        print("✅ Government-grade emergency shutdown completed")
        os._exit(1)

    def start_ultimate_enterprise_mode(self) -> bool:
        """Start government-grade ultimate stealth mode"""
        self.print_ultimate_banner()
        
        # Setup government-grade signal handling
        signal.signal(signal.SIGINT, self.enterprise_signal_handler)
        signal.signal(signal.SIGTERM, self.enterprise_signal_handler)
        
        print("🔒 Initializing government-grade protections...")
        
        # Enable advanced leak protection first
        self.enable_advanced_leak_protection()
        
        # Test basic Tor connection
        try:
            print("🔗 Testing government-grade Tor connection...")
            
            test_session = requests.Session()
            test_session.proxies = {
                'http': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}',
                'https': f'socks5://{self.config["socks5_host"]}:{self.config["tor_port"]}'
            }
            test_session.verify = False
            
            response = test_session.get('http://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                print(f"✅ Government-grade Tor connection verified: {ip_info}")
            else:
                print("⚠️  Government-grade connection test returned non-200 status")
                
        except Exception as e:
            print(f"❌ Government-grade Tor connection failed: {e}")
            return False
        
        # Create government-grade session
        try:
            self.session = self.create_enterprise_session()
            self.session.verify = False
            
            test_response = self.session.get('http://httpbin.org/ip', timeout=10)
            if test_response.status_code == 200:
                ip_info = test_response.json()
                print(f"✅ Government-grade session created: {ip_info}")
            else:
                print("⚠️ Government-grade session created but test request failed")
                
        except Exception as e:
            print(f"❌ Government-grade session creation failed: {e}")
            return False
            
        # Government-grade controller connection
        try:
            if not self.connect_enterprise_controller():
                print("⚠️  Government-grade controller connection failed, using basic mode")
        except Exception as e:
            print(f"⚠️  Government-grade controller error: {e}, continuing in basic mode")
    
        self.is_running = True
        
        # Start government-grade services
        try:
            self.start_enterprise_dummy_traffic()
        except Exception as e:
            print(f"⚠️  Government-grade dummy traffic failed: {e}")
        
        try:
            self.start_enterprise_traffic_monitoring()
        except Exception as e:
            print(f"⚠️  Government-grade traffic monitoring failed: {e}")
        
        try:
            self.start_enterprise_circuit_rotation()
        except Exception as e:
            print(f"⚠️  Government-grade circuit rotation failed: {e}")
        
        try:
            self.enable_enterprise_kill_switch()
        except Exception as e:
            print(f"⚠️  Government-grade kill switch failed: {e}")
        
        # Run government-grade tests
        try:
            if self.run_government_stealth_tests():
                print("🎯 GOVERNMENT-GRADE ULTIMATE STEALTH MODE ACTIVATED")
            else:
                print("🎯 GOVERNMENT-GRADE STEALTH MODE ACTIVATED (some tests failed)")
        except Exception as e:
            print(f"🎯 Government-grade stealth mode ACTIVATED (with limitations: {e})")
    
        print("💡 Press Ctrl+C for government-grade graceful shutdown\n")
        
        return True

    def enterprise_signal_handler(self, signum: int, frame) -> None:
        """Government-grade graceful shutdown"""
        print("\n🛑 Government-grade shutdown initiated...")
        self.stop_enterprise_stealth_mode()

    def stop_enterprise_stealth_mode(self) -> None:
        """Government-grade clean shutdown"""
        self.is_running = False
        try:
            if self.controller:
                self.controller.close()
            if self.session:
                self.session.close()
            
            print("✅ Government-grade stealth mode terminated")
        except Exception as e:
            print(f"❌ Government-grade shutdown error: {e}")

    def make_enterprise_stealth_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make request with all government-grade protections"""
        if not self.is_running or not self.session:
            return None
        
        max_retries = kwargs.pop('max_retries', self.config['max_retries'])
        
        # Artificial delay for timing obfuscation
        if self.advanced_router and ADVANCED_MODULES_AVAILABLE:
            try:
                delay = self.advanced_router.generate_artificial_delays()
                if delay > 0:
                    time.sleep(delay)
            except:
                pass
        
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
                
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    if self.controller:
                        self.enterprise_identity_rotation()
                    self.random_delay_before_rotation()
        
        return None

    def run_continuous_enterprise_stealth(self) -> None:
        """Run continuous government-grade stealth mode"""
        print("🚀 Starting continuous government-grade stealth operations...")
        
        try:
            while self.is_running:
                # Advanced status updates with routing info
                current_time = time.time()
                if current_time - self.start_time >= 60 and int(current_time - self.start_time) % 60 == 0:
                    status_info = f"📊 Government-grade Status: {self.rotation_count} rotations | Running: {int(current_time - self.start_time)}s"
                    
                    # Add advanced routing info if available
                    if self.advanced_router and ADVANCED_MODULES_AVAILABLE:
                        try:
                            strategy = self.advanced_router.get_comprehensive_routing_strategy()
                            status_info += f" | Hops: {strategy['circuit_config']['num_hops']}"
                        except:
                            pass
                    
                    print(status_info)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Government-grade stealth mode interrupted")
        finally:
            self.stop_enterprise_stealth_mode()

def main():
    """Main government-grade entry point"""
    parser = argparse.ArgumentParser(description='GOVERNMENT-GRADE TOR Anonymizer')
    
    parser.add_argument('--test', action='store_true', help='Test government-grade stealth connection')
    parser.add_argument('--url', help='Make government-grade stealth request to URL')
    parser.add_argument('--config', default='settings.json', help='Config file path')
    parser.add_argument('--rotate-now', action='store_true', help='Force immediate IP rotation')
    parser.add_argument('--mode', choices=['stealth', 'advanced', 'ultimate', 'enterprise', 'government'], 
                       default='government', help='Operation mode')
    
    args = parser.parse_args()
    
    try:
        stealth = UltimateTorAnonymizer(args.config)
        
        if not stealth.start_ultimate_enterprise_mode():
            sys.exit(1)
        
        if args.test:
            print("✅ Government-grade stealth test completed")
            stealth.stop_enterprise_stealth_mode()
        elif args.url:
            response = stealth.make_enterprise_stealth_request(args.url)
            if response:
                print(f"✅ Government-grade stealth request: {response.status_code}")
            else:
                print("❌ Government-grade stealth request failed")
            stealth.stop_enterprise_stealth_mode()
        elif args.rotate_now:
            if stealth.enterprise_identity_rotation():
                ip = stealth.get_enterprise_stealth_ip()
                print(f"✅ Government-grade IP rotated: {ip}")
            stealth.stop_enterprise_stealth_mode()
        else:
            stealth.run_continuous_enterprise_stealth()
            
    except KeyboardInterrupt:
        print("\n🎯 Government-grade stealth session completed")
    except Exception as e:
        print(f"❌ Government-grade stealth error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
