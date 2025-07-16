#!/usr/bin/env python3
"""
Test script to verify profile update functionality
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_profile_update():
    """Test profile update with user and profile fields"""
    
    print("=== Testing Profile Update ===")
    
    # First, let's try to authenticate (using test user we just created)
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    print("1. Attempting login...")
    login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        access_token = tokens.get('access')
        print(f"✓ Login successful")
        
        # Headers for authenticated requests
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test profile update
        profile_data = {
            "first_name": "Test",
            "last_name": "User Updated",
            "email": "test@example.com",
            "phone": "+1234567890",
            "bio": "Updated bio text",
            "location": "New York, NY",
            "university": "Test University",
            "major": "Computer Science",
            "graduation_year": 2024
        }
        
        print("2. Attempting profile update...")
        print(f"   Data: {json.dumps(profile_data, indent=2)}")
        
        update_response = requests.put(f"{BASE_URL}/students/profile/", 
                                      json=profile_data, headers=headers)
        
        print(f"   Response status: {update_response.status_code}")
        print(f"   Response: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✓ Profile update successful")
            
            # Get updated profile to verify
            print("3. Fetching updated profile...")
            profile_response = requests.get(f"{BASE_URL}/students/profile/", headers=headers)
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print("✓ Profile fetched successfully")
                print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
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
            print(f"✗ Profile update failed: {update_response.status_code}")
    else:
        print(f"✗ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

if __name__ == "__main__":
    test_profile_update()
