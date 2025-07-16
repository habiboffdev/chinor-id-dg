#!/usr/bin/env python3
"""
Final verification script to check if JavaScript errors are fixed
"""

import subprocess
import requests
import time

def check_js_fixes():
    print("🔧 Verifying JavaScript Fixes...")
    
    try:
        # Test the page loads
        response = requests.get("http://localhost:8080/opportunity-details.html", timeout=5)
        if response.status_code != 200:
            print(f"❌ Page not accessible (Status: {response.status_code})")
            return False
        
        html_content = response.text
        
        # Check that problematic references are removed
        checks = [
            ("getElementById('applyButton')", "Old applyButton references"),
            ("getElementById('loginRequiredSection')", "Missing loginRequiredSection references"),
            ("getElementById('alreadyAppliedSection')", "Missing alreadyAppliedSection references")
        ]
        
        issues_found = []
        for pattern, description in checks:
            if pattern in html_content:
                issues_found.append(description)
        
        # Check that new elements are present
        required_elements = [
            ("getElementById('quickApplyButton')", "Quick apply button"),
            ("getElementById('loginToApplyButton')", "Login to apply button"),
            ("getElementById('applicationSection')", "Application section"),
            ("function checkApplicationStatus", "Application status function")
        ]
        
        missing_elements = []
        for element, description in required_elements:
            if element not in html_content:
                missing_elements.append(description)
        
        # Results
        print("📊 JavaScript Fix Results:")
        
        if issues_found:
            print("❌ Issues still present:")
            for issue in issues_found:
                print(f"   - {issue}")
        else:
            print("✅ No old problematic references found")
        
        if missing_elements:
            print("❌ Missing required elements:")
            for element in missing_elements:
                print(f"   - {element}")
        else:
            print("✅ All required elements present")
        
        # Check for null-safe access patterns
        null_safe_patterns = [
            "if (quickApplyBtn) quickApplyBtn.classList",
            "if (quickApplyButton) quickApplyButton.classList",
            "if (loginToApplyButton) loginToApplyButton.classList",
            "if (applicationSection) applicationSection.classList"
        ]
        
        null_safe_count = sum(1 for pattern in null_safe_patterns if pattern in html_content)
        
        print(f"✅ Null-safe access patterns found: {null_safe_count}/{len(null_safe_patterns)}")
        
        success = len(issues_found) == 0 and len(missing_elements) == 0 and null_safe_count >= 2
        
        if success:
            print("🎉 JavaScript fixes verified successfully!")
        else:
            print("⚠️  Some issues remain")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = check_js_fixes()
    print(f"\n🏁 Final Status: {'✅ PASSED' if success else '❌ FAILED'}")
    exit(0 if success else 1)
