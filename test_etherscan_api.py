"""
Test script for the standalone Etherscan API service
"""

import requests
import os
import json

def test_etherscan_service(base_url="http://localhost:8000"):
    """Test the Etherscan service endpoints"""
    print(f"🔍 Testing Etherscan Service at {base_url}")
    print("=" * 50)
    
    # Test 1: Home endpoint
    print("Test 1: Home endpoint")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Home endpoint accessible")
            print(f"  📦 Service: {data.get('name', 'Unknown')}")
            print(f"  🔢 Version: {data.get('version', 'Unknown')}")
        else:
            print(f"  ❌ Home endpoint returned HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error testing home endpoint: {e}")
    
    # Test 2: Health endpoint
    print("\nTest 2: Health endpoint")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            api_configured = data.get('api_key_configured', False)
            print(f"  Status: {status}")
            print(f"  API Key Configured: {'✅' if api_configured else '❌'}")
            
            if status == 'healthy' and api_configured:
                print("  ✅ Health check passed")
            else:
                print("  ⚠️  Health check indicates issues")
        else:
            print(f"  ❌ Health endpoint returned HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error testing health endpoint: {e}")
    
    # Test 3: Balance endpoint (using a known address)
    print("\nTest 3: Balance endpoint")
    test_address = "0xB5c1baF2E532Bb749a6b2034860178A3558b6e58"  # Your wallet address
    try:
        response = requests.get(f"{base_url}/balance/{test_address}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success:
                balance_eth = data.get('balance_eth', 0)
                print(f"  ✅ Balance check successful")
                print(f"  💰 Balance: {balance_eth} ETH")
            else:
                error = data.get('error', 'Unknown error')
                print(f"  ⚠️  Balance check failed: {error}")
        else:
            print(f"  ❌ Balance endpoint returned HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error testing balance endpoint: {e}")
    
    # Test 4: Nonce endpoint
    print("\nTest 4: Nonce endpoint")
    try:
        response = requests.get(f"{base_url}/nonce/{test_address}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            if success:
                nonce = data.get('nonce', 0)
                print(f"  ✅ Nonce check successful")
                print(f"  🔢 Current nonce: {nonce}")
            else:
                error = data.get('error', 'Unknown error')
                print(f"  ⚠️  Nonce check failed: {error}")
        else:
            print(f"  ❌ Nonce endpoint returned HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error testing nonce endpoint: {e}")

def main():
    """Main test function"""
    print("🚀 Etherscan Service Test")
    print("=" * 50)
    
    # You can change this to your deployed service URL
    service_url = input("Enter Etherscan service URL (or press Enter for localhost:8000): ").strip()
    if not service_url:
        service_url = "http://localhost:8000"
    
    test_etherscan_service(service_url)
    
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    print("To run the Etherscan service locally:")
    print("1. Set your ETHERSCAN_API_KEY environment variable")
    print("2. Run: python etherscan_app.py")
    print("3. The service will start on http://localhost:8000")
    print()
    print("To deploy to Render:")
    print("1. Move the etherscan_app.py, etherscan_requirements.txt,")
    print("   and etherscan_render.yaml files to a new repository")
    print("2. Update the ETHERSCAN_API_KEY in etherscan_render.yaml")
    print("3. Deploy to Render using the render.yaml configuration")

if __name__ == "__main__":
    main()