"""
Universal Bootstrap Script - Works with both ZIP and TAR.GZ formats.
Run this ONCE in UE5 to get automatic updates working.
"""
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile

import requests


def bootstrap_assistant():
    """Download and install the latest AI Assistant client."""
    print("=" * 60)
    print("🚀 BOOTSTRAPPING UE5 AI ASSISTANT...")
    print("=" * 60)

    # Configuration - use production server
    SERVER_URL = "https://ue5-assistant-noahbutcher97.replit.app"

    try:
        # 1. Download latest client
        print("📦 Downloading latest client from server...")
        response = requests.get(f"{SERVER_URL}/api/download_client",
                                timeout=30)

        if response.status_code != 200:
            print(f"❌ Failed to download client: {response.status_code}")
            return False

        # 2. Detect format based on content
        content = response.content
        print(f"📋 Downloaded {len(content)} bytes")

        # Check first few bytes to determine format
        is_zip = content[:2] == b'PK'  # ZIP signature
        is_gzip = content[:2] == b'\x1f\x8b'  # GZIP signature

        # 3. Extract to temp directory
        print(
            f"📂 Extracting client files (format: {'ZIP' if is_zip else 'TAR.GZ' if is_gzip else 'UNKNOWN'})..."
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            if is_zip:
                # Handle ZIP format
                archive_path = os.path.join(tmpdir, "client.zip")
                with open(archive_path, 'wb') as f:
                    f.write(content)

                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(tmpdir)

            elif is_gzip:
                # Handle TAR.GZ format
                archive_path = os.path.join(tmpdir, "client.tar.gz")
                with open(archive_path, 'wb') as f:
                    f.write(content)

                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(tmpdir)
            else:
                print(
                    f"❌ Unknown archive format (first bytes: {content[:10]})")
                return False

            # Find the AIAssistant directory
            extracted_dir = os.path.join(tmpdir, "AIAssistant")
            if not os.path.exists(extracted_dir):
                print("❌ AIAssistant directory not found in archive")
                print(f"📁 Contents of temp dir: {os.listdir(tmpdir)}")
                return False

            # 4. Determine target directory
            # Try to auto-detect or use default path
            import unreal  # type: ignore
            project_path = unreal.Paths.project_content_dir()
            target_dir = os.path.join(project_path, "Python", "AIAssistant")

            # 5. Backup old files if they exist
            if os.path.exists(target_dir):
                backup_dir = target_dir + "_backup"
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                print("📋 Backing up existing files...")
                shutil.move(target_dir, backup_dir)

            # 6. Ensure Python directory exists
            python_dir = os.path.dirname(target_dir)
            if not os.path.exists(python_dir):
                os.makedirs(python_dir)

            # 7. Copy new files
            print(f"✅ Installing latest client to: {target_dir}")
            shutil.copytree(extracted_dir, target_dir)

        print("=" * 60)
        print("✅ BOOTSTRAP COMPLETE!")
        print("=" * 60)

        # 8. Clear any cached modules
        modules_to_clear = [
            key for key in list(sys.modules.keys()) if 'AIAssistant' in key
        ]
        for module in modules_to_clear:
            del sys.modules[module]

        # 9. Initialize the assistant with fresh code
        print("🔄 Initializing AI Assistant with latest code...")
        try:
            # Make sure path is in sys.path
            if python_dir not in sys.path:
                sys.path.append(python_dir)

            from AIAssistant.system import startup
            startup.configure_and_start()
            print("=" * 60)
            print("✅ AI ASSISTANT READY WITH AUTO-UPDATES ENABLED!")
            print("=" * 60)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ Bootstrap error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    bootstrap_assistant()
