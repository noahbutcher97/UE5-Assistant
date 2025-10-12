"""
Auto-Update System for UE5 AI Assistant Client
Downloads latest client files from Replit and installs them automatically.
Now with automatic cache clearing and version tracking.

Usage in UE5 Python Console:
    import AIAssistant.auto_update
    # Shows current version and checks for updates
"""
import importlib
import io
import os
import sys
import tarfile
import threading
import urllib.error
import urllib.request
import uuid
import zipfile

# Version marker for tracking module updates (changes with each update)
_version_marker = str(uuid.uuid4())[:8]

# Optional unreal import for testing outside UE5
try:
    import unreal  # type: ignore
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
        
        @staticmethod
        def log_warning(msg, *args):
            print(f"[UE5 WARNING] {msg}")
    
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
    except (ImportError, AttributeError):
        return "https://ue5-assistant-noahbutcher97.replit.app"


def clear_all_modules(preserve_queue=False):
    """
    Clear all AIAssistant modules from Python's cache.
    This ensures fresh code is loaded after updates.
    
    Args:
        preserve_queue: If True, keeps action_queue module (default False for complete reload)
    """
    print("[AutoUpdate] 🗑️ Clearing module cache...")
    
    # Store action queue reference if needed
    action_queue_ref = None
    if preserve_queue and 'AIAssistant.action_queue' in sys.modules:
        try:
            from .action_queue import get_action_queue
            action_queue_ref = get_action_queue()
            print("[AutoUpdate] 📦 Preserving action queue reference...")
        except (ImportError, AttributeError):
            pass
    
    # Get list of ALL AIAssistant modules (including action_queue for complete reload)
    if preserve_queue:
        modules_to_remove = [
            key for key in list(sys.modules.keys()) 
            if 'AIAssistant' in key and 'action_queue' not in key
        ]
    else:
        # Complete clear - remove everything including action_queue
        modules_to_remove = [
            key for key in list(sys.modules.keys()) 
            if 'AIAssistant' in key
        ]
    
    # Clear each module
    for module_name in modules_to_remove:
        try:
            # Get module reference before deletion
            module = sys.modules.get(module_name)
            
            # Clean up module's globals if possible
            if module and hasattr(module, '__dict__'):
                module.__dict__.clear()
            
            # Remove from sys.modules
            del sys.modules[module_name]
        except Exception:
            pass  # Module may already be deleted
    
    print(f"[AutoUpdate] ✅ Cleared {len(modules_to_remove)} cached modules")
    
    # Also clear importlib caches
    try:
        importlib.invalidate_caches()
        print("[AutoUpdate] ✅ Invalidated import caches")
    except (ImportError, AttributeError):
        pass
    
    # Trigger garbage collection
    import gc
    gc.collect()
    
    return len(modules_to_remove)


def check_and_update(mode="auto"):
    """
    Check for updates and install if available.
    
    Args:
        mode: "auto" (default) - Normal update with auto-restart
              "no_restart" - Emergency update mode, no automatic restart (manual restart required)
    
    Returns:
        True if update was successful, False otherwise
    """
    global _version_marker
    
    # Update version marker for this run
    _version_marker = str(uuid.uuid4())[:8]
    
    # Check if on background thread
    is_background_thread = HAS_UNREAL and threading.current_thread() != threading.main_thread()
    
    if mode == "no_restart":
        print("=" * 60)
        print("🚨 EMERGENCY UPDATE MODE (No Auto-Restart)")
        print("=" * 60)
        print("⚠️  Files will be updated WITHOUT restarting UE5")
        print("⚠️  You MUST manually restart UE5 after update completes")
        print("=" * 60)
        
        # Always use background-safe update for emergency mode
        result = _do_background_update(skip_restart=True)
        
        if result:
            print("=" * 60)
            print("✅ EMERGENCY UPDATE COMPLETE!")
            print("🔄 Please restart Unreal Engine 5 manually now")
            print("=" * 60)
            
            # Show notification in UE5 if possible
            if HAS_UNREAL and threading.current_thread() == threading.main_thread():
                try:
                    unreal.EditorDialog.show_message(
                        "Emergency Update Complete",
                        "Client files have been updated successfully.\n\nPlease restart Unreal Engine 5 now to apply the fixes.",
                        unreal.AppMsgType.OK
                    )
                except:
                    pass  # If dialog fails, continue - user saw console message
        return result
    
    # Normal auto mode
    if is_background_thread:
        print("📢 Auto-update triggered from background thread")
        print("⬇️  Downloading and installing files...")
        # Call background-safe version
        result = _do_background_update()
    else:
        # On main thread, run full update with logging
        result = _do_update()
    
    # If update successful, version marker changed
    # Ticker will detect version change and trigger restart on main thread
    if result and mode == "auto":
        print(f"[AutoUpdate] 📦 Files updated successfully!")
        print(f"[AutoUpdate] ✅ Version marker updated: {_version_marker}")
        print(f"[AutoUpdate] ⏳ Ticker will detect version change and restart on main thread...")
    
    return result


def _do_background_update(skip_restart=False):
    """
    Update function that runs safely from background thread (no Unreal API calls).
    
    Args:
        skip_restart: If True, skips automatic restart (for emergency mode)
    
    Returns:
        True if update successful, False otherwise
    """
    global _version_marker
    backend_url = get_backend_url()
    download_url = f"{backend_url}/api/download_client"
    
    title = "🚨 EMERGENCY UPDATE (No Restart)" if skip_restart else "🔄 UE5 AI Assistant Auto-Update (Background Thread Safe)"
    
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(f"📡 Backend: {backend_url}")
    print(f"📦 Version: {_version_marker}")
    
    try:
        # Download archive from backend
        print(f"⬇️  Downloading: {download_url}")
        
        with urllib.request.urlopen(download_url, timeout=30) as response:
            archive_data = response.read()
        
        print(f"✅ Downloaded {len(archive_data)} bytes")
        
        # Detect format by magic bytes
        is_zip = False
        is_tar_gz = False
        
        if len(archive_data) >= 2:
            # Check magic bytes
            if archive_data[:2] == b'PK':  # ZIP magic bytes (0x50 0x4B)
                is_zip = True
                print("📦 Detected format: ZIP")
            elif archive_data[:2] == b'\x1f\x8b':  # GZIP magic bytes
                is_tar_gz = True
                print("📦 Detected format: TAR.GZ")
            else:
                # Try to determine by attempting TAR.GZ extraction
                print("⚠️ Unknown format, attempting TAR.GZ extraction...")
                is_tar_gz = True
        else:
            print("⚠️ Archive too small, assuming TAR.GZ format...")
            is_tar_gz = True
        
        # Extract archive (pure Python, no Unreal API)
        import pathlib
        
        # Find project dir from current module path
        current_file = pathlib.Path(__file__).resolve()
        # Go up from: Content/Python/AIAssistant/auto_update.py -> project root
        project_dir = str(current_file.parent.parent.parent.parent)
        target_base = os.path.join(project_dir, "Content", "Python")
        
        updated_files = []
        
        # Extract based on detected format
        if is_zip:
            # Extract ZIP archive
            import zipfile
            
            try:
                with zipfile.ZipFile(io.BytesIO(archive_data), 'r') as zip_file:
                    for file_info in zip_file.filelist:
                        if not file_info.is_dir():
                            # Extract file content
                            file_content = zip_file.read(file_info.filename)
                            
                            target_path = os.path.join(target_base, file_info.filename)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            with open(target_path, 'wb') as target_file:
                                target_file.write(file_content)
                            
                            updated_files.append(file_info.filename)
            except zipfile.BadZipFile as e:
                print(f"❌ Invalid ZIP file: {e}")
                return False
        
        elif is_tar_gz:
            # Extract TAR.GZ archive
            try:
                with tarfile.open(fileobj=io.BytesIO(archive_data), mode='r:gz') as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            # Extract file content
                            file_content = tar_file.extractfile(member).read()
                            
                            target_path = os.path.join(target_base, member.name)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            with open(target_path, 'wb') as target_file:
                                target_file.write(file_content)
                            
                            updated_files.append(member.name)
            except tarfile.TarError as e:
                print(f"❌ Invalid TAR.GZ file: {e}")
                return False
        
        else:
            print("❌ Unable to determine archive format!")
            return False
        
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
        except (OSError, IOError) as e:
            print(f"⚠️ Could not clear bytecode cache: {e}")
        
        print("=" * 60)
        if skip_restart:
            print("✅ EMERGENCY UPDATE COMPLETE! Files downloaded and installed.")
            print(f"📦 New version marker: {_version_marker}")
            print("⚠️  NO automatic restart was performed!")
            print("✅ Emergency update complete. Please restart UE5 manually.")
            print("🔄 Please restart Unreal Engine 5 manually to apply fixes")
        else:
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
        # Download archive from backend
        unreal.log(f"⬇️  Downloading latest client from: {download_url}")
        
        with urllib.request.urlopen(download_url, timeout=30) as response:
            archive_data = response.read()
        
        unreal.log(f"✅ Downloaded {len(archive_data)} bytes")
        
        # Detect format by magic bytes
        is_zip = False
        is_tar_gz = False
        
        if len(archive_data) >= 2:
            # Check magic bytes
            if archive_data[:2] == b'PK':  # ZIP magic bytes (0x50 0x4B)
                is_zip = True
                unreal.log("📦 Detected format: ZIP")
            elif archive_data[:2] == b'\x1f\x8b':  # GZIP magic bytes
                is_tar_gz = True
                unreal.log("📦 Detected format: TAR.GZ")
            else:
                # Try to determine by attempting TAR.GZ extraction
                unreal.log("⚠️ Unknown format, attempting TAR.GZ extraction...")
                is_tar_gz = True
        else:
            unreal.log("⚠️ Archive too small, assuming TAR.GZ format...")
            is_tar_gz = True
        
        # Get project directory for extraction
        project_dir = unreal.Paths.project_dir()
        target_base = os.path.join(project_dir, "Content", "Python")
        
        updated_files = []
        
        # Extract based on detected format
        if is_zip:
            # Extract ZIP archive
            import zipfile
            
            try:
                with zipfile.ZipFile(io.BytesIO(archive_data), 'r') as zip_file:
                    for file_info in zip_file.filelist:
                        if not file_info.is_dir():
                            # Extract file content
                            file_content = zip_file.read(file_info.filename)
                            
                            target_path = os.path.join(target_base, file_info.filename)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            with open(target_path, 'wb') as target_file:
                                target_file.write(file_content)
                            
                            updated_files.append(file_info.filename)
            except zipfile.BadZipFile as e:
                unreal.log_error(f"❌ Invalid ZIP file: {e}")
                return False
        
        elif is_tar_gz:
            # Extract TAR.GZ archive
            try:
                with tarfile.open(fileobj=io.BytesIO(archive_data), mode='r:gz') as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            # Extract file content
                            file_content = tar_file.extractfile(member).read()
                            
                            # Extract to target
                            target_path = os.path.join(target_base, member.name)
                            
                            # Create parent directories
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            # Write file
                            with open(target_path, 'wb') as target_file:
                                target_file.write(file_content)
                            
                            updated_files.append(member.name)
            except tarfile.TarError as e:
                unreal.log_error(f"❌ Invalid TAR.GZ file: {e}")
                return False
        
        else:
            unreal.log_error("❌ Unable to determine archive format!")
            return False
        
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
        except (OSError, IOError) as e:
            unreal.log_warning(f"⚠️ Could not clear bytecode cache: {e}")
        
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


