#!/usr/bin/env python
"""
Test profile picture upload functionality
"""

import os
import sys
import django
import requests
from pathlib import Path

# Add the Django project to the Python path
project_root = Path(__file__).parent / 'opportuni_backend'
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_profile_picture_endpoint():
    """Test if the profile picture upload endpoint is working"""
    
    print("Testing Profile Picture Upload Functionality")
    print("=" * 60)
    
    # Test if the endpoint exists
    url = "http://localhost:8000/api/students/upload-profile-picture/"
    
    try:
        # Test without authentication (should return 401)
        response = requests.post(url)
        print(f"Endpoint test (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Endpoint exists and requires authentication")
        elif response.status_code == 404:
            print("✗ Endpoint not found - check URL configuration")
        else:
            print(f"? Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend server")
        print("Make sure the backend is running on port 8000")
        return
    
    # Check if users have avatar field
    print("\nChecking User model for avatar field:")
    user = User.objects.first()
    if user:
        print(f"✓ Found user: {user.email}")
        if hasattr(user, 'avatar'):
            print("✓ User model has avatar field")
            if user.avatar:
                print(f"  Current avatar: {user.avatar}")
            else:
                print("  No avatar currently set")
        else:
            print("✗ User model missing avatar field")
    else:
        print("✗ No users found in database")

if __name__ == "__main__":
    test_profile_picture_endpoint()
