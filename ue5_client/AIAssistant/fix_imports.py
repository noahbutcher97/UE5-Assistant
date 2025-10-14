#!/usr/bin/env python3
"""
Script to fix all imports after folder reorganization.
Maps old flat structure imports to new folder-based imports.
"""
import os
import re

# Import mapping: old pattern -> new pattern (for files in subfolders)
IMPORT_MAPPING = {
    # Core module imports
    r'from \.config import': r'from ..core.config import',
    r'from \.main import': r'from ..core.main import',
    r'from \.utils import': r'from ..core.utils import',
    
    # Network imports  
    r'from \.api_client import': r'from ..network.api_client import',
    r'from \.async_client import': r'from ..network.async_client import',
    r'from \.http_polling_client import': r'from ..network.http_polling_client import',
    r'from \.websocket_client import': r'from ..network.websocket_client import',
    
    # Execution imports
    r'from \.action_executor import': r'from ..execution.action_executor import',
    r'from \.action_executor_extensions import': r'from ..execution.action_executor_extensions import',
    r'from \.action_queue import': r'from ..execution.action_queue import',
    
    # UI imports
    r'from \.ui_manager import': r'from ..ui.ui_manager import',
    r'from \.toolbar_menu import': r'from ..ui.toolbar_menu import',
    
    # Collection imports
    r'from \.context_collector import': r'from ..collection.context_collector import',
    r'from \.file_collector import': r'from ..collection.file_collector import',
    r'from \.project_metadata_collector import': r'from ..collection.project_metadata_collector import',
    
    # System imports
    r'from \.auto_update import': r'from ..system.auto_update import',
    r'from \.startup import': r'from ..system.startup import',
    r'from \.project_registration import': r'from ..system.project_registration import',
    r'from \.install_dependencies import': r'from ..system.install_dependencies import',
    r'from \.clear_and_reload import': r'from ..system.clear_and_reload import',
    r'from \.local_server import': r'from ..system.local_server import',
    
    # Tools imports
    r'from \.scene_orchestrator import': r'from ..tools.scene_orchestrator import',
    r'from \.viewport_controller import': r'from ..tools.viewport_controller import',
    r'from \.actor_manipulator import': r'from ..tools.actor_manipulator import',
    r'from \.ai_agent_utility_generator import': r'from ..tools.ai_agent_utility_generator import',
    r'from \.editor_utility_generator import': r'from ..tools.editor_utility_generator import',
    r'from \.blueprint_capture import': r'from ..tools.blueprint_capture import',
    r'from \.blueprint_helpers import': r'from ..tools.blueprint_helpers import',
    
    # Troubleshoot imports
    r'from \.troubleshooter import': r'from ..troubleshoot.troubleshooter import',
    r'from \.diagnose import': r'from ..troubleshoot.diagnose import',
    r'from \.connection_troubleshooter import': r'from ..troubleshoot.connection_troubleshooter import',
}

# Same-folder imports (single dot stays)
SAME_FOLDER_MAPPING = {
    # Within core folder
    r'from \.config import': r'from .config import',
    r'from \.utils import': r'from .utils import',
    r'from \.main import': r'from .main import',
}

def fix_file_imports(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Determine which mappings to use based on file location
        folder = os.path.dirname(filepath)
        folder_name = os.path.basename(folder)
        
        # For files in subfolders, use parent imports (..)
        if folder_name in ['core', 'network', 'execution', 'ui', 'collection', 'system', 'tools', 'troubleshoot']:
            for old_pattern, new_pattern in IMPORT_MAPPING.items():
                content = re.sub(old_pattern, new_pattern, content)
        
        # Save if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Process all Python files."""
    files_updated = 0
    files_processed = 0
    
    # Files to process (from our analysis)
    target_files = [
        './collection/context_collector.py',
        './execution/action_executor.py',
        './execution/action_executor_extensions.py',
        './network/api_client.py',
        './network/async_client.py',
        './network/websocket_client.py',
        './system/auto_update.py',
        './system/local_server.py',
        './ui/ui_manager.py',
    ]
    
    for filepath in target_files:
        files_processed += 1
        if fix_file_imports(filepath):
            files_updated += 1
            print(f"✅ Updated: {filepath}")
        else:
            print(f"⏭️  Skipped: {filepath} (no changes)")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files updated: {files_updated}")
    print(f"   Files unchanged: {files_processed - files_updated}")

if __name__ == '__main__':
    main()
