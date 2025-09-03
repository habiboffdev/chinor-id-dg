"""
Django management command to test Telegram channel posting
Usage: python manage.py test_telegram_channel [--opportunity-id ID]
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test Telegram channel posting functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--opportunity-id',
            type=int,
            help='ID of specific opportunity to post (optional)',
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Post the latest published opportunity',
        )

    def handle(self, *args, **options):
        # Check if Telegram bot is configured
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN is not configured in settings')
            )
            return
        
        if not settings.TELEGRAM_CHANNEL_ID:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_CHANNEL_ID is not configured in settings')
            )
            return
        
        # Add telegram_bot to Python path if needed
        project_root = settings.BASE_DIR.parent
        telegram_bot_path = project_root / 'telegram_bot'
        if str(telegram_bot_path) not in sys.path:
            sys.path.insert(0, str(telegram_bot_path))
        
        try:
            from apps.opportunities.models import Opportunity
            from telegram_bot.handlers.admin import post_opportunity_to_channel
            from telegram_bot.config import create_bot
            
            # Get opportunity to post
            opportunity = None
            if options['opportunity_id']:
                try:
                    opportunity = Opportunity.objects.get(id=options['opportunity_id'])
                except Opportunity.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Opportunity with ID {options["opportunity_id"]} not found')
                    )
                    return
            elif options['latest']:
                opportunity = Opportunity.objects.filter(status='published').order_by('-created_at').first()
                if not opportunity:
                    self.stdout.write(
                        self.style.ERROR('No published opportunities found')
                    )
                    return
            else:
                # Show available opportunities
                opportunities = Opportunity.objects.filter(status='published').order_by('-created_at')[:10]
                if not opportunities:
                    self.stdout.write(
                        self.style.ERROR('No published opportunities found')
                    )
                    return
                
                self.stdout.write('Available published opportunities:')
                for opp in opportunities:
                    self.stdout.write(f'  ID {opp.id}: {opp.title} - {opp.organization.name}')
                self.stdout.write('\nUse --opportunity-id ID or --latest to post')
                return
            
            # Create bot and post to channel
            bot = create_bot()
            
            self.stdout.write(f'Posting opportunity "{opportunity.title}" to channel...')
            
            success = post_opportunity_to_channel(
                bot=bot,
                opportunity=opportunity,
                channel_id=settings.TELEGRAM_CHANNEL_ID,
                webapp_url=settings.TELEGRAM_WEBAPP_URL
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully posted to channel!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to post to channel')
                )
                
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import required modules: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
