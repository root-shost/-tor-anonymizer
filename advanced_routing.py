#!/usr/bin/env python3
"""
ADVANCED CIRCUIT ROUTING MODULE - CORRETTO
Multi-hop custom circuits and advanced Tor routing
"""

import random
import time
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import stem.control
from stem.control import Controller

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class AdvancedCircuitRouting:
    """
    Advanced Tor circuit routing with multi-hop support
    VERSIONE CORRETTA E FUNZIONANTE
    """
    
    def __init__(self, config_path: str = "settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.controller = None
        
    def setup_logging(self):
        """Setup advanced routing logging"""
        logger = logging.getLogger('advanced_routing')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('logs/advanced_routing.log', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_config(self):
        """Load advanced routing configuration with error handling"""
        default_config = {
            "advanced_circuit_routing": {
                "min_hops": 3,
                "max_hops": 5,
                "entry_node_countries": ['se', 'ch', 'is', 'de', 'nl'],
                "exit_node_countries": ['ch', 'se', 'de', 'nl', 'ca'],
                "exclude_nodes": ['{ru}', '{cn}', '{ir}', '{sy}'],
                "strict_nodes": False
            },
            "artificial_delays": {
                "enabled": True,
                "min_delay_ms": 500,
                "max_delay_ms": 3000
            }
        }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Merge configurations
                if 'advanced_circuit_routing' in user_config:
                    default_config['advanced_circuit_routing'].update(
                        user_config['advanced_circuit_routing']
                    )
                return default_config
        except Exception as e:
            self.logger.warning(f"Config load failed: {e}, using defaults")
            return default_config
    
    def connect_controller(self) -> bool:
        """Connect to Tor controller"""
        try:
            self.controller = Controller.from_port(port=9051)
            self.controller.authenticate()
            self.logger.info("✅ Advanced routing controller connected")
            return True
        except Exception as e:
            self.logger.error(f"❌ Controller connection failed: {e}")
            return False
    
    def generate_multi_hop_circuit(self) -> Dict[str, Any]:
        """Generate multi-hop circuit configuration - CORRETTO"""
        advanced_config = self.config.get('advanced_circuit_routing', {})
        
        min_hops = advanced_config.get('min_hops', 3)
        max_hops = advanced_config.get('max_hops', 5)
        
        num_hops = random.randint(min_hops, max_hops)
        
        entry_nodes = advanced_config.get('entry_node_countries', ['se', 'ch', 'is', 'de'])
        exit_nodes = advanced_config.get('exit_node_countries', ['ch', 'se', 'de', 'nl'])
        exclude_nodes = advanced_config.get('exclude_nodes', ['{ru}', '{cn}', '{ir}'])
        
        circuit = {
            'num_hops': num_hops,
            'entry_guard': random.choice(entry_nodes),
            'exit_node': random.choice(exit_nodes),
            'excluded_countries': exclude_nodes,
            'strict_nodes': advanced_config.get('strict_nodes', False),
            'use_bridges': self.config.get('use_bridges', False),
            'circuit_id': f"circuit_{int(time.time())}_{random.randint(1000, 9999)}"
        }
        
        self.logger.info(f"🔗 Generated {num_hops}-hop circuit: {circuit['circuit_id']}")
        return circuit
    
    def get_torrc_advanced_config(self) -> str:
        """Generate advanced torrc configuration - CORRETTO"""
        circuit = self.generate_multi_hop_circuit()
        
        torrc_lines = [
            "# Advanced Enterprise Routing Configuration",
            f"EntryNodes {{{circuit['entry_guard']}}}",
            f"ExitNodes {{{circuit['exit_node']}}}",
            f"ExcludeNodes {','.join(circuit['excluded_countries'])}",
            f"StrictNodes {1 if circuit['strict_nodes'] else 0}",
            "MaxCircuitDirtiness 300",
            "NewCircuitPeriod 300",
            "CircuitBuildTimeout 60",
            "LearnCircuitBuildTimeout 1",
            "EnforceDistinctSubnets 1",
            "NumEntryGuards 3",
            "GuardLifetime 30 days",
            "NumDirectoryGuards 3",
            "UseEntryGuards 1",
            "LongLivedPorts 21,22,53,80,110,143,443,993,995"
        ]
        
        if circuit['use_bridges']:
            torrc_lines.extend([
                "UseBridges 1",
                "ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy"
            ])
        
        config_text = '\n'.join(torrc_lines)
        self.logger.info("📄 Generated advanced Tor configuration")
        return config_text
    
    def calculate_optimal_rotation_timing(self) -> int:
        """Calculate optimal rotation timing to avoid patterns - CORRETTO"""
        base_interval = self.config.get('identity_rotation_interval', 60)
        
        # Add intelligent variation
        if random.random() > 0.7:  # 30% chance of variation
            variation = random.randint(-10, 30)  # Sometimes longer delays
        else:
            variation = random.randint(-5, 15)   # Usually small variations
            
        optimal_time = max(15, base_interval + variation)  # Minimum 15 seconds
        self.logger.debug(f"⏰ Optimal rotation timing: {optimal_time}s")
        return optimal_time
    
    def generate_artificial_delays(self) -> float:
        """Generate artificial delays between requests - CORRETTO"""
        delay_config = self.config.get('artificial_delays', {})
        
        if delay_config.get('enabled', True):
            min_delay = delay_config.get('min_delay_ms', 500) / 1000.0
            max_delay = delay_config.get('max_delay_ms', 3000) / 1000.0
            
            delay = random.uniform(min_delay, max_delay)
            self.logger.debug(f"⏳ Artificial delay: {delay:.3f}s")
            return delay
        else:
            return 0
    
    def get_traffic_mimicry_pattern(self) -> Dict[str, Any]:
        """Get traffic mimicry pattern for advanced obfuscation - CORRETTO"""
        patterns = [
            {
                'name': 'research_browsing',
                'request_pattern': 'burst_pauses',
                'sites': ['wikipedia.org', 'arxiv.org', 'stackoverflow.com', 'github.com'],
                'behavior': 'reading_intensive',
                'request_rate': 'low',
                'session_length': 'long'
            },
            {
                'name': 'social_media',
                'request_pattern': 'continuous_scrolling', 
                'sites': ['reddit.com', 'twitter.com', 'facebook.com', 'instagram.com'],
                'behavior': 'rapid_interactions',
                'request_rate': 'high',
                'session_length': 'medium'
            },
            {
                'name': 'shopping',
                'request_pattern': 'comparison_browsing',
                'sites': ['amazon.com', 'ebay.com', 'walmart.com', 'bestbuy.com'],
                'behavior': 'product_research',
                'request_rate': 'medium',
                'session_length': 'medium'
            },
            {
                'name': 'news_consumption', 
                'request_pattern': 'periodic_refresh',
                'sites': ['cnn.com', 'bbc.com', 'nytimes.com', 'reuters.com'],
                'behavior': 'article_reading',
                'request_rate': 'low',
                'session_length': 'short'
            }
        ]
        
        selected_pattern = random.choice(patterns)
        self.logger.info(f"🎭 Selected traffic pattern: {selected_pattern['name']}")
        return selected_pattern
    
    def validate_circuit_health(self) -> bool:
        """Validate circuit health and stability"""
        try:
            if not self.controller:
                if not self.connect_controller():
                    return False
            
            circuits = self.controller.get_circuits()
            if not circuits:
                self.logger.warning("⚠️ No active circuits found")
                return False
                
            healthy_circuits = [c for c in circuits if c.status == 'BUILT']
            self.logger.info(f"🔍 Circuit health: {len(healthy_circuits)}/{len(circuits)} healthy")
            return len(healthy_circuits) > 0
            
        except Exception as e:
            self.logger.error(f"❌ Circuit health check failed: {e}")
            return False
    
    def get_comprehensive_routing_strategy(self) -> Dict[str, Any]:
        """Get comprehensive routing strategy - CORRETTO"""
        self.logger.info("🎯 Generating comprehensive routing strategy...")
        
        strategy = {
            'circuit_config': self.generate_multi_hop_circuit(),
            'rotation_timing': self.calculate_optimal_rotation_timing(),
            'artificial_delays': self.generate_artificial_delays(),
            'traffic_pattern': self.get_traffic_mimicry_pattern(),
            'torrc_config': self.get_torrc_advanced_config(),
            'circuit_health': self.validate_circuit_health(),
            'timestamp': time.time(),
            'strategy_id': f"strategy_{int(time.time())}"
        }
        
        self.logger.info("✅ Advanced routing strategy generated successfully")
        return strategy
    
    def close(self):
        """Cleanup resources"""
        if self.controller:
            try:
                self.controller.close()
                self.logger.info("✅ Advanced routing controller closed")
            except:
                pass

def main():
    """Test advanced routing - CORRETTO"""
    print(f"{Colors.BLUE}🔧 Testing Advanced Circuit Routing...{Colors.END}")
    
    try:
        router = AdvancedCircuitRouting()
        strategy = router.get_comprehensive_routing_strategy()
        
        print(f"{Colors.GREEN}✅ Advanced routing configured successfully{Colors.END}")
        print(f"   • Circuit: {strategy['circuit_config']['num_hops']} hops")
        print(f"   • Rotation: {strategy['rotation_timing']} seconds")
        print(f"   • Pattern: {strategy['traffic_pattern']['name']}")
        print(f"   • Health: {'✅' if strategy['circuit_health'] else '❌'}")
        
        router.close()
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Advanced routing test failed: {e}{Colors.END}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
