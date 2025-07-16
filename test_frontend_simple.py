#!/usr/bin/env python3
"""
Simple test to check if opportunities are actually loading in the frontend
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_opportunities_loading():
    print("🧪 Testing opportunities loading in browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:8080/opportunities.html")
        
        print("✅ Page loaded")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Check for opportunities container
        container = driver.find_element(By.ID, "opportunities-container")
        print(f"📦 Container found: {container is not None}")
        
        if container:
            content = container.get_attribute('innerHTML')
            print(f"📄 Container content length: {len(content)}")
            print(f"📄 Container first 200 chars: {content[:200]}")
            
            # Check if there are opportunity cards
            opportunity_cards = driver.find_elements(By.CSS_SELECTOR, ".opportunity-card, .opportunity-item")
            print(f"🎯 Opportunity cards found: {len(opportunity_cards)}")
            
            # Check for empty state
            empty_state = driver.find_elements(By.XPATH, "//*[contains(text(), 'No opportunities')]")
            print(f"📭 Empty state found: {len(empty_state) > 0}")
            
            # Check for loading skeleton
            loading = driver.find_elements(By.ID, "loading-skeleton")
            if loading and loading[0].is_displayed():
                print("⏳ Loading skeleton is visible")
            else:
                print("✅ Loading skeleton is hidden")
                
        return True
        
    except Exception as e:
        print(f"❌ Browser test failed: {str(e)}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

def test_direct_opportunities_call():
    print("🌐 Testing direct opportunities API call...")
    try:
        response = requests.get("http://localhost:8000/api/opportunities/")
        print(f"📡 API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API Response: {data}")
            print(f"🎯 Opportunities count: {len(data.get('results', []))}")
            return True
        else:
            print(f"❌ API failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Frontend Test")
    print("=" * 50)
    
    api_success = test_direct_opportunities_call()
    print()
    
    # Only run browser test if API is working
    if api_success:
        browser_success = test_opportunities_loading()
    else:
        print("⚠️ Skipping browser test due to API failure")
        browser_success = False
    
    print("=" * 50)
    print(f"📊 API Test: {'✅' if api_success else '❌'}")
    print(f"🌐 Browser Test: {'✅' if browser_success else '❌'}")
    
    if api_success and browser_success:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed.")
