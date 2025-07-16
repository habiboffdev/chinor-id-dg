#!/usr/bin/env python3
"""
Simple test to check if backend API is accessible and opportunity exists
"""

import requests
import json

def test_api_connectivity():
    """Test API connectivity and opportunity data"""
    
    print("🔍 DEBUGGING OPPORTUNITY API ACCESS")
    print("=" * 50)
    
    # Test 1: Backend server running
    try:
        print("1️⃣  Testing backend server...")
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"   ✅ Backend server responding (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend server not running on http://localhost:8000")
        print("   💡 Start with: cd opportuni_backend && python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
        return False
    
    # Test 2: API endpoint accessible
    try:
        print("\n2️⃣  Testing API endpoint...")
        response = requests.get('http://localhost:8000/api/', timeout=5)
        print(f"   ✅ API endpoint accessible (status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ API endpoint error: {e}")
        return False
    
    # Test 3: Opportunities list
    try:
        print("\n3️⃣  Testing opportunities list...")
        response = requests.get('http://localhost:8000/api/opportunities/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('results', [])
            print(f"   ✅ Opportunities list accessible ({len(opportunities)} opportunities)")
            
            if opportunities:
                first_opp = opportunities[0]
                print(f"   📋 First opportunity: ID={first_opp.get('id')}, Title='{first_opp.get('title')}'")
                return first_opp.get('id')  # Return first opportunity ID for testing
            else:
                print("   ⚠️  No opportunities found in database")
                return None
                
        elif response.status_code == 401:
            print("   ⚠️  Authentication required for opportunities list")
            # Try to get a specific opportunity that might be public
            return test_specific_opportunity()
        else:
            print(f"   ❌ Opportunities list error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Opportunities list error: {e}")
        return False

def test_specific_opportunity(opp_id=1):
    """Test accessing a specific opportunity"""
    try:
        print(f"\n4️⃣  Testing specific opportunity (ID: {opp_id})...")
        response = requests.get(f'http://localhost:8000/api/opportunities/{opp_id}/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Opportunity {opp_id} accessible")
            print(f"   📋 Title: {data.get('title', 'N/A')}")
            print(f"   🏢 Organization: {data.get('organization', {}).get('name', 'N/A')}")
            print(f"   🖼️  Cover Image: {data.get('cover_image', 'None')}")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Authentication required for opportunity {opp_id}")
            return False
        elif response.status_code == 404:
            print(f"   ❌ Opportunity {opp_id} not found")
            return False
        else:
            print(f"   ❌ Error accessing opportunity {opp_id}: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing opportunity {opp_id}: {e}")
        return False

def main():
    """Main test function"""
    opp_id = test_api_connectivity()
    
    if opp_id:
        success = test_specific_opportunity(opp_id)
    else:
        success = test_specific_opportunity(1)  # Try ID 1 as fallback
    
    print("\n" + "=" * 50)
    if success:
        print("✅ API ACCESS WORKING!")
        print("💡 Issue might be in frontend JavaScript or authentication")
        print("🔧 Check browser console for JavaScript errors")
    else:
        print("❌ API ACCESS ISSUES FOUND!")
        print("🛠️  Possible solutions:")
        print("   1. Start backend: cd opportuni_backend && python manage.py runserver 8000")
        print("   2. Check if opportunity with ID=1 exists in database")
        print("   3. Verify API authentication requirements")
    print("=" * 50)

if __name__ == "__main__":
    main()
