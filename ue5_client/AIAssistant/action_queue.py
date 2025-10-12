"""
Thread-safe action queue system for UE5.
Allows background threads to queue actions for execution on the main thread.
"""
import json
import queue
import threading
import time
import uuid
from typing import Any, Callable, Dict, Optional, Tuple

try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    unreal = None


class ActionQueue:
    """
    Singleton action queue for thread-safe command execution.
    Background threads add actions to the queue, main thread processes them.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the action queue (only once)."""
        if self._initialized:
            return
            
        self.queue = queue.Queue()
        self.pending_results = {}  # request_id -> result
        self.result_events = {}    # request_id -> threading.Event
        self._initialized = True
        self.tick_handle = None
        self.action_handler = None
        
        # Track last process time to avoid spamming
        self.last_process_time = 0
        self.min_process_interval = 0.1  # 100ms minimum between processing
        
        # Version tracking for cache invalidation
        self.current_version = str(uuid.uuid4())[:8]
        self.last_update_check = 0
        self.update_check_interval = 30  # Check every 30 seconds
        
        # Auto-start ticker if in UE5
        if HAS_UNREAL:
            self.start_ticker()
    
    def set_action_handler(self, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]):
        """Set the handler for executing actions."""
        self.action_handler = handler
    
    def queue_action(self, action: str, params: Dict[str, Any], 
                     timeout: float = 5.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Queue an action for execution on the main thread.
        
        Args:
            action: Action name to execute
            params: Parameters for the action
            timeout: Maximum time to wait for result (seconds)
        
        Returns:
            Tuple of (success, result_dict)
        """
        request_id = str(uuid.uuid4())
        
        # Create event for synchronization
        event = threading.Event()
        self.result_events[request_id] = event
        
        # Queue the action
        self.queue.put({
            'request_id': request_id,
            'action': action,
            'params': params,
            'timestamp': time.time()
        })
        
        # Wait for result (with timeout)
        if event.wait(timeout):
            # Got result
            result = self.pending_results.pop(request_id, {
                'success': False,
                'error': 'Result not found'
            })
            self.result_events.pop(request_id, None)
            return (result.get('success', False), result)
        else:
            # Timeout
            self.result_events.pop(request_id, None)
            return (False, {
                'success': False,
                'error': f'Action timed out after {timeout} seconds'
            })
    
    def process_queue(self) -> int:
        """
        Process pending actions from the queue.
        This MUST be called from the main thread only!
        
        Returns:
            Number of actions processed
        """
        if not self.action_handler:
            return 0
        
        # Check if enough time has passed since last process
        current_time = time.time()
        if current_time - self.last_process_time < self.min_process_interval:
            return 0
        
        processed = 0
        max_per_tick = 5  # Process max 5 actions per tick to avoid blocking
        
        while not self.queue.empty() and processed < max_per_tick:
            try:
                item = self.queue.get_nowait()
                request_id = item['request_id']
                action = item['action']
                params = item['params']
                
                # Execute the action (on main thread)
                try:
                    result = self.action_handler(action, params)
                    if not isinstance(result, dict):
                        result = {'success': True, 'data': result}
                except Exception as e:
                    result = {
                        'success': False,
                        'error': f'Action execution failed: {str(e)}'
                    }
                
                # Store result and signal completion
                self.pending_results[request_id] = result
                event = self.result_events.get(request_id)
                if event:
                    event.set()
                
                processed += 1
                
            except queue.Empty:
                break
            except Exception as e:
                print(f"[ActionQueue] Error processing action: {e}")
        
        self.last_process_time = current_time
        return processed
    
    def start_ticker(self):
        """Start the Unreal Engine ticker to process queue on main thread."""
        if not HAS_UNREAL:
            print("[ActionQueue] Cannot start ticker - not in UE5 environment")
            return
        
        if self.tick_handle:
            print("[ActionQueue] Ticker already running")
            return
        
        try:
            # Create a ticker that runs on the main thread
            def tick_callback(delta_time):
                """Called by UE5 on main thread every tick."""
                try:
                    # Import time locally to avoid module clearing issues
                    import time as time_module
                    
                    # Process any pending actions
                    num_processed = self.process_queue()
                    
                    # Check for updates periodically
                    current_time = time_module.time()
                    if current_time - self.last_update_check > self.update_check_interval:
                        self._check_for_updates()
                        self.last_update_check = current_time
                    
                    return True  # Continue ticking
                    
                except Exception as e:
                    print(f"[ActionQueue] Tick error: {e}")
                    import traceback
                    traceback.print_exc()
                    return True  # Continue even on error
            
            # Register ticker with UE5
            self.tick_handle = unreal.register_slate_post_tick_callback(tick_callback)
            print(f"[ActionQueue] ✅ Main thread ticker started (v{self.current_version})")
            
        except Exception as e:
            print(f"[ActionQueue] ❌ Failed to start ticker: {e}")
    
    def stop_ticker(self):
        """Stop the Unreal Engine ticker."""
        if not HAS_UNREAL:
            return
        
        if self.tick_handle:
            try:
                unreal.unregister_slate_post_tick_callback(self.tick_handle)
                self.tick_handle = None
                print("[ActionQueue] Ticker stopped")
            except Exception as e:
                print(f"[ActionQueue] Error stopping ticker: {e}")
    
    def _check_for_updates(self):
        """Check if modules have been updated and need reloading."""
        try:
            # Check if auto_update module exists and has new version
            import sys
            if 'AIAssistant.auto_update' in sys.modules:
                auto_update = sys.modules['AIAssistant.auto_update']
                if hasattr(auto_update, '_version_marker'):
                    new_version = auto_update._version_marker
                    if new_version != self.current_version:
                        print(f"[ActionQueue] 🔄 Version change detected: {self.current_version} → {new_version}")
                        self._trigger_module_reload()
                        self.current_version = new_version
        except Exception as e:
            # Silently ignore - checking is optional
            pass
    
    def _trigger_module_reload(self):
        """Trigger a module reload when updates are detected."""
        try:
            import sys
            import importlib
            
            print("[ActionQueue] 🔄 Clearing module cache for updates...")
            
            # Clear all AIAssistant modules
            modules_to_remove = [key for key in list(sys.modules.keys()) if 'AIAssistant' in key]
            for module in modules_to_remove:
                del sys.modules[module]
            
            print(f"[ActionQueue] 🗑️ Cleared {len(modules_to_remove)} cached modules")
            
            # The modules will be re-imported on next use
            print("[ActionQueue] ✅ Modules will reload with fresh code on next use")
            
        except Exception as e:
            print(f"[ActionQueue] ❌ Module reload failed: {e}")
    
    def clear_all(self):
        """Clear all pending actions and results."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
        
        self.pending_results.clear()
        
        # Signal all waiting threads
        for event in self.result_events.values():
            event.set()
        self.result_events.clear()


# Global instance getter
_action_queue: Optional[ActionQueue] = None


def get_action_queue() -> ActionQueue:
    """Get or create the global action queue instance."""
    global _action_queue
    if _action_queue is None:
        _action_queue = ActionQueue()
    return _action_queue


# Auto-initialize when module loads (if in UE5)
if HAS_UNREAL:
    get_action_queue()