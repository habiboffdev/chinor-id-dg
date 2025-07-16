#!/usr/bin/env python3
"""
Test script to check if opportunities have questions and test the full application flow.
"""

import requests
import json

def test_opportunity_questions():
    """Test if opportunities have additional questions loaded properly"""
    
    print("🧪 Testing Opportunity Questions Loading...")
    
    # Test API endpoint
    api_base = "http://localhost:8000/api"
    
    try:
        # Get list of opportunities
        print("📋 Fetching opportunities...")
        response = requests.get(f"{api_base}/opportunities/")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch opportunities (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
        
        opportunities = response.json()
        print(f"✅ Found {len(opportunities.get('results', []))} opportunities")
        
        if not opportunities.get('results'):
            print("❌ No opportunities found")
            return False
        
        # Test first opportunity details
        first_opp = opportunities['results'][0]
        opp_id = first_opp['id']
        
        print(f"\n🔍 Testing opportunity #{opp_id}: {first_opp['title']}")
        
        # Get detailed opportunity data
        response = requests.get(f"{api_base}/opportunities/{opp_id}/")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch opportunity details (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
        
        opp_data = response.json()
        
        # Check additional questions
        questions = opp_data.get('additional_questions', [])
        print(f"❓ Additional questions found: {len(questions)}")
        
        if questions:
            print("📝 Questions details:")
            for i, q in enumerate(questions):
                print(f"   {i+1}. {q['question']} (Type: {q['question_type']}, Required: {q['is_required']})")
        else:
            print("⚠️  No additional questions found for this opportunity")
        
        # Check other required fields
        required_fields = ['id', 'title', 'description', 'organization', 'application_deadline']
        missing_fields = []
        
        for field in required_fields:
            if field not in opp_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields present")
        
        # Test JSON structure for frontend
        print("\n📦 Testing frontend compatibility...")
        
        # Check if the structure matches what frontend expects
        frontend_fields = [
            'additional_questions', 'title', 'description', 'organization_name',
            'application_deadline', 'location', 'opportunity_type'
        ]
        
        frontend_compatible = True
        for field in frontend_fields:
            if field == 'organization_name':
                # Check if we can get org name from organization object
                if not opp_data.get('organization', {}).get('name'):
                    print(f"⚠️  organization.name not found")
                    frontend_compatible = False
            elif field not in opp_data:
                print(f"⚠️  Field '{field}' not found")
                frontend_compatible = False
        
        if frontend_compatible:
            print("✅ Frontend compatibility check passed")
        else:
            print("⚠️  Some frontend compatibility issues found")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_application_submission():
    """Test the application submission endpoint"""
    
    print("\n🚀 Testing Application Submission...")
    
    # For this test, we'll need authentication
    # Let's check if the endpoint exists and what it expects
    
    api_base = "http://localhost:8000/api"
    
    try:
        # Test POST to applications without auth (should fail gracefully)
        test_data = {
            "opportunity": 1,
            "cover_letter": "Test cover letter for application submission testing",
            "relevant_experience": "Test experience",
            "availability": "Flexible"
        }
        
        response = requests.post(f"{api_base}/applications/", json=test_data)
        
        if response.status_code == 401:
            print("✅ Application endpoint requires authentication (as expected)")
            return True
        elif response.status_code == 403:
            print("✅ Application endpoint requires proper permissions (as expected)")
            return True
        elif response.status_code in [400, 422]:
            print("✅ Application endpoint validates data (as expected)")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Unexpected response from applications endpoint: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Application submission test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Opportunity Questions and Application Flow\n")
    
    # Test 1: Questions loading
    questions_ok = test_opportunity_questions()
    
    # Test 2: Application submission
    submission_ok = test_application_submission()
    
    print(f"\n🏁 Final Result:")
    print(f"   Questions loading: {'✅ PASSED' if questions_ok else '❌ FAILED'}")
    print(f"   Application endpoint: {'✅ PASSED' if submission_ok else '❌ FAILED'}")
    
    overall_success = questions_ok and submission_ok
    print(f"   Overall: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    exit(0 if overall_success else 1)
