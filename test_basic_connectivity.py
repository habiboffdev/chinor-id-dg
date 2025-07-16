#!/usr/bin/env python3
"""
Simple test to check if the backend is working and provide debugging info
"""

import requests
import json

def test_backend_api():
    print("🧪 Testing backend API...")
    
    try:
        # Test basic opportunities endpoint
        response = requests.get("http://localhost:8000/api/opportunities/")
        print(f"📡 API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API Response keys: {list(data.keys())}")
            
            if 'results' in data:
                opportunities = data['results']
                print(f"🎯 Opportunities count: {len(opportunities)}")
                
                if opportunities:
                    opp = opportunities[0]
                    print(f"📄 First opportunity: {opp.get('title', 'No title')}")
                    print(f"📄 First opportunity keys: {list(opp.keys())}")
                else:
                    print("⚠️ No opportunities in results")
            else:
                print(f"⚠️ No 'results' key in response: {data}")
                
            return True
        else:
            print(f"❌ API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_frontend_accessibility():
    print("🌐 Testing frontend accessibility...")
    
    pages = [
        "opportunities.html",
        "debug_load.html",
        "final_filter_test.html"
    ]
    
    results = []
    for page in pages:
        try:
            response = requests.get(f"http://localhost:8080/{page}")
            success = response.status_code == 200
            results.append(success)
            print(f"📄 {page}: {'✅' if success else '❌'} ({response.status_code})")
        except Exception as e:
            results.append(False)
            print(f"📄 {page}: ❌ ({str(e)})")
    
    return all(results)

def provide_manual_test_instructions():
    print("\n" + "="*60)
    print("🔧 MANUAL TESTING INSTRUCTIONS")
    print("="*60)
    print("1. Open http://localhost:8080/opportunities.html in your browser")
    print("2. Open browser console (F12 -> Console)")
    print("3. Look for these messages:")
    print("   - '🚀 INITIALIZING OPPORTUNITIES PAGE!'")
    print("   - '🚀 loadOpportunities() called!'")
    print("   - '✅ Updating UI with opportunities: X'")
    print("4. Check if opportunities are displayed")
    print("5. If not, try clicking 'Clear All Filters' button")
    print("\nAlternatively, test the debug page:")
    print("- http://localhost:8080/debug_load.html")
    print("- Click 'Load Opportunities' button")
    print("- Check the debug console output")
    print("\nDebugging steps:")
    print("- Check browser console for JavaScript errors")
    print("- Verify API calls are being made to /api/opportunities/")
    print("- Check if opportunities-container element exists")
    print("- Verify currentFilters object state")

if __name__ == "__main__":
    print("🚀 Starting Simple Backend/Frontend Test")
    print("=" * 50)
    
    api_success = test_backend_api()
    print()
    
    frontend_success = test_frontend_accessibility()
    
    print("=" * 50)
    print(f"📊 API Test: {'✅' if api_success else '❌'}")
    print(f"🌐 Frontend Test: {'✅' if frontend_success else '❌'}")
    
    if api_success and frontend_success:
        print("🎉 Backend and frontend are accessible!")
        print("💡 If opportunities still don't show, this is likely a JavaScript initialization issue.")
    else:
        print("⚠️ Basic connectivity issues detected.")
    
    provide_manual_test_instructions()
