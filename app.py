from flask import Flask, request, jsonify
import time
import threading
import requests
from etherscan_nonce_tracker import EtherscanNonceTracker
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global API call counter
api_call_counter = 0
counter_lock = threading.Lock()
last_reset = datetime.now()

class RateLimiter:
    def __init__(self, max_calls_per_sec):
        self.max_calls = max_calls_per_sec
        self.lock = threading.Lock()
        self.calls = []
    
    def acquire(self):
        with self.lock:
            current = time.time()
            # Remove calls older than 1 second
            self.calls = [call for call in self.calls if current - call < 1]
            if len(self.calls) >= self.max_calls:
                # Need to wait
                wait_time = 1 - (current - self.calls[0])
                if wait_time > 0:
                    time.sleep(wait_time)
            self.calls.append(time.time())

def increment_api_counter():
    """Thread-safe increment of API call counter"""
    global api_call_counter, counter_lock, last_reset
    
    with counter_lock:
        # Reset counter every hour to prevent overflow
        current_time = datetime.now()
        if (current_time - last_reset).seconds > 3600:
            api_call_counter = 0
            last_reset = current_time
        
        api_call_counter += 1
        return api_call_counter

class EtherscanAPIService(EtherscanNonceTracker):
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(20)  # Increased to 20 calls per second
    
    def call_etherscan_api(self, params):
        self.rate_limiter.acquire()
        increment_api_counter()  # Count this API call
        params['apikey'] = self.etherscan_api_key
        try:
            response = requests.get(self.etherscan_base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '0':
                    # Etherscan error
                    error_message = data.get('message', 'Unknown error')
                    logger.error(f"Etherscan API error: {error_message}")
                    return None, error_message
                return data, None
            else:
                logger.error(f"Etherscan API HTTP error: {response.status_code}")
                return None, f"HTTP error {response.status_code}"
        except Exception as e:
            logger.error(f"Etherscan API request exception: {e}")
            return None, str(e)
    
    def broadcast_raw_transaction(self, raw_tx_hex):
        self.rate_limiter.acquire()
        increment_api_counter()  # Count this API call
        params = {
            'module': 'proxy',
            'action': 'eth_sendRawTransaction',
            'hex': raw_tx_hex
        }
        params['apikey'] = self.etherscan_api_key
        try:
            response = requests.get(self.etherscan_base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    error_message = data['error'].get('message', 'Unknown error')
                    logger.error(f"Broadcast error: {error_message}")
                    return None, error_message
                if 'result' in data:
                    return data['result'], None
                else:
                    error_message = data.get('message', 'Unknown error')
                    logger.error(f"Broadcast failed: {error_message}")
                    return None, error_message
            else:
                logger.error(f"Broadcast HTTP error: {response.status_code}")
                return None, f"HTTP error {response.status_code}"
        except Exception as e:
            logger.error(f"Broadcast request exception: {e}")
            return None, str(e)
    
    def get_eth_price(self):
        """Get current ETH price using Etherscan API"""
        increment_api_counter()  # Count this API call
        params = {
            'module': 'stats',
            'action': 'ethprice',
            'apikey': self.etherscan_api_key
        }
        
        try:
            response = requests.get(self.etherscan_base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    return data.get('result', {})
                else:
                    logger.error(f"ETH price API error: {data.get('message', 'Unknown error')}")
                    return {}
            else:
                logger.error(f"ETH price API HTTP error: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"ETH price API request exception: {e}")
            return {}

service = EtherscanAPIService()

@app.route('/')
def home():
    return jsonify({
        'name': 'Etherscan API Service',
        'version': '2.0.0',
        'api_key_configured': bool(service.etherscan_api_key),
        'endpoints': {
            'GET /': 'This documentation',
            'GET /balance/<address>': 'Get ETH balance',
            'GET /eth-price': 'Get ETH price',
            'GET /health': 'Health check',
            'GET /nonce/<address>': 'Get current nonce',
            'GET /transactions/<address>': 'Get transaction history',
            'POST /broadcast': 'Broadcast raw transaction'
        },
        'status': 'running'
    })

@app.route('/health')
def health():
    global api_call_counter, counter_lock
    with counter_lock:
        current_count = api_call_counter
    
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(service.etherscan_api_key),
        'api_calls': current_count,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    try:
        increment_api_counter()  # Count this API call
        balance = service.get_balance(address)
        return jsonify({
            'status': 'success',
            'address': address,
            'balance_eth': balance,
            'balance_wei': int(balance * 10**18)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/nonce/<address>', methods=['GET'])
def get_nonce(address):
    try:
        increment_api_counter()  # Count this API call
        nonce = service.get_nonce_via_etherscan(address)
        return jsonify({
            'status': 'success',
            'address': address,
            'nonce': nonce,
            'nonce_hex': hex(nonce)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/transactions/<address>', methods=['GET'])
def get_transactions(address):
    try:
        increment_api_counter()  # Count this API call
        limit = int(request.args.get('limit', 10))
        txs = service.get_transaction_history_via_etherscan(address, limit)
        return jsonify({
            'status': 'success',
            'address': address,
            'count': len(txs),
            'transactions': txs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/eth-price', methods=['GET'])
def eth_price():
    try:
        price_data = service.get_eth_price()
        return jsonify({
            'status': 'success',
            'eth_usd': price_data.get('ethusd', '0'),
            'eth_btc': price_data.get('ethbtc', '0'),
            'timestamp': datetime.now().timestamp()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/broadcast', methods=['POST'])
def broadcast():
    api_key = request.args.get('apikey') or request.headers.get('X-API-KEY')
    if not api_key or api_key != service.etherscan_api_key:
        return jsonify({'success': False, 'error': 'Missing or invalid API key'}), 401
    
    data = request.get_json()
    if not data or 'raw_tx_hex' not in data:
        return jsonify({'success': False, 'error': 'Missing raw_tx_hex in request body'}), 400
    
    increment_api_counter()  # Count this API call
    raw_tx_hex = data['raw_tx_hex']
    tx_hash, error = service.broadcast_raw_transaction(raw_tx_hex)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    return jsonify({'success': True, 'tx_hash': tx_hash})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)