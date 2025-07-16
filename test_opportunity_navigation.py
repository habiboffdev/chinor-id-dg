#!/usr/bin/env python3
"""
Test script to verify opportunity navigation works correctly
"""

import time
import requests

def test_opportunity_redirect():
    """Test that opportunities page loads and API endpoints work"""
    
    print("🧪 TESTING OPPORTUNITY NAVIGATION")
    print("=" * 50)
    
    try:
        # Test backend API
        print("📡 Testing backend API...")
        response = requests.get('http://localhost:8000/api/opportunities/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API working - Found {len(data.get('results', []))} opportunities")
            
            if data.get('results'):
                first_opp = data['results'][0]
                print(f"📋 First opportunity: {first_opp.get('title', 'No title')}")
                print(f"❓ Additional questions: {len(first_opp.get('additional_questions', []))}")
        else:
            print(f"❌ Backend API error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running at http://localhost:8000")
        return False
    
    try:
        # Test frontend server
        print("\n🌐 Testing frontend server...")
        response = requests.get('http://localhost:8080/opportunities.html')
        
        if response.status_code == 200:
            print("✅ Frontend server working")
        else:
            print(f"❌ Frontend server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server not running at http://localhost:8080")
        return False
    
    try:
        # Test opportunity details page
        print("\n📄 Testing opportunity details page...")
        response = requests.get('http://localhost:8080/opportunity-details.html?id=1')
        
        if response.status_code == 200:
            print("✅ Opportunity details page accessible")
        else:
            print(f"❌ Opportunity details page error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not access opportunity details page")
        return False
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("🚀 Navigation should work correctly:")
    print("   1. Click 'View Details' on opportunities page")
    print("   2. Should redirect to opportunity-details.html?id=X")
    print("   3. Details page should load all opportunity info")
    print("   4. Application form should show custom questions")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_opportunity_redirect()
