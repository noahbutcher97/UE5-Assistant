"""
WebSocket client for UE5 to enable real-time communication with backend.
"""
import json
import threading
import time
from typing import Optional, Callable, Dict, Any


class WebSocketClient:
    """
    WebSocket client for UE5 to connect to the backend.
    Enables real-time bidirectional communication.
    """
    
    def __init__(self, base_url: str, project_id: str):
        """
        Initialize WebSocket client.
        
        Args:
            base_url: Backend base URL (e.g., "wss://ue5-assistant-noahbutcher97.replit.app")
            project_id: Unique project identifier
        """
        self.base_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        self.project_id = project_id
        self.ws_url = f"{self.base_url}/ws/ue5/{project_id}"
        
        self.ws = None
        self.connected = False
        self.running = False
        self.receive_thread = None
        self.action_handler: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None
        
    def set_action_handler(self, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
        """
        Set the handler for incoming action commands.
        
        Args:
            handler: Function that takes (action, params) and returns response dict
        """
        self.action_handler = handler
    
    def connect(self) -> bool:
        """
        Connect to the WebSocket server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            import websocket
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # Start connection in background thread
            self.running = True
            self.receive_thread = threading.Thread(target=self._run_forever, daemon=True)
            self.receive_thread.start()
            
            # Wait for connection (max 5 seconds)
            for _ in range(50):
                if self.connected:
                    print(f"✅ WebSocket connected: {self.project_id}")
                    return True
                time.sleep(0.1)
            
            return False
            
        except ImportError:
            print("⚠️ websocket-client not installed. Install with: pip install websocket-client")
            return False
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    def _run_forever(self):
        """Run WebSocket connection loop."""
        if self.ws:
            self.ws.run_forever()
    
    def _on_open(self, ws):
        """Handle WebSocket connection opened."""
        self.connected = True
        print(f"🔗 WebSocket opened for project: {self.project_id}")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "execute_action":
                # Execute action requested by dashboard
                action = data.get("action")
                params = data.get("params", {})
                request_id = data.get("request_id")
                
                if self.action_handler:
                    # Execute action
                    result = self.action_handler(action, params)
                    
                    # Send response back
                    response = {
                        "request_id": request_id,
                        "action": action,
                        "success": result.get("success", True),
                        "data": result.get("data"),
                        "error": result.get("error")
                    }
                    
                    self.send_message(response)
                else:
                    # No handler set
                    self.send_message({
                        "request_id": request_id,
                        "success": False,
                        "error": "No action handler configured"
                    })
                    
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error."""
        print(f"❌ WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed."""
        self.connected = False
        print(f"🔌 WebSocket closed: {close_msg}")
    
    def send_message(self, data: dict):
        """
        Send message to backend.
        
        Args:
            data: Message data to send
        """
        if self.ws and self.connected:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
        else:
            print("⚠️ WebSocket not connected")
    
    def disconnect(self):
        """Disconnect from WebSocket server."""
        self.running = False
        if self.ws:
            self.ws.close()
        self.connected = False
        print("🔌 WebSocket disconnected")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected
