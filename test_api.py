#!/usr/bin/env python3
"""
Simple API test script for Opportuni platform
Run this after starting the Django server to test the endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "user_type": "student"
}

def test_endpoint(method, endpoint, data=None, headers=None, token=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    # Default headers
    default_headers = {"Content-Type": "application/json"}
    if token:
        default_headers["Authorization"] = f"Bearer {token}"
    
    if headers:
        default_headers.update(headers)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=default_headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=default_headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=default_headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"📡 {method.upper()} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Success")
            try:
                return response.json()
            except:
                return response.text
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed to {url}")
        print("   Make sure the Django server is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {str(e)}")
        return None

def main():
    print("🚀 Testing Opportuni API Endpoints")
    print("=" * 50)
    
    # Test 1: Health check - list opportunities (should work without auth)
    print("\n1. Testing basic endpoint connectivity...")
    opportunities = test_endpoint("GET", "/opportunities/")
    
    if opportunities is None:
        print("❌ Server is not responding. Please check if Django server is running.")
        sys.exit(1)
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    register_response = test_endpoint("POST", "/auth/register/", TEST_USER)
    
    # Test 3: User login
    print("\n3. Testing user login...")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    login_response = test_endpoint("POST", "/auth/login/", login_data)
    
    token = None
    if login_response and "access" in login_response:
        token = login_response["access"]
        print(f"   🔑 Token received: {token[:20]}...")
    
    if not token:
        print("❌ Could not get authentication token. Some tests will be skipped.")
        return
    
    # Test 4: Get user profile (requires auth)
    print("\n4. Testing authenticated endpoint...")
    profile = test_endpoint("GET", "/auth/profile/", token=token)
    
    # Test 5: Test student profile endpoint
    print("\n5. Testing student profile endpoint...")
    student_profile = test_endpoint("GET", "/students/profile/", token=token)
    
    # Test 6: Test organizations endpoint
    print("\n6. Testing organizations endpoint...")
    organizations = test_endpoint("GET", "/organizations/", token=token)
    
    # Test 7: Test applications endpoint
    print("\n7. Testing applications endpoint...")
    applications = test_endpoint("GET", "/applications/", token=token)
    
    # Test 8: Test notifications endpoint
    print("\n8. Testing notifications endpoint...")
    notifications = test_endpoint("GET", "/notifications/", token=token)
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")
    print("\nIf you see connection errors, make sure to:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Check that the server is running on localhost:8000")
    print("3. Ensure all migrations are applied: python manage.py migrate")

if __name__ == "__main__":
    main()
