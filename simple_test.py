#!/usr/bin/env python3
"""
Simple test to check profile update endpoint
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
    
    # Test profile update with minimal data
    profile_data = {
        "phone": "+1234567890",
        "bio": "Updated bio"
    }
    
    print(f"2. Profile update with data: {profile_data}")
    update_response = requests.put(f"{BASE_URL}/students/profile/", 
                                  json=profile_data, headers=headers)
    
    print(f"Update status: {update_response.status_code}")
    print(f"Update response: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✓ Profile update successful")
    else:
        print("✗ Profile update failed")
        
else:
    print("✗ Login failed")
