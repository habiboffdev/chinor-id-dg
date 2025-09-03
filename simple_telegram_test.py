"""
Simple Telegram posting verification script
Tests basic functionality without complex mocking
"""
import os
import sys
import django
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
backend_path = project_root / 'opportuni_backend'
telegram_bot_path = project_root / 'telegram_bot'

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(telegram_bot_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

def test_basic_imports():
    """Test if all required modules can be imported"""
    print("🔧 Testing basic imports...")
    
    try:
        # Test Django imports
        from apps.opportunities.models import Opportunity
        from apps.organizations.models import Organization
        print("✅ Django models imported successfully")
        
        # Test telegram bot imports
        from telegram_bot.handlers.admin import format_opportunity_for_channel
        from telegram_bot.handlers.admin import create_opportunity_keyboard
        from telegram_bot.handlers.admin import post_opportunity_to_channel
        print("✅ Telegram bot modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_opportunity_formatting():
    """Test opportunity message formatting"""
    print("\n📝 Testing opportunity formatting...")
    
    try:
        from apps.opportunities.models import Opportunity
        from apps.organizations.models import Organization
        from django.contrib.auth import get_user_model
        from telegram_bot.handlers.admin import format_opportunity_for_channel
        from django.utils import timezone
        from datetime import timedelta
        
        User = get_user_model()
        
        # Create or get test user for organization
        test_user, user_created = User.objects.get_or_create(
            username='test_org_user',
            defaults={
                'email': 'test@simple-test.com',
                'first_name': 'Test',
                'last_name': 'Organization',
                'user_type': 'organization'
            }
        )
        
        # Create test organization
        org, created = Organization.objects.get_or_create(
            name="Simple Test Org",
            defaults={
                'user': test_user,
                'description': 'Simple test organization',
                'website': 'https://simple-test.com',
                'country': 'Test Country',
                'city': 'Test City',
                'email': 'test@simple-test.com',
                'organization_type': 'corporation'
            }
        )
        
        # Create test opportunity and save it
        opportunity = Opportunity.objects.create(
            title="Simple Test Opportunity",
            organization=org,
            description="A simple test opportunity for basic verification",
            opportunity_type='job',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=45),
            location='Remote Work',
            is_remote=True,
            compensation='$50,000',
            required_major='Any',
            graduation_year_min=2020,
            graduation_year_max=2025
        )
        
        # Test formatting
        formatted_text = format_opportunity_for_channel(opportunity)
        
        print("📄 Formatted message preview:")
        print("-" * 50)
        print(formatted_text)
        print("-" * 50)
        
        # Check for key elements
        required_elements = [
            "Simple Test Opportunity",
            "Simple Test Org",
            "Job",
            "Remote Work",
            "$50,000"
        ]
        
        missing = []
        for element in required_elements:
            if element not in formatted_text:
                missing.append(element)
        
        # Clean up the test opportunity
        opportunity.delete()
        
        if missing:
            print(f"❌ Missing elements: {missing}")
            return False
        else:
            print("✅ All required elements present in formatted message")
            return True
            
    except Exception as e:
        print(f"❌ Formatting test error: {e}")
        return False

def test_keyboard_creation():
    """Test inline keyboard creation"""
    print("\n⌨️  Testing keyboard creation...")
    
    try:
        from apps.opportunities.models import Opportunity
        from apps.organizations.models import Organization
        from telegram_bot.handlers.admin import create_opportunity_keyboard
        from django.utils import timezone
        from datetime import timedelta
        
        # Get organization
        org = Organization.objects.filter(name="Simple Test Org").first()
        if not org:
            print("❌ Test organization not found")
            return False
        
        # Create test opportunity (in memory only)
        opportunity = Opportunity(
            id=999,  # Fake ID for testing
            title="Keyboard Test",
            organization=org,
            description="Testing keyboard",
            opportunity_type='internship',
            status='published',
            application_deadline=timezone.now() + timedelta(days=30),
            start_date=timezone.now().date() + timedelta(days=45),
            location='Test Location'
        )
        
        # Test keyboard creation
        webapp_url = "https://test.opportuni.com"
        keyboard = create_opportunity_keyboard(opportunity, webapp_url)
        
        # Check keyboard structure
        if hasattr(keyboard, 'keyboard') and keyboard.keyboard:
            button_count = sum(len(row) for row in keyboard.keyboard)
            print(f"✅ Keyboard created with {button_count} buttons")
            
            # Show button details
            for i, row in enumerate(keyboard.keyboard):
                for j, button in enumerate(row):
                    print(f"   Button {i+1}.{j+1}: {button.text}")
                    if hasattr(button, 'url'):
                        print(f"     URL: {button.url}")
            
            return True
        else:
            print("❌ No buttons in keyboard")
            return False
            
    except Exception as e:
        print(f"❌ Keyboard test error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from django.conf import settings
        
        config_items = [
            ('BOT_TOKEN', getattr(settings, 'TELEGRAM_BOT_TOKEN', None)),
            ('BOT_ENABLED', getattr(settings, 'TELEGRAM_BOT_ENABLED', None)),
            ('CHANNEL_ID', getattr(settings, 'TELEGRAM_CHANNEL_ID', None)),
            ('WEBAPP_URL', getattr(settings, 'TELEGRAM_WEBAPP_URL', None)),
        ]
        
        config_ok = True
        for name, value in config_items:
            if value:
                # Mask token for security
                display_value = value if name != 'BOT_TOKEN' else f"{'*' * (len(str(value)) - 4)}{str(value)[-4:]}" if len(str(value)) > 4 else "****"
                print(f"✅ {name}: {display_value}")
            else:
                print(f"⚠️  {name}: Not configured")
                if name in ['BOT_TOKEN']:  # Critical configs
                    config_ok = False
        
        return config_ok
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Run all simple tests"""
    print("🚀 Simple Telegram Posting Verification")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_configuration),
        ("Opportunity Formatting", test_opportunity_formatting),
        ("Keyboard Creation", test_keyboard_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("-" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✅ Basic Telegram posting functionality is working")
        print("\nNext steps:")
        print("1. Set up your real bot token and channel")
        print("2. Use: python manage.py test_telegram_channel --latest")
        print("3. Create a new opportunity to test auto-posting")
    else:
        print("⚠️  Some verifications failed")
        print("Check the error messages above and fix configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
