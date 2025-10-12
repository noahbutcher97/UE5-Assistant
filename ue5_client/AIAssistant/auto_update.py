"""
Auto-Update System for UE5 AI Assistant Client
Downloads latest client files from Replit and installs them automatically.
Now with automatic cache clearing and version tracking.

Usage in UE5 Python Console:
    import AIAssistant.auto_update
    # Shows current version and checks for updates
"""
import io
import os
import sys
import uuid
import importlib
import threading
import urllib.request
import urllib.error
import zipfile

# Version marker for tracking module updates (changes with each update)
_version_marker = str(uuid.uuid4())[:8]

# Optional unreal import for testing outside UE5
try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    # Create mock unreal module for testing
    class MockPaths:
        @staticmethod
        def project_dir():
            return "/mock/project"
    
    class MockUnreal:
        Paths = MockPaths
        
        @staticmethod
        def log(msg, *args):
            print(f"[UE5] {msg}")
        
        @staticmethod
        def log_error(msg, *args):
            print(f"[UE5 ERROR] {msg}")
    
    unreal = MockUnreal()


def _safe_log(message, is_error=False):
    """Safe logging that works both in UE5 and standalone environments."""
    if HAS_UNREAL:
        if is_error:
            unreal.log_error(message)
        else:
            unreal.log(message)
    else:
        prefix = "[ERROR]" if is_error else "[INFO]"
        print(f"{prefix} {message}")


def get_backend_url():
    """Get backend URL from config."""
    try:
        from .config import get_config
        config = get_config()
        return config.api_url
    except:
        return "https://ue5-assistant-noahbutcher97.replit.app"


def clear_all_modules():
    """
    Clear all AIAssistant modules from Python's cache.
    This ensures fresh code is loaded after updates.
    """
    print("[AutoUpdate] 🗑️ Clearing module cache...")
    
    # Get list of modules to clear (exclude action_queue to preserve the ticker)
    modules_to_remove = [
        key for key in list(sys.modules.keys()) 
        if 'AIAssistant' in key and 'action_queue' not in key
    ]
    
    # Clear each module
    for module_name in modules_to_remove:
        try:
            del sys.modules[module_name]
        except:
            pass  # Module may already be deleted
    
    print(f"[AutoUpdate] ✅ Cleared {len(modules_to_remove)} cached modules")
    
    # Trigger garbage collection
    import gc
    gc.collect()
    
    return len(modules_to_remove)


def check_and_update():
    """
    Check for updates and install if available.
    Automatically clears module cache after successful update.
    """
    global _version_marker
    
    # Update version marker for this run
    _version_marker = str(uuid.uuid4())[:8]
    
    # Check if on background thread
    if HAS_UNREAL and threading.current_thread() != threading.main_thread():
        print("📢 Auto-update triggered from background thread")
        print("⬇️  Downloading and installing files...")
        # Call background-safe version
        result = _do_background_update()
    else:
        # On main thread, run full update with logging
        result = _do_update()
    
    # If update successful, clear module cache
    if result:
        cleared = clear_all_modules()
        print(f"[AutoUpdate] 🔄 Module cache cleared ({cleared} modules)")
        print("[AutoUpdate] ✅ Fresh code will be loaded on next use")
    
    return result