def force_restart_assistant():
    """
    Force restart the AI Assistant with completely fresh code.
    This is called automatically after updates and can also be triggered manually.
    """
    print("=" * 60)
    print("🚀 Force Restarting AI Assistant with Fresh Code")
    print("=" * 60)
    
    try:
        # Step 1: Stop existing connections if any
        print("📦 Step 1: Stopping existing connections...")
        try:
            # Try to stop HTTP polling if it exists
            if 'AIAssistant.main' in sys.modules:
                main_module = sys.modules['AIAssistant.main']
                if hasattr(main_module, '_assistant_instance'):
                    assistant = main_module._assistant_instance
                    if hasattr(assistant, 'http_client') and assistant.http_client:
                        assistant.http_client.disconnect()
                        print("   - Stopped HTTP polling client")
                    if hasattr(assistant, 'ws_client') and assistant.ws_client:
                        assistant.ws_client.disconnect()
                        print("   - Stopped WebSocket client")
        except Exception as e:
            print(f"   - Could not stop existing connections: {e}")
        
        # Step 2: Clear ALL modules completely
        print("📦 Step 2: Clearing all module cache...")
        cleared = clear_all_modules(preserve_queue=False)
        print(f"   - Cleared {cleared} modules")
        
        # Step 3: Invalidate import caches
        importlib.invalidate_caches()
        
        # Step 4: Force reimport main module
        print("📦 Step 3: Re-importing main module with fresh code...")
        import AIAssistant.main as fresh_main
        
        # Step 5: Re-initialize the assistant with fresh code
        print("📦 Step 4: Re-initializing assistant...")
        fresh_main.get_assistant()  # Creates new instance with fresh code
        
        print("✅ AI Assistant restarted with fresh code!")
        print(f"📦 Current version: {_version_marker}")
        
        return True
        
    except Exception as e:
        print(f"❌ Restart failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("=" * 60)


def force_reload_all():
    """
    Force a complete reload of all AIAssistant modules.
    Useful for manual troubleshooting or after file changes.
    """
    print("=" * 60)
    print("🔄 Force Reloading All AIAssistant Modules")
    print("=" * 60)
    
    # Use the new force restart function
    success = force_restart_assistant()
    
    if success:
        print("✅ All modules reloaded successfully!")
        print(f"📦 Current version: {_version_marker}")
    else:
        print("❌ Reload encountered issues - check logs above")
    
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