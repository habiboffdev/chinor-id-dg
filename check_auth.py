#!/usr/bin/env python3
"""
Script to check authentication status and debug profile loading
"""

import requests
import json

# Test login and profile retrieval
def test_auth():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing authentication...")
    
    # First, let's try to create a test user
    print("\n1. Testing user registration...")
    register_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register/", json=register_data)
        print(f"   Registration: {response.status_code}")
        if response.status_code != 201:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Registration failed: {e}")
    
    # Try to login
    print("\n2. Testing login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"   Login: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            print(f"   ✅ Login successful!")
            print(f"   User type: {login_result.get('user_type')}")
            
            # Get the token
            token = login_result.get('access_token')
            if token:
                print(f"   Token received: {token[:20]}...")
                
                # Test profile retrieval
                print("\n3. Testing profile retrieval...")
                headers = {"Authorization": f"Bearer {token}"}
                
                try:
                    profile_response = requests.get(f"{base_url}/api/students/profile/", headers=headers)
                    print(f"   Profile API: {profile_response.status_code}")
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        print(f"   ✅ Profile loaded successfully!")
                        print(f"   Profile data: {json.dumps(profile_data, indent=2)}")
                    else:
                        print(f"   ❌ Profile loading failed: {profile_response.text}")
                        
                except Exception as e:
                    print(f"   Profile request failed: {e}")
            else:
                print("   ❌ No token received")
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   Login request failed: {e}")

if __name__ == "__main__":
    test_auth()
