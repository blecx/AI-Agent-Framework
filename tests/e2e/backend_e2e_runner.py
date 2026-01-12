#!/usr/bin/env python3
"""
Backend E2E Test Harness Runner

This script provides a standardized way to run the backend API in E2E test mode,
suitable for cross-repo testing with the client repository.

Usage:
    # Run backend in E2E mode (foreground)
    python tests/e2e/backend_e2e_runner.py --mode server

    # Run health check against running backend
    python tests/e2e/backend_e2e_runner.py --mode health-check --url http://localhost:8000

    # Run full E2E validation suite
    python tests/e2e/backend_e2e_runner.py --mode validate --url http://localhost:8000
"""

import argparse
import sys
import os
import subprocess
import time
from pathlib import Path
import httpx


def start_backend_server(port=8000, docs_path=None):
    """
    Start the backend API server for E2E testing.
    
    Args:
        port: Port to run the server on
        docs_path: Path for project documents (uses temp dir if not specified)
    """
    # Set up environment
    if docs_path is None:
        import tempfile
        docs_path = tempfile.mkdtemp(prefix="e2e-projectDocs-")
        print(f"Using temporary docs path: {docs_path}")
    
    os.environ["PROJECT_DOCS_PATH"] = docs_path
    
    # Locate the API directory
    api_dir = Path(__file__).resolve().parent.parent.parent / "apps" / "api"
    
    if not api_dir.exists():
        print(f"Error: API directory not found at {api_dir}")
        sys.exit(1)
    
    print(f"Starting backend API on port {port}...")
    print(f"Project docs path: {docs_path}")
    print(f"API directory: {api_dir}")
    
    # Start uvicorn
    try:
        subprocess.run(
            [
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ],
            cwd=str(api_dir),
            check=True,
            env={**os.environ, "PROJECT_DOCS_PATH": docs_path}
        )
    except KeyboardInterrupt:
        print("\nShutting down backend server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def check_health(base_url):
    """
    Check if the backend is healthy and responsive.
    
    Args:
        base_url: Base URL of the backend (e.g., http://localhost:8000)
    
    Returns:
        bool: True if healthy, False otherwise
    """
    print(f"Checking backend health at {base_url}...")
    
    try:
        response = httpx.get(f"{base_url}/health", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Backend is healthy")
        print(f"  Status: {data.get('status')}")
        print(f"  Docs path: {data.get('docs_path')}")
        print(f"  Docs exists: {data.get('docs_exists')}")
        print(f"  Git initialized: {data.get('docs_is_git')}")
        
        return data.get("status") == "healthy"
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def validate_backend(base_url):
    """
    Run validation checks against the backend API.
    
    Args:
        base_url: Base URL of the backend
    
    Returns:
        bool: True if all validations pass, False otherwise
    """
    print(f"\nRunning E2E validation suite against {base_url}...\n")
    
    client = httpx.Client(base_url=base_url, timeout=10.0)
    all_passed = True
    
    # Test 1: Health check
    print("1. Health Check")
    try:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json().get("status") == "healthy"
        print("   ✓ Health check passed")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        all_passed = False
    
    # Test 2: Create project
    print("2. Create Project")
    test_project_key = f"E2ETEST{int(time.time())}"
    try:
        response = client.post(
            "/projects",
            json={"key": test_project_key, "name": "E2E Test Project"}
        )
        assert response.status_code == 201
        project_data = response.json()
        assert project_data["key"] == test_project_key
        print(f"   ✓ Project created: {test_project_key}")
    except Exception as e:
        print(f"   ✗ Project creation failed: {e}")
        all_passed = False
        return all_passed
    
    # Test 3: List projects
    print("3. List Projects")
    try:
        response = client.get("/projects")
        assert response.status_code == 200
        projects = response.json()
        assert any(p["key"] == test_project_key for p in projects)
        print(f"   ✓ Project found in list")
    except Exception as e:
        print(f"   ✗ List projects failed: {e}")
        all_passed = False
    
    # Test 4: Get project state
    print("4. Get Project State")
    try:
        response = client.get(f"/projects/{test_project_key}/state")
        assert response.status_code == 200
        state = response.json()
        assert "project_info" in state
        assert "artifacts" in state
        print(f"   ✓ Project state retrieved")
    except Exception as e:
        print(f"   ✗ Get project state failed: {e}")
        all_passed = False
    
    # Test 5: List artifacts (should be empty)
    print("5. List Artifacts")
    try:
        response = client.get(f"/projects/{test_project_key}/artifacts")
        assert response.status_code == 200
        artifacts = response.json()
        print(f"   ✓ Artifacts listed (count: {len(artifacts)})")
    except Exception as e:
        print(f"   ✗ List artifacts failed: {e}")
        all_passed = False
    
    # Test 6: Propose command (assess_gaps)
    print("6. Propose Command (assess_gaps)")
    try:
        response = client.post(
            f"/projects/{test_project_key}/commands/propose",
            json={"command": "assess_gaps", "params": {}}
        )
        # Accept both success and LLM unavailable errors
        if response.status_code == 200:
            proposal = response.json()
            print(f"   ✓ Command proposed (proposal_id: {proposal['proposal_id'][:8]}...)")
        elif response.status_code == 500 and "LLM" in response.text:
            print(f"   ⚠ Command propose returned 500 (LLM unavailable, acceptable)")
        else:
            raise Exception(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Propose command failed: {e}")
        all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All validation tests passed!")
    else:
        print("✗ Some validation tests failed")
    print(f"{'='*50}\n")
    
    client.close()
    return all_passed


def wait_for_backend(base_url, timeout=30, interval=1):
    """
    Wait for backend to become available.
    
    Args:
        base_url: Base URL of the backend
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
    
    Returns:
        bool: True if backend becomes available, False if timeout
    """
    print(f"Waiting for backend at {base_url} (timeout: {timeout}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(f"{base_url}/health", timeout=2.0)
            if response.status_code == 200:
                print(f"✓ Backend is ready!")
                return True
        except Exception:
            pass
        
        time.sleep(interval)
    
    print(f"✗ Timeout waiting for backend")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Backend E2E Test Harness Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start backend server
  python tests/e2e/backend_e2e_runner.py --mode server

  # Check if backend is healthy
  python tests/e2e/backend_e2e_runner.py --mode health-check --url http://localhost:8000

  # Run full validation suite
  python tests/e2e/backend_e2e_runner.py --mode validate --url http://localhost:8000

  # Wait for backend then validate
  python tests/e2e/backend_e2e_runner.py --mode wait-and-validate --url http://localhost:8000
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["server", "health-check", "validate", "wait-and-validate"],
        required=True,
        help="Operation mode"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend URL (for health-check, validate modes)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (for server mode)"
    )
    parser.add_argument(
        "--docs-path",
        help="Path for project documents (temp dir if not specified)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout for wait operations in seconds"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server":
        start_backend_server(port=args.port, docs_path=args.docs_path)
    
    elif args.mode == "health-check":
        healthy = check_health(args.url)
        sys.exit(0 if healthy else 1)
    
    elif args.mode == "validate":
        passed = validate_backend(args.url)
        sys.exit(0 if passed else 1)
    
    elif args.mode == "wait-and-validate":
        if wait_for_backend(args.url, timeout=args.timeout):
            passed = validate_backend(args.url)
            sys.exit(0 if passed else 1)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
