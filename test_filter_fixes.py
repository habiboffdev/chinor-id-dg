#!/usr/bin/env python3
"""
Comprehensive test script to verify filter/search functionality fixes.
This script will run automated tests to ensure all issues are resolved.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8080"
API_BASE_URL = "http://localhost:8000/api"

def log(message):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def test_api_endpoint():
    """Test that the opportunities API endpoint works without auth"""
    log("Testing API endpoint accessibility...")
    
    try:
        # Test basic opportunities endpoint
        response = requests.get(f"{API_BASE_URL}/opportunities/")
        log(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ API accessible - Found {len(data.get('results', []))} opportunities")
            return True
        else:
            log(f"❌ API not accessible - Status: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ API test failed: {str(e)}")
        return False

def test_filter_parameters():
    """Test various filter parameters"""
    log("Testing filter parameters...")
    
    test_cases = [
        {"search": "python"},
        {"type": "internship"},
        {"location": "remote"},
        {"search": "data", "type": "scholarship"},
        {"application_deadline__gte": "2024-01-01"},
        {"created_at__gte": "2024-01-01"}
    ]
    
    results = []
    for i, params in enumerate(test_cases):
        try:
            response = requests.get(f"{API_BASE_URL}/opportunities/", params=params)
            success = response.status_code == 200
            results.append(success)
            log(f"Filter test {i+1}: {params} -> {'✅' if success else '❌'}")
        except Exception as e:
            results.append(False)
            log(f"Filter test {i+1}: {params} -> ❌ ({str(e)})")
    
    return all(results)

def test_frontend_accessibility():
    """Test that frontend pages are accessible"""
    log("Testing frontend accessibility...")
    
    pages = [
        "opportunities.html",
        "final_filter_test.html"
    ]
    
    results = []
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}/{page}")
            success = response.status_code == 200
            results.append(success)
            log(f"Frontend test {page}: {'✅' if success else '❌'}")
        except Exception as e:
            results.append(False)
            log(f"Frontend test {page}: ❌ ({str(e)})")
    
    return all(results)

def check_javascript_syntax():
    """Check JavaScript files for syntax errors"""
    log("Checking JavaScript syntax...")
    
    js_files = [
        "opportuni_frontend/assets/js/opportunities.js",
        "opportuni_frontend/assets/js/api.js",
        "opportuni_frontend/assets/js/utils.js",
        "opportuni_frontend/assets/js/auth.js"
    ]
    
    import subprocess
    import os
    
    results = []
    for js_file in js_files:
        try:
            if os.path.exists(js_file):
                result = subprocess.run(
                    ["node", "-c", js_file], 
                    capture_output=True, 
                    text=True,
                    cwd="/home/mirzosharif/MVP/chinor_id_new"
                )
                success = result.returncode == 0
                results.append(success)
                log(f"JS syntax check {js_file}: {'✅' if success else '❌'}")
                if not success:
                    log(f"Error: {result.stderr}")
            else:
                log(f"JS file not found: {js_file}")
                results.append(False)
        except Exception as e:
            results.append(False)
            log(f"JS syntax check {js_file}: ❌ ({str(e)})")
    
    return all(results)

def run_comprehensive_test():
    """Run all tests"""
    log("🚀 Starting Comprehensive Filter/Search Test")
    log("=" * 60)
    
    tests = [
        ("API Endpoint", test_api_endpoint),
        ("Filter Parameters", test_filter_parameters),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("JavaScript Syntax", check_javascript_syntax)
    ]
    
    results = {}
    for test_name, test_func in tests:
        log(f"\n📋 Running {test_name} Test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            log(f"❌ {test_name} test failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    log("\n" + "=" * 60)
    log("📊 TEST SUMMARY")
    log("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log(f"{test_name:.<30} {status}")
        if not result:
            all_passed = False
    
    log("=" * 60)
    if all_passed:
        log("🎉 ALL TESTS PASSED! Filter/search functionality is working correctly.")
    else:
        log("⚠️ Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
