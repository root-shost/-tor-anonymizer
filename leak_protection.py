#!/usr/bin/env python3
"""
BROWSER FINGERPRINT PROTECTION MODULE v3.0 - ENTERPRISE EDITION
Advanced anti-fingerprinting techniques for ultimate anonymity
"""

import random
import time
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import platform
import sys

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AdvancedFingerprintingProtection:
    """
    Comprehensive browser fingerprinting protection
    ENTERPRISE VERSION - Fixed implementation
    """
    
    def __init__(self, config_path: str = "fingerprint_protection.json"):
        self.config_path = config_path
        self.logger = self.setup_enterprise_logging()
        self.config = self.load_config()
        self.initialized = False
        
        try:
            self.validate_environment()
            self.initialized = True
            self.logger.info("Enterprise fingerprint protection initialized")
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise
    
    def setup_enterprise_logging(self):
        """Setup enterprise logging with proper error handling"""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            logger = logging.getLogger('EnterpriseFingerprintProtection')
            logger.setLevel(logging.INFO)
            
            # Avoid duplicate handlers
            if not logger.handlers:
                handler = logging.FileHandler('logs/fingerprint_protection.log', encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            
            return logger
        except Exception as e:
            # Fallback to basic logging
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger('EnterpriseFingerprintProtection')
    
    def validate_environment(self):
        """Validate that required environment is available"""
        self.logger.info("Validating fingerprint protection environment...")
        
        # Check if we can write to log directory
        try:
            test_file = Path("logs/test_write.tmp")
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            self.logger.warning(f"Log directory not writable: {e}")
        
        self.logger.info("Environment validation completed")
    
    def load_config(self) -> Dict[str, Any]:
        """Load fingerprint protection configuration with error handling"""
        default_config = {
            "canvas_noise": True,
            "webgl_spoofing": True,
            "font_masking": True,
            "timezone_spoofing": True,
            "screen_resolution_spoofing": True,
            "audio_context_spoofing": True,
            "hardware_concurrency_spoofing": True,
            "language_spoofing": True,
            "platform_spoofing": True
        }
        
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                self.logger.info("Fingerprint protection configuration loaded successfully")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Config load failed: {e}, using defaults")
        else:
            self.logger.info("No config file found, using default fingerprint protection settings")
            # Create default config file
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                self.logger.info("Default fingerprint protection configuration created")
            except IOError as e:
                self.logger.warning(f"Could not create config file: {e}")
            
        return default_config
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """Generate stealth headers with advanced fingerprint protection"""
        if not self.initialized:
            self.logger.warning("Fingerprint protection not initialized, using basic headers")
            return self.get_fallback_headers()
        
        try:
            base_headers = {
                'User-Agent': self.get_advanced_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': self.get_random_accept_language(),
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                'TE': 'trailers'
            }
            
            # Add additional fingerprint-resistant headers (with error handling)
            if random.random() > 0.5:
                try:
                    base_headers['Sec-CH-UA'] = self.get_sec_ch_ua()
                    base_headers['Sec-CH-UA-Mobile'] = '?0'
                    base_headers['Sec-CH-UA-Platform'] = self.get_random_platform_header()
                except Exception as e:
                    self.logger.debug(f"Sec-CH-UA headers failed: {e}")
            
            self.logger.debug("Stealth headers generated successfully")
            return base_headers
            
        except Exception as e:
            self.logger.error(f"Stealth headers generation failed: {e}")
            return self.get_fallback_headers()
    
    def get_fallback_headers(self) -> Dict[str, str]:
        """Get fallback headers in case of errors"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    def get_advanced_user_agent(self) -> str:
        """Generate advanced user agent with randomization and error handling"""
        try:
            platforms = [
                # Windows
                {
                    "template": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                    "type": "chrome"
                },
                {
                    "template": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}",
                    "type": "firefox"
                },
                {
                    "template": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/{version} Safari/537.36",
                    "type": "edge"
                },
                
                # macOS
                {
                    "template": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                    "type": "chrome"
                },
                {
                    "template": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}",
                    "type": "firefox"
                },
                
                # Linux
                {
                    "template": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                    "type": "chrome"
                },
                {
                    "template": "Mozilla/5.0 (X11; Linux x86_64; rv:{version}) Gecko/20100101 Firefox/{version}",
                    "type": "firefox"
                }
            ]
            
            platform_info = random.choice(platforms)
            template = platform_info["template"]
            browser_type = platform_info["type"]
            
            # Version randomization based on browser type
            if browser_type == "chrome":
                version = f"{random.randint(120, 130)}.0.{random.randint(1000, 9999)}.{random.randint(100, 999)}"
            elif browser_type == "firefox":
                version = f"{random.randint(120, 130)}.0"
            else:  # edge
                version = f"{random.randint(120, 130)}.0.{random.randint(1000, 9999)}.0"
            
            user_agent = template.format(version=version)
            self.logger.debug(f"Generated User-Agent: {user_agent[:50]}...")
            return user_agent
            
        except Exception as e:
            self.logger.error(f"User-Agent generation failed: {e}")
            return "Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0"
    
    def get_random_accept_language(self) -> str:
        """Generate random accept language header"""
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-CA,en;q=0.9',
            'en-AU,en;q=0.9',
            'de-DE,de;q=0.9,en;q=0.8',
            'fr-FR,fr;q=0.9,en;q=0.8',
            'es-ES,es;q=0.9,en;q=0.8',
            'ja-JP,ja;q=0.9,en;q=0.8'
        ]
        return random.choice(languages)
    
    def get_sec_ch_ua(self) -> str:
        """Generate Sec-CH-UA header for fingerprint resistance"""
        chrome_versions = [
            '"Chromium";v="128", "Google Chrome";v="128", "Not=A?Brand";v="99"',
            '"Chromium";v="127", "Google Chrome";v="127", "Not=A?Brand";v="99"',
            '"Chromium";v="126", "Google Chrome";v="126", "Not=A?Brand";v="99"'
        ]
        return random.choice(chrome_versions)
    
    def get_random_platform_header(self) -> str:
        """Generate random platform header"""
        platforms = ['"Windows"', '"macOS"', '"Linux"']
        return random.choice(platforms)
    
    def generate_canvas_fingerprint_noise(self) -> Dict[str, Any]:
        """Generate canvas fingerprint noise with error handling"""
        if not self.config.get('canvas_noise', True):
            return {}
        
        try:
            return {
                'canvas_noise_level': random.randint(1, 5),
                'canvas_data_uri_spoofing': True,
                'webgl_parameter_spoofing': True,
                'timestamp': int(time.time())
            }
        except Exception as e:
            self.logger.error(f"Canvas noise generation failed: {e}")
            return {}
    
    def spoof_webgl_parameters(self) -> Dict[str, Any]:
        """Spoof WebGL parameters with error handling"""
        if not self.config.get('webgl_spoofing', True):
            return {}
        
        try:
            return {
                'webgl_vendor': random.choice(['Google Inc.', 'Intel Inc.', 'NVIDIA Corporation']),
                'webgl_renderer': random.choice([
                    'ANGLE (Intel, Intel(R) UHD Graphics 630 (0x000059A2) Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver'
                ]),
                'webgl_unmasked_vendor': 'Google Inc.',
                'webgl_unmasked_renderer': 'Google SwiftShader'
            }
        except Exception as e:
            self.logger.error(f"WebGL spoofing failed: {e}")
            return {}
    
    def mask_fonts(self) -> Dict[str, Any]:
        """Font masking techniques with error handling"""
        if not self.config.get('font_masking', True):
            return {}
        
        try:
            common_fonts = [
                'Arial', 'Helvetica', 'Times New Roman', 'Courier New',
                'Verdana', 'Georgia', 'Palatino', 'Garamond', 'Bookman',
                'Comic Sans MS', 'Trebuchet MS', 'Arial Black', 'Impact'
            ]
            
            return {
                'font_list': random.sample(common_fonts, random.randint(5, 10)),
                'font_hash_spoofing': True
            }
        except Exception as e:
            self.logger.error(f"Font masking failed: {e}")
            return {}
    
    def spoof_timezone(self) -> Dict[str, Any]:
        """Spoof timezone information with error handling"""
        if not self.config.get('timezone_spoofing', True):
            return {}
        
        try:
            timezones = [
                'America/New_York', 'America/Los_Angeles', 'Europe/London',
                'Europe/Paris', 'Asia/Tokyo', 'Australia/Sydney',
                'Europe/Berlin', 'America/Chicago', 'Asia/Singapore'
            ]
            
            return {
                'timezone': random.choice(timezones),
                'timezone_offset': random.randint(-720, 720),  # minutes from UTC
                'dst_offset': random.randint(0, 120)  # daylight savings offset
            }
        except Exception as e:
            self.logger.error(f"Timezone spoofing failed: {e}")
            return {}
    
    def spoof_screen_resolution(self) -> Dict[str, Any]:
        """Spoof screen resolution with error handling"""
        if not self.config.get('screen_resolution_spoofing', True):
            return {}
        
        try:
            resolutions = [
                {'width': 1920, 'height': 1080, 'depth': 24},
                {'width': 1366, 'height': 768, 'depth': 24},
                {'width': 1536, 'height': 864, 'depth': 24},
                {'width': 1440, 'height': 900, 'depth': 24},
                {'width': 1280, 'height': 720, 'depth': 24}
            ]
            
            return random.choice(resolutions)
        except Exception as e:
            self.logger.error(f"Screen resolution spoofing failed: {e}")
            return {'width': 1920, 'height': 1080, 'depth': 24}
    
    def get_browser_fingerprint_config(self) -> Dict[str, Any]:
        """Get complete browser fingerprint configuration for Selenium/Playwright - NUOVO METODO AGGIUNTO"""
        if not self.initialized:
            self.logger.warning("Fingerprint protection not initialized, using basic config")
            return self.get_fallback_fingerprint_config()
        
        try:
            fingerprint_config = {
                'user_agent': self.get_advanced_user_agent(),
                'viewport': self.spoof_screen_resolution(),
                'timezone': self.spoof_timezone(),
                'headers': self.get_stealth_headers(),
                'webgl': self.spoof_webgl_parameters(),
                'canvas': self.generate_canvas_fingerprint_noise(),
                'fonts': self.mask_fonts(),
                'languages': [lang.split(';')[0] for lang in self.get_random_accept_language().split(',')],
                'platform': platform.system().lower(),
                'hardware': {
                    'concurrency': random.randint(4, 16) if self.config.get('hardware_concurrency_spoofing', True) else None,
                    'memory': random.choice([4, 8, 16]),
                    'cores': random.randint(2, 8)
                },
                'audio': {
                    'context_spoofing': self.config.get('audio_context_spoofing', True)
                },
                'metadata': {
                    'generated_at': time.time(),
                    'protection_level': 'enterprise',
                    'version': '3.0.0'
                }
            }
            
            self.logger.info("Browser fingerprint configuration generated successfully")
            return fingerprint_config
            
        except Exception as e:
            self.logger.error(f"Browser fingerprint config generation failed: {e}")
            return self.get_fallback_fingerprint_config()
    
    def get_fallback_fingerprint_config(self) -> Dict[str, Any]:
        """Fallback fingerprint configuration"""
        return {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0',
            'viewport': {'width': 1920, 'height': 1080, 'depth': 24},
            'timezone': 'America/New_York',
            'headers': self.get_fallback_headers(),
            'languages': ['en-US', 'en'],
            'platform': 'windows',
            'metadata': {
                'generated_at': time.time(),
                'protection_level': 'fallback',
                'version': '3.0.0'
            }
        }
    
    def get_comprehensive_protection(self) -> Dict[str, Any]:
        """Get comprehensive fingerprint protection settings with error handling"""
        if not self.initialized:
            self.logger.error("Cannot generate protection: module not initialized")
            return {}
        
        self.logger.info("Generating comprehensive fingerprint protection...")
        
        try:
            protections = {
                'headers': self.get_stealth_headers(),
                'canvas_protection': self.generate_canvas_fingerprint_noise(),
                'webgl_protection': self.spoof_webgl_parameters(),
                'font_protection': self.mask_fonts(),
                'timezone_protection': self.spoof_timezone(),
                'screen_protection': self.spoof_screen_resolution(),
                'audio_protection': {
                    'audio_context_spoofing': self.config.get('audio_context_spoofing', True)
                },
                'hardware_protection': {
                    'hardware_concurrency': random.randint(4, 16) if self.config.get('hardware_concurrency_spoofing', True) else None,
                    'device_memory': random.choice([4, 8, 16])
                },
                'browser_fingerprint_config': self.get_browser_fingerprint_config(),  # AGGIUNTO
                'metadata': {
                    'generated_at': time.time(),
                    'version': '3.0.0',
                    'protection_level': 'enterprise'
                }
            }
            
            self.logger.info("Fingerprint protection configuration generated successfully")
            return protections
            
        except Exception as e:
            self.logger.error(f"Comprehensive protection generation failed: {e}")
            return {
                'headers': self.get_fallback_headers(),
                'browser_fingerprint_config': self.get_fallback_fingerprint_config(),  # AGGIUNTO
                'metadata': {
                    'generated_at': time.time(),
                    'version': '3.0.0',
                    'protection_level': 'fallback',
                    'error': str(e)
                }
            }

def main():
    """Test fingerprint protection with enhanced error handling"""
    print(f"{Colors.BLUE}🔍 Testing Enterprise Fingerprint Protection...{Colors.END}")
    
    try:
        protector = AdvancedFingerprintingProtection()
        
        if not protector.initialized:
            print(f"{Colors.RED}❌ Fingerprint protection initialization failed{Colors.END}")
            return False
        
        protections = protector.get_comprehensive_protection()
        
        if protections:
            print(f"{Colors.GREEN}✅ Fingerprint protection configured successfully{Colors.END}")
            print(f"   • Protection level: {protections.get('metadata', {}).get('protection_level', 'unknown')}")
            print(f"   • Components: {len(protections) - 1} protection layers")
            print(f"   • User-Agent: {protections['headers']['User-Agent'][:60]}...")
            
            # Test nuovo metodo
            browser_config = protector.get_browser_fingerprint_config()
            print(f"   • Browser Config: {browser_config['viewport']['width']}x{browser_config['viewport']['height']}")
            
            return True
        else:
            print(f"{Colors.RED}❌ Fingerprint protection configuration failed{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Fingerprint protection test failed: {e}{Colors.END}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
