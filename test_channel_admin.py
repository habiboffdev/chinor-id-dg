"""
Test script for channel administration functionality
Run this to verify the channel posting works correctly
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent
backend_path = project_root / 'opportuni_backend'
telegram_bot_path = project_root / 'telegram_bot'

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(telegram_bot_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

def test_opportunity_formatting():
    """Test opportunity formatting for channel posts"""
    print("Testing opportunity formatting...")
    
    try:
        from apps.opportunities.models import Opportunity
        from apps.organizations.models import Organization
        from telegram_bot.handlers.admin import format_opportunity_for_channel
        from django.utils import timezone
        from datetime import timedelta
        
        # Get or create a test organization
        org, _ = Organization.objects.get_or_create(
            name="Test Tech Company",
            defaults={
                'description': 'A test technology company',
                'website': 'https://example.com',
                'location': 'San Francisco, CA',
                'organization_type': 'private_company'
            }
        )
        
        # Get or create a test opportunity
        opportunity, created = Opportunity.objects.get_or_create(
            title="Test Software Internship",
            organization=org,
            defaults={
                'description': 'This is a test internship opportunity for software development. Join our team and work on exciting projects with modern technologies.',
                'opportunity_type': 'internship',
                'status': 'published',
                'application_deadline': timezone.now() + timedelta(days=30),
                'start_date': timezone.now().date() + timedelta(days=45),
                'end_date': timezone.now().date() + timedelta(days=135),
                'location': 'San Francisco, CA',
                'is_remote': True,
                'compensation': '$25/hour',
                'required_major': 'Computer Science',
                'graduation_year_min': 2024,
                'graduation_year_max': 2026,
                'min_gpa': 3.0,
                'max_applications': 50
            }
        )
        
        # Test formatting
        formatted_text = format_opportunity_for_channel(opportunity)
        print("Formatted channel post:")
        print("=" * 50)
        print(formatted_text)
        print("=" * 50)
        
        # Check if key elements are present
        assert "Test Software Internship" in formatted_text
        assert "Test Tech Company" in formatted_text
        assert "Internship" in formatted_text
        assert "San Francisco, CA" in formatted_text
        assert "Remote" in formatted_text
        assert "$25/hour" in formatted_text
        assert "Computer Science" in formatted_text
        assert "2024-2026" in formatted_text
        
        print("✅ Opportunity formatting test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Opportunity formatting test failed: {e}")
        return False


def test_admin_functions():
    """Test admin authorization functions"""
    print("\nTesting admin functions...")
    
    try:
        from telegram_bot.handlers.admin import is_admin, add_admin, remove_admin, load_admins_from_config
        
        # Test admin management
        test_user_id = 123456789
        
        # Initially should not be admin
        assert not is_admin(test_user_id), "User should not be admin initially"
        
        # Add admin
        add_admin(test_user_id)
        assert is_admin(test_user_id), "User should be admin after adding"
        
        # Remove admin
        remove_admin(test_user_id)
        assert not is_admin(test_user_id), "User should not be admin after removing"
        
        # Test loading from config
        os.environ['TELEGRAM_ADMIN_IDS'] = '111,222,333'
        load_admins_from_config()
        assert is_admin(111), "Admin 111 should be loaded from config"
        assert is_admin(222), "Admin 222 should be loaded from config"
        assert is_admin(333), "Admin 333 should be loaded from config"
        assert not is_admin(444), "Admin 444 should not be loaded"
        
        print("✅ Admin functions test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Admin functions test failed: {e}")
        return False


def test_signal_integration():
    """Test Django signal integration"""
    print("\nTesting signal integration...")
    
    try:
        from apps.opportunities.models import Opportunity
        from apps.organizations.models import Organization
        from django.conf import settings
        from django.utils import timezone
        from datetime import timedelta
        
        # Enable Telegram for testing
        original_enabled = getattr(settings, 'TELEGRAM_BOT_ENABLED', False)
        settings.TELEGRAM_BOT_ENABLED = True
        
        try:
            # Get or create test organization
            org, _ = Organization.objects.get_or_create(
                name="Signal Test Company",
                defaults={
                    'description': 'Test company for signal testing',
                    'website': 'https://example.com',
                    'location': 'New York, NY',
                    'organization_type': 'private_company'
                }
            )
            
            # Create opportunity with draft status
            opportunity = Opportunity.objects.create(
                title="Signal Test Opportunity",
                organization=org,
                description="Test opportunity for signal testing",
                opportunity_type='internship',
                status='draft',  # Start as draft
                application_deadline=timezone.now() + timedelta(days=30),
                start_date=timezone.now().date() + timedelta(days=45),
                location='New York, NY'
            )
            
            print(f"Created opportunity with ID {opportunity.id} in draft status")
            
            # Change status to published (this should trigger the signal)
            opportunity.status = 'published'
            opportunity.save()
            
            print("Changed status to published - signal should have fired")
            print("✅ Signal integration test completed (check logs for actual posting)")
            
            # Clean up
            opportunity.delete()
            
        finally:
            # Restore original setting
            settings.TELEGRAM_BOT_ENABLED = original_enabled
        
        return True
        
    except Exception as e:
        print(f"❌ Signal integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Starting Telegram Channel Administration Tests")
    print("=" * 60)
    
    tests = [
        test_opportunity_formatting,
        test_admin_functions,
        test_signal_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Channel administration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
