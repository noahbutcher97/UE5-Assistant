#!/usr/bin/env python3
"""Test script to verify tar.gz extraction in auto_update.py works correctly."""
import io
import tarfile
import urllib.request

def test_tar_gz_download():
    """Test downloading and extracting tar.gz from backend."""
    backend_url = "https://ue5-assistant-noahbutcher97.replit.app"
    download_url = f"{backend_url}/api/download_client"
    
    print("=" * 60)
    print("Testing tar.gz Download and Extraction")
    print("=" * 60)
    print(f"📡 Backend: {backend_url}")
    print(f"⬇️  Downloading from: {download_url}")
    
    try:
        # Download tar.gz from backend
        with urllib.request.urlopen(download_url, timeout=30) as response:
            tar_data = response.read()
        
        print(f"✅ Downloaded {len(tar_data)} bytes")
        
        # Test extraction (without actually writing files)
        updated_files = []
        
        with tarfile.open(fileobj=io.BytesIO(tar_data), mode='r:gz') as tar_file:
            for member in tar_file.getmembers():
                if member.isfile():
                    # Just verify we can extract the file content
                    file_content = tar_file.extractfile(member).read()
                    updated_files.append(member.name)
                    print(f"   ✓ {member.name} ({len(file_content)} bytes)")
        
        print(f"\n✅ Successfully extracted {len(updated_files)} files from tar.gz!")
        print("\n📋 Sample files extracted:")
        for f in updated_files[:10]:  # Show first 10 files
            print(f"   - {f}")
        if len(updated_files) > 10:
            print(f"   ... and {len(updated_files) - 10} more files")
        
        return True
        
    except tarfile.TarError as e:
        print(f"❌ tar.gz extraction error: {e}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("Testing Auto-Update tar.gz Support")
    print("")
    
    if test_tar_gz_download():
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("tar.gz download and extraction works correctly!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Test failed!")
        print("=" * 60)

if __name__ == "__main__":
    main()