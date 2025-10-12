#!/usr/bin/env python3
"""Test script to verify HTTP registration endpoint works correctly."""
import requests
import json
import time

# Test server URL
BASE_URL = "https://ue5-assistant-noahbutcher97.replit.app"

# Test project details
PROJECT_ID = "test_project_123"
PROJECT_NAME = "Test HTTP Client"

def test_registration():
    """Test HTTP registration endpoint."""
    print("=" * 60)
    print("Testing HTTP Registration Endpoint")
    print("=" * 60)
    
    # Register via HTTP
    register_url = f"{BASE_URL}/api/ue5/register_http"
    payload = {
        "project_id": PROJECT_ID,
        "project_name": PROJECT_NAME
    }
    
    print(f"URL: {register_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending registration request...")
    
    try:
        response = requests.post(register_url, json=payload, timeout=10)
        print(f"✅ Response received!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n✅ Registration successful!")
                return True
            else:
                print(f"\n❌ Registration failed: {data.get('error')}")
                return False
        else:
            print(f"\n❌ HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_polling():
    """Test polling for commands."""
    print("\n" + "=" * 60)
    print("Testing Polling Endpoint")
    print("=" * 60)
    
    poll_url = f"{BASE_URL}/api/ue5/poll"
    payload = {
        "project_id": PROJECT_ID,
        "project_name": PROJECT_NAME
    }
    
    print(f"URL: {poll_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nPolling for commands...")
    
    try:
        response = requests.post(poll_url, json=payload, timeout=10)
        print(f"✅ Response received!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Commands: {data.get('commands', [])}")
            print(f"Registered: {data.get('registered', False)}")
            return True
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("Testing HTTP Polling System")
    print("Server:", BASE_URL)
    print("")
    
    # Test registration
    if test_registration():
        # Wait a bit
        time.sleep(1)
        
        # Test polling
        test_polling()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()