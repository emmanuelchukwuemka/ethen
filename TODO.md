# TODO - Etherscan API Service Improvements

1. Add endpoint and method to broadcast raw transactions:
   - Implement a new method in EtherscanAPIService to call `eth_sendRawTransaction` with the raw signed transaction hex.
   - Add a Flask route `/broadcast` to accept POST requests with raw transaction hex.
   - Include the API key in the request parameters.

2. Implement rate limiting:
   - Enforce a maximum of 10 API calls per second.
   - Use timestamps and counters to track calls and delay requests if needed.

3. Add error handling:
   - Detect and return clear errors for missing or invalid API key.
   - Handle other API errors gracefully.

4. Test the new broadcast endpoint locally:
   - Verify broadcasting works with a valid API key.
   - Verify rate limiting is enforced.

5. Deploy and test on Render:
   - Confirm the deployed service works as expected.
   - Verify API key is correctly set in environment variables on Render.

6. Optional:
   - Investigate upgrading to Etherscan V2 API for future-proofing.

# Notes
- The current service already supports balance, nonce, transactions, and ETH price.
- The main missing feature is broadcasting raw transactions.
- Rate limiting is currently not implemented and must be added to avoid API throttling.
