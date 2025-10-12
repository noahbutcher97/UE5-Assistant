"""
HTTP Polling client for UE5 - Fallback when WebSocket doesn't work.
Provides same interface as WebSocketClient for seamless fallback.
"""
import json
import threading
import time
from typing import Any, Callable, Dict, Optional
import requests


class HTTPPollingClient:
    """
    HTTP Polling client for UE5 to connect to the backend.
    Fallback for when WebSocket connections are blocked.
    """
    
    def __init__(self, base_url: str, project_id: str, project_name: str = "Unknown"):
        """
        Initialize HTTP Polling client.
        
        Args:
            base_url: Backend base URL (e.g., "https://ue5-assistant-noahbutcher97.replit.app")
            project_id: Unique project identifier
            project_name: Human-readable project name
        """
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.project_name = project_name
        
        self.connected = False
        self.running = False
        self.poll_thread = None
        self.action_handler: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None
        
        # Polling settings
        self.poll_interval = 2.0  # seconds
        self.heartbeat_interval = 10.0  # seconds
        self.last_heartbeat = 0
        
        # Auto-reconnect settings
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.reconnect_delay = 5.0  # seconds
        
    def set_action_handler(self, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
        """
        Set the handler for incoming action commands.
        
        Args:
            handler: Function that takes (action, params) and returns response dict
        """
        self.action_handler = handler
    
    def connect(self) -> bool:
        """
        Connect to the backend via HTTP polling.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            print(f"🔌 Attempting HTTP polling connection to: {self.base_url}")
            
            # Register with backend
            response = requests.post(
                f"{self.base_url}/api/ue5/register_http",
                json={
                    "project_id": self.project_id,
                    "project_name": self.project_name
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.connected = True
                    
                    # Start polling thread
                    self.running = True
                    self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
                    self.poll_thread.start()
                    
                    print(f"✅ HTTP polling connected: {self.project_id}")
                    return True
            
            print(f"❌ HTTP polling registration failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ HTTP polling connection failed: {e}")
            return False
    
    def _poll_loop(self):
        """Main polling loop - runs in background thread."""
        while self.running:
            try:
                # Send heartbeat periodically
                current_time = time.time()
                if current_time - self.last_heartbeat > self.heartbeat_interval:
                    self._send_heartbeat()
                    self.last_heartbeat = current_time
                
                # Poll for commands
                response = requests.post(
                    f"{self.base_url}/api/ue5/poll",
                    json={"project_id": self.project_id},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get("commands", [])
                    
                    # Check if we're still registered
                    if not data.get("registered", True):
                        print("⚠️ Server doesn't recognize us - re-registering...")
                        self._attempt_reconnect()
                        continue
                    
                    # Process each command
                    for cmd in commands:
                        self._handle_command(cmd)
                    
                    # Reset failure counter on success
                    self.consecutive_failures = 0
                    self.connected = True
                
                else:
                    # Non-200 status code
                    self.consecutive_failures += 1
                    print(f"⚠️ Poll failed with status {response.status_code} (attempt {self.consecutive_failures}/{self.max_consecutive_failures})")
                    
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        self._attempt_reconnect()
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.consecutive_failures += 1
                print(f"⚠️ Polling error: {e} (attempt {self.consecutive_failures}/{self.max_consecutive_failures})")
                
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self._attempt_reconnect()
                else:
                    time.sleep(self.poll_interval * 2)  # Wait longer on error
    
    def _send_heartbeat(self):
        """Send heartbeat to keep connection alive."""
        try:
            requests.post(
                f"{self.base_url}/api/ue5/heartbeat",
                json={"project_id": self.project_id},
                timeout=5
            )
        except Exception as e:
            print(f"⚠️ Heartbeat failed: {e}")
    
    def _attempt_reconnect(self):
        """Attempt to reconnect after multiple failures."""
        self.connected = False
        print(f"🔄 Backend connection lost. Attempting to re-register in {self.reconnect_delay}s...")
        time.sleep(self.reconnect_delay)
        
        try:
            # Re-register with backend
            response = requests.post(
                f"{self.base_url}/api/ue5/register_http",
                json={
                    "project_id": self.project_id,
                    "project_name": self.project_name
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.connected = True
                    self.consecutive_failures = 0
                    print(f"✅ Successfully re-registered: {self.project_id}")
                    return True
            
            print(f"❌ Re-registration failed: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Re-registration error: {e}")
        
        # Reset counter to try again after more failures
        self.consecutive_failures = 0
        return False
    
    def _handle_command(self, cmd: dict):
        """Handle incoming command from backend."""
        try:
            message_type = cmd.get("type")
            
            if message_type == "execute_action":
                # Execute action requested by dashboard
                action = cmd.get("action")
                params = cmd.get("params", {})
                request_id = cmd.get("request_id")
                
                if self.action_handler:
                    # Execute action
                    result = self.action_handler(action, params)
                    
                    # Send response back via HTTP
                    response = {
                        "request_id": request_id,
                        "action": action,
                        "success": result.get("success", True),
                        "data": result.get("data"),
                        "error": result.get("error")
                    }
                    
                    self.send_message(response)
                    print(f"✅ Executed action: {action} (result: {result.get('success')})")
                else:
                    # No handler - send error response
                    self.send_message({
                        "request_id": request_id,
                        "success": False,
                        "error": "No action handler configured"
                    })
            
            elif message_type == "auto_update":
                # Backend triggered auto-update
                print("📢 Backend update detected! Running auto-update...")
                self._handle_auto_update()
                    
        except Exception as e:
            print(f"❌ Error handling command: {e}")
    
    def _handle_auto_update(self):
        """Handle auto-update triggered by backend."""
        try:
            # Import here to avoid circular dependency
            import importlib
            import sys
            
            # Check if we're in UE5 environment
            try:
                import unreal
            except ImportError:
                print("⚠️ Auto-update skipped (not in UE5 environment)")
                return
            
            # Run auto-update to download files
            if 'AIAssistant.auto_update' in sys.modules:
                # Reload the module
                importlib.reload(sys.modules['AIAssistant.auto_update'])
            
            from AIAssistant import auto_update
            result = auto_update.check_and_update()
            
            # check_and_update returns bool
            if result:
                print("✅ Auto-update completed successfully")
                print("🔄 Force reloading ALL AIAssistant modules...")
                
                # Force clear ALL AIAssistant modules from cache
                modules_to_remove = [key for key in sys.modules.keys() if 'AIAssistant' in key]
                for module in modules_to_remove:
                    del sys.modules[module]
                print(f"🗑️ Cleared {len(modules_to_remove)} cached modules")
                
                # Don't re-import from background thread - let UE5 reload naturally
                print("✅ Modules cleared. Fresh code will load on next request.")
            else:
                print("ℹ️ Auto-update failed or no updates available")
                
        except Exception as e:
            print(f"❌ Auto-update failed: {e}")
    
    def send_message(self, data: dict):
        """
        Send message to backend via HTTP POST with retry logic.
        
        Args:
            data: Message data to send
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/ue5/response",
                    json={
                        "project_id": self.project_id,
                        "response": data
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    return  # Success
                else:
                    print(f"⚠️ Response send failed ({response.status_code}), attempt {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                print(f"⚠️ Failed to send message (attempt {attempt + 1}/{max_retries}): {e}")
            
            # Retry with delay (except on last attempt)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        # All retries failed
        print(f"❌ Failed to send message after {max_retries} attempts")
    
    def disconnect(self):
        """Disconnect from backend."""
        self.running = False
        self.connected = False
        print("🔌 HTTP polling disconnected")
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected
