"""
DEBUG TEST: Reproduce http_client = None bug
This test simulates the exact UE5 client initialization flow to find why
assistant.http_client becomes None even after successful connection.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import threading
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock unreal module BEFORE any AIAssistant imports
sys.modules['unreal'] = Mock()
mock_unreal = sys.modules['unreal']
mock_unreal.Paths = Mock()
mock_unreal.Paths.project_dir = Mock(return_value="D:/UnrealProjects/TestProject")
mock_unreal.Paths.get_project_file_path = Mock(return_value="D:/UnrealProjects/TestProject/TestProject.uproject")
mock_unreal.log = Mock(side_effect=lambda msg: print(f"[MOCK LOG] {msg}"))
mock_unreal.log_warning = Mock(side_effect=lambda msg: print(f"[MOCK WARNING] {msg}"))
mock_unreal.log_error = Mock(side_effect=lambda msg: print(f"[MOCK ERROR] {msg}"))


def test_http_client_persistence():
    """
    Reproduce the bug: assistant.http_client becomes None after successful connection.
    """
    print("\n" + "="*80)
    print("🔍 DIAGNOSTIC TEST: HTTP Client Persistence Bug")
    print("="*80 + "\n")
    
    # Start test backend server in background
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    
    # Register project via HTTP to simulate backend
    project_id = "6e6498da3aead6dd4465aaf5df7d0127"
    register_resp = client.post("/api/ue5/register_http", json={
        "project_id": project_id,
        "project_name": "TestProject"
    })
    print(f"✅ Backend registered project: {register_resp.json()}")
    
    # Now simulate UE5 client initialization
    print("\n📋 Simulating UE5 Client Initialization...")
    print("-" * 80)
    
    # Import after mocking unreal
    from ue5_client.AIAssistant.main import AIAssistant
    from ue5_client.AIAssistant.http_polling_client import HTTPPollingClient
    
    # Create assistant instance (simulates __init__)
    print("\n1️⃣ Creating AIAssistant instance...")
    assistant = AIAssistant()
    
    print(f"   Initial http_client value: {assistant.http_client}")
    print(f"   Assistant object ID: {id(assistant)}")
    
    # Check if http_client was set during __init__
    print(f"\n2️⃣ Checking http_client after __init__...")
    print(f"   assistant.http_client: {assistant.http_client}")
    
    if assistant.http_client is not None:
        print(f"   ✅ HTTP client exists!")
        print(f"   Connected: {assistant.http_client.connected}")
        print(f"   Base URL: {assistant.http_client.base_url}")
        print(f"   Poll thread: {assistant.http_client.poll_thread}")
        
        # Check if polling thread is running
        if assistant.http_client.poll_thread:
            print(f"   Poll thread alive: {assistant.http_client.poll_thread.is_alive()}")
    else:
        print(f"   ❌ HTTP client is None!")
        
    # Check all running threads
    print(f"\n3️⃣ Checking active threads...")
    for thread in threading.enumerate():
        print(f"   Thread: {thread.name} (alive: {thread.is_alive()}, daemon: {thread.daemon})")
    
    # Check if singleton is working
    print(f"\n4️⃣ Checking singleton pattern...")
    from ue5_client.AIAssistant.main import _assistant, get_assistant
    print(f"   _assistant global: {_assistant}")
    print(f"   get_assistant() returns: {get_assistant()}")
    print(f"   Are they same object? {assistant is _assistant}")
    print(f"   Are they same as get_assistant()? {assistant is get_assistant()}")
    
    # Final check
    print(f"\n5️⃣ FINAL CHECK:")
    print(f"   assistant.http_client = {assistant.http_client}")
    print(f"   _assistant.http_client = {_assistant.http_client if _assistant else 'N/A'}")
    print(f"   get_assistant().http_client = {get_assistant().http_client}")
    
    print("\n" + "="*80)
    print("🎯 TEST COMPLETE")
    print("="*80 + "\n")
    
    # Assertions
    if assistant.http_client is None:
        print("❌ BUG REPRODUCED: http_client is None even after successful initialization!")
        print("\n🔍 Potential causes:")
        print("   1. Connection failed silently during _init_websocket()")
        print("   2. Exception caught and http_client never got set")
        print("   3. Multiple assistant instances created")
        print("   4. http_client reference cleared by something")
    else:
        print("✅ http_client persists correctly")
    
    # Give threads time to start
    time.sleep(0.5)
    
    return assistant


if __name__ == "__main__":
    assistant = test_http_client_persistence()
