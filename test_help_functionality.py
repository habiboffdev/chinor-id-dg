#!/usr/bin/env python3
"""
Quick test script to verify help functionality translations are working correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot.i18n import t

def test_help_translations():
    """Test that help translations are available in all languages"""
    
    languages = ['en', 'ru', 'uz']
    help_keys = ['help_button', 'help_registration', 'help_registered']
    
    print("🧪 Testing Help Functionality Translations")
    print("=" * 50)
    
    for lang in languages:
        print(f"\n📍 Language: {lang.upper()}")
        print("-" * 30)
        
        for key in help_keys:
            translation = t(lang, key)
            if translation and translation != key:  # Check it's not falling back to key
                print(f"✅ {key}: Available")
                # Show first line of translation for verification
                first_line = translation.split('\n')[0][:60]
                print(f"   Preview: {first_line}...")
            else:
                print(f"❌ {key}: Missing or incomplete")
        
        # Test that button text is different for each language
        button_text = t(lang, 'help_button')
        print(f"🔘 Help button: {button_text}")

def test_help_content_structure():
    """Test that help content has proper structure"""
    
    print("\n\n🧪 Testing Help Content Structure")
    print("=" * 50)
    
    # Test registration help content
    reg_help_en = t('en', 'help_registration')
    
    # Check for key elements
    required_elements = [
        '1️⃣',  # Step numbering
        'Student 🎓',  # Registration button reference
        'Full name',  # Registration steps
        'Phone number',
        'Email address',
        'Discover opportunities',  # Features after registration
        'Tips:',  # Tips section
    ]
    
    print("\n📋 Registration Help Content Check:")
    for element in required_elements:
        if element in reg_help_en:
            print(f"✅ Contains: {element}")
        else:
            print(f"❌ Missing: {element}")
    
    # Test registered help content
    reg_user_help_en = t('en', 'help_registered')
    
    registered_elements = [
        "You're registered!",
        "Discover Opportunities",
        "Get Recommendations", 
        "My Applications",
        "My Profile",
        "Need help?",
    ]
    
    print("\n📋 Registered User Help Content Check:")
    for element in registered_elements:
        if element in reg_user_help_en:
            print(f"✅ Contains: {element}")
        else:
            print(f"❌ Missing: {element}")

if __name__ == "__main__":
    test_help_translations()
    test_help_content_structure()
    print("\n\n🎉 Help functionality test completed!")
    print("\n💡 To test in Telegram:")
    print("1. Start the bot")
    print("2. Send 'help' command or press 'Help ❓' button")
    print("3. Verify different help content for registered vs unregistered users")
