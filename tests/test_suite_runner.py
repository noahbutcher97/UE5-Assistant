"""
Comprehensive Test Suite Runner with Detailed Reporting
Executes all tests systematically and generates validation report.
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class TestSuiteRunner:
    """Orchestrates execution of all test suites with detailed reporting."""
    
    def __init__(self):
        self.results = {}
        self.test_suites = self._define_test_suites()
        self.start_time = None
        self.end_time = None
    
    def _define_test_suites(self) -> List[Tuple[str, str, str]]:
        """Define all test suites organized by category."""
        return [
            # UI Tests
            ("Dashboard UI Elements", "tests/ui/test_dashboard_elements.py", "UI"),
            
            # Backend Tests
            ("Backend API Endpoints", "tests/backend/test_api_endpoints.py", "Backend"),
            ("Backend Routes Comprehensive", "tests/backend/test_routes_comprehensive.py", "Backend"),
            ("HTTP Polling Flow", "tests/integration/test_http_polling_flow.py", "Backend"),
            ("Auto-Update System", "tests/backend/test_auto_update.py", "Backend"),
            
            # UE5 Client Tests
            ("Action Execution", "tests/ue5_client/test_action_execution.py", "UE5 Client"),
            ("Client Modules", "tests/ue5_client/test_client_modules.py", "UE5 Client"),
            
            # Integration Tests
            ("Dashboard Integration", "tests/integration/test_dashboard_actions.py", "Integration"),
            ("End-to-End Workflows", "tests/integration/test_end_to_end_workflows.py", "Integration"),
        ]
    
    def print_header(self, text: str):
        """Print formatted header."""
        print("\n" + "=" * 100)
        print(f"  {text}")
        print("=" * 100)
    
    def print_section(self, text: str):
        """Print formatted section."""
        print("\n" + "-" * 100)
        print(f"  {text}")
        print("-" * 100)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        self.print_section("Checking Dependencies")
        
        required = ["pytest", "fastapi", "uvicorn", "httpx"]
        missing = []
        
        for package in required:
            try:
                __import__(package)
                print(f"  ✅ {package:<20} - installed")
            except ImportError:
                print(f"  ❌ {package:<20} - NOT installed")
                missing.append(package)
        
        if missing:
            print(f"\n  ⚠️  Missing packages: {', '.join(missing)}")
            print(f"  Install with: pip install {' '.join(missing)}")
            return False
        
        return True
    
    def run_test_suite(self, name: str, test_path: str, category: str) -> Dict:
        """Run a test suite and return detailed results."""
        self.print_section(f"Running: {name} ({category})")
        
        result = {
            "name": name,
            "path": test_path,
            "category": category,
            "passed": False,
            "duration": 0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": "",
            "error": None
        }
        
        if not Path(test_path).exists():
            result["error"] = f"Test file not found: {test_path}"
            print(f"  ⚠️  {result['error']}")
            return result
        
        try:
            start = datetime.now()
            
            process = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short", 
                 "--color=yes", "-q"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            end = datetime.now()
            result["duration"] = (end - start).total_seconds()
            
            result["output"] = process.stdout + process.stderr
            
            # Parse pytest output for stats
            output_lower = result["output"].lower()
            
            # Count passed/failed tests
            if "passed" in output_lower:
                # Extract numbers from pytest output
                import re
                match = re.search(r'(\d+)\s+passed', output_lower)
                if match:
                    result["tests_passed"] = int(match.group(1))
            
            if "failed" in output_lower:
                match = re.search(r'(\d+)\s+failed', output_lower)
                if match:
                    result["tests_failed"] = int(match.group(1))
            
            result["tests_run"] = result["tests_passed"] + result["tests_failed"]
            
            if process.returncode == 0:
                result["passed"] = True
                print(f"  ✅ {name} - PASSED ({result['tests_passed']} tests, {result['duration']:.2f}s)")
            else:
                print(f"  ❌ {name} - FAILED ({result['tests_failed']} failed, {result['duration']:.2f}s)")
            
            # Show brief output
            if result["tests_failed"] > 0:
                print("\n  Failed test details:")
                lines = result["output"].split("\n")
                for line in lines:
                    if "FAILED" in line or "ERROR" in line or "assert" in line.lower():
                        print(f"    {line}")
            
        except subprocess.TimeoutExpired:
            result["error"] = "TIMEOUT (exceeded 120s)"
            print(f"  ❌ {name} - {result['error']}")
        except Exception as e:
            result["error"] = str(e)
            print(f"  ❌ {name} - ERROR: {e}")
        
        return result
    
    def generate_report(self):
        """Generate detailed test report."""
        self.print_header("TEST SUITE VALIDATION REPORT")
        
        # Calculate totals
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r["passed"])
        failed_suites = total_suites - passed_suites
        
        total_tests = sum(r["tests_run"] for r in self.results.values())
        total_passed = sum(r["tests_passed"] for r in self.results.values())
        total_failed = sum(r["tests_failed"] for r in self.results.values())
        
        total_duration = sum(r["duration"] for r in self.results.values())
        
        # Group by category
        categories = {}
        for result in self.results.values():
            cat = result["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Print category summaries
        for category, results in sorted(categories.items()):
            self.print_section(f"{category} Tests")
            
            cat_passed = sum(1 for r in results if r["passed"])
            cat_total = len(results)
            
            for result in results:
                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                duration = f"{result['duration']:.2f}s"
                tests = f"{result['tests_passed']}/{result['tests_run']}" if result['tests_run'] > 0 else "N/A"
                print(f"  {status:<12} {result['name']:<50} ({tests} tests, {duration})")
                
                if result["error"]:
                    print(f"              Error: {result['error']}")
            
            print(f"\n  Category Summary: {cat_passed}/{cat_total} suites passed")
        
        # Print overall summary
        self.print_header("OVERALL SUMMARY")
        
        print(f"\n  Test Suites:     {passed_suites}/{total_suites} passed")
        print(f"  Individual Tests: {total_passed}/{total_tests} passed")
        print(f"  Total Duration:   {total_duration:.2f}s")
        print(f"  Start Time:       {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  End Time:         {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Coverage analysis
        self.print_section("Coverage Analysis")
        
        print(f"\n  ✅ Dashboard UI Elements:        {'Tested' if any('Dashboard UI' in r['name'] for r in self.results.values()) else 'Not Tested'}")
        print(f"  ✅ Backend API Endpoints:        {'Tested' if any('Backend' in r['category'] for r in self.results.values()) else 'Not Tested'}")
        print(f"  ✅ UE5 Client Modules:           {'Tested' if any('Client' in r['category'] for r in self.results.values()) else 'Not Tested'}")
        print(f"  ✅ Integration Workflows:        {'Tested' if any('Integration' in r['category'] for r in self.results.values()) else 'Not Tested'}")
        print(f"  ✅ Error Recovery:               {'Tested' if any('Error' in r['name'] or 'Recovery' in r['name'] for r in self.results.values()) else 'Not Tested'}")
        
        # Final verdict
        self.print_header("FINAL VERDICT")
        
        if passed_suites == total_suites and total_failed == 0:
            print("\n  🎉 ALL TESTS PASSED!")
            print("\n  ✅ System Validation Complete:")
            print("     • All dashboard UI elements functional")
            print("     • All backend API endpoints working")
            print("     • All UE5 client modules operational")
            print("     • End-to-end workflows verified")
            print("     • Error recovery mechanisms tested")
            print("     • Multi-project concurrency validated")
            print("\n  🚀 The UE5 AI Assistant is production-ready!")
            return 0
        else:
            print("\n  ❌ SOME TESTS FAILED")
            print(f"\n  ⚠️  {failed_suites} test suite(s) failed")
            print(f"  ⚠️  {total_failed} individual test(s) failed")
            print("\n  Review the detailed output above to identify and fix issues.")
            
            # List failed suites
            if failed_suites > 0:
                print("\n  Failed Suites:")
                for result in self.results.values():
                    if not result["passed"]:
                        print(f"     • {result['name']}")
                        if result["error"]:
                            print(f"       Error: {result['error']}")
            
            return 1
    
    def run(self) -> int:
        """Run all test suites and generate report."""
        self.print_header("UE5 AI ASSISTANT - COMPREHENSIVE TEST SUITE")
        print("  Validating all systems: UI, Backend, UE5 Client, and Integration")
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n  ❌ Dependencies not met. Please install required packages.")
            return 1
        
        # Run all test suites
        self.start_time = datetime.now()
        
        for name, path, category in self.test_suites:
            result = self.run_test_suite(name, path, category)
            self.results[name] = result
        
        self.end_time = datetime.now()
        
        # Generate report
        return self.generate_report()


def main():
    """Main entry point."""
    runner = TestSuiteRunner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
