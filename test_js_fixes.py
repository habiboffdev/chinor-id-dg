#!/usr/bin/env python3
"""
Simple test script to verify the opportunity details page structure
and check for common JavaScript issues.
"""

import os
import sys
import subprocess
import time
import requests

def test_page_loads():
    """Test that the page loads and has expected structure"""
    
    print("🧪 Testing Opportunity Details Page Structure...")
    
    # Start the frontend server
    frontend_dir = "/home/mirzosharif/MVP/chinor_id_new/opportuni_frontend"
    server_process = None
    
    try:
        print("📡 Starting frontend server...")
        server_process = subprocess.Popen(
            ["python3", "-m", "http.server", "8080"],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test server is running
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            print(f"✅ Frontend server running (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend server not accessible: {e}")
            return False
        
        # Test the opportunity details page
        test_url = "http://localhost:8080/opportunity-details.html"
        print(f"🌐 Testing page: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Page loads successfully (Status: {response.status_code})")
                
                # Check for key elements in HTML
                html_content = response.text
                
                elements_to_check = [
                    ('id="coverImageContainer"', 'Cover image container'),
                    ('id="contentContainer"', 'Content container'),
                    ('id="opportunityTitle"', 'Opportunity title'),
                    ('id="applicationSection"', 'Application section'),
                    ('id="quickApplyButton"', 'Quick apply button'),
                    ('id="loginToApplyButton"', 'Login to apply button'),
                    ('id="coverLetter"', 'Cover letter field'),
                    ('id="applicationForm"', 'Application form'),
                    ('checkApplicationStatus', 'Application status function'),
                    ('setupApplicationForm', 'Setup form function')
                ]
                
                missing_elements = []
                for element, description in elements_to_check:
                    if element in html_content:
                        print(f"✅ Found {description}")
                    else:
                        missing_elements.append(description)
                        print(f"❌ Missing {description}")
                
                # Check for potential JavaScript issues
                js_issues = []
                
                # Check for old element references
                if "getElementById('applyButton')" in html_content:
                    js_issues.append("Old 'applyButton' reference found")
                
                if "getElementById('loginRequiredSection')" in html_content:
                    js_issues.append("Reference to missing 'loginRequiredSection'")
                
                if "getElementById('alreadyAppliedSection')" in html_content:
                    js_issues.append("Reference to missing 'alreadyAppliedSection'")
                
                # Check for new fixes
                if "getElementById('quickApplyButton')" in html_content:
                    print("✅ Updated button references found")
                
                # Report JavaScript issues
                if js_issues:
                    print("\n⚠️  Potential JavaScript issues:")
                    for issue in js_issues:
                        print(f"   - {issue}")
                else:
                    print("✅ No obvious JavaScript issues found")
                
                # Summary
                print(f"\n📊 Test Summary:")
                print(f"   - Missing elements: {len(missing_elements)}")
                print(f"   - JavaScript issues: {len(js_issues)}")
                
                if len(missing_elements) == 0 and len(js_issues) == 0:
                    print("🎉 Basic structure tests passed!")
                    return True
                else:
                    print("⚠️  Some issues found")
                    return False
                    
            else:
                print(f"❌ Page failed to load (Status: {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to load page: {e}")
            return False
    
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("🛑 Frontend server stopped")
    
    return False

def check_html_structure():
    """Check the HTML file structure directly"""
    
    print("\n🔍 Checking HTML file structure...")
    
    html_file = "/home/mirzosharif/MVP/chinor_id_new/opportuni_frontend/opportunity-details.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 HTML file size: {len(content)} characters")
        
        # Check for critical sections
        critical_sections = [
            ('<div id="coverImageContainer"', 'Cover image container'),
            ('<div id="contentContainer"', 'Content container'),
            ('<div id="applicationSection"', 'Application section'),
            ('<form id="applicationForm"', 'Application form'),
            ('function checkApplicationStatus', 'Application status function'),
            ('function setupApplicationForm', 'Setup form function')
        ]
        
        for section, description in critical_sections:
            if section in content:
                print(f"✅ Found {description}")
            else:
                print(f"❌ Missing {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Opportunity Details Page Tests\n")
    
    # Test 1: Check HTML structure
    structure_ok = check_html_structure()
    
    # Test 2: Test page loads
    if structure_ok:
        load_ok = test_page_loads()
    else:
        load_ok = False
    
    print(f"\n🏁 Final Result: {'✅ PASSED' if structure_ok and load_ok else '❌ FAILED'}")
    sys.exit(0 if (structure_ok and load_ok) else 1)
