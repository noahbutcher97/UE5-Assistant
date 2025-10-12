"""
Comprehensive Test Suite for Auto-Update System
Tests the entire update flow in Replit environment without needing UE5.
"""
import sys
import os
from pathlib import Path

# Add AIAssistant to path (project root is 2 levels up from this file)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "ue5_client"))

def test_import():
    """Test that auto_update can be imported without UE5."""
    print("🧪 Test 1: Import auto_update module...")
    try:
        from AIAssistant import auto_update  # type: ignore
        print("   ✅ Module imported successfully")
        print(f"   📦 Module location: {auto_update.__file__}")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_backend_connection():
    """Test backend URL detection."""
    print("\n🧪 Test 2: Backend URL configuration...")
    try:
        from AIAssistant.auto_update import get_backend_url  # type: ignore
        url = get_backend_url()
        print(f"   ✅ Backend URL: {url}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_download_endpoint():
    """Test the download endpoint."""
    print("\n🧪 Test 3: Download endpoint test...")
    try:
        import urllib.request
        from AIAssistant.auto_update import get_backend_url  # type: ignore
        
        backend_url = get_backend_url()
        download_url = f"{backend_url}/api/download_client"
        
        print(f"   📡 Testing: {download_url}")
        req = urllib.request.Request(download_url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            print(f"   ✅ Downloaded {len(data)} bytes")
            print(f"   📦 Content-Type: {response.headers.get('Content-Type')}")
            
            # Verify it's a ZIP file
            if data[:2] == b'PK':
                print("   ✅ Valid ZIP file signature detected")
                return True
            else:
                print("   ❌ Invalid file format (not a ZIP)")
                return False
                
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_logging():
    """Test safe logging in non-UE5 environment."""
    print("\n🧪 Test 4: Safe logging system...")
    try:
        from AIAssistant.auto_update import _safe_log  # type: ignore
        
        _safe_log("Test normal log")
        _safe_log("Test error log", is_error=True)
        print("   ✅ Safe logging works in test environment")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_version_display():
    """Test version checking in non-UE5 environment."""
    print("\n🧪 Test 5: Version display (non-UE5 environment)...")
    try:
        from AIAssistant.auto_update import show_version  # type: ignore
        show_version()
        print("   ✅ Version check handled gracefully")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_update_prevention():
    """Test that update is prevented in non-UE5 environment."""
    print("\n🧪 Test 6: Update prevention (safety check)...")
    try:
        from AIAssistant.auto_update import check_and_update  # type: ignore
        result = check_and_update()
        
        if result is False:
            print("   ✅ Update correctly prevented in test environment")
            return True
        else:
            print("   ❌ Update should have been prevented")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_zip_contents():
    """Test that downloaded ZIP contains expected files."""
    print("\n🧪 Test 7: ZIP contents verification...")
    try:
        import urllib.request
        import zipfile
        import io
        from AIAssistant.auto_update import get_backend_url  # type: ignore
        
        backend_url = get_backend_url()
        download_url = f"{backend_url}/api/download_client"
        
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            zip_data = response.read()
        
        # Inspect ZIP contents
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            files = zf.namelist()
            print(f"   📦 ZIP contains {len(files)} files:")
            
            expected_files = [
                'AIAssistant/__init__.py',
                'AIAssistant/main.py',
                'AIAssistant/auto_update.py',
                'AIAssistant/diagnose.py',
                'AIAssistant/install_dependencies.py'
            ]
            
            for expected in expected_files:
                if expected in files:
                    print(f"      ✅ {expected}")
                else:
                    print(f"      ❌ Missing: {expected}")
                    
            return all(f in files for f in expected_files)
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run complete test suite."""
    print("=" * 70)
    print("🚀 AUTO-UPDATE SYSTEM TEST SUITE")
    print("=" * 70)
    print("Testing auto-update system in Replit environment (no UE5 required)")
    print()
    
    tests = [
        test_import,
        test_backend_connection,
        test_safe_logging,
        test_version_display,
        test_update_prevention,
        test_download_endpoint,
        test_zip_contents
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print("\n🎯 The auto-update system is working correctly and CDN-proof!")
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("\n⚠️  Review failures above and fix issues")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