def _do_background_update():
    """Update function that runs safely from background thread (no Unreal API calls)."""
    global _version_marker
    backend_url = get_backend_url()
    download_url = f"{backend_url}/api/download_client"
    
    print("=" * 60)
    print("🔄 UE5 AI Assistant Auto-Update (Background Thread Safe)")
    print("=" * 60)
    print(f"📡 Backend: {backend_url}")
    print(f"📦 Version: {_version_marker}")
    
    try:
        # Download ZIP from backend
        print(f"⬇️  Downloading: {download_url}")
        
        with urllib.request.urlopen(download_url, timeout=30) as response:
            zip_data = response.read()
        
        print(f"✅ Downloaded {len(zip_data)} bytes")
        
        # Extract ZIP (pure Python, no Unreal API)
        import pathlib
        
        # Find project dir from current module path
        current_file = pathlib.Path(__file__).resolve()
        # Go up from: Content/Python/AIAssistant/auto_update.py -> project root
        project_dir = str(current_file.parent.parent.parent.parent)
        target_base = os.path.join(project_dir, "Content", "Python")
        
        updated_files = []
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
            for file_info in zip_file.filelist:
                if file_info.filename.endswith('/'):
                    continue
                
                target_path = os.path.join(target_base, file_info.filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with open(target_path, 'wb') as target_file:
                    target_file.write(zip_file.read(file_info.filename))
                
                updated_files.append(file_info.filename)
        
        print(f"✅ Updated {len(updated_files)} files")
        
        # Update version marker
        _version_marker = str(uuid.uuid4())[:8]
        
        # Clear Python's bytecode cache for updated files
        try:
            import shutil
            cache_dir = os.path.join(target_base, "AIAssistant", "__pycache__")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                print("✅ Cleared Python bytecode cache")
        except:
            pass
        
        print("=" * 60)
        print("✅ Auto-update complete! Files downloaded and installed.")
        print(f"📦 New version marker: {_version_marker}")
        print("🔄 Module cache will be cleared automatically...")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def _do_update():
    """Internal update function that must run on main thread."""
    global _version_marker
    backend_url = get_backend_url()
    download_url = f"{backend_url}/api/download_client"
    
    unreal.log("=" * 60)
    unreal.log("🔄 UE5 AI Assistant Auto-Update (Main Thread)")
    unreal.log("=" * 60)
    unreal.log(f"📡 Backend: {backend_url}")
    unreal.log(f"📦 Current Version: {_version_marker}")
    
    try:
        # Download ZIP from backend
        unreal.log(f"⬇️  Downloading latest client from: {download_url}")
        
        with urllib.request.urlopen(download_url, timeout=30) as response:
            zip_data = response.read()
        
        unreal.log(f"✅ Downloaded {len(zip_data)} bytes")
        
        # Extract ZIP
        project_dir = unreal.Paths.project_dir()
        target_base = os.path.join(project_dir, "Content", "Python")
        
        updated_files = []
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
            for file_info in zip_file.filelist:
                if file_info.filename.endswith('/'):
                    continue  # Skip directories
                
                # Extract to target
                target_path = os.path.join(target_base, file_info.filename)
                
                # Create parent directories
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Write file
                with open(target_path, 'wb') as target_file:
                    target_file.write(zip_file.read(file_info.filename))
                
                updated_files.append(file_info.filename)
        
        unreal.log(f"✅ Updated {len(updated_files)} files")
        
        # Update version marker
        _version_marker = str(uuid.uuid4())[:8]
        
        # Clear Python's bytecode cache
        try:
            import shutil
            cache_dir = os.path.join(target_base, "AIAssistant", "__pycache__")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                unreal.log("✅ Cleared Python bytecode cache")
        except:
            pass
        
        # Create auto_start.py for auto-initialization
        auto_start_path = os.path.join(target_base, "auto_start.py")
        auto_start_content = """# Auto-generated initialization script for UE5 AI Assistant
# This file automatically initializes the AI Assistant when UE5 loads

import unreal

try:
    # Import and initialize the AI Assistant
    import AIAssistant.main
    unreal.log("✅ AI Assistant auto-initialized successfully!")
except Exception as e:
    unreal.log_error(f"❌ Failed to auto-initialize AI Assistant: {e}")
    unreal.log("💡 You can manually initialize by running: import AIAssistant.main")
"""
        try:
            with open(auto_start_path, 'w') as f:
                f.write(auto_start_content)
            unreal.log("✅ Created auto_start.py for automatic initialization")
        except Exception as e:
            unreal.log_error(f"⚠️ Could not create auto_start.py: {e}")
        
        unreal.log("=" * 60)
        unreal.log("📋 Updated Files:")
        for f in updated_files[:10]:  # Show first 10 files
            unreal.log(f"   - {f}")
        if len(updated_files) > 10:
            unreal.log(f"   ... and {len(updated_files) - 10} more files")
        
        # Auto-configure backend URL
        unreal.log("🔧 Configuring backend connection...")
        try:
            from .config import get_config
            config = get_config()
            
            # Ensure we're using the correct server
            if config.get("active_server") != "production":
                config.set("active_server", "production")
                unreal.log(f"✅ Backend configured: {config.api_url}")
            else:
                unreal.log(f"✅ Backend already configured: {config.api_url}")
                
        except Exception as e:
            unreal.log_error(f"⚠️ Config auto-fix failed: {e}")
            unreal.log("💡 Manually run: from AIAssistant.config import get_config; get_config().set('active_server', 'production')")
        
        unreal.log("=" * 60)
        unreal.log("✅ Update complete!")
        unreal.log(f"📦 New version marker: {_version_marker}")
        unreal.log("🔄 Module cache cleared - fresh code ready!")
        unreal.log("✨ No restart required - changes take effect immediately!")
        unreal.log("=" * 60)
        
        return True
        
    except urllib.error.URLError as e:
        unreal.log_error(f"❌ Network error: {e}")
        unreal.log_error("   Check your internet connection and backend URL")
        return False
    except Exception as e:
        unreal.log_error(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def force_reload_all():
    """
    Force a complete reload of all AIAssistant modules.
    Useful for manual troubleshooting or after file changes.
    """
    print("=" * 60)
    print("🔄 Force Reloading All AIAssistant Modules")
    print("=" * 60)
    
    # Clear all modules
    cleared = clear_all_modules()
    
    # Try to reinitialize with fresh code
    try:
        print("📦 Re-importing main module with fresh code...")
        import AIAssistant.main
        
        # Re-initialize action queue if needed
        try:
            from .action_queue import get_action_queue
            queue = get_action_queue()
            queue.start_ticker()
            print("✅ Action queue ticker restarted")
        except:
            pass
        
        print("✅ All modules reloaded successfully!")
        print(f"📦 Current version: {_version_marker}")
        
    except Exception as e:
        print(f"❌ Reload failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)


def show_version():
    """Display current client version info."""
    global _version_marker
    
    try:
        # Check if on background thread
        if threading.current_thread() != threading.main_thread():
            _safe_log(f"💡 Auto-update module loaded (v{_version_marker})")
            return
        
        if not HAS_UNREAL:
            print(f"📦 Auto-update module v{_version_marker} (test mode)")
            return
        
        project_dir = unreal.Paths.project_dir()
        client_path = os.path.join(project_dir, "Content", "Python", "AIAssistant")
        
        if os.path.exists(client_path):
            files = [f for f in os.listdir(client_path) if f.endswith('.py')]
            unreal.log(f"📦 Client installed with {len(files)} Python files")
            unreal.log(f"🔖 Version marker: {_version_marker}")
            
            # Check for action_queue.py as version indicator
            queue_file = os.path.join(client_path, "action_queue.py")
            if os.path.exists(queue_file):
                unreal.log("✅ Latest version (includes thread-safe queue)")
            else:
                unreal.log("⚠️  Older version (missing action_queue.py)")
                unreal.log("💡 Run check_and_update() to upgrade")
        else:
            unreal.log("❌ Client not installed")
            
    except Exception as e:
        print(f"Error checking version: {e}")


# Auto-run on import (only show version, don't auto-update)
show_version()

# Only show update hint on main thread
if HAS_UNREAL and threading.current_thread() == threading.main_thread():
    unreal.log("\n💡 Commands:")
    unreal.log("   Update: AIAssistant.auto_update.check_and_update()")
    unreal.log("   Reload: AIAssistant.auto_update.force_reload_all()")
    unreal.log("   Clear:  AIAssistant.auto_update.clear_all_modules()\n")