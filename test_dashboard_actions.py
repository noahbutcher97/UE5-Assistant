#!/usr/bin/env python3
"""Test script to verify dashboard actions are working correctly."""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_action(action_name, query):
    """Test a specific dashboard action."""
    print(f"\n🧪 Testing: {action_name}")
    print(f"   Query: {query}")
    
    # Step 1: Execute command
    try:
        response = requests.post(f"{BASE_URL}/execute_command", 
                                json={"user_input": query, "project_id": ""})
        data = response.json()
        
        if data.get("success"):
            result = data.get("response", data.get("result", ""))
            
            # Check if UE5 request is needed
            if "[UE_REQUEST]" in result or "[UE_CONTEXT_REQUEST]" in result:
                print(f"   ✅ AI returned UE_REQUEST token for {action_name}")
                
                # Extract action from token
                action = result.replace("[UE_REQUEST]", "").replace("[UE_CONTEXT_REQUEST]", "").strip().split("|")[0]
                print(f"   📡 Action to execute: {action}")
                
                # Step 2: Send to UE5
                ue5_response = requests.post(f"{BASE_URL}/send_command_to_ue5",
                    json={
                        "project_id": "189fb60ac15dee00c81189bbf2abcc6c",
                        "command": {
                            "type": "execute_action",
                            "action": action,
                            "params": {}
                        }
                    })
                
                ue5_data = ue5_response.json()
                
                if ue5_data.get("success"):
                    print(f"   ✅ UE5 command sent successfully")
                    if ue5_data.get("data"):
                        print(f"   📊 Data received: {str(ue5_data['data'])[:100]}...")
                else:
                    print(f"   ❌ UE5 command failed: {ue5_data.get('error')}")
            else:
                print(f"   ℹ️ Direct response: {result[:100]}...")
        else:
            print(f"   ❌ Command failed: {data.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")


def main():
    print("=" * 60)
    print("🚀 UE5 Dashboard Actions Test Suite")
    print("=" * 60)
    
    # Test each dashboard quick action
    actions_to_test = [
        ("describe_viewport", "describe viewport"),
        ("browse_files", "browse files"),
        ("list_blueprints", "list blueprints"),
        ("project_info", "project info"),
    ]
    
    for action_name, query in actions_to_test:
        test_action(action_name, query)
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    
    print("\n📝 Test Summary:")
    print("- All actions should return UE_REQUEST tokens")
    print("- Commands should be sent to UE5 successfully")
    print("- No threading errors should occur")
    print("- Real UE5 data should be returned")


if __name__ == "__main__":
    main()