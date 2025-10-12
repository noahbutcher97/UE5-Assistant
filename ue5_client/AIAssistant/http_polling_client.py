"""
HTTP Polling client for UE5 - Fallback when WebSocket doesn't work.
Provides same interface as WebSocketClient for seamless fallback.
Now with thread-safe action execution via queue system.
"""
import json
import sys
import importlib
import threading
import time
from typing import Any, Callable, Dict, Optional
import requests

# Import action queue for thread-safe execution
try:
    from .action_queue import get_action_queue
    HAS_ACTION_QUEUE = True
except ImportError:
    HAS_ACTION_QUEUE = False
    print("⚠️ Action queue not available - using direct execution")


class HTTPPollingClient:
    """
    HTTP Polling client for UE5 to connect to the backend.
    Fallback for when WebSocket connections are blocked.
    Now with thread-safe action execution via queue system.
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
        
        # Version tracking for module reload
        self.last_module_version = None
        self.last_version_check = 0
        self.version_check_interval = 10  # Check every 10 seconds
        
        # Initialize action queue if available
        if HAS_ACTION_QUEUE:
            self.action_queue = get_action_queue()
            print("✅ Using thread-safe action queue for execution")
        else:
            self.action_queue = None
            print("⚠️ Action queue not available - direct execution (may cause threading issues)")
        
    def set_action_handler(self, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
        """
        Set the handler for incoming action commands.
        
        Args:
            handler: Function that takes (action, params) and returns response dict
        """
        self.action_handler = handler
        
        # Also register with action queue if available
        if self.action_queue:
            self.action_queue.set_action_handler(handler)
            print("✅ Action handler registered with thread-safe queue")
    
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
                    
                    # Start action queue ticker if available
                    if self.action_queue:
                        self.action_queue.start_ticker()
                    
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
        print("[HTTPPolling] Background polling thread started")
        
        while self.running:
            try:
                # Check for module updates periodically
                current_time = time.time()
                if current_time - self.last_version_check > self.version_check_interval:
                    self._check_module_version()
                    self.last_version_check = current_time
                
                # Send heartbeat periodically
                if current_time - self.last_heartbeat > self.heartbeat_interval:
                    self._send_heartbeat()
                    self.last_heartbeat = current_time
                
                # Poll for commands (include project_name for auto-registration)
                response = requests.post(
                    f"{self.base_url}/api/ue5/poll",
                    json={
                        "project_id": self.project_id,
                        "project_name": self.project_name
                    },
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
        
        print("[HTTPPolling] Background polling thread stopped")
    
    def _check_module_version(self):
        """Check if modules have been updated and trigger reload if needed."""
        try:
            # Check if auto_update module has a version marker
            if 'AIAssistant.auto_update' in sys.modules:
                auto_update = sys.modules['AIAssistant.auto_update']
                if hasattr(auto_update, '_version_marker'):
                    current_version = auto_update._version_marker
                    if self.last_module_version and current_version != self.last_module_version:
                        print(f"[HTTPPolling] 📦 Module version changed: {self.last_module_version} → {current_version}")
                        self._trigger_module_reload()
                    self.last_module_version = current_version
        except Exception:
            pass  # Silently ignore version check errors
    
    def _trigger_module_reload(self):
        """Trigger a full module reload when updates are detected."""
        print("[HTTPPolling] 🔄 Triggering automatic module reload...")
        
        try:
            # Clear all AIAssistant modules except action_queue
            modules_to_remove = [
                key for key in list(sys.modules.keys()) 
                if 'AIAssistant' in key and 'action_queue' not in key
            ]
            
            for module in modules_to_remove:
                del sys.modules[module]
            
            print(f"[HTTPPolling] 🗑️ Cleared {len(modules_to_remove)} cached modules")
            
            # Re-import action handler module to get fresh code
            if self.action_handler:
                # Re-register action handler after reload
                print("[HTTPPolling] 🔄 Re-registering action handler with fresh code...")
                # The handler will be re-imported on next use
            
            print("[HTTPPolling] ✅ Module reload complete - fresh code active")
            
        except Exception as e:
            print(f"[HTTPPolling] ❌ Module reload failed: {e}")
    
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
        
        # Clear modules before reconnecting (fresh start)
        self._trigger_module_reload()
        
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
                    
                    # Restart action queue ticker if needed
                    if self.action_queue:
                        self.action_queue.start_ticker()
                    
                    return True
            
            print(f"❌ Re-registration failed: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Re-registration error: {e}")
        
        # Reset counter to try again after more failures
        self.consecutive_failures = 0
        return False
    
    def _handle_command(self, cmd: dict):
        """Handle incoming command from backend with automatic error recovery."""
        try:
            message_type = cmd.get("type")
            
            if message_type == "execute_action":
                # Execute action requested by dashboard
                action = cmd.get("action")
                params = cmd.get("params", {})
                request_id = cmd.get("request_id")
                
                # Fix action name mapping
                if action == "project_info":
                    action = "get_project_info"
                
                print(f"[HTTPPolling] 📥 Received action: {action} (from background thread)")
                
                if self.action_handler:
                    if self.action_queue:
                        # Use thread-safe queue execution (RECOMMENDED)
                        print(f"[HTTPPolling] 🎯 Queueing action for main thread: {action}")
                        success, result = self.action_queue.queue_action(
                            action, params, timeout=10.0
                        )
                        
                        # Check for threading errors and trigger automatic recovery
                        if not success and result.get("error"):
                            error_msg = str(result.get("error", ""))
                            if any(err in error_msg.lower() for err in 
                                   ["main thread scheduling failed", "thread", "threading", 
                                    "unreal.ticker", "ticker failed"]):
                                print("[HTTPPolling] 🚨 THREADING ERROR DETECTED!")
                                print("[HTTPPolling] 🔄 Triggering automatic module reload for recovery...")
                                self._trigger_emergency_recovery()
                                
                                # Retry the action after recovery
                                print("[HTTPPolling] 🔁 Retrying action after recovery...")
                                success, result = self.action_queue.queue_action(
                                    action, params, timeout=10.0
                                )
                        
                        if success:
                            print(f"[HTTPPolling] ✅ Action executed on main thread: {action}")
                        else:
                            print(f"[HTTPPolling] ❌ Action failed: {result.get('error', 'Unknown error')}")
                        
                        # Send response back via HTTP
                        response = {
                            "request_id": request_id,
                            "action": action,
                            "success": success,
                            "data": result.get("data"),
                            "error": result.get("error")
                        }
                        
                        self.send_message(response)
                        
                    else:
                        # Fallback to direct execution (may cause threading issues)
                        print(f"[HTTPPolling] ⚠️ Direct execution from background thread: {action}")
                        print("[HTTPPolling] ⚠️ This may cause 'Main thread scheduling failed' errors!")
                        
                        try:
                            result = self.action_handler(action, params)
                            
                            # Check for threading errors in response
                            if not result.get("success") and result.get("error"):
                                error_msg = str(result.get("error", ""))
                                if any(err in error_msg.lower() for err in 
                                       ["main thread scheduling failed", "thread", "threading"]):
                                    print("[HTTPPolling] 🚨 THREADING ERROR DETECTED!")
                                    print("[HTTPPolling] 🔄 Triggering automatic module reload for recovery...")
                                    self._trigger_emergency_recovery()
                                    
                                    # Retry after recovery
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
                            print(f"[HTTPPolling] Action completed: {action}")
                            
                        except Exception as e:
                            error_msg = str(e)
                            # Check if it's a threading error
                            if any(err in error_msg.lower() for err in 
                                   ["main thread", "thread", "threading", "ticker"]):
                                print("[HTTPPolling] 🚨 THREADING ERROR DETECTED!")
                                self._trigger_emergency_recovery()
                            
                            print(f"[HTTPPolling] ❌ Direct execution error: {e}")
                            self.send_message({
                                "request_id": request_id,
                                "success": False,
                                "error": str(e)
                            })
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
            
            elif message_type == "force_reload":
                # Backend triggered force module reload
                print("📢 Force module reload requested by dashboard!")
                self._trigger_emergency_recovery()
                    
        except Exception as e:
            print(f"❌ Error handling command: {e}")
    
    def _handle_auto_update(self):
        """Handle auto-update triggered by backend."""
        try:
            print("[HTTPPolling] 🔄 Starting auto-update process...")
            
            # Check if we're in UE5 environment
            try:
                import unreal
            except ImportError:
                print("⚠️ Auto-update skipped (not in UE5 environment)")
                return
            
            # Clear old auto_update module first
            if 'AIAssistant.auto_update' in sys.modules:
                del sys.modules['AIAssistant.auto_update']
                print("[HTTPPolling] Cleared old auto_update module")
            
            # Import fresh auto_update module
            from AIAssistant import auto_update
            
            # Add version marker for tracking
            import uuid
            auto_update._version_marker = str(uuid.uuid4())[:8]
            
            # Run update (safe from background thread)
            result = auto_update.check_and_update()
            
            if result:
                print("[HTTPPolling] ✅ Auto-update completed successfully")
                print("[HTTPPolling] 🔄 Triggering full module reload...")
                
                # Force clear ALL AIAssistant modules except action_queue
                modules_to_remove = [
                    key for key in list(sys.modules.keys()) 
                    if 'AIAssistant' in key and 'action_queue' not in key
                ]
                
                for module in modules_to_remove:
                    del sys.modules[module]
                
                print(f"[HTTPPolling] 🗑️ Cleared {len(modules_to_remove)} cached modules")
                print("[HTTPPolling] ✅ Fresh code will load on next use")
                
                # Update version tracker
                self.last_module_version = auto_update._version_marker
                
            else:
                print("[HTTPPolling] ℹ️ No updates available or update failed")
                
        except Exception as e:
            print(f"[HTTPPolling] ❌ Auto-update failed: {e}")
    
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
        
        # Stop action queue ticker if available
        if self.action_queue:
            self.action_queue.stop_ticker()
        
        print("🔌 HTTP polling disconnected")
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected