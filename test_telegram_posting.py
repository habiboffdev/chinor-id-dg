"""
Integration test for Telegram channel opportunity posting
Tests the complete flow from Django opportunity creation to Telegram channel posting
"""
import os
import sys
import django
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
project_root = Path(__file__).parent
backend_path = project_root / 'opportuni_backend'
telegram_bot_path = project_root / 'telegram_bot'

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(telegram_bot_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()


class TelegramChannelPostingTest:
    """Test class for Telegram channel posting functionality"""
    
    def __init__(self):
        self.test_results = []
        self.mock_bot = None
        self.test_org = None
        self.setup_mocks()
    
    def setup_mocks(self):
        """Setup mock objects for testing"""
        self.mock_bot = Mock()
        self.mock_bot.send_message = Mock(return_value=True)
        
        # Mock the bot creation to return our mock
        self.bot_creation_patcher = patch('telegram_bot.config.create_bot')
        self.mock_create_bot = self.bot_creation_patcher.start()
        self.mock_create_bot.return_value = self.mock_bot
    
    def cleanup_mocks(self):
        """Clean up patches"""
        self.bot_creation_patcher.stop()
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append(f"{status} {test_name}: {message}")
        print(f"{status} {test_name}: {message}")
    
    def create_test_organization(self):
        """Create a test organization"""
        try:
            from apps.organizations.models import Organization
            
            org, created = Organization.objects.get_or_create(
                name="Test Bot Organization",
                defaults={
                    'description': 'Test organization for bot posting tests',
                    'website': 'https://test-bot.example.com',
                    'location': 'Test City, Test Country',
                    'organization_type': 'private_company'
                }
            )
            
            self.test_org = org
            self.log_result("Create Test Organization", True, f"Created/found org ID {org.id}")
            return org
            
        except Exception as e:
            self.log_result("Create Test Organization", False, str(e))
            return None
    
    def test_opportunity_formatting(self):
        """Test that opportunity formatting works correctly"""
        try:
            from apps.opportunities.models import Opportunity
            from telegram_bot.handlers.admin import format_opportunity_for_channel
            
            # Create test opportunity
            opportunity = Opportunity.objects.create(
                title="Test Bot Software Engineer Position",
                organization=self.test_org,
                description="This is a test opportunity created by the bot testing system. It includes all the necessary fields to verify proper formatting and posting functionality.",
                opportunity_type='job',
                status='published',
                application_deadline=timezone.now() + timedelta(days=30),
                start_date=timezone.now().date() + timedelta(days=45),
                end_date=timezone.now().date() + timedelta(days=135),
                location='Remote / San Francisco, CA',
                is_remote=True,
                compensation='$120,000 - $150,000/year',
                required_major='Computer Science',
                graduation_year_min=2022,
                graduation_year_max=2025,
                min_gpa=3.5,
                max_applications=100
            )
            
            # Test formatting
            formatted_text = format_opportunity_for_channel(opportunity)
            
            # Verify required elements are present
            required_elements = [
                "Test Bot Software Engineer Position",
                "Test Bot Organization",
                "Job",
                "Remote / San Francisco, CA",
                "Remote",
                "$120,000 - $150,000/year",
                "Computer Science",
                "2022-2025",
                "3.5",
                "Apply now on Opportuni!"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in formatted_text:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_result("Opportunity Formatting", False, f"Missing elements: {missing_elements}")
                return False, opportunity
            else:
                self.log_result("Opportunity Formatting", True, "All required elements present")
                return True, opportunity
                
        except Exception as e:
            self.log_result("Opportunity Formatting", False, str(e))
            return False, None
    
    def test_channel_posting_function(self, opportunity):
        """Test the channel posting function directly"""
        try:
            from telegram_bot.handlers.admin import post_opportunity_to_channel
            from django.conf import settings
            
            # Mock channel settings
            test_channel_id = "@test_channel"
            test_webapp_url = "https://test.opportuni.com"
            
            # Test posting
            result = post_opportunity_to_channel(
                bot=self.mock_bot,
                opportunity=opportunity,
                channel_id=test_channel_id,
                webapp_url=test_webapp_url
            )
            
            # Verify bot.send_message was called
            if self.mock_bot.send_message.called:
                call_args = self.mock_bot.send_message.call_args
                
                # Check if correct parameters were passed
                expected_chat_id = test_channel_id
                actual_chat_id = call_args[1]['chat_id']
                
                if actual_chat_id == expected_chat_id:
                    self.log_result("Channel Posting Function", True, f"Posted to {test_channel_id}")
                    return True
                else:
                    self.log_result("Channel Posting Function", False, f"Wrong chat_id: {actual_chat_id}")
                    return False
            else:
                self.log_result("Channel Posting Function", False, "send_message not called")
                return False
                
        except Exception as e:
            self.log_result("Channel Posting Function", False, str(e))
            return False
    
    def test_signal_integration(self):
        """Test Django signal integration for automatic posting"""
        try:
            from apps.opportunities.models import Opportunity
            from django.conf import settings
            
            # Enable Telegram for testing
            original_enabled = getattr(settings, 'TELEGRAM_BOT_ENABLED', False)
            original_channel_id = getattr(settings, 'TELEGRAM_CHANNEL_ID', None)
            
            # Set test configuration
            settings.TELEGRAM_BOT_ENABLED = True
            settings.TELEGRAM_CHANNEL_ID = "@test_signal_channel"
            
            try:
                # Reset mock
                self.mock_bot.send_message.reset_mock()
                
                # Create opportunity with draft status first
                opportunity = Opportunity.objects.create(
                    title="Signal Test Opportunity",
                    organization=self.test_org,
                    description="Testing Django signals integration",
                    opportunity_type='internship',
                    status='draft',  # Start as draft
                    application_deadline=timezone.now() + timedelta(days=20),
                    start_date=timezone.now().date() + timedelta(days=30),
                    location='Test Location'
                )
                
                # Verify no posting happened for draft
                if self.mock_bot.send_message.called:
                    self.log_result("Signal Integration - Draft", False, "Posted draft opportunity (should not happen)")
                    return False
                
                self.log_result("Signal Integration - Draft", True, "No posting for draft status")
                
                # Now change to published (this should trigger posting)
                self.mock_bot.send_message.reset_mock()
                opportunity.status = 'published'
                opportunity.save()
                
                # Give signals a moment to process (they run in threads)
                import time
                time.sleep(1)
                
                # Check if posting was attempted
                if self.mock_bot.send_message.called:
                    self.log_result("Signal Integration - Published", True, "Signal triggered posting")
                    
                    # Clean up
                    opportunity.delete()
                    return True
                else:
                    self.log_result("Signal Integration - Published", False, "Signal did not trigger posting")
                    opportunity.delete()
                    return False
                    
            finally:
                # Restore original settings
                settings.TELEGRAM_BOT_ENABLED = original_enabled
                settings.TELEGRAM_CHANNEL_ID = original_channel_id
                
        except Exception as e:
            self.log_result("Signal Integration", False, str(e))
            return False
    
    def test_new_opportunity_creation(self):
        """Test automatic posting when creating new published opportunity"""
        try:
            from apps.opportunities.models import Opportunity
            from django.conf import settings
            
            # Enable Telegram for testing
            original_enabled = getattr(settings, 'TELEGRAM_BOT_ENABLED', False)
            original_channel_id = getattr(settings, 'TELEGRAM_CHANNEL_ID', None)
            
            settings.TELEGRAM_BOT_ENABLED = True
            settings.TELEGRAM_CHANNEL_ID = "@test_new_opp_channel"
            
            try:
                # Reset mock
                self.mock_bot.send_message.reset_mock()
                
                # Create opportunity directly as published
                opportunity = Opportunity.objects.create(
                    title="New Published Opportunity Test",
                    organization=self.test_org,
                    description="Testing new opportunity creation with published status",
                    opportunity_type='scholarship',
                    status='published',  # Created as published
                    application_deadline=timezone.now() + timedelta(days=25),
                    start_date=timezone.now().date() + timedelta(days=40),
                    location='New Test Location',
                    compensation='$5,000'
                )
                
                # Give signals a moment to process
                import time
                time.sleep(1)
                
                # Check if posting was triggered
                if self.mock_bot.send_message.called:
                    self.log_result("New Opportunity Creation", True, "New published opportunity triggered posting")
                    result = True
                else:
                    self.log_result("New Opportunity Creation", False, "New published opportunity did not trigger posting")
                    result = False
                
                # Clean up
                opportunity.delete()
                return result
                
            finally:
                # Restore original settings
                settings.TELEGRAM_BOT_ENABLED = original_enabled
                settings.TELEGRAM_CHANNEL_ID = original_channel_id
                
        except Exception as e:
            self.log_result("New Opportunity Creation", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling when posting fails"""
        try:
            from telegram_bot.handlers.admin import post_opportunity_to_channel
            
            # Create mock bot that raises exception
            error_bot = Mock()
            error_bot.send_message.side_effect = Exception("Network error")
            
            # Test with invalid opportunity
            result = post_opportunity_to_channel(
                bot=error_bot,
                opportunity=None,  # Invalid opportunity
                channel_id="@test_channel",
                webapp_url="https://test.com"
            )
            
            # Should return False on error
            if result is False:
                self.log_result("Error Handling", True, "Properly handled posting error")
                return True
            else:
                self.log_result("Error Handling", False, "Did not handle error properly")
                return False
                
        except Exception as e:
            self.log_result("Error Handling", False, str(e))
            return False
    
    def test_keyboard_generation(self):
        """Test inline keyboard generation for channel posts"""
        try:
            from telegram_bot.handlers.admin import create_opportunity_keyboard
            from apps.opportunities.models import Opportunity
            
            # Create test opportunity
            opportunity = Opportunity.objects.create(
                title="Keyboard Test Opportunity",
                organization=self.test_org,
                description="Testing keyboard generation",
                opportunity_type='workshop',
                status='published',
                application_deadline=timezone.now() + timedelta(days=15),
                start_date=timezone.now().date() + timedelta(days=20),
                location='Keyboard Test Location'
            )
            
            # Test keyboard creation
            webapp_url = "https://test.opportuni.com"
            keyboard = create_opportunity_keyboard(opportunity, webapp_url)
            
            # Check if keyboard has buttons
            if hasattr(keyboard, 'keyboard') and len(keyboard.keyboard) > 0:
                self.log_result("Keyboard Generation", True, f"Generated keyboard with {len(keyboard.keyboard)} rows")
                opportunity.delete()
                return True
            else:
                self.log_result("Keyboard Generation", False, "No keyboard buttons generated")
                opportunity.delete()
                return False
                
        except Exception as e:
            self.log_result("Keyboard Generation", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🤖 Starting Telegram Channel Posting Tests")
        print("=" * 60)
        
        # Setup
        if not self.create_test_organization():
            print("❌ Failed to create test organization. Aborting tests.")
            return False
        
        # Run tests
        tests = [
            self.test_opportunity_formatting,
            self.test_signal_integration,
            self.test_new_opportunity_creation,
            self.test_error_handling,
            self.test_keyboard_generation
        ]
        
        # Special handling for formatting test to get opportunity for other tests
        formatting_success, test_opportunity = self.test_opportunity_formatting()
        
        if formatting_success and test_opportunity:
            # Run channel posting test with the created opportunity
            self.test_channel_posting_function(test_opportunity)
            # Clean up test opportunity
            test_opportunity.delete()
        
        # Run remaining tests
        for test_func in tests[1:]:  # Skip formatting test as we already ran it
            try:
                test_func()
            except Exception as e:
                self.log_result(test_func.__name__, False, f"Exception: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY:")
        print("-" * 30)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result)
        total = len(self.test_results)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Telegram posting is working correctly.")
            success_rate = 100
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            success_rate = (passed / total) * 100
        
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Cleanup
        if self.test_org:
            self.test_org.delete()
            print("🧹 Cleaned up test organization")
        
        self.cleanup_mocks()
        
        return passed == total


def main():
    """Main test runner"""
    try:
        # Print environment info
        print("🔧 Environment Check:")
        print(f"Python: {sys.version}")
        print(f"Django: {django.get_version()}")
        
        # Check Django settings
        from django.conf import settings
        print(f"Django Settings: {settings.SETTINGS_MODULE}")
        
        # Check if required apps are available
        try:
            from apps.opportunities.models import Opportunity
            from apps.organizations.models import Organization
            print("✅ Django models available")
        except ImportError as e:
            print(f"❌ Django models not available: {e}")
            return False
        
        # Check if telegram bot modules are available
        try:
            from telegram_bot.handlers.admin import post_opportunity_to_channel
            print("✅ Telegram bot modules available")
        except ImportError as e:
            print(f"❌ Telegram bot modules not available: {e}")
            return False
        
        print("\n" + "=" * 60)
        
        # Run tests
        test_runner = TelegramChannelPostingTest()
        success = test_runner.run_all_tests()
        
        return success
        
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
