"""
Opportuni Telegram Bot entry points. Does not auto-start anything.
Expose run_polling() and run_webhook() for manual start.
"""
from typing import Optional

import telebot

from telegram_bot.config import create_bot, Settings, setup_django
from telegram_bot.handlers.common import wire_common_handlers
from telegram_bot.handlers.student import wire_student_handlers
from telegram_bot.handlers.admin import wire_admin_handlers


def build_bot(parse_mode: Optional[str] = 'HTML') -> telebot.TeleBot:
    settings = Settings.load()

    # Seamless Django ORM access (attempt by default; skip on failure)
    try:
        setup_django()
    except Exception as e:
        # Don't hard-crash the bot if ORM isn't needed; print a concise hint
        print(f"[telegram_bot] Django ORM setup skipped: {e}")

    bot = create_bot(parse_mode=parse_mode)

    # Wire handlers: admin first, then student, then common fallback
    wire_admin_handlers(bot)
    wire_student_handlers(bot)
    wire_common_handlers(bot, settings.webapp_url)

    return bot


def run_polling(interval: int = 0, timeout: int = 20):
    bot = build_bot()
    # Explicitly do not call infinity_polling here automatically from import
    bot.infinity_polling(interval=interval, timeout=timeout)


def run_webhook():
    """Skeleton for webhook mode. Integrate with your web server.
    See pyTelegramBotAPI docs for telebot.ext.webhooks usage.
    """
    raise NotImplementedError("Implement webhook integration with your WSGI/ASGI stack if needed.")
