"""
Enhanced health check endpoint with detailed system checks.

Provides comprehensive health status including:
- Overall system status
- Git repository health
- LLM service availability
- Disk space
- Memory usage
"""

import os
import psutil
import httpx
from typing import Dict, Any
from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter()


def check_git_repository(docs_path: str) -> Dict[str, Any]:
    """Check Git repository health."""
    try:
        git_dir = os.path.join(docs_path, ".git")

        status = {
            "healthy": False,
            "docs_path": docs_path,
            "docs_exists": os.path.exists(docs_path),
            "is_git_repo": os.path.exists(git_dir),
            "writable": False,
            "message": "",
        }

        if not os.path.exists(docs_path):
            status["message"] = "Project docs path does not exist"
            return status

        if not os.path.exists(git_dir):
            status["message"] = "Not a Git repository"
            return status

        # Check if writable
        test_file = os.path.join(docs_path, ".health_check")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            status["writable"] = True
        except Exception as e:
            status["message"] = f"Directory not writable: {str(e)}"
            return status

        status["healthy"] = True
        status["message"] = "Git repository is healthy"
        return status

    except Exception as e:
        return {
            "healthy": False,
            "message": f"Error checking Git repository: {str(e)}",
        }


def check_llm_service(llm_service) -> Dict[str, Any]:
    """Check LLM service availability."""
    try:
        # LLM service is optional - system can work with templates
        # Just check if the service object exists and has config
        if llm_service is None:
            return {
                "healthy": True,
                "message": "LLM service not initialized (using templates fallback)",
            }

        # Try to access the config (which should always exist after __init__)
        if not hasattr(llm_service, "config"):
            return {
                "healthy": True,
                "message": "LLM service config not found (using templates fallback)",
            }

        config = llm_service.config
        base_url = config.get("base_url", "")

        status = {
            "healthy": True,  # Default to healthy since LLM is optional
            "endpoint_configured": bool(base_url),
            "message": "",
        }

        if base_url:
            # Try a quick connectivity check (timeout 2s)
            try:
                response = httpx.get(f"{base_url}/models", timeout=2.0)
                # LLM is optional - always healthy regardless of response
                if response.status_code == 200:
                    status["message"] = "LLM service is reachable"
                else:
                    status["message"] = (
                        f"LLM service returned status {response.status_code} (using templates fallback)"
                    )
            except httpx.TimeoutException:
                status["message"] = "LLM service timeout (using templates fallback)"
            except Exception as e:
                status["message"] = (
                    f"Cannot reach LLM service (using templates fallback): {str(e)}"
                )
        else:
            status["message"] = "LLM endpoint not configured (using templates)"

        return status

    except Exception as e:
        return {
            "healthy": True,  # Always healthy since LLM is optional
            "message": f"Error checking LLM service: {str(e)}",
        }


def check_disk_space(path: str, min_free_gb: float = 1.0) -> Dict[str, Any]:
    """Check disk space availability."""
    try:
        usage = psutil.disk_usage(path)
        free_gb = usage.free / (1024**3)

        status = {
            "healthy": free_gb >= min_free_gb,
            "path": path,
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(free_gb, 2),
            "percent_used": usage.percent,
            "message": "",
        }

        if status["healthy"]:
            status["message"] = f"{free_gb:.2f}GB free"
        else:
            status["message"] = f"Low disk space: only {free_gb:.2f}GB free"

        return status

    except Exception as e:
        return {
            "healthy": False,
            "message": f"Error checking disk space: {str(e)}",
        }


def check_memory(min_free_percent: float = 10.0) -> Dict[str, Any]:
    """Check memory availability."""
    try:
        memory = psutil.virtual_memory()
        free_percent = 100 - memory.percent

        status = {
            "healthy": free_percent >= min_free_percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "free_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent,
            "message": "",
        }

        if status["healthy"]:
            status["message"] = f"{free_percent:.1f}% free"
        else:
            status["message"] = f"Low memory: only {free_percent:.1f}% free"

        return status

    except Exception as e:
        return {
            "healthy": False,
            "message": f"Error checking memory: {str(e)}",
        }


@router.get("/health")
async def health_check_simple():
    """
    Simple health check (backward compatible).

    Always returns 200 OK if API is running, even if some components are degraded.
    This ensures infrastructure health checks pass while detailed status is available
    at /api/v1/health for monitoring.
    """
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    docs_exists = os.path.exists(docs_path)
    docs_is_git = (
        os.path.exists(os.path.join(docs_path, ".git")) if docs_exists else False
    )

    return {
        "status": "healthy",  # Always healthy if API responds
        "docs_path": docs_path,
        "docs_exists": docs_exists,
        "docs_is_git": docs_is_git,
        "message": (
            "API is running" if docs_is_git else "API running (docs not initialized)"
        ),
    }


@router.get("/api/v1/health")
async def health_check_detailed(request: Request):
    """
    Detailed health check with comprehensive system status.

    Returns:
    - overall status: healthy/degraded/unhealthy
    - component health: git, llm, disk, memory
    - timestamp
    """
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")

    # Run all health checks
    git_status = check_git_repository(docs_path)
    llm_status = check_llm_service(request.app.state.llm_service)
    disk_status = check_disk_space(docs_path)
    memory_status = check_memory()

    # Determine overall status
    critical_checks = [
        git_status["healthy"],
        disk_status["healthy"],
        memory_status["healthy"],
    ]
    non_critical_checks = [llm_status["healthy"]]

    if all(critical_checks):
        if all(non_critical_checks):
            overall_status = "healthy"
        else:
            overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "api_version": "v1",
        "checks": {
            "git_repository": git_status,
            "llm_service": llm_status,
            "disk_space": disk_status,
            "memory": memory_status,
        },
    }
