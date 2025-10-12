"""
Bootstrap script for UE5 AI Assistant - Run this ONCE to get automatic updates working.
This downloads the latest client code and initializes the assistant properly.
"""
import os
import sys
import tarfile
import tempfile
import shutil
import requests

def bootstrap_assistant():
    """Download and install the latest AI Assistant client."""
    print("=" * 60)
    print("🚀 BOOTSTRAPPING UE5 AI ASSISTANT...")
    print("=" * 60)
    
    # Configuration
    SERVER_URL = "https://ue5-assistant-noahbutcher97.replit.app"
    
    try:
        # 1. Download latest client
        print("📦 Downloading latest client from server...")
        response = requests.get(f"{SERVER_URL}/api/download_client", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to download client: {response.status_code}")
            return False
        
        # 2. Extract to temp directory
        print("📂 Extracting client files...")
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "client.tar.gz")
            
            # Save tar.gz file
            with open(tar_path, 'wb') as f:
                f.write(response.content)
            
            # Extract tar.gz
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(tmpdir)
            
            # Find the AIAssistant directory
            extracted_dir = os.path.join(tmpdir, "AIAssistant")
            if not os.path.exists(extracted_dir):
                print("❌ AIAssistant directory not found in archive")
                return False
            
            # 3. Get current script directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            target_dir = os.path.join(current_dir, "AIAssistant")
            
            # 4. Backup old files if they exist
            if os.path.exists(target_dir):
                backup_dir = target_dir + "_backup"
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                print("📋 Backing up existing files...")
                shutil.move(target_dir, backup_dir)
            
            # 5. Copy new files
            print("✅ Installing latest client...")
            shutil.copytree(extracted_dir, target_dir)
        
        print("=" * 60)
        print("✅ BOOTSTRAP COMPLETE!")
        print("=" * 60)
        
        # 6. Clear any cached modules
        modules_to_clear = [key for key in list(sys.modules.keys()) if 'AIAssistant' in key]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # 7. Initialize the assistant with fresh code
        print("🔄 Initializing AI Assistant with latest code...")
        try:
            import AIAssistant.startup as startup
            startup.configure_and_start()
            print("✅ AI Assistant is ready with auto-updates enabled!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Bootstrap error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    bootstrap_assistant()