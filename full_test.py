#!/usr/bin/env python3
"""
Test profile update with user fields
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test credentials
login_data = {
    "email": "test@example.com",
    "password": "testpass123"
}

print("1. Login...")
login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    tokens = login_response.json()
    access_token = tokens.get('access')
    print("✓ Login successful")
    
    # Headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test profile update with user + profile fields
    profile_data = {
        "first_name": "TestUpdated",
        "last_name": "UserUpdated",
        "email": "test@example.com",
        "phone": "+9876543210",
        "bio": "Updated bio with user fields",
        "location": "San Francisco, CA",
        "university": "Updated University",
        "major": "Updated Major",
        "graduation_year": 2025
    }
    
    print(f"2. Profile update with data: {profile_data}")
    update_response = requests.put(f"{BASE_URL}/students/profile/", 
                                  json=profile_data, headers=headers)
    
    print(f"Update status: {update_response.status_code}")
    print(f"Update response: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✓ Profile update successful")
        
        # Fetch updated profile to verify user fields
        print("3. Fetching profile...")
        profile_response = requests.get(f"{BASE_URL}/students/profile/", headers=headers)
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print("✓ Profile fetched successfully")
            print(f"   First name: {profile.get('first_name')}")
            print(f"   Last name: {profile.get('last_name')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   Phone: {profile.get('phone')}")
            print(f"   Bio: {profile.get('bio')}")
            print(f"   Location: {profile.get('location')}")
            print(f"   University: {profile.get('university')}")
            print(f"   Major: {profile.get('major')}")
            print(f"   Graduation Year: {profile.get('graduation_year')}")
        else:
            print(f"✗ Failed to fetch profile: {profile_response.status_code}")
            
    else:
        print("✗ Profile update failed")
        
else:
    print("✗ Login failed")
