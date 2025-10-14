#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for UE5 AI Assistant
Runs all tests without requiring Unreal Engine access.
"""
import subprocess
import sys
from pathlib import Path


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str):
    """Print formatted section."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


def run_test_suite(name: str, test_path: str) -> bool:
    """Run a test suite and return success status."""
    print_section(f"Running: {name}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short", "--color=yes"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {name} - PASSED")
            return True
        else:
            print(f"❌ {name} - FAILED")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {name} - TIMEOUT (exceeded 120s)")
        return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print_section("Checking Dependencies")
    
    required = ["pytest", "fastapi", "uvicorn"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """Run all test suites."""
    print_header("UE5 AI Assistant - Comprehensive Test Suite")
    print("Testing the entire system WITHOUT requiring Unreal Engine")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependencies not met. Please install required packages.")
        return 1
    
    # Define test suites (comprehensive coverage)
    test_suites = [
        # UI Tests
        ("Dashboard UI Elements", "tests/ui/test_dashboard_elements.py"),
        
        # Backend Tests
        ("Backend API Tests", "tests/backend/test_api_endpoints.py"),
        ("Backend Routes Comprehensive", "tests/backend/test_routes_comprehensive.py"),
        ("HTTP Polling Flow Tests", "tests/integration/test_http_polling_flow.py"),
        ("Auto-Update System", "tests/backend/test_auto_update.py"),
        
        # UE5 Client Tests
        ("Action Execution Tests", "tests/ue5_client/test_action_execution.py"),
        ("Client Modules Tests", "tests/ue5_client/test_client_modules.py"),
        
        # Integration Tests
        ("Dashboard Integration Tests", "tests/integration/test_dashboard_actions.py"),
        ("End-to-End Workflows", "tests/integration/test_end_to_end_workflows.py"),
    ]
    
    # Run all test suites
    results = {}
    for name, path in test_suites:
        if Path(path).exists():
            results[name] = run_test_suite(name, path)
        else:
            print(f"⚠️  Test file not found: {path}")
            results[name] = False
    
    # Print summary
    print_header("Test Results Summary")
    
    total = len(results)
    passed = sum(1 for success in results.values() if success)
    failed = total - passed
    
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} - {name}")
    
    print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")
    
    # Success criteria
    print("\n" + "=" * 80)
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ System Verification Complete:")
        print("  • All API endpoints work correctly")
        print("  • HTTP polling flow works end-to-end")
        print("  • Actions execute without threading errors")
        print("  • Dashboard commands return real data")
        print("  • Auto-update mechanism works properly")
        print("  • Error handling recovers gracefully")
        print("\n🚀 The UE5 AI Assistant is ready for deployment!")
        return_code = 0
    else:
        print("❌ SOME TESTS FAILED")
        print(f"\n⚠️  {failed} test suite(s) need attention.")
        print("Review the output above to identify and fix issues.")
        return_code = 1
    
    print("=" * 80 + "\n")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())
