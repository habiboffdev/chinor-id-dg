#!/usr/bin/env python3
"""
API Response Validation Test
Tests the opportunities API endpoint to understand the response structure
"""

import requests
import json
import sys

def test_api_response():
    """Test the opportunities API endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/api/opportunities/"
    
    try:
        print("Testing API endpoint:", url)
        
        # Make request without authentication first
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Check if it's paginated
            if isinstance(data, dict):
                if 'results' in data:
                    print("✅ Paginated response detected")
                    opportunities = data['results']
                    print(f"Results type: {type(opportunities)}")
                    print(f"Results count: {len(opportunities) if isinstance(opportunities, list) else 'Not a list'}")
                    
                    if isinstance(opportunities, list) and len(opportunities) > 0:
                        print("✅ Sample opportunity keys:", list(opportunities[0].keys()))
                    else:
                        print("⚠️  No opportunities in results")
                        
                elif isinstance(data, list):
                    print("✅ Direct array response")
                    print(f"Opportunities count: {len(data)}")
                    if len(data) > 0:
                        print("✅ Sample opportunity keys:", list(data[0].keys()))
                else:
                    print("❌ Unexpected response format")
                    print("Response structure:", json.dumps(data, indent=2)[:500])
            
        elif response.status_code == 401:
            print("⚠️  Authentication required")
            print("Response:", response.text)
            
        elif response.status_code == 403:
            print("⚠️  Permission denied")
            print("Response:", response.text)
            
        else:
            print(f"❌ Error response: {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the Django server running?")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    return True

def validate_response_format():
    """Validate expected response format"""
    print("\n" + "="*50)
    print("EXPECTED API RESPONSE FORMATS:")
    print("="*50)
    
    print("\n1. Paginated Response (Preferred):")
    print(json.dumps({
        "count": 25,
        "next": "http://localhost:8000/api/opportunities/?page=2",
        "previous": None,
        "results": [
            {
                "id": 1,
                "title": "Software Engineer Internship",
                "opportunity_type": "internship",
                "organization_name": "Tech Corp",
                "description": "Great opportunity...",
                "location": "San Francisco, CA",
                "is_remote": False,
                "application_deadline": "2025-08-15T23:59:59Z"
            }
        ]
    }, indent=2))
    
    print("\n2. Direct Array Response (Alternative):")
    print(json.dumps([
        {
            "id": 1,
            "title": "Software Engineer Internship",
            "opportunity_type": "internship",
            "organization_name": "Tech Corp"
        }
    ], indent=2))

if __name__ == "__main__":
    print("🔍 API Response Structure Test")
    print("="*50)
    
    success = test_api_response()
    validate_response_format()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
        sys.exit(1)
