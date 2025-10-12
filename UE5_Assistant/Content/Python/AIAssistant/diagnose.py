"""
Diagnostic script to test AIAssistant import issues
Run in UE5 Python Console: import AIAssistant.diagnose
"""

def test_imports():
    """Test each import step by step."""
    import unreal
    
    unreal.log("=" * 60)
    unreal.log("🔍 AIAssistant Diagnostic Test")
    unreal.log("=" * 60)
    
    # Test 1: Basic imports
    try:
        from typing import Optional
        unreal.log("✅ typing.Optional import OK")
    except Exception as e:
        unreal.log_error(f"❌ typing import failed: {e}")
    
    # Test 2: Config
    try:
        from .config import get_config
        unreal.log("✅ config import OK")
    except Exception as e:
        unreal.log_error(f"❌ config import failed: {e}")
    
    # Test 3: API Client
    try:
        from .api_client import get_client
        unreal.log("✅ api_client import OK")
    except Exception as e:
        unreal.log_error(f"❌ api_client import failed: {e}")
    
    # Test 4: Action Executor
    try:
        from .action_executor import get_executor
        unreal.log("✅ action_executor import OK")
    except Exception as e:
        unreal.log_error(f"❌ action_executor import failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: WebSocket Client
    try:
        from .websocket_client import WebSocketClient
        unreal.log("✅ websocket_client import OK")
    except Exception as e:
        unreal.log_error(f"❌ websocket_client import failed: {e}")
    
    # Test 6: Try importing main
    try:
        from . import main
        unreal.log("✅ main module import OK")
    except Exception as e:
        unreal.log_error(f"❌ main module import failed: {e}")
        import traceback
        traceback.print_exc()
    
    unreal.log("=" * 60)
    unreal.log("✅ Diagnostic complete - check above for errors")
    unreal.log("=" * 60)

# Run automatically
test_imports()
