"""
WebSocket Manager for UE5 <-> Dashboard Communication
Enables real-time bidirectional communication between browser and Unreal Engine.
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections between UE5 clients and dashboard."""
    
    def __init__(self):
        # Active UE5 client connections (keyed by project_id)
        self.ue5_clients: Dict[str, WebSocket] = {}
        
        # Active dashboard connections
        self.dashboard_clients: Set[WebSocket] = set()
        
        # Pending requests waiting for UE5 response
        self.pending_requests: Dict[str, dict] = {}
    
    async def connect_ue5(self, websocket: WebSocket, project_id: str):
        """Register UE5 client connection."""
        await websocket.accept()
        self.ue5_clients[project_id] = websocket
        print(f"✅ UE5 client connected: {project_id}")
        
        # Notify dashboards
        await self.broadcast_to_dashboards({
            "type": "ue5_status",
            "project_id": project_id,
            "status": "connected",
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Register dashboard connection."""
        await websocket.accept()
        self.dashboard_clients.add(websocket)
        print(f"✅ Dashboard connected (total: {len(self.dashboard_clients)})")
        
        # Send current UE5 connection status
        connected_projects = list(self.ue5_clients.keys())
        await websocket.send_json({
            "type": "initial_status",
            "connected_projects": connected_projects,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect_ue5(self, project_id: str):
        """Unregister UE5 client."""
        if project_id in self.ue5_clients:
            del self.ue5_clients[project_id]
            print(f"❌ UE5 client disconnected: {project_id}")
    
    def disconnect_dashboard(self, websocket: WebSocket):
        """Unregister dashboard connection."""
        self.dashboard_clients.discard(websocket)
        print(f"❌ Dashboard disconnected (remaining: {len(self.dashboard_clients)})")
    
    async def send_command_to_ue5(self, project_id: str, command: dict) -> dict:
        """
        Send command from dashboard to UE5 and wait for response.
        
        Args:
            project_id: Target UE5 project
            command: Command data with 'action' and 'params'
        
        Returns:
            Response from UE5 or error dict
        """
        if project_id not in self.ue5_clients:
            return {
                "success": False,
                "error": f"UE5 client not connected for project: {project_id}"
            }
        
        # Generate request ID
        request_id = f"req_{datetime.now().timestamp()}"
        command["request_id"] = request_id
        
        try:
            # Send command to UE5
            websocket = self.ue5_clients[project_id]
            await websocket.send_json(command)
            
            # Wait for response (with timeout)
            response = await asyncio.wait_for(
                self._wait_for_response(request_id),
                timeout=30.0
            )
            
            return response
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "UE5 response timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command failed: {str(e)}"
            }
    
    async def _wait_for_response(self, request_id: str) -> dict:
        """Wait for UE5 to respond to a request."""
        # Poll for response (simple implementation)
        for _ in range(300):  # 30 seconds (100ms intervals)
            if request_id in self.pending_requests:
                response = self.pending_requests.pop(request_id)
                return response
            await asyncio.sleep(0.1)
        
        raise asyncio.TimeoutError()
    
    async def handle_ue5_response(self, project_id: str, response: dict):
        """Handle response from UE5 client."""
        request_id = response.get("request_id")
        
        if request_id:
            # Store response for pending request
            self.pending_requests[request_id] = response
        
        # Also broadcast to dashboards for real-time updates
        await self.broadcast_to_dashboards({
            "type": "ue5_response",
            "project_id": project_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_to_dashboards(self, message: dict):
        """Broadcast message to all connected dashboards."""
        disconnected = set()
        
        for dashboard in self.dashboard_clients:
            try:
                await dashboard.send_json(message)
            except Exception:
                disconnected.add(dashboard)
        
        # Clean up disconnected clients
        for client in disconnected:
            self.disconnect_dashboard(client)


# Global manager instance
manager = ConnectionManager()


def get_manager() -> ConnectionManager:
    """Get the global WebSocket manager."""
    return manager
