"""
Helper functions for Google Cloud environment detection.
These functions automatically detect Cloud Run environment settings.
"""

import os
import requests
from typing import Optional


def get_project_id() -> Optional[str]:
    """
    Get the Google Cloud Project ID from the environment.
    
    Tries multiple methods in order:
    1. Environment variable GOOGLE_CLOUD_PROJECT
    2. Metadata server (for Cloud Run/Compute Engine)
    3. gcloud config (if available)
    
    Returns:
        Optional[str]: The project ID if found, None otherwise
    """
    # Method 1: Check environment variable
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id
    
    # Method 2: Check Cloud Run environment variable
    project_id = os.getenv("GCP_PROJECT")
    if project_id:
        return project_id
    
    # Method 3: Query metadata server (works in Cloud Run, Compute Engine, etc.)
    try:
        url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except (requests.RequestException, requests.Timeout):
        pass
    
    # Method 4: Try gcloud config (if gcloud is available)
    try:
        import subprocess
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return None


def get_region() -> Optional[str]:
    """
    Get the Google Cloud region from the environment.
    
    Returns:
        Optional[str]: The region if found, None otherwise
    """
    # Check Cloud Run environment variable
    region = os.getenv("GOOGLE_CLOUD_REGION")
    if region:
        return region
    
    # Check other common environment variables
    region = os.getenv("CLOUD_RUN_REGION")
    if region:
        return region
    
    # Query metadata server
    try:
        url = "http://metadata.google.internal/computeMetadata/v1/instance/region"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            # Extract region from full path like "projects/123/regions/us-central1"
            region_path = response.text.strip()
            return region_path.split("/")[-1]
    except (requests.RequestException, requests.Timeout):
        pass
    
    return None


def is_cloud_run() -> bool:
    """
    Check if the application is running in Cloud Run.
    
    Returns:
        bool: True if running in Cloud Run, False otherwise
    """
    # Check for Cloud Run specific environment variables
    return (
        os.getenv("K_SERVICE") is not None or
        os.getenv("K_REVISION") is not None or
        os.getenv("K_CONFIGURATION") is not None
    )


def get_service_name() -> Optional[str]:
    """
    Get the Cloud Run service name.
    
    Returns:
        Optional[str]: The service name if running in Cloud Run, None otherwise
    """
    return os.getenv("K_SERVICE")


def print_environment_info():
    """
    Print information about the current Google Cloud environment.
    Useful for debugging and verification.
    """
    print("🔍 Google Cloud Environment Information")
    print("=" * 40)
    print(f"Project ID: {get_project_id()}")
    print(f"Region: {get_region()}")
    print(f"Service Name: {get_service_name()}")
    print(f"Is Cloud Run: {is_cloud_run()}")
    print(f"K_SERVICE: {os.getenv('K_SERVICE')}")
    print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print("=" * 40)
