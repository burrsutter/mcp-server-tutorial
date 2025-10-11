"""
Test script for FastAPI wrapper
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get API port from environment or use default
API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://localhost:{API_PORT}"


def test_add_endpoint():
    """Test the /add endpoint"""
    url = f"{BASE_URL}/add"

    # Test data
    data = {
        "a": 2.0,
        "b": 3.0
    }

    print(f"Testing POST {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        result = response.json()
        print(f"\nResponse (Status {response.status_code}):")
        print(json.dumps(result, indent=2))

        print(f"\n✓ Result: {result['result']} (type: {type(result['result']).__name__})")

    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the API server")
        print(f"  Make sure the FastAPI server is running on {BASE_URL}")
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_health_endpoint():
    """Test the /health endpoint"""
    url = f"{BASE_URL}/health"

    print(f"\nTesting GET {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()

        result = response.json()
        print(f"Response (Status {response.status_code}):")
        print(json.dumps(result, indent=2))

    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the API server")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing FastAPI LangGraph Agent Wrapper")
    print("=" * 60)

    # First check if server is healthy
    test_health_endpoint()

    print("\n" + "=" * 60)

    # Test the add endpoint
    test_add_endpoint()

    print("\n" + "=" * 60)
