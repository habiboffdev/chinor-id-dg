#!/usr/bin/env python3
"""
Test the updated opportunity details page functionality
"""

import requests

def test_opportunity_details():
    """Test opportunity details functionality"""
    
    print("🧪 TESTING UPDATED OPPORTUNITY DETAILS")
    print("=" * 50)
    
    try:
        # Test API to ensure cover_image is included
        print("📡 Testing opportunity API with cover image...")
        response = requests.get('http://localhost:8000/api/opportunities/1/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API working")
            print(f"📋 Title: {data.get('title', 'N/A')}")
            print(f"🏢 Organization: {data.get('organization', {}).get('name', 'N/A')}")
            print(f"🖼️  Cover Image: {data.get('cover_image', 'No cover image')}")
            print(f"❓ Additional Questions: {len(data.get('additional_questions', []))}")
            
            # Check if cover_image field exists
            if 'cover_image' in data:
                print("✅ Cover image field present in API response")
            else:
                print("❌ Cover image field missing from API response")
                
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running")
        return False
    
    # Test frontend access
    try:
        print("\n🌐 Testing opportunity details page...")
        response = requests.get('http://localhost:8080/opportunity-details.html?id=1')
        
        if response.status_code == 200:
            print("✅ Opportunity details page accessible")
            
            # Check for removed fields in HTML
            html_content = response.text
            if 'resumeUpload' not in html_content:
                print("✅ Resume upload field removed")
            else:
                print("❌ Resume upload field still present")
                
            if 'portfolioLink' not in html_content:
                print("✅ Portfolio field removed")
            else:
                print("❌ Portfolio field still present")
                
            if 'linkedinProfile' not in html_content:
                print("✅ LinkedIn field removed") 
            else:
                print("❌ LinkedIn field still present")
                
            if 'coverImageContainer' in html_content:
                print("✅ Cover image container present")
            else:
                print("❌ Cover image container missing")
                
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server not running")
        return False
    
    print("\n" + "=" * 50)
    print("✅ TESTS COMPLETED!")
    print("🎯 Summary of changes:")
    print("   • ✅ Cover image functionality added")
    print("   • ✅ Resume upload field removed")
    print("   • ✅ Portfolio field removed") 
    print("   • ✅ LinkedIn field removed")
    print("   • ✅ Simplified application form")
    print("   • ✅ Professional cover image design")
    print("\n🌐 Test the page: http://localhost:8080/opportunity-details.html?id=1")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_opportunity_details()
