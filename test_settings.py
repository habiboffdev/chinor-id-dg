#!/usr/bin/env python3
"""
Test the settings page functionality
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_settings_functionality():
    """Test settings page related functionality"""
    
    print("=== Testing Settings Page Functionality ===")
    
    # First, let's try to authenticate
    login_data = {
        "email": "test@example.com",
        "password": "password123"
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
        
        # Test profile retrieval (for account info)
        print("\n2. Testing profile retrieval...")
        profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"✓ Profile retrieved successfully")
            print(f"   Username: {profile_data.get('username', 'N/A')}")
            print(f"   Email: {profile_data.get('email', 'N/A')}")
            print(f"   User Type: {profile_data.get('user_type', 'N/A')}")
        else:
            print(f"✗ Profile retrieval failed: {profile_response.status_code} - {profile_response.text}")
            return False
        
        # Test account information update
        print("\n3. Testing account information update...")
        update_data = {
            "username": profile_data.get('username', 'test_user'),
            "first_name": "Updated Test",
            "last_name": "User"
        }
        
        update_response = requests.put(f"{BASE_URL}/auth/profile/", json=update_data, headers=headers)
        
        if update_response.status_code == 200:
            print(f"✓ Account information updated successfully")
            updated_profile = update_response.json()
            print(f"   Updated name: {updated_profile.get('first_name')} {updated_profile.get('last_name')}")
        else:
            print(f"✗ Account update failed: {update_response.status_code} - {update_response.text}")
        
        # Test password change (with wrong old password - should fail)
        print("\n4. Testing password change validation...")
        password_data = {
            "old_password": "wrongpassword",
            "new_password": "newtestpass123",
            "new_password_confirm": "newtestpass123"
        }
        
        password_response = requests.put(f"{BASE_URL}/auth/change-password/", json=password_data, headers=headers)
        
        if password_response.status_code == 400:
            error_data = password_response.json()
            if 'old_password' in error_data:
                print(f"✓ Password change validation working (wrong old password detected)")
            else:
                print(f"✗ Unexpected validation error: {error_data}")
        else:
            print(f"✗ Password change validation failed: {password_response.status_code} - {password_response.text}")
        
        print("\n=== Settings Functionality Test Complete ===")
        return True
        
    else:
        print(f"✗ Login failed: {login_response.status_code} - {login_response.text}")
        return False

if __name__ == "__main__":
    print("Testing Settings Page Functionality")
    print("=" * 50)
    
    success = test_settings_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Settings functionality tests completed!")
        print("🌐 You can now test the settings page at: http://localhost:8080/settings.html")
        print("\nTest the following features:")
        print("- Account information update (username, first name, last name)")
        print("- Email address change (with proper validation)")
        print("- Password change (with current password validation)")
        print("- Email preferences toggles")
    else:
        print("❌ Settings functionality tests failed!")
        print("Please check that:")
        print("1. Django server is running (python manage.py runserver)")
        print("2. Test user exists (run create_sample_data.py)")
        print("3. Database is properly migrated")
