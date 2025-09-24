"""
Standalone Etherscan API Service
This service provides Etherscan integration that can be deployed separately from the main application
"""

import json
import logging
import os
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
def setup_logging():
    """Setup logging with OS-appropriate log file path"""
    log_file_path = '/tmp/etherscan-api.log'
    # Use Windows temp directory if on Windows
    if os.name == 'nt':  # Windows
        temp_dir = os.environ.get('TEMP', 'C:\\temp')
        log_file_path = os.path.join(temp_dir, 'etherscan-api.log')
        # Ensure the directory exists
        os.makedirs(temp_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path)
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class EtherscanAPIService:
    """Standalone Etherscan API service"""
    
    def __init__(self):
        self.api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.base_url = "https://api.etherscan.io/api"
        self.call_count = 0
        self.last_reset = datetime.now()
        
        if not self.api_key:
            logger.warning("ETHERSCAN_API_KEY not set - Etherscan API calls will fail")
        else:
            logger.info("ETHERSCAN_API_KEY successfully loaded")
    
    def track_call(self):
        """Track API calls for rate limiting awareness"""
        self.call_count += 1
        logger.info(f"Etherscan API call #{self.call_count}")
    
    def get_account_balance(self, address: str) -> Dict[str, Any]:
        """Get account balance"""
        try:
            self.track_call()
            
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    balance_wei = int(data['result'])
                    balance_eth = balance_wei / 10**18
                    return {
                        'success': True,
                        'balance_wei': balance_wei,
                        'balance_eth': balance_eth,
                        'address': address
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_transaction_history(self, address: str, limit: int = 10) -> Dict[str, Any]:
        """Get transaction history"""
        try:
            self.track_call()
            
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': limit,
                'sort': 'desc',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    return {
                        'success': True,
                        'transactions': data['result'],
                        'count': len(data['result']),
                        'address': address
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_nonce(self, address: str) -> Dict[str, Any]:
        """Get current nonce via Etherscan"""
        try:
            self.track_call()
            
            params = {
                'module': 'proxy',
                'action': 'eth_getTransactionCount',
                'address': address,
                'tag': 'pending',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    nonce = int(data['result'], 16)  # Convert hex to int
                    return {
                        'success': True,
                        'nonce': nonce,
                        'address': address
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('error', {}).get('message', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting nonce: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_eth_price(self) -> Dict[str, Any]:
        """Get current ETH price"""
        try:
            self.track_call()
            
            params = {
                'module': 'stats',
                'action': 'ethprice',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    return {
                        'success': True,
                        'ethbtc': data['result']['ethbtc'],
                        'ethbtc_timestamp': data['result']['ethbtc_timestamp'],
                        'ethusd': data['result']['ethusd'],
                        'ethusd_timestamp': data['result']['ethusd_timestamp']
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting ETH price: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Initialize service
etherscan_service = EtherscanAPIService()

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'name': 'Etherscan API Service',
        'version': '1.0.0',
        'status': 'running',
        'api_key_configured': bool(etherscan_service.api_key),
        'endpoints': {
            'GET /': 'This documentation',
            'GET /health': 'Health check',
            'GET /balance/<address>': 'Get ETH balance',
            'GET /nonce/<address>': 'Get current nonce',
            'GET /transactions/<address>': 'Get transaction history',
            'GET /eth-price': 'Get ETH price'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if etherscan_service.api_key else 'unhealthy',
        'api_key_configured': bool(etherscan_service.api_key),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/balance/<address>')
def get_balance(address: str):
    """Get ETH balance for address"""
    result = etherscan_service.get_account_balance(address)
    return jsonify(result)

@app.route('/nonce/<address>')
def get_nonce(address: str):
    """Get current nonce for address"""
    result = etherscan_service.get_nonce(address)
    return jsonify(result)

@app.route('/transactions/<address>')
def get_transactions(address: str):
    """Get transaction history for address"""
    limit = request.args.get('limit', 10, type=int)
    result = etherscan_service.get_transaction_history(address, limit)
    return jsonify(result)

@app.route('/eth-price')
def get_eth_price():
    """Get current ETH price"""
    result = etherscan_service.get_eth_price()
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)