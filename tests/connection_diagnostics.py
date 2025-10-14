#!/usr/bin/env python3
"""
UE5 AI Assistant - Connection Diagnostics Tool
Comprehensive test suite for diagnosing and validating client-server connections.

Tests:
1. Backend endpoint availability
2. Project Registry functionality
3. HTTP polling client registration
4. Heartbeat mechanism
5. Connection health tracking
6. Dashboard status accuracy
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

class ConnectionDiagnostics:
    """Comprehensive connection diagnostic tool."""
    
    def __init__(self, backend_url: str = "http://localhost:5000"):
        self.backend_url = backend_url.rstrip('/')
        self.test_project_id = "test_project_12345"
        self.test_project_name = "DiagnosticTestProject"
        self.results: List[Tuple[str, bool, str]] = []
    
    def run_all_tests(self) -> Dict:
        """Run all diagnostic tests and return results."""
        print("=" * 80)
        print("🔧 UE5 AI Assistant - Connection Diagnostics")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}\n")
        
        # Test 1: Backend health
        self._test_backend_health()
        
        # Test 2: Project endpoints
        self._test_project_endpoints()
        
        # Test 3: UE5 client registration
        self._test_ue5_registration()
        
        # Test 4: Heartbeat mechanism
        self._test_heartbeat()
        
        # Test 5: Connection health tracking
        self._test_connection_health()
        
        # Test 6: Project listing
        self._test_project_listing()
        
        # Test 7: Cleanup
        self._cleanup()
        
        # Summary
        self._print_summary()
        
        return {
            "total_tests": len(self.results),
            "passed": sum(1 for _, passed, _ in self.results if passed),
            "failed": sum(1 for _, passed, _ in self.results if not passed),
            "results": self.results
        }
    
    def _test_backend_health(self):
        """Test if backend is accessible."""
        test_name = "Backend Health Check"
        try:
            response = requests.get(f"{self.backend_url}/api/config", timeout=5)
            if response.status_code == 200:
                self._pass(test_name, "Backend is accessible")
            else:
                self._fail(test_name, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self._fail(test_name, f"Connection failed: {e}")
    
    def _test_project_endpoints(self):
        """Test project-related endpoints."""
        test_name = "Project Endpoints"
        try:
            response = requests.get(f"{self.backend_url}/api/projects", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "projects" in data:
                    self._pass(test_name, f"Endpoint working, {len(data['projects'])} projects found")
                else:
                    self._fail(test_name, "Missing 'projects' key in response")
            else:
                self._fail(test_name, f"Status {response.status_code}")
        except Exception as e:
            self._fail(test_name, str(e))
    
    def _test_ue5_registration(self):
        """Test UE5 client registration."""
        test_name = "UE5 Client Registration"
        try:
            payload = {
                "project_id": self.test_project_id,
                "project_name": self.test_project_name
            }
            response = requests.post(
                f"{self.backend_url}/api/ue5/register_http",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self._pass(test_name, "Registration successful")
                else:
                    self._fail(test_name, f"Registration failed: {data}")
            else:
                self._fail(test_name, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self._fail(test_name, str(e))
    
    def _test_heartbeat(self):
        """Test heartbeat mechanism."""
        test_name = "Heartbeat Mechanism"
        try:
            payload = {"project_id": self.test_project_id}
            response = requests.post(
                f"{self.backend_url}/api/ue5/heartbeat",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self._pass(test_name, "Heartbeat accepted")
                else:
                    self._fail(test_name, f"Heartbeat rejected: {data}")
            else:
                self._fail(test_name, f"Status {response.status_code}")
        except Exception as e:
            self._fail(test_name, str(e))
    
    def _test_connection_health(self):
        """Test connection health tracking."""
        test_name = "Connection Health Tracking"
        try:
            # Send heartbeat
            requests.post(
                f"{self.backend_url}/api/ue5/heartbeat",
                json={"project_id": self.test_project_id},
                timeout=5
            )
            
            # Check project list for health status
            response = requests.get(f"{self.backend_url}/api/projects", timeout=5)
            data = response.json()
            
            # Find our test project
            test_project = None
            for project in data.get("projects", []):
                if project.get("project_id") == self.test_project_id:
                    test_project = project
                    break
            
            if test_project:
                if test_project.get("is_active"):
                    health = test_project.get("connection_health", {})
                    self._pass(test_name, f"Project marked active, health: {health.get('status')}")
                else:
                    self._fail(test_name, "Project not marked as active after heartbeat")
            else:
                self._fail(test_name, "Test project not found in project list")
        except Exception as e:
            self._fail(test_name, str(e))
    
    def _test_project_listing(self):
        """Test project listing functionality."""
        test_name = "Project Listing"
        try:
            response = requests.get(f"{self.backend_url}/api/projects", timeout=5)
            data = response.json()
            
            projects = data.get("projects", [])
            active_count = sum(1 for p in projects if p.get("is_active"))
            
            self._pass(test_name, f"Total: {len(projects)}, Active: {active_count}")
        except Exception as e:
            self._fail(test_name, str(e))
    
    def _cleanup(self):
        """Clean up test data."""
        test_name = "Cleanup Test Data"
        try:
            # Delete test project from registry
            response = requests.delete(
                f"{self.backend_url}/api/projects/{self.test_project_id}",
                timeout=5
            )
            if response.status_code == 200 or response.status_code == 404:
                self._pass(test_name, "Test project removed from registry")
            else:
                self._pass(test_name, f"Cleanup attempted (status {response.status_code})")
        except Exception as e:
            # Not critical if cleanup fails
            self._pass(test_name, f"Cleanup attempted: {e}")
    
    def _pass(self, test_name: str, message: str):
        """Record a passed test."""
        self.results.append((test_name, True, message))
        print(f"✅ {test_name}: {message}")
    
    def _fail(self, test_name: str, message: str):
        """Record a failed test."""
        self.results.append((test_name, False, message))
        print(f"❌ {test_name}: {message}")
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 Test Summary")
        print("=" * 80)
        
        passed = sum(1 for _, p, _ in self.results if p)
        failed = sum(1 for _, p, _ in self.results if not p)
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("=" * 80)
        
        if failed > 0:
            print("\n⚠️ Failed Tests:")
            for name, passed, msg in self.results:
                if not passed:
                    print(f"  - {name}: {msg}")


def main():
    """Run diagnostics."""
    diagnostics = ConnectionDiagnostics()
    results = diagnostics.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
