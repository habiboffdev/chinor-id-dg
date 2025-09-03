"""
Django management command to run the Telegram bot
Usage: python manage.py run_telegram_bot
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os


class Command(BaseCommand):
    help = 'Run the Telegram bot in polling mode'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=0,
            help='Polling interval in seconds (default: 0 for immediate)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=20,
            help='Timeout for long polling in seconds (default: 20)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        timeout = options['timeout']
        
        # Check if Telegram bot is configured
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN is not configured in settings')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting Telegram bot...')
        )
        self.stdout.write(f'Polling interval: {interval}s')
        self.stdout.write(f'Timeout: {timeout}s')
        
        # Add telegram_bot to Python path if needed
        project_root = settings.BASE_DIR.parent  # Go up from opportuni_backend to project root
        telegram_bot_path = project_root / 'telegram_bot'
        if str(telegram_bot_path) not in sys.path:
            sys.path.insert(0, str(telegram_bot_path))
        
        try:
            # Import and run the bot
            from telegram_bot.bot import run_polling
            
            self.stdout.write(
                self.style.SUCCESS('Bot started successfully. Press Ctrl+C to stop.')
            )
            
            run_polling(interval=interval, timeout=timeout)
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('\nBot stopped by user.')
            )
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to import bot: {e}')
            )
            self.stdout.write(
                'Make sure telegram_bot requirements are installed:'
            )
            self.stdout.write(
                'pip install -r telegram_bot/requirements.txt'
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Bot error: {e}')
            )
