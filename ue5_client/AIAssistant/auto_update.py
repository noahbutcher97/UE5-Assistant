"""
Auto-Update System for UE5 AI Assistant Client
Downloads latest client files from Replit and installs them automatically.

Usage in UE5 Python Console:
    import AIAssistant.auto_update
    # Shows current version and checks for updates
"""
import io
import os
import urllib.request
import urllib.error
import zipfile

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


def check_and_update():
    """Check for updates and install if available."""
    import threading
    
    # If not on main thread, schedule execution on main thread
    if HAS_UNREAL and threading.current_thread() != threading.main_thread():
        _safe_log("⚙️ Scheduling auto-update on main thread...")
        # Use Python command execution to run on main thread
        try:
            import unreal
            unreal.PythonScriptLibrary.execute_python_command(
                "import AIAssistant.auto_update; AIAssistant.auto_update._do_update()"
            )
            return True
        except Exception as e:
            _safe_log(f"❌ Failed to schedule update: {e}", is_error=True)
            _safe_log("💡 To update: import AIAssistant.auto_update; AIAssistant.auto_update.check_and_update()")
            return False
    
    # If on main thread, run directly
    return _do_update()


def _do_update():
    """Internal update function that must run on main thread."""
    backend_url = get_backend_url()
    download_url = f"{backend_url}/api/download_client"
    
    unreal.log("=" * 60)
    unreal.log("🔄 UE5 AI Assistant Auto-Update")
    unreal.log("=" * 60)
    unreal.log(f"📡 Backend: {backend_url}")
    
    try:
        # Download ZIP from backend (GET for Replit proxy compatibility)
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
        for f in updated_files:
            unreal.log(f"   - {f}")
        unreal.log("=" * 60)
        unreal.log("✅ Update complete!")
        unreal.log("⚠️  IMPORTANT: Restart Unreal Editor for changes to take effect")
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


def show_version():
    """Display current client version info."""
    try:
        import threading
        
        # Only run on main thread (UE5 API restriction)
        if threading.current_thread() != threading.main_thread():
            _safe_log("💡 Auto-update module loaded")
            return
        
        project_dir = unreal.Paths.project_dir()
        client_path = os.path.join(project_dir, "Content", "Python", "AIAssistant")
        
        if os.path.exists(client_path):
            files = [f for f in os.listdir(client_path) if f.endswith('.py')]
            unreal.log(f"📦 Client installed with {len(files)} Python files")
            
            # Check for test_registration.py as version indicator
            test_file = os.path.join(client_path, "test_registration.py")
            if os.path.exists(test_file):
                unreal.log("✅ Latest version (includes diagnostic tools)")
            else:
                unreal.log("⚠️  Older version (missing test_registration.py)")
                unreal.log("💡 Run check_and_update() to upgrade")
        else:
            unreal.log("❌ Client not installed")
            
    except Exception as e:
        unreal.log_error(f"Error checking version: {e}")


# Auto-run on import
show_version()
unreal.log("\n💡 To update: import AIAssistant.auto_update; AIAssistant.auto_update.check_and_update()\n")
