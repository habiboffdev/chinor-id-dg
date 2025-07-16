#!/usr/bin/env python
"""
Test the actual API endpoint that the frontend calls
"""

import requests
import json

def test_dashboard_api():
    """Test the dashboard API endpoint directly"""
    
    # API endpoint
    url = "http://localhost:8000/api/students/dashboard/"
    
    # You'll need to get a valid token first
    # For now, let's test if the endpoint is accessible
    
    try:
        # Test without authentication first to see if endpoint exists
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Endpoint exists but requires authentication (expected)")
        elif response.status_code == 200:
            print("✓ Endpoint accessible")
            data = response.json()
            print("Response data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend server")
        print("Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard_api()
