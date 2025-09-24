"""
Script to fix Etherscan integration issues by improving Ethereum RPC connectivity
"""

import json
import logging
import os
from web3 import Web3
import requests
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EthereumConnectionFixer:
    """Class to fix Ethereum connection issues and improve Etherscan integration"""
    
    def __init__(self):
        self.config = self.load_config()
        self.w3: Optional[Web3] = None
        self.connected_endpoint: Optional[str] = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        config_file = "config.json"
        
        # Try to load from file first
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded from file")
            return config
        else:
            # Fallback to environment variables for production
            logger.info("Config file not found, using environment variables")
            config = {
                "chain_id": int(os.getenv("CHAIN_ID", "1")),
                "public_client_rpc": os.getenv("RPC_ENDPOINT", "https://ethereum-rpc.publicnode.com"),
                "wallet_address": os.getenv("WALLET_ADDRESS", ""),
                "api_key": os.getenv("ETHEREUM_API_KEY", ""),
                "etherscan_api_key": os.getenv("ETHERSCAN_API_KEY", ""),
                "network_settings": {
                    "timeout": 15,
                    "retry_attempts": 3
                }
            }
            return config
    
    def initialize_web3_with_fallback(self) -> bool:
        """Initialize Web3 with multiple fallback endpoints"""
        print("🔄 Initializing Web3 with fallback endpoints...")
        
        # List of RPC endpoints to try
        rpc_endpoints = [
            {"name": "PublicNode", "url": "https://ethereum-rpc.publicnode.com", "timeout": 15},
            {"name": "Ankr", "url": "https://rpc.ankr.com/eth", "timeout": 15},
            {"name": "drpc", "url": "https://eth.drpc.org", "timeout": 15},
            {"name": "BlockPI", "url": "https://ethereum.blockpi.network/v1/rpc/public", "timeout": 15},
            {"name": "Cloudflare", "url": "https://cloudflare-eth.com", "timeout": 20},
            {"name": "Infura", "url": f"https://mainnet.infura.io/v3/{self.config.get('api_key', '')}", "timeout": 15}
        ]
        
        # Try each endpoint
        for endpoint in rpc_endpoints:
            try:
                print(f"  Trying {endpoint['name']}: {endpoint['url']}")
                
                # Create Web3 instance with specific timeout
                w3 = Web3(Web3.HTTPProvider(
                    endpoint['url'], 
                    request_kwargs={'timeout': endpoint['timeout']}
                ))
                
                # Test connection
                if w3.is_connected():
                    print(f"  ✅ Connected successfully to {endpoint['name']}")
                    
                    # Verify basic functionality
                    chain_id = w3.eth.chain_id
                    block_number = w3.eth.block_number
                    print(f"    Chain ID: {chain_id}")
                    print(f"    Current Block: {block_number}")
                    
                    # Set as working instance
                    self.w3 = w3
                    self.connected_endpoint = endpoint['name']
                    return True
                else:
                    print(f"  ❌ Failed to connect to {endpoint['name']}")
                    
            except Exception as e:
                print(f"  ❌ Error connecting to {endpoint['name']}: {e}")
                continue
        
        print("❌ Failed to connect to any Ethereum RPC endpoint")
        return False
    
    def test_etherscan_integration(self) -> bool:
        """Test Etherscan API integration"""
        print("\n🔍 Testing Etherscan API integration...")
        
        etherscan_api_key = self.config.get("etherscan_api_key")
        if not etherscan_api_key:
            print("❌ Etherscan API key not found in configuration")
            return False
        
        try:
            # Test basic account balance API
            url = "https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': self.config.get("wallet_address", "0xB5c1baF2E532Bb749a6b2034860178A3558b6e58"),
                'tag': 'latest',
                'apikey': etherscan_api_key
            }
            
            print(f"  Testing Etherscan API with key: {etherscan_api_key[:8]}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    balance = int(data.get('result', 0))
                    balance_eth = balance / 10**18
                    print(f"  ✅ Etherscan API working correctly")
                    print(f"    Wallet Balance: {balance_eth} ETH")
                    return True
                else:
                    print(f"  ❌ Etherscan API error: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"  ❌ Etherscan API request failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Etherscan API test failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "etherscan_api_key_configured": bool(self.config.get("etherscan_api_key")),
            "ethereum_connected": self.w3 is not None,
            "connected_endpoint": self.connected_endpoint,
            "wallet_address": self.config.get("wallet_address", "")
        }
        
        if self.w3:
            try:
                status.update({
                    "chain_id": self.w3.eth.chain_id,
                    "current_block": self.w3.eth.block_number,
                    "gas_price_gwei": float(self.w3.from_wei(self.w3.eth.gas_price, 'gwei'))
                })
            except Exception as e:
                print(f"Warning: Could not get blockchain details: {e}")
        
        return status
    
    def fix_render_deployment(self):
        """Fix common Render deployment issues"""
        print("\n🔧 Fixing Render deployment issues...")
        
        # Check if we're running on Render
        if os.getenv('RENDER'):
            print("  Detected Render deployment environment")
            
            # Suggest environment variable fixes
            print("  Recommended environment variables:")
            print("    ETHEREUM_API_KEY=your_infura_or_alchemy_api_key")
            print("    ETHERSCAN_API_KEY=your_etherscan_api_key")
            print("    RPC_ENDPOINT=https://ethereum-rpc.publicnode.com")
            print("    WALLET_ADDRESS=your_wallet_address")
            
            # Check for common issues
            if not self.config.get("api_key"):
                print("  ⚠️  Warning: ETHEREUM_API_KEY not set - consider using Infura/Alchemy")
            
            if not self.config.get("etherscan_api_key"):
                print("  ⚠️  Warning: ETHERSCAN_API_KEY not set - Etherscan integration will not work")
        else:
            print("  Not running on Render - skipping Render-specific fixes")
    
    def generate_fix_report(self) -> str:
        """Generate a report of the fixes applied"""
        status = self.get_system_status()
        
        report = []
        report.append("🔧 ETHERSCAN INTEGRATION FIX REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Etherscan API key status
        if status["etherscan_api_key_configured"]:
            report.append("✅ Etherscan API Key: Configured")
        else:
            report.append("❌ Etherscan API Key: Missing")
            report.append("   Solution: Add ETHERSCAN_API_KEY environment variable")
        
        # Ethereum connection status
        if status["ethereum_connected"]:
            report.append(f"✅ Ethereum Connection: Connected via {status['connected_endpoint']}")
            report.append(f"   Chain ID: {status['chain_id']}")
            report.append(f"   Current Block: {status['current_block']}")
        else:
            report.append("❌ Ethereum Connection: Failed")
            report.append("   Solutions:")
            report.append("   1. Check network connectivity")
            report.append("   2. Verify firewall settings")
            report.append("   3. Use a dedicated node service (Infura/Alchemy)")
            report.append("   4. Try different RPC endpoints")
        
        # Wallet address
        if status["wallet_address"]:
            report.append(f"✅ Wallet Address: {status['wallet_address']}")
        else:
            report.append("⚠️  Wallet Address: Not configured")
        
        # Additional recommendations
        report.append("")
        report.append("💡 RECOMMENDATIONS:")
        report.append("1. For production deployments, use dedicated node services like Infura or Alchemy")
        report.append("2. Monitor your Etherscan API usage to avoid rate limits")
        report.append("3. Implement proper error handling for network failures")
        report.append("4. Consider using multiple fallback RPC endpoints")
        
        return "\n".join(report)

def main():
    """Main function to fix Etherscan integration issues"""
    print("🚀 Etherscan Integration Fix Tool")
    print("=" * 50)
    
    # Create fixer instance
    fixer = EthereumConnectionFixer()
    
    # Initialize Web3 connection
    ethereum_connected = fixer.initialize_web3_with_fallback()
    
    # Test Etherscan integration
    etherscan_working = fixer.test_etherscan_integration()
    
    # Fix Render deployment issues
    fixer.fix_render_deployment()
    
    # Generate and display fix report
    print("\n" + fixer.generate_fix_report())
    
    # Final status
    print("\n" + "=" * 50)
    if ethereum_connected and etherscan_working:
        print("🎉 SUCCESS: Etherscan integration is now working!")
        print("   Both Ethereum connection and Etherscan API are functional")
    elif etherscan_working:
        print("⚠️  PARTIAL SUCCESS: Etherscan API is working")
        print("   But Ethereum connection is still failing")
        print("   Etherscan integration will work but with limited functionality")
    else:
        print("❌ FAILURE: Etherscan integration is still not working")
        print("   Please check the recommendations above")
    
    return ethereum_connected and etherscan_working

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)