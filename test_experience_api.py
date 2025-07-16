#!/usr/bin/env python3

import requests
import json
import sys

def test_experience_creation():
    base_url = 'http://localhost:8000/api'
    
    # Test login
    print("1. Testing login...")
    login_data = {'email': 'test@example.com', 'password': 'password123'}
    login_response = requests.post(f'{base_url}/auth/login/', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    tokens = login_response.json()
    headers = {'Authorization': f'Bearer {tokens["access"]}'}
    print("✅ Login successful!")
    
    # Test experience creation with various data scenarios
    test_cases = [
        {
            'name': 'Complete experience data',
            'data': {
                'title': 'Frontend Developer', 
                'company': 'Tech Solutions Inc',
                'experience_type': 'full_time',
                'description': 'Developed responsive web applications using React and JavaScript',
                'start_date': '2023-01-15',
                'end_date': '2024-01-15',
                'location': 'New York, NY',
                'is_current': False
            }
        },
        {
            'name': 'Current job (no end date)',
            'data': {
                'title': 'Software Intern', 
                'company': 'Startup Corp',
                'experience_type': 'internship',
                'description': 'Learning full-stack development',
                'start_date': '2024-06-01',
                'location': 'Remote',
                'is_current': True
            }
        },
        {
            'name': 'Minimal required data',
            'data': {
                'title': 'Project Manager', 
                'company': 'Business Solutions',
                'experience_type': 'project',
                'description': 'Managed team of 5 developers',
                'start_date': '2023-03-01'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i+1}. Testing: {test_case['name']}")
        exp_response = requests.post(f'{base_url}/students/experience/', 
                                   json=test_case['data'], headers=headers)
        
        if exp_response.status_code == 201:
            print(f"✅ Success: Experience created")
            print(f"   Response: {exp_response.json()}")
        else:
            print(f"❌ Failed: {exp_response.status_code}")
            print(f"   Response: {exp_response.text}")
            
            # Try to parse error details
            try:
                error_data = exp_response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
    
    # Test getting experiences
    print(f"\n{len(test_cases)+2}. Testing: Get experiences")
    get_response = requests.get(f'{base_url}/students/experience/', headers=headers)
    
    if get_response.status_code == 200:
        experiences = get_response.json()
        print(f"✅ Success: Retrieved {len(experiences.get('results', []))} experiences")
    else:
        print(f"❌ Failed to get experiences: {get_response.status_code} - {get_response.text}")
    
    return True

if __name__ == "__main__":
    print("Testing Experience API...")
    test_experience_creation()
