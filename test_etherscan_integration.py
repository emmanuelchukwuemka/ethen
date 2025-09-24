"""
Test script to verify Etherscan integration is working properly
"""

import requests
import json
import os

def test_etherscan_integration(base_url="http://localhost:5000"):
    """Test Etherscan integration by checking the status endpoint"""
    print(f"🔍 Testing Etherscan integration on {base_url}")
    print("=" * 50)
    
    try:
        # Test the status endpoint
        response = requests.get(f"{base_url}/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint is accessible")
            
            # Check if Etherscan integration is detected
            blockchain_data = data.get('data', {}).get('blockchain', {})
            etherscan_data = blockchain_data.get('etherscan_integration', {})
            
            if etherscan_data:
                api_configured = etherscan_data.get('api_key_configured', False)
                tracking_active = etherscan_data.get('tracking_active', False)
                
                print(f"🔍 Etherscan Integration Status:")
                print(f"   API Key Configured: {'✅' if api_configured else '❌'}")
                print(f"   Tracking Active: {'✅' if tracking_active else '❌'}")
                
                if api_configured and tracking_active:
                    print("🎉 Etherscan integration is working properly!")
                    return True
                elif api_configured:
                    print("⚠️  Etherscan API key is configured but tracking is not active")
                    print("   This may be due to Ethereum connection issues")
                else:
                    print("❌ Etherscan API key is not configured")
                    print("   Please set the ETHERSCAN_API_KEY environment variable")
            else:
                print("❌ Etherscan integration data not found in status response")
        else:
            print(f"❌ Status endpoint returned error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the server is running")
    except Exception as e:
        print(f"❌ Error testing Etherscan integration: {e}")
    
    return False

def test_etherscan_api_directly():
    """Test Etherscan API directly using the configured API key"""
    print("\n🔍 Testing Etherscan API directly...")
    print("=" * 50)
    
    # Try to get API key from environment or config
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
    
    if not etherscan_api_key:
        # Try to load from config file
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                etherscan_api_key = config.get("etherscan_api_key")
        except:
            pass
    
    if not etherscan_api_key:
        print("❌ Etherscan API key not found")
        print("   Please set ETHERSCAN_API_KEY environment variable")
        return False
    
    try:
        # Test basic Etherscan API functionality
        url = "https://api.etherscan.io/api"
        params = {
            'module': 'stats',
            'action': 'ethprice',
            'apikey': etherscan_api_key
        }
        
        print(f"Testing Etherscan API with key: {etherscan_api_key[:8]}...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1':
                print("✅ Etherscan API is working correctly")
                print(f"   ETH Price: ${data.get('result', {}).get('ethusd', 'Unknown')}")
                return True
            else:
                print(f"❌ Etherscan API error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Etherscan API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Etherscan API: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Etherscan Integration Test")
    print("=" * 50)
    
    # Test through the application
    app_working = test_etherscan_integration("https://crypto-ob3q.onrender.com")
    
    # Test Etherscan API directly
    api_working = test_etherscan_api_directly()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if app_working and api_working:
        print("🎉 All tests passed! Etherscan integration is working properly.")
    elif api_working:
        print("⚠️  Etherscan API is working but integration with the app is not.")
        print("   This may be due to Ethereum connection issues in the application.")
    elif app_working:
        print("⚠️  Application shows Etherscan integration but direct API test failed.")
        print("   There may be an issue with the API key or network connectivity.")
    else:
        print("❌ Etherscan integration is not working.")
        print("   Please check the troubleshooting section in README.md")
    
    return app_working and api_working

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)