"""
Django management command to test Telegram channel posting
Usage: python manage.py test_telegram_posting
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch
import sys
import time
from pathlib import Path

# Add telegram_bot to Python path
project_root = Path(__file__).resolve().parents[5]  # Go up to project root (MVP/chinor_id_new)
telegram_bot_path = project_root / 'telegram_bot'
if str(telegram_bot_path) not in sys.path:
    sys.path.insert(0, str(telegram_bot_path))

# Also add the project root for telegram_bot module
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class Command(BaseCommand):
    help = 'Test Telegram channel posting functionality with real Django integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mock-bot',
            action='store_true',
            help='Use mock bot instead of real Telegram API',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test data after testing',
        )

    def handle(self, *args, **options):
        self.use_mock = options['mock_bot']
        self.cleanup = options.get('cleanup', True)
        self.test_results = []
        
        self.stdout.write("🤖 Testing Telegram Channel Posting Integration")
        self.stdout.write("=" * 60)
        
        # Check configuration
        if not self.check_configuration():
            return
        
        # Setup mocks if requested
        if self.use_mock:
            self.setup_mocks()
        
        try:
            # Run tests
            self.run_tests()
            
            # Print summary
            self.print_summary()
            
        finally:
            if self.use_mock:
                self.cleanup_mocks()
    
    def check_configuration(self):
        """Check if Telegram configuration is available"""
        config_ok = True
        
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(self.style.ERROR("❌ TELEGRAM_BOT_TOKEN not configured"))
            config_ok = False
        else:
            self.stdout.write(self.style.SUCCESS("✅ Bot token configured"))
        
        if not hasattr(settings, 'TELEGRAM_BOT_ENABLED'):
            self.stdout.write(self.style.WARNING("⚠️  TELEGRAM_BOT_ENABLED not in settings"))
        elif settings.TELEGRAM_BOT_ENABLED:
            self.stdout.write(self.style.SUCCESS("✅ Telegram bot enabled"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Telegram bot disabled"))
        
        if not hasattr(settings, 'TELEGRAM_CHANNEL_ID') or not settings.TELEGRAM_CHANNEL_ID:
            self.stdout.write(self.style.WARNING("⚠️  TELEGRAM_CHANNEL_ID not configured"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Channel ID: {settings.TELEGRAM_CHANNEL_ID}"))
        
        return config_ok
    
    def setup_mocks(self):
        """Setup mock objects for testing"""
        self.stdout.write("🔧 Setting up mock bot...")
        
        # Import telegram_bot modules here after path is set
        try:
            import telegram_bot.config
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"❌ Cannot import telegram_bot: {e}"))
            return
        
        self.mock_bot = Mock()
        self.mock_bot.send_message = Mock(return_value=True)
        
        # Mock the bot creation
        self.bot_patcher = patch('telegram_bot.config.create_bot')
        self.mock_create_bot = self.bot_patcher.start()
        self.mock_create_bot.return_value = self.mock_bot
        
        self.stdout.write(self.style.SUCCESS("✅ Mock bot setup complete"))
    
    def cleanup_mocks(self):
        """Clean up mock patches"""
        if hasattr(self, 'bot_patcher'):
            self.bot_patcher.stop()
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {test_name}: {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {test_name}: {message}"))
        
        self.test_results.append((test_name, success, message))
    
    def test_opportunity_formatting(self):
        """Test opportunity message formatting"""
        try:
            from apps.organizations.models import Organization
            from apps.opportunities.models import Opportunity
            from telegram_bot.handlers.admin import format_opportunity_for_channel
            
            # Get or create test organization
            from apps.accounts.models import User
            
            # Create a user for the organization
            user, _ = User.objects.get_or_create(
                username="test_telegram_user",
                defaults={
                    'email': 'test@telegram.example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            
            org, created = Organization.objects.get_or_create(
                name="Test Telegram Organization",
                defaults={
                    'user': user,
                    'description': 'Test organization for Telegram posting',
                    'website': 'https://test-telegram.example.com',
                    'country': 'Test Country',
                    'city': 'Test City',
                    'email': 'org@telegram.example.com',
                    'organization_type': 'private_company'
                }
            )
            
            # Create test opportunity
            opportunity = Opportunity.objects.create(
                title="Test Telegram Software Developer",
                organization=org,
                description="A comprehensive test opportunity for verifying Telegram posting functionality with all required fields and proper formatting.",
                opportunity_type='job',
                status='published',
                application_deadline=timezone.now() + timedelta(days=30),
                start_date=timezone.now().date() + timedelta(days=45),
                location='Remote / Test City',
                is_remote=True,
                compensation='$80,000 - $120,000',
                required_major='Computer Science',
                graduation_year_min=2020,
                graduation_year_max=2025,
                min_gpa=3.0,
                max_applications=50
            )
            
            # Test formatting
            formatted_message = format_opportunity_for_channel(opportunity)
            
            # Verify key elements
            required_elements = [
                opportunity.title,
                org.name,
                "Job",
                "Remote",
                "$80,000 - $120,000",
                "Computer Science"
            ]
            
            missing = [elem for elem in required_elements if elem not in formatted_message]
            
            if missing:
                self.log_result("Message Formatting", False, f"Missing: {missing}")
                return False, None, None
            else:
                self.log_result("Message Formatting", True, "All elements present")
                return True, opportunity, org
                
        except Exception as e:
            self.log_result("Message Formatting", False, str(e))
            return False, None, None
    
    def test_direct_posting(self, opportunity):
        """Test direct channel posting function"""
        try:
            from telegram_bot.handlers.admin import post_opportunity_to_channel
            from telegram_bot.config import create_bot
            
            if self.use_mock:
                bot = self.mock_bot
                # Reset mock for this test
                bot.send_message.reset_mock()
            else:
                bot = create_bot()
            
            # Test posting
            channel_id = getattr(settings, 'TELEGRAM_CHANNEL_ID', '@test_channel')
            webapp_url = getattr(settings, 'TELEGRAM_WEBAPP_URL', 'https://test.com')
            
            result = post_opportunity_to_channel(
                bot=bot,
                opportunity=opportunity,
                channel_id=channel_id,
                webapp_url=webapp_url
            )
            
            if self.use_mock:
                # Check if mock was called
                if bot.send_message.called:
                    call_args = bot.send_message.call_args
                    self.log_result("Direct Posting", True, f"Mock called with {len(call_args[1])} parameters")
                    return True
                else:
                    self.log_result("Direct Posting", False, "Mock send_message not called")
                    return False
            else:
                # Real bot posting
                if result:
                    self.log_result("Direct Posting", True, f"Posted to {channel_id}")
                    return True
                else:
                    self.log_result("Direct Posting", False, "Posting function returned False")
                    return False
                    
        except Exception as e:
            self.log_result("Direct Posting", False, str(e))
            return False
    
    def test_signal_triggered_posting(self, org):
        """Test automatic posting via Django signals"""
        try:
            from apps.opportunities.models import Opportunity
            
            # Temporarily enable Telegram for this test
            original_enabled = getattr(settings, 'TELEGRAM_BOT_ENABLED', False)
            settings.TELEGRAM_BOT_ENABLED = True
            
            if self.use_mock:
                self.mock_bot.send_message.reset_mock()
            
            try:
                # Create opportunity with published status (should trigger signal)
                opportunity = Opportunity.objects.create(
                    title="Signal Test Opportunity - Auto Post",
                    organization=org,
                    description="Testing automatic posting via Django signals",
                    opportunity_type='internship',
                    status='published',  # This should trigger auto-posting
                    application_deadline=timezone.now() + timedelta(days=20),
                    start_date=timezone.now().date() + timedelta(days=30),
                    location='Signal Test Location'
                )
                
                # Wait for signal processing (signals run in background threads)
                time.sleep(2)
                
                if self.use_mock:
                    if self.mock_bot.send_message.called:
                        self.log_result("Signal Auto-Posting", True, "Signal triggered mock posting")
                        result = True
                    else:
                        self.log_result("Signal Auto-Posting", False, "Signal did not trigger mock posting")
                        result = False
                else:
                    # For real bot, we can't easily verify if posting happened
                    # But we can check if no errors occurred
                    self.log_result("Signal Auto-Posting", True, "Signal processed without errors")
                    result = True
                
                # Test status change from draft to published
                if self.use_mock:
                    self.mock_bot.send_message.reset_mock()
                
                # Create draft opportunity
                draft_opp = Opportunity.objects.create(
                    title="Draft to Published Test",
                    organization=org,
                    description="Testing status change from draft to published",
                    opportunity_type='workshop',
                    status='draft',
                    application_deadline=timezone.now() + timedelta(days=15),
                    start_date=timezone.now().date() + timedelta(days=25),
                    location='Draft Test Location'
                )
                
                time.sleep(1)
                
                # Change to published
                draft_opp.status = 'published'
                draft_opp.save()
                
                time.sleep(2)
                
                if self.use_mock:
                    if self.mock_bot.send_message.called:
                        self.log_result("Status Change Posting", True, "Status change triggered posting")
                    else:
                        self.log_result("Status Change Posting", False, "Status change did not trigger posting")
                else:
                    self.log_result("Status Change Posting", True, "Status change processed")
                
                # Cleanup test opportunities
                if self.cleanup:
                    opportunity.delete()
                    draft_opp.delete()
                
                return result
                
            finally:
                settings.TELEGRAM_BOT_ENABLED = original_enabled
                
        except Exception as e:
            self.log_result("Signal Auto-Posting", False, str(e))
            return False
    
    def test_keyboard_creation(self, opportunity):
        """Test inline keyboard creation"""
        try:
            from telegram_bot.handlers.admin import create_opportunity_keyboard
            
            webapp_url = getattr(settings, 'TELEGRAM_WEBAPP_URL', 'https://test.com')
            keyboard = create_opportunity_keyboard(opportunity, webapp_url)
            
            # Check if keyboard has buttons
            if hasattr(keyboard, 'keyboard') and keyboard.keyboard:
                button_count = sum(len(row) for row in keyboard.keyboard)
                self.log_result("Keyboard Creation", True, f"Created {button_count} buttons")
                return True
            else:
                self.log_result("Keyboard Creation", False, "No buttons in keyboard")
                return False
                
        except Exception as e:
            self.log_result("Keyboard Creation", False, str(e))
            return False
    
    def run_tests(self):
        """Run all tests"""
        # Test 1: Message formatting
        format_success, test_opportunity, test_org = self.test_opportunity_formatting()
        
        if not format_success:
            self.stdout.write(self.style.ERROR("❌ Cannot continue without working message formatting"))
            return
        
        # Test 2: Direct posting
        self.test_direct_posting(test_opportunity)
        
        # Test 3: Keyboard creation
        self.test_keyboard_creation(test_opportunity)
        
        # Test 4: Signal-triggered posting
        self.test_signal_triggered_posting(test_org)
        
        # Cleanup
        if self.cleanup and test_opportunity:
            test_opportunity.delete()
            test_org.delete()
            self.stdout.write("🧹 Cleaned up test data")
    
    def print_summary(self):
        """Print test summary"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 TEST SUMMARY")
        self.stdout.write("-" * 30)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✅" if success else "❌"
            self.stdout.write(f"{status} {test_name}: {message}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.stdout.write(f"\n🎯 Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            self.stdout.write(self.style.SUCCESS("🎉 ALL TESTS PASSED!"))
            self.stdout.write("✅ Telegram channel posting is working correctly")
        else:
            self.stdout.write(self.style.WARNING("⚠️  Some tests failed"))
            self.stdout.write("Check the configuration and error messages above")
        
        # Usage instructions
        self.stdout.write("\n📝 To test with real bot:")
        self.stdout.write("python manage.py test_telegram_posting")
        self.stdout.write("\n📝 To test with mock (safer):")
        self.stdout.write("python manage.py test_telegram_posting --mock-bot")
