# 🚀 Etherscan API Service

**Standalone Etherscan API service that can be deployed separately from the main Ethereum Withdrawal API**

## ✨ Features

- ✅ **Etherscan API Integration** - Direct access to Etherscan's powerful blockchain data
- ✅ **Account Balance Queries** - Get ETH and token balances for any address
- ✅ **Transaction History** - Retrieve transaction history for any address
- ✅ **Nonce Tracking** - Get current nonce for address to prevent transaction conflicts
- ✅ **ETH Price Data** - Get current ETH price in USD and BTC
- ✅ **Rate Limiting Awareness** - Track API calls to avoid exceeding limits
- ✅ **Production Ready** - Flask + Gunicorn with CORS support

## 🔧 API Endpoints

- `GET /` - API documentation
- `GET /health` - Health check
- `GET /balance/<address>` - Get ETH balance for address
- `GET /nonce/<address>` - Get current nonce for address
- `GET /transactions/<address>` - Get transaction history for address
- `GET /eth-price` - Get current ETH price

## 🚀 Deploy to Render

### One-Click Deploy
1. Create a new repository with these files
2. Connect to Render.com
3. Select "Web Service"
4. Update the `ETHERSCAN_API_KEY` in `etherscan_render.yaml`
5. Your API will be deployed automatically

### Manual Deploy
1. Clone this repository
2. Connect to Render.com
3. Select "Web Service"
4. Update the `ETHERSCAN_API_KEY` in `etherscan_render.yaml`
5. Your API will be deployed automatically

## 🔐 Environment Variables

All sensitive data is configured via environment variables:

```bash
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r etherscan_requirements.txt

# Set your Etherscan API key
export ETHERSCAN_API_KEY=your_actual_api_key_here

# Run locally
python etherscan_app.py

# Server will start on http://localhost:8000
```

## 💡 Usage Examples

### Check Balance
```bash
curl http://localhost:8000/balance/0xB5c1baF2E532Bb749a6b2034860178A3558b6e58
```

### Get Current Nonce
```bash
curl http://localhost:8000/nonce/0xB5c1baF2E532Bb749a6b2034860178A3558b6e58
```

### Get Transaction History
```bash
curl http://localhost:8000/transactions/0xB5c1baF2E532Bb749a6b2034860178A3558b6e58?limit=5
```

### Get ETH Price
```bash
curl http://localhost:8000/eth-price
```

## 📈 Performance

- **Response Time**: <500ms for most API calls
- **Rate Limiting**: Tracks calls to prevent exceeding Etherscan limits
- **Concurrent Requests**: Supports multiple simultaneous operations

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/`
2. Monitor health endpoint at `/health`
3. Review logs for error details

---

**Built with ❤️ for the Ethereum ecosystem**