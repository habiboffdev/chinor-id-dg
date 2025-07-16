#!/usr/bin/env python3
"""
Simple test script to check if frontend and backend are working properly
"""

import requests
import json

# Test backend API endpoints
API_BASE = "http://localhost:8000/api"

def test_backend():
    print("Testing backend connectivity...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"API Root: {response.status_code}")
    except Exception as e:
        print(f"API Root failed: {e}")
    
    # Test authentication endpoints
    try:
        response = requests.post(f"{API_BASE}/auth/register/", json={
            "username": "testuser123",
            "email": "test123@example.com", 
            "password": "testpass123",
            "user_type": "student"
        })
        print(f"Register test: {response.status_code}")
        if response.status_code == 400:
            print("Registration failed (probably user exists - this is normal)")
    except Exception as e:
        print(f"Register failed: {e}")
    
    # Test login
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json={
            "username": "testuser123",
            "password": "testpass123"
        })
        print(f"Login test: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            if token:
                print("Login successful, testing authenticated endpoints...")
                
                # Test student profile
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = requests.get(f"{API_BASE}/students/profile/", headers=headers)
                print(f"Student profile: {profile_response.status_code}")
                
                # Test education endpoint
                edu_response = requests.get(f"{API_BASE}/students/education/", headers=headers)
                print(f"Education endpoint: {edu_response.status_code}")
                
                # Test experience endpoint  
                exp_response = requests.get(f"{API_BASE}/students/experience/", headers=headers)
                print(f"Experience endpoint: {exp_response.status_code}")
                
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Login failed: {e}")

def test_frontend():
    print("\nTesting frontend connectivity...")
    
    try:
        response = requests.get("http://localhost:8080/profile.html")
        print(f"Frontend profile page: {response.status_code}")
        
        # Check if the page contains the expected elements
        if response.status_code == 200:
            content = response.text
            if 'addExperienceBtn' in content:
                print("✓ Add Experience button found in HTML")
            else:
                print("✗ Add Experience button NOT found in HTML")
                
            if 'modalOverlay' in content:
                print("✓ Modal overlay found in HTML")
            else:
                print("✗ Modal overlay NOT found in HTML")
                
            if 'showExperienceModal' in content:
                print("✓ showExperienceModal function found in HTML")
            else:
                print("✗ showExperienceModal function NOT found in HTML")
        
    except Exception as e:
        print(f"Frontend test failed: {e}")

if __name__ == "__main__":
    test_backend()
    test_frontend()
    print("\nTest complete!")
